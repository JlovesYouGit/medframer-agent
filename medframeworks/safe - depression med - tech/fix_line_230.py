#!/usr/bin/env python3

# Read the file
with open(r'n:\safe - depression med - tech\side_effect_neutralization_system.py', 'r') as f:
    lines = f.readlines()

# Fix line 230 specifically (index 229)
for i, line in enumerate(lines):
    if i == 229:  # Line 230 (0-indexed)
        if 'nutrilitzer[' in line:
            lines[i] = line.replace('nutrilitzer[', 'nutrilizer[')
            print(f"Fixed line {i+1}: {lines[i].strip()}")

# Write back
with open(r'n:\safe - depression med - tech\side_effect_neutralization_system.py', 'w') as f:
    f.writelines(lines)

print("✅ Fixed line 230 variable name issue")
