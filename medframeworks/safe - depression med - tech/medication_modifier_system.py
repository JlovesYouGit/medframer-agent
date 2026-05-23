#!/usr/bin/env python3
"""
Medication Modifier System
Handles 0.5mg addon modifications with electrolyte management
Addresses visual dissociation and lag through stelavis electrolyte production
"""

import json
import time
import math
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum

class ModifierType(Enum):
    """Types of medication modifiers"""
    STERPLISTIC_VIACRON = "sterplistic_viacron"
    STELAVIS_ELECTROLYTE = "stelavis_electrolyte"
    VISUAL_STABILIZER = "visual_stabilizer"
    LAG_REDUCER = "lag_reducer"

class ElectrolyteType(Enum):
    """Types of electrolytes managed by the system"""
    SODIUM = "sodium"
    POTASSIUM = "potassium"
    MAGNESIUM = "magnesium"
    CALCIUM = "calcium"
    CHLORIDE = "chloride"

@dataclass
class ElectrolyteLevel:
    """Represents current electrolyte levels"""
    electrolyte_type: ElectrolyteType
    current_level: float  # mmol/L
    optimal_level: float   # mmol/L
    production_rate: float  # mmol/hour
    consumption_rate: float # mmol/hour
    
    def get_deficit(self) -> float:
        """Calculate current deficit"""
        return max(0, self.optimal_level - self.current_level)
    
    def get_status(self) -> str:
        """Get status description"""
        deficit = self.get_deficit()
        if deficit <= 0:
            return "optimal"
        elif deficit < 0.5:
            return "slight_deficit"
        elif deficit < 1.0:
            return "moderate_deficit"
        else:
            return "severe_deficit"

@dataclass
class VisualStabilizationMetrics:
    """Metrics for visual dissociation and lag"""
    dissociation_level: float    # 0.0 to 1.0
    response_lag_ms: float       # milliseconds
    visual_clarity: float        # 0.0 to 1.0
    tracking_stability: float    # 0.0 to 1.0
    
    def get_overall_stability(self) -> float:
        """Calculate overall visual stability score"""
        return (self.visual_clarity + self.tracking_stability) / 2.0

@dataclass
class ModifierConfiguration:
    """Configuration for 0.5mg modifier addon"""
    modifier_id: str
    modifier_type: ModifierType
    dosage_mg: float
    sterplistic_concentration: float  # 0.0 to 1.0
    stelavis_production_rate: float    # 0.1 mmol/hour as specified
    target_electrolytes: List[ElectrolyteType]
    visual_stabilization_enabled: bool
    lag_reduction_enabled: bool
    
    def to_json(self) -> str:
        """Convert configuration to JSON"""
        return json.dumps(asdict(self), default=str, indent=2)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'ModifierConfiguration':
        """Create configuration from JSON"""
        data = json.loads(json_str)
        # Convert string enums back to enums
        data['modifier_type'] = ModifierType(data['modifier_type'])
        data['target_electrolytes'] = [ElectrolyteType(e) for e in data['target_electrolytes']]
        return cls(**data)

class MedicationModifierSystem:
    """
    Advanced modifier system for 0.5mg addon with electrolyte management
    Addresses pill side effects: electrolyte consumption, visual dissociation, and lag
    """
    
    def __init__(self):
        self.electrolyte_levels = self._initialize_electrolyte_levels()
        self.visual_metrics = VisualStabilizationMetrics(
            dissociation_level=0.3,  # Moderate dissociation from side effects
            response_lag_ms=150.0,    # 150ms lag
            visual_clarity=0.7,
            tracking_stability=0.6
        )
        self.active_modifiers: Dict[str, ModifierConfiguration] = {}
        self.modification_history: List[Dict[str, Any]] = []
        
    def _initialize_electrolyte_levels(self) -> Dict[ElectrolyteType, ElectrolyteLevel]:
        """Initialize baseline electrolyte levels affected by medication"""
        return {
            ElectrolyteType.SODIUM: ElectrolyteLevel(
                electrolyte_type=ElectrolyteType.SODIUM,
                current_level=135.0,  # mmol/L
                optimal_level=140.0,
                production_rate=0.0,
                consumption_rate=0.8  # Increased by medication
            ),
            ElectrolyteType.POTASSIUM: ElectrolyteLevel(
                electrolyte_type=ElectrolyteType.POTASSIUM,
                current_level=3.8,
                optimal_level=4.2,
                production_rate=0.0,
                consumption_rate=0.6
            ),
            ElectrolyteType.MAGNESIUM: ElectrolyteLevel(
                electrolyte_type=ElectrolyteType.MAGNESIUM,
                current_level=0.7,
                optimal_level=0.9,
                production_rate=0.0,
                consumption_rate=0.4
            ),
            ElectrolyteType.CALCIUM: ElectrolyteLevel(
                electrolyte_type=ElectrolyteType.CALCIUM,
                current_level=8.5,
                optimal_level=9.5,
                production_rate=0.0,
                consumption_rate=0.5
            ),
            ElectrolyteType.CHLORIDE: ElectrolyteLevel(
                electrolyte_type=ElectrolyteType.CHLORIDE,
                current_level=98.0,
                optimal_level=103.0,
                production_rate=0.0,
                consumption_rate=0.7
            )
        }
    
    def add_0_5mg_modifier(self, modifier_id: str, 
                          sterplistic_strength: float = 0.7,
                          stelavis_rate: float = 0.1) -> bool:
        """
        Add 0.5mg modifier with sterplistic viacron and stelavis electrolyte production
        
        Args:
            modifier_id: Unique identifier for this modifier
            sterplistic_strength: Concentration of sterplistic viacron (0.0-1.0)
            stelavis_rate: Electrolyte production rate in mmol/hour (default 0.1)
        
        Returns:
            True if modifier added successfully
        """
        try:
            config = ModifierConfiguration(
                modifier_id=modifier_id,
                modifier_type=ModifierType.STERPLISTIC_VIACRON,
                dosage_mg=0.5,
                sterplistic_concentration=sterplistic_strength,
                stelavis_production_rate=stelavis_rate,
                target_electrolytes=[
                    ElectrolyteType.SODIUM,
                    ElectrolyteType.POTASSIUM,
                    ElectrolyteType.MAGNESIUM
                ],
                visual_stabilization_enabled=True,
                lag_reduction_enabled=True
            )
            
            self.active_modifiers[modifier_id] = config
            
            # Apply stelavis electrolyte production
            self._apply_stelavis_production(config)
            
            # Apply visual stabilization
            self._apply_visual_stabilization(config)
            
            # Record in history
            self.modification_history.append({
                'timestamp': time.time(),
                'action': 'add_modifier',
                'modifier_id': modifier_id,
                'config': config.to_json()
            })
            
            return True
            
        except Exception as e:
            print(f"Error adding modifier: {e}")
            return False
    
    def _apply_stelavis_production(self, config: ModifierConfiguration):
        """Apply stelavis electrolyte production to counteract consumption"""
        production_rate = config.stelavis_production_rate
        
        # Distribute production across target electrolytes
        for electrolyte_type in config.target_electrolytes:
            if electrolyte_type in self.electrolyte_levels:
                level = self.electrolyte_levels[electrolyte_type]
                level.production_rate = production_rate / len(config.target_electrolytes)
                
                # Update current level based on production vs consumption
                net_change = level.production_rate - level.consumption_rate
                level.current_level += net_change * 0.1  # Apply over time increment
                
                # Clamp to reasonable bounds
                level.current_level = max(level.optimal_level * 0.8, 
                                         min(level.optimal_level * 1.2, level.current_level))
    
    def _apply_visual_stabilization(self, config: ModifierConfiguration):
        """Apply visual stabilization to reduce dissociation and lag"""
        if config.visual_stabilization_enabled:
            # Reduce dissociation based on sterplistic concentration
            reduction_factor = config.sterplistic_concentration * 0.4
            self.visual_metrics.dissociation_level *= (1.0 - reduction_factor)
            
            # Improve visual clarity
            self.visual_metrics.visual_clarity += reduction_factor * 0.3
            self.visual_metrics.visual_clarity = min(1.0, self.visual_metrics.visual_clarity)
            
            # Improve tracking stability
            self.visual_metrics.tracking_stability += reduction_factor * 0.25
            self.visual_metrics.tracking_stability = min(1.0, self.visual_metrics.tracking_stability)
        
        if config.lag_reduction_enabled:
            # Reduce response lag
            lag_reduction = config.sterplistic_concentration * 50.0  # ms reduction
            self.visual_metrics.response_lag_ms *= (1.0 - config.sterplistic_concentration * 0.3)
            self.visual_metrics.response_lag_ms = max(50.0, self.visual_metrics.response_lag_ms)
    
    def get_electrolyte_status(self) -> Dict[str, Any]:
        """Get current electrolyte status summary"""
        status = {}
        for electrolyte_type, level in self.electrolyte_levels.items():
            status[electrolyte_type.value] = {
                'current_level': level.current_level,
                'optimal_level': level.optimal_level,
                'deficit': level.get_deficit(),
                'status': level.get_status(),
                'net_change': level.production_rate - level.consumption_rate
            }
        return status
    
    def get_visual_status(self) -> Dict[str, Any]:
        """Get current visual stabilization status"""
        return {
            'dissociation_level': self.visual_metrics.dissociation_level,
            'response_lag_ms': self.visual_metrics.response_lag_ms,
            'visual_clarity': self.visual_metrics.visual_clarity,
            'tracking_stability': self.visual_metrics.tracking_stability,
            'overall_stability': self.visual_metrics.get_overall_stability()
        }
    
    def save_configuration(self, filename: str) -> bool:
        """Save current modifier configuration to JSON file"""
        try:
            config_data = {
                'active_modifiers': {k: v.to_json() for k, v in self.active_modifiers.items()},
                'electrolyte_levels': {k.value: asdict(v) for k, v in self.electrolyte_levels.items()},
                'visual_metrics': asdict(self.visual_metrics),
                'modification_history': self.modification_history[-10:]  # Last 10 modifications
            }
            
            with open(filename, 'w') as f:
                json.dump(config_data, f, indent=2, default=str)
            
            return True
        except Exception as e:
            print(f"Error saving configuration: {e}")
            return False
    
    def load_configuration(self, filename: str) -> bool:
        """Load modifier configuration from JSON file"""
        try:
            with open(filename, 'r') as f:
                config_data = json.load(f)
            
            # Load active modifiers
            for modifier_id, config_json in config_data.get('active_modifiers', {}).items():
                self.active_modifiers[modifier_id] = ModifierConfiguration.from_json(config_json)
            
            # Load electrolyte levels
            for electrolyte_str, level_data in config_data.get('electrolyte_levels', {}).items():
                electrolyte_type = ElectrolyteType(electrolyte_str)
                level_data['electrolyte_type'] = electrolyte_type
                self.electrolyte_levels[electrolyte_type] = ElectrolyteLevel(**level_data)
            
            # Load visual metrics
            if 'visual_metrics' in config_data:
                self.visual_metrics = VisualStabilizationMetrics(**config_data['visual_metrics'])
            
            return True
        except Exception as e:
            print(f"Error loading configuration: {e}")
            return False
    
    def remove_modifier(self, modifier_id: str) -> bool:
        """Remove an active modifier"""
        if modifier_id in self.active_modifiers:
            del self.active_modifiers[modifier_id]
            
            # Record in history
            self.modification_history.append({
                'timestamp': time.time(),
                'action': 'remove_modifier',
                'modifier_id': modifier_id
            })
            
            return True
        return False
    
    def get_system_summary(self) -> Dict[str, Any]:
        """Get complete system status summary"""
        return {
            'active_modifiers': list(self.active_modifiers.keys()),
            'electrolyte_status': self.get_electrolyte_status(),
            'visual_status': self.get_visual_status(),
            'total_modifications': len(self.modification_history)
        }
