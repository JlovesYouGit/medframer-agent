#!/usr/bin/env python3
"""
Advanced Baseline Adjustment System
Fine-tunes oxygen efficiency and pH to prevent lung strain
Optimizes long-term effects through volumetric tuning
"""

import time
import json
import math
import numpy as np
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass
from enum import Enum

class AdjustmentType(Enum):
    OXYGEN_EFFICIENCY = "oxygen_efficiency"
    PH_BALANCE = "ph_balance"
    LUNG_STRAIN = "lung_strain"
    VOLUMETRIC_TUNING = "volumetric_tuning"
    LONG_TERM_OPTIMIZATION = "long_term_optimization"

class AdjustmentIntensity(Enum):
    MINIMAL = "minimal"
    MODERATE = "moderate"
    SIGNIFICANT = "significant"
    PRECISE = "precise"

@dataclass
class OxygenEfficiencyProfile:
    """Profile for oxygen efficiency optimization"""
    current_efficiency: float  # 0-1
    target_efficiency: float    # 0-1
    lung_strain_factor: float   # 0-1
    oxygen_saturation: float    # 0-1
    metabolic_rate: float       # relative
    adjustment_rate: float      # change per cycle

@dataclass
class PHBalanceProfile:
    """Profile for pH balance optimization"""
    current_ph: float          # pH units
    target_ph: float           # pH units
    buffer_capacity: float     # 0-1
    acid_base_balance: float    # -1 to 1
    respiratory_compensation: float  # 0-1

@dataclass
class VolumetricTuning:
    """Volumetric tuning parameters"""
    lung_volume_optimal: float  # L
    tidal_volume: float        # L
    breathing_rate: float      # breaths/min
    dead_space_ratio: float    # 0-1
    alveolar_ventilation: float # L/min

@dataclass
class BaselineAdjustment:
    """Baseline adjustment configuration"""
    adjustment_id: str
    adjustment_type: AdjustmentType
    intensity: AdjustmentIntensity
    current_value: float
    target_value: float
    adjustment_rate: float
    max_safe_change: float
    long_term_sustainability: float  # 0-1

class AdvancedBaselineAdjuster:
    """
    Advanced system for adjusting baselines to prevent lung strain
    Optimizes oxygen efficiency and pH through volumetric tuning
    """
    
    def __init__(self):
        self.current_baselines = self._initialize_current_baselines()
        self.adjustment_history: List[Dict[str, Any]] = []
        self.oxygen_profile = self._initialize_oxygen_profile()
        self.ph_profile = self._initialize_ph_profile()
        self.volumetric_tuning = self._initialize_volumetric_tuning()
        self.adjustment_session_id = f"baseline_adjust_{int(time.time())}"
        self.safety_constraints = self._initialize_safety_constraints()
        
    def _initialize_current_baselines(self) -> Dict[str, float]:
        """Initialize current baseline values"""
        return {
            "oxygen_efficiency": 0.75,  # Current oxygen utilization efficiency
            "oxygen_saturation": 0.95,  # Blood oxygen saturation
            "ph_level": 7.40,           # Blood pH
            "lung_capacity": 4.5,       # Liters
            "tidal_volume": 0.5,        # Liters per breath
            "breathing_rate": 16,       # Breaths per minute
            "lung_strain_index": 0.15,  # Current lung strain (0-1)
            "metabolic_rate": 1.0,      # Relative metabolic rate
            "cellular_oxygen_demand": 0.8  # Cellular oxygen demand
        }
    
    def _initialize_oxygen_profile(self) -> OxygenEfficiencyProfile:
        """Initialize oxygen efficiency profile"""
        return OxygenEfficiencyProfile(
            current_efficiency=self.current_baselines["oxygen_efficiency"],
            target_efficiency=0.85,  # Slightly higher but safe target
            lung_strain_factor=self.current_baselines["lung_strain_index"],
            oxygen_saturation=self.current_baselines["oxygen_saturation"],
            metabolic_rate=self.current_baselines["metabolic_rate"],
            adjustment_rate=0.02  # 2% adjustment per cycle
        )
    
    def _initialize_ph_profile(self) -> PHBalanceProfile:
        """Initialize pH balance profile"""
        return PHBalanceProfile(
            current_ph=self.current_baselines["ph_level"],
            target_ph=7.42,  # Slightly alkaline for better oxygen binding
            buffer_capacity=0.8,
            acid_base_balance=0.1,  # Slightly alkaline
            respiratory_compensation=0.7
        )
    
    def _initialize_volumetric_tuning(self) -> VolumetricTuning:
        """Initialize volumetric tuning parameters"""
        return VolumetricTuning(
            lung_volume_optimal=self.current_baselines["lung_capacity"],
            tidal_volume=self.current_baselines["tidal_volume"],
            breathing_rate=self.current_baselines["breathing_rate"],
            dead_space_ratio=0.3,  # Normal anatomical dead space
            alveolar_ventilation=self.current_baselines["tidal_volume"] * 
                               self.current_baselines["breathing_rate"] * 0.7  # Minus dead space
        )
    
    def _initialize_safety_constraints(self) -> Dict[str, Dict[str, float]]:
        """Initialize safety constraints for adjustments"""
        return {
            "oxygen_efficiency": {
                "min_safe": 0.6,
                "max_safe": 0.9,
                "optimal_range": (0.75, 0.85),
                "max_change_rate": 0.05  # Max 5% change per cycle
            },
            "ph_level": {
                "min_safe": 7.35,
                "max_safe": 7.45,
                "optimal_range": (7.38, 7.42),
                "max_change_rate": 0.02  # Max 0.02 pH units per cycle
            },
            "lung_strain": {
                "min_safe": 0.0,
                "max_safe": 0.3,
                "optimal_range": (0.05, 0.15),
                "max_change_rate": 0.03  # Max 3% change per cycle
            },
            "breathing_rate": {
                "min_safe": 12,
                "max_safe": 20,
                "optimal_range": (14, 16),
                "max_change_rate": 1.0  # Max 1 breath/min per cycle
            }
        }
    
    def perform_volumetric_tuning(self) -> Dict[str, Any]:
        """Perform volumetric tuning to optimize oxygen efficiency"""
        print(f"🎯 PERFORMING VOLUMETRIC TUNING")
        print("=" * 50)
        
        tuning_results = {}
        
        # Step 1: Analyze current oxygen efficiency
        print(f"\n📊 STEP 1: ANALYZING CURRENT OXYGEN EFFICIENCY")
        current_analysis = self._analyze_current_oxygen_state()
        tuning_results["current_analysis"] = current_analysis
        
        # Step 2: Calculate optimal adjustments
        print(f"\n🧮 STEP 2: CALCULATING OPTIMAL ADJUSTMENTS")
        optimal_adjustments = self._calculate_optimal_adjustments(current_analysis)
        tuning_results["optimal_adjustments"] = optimal_adjustments
        
        # Step 3: Apply volumetric tuning
        print(f"\n⚙️ STEP 3: APPLYING VOLUMETRIC TUNING")
        applied_tuning = self._apply_volumetric_tuning(optimal_adjustments)
        tuning_results["applied_tuning"] = applied_tuning
        
        # Step 4: Validate lung strain
        print(f"\n🫁 STEP 4: VALIDATING LUNG STRAIN")
        lung_validation = self._validate_lung_strain(applied_tuning)
        tuning_results["lung_validation"] = lung_validation
        
        # Step 5: Optimize pH balance
        print(f"\n⚖️ STEP 5: OPTIMIZING PH BALANCE")
        ph_optimization = self._optimize_ph_balance(applied_tuning)
        tuning_results["ph_optimization"] = ph_optimization
        
        # Step 6: Long-term sustainability check
        print(f"\n🔄 STEP 6: LONG-TERM SUSTAINABILITY CHECK")
        sustainability_check = self._check_long_term_sustainability(tuning_results)
        tuning_results["sustainability"] = sustainability_check
        
        print(f"\n✅ VOLUMETRIC TUNING COMPLETED")
        print(f"  Oxygen efficiency: {self.oxygen_profile.current_efficiency:.3f}")
        print(f"  Lung strain: {self.oxygen_profile.lung_strain_factor:.3f}")
        print(f"  pH level: {self.ph_profile.current_ph:.3f}")
        print(f"  Sustainability: {sustainability_check['sustainability_score']:.3f}")
        
        return tuning_results
    
    def _analyze_current_oxygen_state(self) -> Dict[str, Any]:
        """Analyze current oxygen utilization state"""
        print("  Analyzing current oxygen utilization...")
        
        # Calculate oxygen utilization metrics
        oxygen_delivery = self.volumetric_tuning.alveolar_ventilation * self.oxygen_profile.oxygen_saturation
        oxygen_consumption = self.current_baselines["cellular_oxygen_demand"] * self.oxygen_profile.metabolic_rate
        utilization_efficiency = oxygen_consumption / oxygen_delivery if oxygen_delivery > 0 else 0
        
        # Assess lung strain
        breathing_work = (self.volumetric_tuning.tidal_volume ** 2) * self.volumetric_tuning.breathing_rate
        lung_strain = breathing_work / 100.0  # Normalized to 0-1
        
        # Update profiles
        self.oxygen_profile.current_efficiency = utilization_efficiency
        self.oxygen_profile.lung_strain_factor = lung_strain
        
        analysis = {
            "oxygen_delivery": oxygen_delivery,
            "oxygen_consumption": oxygen_consumption,
            "utilization_efficiency": utilization_efficiency,
            "breathing_work": breathing_work,
            "lung_strain": lung_strain,
            "current_status": "optimal" if 0.7 < utilization_efficiency < 0.85 and lung_strain < 0.2 else "needs_adjustment"
        }
        
        print(f"    Oxygen delivery: {oxygen_delivery:.3f} L/min")
        print(f"    Oxygen consumption: {oxygen_consumption:.3f} L/min")
        print(f"    Utilization efficiency: {utilization_efficiency:.3f}")
        print(f"    Lung strain: {lung_strain:.3f}")
        print(f"    Status: {analysis['current_status']}")
        
        return analysis
    
    def _calculate_optimal_adjustments(self, current_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate optimal adjustments within safety constraints"""
        print("  Calculating optimal adjustments...")
        
        adjustments = {}
        
        # Oxygen efficiency adjustment
        current_eff = current_analysis["utilization_efficiency"]
        target_eff = 0.82  # Slightly lower than previous target to reduce strain
        
        if current_eff < target_eff:
            # Need to improve efficiency
            eff_adjustment = min(target_eff - current_eff, 
                               self.safety_constraints["oxygen_efficiency"]["max_change_rate"])
            adjustments["oxygen_efficiency"] = eff_adjustment
        else:
            adjustments["oxygen_efficiency"] = 0.0
        
        # Breathing rate adjustment
        current_rate = self.volumetric_tuning.breathing_rate
        optimal_rate = 14.0  # Slightly lower to reduce strain
        
        if abs(current_rate - optimal_rate) > 0.5:
            rate_adjustment = np.clip(optimal_rate - current_rate,
                                    -self.safety_constraints["breathing_rate"]["max_change_rate"],
                                    self.safety_constraints["breathing_rate"]["max_change_rate"])
            adjustments["breathing_rate"] = rate_adjustment
        else:
            adjustments["breathing_rate"] = 0.0
        
        # Tidal volume adjustment
        current_tv = self.volumetric_tuning.tidal_volume
        optimal_tv = 0.45  # Slightly smaller to reduce strain
        
        if abs(current_tv - optimal_tv) > 0.05:
            tv_adjustment = np.clip(optimal_tv - current_tv, -0.02, 0.02)
            adjustments["tidal_volume"] = tv_adjustment
        else:
            adjustments["tidal_volume"] = 0.0
        
        # pH adjustment
        current_ph = self.ph_profile.current_ph
        target_ph = 7.40  # Back to neutral to reduce strain
        
        if abs(current_ph - target_ph) > 0.01:
            ph_adjustment = np.clip(target_ph - current_ph,
                                  -self.safety_constraints["ph_level"]["max_change_rate"],
                                  self.safety_constraints["ph_level"]["max_change_rate"])
            adjustments["ph_level"] = ph_adjustment
        else:
            adjustments["ph_level"] = 0.0
        
        print(f"    Oxygen efficiency adjustment: {adjustments['oxygen_efficiency']:.3f}")
        print(f"    Breathing rate adjustment: {adjustments['breathing_rate']:.1f} breaths/min")
        print(f"    Tidal volume adjustment: {adjustments['tidal_volume']:.3f} L")
        print(f"    pH level adjustment: {adjustments['ph_level']:.3f}")
        
        return adjustments
    
    def _apply_volumetric_tuning(self, adjustments: Dict[str, Any]) -> Dict[str, Any]:
        """Apply volumetric tuning adjustments"""
        print("  Applying volumetric tuning adjustments...")
        
        applied = {}
        
        # Apply oxygen efficiency adjustment
        if adjustments["oxygen_efficiency"] != 0:
            old_eff = self.oxygen_profile.current_efficiency
            new_eff = np.clip(old_eff + adjustments["oxygen_efficiency"],
                             self.safety_constraints["oxygen_efficiency"]["min_safe"],
                             self.safety_constraints["oxygen_efficiency"]["max_safe"])
            self.oxygen_profile.current_efficiency = new_eff
            applied["oxygen_efficiency"] = {"old": old_eff, "new": new_eff, "change": new_eff - old_eff}
        
        # Apply breathing rate adjustment
        if adjustments["breathing_rate"] != 0:
            old_rate = self.volumetric_tuning.breathing_rate
            new_rate = np.clip(old_rate + adjustments["breathing_rate"],
                             self.safety_constraints["breathing_rate"]["min_safe"],
                             self.safety_constraints["breathing_rate"]["max_safe"])
            self.volumetric_tuning.breathing_rate = new_rate
            applied["breathing_rate"] = {"old": old_rate, "new": new_rate, "change": new_rate - old_rate}
        
        # Apply tidal volume adjustment
        if adjustments["tidal_volume"] != 0:
            old_tv = self.volumetric_tuning.tidal_volume
            new_tv = np.clip(old_tv + adjustments["tidal_volume"], 0.3, 0.7)
            self.volumetric_tuning.tidal_volume = new_tv
            applied["tidal_volume"] = {"old": old_tv, "new": new_tv, "change": new_tv - old_tv}
        
        # Apply pH adjustment
        if adjustments["ph_level"] != 0:
            old_ph = self.ph_profile.current_ph
            new_ph = np.clip(old_ph + adjustments["ph_level"],
                            self.safety_constraints["ph_level"]["min_safe"],
                            self.safety_constraints["ph_level"]["max_safe"])
            self.ph_profile.current_ph = new_ph
            applied["ph_level"] = {"old": old_ph, "new": new_ph, "change": new_ph - old_ph}
        
        # Recalculate alveolar ventilation
        old_av = self.volumetric_tuning.alveolar_ventilation
        self.volumetric_tuning.alveolar_ventilation = (
            self.volumetric_tuning.tidal_volume * 
            self.volumetric_tuning.breathing_rate * 
            (1 - self.volumetric_tuning.dead_space_ratio)
        )
        applied["alveolar_ventilation"] = {
            "old": old_av, 
            "new": self.volumetric_tuning.alveolar_ventilation, 
            "change": self.volumetric_tuning.alveolar_ventilation - old_av
        }
        
        print(f"    Applied adjustments: {len(applied)} parameters")
        
        return applied
    
    def _validate_lung_strain(self, applied_tuning: Dict[str, Any]) -> Dict[str, Any]:
        """Validate lung strain after adjustments"""
        print("  Validating lung strain...")
        
        # Recalculate lung strain
        breathing_work = (self.volumetric_tuning.tidal_volume ** 2) * self.volumetric_tuning.breathing_rate
        new_lung_strain = breathing_work / 100.0
        
        # Compare with safety limits
        safety_check = {
            "within_safe_limits": new_lung_strain <= self.safety_constraints["lung_strain"]["max_safe"],
            "strain_reduction": self.oxygen_profile.lung_strain_factor - new_lung_strain,
            "strain_level": "low" if new_lung_strain < 0.1 else "moderate" if new_lung_strain < 0.2 else "high",
            "acceptable": new_lung_strain < 0.2
        }
        
        # Update lung strain factor
        old_strain = self.oxygen_profile.lung_strain_factor
        self.oxygen_profile.lung_strain_factor = new_lung_strain
        
        validation = {
            "old_strain": old_strain,
            "new_strain": new_lung_strain,
            "strain_change": new_lung_strain - old_strain,
            "safety_check": safety_check
        }
        
        print(f"    Old lung strain: {old_strain:.3f}")
        print(f"    New lung strain: {new_lung_strain:.3f}")
        print(f"    Strain level: {safety_check['strain_level']}")
        print(f"    Within safe limits: {safety_check['within_safe_limits']}")
        
        return validation
    
    def _optimize_ph_balance(self, applied_tuning: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize pH balance for better oxygen binding"""
        print("  Optimizing pH balance...")
        
        # Calculate optimal pH for current oxygen efficiency
        target_ph = 7.40  # Standard physiological pH
        
        # Apply fine adjustment if needed
        current_ph = self.ph_profile.current_ph
        ph_difference = target_ph - current_ph
        
        if abs(ph_difference) > 0.005:
            # Fine adjustment needed
            adjustment = np.clip(ph_difference * 0.5, -0.01, 0.01)
            new_ph = current_ph + adjustment
            
            # Update profile
            old_ph = self.ph_profile.current_ph
            self.ph_profile.current_ph = new_ph
            
            optimization = {
                "old_ph": old_ph,
                "new_ph": new_ph,
                "adjustment": adjustment,
                "oxygen_binding_optimization": self._calculate_oxygen_binding_optimization(new_ph)
            }
        else:
            optimization = {
                "status": "optimal",
                "current_ph": current_ph,
                "oxygen_binding_optimization": self._calculate_oxygen_binding_optimization(current_ph)
            }
        
        print(f"    Current pH: {self.ph_profile.current_ph:.3f}")
        print(f"    Oxygen binding optimization: {optimization.get('oxygen_binding_optimization', 0):.3f}")
        
        return optimization
    
    def _calculate_oxygen_binding_optimization(self, ph: float) -> float:
        """Calculate oxygen binding optimization based on pH"""
        # Bohr effect: lower pH reduces oxygen binding affinity
        # Optimal pH for oxygen binding is around 7.4
        ph_deviation = abs(ph - 7.4)
        binding_optimization = 1.0 - (ph_deviation * 0.5)  # Scale to 0-1
        return max(0.0, min(1.0, binding_optimization))
    
    def _check_long_term_sustainability(self, tuning_results: Dict[str, Any]) -> Dict[str, Any]:
        """Check long-term sustainability of adjustments"""
        print("  Checking long-term sustainability...")
        
        # Calculate sustainability score
        factors = {
            "lung_strain_sustainability": 1.0 - self.oxygen_profile.lung_strain_factor,
            "oxygen_efficiency_sustainability": self.oxygen_profile.current_efficiency,
            "ph_stability": 1.0 - abs(self.ph_profile.current_ph - 7.4),
            "breathing_pattern_stability": 1.0 - abs(self.volumetric_tuning.breathing_rate - 14.0) / 6.0,
            "volumetric_efficiency": min(1.0, self.volumetric_tuning.alveolar_ventilation / 4.0)
        }
        
        sustainability_score = sum(factors.values()) / len(factors)
        
        # Determine sustainability level
        if sustainability_score > 0.8:
            sustainability_level = "excellent"
        elif sustainability_score > 0.6:
            sustainability_level = "good"
        elif sustainability_score > 0.4:
            sustainability_level = "moderate"
        else:
            sustainability_level = "poor"
        
        # Generate recommendations
        recommendations = []
        if factors["lung_strain_sustainability"] < 0.7:
            recommendations.append("Further reduce breathing rate to minimize lung strain")
        if factors["oxygen_efficiency_sustainability"] < 0.7:
            recommendations.append("Gradually improve oxygen utilization efficiency")
        if factors["ph_stability"] < 0.8:
            recommendations.append("Maintain pH balance within optimal range")
        
        sustainability_check = {
            "sustainability_score": sustainability_score,
            "sustainability_level": sustainability_level,
            "factors": factors,
            "recommendations": recommendations,
            "long_term_viable": sustainability_score > 0.6
        }
        
        print(f"    Sustainability score: {sustainability_score:.3f}")
        print(f"    Sustainability level: {sustainability_level}")
        print(f"    Long-term viable: {sustainability_check['long_term_viable']}")
        
        return sustainability_check
    
    def get_adjusted_baselines(self) -> Dict[str, float]:
        """Get adjusted baseline values"""
        return {
            "oxygen_efficiency": self.oxygen_profile.current_efficiency,
            "oxygen_saturation": self.oxygen_profile.oxygen_saturation,
            "ph_level": self.ph_profile.current_ph,
            "lung_capacity": self.volumetric_tuning.lung_volume_optimal,
            "tidal_volume": self.volumetric_tuning.tidal_volume,
            "breathing_rate": self.volumetric_tuning.breathing_rate,
            "lung_strain_index": self.oxygen_profile.lung_strain_factor,
            "metabolic_rate": self.oxygen_profile.metabolic_rate,
            "alveolar_ventilation": self.volumetric_tuning.alveolar_ventilation
        }
    
    def export_adjustment_data(self, filename: str = None) -> str:
        """Export adjustment data"""
        if filename is None:
            filename = f"baseline_adjustment_{self.adjustment_session_id}.json"
        
        export_data = {
            "session_info": {
                "session_id": self.adjustment_session_id,
                "timestamp": time.time()
            },
            "original_baselines": self.current_baselines,
            "adjusted_baselines": self.get_adjusted_baselines(),
            "oxygen_profile": {
                "current_efficiency": self.oxygen_profile.current_efficiency,
                "target_efficiency": self.oxygen_profile.target_efficiency,
                "lung_strain_factor": self.oxygen_profile.lung_strain_factor,
                "oxygen_saturation": self.oxygen_profile.oxygen_saturation
            },
            "ph_profile": {
                "current_ph": self.ph_profile.current_ph,
                "target_ph": self.ph_profile.target_ph,
                "buffer_capacity": self.ph_profile.buffer_capacity
            },
            "volumetric_tuning": {
                "lung_volume_optimal": self.volumetric_tuning.lung_volume_optimal,
                "tidal_volume": self.volumetric_tuning.tidal_volume,
                "breathing_rate": self.volumetric_tuning.breathing_rate,
                "alveolar_ventilation": self.volumetric_tuning.alveolar_ventilation
            },
            "safety_constraints": self.safety_constraints
        }
        
        with open(filename, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        print(f"  Adjustment data exported to: {filename}")
        return filename


def demonstrate_advanced_baseline_adjustment():
    """Demonstrate the advanced baseline adjustment system"""
    print("🎯 ADVANCED BASELINE ADJUSTMENT DEMONSTRATION")
    print("=" * 80)
    
    # Initialize adjuster
    adjuster = AdvancedBaselineAdjuster()
    
    # Display current baselines
    print(f"\n{'='*60}")
    print(f"CURRENT BASELINES")
    print(f"{'='*60}")
    
    current_baselines = adjuster.current_baselines
    print(f"  Oxygen efficiency: {current_baselines['oxygen_efficiency']:.3f}")
    print(f"  Oxygen saturation: {current_baselines['oxygen_saturation']:.3f}")
    print(f"  pH level: {current_baselines['ph_level']:.3f}")
    print(f"  Lung strain index: {current_baselines['lung_strain_index']:.3f}")
    print(f"  Breathing rate: {current_baselines['breathing_rate']:.1f} breaths/min")
    print(f"  Tidal volume: {current_baselines['tidal_volume']:.3f} L")
    
    # Perform volumetric tuning
    print(f"\n{'='*60}")
    print(f"VOLUMETRIC TUNING")
    print(f"{'='*60}")
    
    tuning_results = adjuster.perform_volumetric_tuning()
    
    # Display adjusted baselines
    print(f"\n{'='*60}")
    print(f"ADJUSTED BASELINES")
    print(f"{'='*60}")
    
    adjusted_baselines = adjuster.get_adjusted_baselines()
    print(f"  Oxygen efficiency: {adjusted_baselines['oxygen_efficiency']:.3f}")
    print(f"  Oxygen saturation: {adjusted_baselines['oxygen_saturation']:.3f}")
    print(f"  pH level: {adjusted_baselines['ph_level']:.3f}")
    print(f"  Lung strain index: {adjusted_baselines['lung_strain_index']:.3f}")
    print(f"  Breathing rate: {adjusted_baselines['breathing_rate']:.1f} breaths/min")
    print(f"  Tidal volume: {adjusted_baselines['tidal_volume']:.3f} L")
    print(f"  Alveolar ventilation: {adjusted_baselines['alveolar_ventilation']:.3f} L/min")
    
    # Display key improvements
    print(f"\n{'='*60}")
    print(f"KEY IMPROVEMENTS")
    print(f"{'='*60}")
    
    improvements = {
        "Lung strain reduction": current_baselines['lung_strain_index'] - adjusted_baselines['lung_strain_index'],
        "Breathing rate optimization": current_baselines['breathing_rate'] - adjusted_baselines['breathing_rate'],
        "pH stabilization": abs(7.4 - adjusted_baselines['ph_level']),
        "Oxygen efficiency": adjusted_baselines['oxygen_efficiency'] - current_baselines['oxygen_efficiency']
    }
    
    for metric, change in improvements.items():
        status = "✅ Improved" if change > 0 else "⚠️ Adjusted"
        print(f"  {metric}: {change:.3f} ({status})")
    
    # Display sustainability
    sustainability = tuning_results["sustainability"]
    print(f"\n🔄 LONG-TERM SUSTAINABILITY:")
    print(f"  Score: {sustainability['sustainability_score']:.3f}")
    print(f"  Level: {sustainability['sustainability_level']}")
    print(f"  Long-term viable: {sustainability['long_term_viable']}")
    
    # Export data
    export_file = adjuster.export_adjustment_data()
    print(f"\n📁 Adjustment data exported: {export_file}")
    
    return adjuster


if __name__ == "__main__":
    demonstrate_advanced_baseline_adjustment()
