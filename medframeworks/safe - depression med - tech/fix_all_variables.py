#!/usr/bin/env python3

# Read the file
with open(r'n:\safe - depression med - tech\side_effect_neutralization_system.py', 'r') as f:
    content = f.read()

# Fix ALL instances of the typo
content = content.replace('nutrilitzer[', 'nutrilizer[')
content = content.replace('len(nutrilitzer[', 'len(nutrilitizer[')

# Write back
with open(r'n:\safe - depression med - tech\side_effect_neutralization_system.py', 'w') as f:
    f.write(content)

print("✅ Fixed ALL variable name definition issues")
