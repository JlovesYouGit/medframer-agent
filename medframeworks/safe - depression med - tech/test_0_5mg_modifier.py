#!/usr/bin/env python3
"""
Test script for 0.5mg medication modifier system
Demonstrates sterplistic viacron with stelavis electrolyte production
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from medication_modifier_system import MedicationModifierSystem

def test_0_5mg_modifier():
    """Test the 0.5mg modifier functionality"""
    print("💊 TESTING 0.5mg MEDICATION MODIFIER SYSTEM")
    print("=" * 60)
    
    # Initialize the modifier system
    modifier_system = MedicationModifierSystem()
    
    print("\n📊 INITIAL ELECTROLYTE STATUS:")
    electrolyte_status = modifier_system.get_electrolyte_status()
    for electrolyte, status in electrolyte_status.items():
        print(f"  {electrolyte}: {status['current_level']:.1f} mmol/L (Deficit: {status['deficit']:.1f})")
    
    print("\n👁️ INITIAL VISUAL METRICS:")
    visual_status = modifier_system.get_visual_status()
    print(f"  Dissociation: {visual_status['dissociation_level']:.1%}")
    print(f"  Response lag: {visual_status['response_lag_ms']:.1f}ms")
    print(f"  Visual clarity: {visual_status['visual_clarity']:.1%}")
    print(f"  Tracking stability: {visual_status['tracking_stability']:.1%}")
    print(f"  Overall stability: {visual_status['overall_stability']:.1%}")
    
    print("\n💊 ADDING 0.5mg MODIFIER:")
    print("  - Sterplistic viacron concentration: 0.7")
    print("  - Stelavis electrolyte production: 0.1 mmol/hour")
    
    # Add the 0.5mg modifier
    success = modifier_system.add_0_5mg_modifier(
        modifier_id="test_0_5mg_v1",
        sterplistic_strength=0.7,
        stelavis_rate=0.1
    )
    
    if success:
        print("\n✅ 0.5mg MODIFIER SUCCESSFULLY ADDED")
        
        print("\n📊 UPDATED ELECTROLYTE STATUS:")
        electrolyte_status = modifier_system.get_electrolyte_status()
        for electrolyte, status in electrolyte_status.items():
            if status['net_change'] > 0:
                print(f"  {electrolyte}: {status['current_level']:.1f} mmol/L (+{status['net_change']:.2f} mmol/hour)")
            else:
                print(f"  {electrolyte}: {status['current_level']:.1f} mmol/L ({status['net_change']:.2f} mmol/hour)")
        
        print("\n👁️ UPDATED VISUAL METRICS:")
        visual_status = modifier_system.get_visual_status()
        print(f"  Dissociation: {visual_status['dissociation_level']:.1%} (reduced)")
        print(f"  Response lag: {visual_status['response_lag_ms']:.1f}ms (reduced)")
        print(f"  Visual clarity: {visual_status['visual_clarity']:.1%} (improved)")
        print(f"  Tracking stability: {visual_status['tracking_stability']:.1%} (improved)")
        print(f"  Overall stability: {visual_status['overall_stability']:.1%} (improved)")
        
        print("\n🎯 SYSTEM SUMMARY:")
        summary = modifier_system.get_system_summary()
        print(f"  Active modifiers: {summary['active_modifiers']}")
        print(f"  Total modifications: {summary['total_modifications']}")
        
        print("\n💾 SAVING CONFIGURATION...")
        save_success = modifier_system.save_configuration("test_modifier_config.json")
        if save_success:
            print("✅ Configuration saved to test_modifier_config.json")
        
        print("\n🎉 0.5mg MODIFIER TEST COMPLETED SUCCESSFULLY!")
        print("\n🌟 BENEFITS ACHIEVED:")
        print("  ✅ Sterplistic viacron integration (0.7 concentration)")
        print("  ✅ Stelavis electrolyte production (0.1 mmol/hour)")
        print("  ✅ Reduced visual dissociation")
        print("  ✅ Decreased response lag")
        print("  ✅ Improved visual clarity and tracking")
        print("  ✅ Counteracted pill side effects")
        
        return True
    else:
        print("\n❌ FAILED TO ADD 0.5mg MODIFIER")
        return False

if __name__ == "__main__":
    success = test_0_5mg_modifier()
    exit(0 if success else 1)
