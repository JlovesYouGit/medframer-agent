import argparse
import time
import json
import logging
from typing import Dict, Any
from pathlib import Path

from .audio_utils import extract_dysarthria_features, classify_auditory_sample
from .usb_neuro_stimulator import USBNeuroStimulator
from .vocal_rehabilitation_trainer import VocalRehabilitationTrainer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('vocal_rehab.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class VocalRehabilitationSystem:
    def __init__(self):
        self.stimulator = USBNeuroStimulator()
        self.trainer = VocalRehabilitationTrainer()
        self.connected = False
        
    def connect_devices(self) -> bool:
        """Connect to all required devices"""
        logger.info("Connecting to USB stimulation device...")
        self.connected = self.stimulator.connect()
        if self.connected:
            logger.info("USB device connected successfully")
        else:
            logger.warning("Running in simulation mode - no USB device connected")
        return self.connected
    
    def disconnect_devices(self):
        """Disconnect from all devices"""
        self.stimulator.disconnect()
        self.trainer.disconnect_stimulator()
        self.connected = False
        logger.info("All devices disconnected")
    
    def analyze_audio(self, audio_path: str) -> Dict[str, Any]:
        """Complete audio analysis with classification and feature extraction"""
        if not Path(audio_path).exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
        
        logger.info(f"Analyzing audio: {audio_path}")
        
        # Get classification
        classification = classify_auditory_sample(audio_path)
        
        # Extract detailed features
        features = extract_dysarthria_features(audio_path)
        
        return {
            'classification': {
                'label': classification.label,
                'confidence': classification.confidence
            },
            'acoustic_features': features,
            'file_path': audio_path,
            'timestamp': time.time()
        }
    
    def run_diagnostic_mode(self, audio_path: str):
        """Run diagnostic mode with analysis only"""
        results = self.analyze_audio(audio_path)
        print("\n" + "="*60)
        print("VOCAL ANALYSIS RESULTS")
        print("="*60)
        print(f"Classification: {results['classification']['label']}")
        print(f"Confidence: {results['classification']['confidence']:.3f}")
        print("\nAcoustic Features:")
        for feature, value in results['acoustic_features'].items():
            if isinstance(value, (int, float)):
                print(f"  {feature}: {value:.4f}")
        print("="*60)
        
        return results
    
    def run_training_mode(self, baseline_audio: str, target_frequency: float = 180.0):
        """Run vocal training mode with adaptive stimulation"""
        if not self.connected:
            logger.warning("Training mode requires USB device connection")
            if not self.connect_devices():
                logger.error("Cannot start training without device connection")
                return
        
        logger.info("Starting vocal training mode...")
        
        try:
            # Start training session
            session_id = self.trainer.start_training_session(baseline_audio, target_frequency)
            logger.info(f"Training session started: {session_id}")
            
            # Simple training loop (in real usage, this would use new recordings)
            print("\nStarting training cycles...")
            print("Press Ctrl+C to stop training")
            
            cycle_count = 0
            while True:
                try:
                    # In real usage, you would record new audio here
                    # For demo, we'll use the baseline audio
                    result = self.trainer.run_training_cycle(baseline_audio)
                    
                    print(f"\nCycle {cycle_count + 1}:")
                    print(f"  Score: {result['current_score']:.3f}")
                    print(f"  Improvement: {result['improvement']:+.3f}")
                    print(f"  Stimulation Intensity: {result['stimulation_intensity']:.2f}")
                    
                    cycle_count += 1
                    time.sleep(3)  # Wait between cycles
                    
                except KeyboardInterrupt:
                    print("\nTraining interrupted by user")
                    break
                    
        finally:
            # Get final results
            summary = self.trainer.get_session_summary()
            if summary:
                print("\n" + "="*60)
                print("TRAINING SESSION SUMMARY")
                print("="*60)
                print(f"Session ID: {summary['session_id']}")
                print(f"Cycles completed: {summary['cycles_completed']}")
                print(f"Baseline score: {summary['baseline_score']:.3f}")
                print(f"Final score: {summary['current_score']:.3f}")
                print(f"Overall improvement: {summary['improvement']:+.3f}")
                print("="*60)
            
            self.trainer.end_session()
    
    def test_stimulation(self):
        """Test stimulation patterns"""
        if not self.connected:
            logger.warning("Stimulation test requires USB device connection")
            if not self.connect_devices():
                logger.error("Cannot test stimulation without device connection")
                return
        
        try:
            print("\nTesting brain region stimulation...")
            print("Stimulating Broca's area...")
            self.stimulator.stimulate_brain_region('broca', 0.5)
            time.sleep(2)
            self.stimulator.stop_stimulation()
            
            print("Stimulating dLMC...")
            self.stimulator.stimulate_brain_region('dlmc', 0.4)
            time.sleep(2)
            self.stimulator.stop_stimulation()
            
            print("\nTesting vocal tract stimulation...")
            print("Stimulating thyroid ligaments...")
            self.stimulator.stimulate_vocal_tract('thyroid', 0.3)
            time.sleep(2)
            self.stimulator.stop_stimulation()
            
            print("Stimulating vocal folds...")
            self.stimulator.stimulate_vocal_tract('vocal_fold', 0.2)
            time.sleep(2)
            self.stimulator.stop_stimulation()
            
            print("\nAll stimulation tests completed successfully")
            
        except Exception as e:
            logger.error(f"Stimulation test failed: {e}")
        finally:
            self.stimulator.stop_stimulation()

def main():
    parser = argparse.ArgumentParser(description="Vocal Rehabilitation System")
    parser.add_argument('--audio', '-a', help="Audio file to analyze")
    parser.add_argument('--mode', '-m', choices=['analyze', 'train', 'test'], 
                       default='analyze', help="Operation mode")
    parser.add_argument('--target-freq', '-f', type=float, default=180.0,
                       help="Target frequency for training (Hz)")
    parser.add_argument('--output', '-o', help="Output file for results")
    
    args = parser.parse_args()
    
    system = VocalRehabilitationSystem()
    
    try:
        if args.mode == 'analyze':
            if not args.audio:
                parser.error("Analysis mode requires --audio argument")
            
            results = system.run_diagnostic_mode(args.audio)
            
            if args.output:
                with open(args.output, 'w') as f:
                    json.dump(results, f, indent=2)
                logger.info(f"Results saved to {args.output}")
                
        elif args.mode == 'train':
            if not args.audio:
                parser.error("Training mode requires --audio argument")
            
            system.connect_devices()
            system.run_training_mode(args.audio, args.target_freq)
            
        elif args.mode == 'test':
            system.connect_devices()
            system.test_stimulation()
            
    except Exception as e:
        logger.error(f"Error: {e}")
    finally:
        system.disconnect_devices()

if __name__ == "__main__":
    main()