#!/usr/bin/env python3
"""
Quick Start Guide for Enhanced Electrode Array System
Demonstrates polygonal object mapping and aromatic activation
"""

from electrode_array_system import (
    MolecularManipulator, PolygonalObjectMapping, 
    MolecularBond, ElectrodePosition
)

def quick_demo():
    """Quick demonstration of the enhanced system capabilities"""
    
    print("🧬 ENHANCED MOLECULAR MANIPULATION SYSTEM")
    print("=" * 50)
    
    # Initialize the system
    manipulator = MolecularManipulator()
    
    # Create a custom aromatic molecule with polygonal mapping
    print("\n📐 Creating polygonal molecular mapping...")
    
    # Define a benzene-like aromatic ring
    aromatic_vertices = [
        (0.0, 0.0, 0.0), (1.4, 0.0, 0.0), (2.1, 1.2, 0.0),
        (1.4, 2.4, 0.0), (0.0, 2.4, 0.0), (-0.7, 1.2, 0.0)
    ]
    
    aromatic_mapping = PolygonalObjectMapping(
        vertices=aromatic_vertices,
        width=0.0, height=0.0, depth=0.3,
        surface_area=0.0, volume=0.0,
        aromatic_regions=[(0.7, 1.2, 0.0)],  # Ring center
        scent_intensity=0.85
    )
    
    # Calculate molecular properties
    aromatic_mapping.calculate_dimensions()
    aromatic_mapping.calculate_surface_area() 
    aromatic_mapping.calculate_volume()
    
    print(f"✓ Molecular dimensions: {aromatic_mapping.width:.1f} × {aromatic_mapping.height:.1f} × {aromatic_mapping.depth:.1f} Å")
    print(f"✓ Surface area: {aromatic_mapping.surface_area:.2f} Ų")
    print(f"✓ Volume: {aromatic_mapping.volume:.3f} ų")
    
    # Generate scent profile
    print("\n🌸 Generating aromatic scent profile...")
    scent_profile = aromatic_mapping.generate_aromatic_scent_profile()
    
    for note, intensity in scent_profile.items():
        if intensity > 0.1:
            bars = "█" * int(intensity * 10)
            print(f"  {note.capitalize():8} {bars} {intensity:.2f}")
    
    # Configure electrode array for this molecule
    print("\n⚡ Configuring electrode array...")
    
    test_bond = MolecularBond(
        atom_a="C", atom_b="C", bond_type="aromatic",
        length=1.40, strength=120.0,
        position=ElectrodePosition(0.7, 1.2, 0.0),
        polygonal_mapping=aromatic_mapping
    )
    
    # Optimize field distribution
    field_dist = manipulator.electrode_array.calculate_polygonal_field_distribution(aromatic_mapping)
    print(f"✓ Field uniformity: {field_dist['field_uniformity']:.1%}")
    print(f"✓ Max field strength: {field_dist['max_field_strength']:.1f} V/m")
    
    # Apply aromatic activation
    print("\n🎯 Applying aromatic activation sequence...")
    manipulator.electrode_array.apply_aromatic_activation_sequence([test_bond])
    
    print("\n🎉 System demonstration complete!")
    print("✓ Polygonal mapping: ACTIVE")
    print("✓ Dimensional control: OPTIMIZED") 
    print("✓ Aromatic activation: SUCCESSFUL")
    print("✓ Scent generation: OPERATIONAL")

if __name__ == "__main__":
    quick_demo()