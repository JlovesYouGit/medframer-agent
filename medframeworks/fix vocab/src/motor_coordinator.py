import json
from typing import Dict, Any
from pathlib import Path
import logging

class MotorCoordinator:
    def __init__(self, config_path: str = "src/motor_config.json"):
        self.config = self._load_config(config_path)
        self.current_adjustments = {
            'cortical_lag': 0.0,
            'articulation_gain': 1.0,
            'error_correction': 0.0
        }
        
    def _load_config(self, path: str) -> Dict[str, Any]:
        """Load motor coordination configuration"""
        try:
            with open(path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logging.error(f"Failed to load motor config: {e}")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Return default configuration if file loading fails"""
        return {
            "motor_coordination": {
                "cortical_lag_adjustment": {
                    "baseline_lag_ms": 50,
                    "max_adjustment_ms": 100,
                    "sensitivity": 0.7,
                    "recovery_rate": 0.2
                },
                "speech_articulation": {
                    "lip_sync_gain": 1.2,
                    "tongue_position_correction": 0.8,
                    "jaw_movement_scaling": 1.0,
                    "vocal_cord_timing_offset_ms": -10
                },
                "motor_learning": {
                    "error_correction_rate": 0.05,
                    "retention_factor": 0.9,
                    "decay_time_minutes": 120,
                    "max_adaptation_per_session": 0.3
                },
                "safety_limits": {
                    "max_cortical_stimulation": 0.8,
                    "min_articulation_interval_ms": 200,
                    "allow_negative_lag": false,
                    "emergency_cutoff_threshold": 0.95
                }
            }
        }
    
    def calculate_lag_adjustment(self, error: float) -> float:
        """Calculate cortical lag adjustment based on motor error"""
        params = self.config['motor_coordination']['cortical_lag_adjustment']
        adjustment = error * params['sensitivity']
        
        # Apply limits
        max_adj = params['max_adjustment_ms']
        adjustment = max(-max_adj, min(adjustment, max_adj))
        
        # Apply baseline
        return params['baseline_lag_ms'] + adjustment
    
    def calculate_articulation_gain(self, performance: float) -> float:
        """Calculate speech articulation gain factors"""
        params = self.config['motor_coordination']['speech_articulation']
        base_gain = params['lip_sync_gain']
        
        # Adjust based on performance (0-1 scale)
        if performance < 0.5:
            return base_gain * (1 + (0.5 - performance))
        return base_gain
    
    def update_error_correction(self, error: float):
        """Update motor learning based on observed error"""
        params = self.config['motor_coordination']['motor_learning']
        self.current_adjustments['error_correction'] += error * params['error_correction_rate']
        
        # Apply retention and decay
        self.current_adjustments['error_correction'] *= params['retention_factor']
        
        # Apply limits
        max_adapt = params['max_adaptation_per_session']
        self.current_adjustments['error_correction'] = max(-max_adapt, min(self.current_adjustments['error_correction'], max_adapt))
    
    def get_current_parameters(self) -> Dict[str, float]:
        """Get current motor coordination parameters"""
        return {
            'effective_lag_ms': self.calculate_lag_adjustment(self.current_adjustments['error_correction']),
            'articulation_gain': self.calculate_articulation_gain(1 - self.current_adjustments['error_correction']),
            'error_correction_factor': self.current_adjustments['error_correction'],
            'safety_ok': self._check_safety_limits()
        }
    
    def _check_safety_limits(self) -> bool:
        """Verify all parameters are within safe limits"""
        limits = self.config['motor_coordination']['safety_limits']
        
        # Check cortical stimulation directly
        if abs(self.current_adjustments['error_correction']) > limits['max_cortical_stimulation']:
            return False
        
        # Check articulation timing by calculating lag directly (avoid recursion)
        lag_params = self.config['motor_coordination']['cortical_lag_adjustment']
        error = self.current_adjustments['error_correction']
        adjustment = error * lag_params['sensitivity']
        max_adj = lag_params['max_adjustment_ms']
        effective_lag = lag_params['baseline_lag_ms'] + max(-max_adj, min(adjustment, max_adj))
        
        if effective_lag < 0 and not limits['allow_negative_lag']:
            return False
        
        return True
    
    def reset_session(self):
        """Reset session-specific adjustments"""
        self.current_adjustments = {
            'cortical_lag': 0.0,
            'articulation_gain': 1.0,
            'error_correction': 0.0
        }

# Example usage
if __name__ == "__main__":
    coordinator = MotorCoordinator()
    
    # Simulate motor error (positive = too slow, negative = too fast)
    motor_error = 0.3  # 30% too slow
    
    # Update adjustments
    coordinator.update_error_correction(motor_error)
    
    # Get current parameters
    params = coordinator.get_current_parameters()
    print(f"Adjusted parameters: {params}")
    
    # Check safety
    print(f"Safety status: {'OK' if params['safety_ok'] else 'WARNING'}")