import os
from dataclasses import dataclass


@dataclass
class FeatureConfig:
    sample_rate: int = 16000
    preemph: float = 0.97
    f0_min: float = 50.0
    f0_max: float = 500.0
    tremor_min_hz: float = 0.2
    tremor_max_hz: float = 20.0
    # For jitter/shimmer windows
    f0_tracking_method: str = "praat"  # or "librosa"


@dataclass
class TrainingConfig:
    test_size: float = 0.2
    random_state: int = 42
    cv_folds: int = 5


@dataclass
class Paths:
    # You will need to set these to your local dataset folders or manifest CSVs
    audio_dir: str = os.environ.get("AUDIO_DIR", "")
    manifest_csv: str = os.environ.get("MANIFEST_CSV", "")


feature_cfg = FeatureConfig()
train_cfg = TrainingConfig()
paths = Paths()
