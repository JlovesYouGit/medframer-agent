#!/usr/bin/env python3

# Read the file
with open(r'n:\safe - depression med - tech\side_effect_neutralization_system.py', 'r') as f:
    content = f.read()

# Add the missing _initialize_body_regions method
body_regions_method = '''
    def _initialize_body_regions(self) -> Dict[str, BodyRegion]:
        """Initialize body regions commonly affected by escitalopram side effects"""
        regions = {
            # Neck and shoulder region (common tension area)
            "cervical_spine": BodyRegion(
                region_name="Cervical Spine/Neck",
                coordinates=(0.0, 0.8, 0.0),  # Upper body, centered
                tension_level=0.8,  # High tension from medication
                pain_level=0.7,
                circulation_efficiency=0.6,  # Reduced from tension
                muscle_relaxation=0.3,  # Very tense
                target_relief_level=0.9
            ),
            
            # Upper back and shoulders
            "upper_back": BodyRegion(
                region_name="Upper Back/Shoulders",
                coordinates=(0.0, 0.6, 0.2),  # Upper back, slightly forward
                tension_level=0.7,
                pain_level=0.6,
                circulation_efficiency=0.7,
                muscle_relaxation=0.4,
                target_relief_level=0.85
            ),
            
            # Brain regions
            "left_cerebral_cortex": BodyRegion(
                region_name="Left Cerebral Cortex",
                coordinates=(-0.3, 1.0, 0.0),  # Left hemisphere
                tension_level=0.4,  # Moderate from medication
                pain_level=0.2,
                circulation_efficiency=0.8,
                muscle_relaxation=0.7,
                target_relief_level=0.8
            ),
            
            "right_hemisphere": BodyRegion(
                region_name="Right Hemisphere Lower Region",
                coordinates=(0.3, 0.9, -0.1),  # Right hemisphere
                tension_level=0.4,
                pain_level=0.2,
                circulation_efficiency=0.8,
                muscle_relaxation=0.7,
                target_relief_level=0.8
            ),
            
            # Cardiac region
            "cardiac_region": BodyRegion(
                region_name="Heart/Cardiac Region",
                coordinates=(0.0, 0.4, 0.0),  # Chest center
                tension_level=0.5,  # Heart strain from medication
                pain_level=0.4,
                circulation_efficiency=0.6,  # Reduced circulation
                muscle_relaxation=0.6,
                target_relief_level=0.8
            ),
            
            # Peripheral circulation
            "peripheral_circulation": BodyRegion(
                region_name="Peripheral Circulation",
                coordinates=(0.0, 0.0, 0.0),  # Lower body reference
                tension_level=0.3,  # Mild circulation issues
                pain_level=0.2,
                circulation_efficiency=0.7,
                muscle_relaxation=0.8,
                target_relief_level=0.85
            )
        }
        
        print(f"✅ Initialized {len(regions)} body regions for side effect monitoring")
        return regions
    
'''

# Insert the missing method after the numerical conversion function
content = content.replace(
    '    def _detect_initial_pill_side_effects(self)',
    body_regions_method + '\n    def _detect_initial_pill_side_effects(self)'
)

# Write back
with open(r'n:\safe - depression med - tech\side_effect_neutralization_system.py', 'w') as f:
    f.write(content)

print("✅ Added missing _initialize_body_regions method")
