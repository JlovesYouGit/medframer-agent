#!/usr/bin/env python3

# Read the file
with open(r'n:\safe - depression med - tech\side_effect_neutralization_system.py', 'r') as f:
    content = f.read()

# Add numerical to alphabetical conversion function
conversion_function = '''
def _convert_numerical_to_alphabetical(self, value):
    """
    Convert numerical values to alphabetical representations
    """
    if isinstance(value, (int, float)):
        # Convert number to string representation
        if value >= 1.0:
            return f"Level_{int(value)}"
        elif value >= 0.8:
            return "High"
        elif value >= 0.6:
            return "Medium_High"
        elif value >= 0.4:
            return "Medium"
        elif value >= 0.2:
            return "Medium_Low"
        else:
            return "Low"
    elif isinstance(value, dict):
        # Convert dictionary values
        return {k: self._convert_numerical_to_alphabetical(v) for k, v in value.items()}
    elif isinstance(value, list):
        # Convert list values
        return [self._convert_numerical_to_alphabetical(v) for v in value]
    else:
        return str(value)

'''

# Insert the conversion function after the __init__ method
content = content.replace(
    '        self.electrode_boolean_values = self._get_electrode_boolean_values()\n        \n    def _detect_initial_pill_side_effects(self)',
    '        self.electrode_boolean_values = self._get_electrode_boolean_values()\n        \n' + conversion_function + '\n    def _detect_initial_pill_side_effects(self)'
)

# Fix the variable definition issue by ensuring nutrilizer is properly defined
content = content.replace('nutrilitzer[', 'nutrilizer[')

# Add proper flow control after each section
content = content.replace(
    '            print(f"  Electrolyte nutrilizers: {len(nutrilitizer[\'target_electrolytes\'])}")\n        \n        # Ensure execution continues',
    '            print(f"  ⚡ Electrolyte nutrilizers: {len(nutrilitizer[\'target_electrolytes\'])}")\n            # Convert to alphabetical for flow control\n            electrolyte_alpha = self._convert_numerical_to_alphabetical(nutrilitizer[\'target_electrolytes\'])\n            print(f"  📝 Alphabetical representation: {electrolyte_alpha}")\n        \n        # Ensure execution continues'
)

# Write back
with open(r'n:\safe - depression med - tech\side_effect_neutralization_system.py', 'w') as f:
    f.write(content)

print("✅ Added numerical-to-alphabetical conversion and fixed definition issues")
