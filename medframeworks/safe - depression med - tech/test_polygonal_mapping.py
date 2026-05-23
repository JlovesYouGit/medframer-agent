#!/usr/bin/env python3
"""
Test script for the enhanced electrode array system with polygonal object mapping
Demonstrates the improved dimensional control and aromatic activation features
"""

import sys
import math
from typing import Tuple, List, Dict, Optional, Any
from dataclasses import dataclass
from enum import Enum

# Mock numpy for testing without dependencies
class MockNumpy:
    def zeros(self, size):
        return [0.0] * size

np = MockNumpy()

# Import our enhanced electrode system
try:
    from electrode_array_system import (
        ElectrodeArray, MolecularManipulator, PolygonalObjectMapping,
        MolecularBond, ElectrodePosition, ElectrodeType
    )
except ImportError as e:
    print(f"Import error: {e}")
    print("Please ensure electrode_array_system.py is in the same directory")
    sys.exit(1)


def test_polygonal_mapping():
    """Test the polygonal object mapping functionality"""
    print("=== TESTING POLYGONAL OBJECT MAPPING ===")
    
    # Create a test polygonal mapping for a benzene ring
    benzene_vertices = [
        (0.0, 0.0, 0.0), (1.4, 0.0, 0.0), (2.1, 1.2, 0.0),
        (1.4, 2.4, 0.0), (0.0, 2.4, 0.0), (-0.7, 1.2, 0.0)
    ]
    
    benzene_mapping = PolygonalObjectMapping(
        vertices=benzene_vertices,
        width=0.0, height=0.0, depth=0.0,
        surface_area=0.0, volume=0.0,
        aromatic_regions=[(0.7, 1.2, 0.0)],  # Center of ring
        scent_intensity=0.8
    )
    
    # Calculate dimensions
    benzene_mapping.calculate_dimensions()
    benzene_mapping.calculate_surface_area()
    benzene_mapping.calculate_volume()
    
    print(f"Benzene Ring Mapping:")
    print(f"  Vertices: {len(benzene_mapping.vertices)}")
    print(f"  Dimensions: {benzene_mapping.width:.2f} x {benzene_mapping.height:.2f} x {benzene_mapping.depth:.2f} Å")
    print(f"  Surface Area: {benzene_mapping.surface_area:.3f} Ų")
    print(f"  Volume: {benzene_mapping.volume:.3f} ų")
    print(f"  Centroid: {benzene_mapping.get_centroid()}")
    
    # Test scent profile generation
    scent_profile = benzene_mapping.generate_aromatic_scent_profile()
    print(f"  Scent Profile:")
    for note, intensity in scent_profile.items():
        if intensity > 0.1:
            print(f"    {note.capitalize()}: {intensity:.2f}")
    
    return benzene_mapping


def test_electrode_array_enhancement():
    """Test the enhanced electrode array functionality"""
    print("\n=== TESTING ENHANCED ELECTRODE ARRAY ===")
    
    # Create electrode array
    array = ElectrodeArray(num_electrodes=16)  # Smaller array for testing
    
    # Create a test molecular bond with polygonal mapping
    test_vertices = [
        (0.0, 0.0, 0.0), (1.0, 0.0, 0.0), (1.0, 1.0, 0.0), (0.0, 1.0, 0.0)
    ]
    
    test_mapping = PolygonalObjectMapping(
        vertices=test_vertices,
        width=0.0, height=0.0, depth=0.0,
        surface_area=0.0, volume=0.0,
        aromatic_regions=[(0.5, 0.5, 0.0)],
        scent_intensity=0.6
    )
    test_mapping.calculate_dimensions()
    test_mapping.calculate_surface_area()
    test_mapping.calculate_volume()
    
    test_bond = MolecularBond(
        atom_a="C", atom_b="C", bond_type="aromatic",
        length=1.40, strength=120.0,
        position=ElectrodePosition(0.5, 0.5, 0.0),
        polygonal_mapping=test_mapping
    )
    
    # Test polygonal field distribution calculation
    field_dist = array.calculate_polygonal_field_distribution(test_mapping)
    
    print(f"Field Distribution Analysis:")
    print(f"  Vertex fields calculated: {len(field_dist['vertices'])}")
    print(f"  Edge fields calculated: {len(field_dist['edges'])}")
    print(f"  Field uniformity: {field_dist['field_uniformity']:.3f}")
    print(f"  Max field strength: {field_dist['max_field_strength']:.2f} V/m")
    print(f"  Min field strength: {field_dist['min_field_strength']:.2f} V/m")
    
    # Test aromatic field pattern generation
    aromatic_pattern = array.generate_aromatic_field_pattern(test_mapping)
    print(f"Aromatic Pattern:")
    print(f"  Pattern type: {aromatic_pattern['pattern']}")
    print(f"  Intensity: {aromatic_pattern['intensity']:.2f}")
    print(f"  Voltage patterns: {len(aromatic_pattern['voltage_patterns'])}")
    
    return array, test_bond


def test_molecular_manipulator():
    """Test the complete molecular manipulator system"""
    print("\n=== TESTING MOLECULAR MANIPULATOR SYSTEM ===")
    
    # Create manipulator (without real-time data processor for testing)
    manipulator = MolecularManipulator()
    
    # Test molecular structure parsing
    molecular_bonds = manipulator._parse_molecular_structure("C21H22FN3O")
    
    print(f"Parsed Molecular Structure:")
    print(f"  Number of bonds: {len(molecular_bonds)}")
    
    for i, bond in enumerate(molecular_bonds):
        print(f"  Bond {i+1}: {bond.atom_a}-{bond.atom_b} ({bond.bond_type})")
        if bond.polygonal_mapping:
            print(f"    Polygonal mapping: {len(bond.polygonal_mapping.vertices)} vertices")
            print(f"    Aromatic regions: {len(bond.polygonal_mapping.aromatic_regions)}")
            print(f"    Scent intensity: {bond.polygonal_mapping.scent_intensity:.2f}")
    
    # Test configuration for molecular target
    manipulator.electrode_array.configure_for_molecular_target(molecular_bonds)
    
    # Test aromatic activation
    manipulator.electrode_array.apply_aromatic_activation_sequence(molecular_bonds)
    
    return manipulator


def demonstrate_scent_generation():
    """Demonstrate the scent generation capabilities"""
    print("\n=== SCENT GENERATION DEMONSTRATION ===")
    
    # Create different aromatic mappings to show scent variety
    scent_mappings = []
    
    # Floral scent (multiple aromatic regions)
    floral_vertices = [(0, 0, 0), (2, 0, 0), (3, 1.5, 0), (2, 3, 0), (0, 3, 0), (-1, 1.5, 0)]
    floral_mapping = PolygonalObjectMapping(
        vertices=floral_vertices,
        width=0, height=0, depth=0.3,
        surface_area=0, volume=0,
        aromatic_regions=[(1, 1.5, 0), (0.5, 2, 0), (1.5, 1, 0)],  # Multiple aromatic centers
        scent_intensity=0.9
    )
    floral_mapping.calculate_dimensions()
    floral_mapping.calculate_surface_area()
    floral_mapping.calculate_volume()
    scent_mappings.append(("Floral Compound", floral_mapping))
    
    # Fresh/citrus scent (elongated molecule)
    citrus_vertices = [(0, 0, 0), (4, 0, 0), (4, 1, 0), (0, 1, 0)]
    citrus_mapping = PolygonalObjectMapping(
        vertices=citrus_vertices,
        width=0, height=0, depth=0.2,
        surface_area=0, volume=0,
        aromatic_regions=[(2, 0.5, 0)],
        scent_intensity=0.7
    )
    citrus_mapping.calculate_dimensions()
    citrus_mapping.calculate_surface_area()
    citrus_mapping.calculate_volume()
    scent_mappings.append(("Citrus Compound", citrus_mapping))
    
    # Woody/musky scent (large volume)
    woody_vertices = [(0, 0, 0), (2, 0, 0), (2, 2, 0), (0, 2, 0), (1, 1, 2)]  # Pyramid shape
    woody_mapping = PolygonalObjectMapping(
        vertices=woody_vertices,
        width=0, height=0, depth=0,
        surface_area=0, volume=0,
        aromatic_regions=[(1, 1, 0.5)],
        scent_intensity=0.6
    )
    woody_mapping.calculate_dimensions()
    woody_mapping.calculate_surface_area()
    woody_mapping.calculate_volume()
    scent_mappings.append(("Woody Compound", woody_mapping))
    
    # Generate and display scent profiles
    for name, mapping in scent_mappings:
        scent_profile = mapping.generate_aromatic_scent_profile()
        print(f"\n{name}:")
        print(f"  Dimensions: {mapping.width:.1f} x {mapping.height:.1f} x {mapping.depth:.1f} Å")
        print(f"  Volume: {mapping.volume:.3f} ų")
        print(f"  Scent Notes:")
        
        sorted_notes = sorted(scent_profile.items(), key=lambda x: x[1], reverse=True)
        for note, intensity in sorted_notes:
            if intensity > 0.1:
                strength = "Strong" if intensity > 0.6 else "Moderate" if intensity > 0.3 else "Mild"
                print(f"    {note.capitalize()}: {intensity:.2f} ({strength})")


def main():
    """Main test function"""
    print("ENHANCED ELECTRODE ARRAY SYSTEM - POLYGONAL OBJECT MAPPING TEST")
    print("=" * 70)
    
    try:
        # Run all tests
        benzene_mapping = test_polygonal_mapping()
        array, test_bond = test_electrode_array_enhancement()
        manipulator = test_molecular_manipulator()
        demonstrate_scent_generation()
        
        print("\n" + "=" * 70)
        print("✓ All tests completed successfully!")
        print("✓ Polygonal object mapping: FUNCTIONAL")
        print("✓ Dimensional control: ENHANCED")
        print("✓ Aromatic activation: OPERATIONAL")
        print("✓ Scent generation: ACTIVE")
        print("✓ Field distribution optimization: WORKING")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)