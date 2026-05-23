import numpy as np
import librosa
import scipy.signal as sps
from dataclasses import dataclass
import json


@dataclass
class ClassificationResult:
    label: str
    confidence: float
    features: dict


def load_wav(path: str, sr: int = 16000):
    y, orig_sr = librosa.load(path, sr=None, mono=True)
    if orig_sr != sr:
        y = librosa.resample(y, orig_sr=orig_sr, target_sr=sr)
    return y.astype(np.float32), sr


def pre_emphasis(y: np.ndarray, preemph: float = 0.97) -> np.ndarray:
    return sps.lfilter([1, -preemph], [1], y)


def amplitude_envelope(y: np.ndarray, sr: int, frame_length: int = 1024, hop_length: int = 256) -> np.ndarray:
    # RMS as amplitude envelope
    rms = librosa.feature.rms(y=y, frame_length=frame_length, hop_length=hop_length, center=True)
    return rms.squeeze(0)


def spectral_flux(y: np.ndarray, sr: int, n_fft: int = 1024, hop_length: int = 256) -> np.ndarray:
    S = np.abs(librosa.stft(y, n_fft=n_fft, hop_length=hop_length))
    S = S / (np.max(S, axis=0, keepdims=True) + 1e-10)
    flux = np.sqrt(np.sum(np.diff(S, axis=1, prepend=S[:, :1])**2, axis=0))
    return flux


def pitch_variability(y: np.ndarray, sr: int, fmin: float = 50.0, fmax: float = 500.0):
    t, f0 = extract_f0(y, sr, fmin=fmin, fmax=fmax)
    f0_i = interpolate_nan(f0)
    valid = np.isfinite(f0)
    pv = float(np.nanstd(f0)) if np.any(valid) else 0.0
    jitter = float(np.nanmean(np.abs(np.diff(f0_i)) / (f0_i[:-1] + 1e-6))) if len(f0_i) > 1 else 0.0
    return pv, jitter


def summarize(arr: np.ndarray):
    if arr is None or len(arr) == 0:
        return {"mean": 0.0, "std": 0.0, "p90": 0.0, "p10": 0.0}
    return {
        "mean": float(np.mean(arr)),
        "std": float(np.std(arr)),
        "p90": float(np.percentile(arr, 90)),
        "p10": float(np.percentile(arr, 10)),
    }


def classify_auditory_sample(path: str,
                             target_sr: int = 16000,
                             n_fft: int = 1024,
                             hop_length: int = 256) -> ClassificationResult:
    """
    Logic-only classifier that labels an audio sample by the degree of frequency (Hz) fluctuations.
    Returns one of: 'steady', 'modulated', 'highly_fluctuating'.
    """
    y, sr = load_wav(path, sr=target_sr)
    if len(y) == 0:
        return ClassificationResult(label="unknown", confidence=0.0, features={})

    # Basic preprocessing
    y_pe = pre_emphasis(y)

    # Features capturing fluctuations
    flux = spectral_flux(y_pe, sr, n_fft=n_fft, hop_length=hop_length)
    env = amplitude_envelope(y_pe, sr, frame_length=n_fft, hop_length=hop_length)

    # Spectral centroid and bandwidth
    S = np.abs(librosa.stft(y_pe, n_fft=n_fft, hop_length=hop_length))
    centroid = librosa.feature.spectral_centroid(S=S, sr=sr).squeeze(0)
    bandwidth = librosa.feature.spectral_bandwidth(S=S, sr=sr).squeeze(0)

    # Pitch-based variability (if voiced)
    pv, jitter = pitch_variability(y_pe, sr)

    # Aggregate statistics
    flux_s = summarize(flux)
    cent_s = summarize(centroid)
    bw_s = summarize(bandwidth)
    env_s = summarize(env)

    # Heuristic thresholds (tuned for 16kHz, hop 256)
    # These are scale-invariant-ish due to normalization above.
    flux_level = flux_s["mean"] + 0.5 * flux_s["std"]
    cent_var = cent_s["std"]
    bw_level = bw_s["mean"]

    # Rule logic
    # - If spectral flux and bandwidth are very high or pitch jitter high -> highly_fluctuating
    # - Else if moderate -> modulated
    # - Else -> steady
    high_flux = flux_level > 0.25
    high_bw = bw_level > 1200
    high_jitter = jitter > 0.02
    high_cent_var = cent_var > 400

    mod_flux = flux_level > 0.12
    mod_bw = bw_level > 700
    mod_cent_var = cent_var > 200

    if (high_flux and (high_bw or high_cent_var)) or high_jitter:
        label = "highly_fluctuating"
        confidence = 0.7
    elif (mod_flux and (mod_bw or mod_cent_var)):
        label = "modulated"
        confidence = 0.6
    else:
        label = "steady"
        confidence = 0.6

    features = {
        "flux": flux_s,
        "centroid": cent_s,
        "bandwidth": bw_s,
        "envelope": env_s,
        "pitch_std": float(pv),
        "pitch_jitter": float(jitter),
        "sr": sr,
        "n_fft": n_fft,
        "hop_length": hop_length,
    }

    return ClassificationResult(label=label, confidence=confidence, features=features)


def extract_f0(y: np.ndarray, sr: int, fmin: float = 50.0, fmax: float = 500.0, method: str = "praat"):
    if method == "praat":
        try:
            import parselmouth
            snd = parselmouth.Sound(y, sampling_frequency=sr)
            pitch = snd.to_pitch(time_step=0.0, pitch_floor=fmin, pitch_ceiling=fmax)
            # Convert to numpy arrays
            timestamps = pitch.xs()
            f0 = pitch.selected_array['frequency']
            f0[f0 == 0] = np.nan
            return timestamps, f0
        except Exception:
            # Fallback to librosa
            pass
    # librosa fallback (pyin)
    f0, voiced_flag, voiced_probs = librosa.pyin(y, fmin=fmin, fmax=fmax, sr=sr)
    t = np.arange(len(f0)) * (512 / sr)  # default hop=512 in pyin
    return t, f0


def interpolate_nan(arr: np.ndarray) -> np.ndarray:
    x = np.arange(len(arr))
    good = np.isfinite(arr)
    if good.sum() < 2:
        return np.full_like(arr, np.nanmean(arr) if np.isfinite(np.nanmean(arr)) else 0.0)
    return np.interp(x, x[good], arr[good])


def envelope_from_frames(arr: np.ndarray, hop_length: int) -> np.ndarray:
    # Expand to sample rate based on hop_length if needed
    return arr


def contour_fft(contour: np.ndarray, sr_hz: float):
    # Compute FFT magnitude for low-frequency modulation analysis
    n = len(contour)
    if n < 4:
        return np.array([]), np.array([])
    # detrend
    contour = contour - np.nanmean(contour)
    contour = np.nan_to_num(contour)
    window = np.hanning(n)
    spec = np.abs(np.fft.rfft(contour * window))
    freqs = np.fft.rfftfreq(n, d=1.0/sr_hz)
    return freqs, spec


def bandpass_modulation(contour: np.ndarray, sr_hz: float, low: float = 2.0, high: float = 10.0) -> np.ndarray:
    """Band-pass filter a contour to isolate 2-10 Hz modulation."""
    n = len(contour)
    if n < 8 or sr_hz <= 0:
        return np.zeros_like(contour)
    contour = np.nan_to_num(contour - np.nanmean(contour))
    nyq = 0.5 * sr_hz
    low_n = max(low / nyq, 1e-6)
    high_n = min(high / nyq, 0.99)
    if low_n >= high_n:
        return np.zeros_like(contour)
    b, a = sps.butter(4, [low_n, high_n], btype='band')
    return sps.filtfilt(b, a, contour)


def _shannon_entropy_norm(hist: np.ndarray) -> float:
    p = hist.astype(np.float64)
    p = p / (np.sum(p) + 1e-12)
    p = p[p > 0]
    if len(p) == 0:
        return 0.0
    H = -np.sum(p * np.log2(p))
    Hmax = np.log2(len(p))
    return float(H / (Hmax + 1e-12))


def extract_dysarthria_features(path: str,
                                target_sr: int = 16000,
                                n_fft: int = 1024,
                                hop_length: int = 256) -> dict:
    """
    Software-only extraction of acoustic markers related to dysarthria/ALS.
    Returns a dictionary with:
      - jitter, shimmer
      - FTrI, FTrP (frequency tremor index/percent)
      - ATrI, ATrP (amplitude tremor index/percent)
      - PVI (pitch period variability)
      - NHR (noise-to-harmonics ratio)
      - PPE (pitch period entropy, normalized 0..1)
      - modulogram summaries for F0 and amplitude (dominant mod freq/power in 0.2-20 Hz)
    """
    y, sr = load_wav(path, sr=target_sr)
    if len(y) == 0:
        return {}

    # Pre-emphasis for better high-freq balance
    y_pe = pre_emphasis(y)

    # Frame-level amplitude envelope and pitch
    env = amplitude_envelope(y_pe, sr, frame_length=n_fft, hop_length=hop_length)
    t_f0, f0 = extract_f0(y_pe, sr)
    f0_i = interpolate_nan(f0)

    # Contour sampling rate (frames per second)
    sr_hz = sr / float(hop_length)

    # Jitter: mean absolute relative change in F0 (voiced)
    f0_valid = np.isfinite(f0)
    if np.any(f0_valid):
        f0_v = f0[f0_valid]
        if len(f0_v) > 1:
            jitter = float(np.nanmean(np.abs(np.diff(f0_v)) / (f0_v[:-1] + 1e-8)))
        else:
            jitter = 0.0
    else:
        jitter = 0.0

    # Shimmer: mean absolute relative change in amplitude envelope
    env_safe = np.maximum(env, 1e-6)
    shimmer = float(np.mean(np.abs(np.diff(env_safe)) / env_safe[:-1])) if len(env_safe) > 1 else 0.0

    # Pitch Period Variability (PVI): CV of period 1/F0
    if np.any(f0_valid):
        T = 1.0 / np.maximum(f0_v, 1e-6)
        pvi = float(np.std(T) / (np.mean(T) + 1e-8)) if len(T) > 1 else 0.0
    else:
        pvi = 0.0

    # Tremor indices via 2-10 Hz band-pass of F0 and envelope
    f0_bp = bandpass_modulation(f0_i, sr_hz, 2.0, 10.0)
    env_bp = bandpass_modulation(env, sr_hz, 2.0, 10.0)

    # Index: bandpassed RMS relative to total RMS of detrended contour
    def _rms(x):
        x = np.asarray(x)
        return np.sqrt(np.mean(x**2)) if len(x) else 0.0

    f0_det = np.nan_to_num(f0_i - np.nanmean(f0_i))
    env_det = np.nan_to_num(env - np.nanmean(env))

    ftri = float(_rms(f0_bp) / ( _rms(f0_det) + 1e-12 ))
    atri = float(_rms(env_bp) / ( _rms(env_det) + 1e-12 ))

    # Percentage: frames where modulation amplitude exceeds 0.5*std of detrended contour
    fthr = 0.5 * (np.std(f0_det) + 1e-12)
    athr = 0.5 * (np.std(env_det) + 1e-12)
    ftrp = float(np.mean(np.abs(f0_bp) > fthr)) if len(f0_bp) else 0.0
    atrp = float(np.mean(np.abs(env_bp) > athr)) if len(env_bp) else 0.0

    # NHR: approximate via harmonic component energy vs residual
    try:
        harm, perc = librosa.effects.hpss(y_pe)
        harm_e = float(np.sum(harm**2) + 1e-12)
        noise = y_pe - harm
        noise_e = float(np.sum(noise**2))
        nhr = float(noise_e / harm_e)
    except Exception:
        nhr = 0.0

    # PPE: normalized entropy of pitch period deviations
    if np.any(f0_valid):
        T_all = 1.0 / np.maximum(f0_i, 1e-6)
        z = (T_all - np.nanmedian(T_all)) / (np.nanmedian(T_all) + 1e-8)
        z = z[np.isfinite(z)]
        if len(z) > 0:
            hist, _ = np.histogram(np.clip(z, -0.5, 0.5), bins=50, range=(-0.5, 0.5))
            ppe = _shannon_entropy_norm(hist)
        else:
            ppe = 0.0
    else:
        ppe = 0.0

    # Modulogram summaries (0.2-20 Hz): dominant frequency and normalized power
    def _mod_summary(contour):
        freqs, spec = contour_fft(contour, sr_hz)
        if len(freqs) == 0:
            return {"peak_freq": 0.0, "peak_power": 0.0}
        mask = (freqs >= 0.2) & (freqs <= 20.0)
        if not np.any(mask):
            return {"peak_freq": 0.0, "peak_power": 0.0}
        f = freqs[mask]
        s = spec[mask]
        if len(s) == 0 or np.sum(s) == 0:
            return {"peak_freq": 0.0, "peak_power": 0.0}
        idx = int(np.argmax(s))
        peak_power = float(s[idx] / (np.sum(s) + 1e-12))
        return {"peak_freq": float(f[idx]), "peak_power": peak_power}

    mod_f0 = _mod_summary(f0_i)
    mod_env = _mod_summary(env)

    return {
        "jitter": jitter,
        "shimmer": shimmer,
        "FTrI": ftri,
        "FTrP": ftrp,
        "ATrI": atri,
        "ATrP": atrp,
        "PVI": pvi,
        "NHR": nhr,
        "PPE": ppe,
        "mod_peak_f0_hz": mod_f0["peak_freq"],
        "mod_peak_f0_power": mod_f0["peak_power"],
        "mod_peak_env_hz": mod_env["peak_freq"],
        "mod_peak_env_power": mod_env["peak_power"],
        "sr": sr,
        "hop_length": hop_length,
        "n_fft": n_fft,
    }


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python -m src.audio_utils <path_to_wav>")
        sys.exit(1)
    path = sys.argv[1]
    feats = extract_dysarthria_features(path)
    print(json.dumps(feats, indent=2))
