import numpy as np
from typing import Dict, List, Optional
import time
import logging
from dataclasses import dataclass
from .audio_utils import extract_dysarthria_features, classify_auditory_sample
from .usb_neuro_stimulator import USBNeuroStimulator, VocalTrainingSession

@dataclass
class TrainingProgress:
    session_id: str
    baseline_features: Dict
    current_features: Dict
    improvement_score: float
    stimulation_intensity: float
    completed_cycles: int

class VocalRehabilitationTrainer:
    def __init__(self):
        self.stimulator = USBNeuroStimulator()
        self.current_session: Optional[VocalTrainingSession] = None
        self.progress: Optional[TrainingProgress] = None
        self.weights = self._initialize_weights()
        
    def _initialize_weights(self) -> Dict[str, float]:
        """Initialize neural network weights for adaptive training"""
        return {
            'jitter_weight': 0.3,
            'shimmer_weight': 0.25,
            'ftri_weight': 0.15,
            'atri_weight': 0.1,
            'pvi_weight': 0.1,
            'nhr_weight': 0.05,
            'ppe_weight': 0.05
        }
    
    def connect_stimulator(self) -> bool:
        """Connect to USB stimulation device"""
        return self.stimulator.connect()
    
    def disconnect_stimulator(self):
        """Disconnect from stimulation device"""
        self.stimulator.disconnect()
    
    def start_training_session(self, audio_path: str, target_frequency: float = 180.0) -> str:
        """Start a new vocal training session"""
        # Extract baseline features
        baseline_features = extract_dysarthria_features(audio_path)
        classification = classify_auditory_sample(audio_path)
        
        # Create training session
        self.current_session = self.stimulator.create_vocal_training_session(
            target_frequency=target_frequency,
            tolerance=50.0
        )
        
        # Initialize progress tracking
        session_id = f"session_{int(time.time())}"
        self.progress = TrainingProgress(
            session_id=session_id,
            baseline_features=baseline_features,
            current_features=baseline_features,
            improvement_score=0.0,
            stimulation_intensity=0.3,  # Start with mild stimulation
            completed_cycles=0
        )
        
        logging.info(f"Started training session {session_id}")
        logging.info(f"Baseline features: {baseline_features}")
        logging.info(f"Audio classification: {classification.label} (confidence: {classification.confidence})")
        
        return session_id
    
    def calculate_performance_score(self, features: Dict) -> float:
        """Calculate overall performance score from acoustic features"""
        # Normalize and weight features (lower values are better for most metrics)
        score = 0.0
        total_weight = 0.0
        
        for feature_name, weight in self.weights.items():
            feature_base = feature_name.replace('_weight', '')
            if feature_base in features:
                value = features[feature_base]
                # Normalize based on typical ranges
                if feature_base in ['jitter', 'shimmer', 'ftri', 'atri', 'pvi', 'nhr']:
                    normalized = 1.0 - min(value / 0.1, 1.0)  # Lower is better
                elif feature_base == 'ppe':
                    normalized = 1.0 - value  # Lower entropy is better
                else:
                    normalized = 1.0
                
                score += normalized * weight
                total_weight += weight
        
        return score / total_weight if total_weight > 0 else 0.0
    
    def update_weights(self, current_features: Dict, baseline_features: Dict):
        """Adaptively update feature weights based on training progress"""
        improvements = {}
        
        for feature in self.weights.keys():
            feature_name = feature.replace('_weight', '')
            if feature_name in current_features and feature_name in baseline_features:
                improvement = baseline_features[feature_name] - current_features[feature_name]
                improvements[feature_name] = max(improvement, 0)  # Only positive improvements
        
        # Normalize improvements to get weight adjustments
        total_improvement = sum(improvements.values())
        if total_improvement > 0:
            for feature_name, improvement in improvements.items():
                weight_key = f"{feature_name}_weight"
                if weight_key in self.weights:
                    # Increase weight for features showing improvement
                    adjustment = (improvement / total_improvement) * 0.1
                    self.weights[weight_key] = min(self.weights[weight_key] + adjustment, 0.5)
        
        # Renormalize weights to sum to 1.0
        total = sum(self.weights.values())
        if total > 0:
            for key in self.weights:
                self.weights[key] /= total
    
    def run_training_cycle(self, audio_path: str) -> Dict:
        """Run a single training cycle with adaptive stimulation"""
        if not self.current_session or not self.progress:
            raise RuntimeError("No active training session")
        
        # Extract current features
        current_features = extract_dysarthria_features(audio_path)
        self.progress.current_features = current_features
        
        # Calculate performance scores
        baseline_score = self.calculate_performance_score(self.progress.baseline_features)
        current_score = self.calculate_performance_score(current_features)
        improvement = current_score - baseline_score
        
        # Update progress
        self.progress.improvement_score = improvement
        self.progress.completed_cycles += 1
        
        # Adaptive stimulation based on performance
        if improvement < 0:  # Performance declined
            self.progress.stimulation_intensity = min(self.progress.stimulation_intensity + 0.1, 1.0)
        elif improvement > 0.1:  # Good improvement
            self.progress.stimulation_intensity = max(self.progress.stimulation_intensity - 0.05, 0.1)
        
        # Apply stimulation
        self._apply_adaptive_stimulation()
        
        # Update weights for next cycle
        self.update_weights(current_features, self.progress.baseline_features)
        
        logging.info(f"Cycle {self.progress.completed_cycles}: "
                    f"Score: {current_score:.3f} (Δ: {improvement:+.3f}), "
                    f"Intensity: {self.progress.stimulation_intensity:.2f}")
        
        return {
            'cycle': self.progress.completed_cycles,
            'current_score': current_score,
            'improvement': improvement,
            'stimulation_intensity': self.progress.stimulation_intensity,
            'features': current_features
        }
    
    def _apply_adaptive_stimulation(self):
        """Apply neurostimulation based on current performance"""
        intensity = self.progress.stimulation_intensity
        
        # Stimulate Broca's area for speech production
        self.stimulator.stimulate_brain_region('broca', intensity)
        
        # Stimulate dLMC for motor control
        self.stimulator.stimulate_brain_region('dlmc', intensity * 0.8)
        
        # Stimulate vocal tract structures
        self.stimulator.stimulate_vocal_tract('thyroid', intensity * 0.6)
        self.stimulator.stimulate_vocal_tract('vocal_fold', intensity * 0.4)
        
        # Brief stimulation period
        time.sleep(2.0)
        self.stimulator.stop_stimulation()
    
    def get_session_summary(self) -> Optional[Dict]:
        """Get summary of current training session"""
        if not self.progress:
            return None
        
        baseline_score = self.calculate_performance_score(self.progress.baseline_features)
        current_score = self.calculate_performance_score(self.progress.current_features)
        
        return {
            'session_id': self.progress.session_id,
            'cycles_completed': self.progress.completed_cycles,
            'baseline_score': baseline_score,
            'current_score': current_score,
            'improvement': current_score - baseline_score,
            'current_stimulation_intensity': self.progress.stimulation_intensity,
            'feature_weights': self.weights.copy()
        }
    
    def end_session(self):
        """End the current training session"""
        self.stimulator.stop_stimulation()
        self.current_session = None
        logging.info(f"Ended session {self.progress.session_id if self.progress else 'unknown'}")
        self.progress = None

# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    trainer = VocalRehabilitationTrainer()
    
    if trainer.connect_stimulator():
        try:
            # Start training session with sample audio
            session_id = trainer.start_training_session(
                "path/to/baseline_audio.wav",
                target_frequency=180.0
            )
            
            # Run a few training cycles (in real usage, this would be with new recordings)
            for cycle in range(3):
                result = trainer.run_training_cycle("path/to/current_audio.wav")
                print(f"Cycle {cycle + 1}: {result}")
                time.sleep(1)
            
            # Get final summary
            summary = trainer.get_session_summary()
            print(f"Session summary: {summary}")
            
        finally:
            trainer.end_session()
            trainer.disconnect_stimulator()
    else:
        print("Stimulator not available, running in analysis mode only")
        features = extract_dysarthria_features("path/to/sample_audio.wav")
        print(f"Acoustic features: {features}")