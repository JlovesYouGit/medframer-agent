#!/usr/bin/env python3

# Read the file
with open(r'n:\safe - depression med - tech\hydrogen_balance_resolver.py', 'r') as f:
    content = f.read()

# Fix the syntax error on line 173 - properly separate statements
content = content.replace(
    '        if current_ph < target_ph_range[0]:\n            ph_adjustment = target_ph_range[0] - current_ph\n            adjustment_direction = "increase"\n        elif current_ph > target_ph_range[1]:\n            ph_adjustment = current_ph - target_ph_range[1]\n            adjustment_direction = "decrease"\n        else:\n            ph_adjustment = 0\n            adjustment_direction = "optimal"',
    '''        if current_ph < target_ph_range[0]:
            ph_adjustment = target_ph_range[0] - current_ph
            adjustment_direction = "increase"
        elif current_ph > target_ph_range[1]:
            ph_adjustment = current_ph - target_ph_range[1]
            adjustment_direction = "decrease"
        else:
            ph_adjustment = 0
            adjustment_direction = "optimal"'''
)

# Write back
with open(r'n:\safe - depression med - tech\hydrogen_balance_resolver.py', 'w') as f:
    f.write(content)

print("✅ Fixed syntax errors in hydrogen_balance_resolver.py")
