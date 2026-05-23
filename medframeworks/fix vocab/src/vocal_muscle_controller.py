import json
import logging
from typing import Dict, List, Optional
from dataclasses import dataclass
import numpy as np

@dataclass
class MuscleState:
    name: str
    current_contraction: float  # 0-1 scale
    target_contraction: float
    contraction_rate: float
    relaxation_rate: float
    pain_threshold: float
    overbearing_threshold: float

class VocalMuscleController:
    def __init__(self, config_path: str = "src/muscle_config.json"):
        self.muscles = self._load_muscle_config(config_path)
        self.pain_sensitivity = 0.5
        self.overbearing_adjustment = 0.3
        
    def _load_muscle_config(self, path: str) -> Dict[str, MuscleState]:
        """Load muscle configuration from JSON file"""
        try:
            with open(path, 'r') as f:
                config = json.load(f)
                return {name: MuscleState(**params) for name, params in config.items()}
        except Exception as e:
            logging.error(f"Failed to load muscle config: {e}")
            return self._get_default_muscles()
    
    def _get_default_muscles(self) -> Dict[str, MuscleState]:
        """Return default muscle configuration"""
        return {
            "vocal_cords": MuscleState(
                name="vocal_cords",
                current_contraction=0.3,
                target_contraction=0.3,
                contraction_rate=0.1,
                relaxation_rate=0.15,
                pain_threshold=0.7,
                overbearing_threshold=0.8
            ),
            "tongue": MuscleState(
                name="tongue",
                current_contraction=0.4,
                target_contraction=0.4,
                contraction_rate=0.08,
                relaxation_rate=0.12,
                pain_threshold=0.6,
                overbearing_threshold=0.75
            ),
            "lips": MuscleState(
                name="lips",
                current_contraction=0.5,
                target_contraction=0.5,
                contraction_rate=0.12,
                relaxation_rate=0.18,
                pain_threshold=0.65,
                overbearing_threshold=0.7
            ),
            "jaw": MuscleState(
                name="jaw",
                current_contraction=0.35,
                target_contraction=0.35,
                contraction_rate=0.05,
                relaxation_rate=0.1,
                pain_threshold=0.75,
                overbearing_threshold=0.85
            )
        }
    
    def update_pain_feedback(self, pain_levels: Dict[str, float]):
        """Adjust muscle targets based on pain feedback"""
        for muscle_name, pain in pain_levels.items():
            if muscle_name in self.muscles:
                muscle = self.muscles[muscle_name]
                if pain > muscle.pain_threshold:
                    # Reduce target contraction if pain exceeds threshold
                    reduction = self.pain_sensitivity * (pain - muscle.pain_threshold)
                    muscle.target_contraction = max(0, muscle.target_contraction - reduction)
    
    def update_overbearing_feedback(self, overbearing_levels: Dict[str, float]):
        """Adjust muscle targets based on overbearing feedback"""
        for muscle_name, level in overbearing_levels.items():
            if muscle_name in self.muscles:
                muscle = self.muscles[muscle_name]
                if level > muscle.overbearing_threshold:
                    # Adjust contraction based on overbearing level
                    adjustment = self.overbearing_adjustment * (level - muscle.overbearing_threshold)
                    muscle.target_contraction = np.clip(muscle.target_contraction - adjustment, 0, 1)
    
    def update_muscle_states(self):
        """Gradually adjust current contraction towards target"""
        for muscle in self.muscles.values():
            if muscle.current_contraction < muscle.target_contraction:
                # Contract muscle
                muscle.current_contraction = min(
                    muscle.current_contraction + muscle.contraction_rate,
                    muscle.target_contraction
                )
            else:
                # Relax muscle
                muscle.current_contraction = max(
                    muscle.current_contraction - muscle.relaxation_rate,
                    muscle.target_contraction
                )
    
    def get_current_contractions(self) -> Dict[str, float]:
        """Get current muscle contraction states"""
        return {name: muscle.current_contraction for name, muscle in self.muscles.items()}
    
    def set_speech_targets(self, phoneme: str):
        """Set target contractions for specific speech sounds"""
        # Basic phoneme targets (would be expanded in real system)
        targets = {
            'a': {'vocal_cords': 0.3, 'tongue': 0.2, 'lips': 0.4, 'jaw': 0.3},
            'e': {'vocal_cords': 0.4, 'tongue': 0.3, 'lips': 0.3, 'jaw': 0.4},
            'i': {'vocal_cords': 0.5, 'tongue': 0.5, 'lips': 0.2, 'jaw': 0.2},
            'o': {'vocal_cords': 0.35, 'tongue': 0.25, 'lips': 0.5, 'jaw': 0.35},
            'u': {'vocal_cords': 0.45, 'tongue': 0.4, 'lips': 0.3, 'jaw': 0.25}
        }
        
        if phoneme in targets:
            for muscle, value in targets[phoneme].items():
                if muscle in self.muscles:
                    self.muscles[muscle].target_contraction = value
    
    def reset_to_neutral(self):
        """Reset all muscles to neutral positions"""
        for muscle in self.muscles.values():
            muscle.target_contraction = 0.3
            muscle.current_contraction = 0.3

# Example usage
if __name__ == "__main__":
    controller = VocalMuscleController()
    
    # Simulate pain feedback
    controller.update_pain_feedback({'vocal_cords': 0.8, 'tongue': 0.5})
    
    # Update muscle states
    controller.update_muscle_states()
    
    # Get current contractions
    print("Current muscle states:", controller.get_current_contractions())