import time
import numpy as np
from dataclasses import dataclass
from typing import List, Dict, Optional
import threading
import logging

try:
    import pywinusb.hid as hid
    HAS_PYUSB = True
except ImportError:
    HAS_PYUSB = False
    logging.warning("pywinusb not available. USB control will be simulated.")

@dataclass
class StimulationPattern:
    frequency: float  # Hz
    amplitude: float  # normalized 0-1
    duration: float   # seconds
    waveform: str     # sine, square, pulse

@dataclass
class VocalTrainingSession:
    target_frequency: float
    tolerance: float
    duration: float
    feedback_type: str  # auditory, tactile, visual

class USBNeuroStimulator:
    def __init__(self, vendor_id: int = None, product_id: int = None):
        """
        Initialize USB neuro stimulator
        If no VID/PID provided, will auto-detect compatible devices
        """
        # Use provided IDs or auto-detect
        self.vendor_id = vendor_id or 0x0E8D  # Default to detected Android-ish device
        self.product_id = product_id or 0x0616
        self.device = None
        self.is_connected = False
        self.current_pattern = None
        self.stimulation_active = False
        self.thread = None
        
        # Brain region stimulation parameters
        self.broca_params = {
            'frequency_range': (10, 20),  # Hz
            'amplitude_range': (0.3, 0.7),
            'duration_range': (0.1, 0.5)
        }
        
        self.dlmc_params = {
            'frequency_range': (5, 15),   # Hz  
            'amplitude_range': (0.2, 0.6),
            'duration_range': (0.2, 0.8)
        }
        
        # Vocal tract targeting
        self.thyroid_params = {
            'frequency_range': (2, 8),    # Hz
            'amplitude_range': (0.1, 0.4),
            'duration_range': (0.3, 1.0)
        }
        
        self.vocal_fold_params = {
            'frequency_range': (1, 5),    # Hz
            'amplitude_range': (0.05, 0.3),
            'duration_range': (0.5, 2.0)
        }

    def connect(self) -> bool:
        """Connect to USB stimulation device - auto-detect compatible devices"""
        if not HAS_PYUSB:
            logging.info("Simulating USB connection")
            self.is_connected = True
            return True
            
        try:
            # First try specific device if provided
            if self.vendor_id and self.product_id:
                devices = hid.HidDeviceFilter(vendor_id=self.vendor_id, product_id=self.product_id).get_devices()
                if devices:
                    self.device = devices[0]
                    self.device.open()
                    self.is_connected = True
                    logging.info(f"USB device connected: VID=0x{self.vendor_id:04X}, PID=0x{self.product_id:04X}")
                    return True
            
            # Auto-detect: try to find any compatible device
            all_devices = hid.HidDeviceFilter().get_devices()
            compatible_devices = [
                dev for dev in all_devices 
                if not any(x in str(dev.product_name).lower() for x in ['keyboard', 'mouse', 'game'])
            ]
            
            if compatible_devices:
                # Prefer devices that look like stimulation hardware
                for dev in compatible_devices:
                    if 'stim' in str(dev.product_name).lower() or 'neuro' in str(dev.product_name).lower():
                        self.device = dev
                        break
                else:
                    # Use first compatible device
                    self.device = compatible_devices[0]
                
                self.device.open()
                self.is_connected = True
                self.vendor_id = self.device.vendor_id
                self.product_id = self.device.product_id
                logging.info(f"Auto-connected to USB device: {self.device.product_name}")
                logging.info(f"VID=0x{self.vendor_id:04X}, PID=0x{self.product_id:04X}")
                return True
            else:
                logging.warning("No compatible USB devices found for stimulation")
                return False
                
        except Exception as e:
            logging.error(f"USB connection failed: {e}")
            return False

    def disconnect(self):
        """Disconnect from USB device"""
        if self.device and self.device.is_opened():
            self.device.close()
        self.is_connected = False
        self.stimulation_active = False
        logging.info("USB device disconnected")

    def send_pulse(self, frequency: float, amplitude: float, duration: float):
        """Send a single stimulation pulse"""
        if not self.is_connected:
            logging.warning("Device not connected - simulating pulse")
            time.sleep(duration)
            return
            
        try:
            # Convert parameters to USB packet
            pulse_data = self._create_pulse_packet(frequency, amplitude, duration)
            if HAS_PYUSB and self.device:
                self.device.send_output_report(pulse_data)
            logging.debug(f"Pulse sent: {frequency}Hz, {amplitude}amp, {duration}s")
        except Exception as e:
            logging.error(f"Pulse sending failed: {e}")

    def _create_pulse_packet(self, frequency: float, amplitude: float, duration: float) -> List[int]:
        """Create USB data packet for stimulation parameters"""
        # Standard HID report format (64 bytes typically)
        # Adjust based on actual device requirements
        freq_int = int(frequency * 10)   # 0.1Hz resolution
        amp_int = int(amplitude * 100)   # 1% resolution
        dur_ms = int(duration * 1000)    # milliseconds
        
        # Create 64-byte HID report (common standard)
        report = [0] * 64
        report[0] = 0x02  # Report ID (if required)
        report[1] = 0x55   # Start marker
        report[2] = 0xAA   # Start marker
        
        # Frequency (2 bytes, little endian)
        report[3] = freq_int & 0xFF
        report[4] = (freq_int >> 8) & 0xFF
        
        # Amplitude (1 byte)
        report[5] = amp_int & 0xFF
        
        # Duration (2 bytes, little endian)
        report[6] = dur_ms & 0xFF
        report[7] = (dur_ms >> 8) & 0xFF
        
        return report

    def start_pattern(self, pattern: StimulationPattern):
        """Start continuous stimulation pattern"""
        if self.stimulation_active:
            self.stop_stimulation()
            
        self.current_pattern = pattern
        self.stimulation_active = True
        self.thread = threading.Thread(target=self._pattern_worker, daemon=True)
        self.thread.start()

    def _pattern_worker(self):
        """Worker thread for continuous stimulation patterns"""
        while self.stimulation_active and self.current_pattern:
            self.send_pulse(
                self.current_pattern.frequency,
                self.current_pattern.amplitude,
                self.current_pattern.duration
            )
            # Calculate interval based on frequency
            interval = 1.0 / self.current_pattern.frequency
            time.sleep(interval)

    def stop_stimulation(self):
        """Stop all stimulation"""
        self.stimulation_active = False
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=1.0)
        logging.info("Stimulation stopped")

    def stimulate_brain_region(self, region: str, intensity: float = 0.5):
        """Stimulate specific brain regions for speech rehabilitation"""
        intensity = np.clip(intensity, 0.0, 1.0)
        
        if region.lower() == 'broca':
            params = self.broca_params
            target = "Broca's area"
        elif region.lower() == 'dlmc':
            params = self.dlmc_params
            target = "dLMC"
        else:
            raise ValueError(f"Unknown brain region: {region}")
        
        # Calculate parameters based on intensity
        freq = params['frequency_range'][0] + intensity * (
            params['frequency_range'][1] - params['frequency_range'][0])
        amp = params['amplitude_range'][0] + intensity * (
            params['amplitude_range'][1] - params['amplitude_range'][0])
        dur = params['duration_range'][0] + intensity * (
            params['duration_range'][1] - params['duration_range'][0])
        
        pattern = StimulationPattern(frequency=freq, amplitude=amp, duration=dur, waveform='sine')
        self.start_pattern(pattern)
        logging.info(f"Stimulating {target} at {freq:.1f}Hz, {amp:.2f}amp")

    def stimulate_vocal_tract(self, area: str, intensity: float = 0.3):
        """Stimulate vocal tract areas for muscle training"""
        intensity = np.clip(intensity, 0.0, 1.0)
        
        if area.lower() == 'thyroid':
            params = self.thyroid_params
            target = "thyroid ligaments"
        elif area.lower() == 'vocal_fold':
            params = self.vocal_fold_params
            target = "vocal folds"
        else:
            raise ValueError(f"Unknown vocal tract area: {area}")
        
        freq = params['frequency_range'][0] + intensity * (
            params['frequency_range'][1] - params['frequency_range'][0])
        amp = params['amplitude_range'][0] + intensity * (
            params['amplitude_range'][1] - params['amplitude_range'][0])
        dur = params['duration_range'][0] + intensity * (
            params['duration_range'][1] - params['duration_range'][0])
        
        pattern = StimulationPattern(frequency=freq, amplitude=amp, duration=dur, waveform='pulse')
        self.start_pattern(pattern)
        logging.info(f"Stimulating {target} at {freq:.1f}Hz, {amp:.2f}amp")

    def create_vocal_training_session(self, target_freq: float, tolerance: float = 50.0) -> VocalTrainingSession:
        """Create a vocal training session with specific parameters"""
        return VocalTrainingSession(
            target_frequency=target_freq,
            tolerance=tolerance,
            duration=30.0,  # 30 seconds default
            feedback_type="tactile"
        )

    def adaptive_stimulation(self, current_performance: float, target_performance: float):
        """Adapt stimulation parameters based on performance feedback"""
        error = abs(current_performance - target_performance)
        
        # Simple PID-like adjustment
        if error > 0.3:  # Large error
            intensity = 0.8
        elif error > 0.1:  # Medium error
            intensity = 0.5
        else:  # Small error
            intensity = 0.2
            
        # Apply stimulation to both brain and vocal tract
        self.stimulate_brain_region('broca', intensity)
        self.stimulate_vocal_tract('thyroid', intensity * 0.7)

# Example usage and test
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    stimulator = USBNeuroStimulator()
    if stimulator.connect():
        try:
            # Test brain region stimulation
            print("Testing Broca's area stimulation...")
            stimulator.stimulate_brain_region('broca', 0.6)
            time.sleep(3)
            stimulator.stop_stimulation()
            
            # Test vocal tract stimulation
            print("Testing thyroid ligaments stimulation...")
            stimulator.stimulate_vocal_tract('thyroid', 0.4)
            time.sleep(3)
            stimulator.stop_stimulation()
            
        finally:
            stimulator.disconnect()
    else:
        print("Running in simulation mode")
        # Test simulation mode
        stimulator.stimulate_brain_region('dlmc', 0.5)
        time.sleep(2)
        stimulator.stop_stimulation()