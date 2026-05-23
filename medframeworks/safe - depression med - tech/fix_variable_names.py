#!/usr/bin/env python3
"""
Quick fix for the variable name issue in side_effect_neutralization_system.py
"""

import re

# Read the file
with open(r'n:\safe - depression med - tech\side_effect_neutralization_system.py', 'r') as f:
    content = f.read()

# Fix all instances of 'nutrilitizer' to 'nutrilizer' in the problematic section
content = content.replace('nutrilitzer[\'target_electrolytes\']', 'nutrilizer[\'target_electrolytes\']')
content = content.replace('nutrilitzer[\'visual_stabilizers\']', 'nutrilizer[\'visual_stabilizers\']')
content = content.replace('nutrilitzer[\'circulation_enhancers\']', 'nutrilizer[\'circulation_enhancers\']')
content = content.replace('nutrilitzer[\'neurotransmitter_balancers\']', 'nutrilizer[\'neurotransmitter_balancers\']')

# Write the file back
with open(r'n:\safe - depression med - tech\side_effect_neutralization_system.py', 'w') as f:
    f.write(content)

print("✅ Fixed variable name issues in side_effect_neutralization_system.py")
