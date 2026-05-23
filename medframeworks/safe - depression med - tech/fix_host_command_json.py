#!/usr/bin/env python3

# Read the file
with open(r'n:\safe - depression med - tech\host_body_command_system.py', 'r') as f:
    content = f.read()

# Fix the JSON serialization issue by converting HostResponse to dict
old_result = '''            return {
                "success": True,
                "response": response,
                "applied_changes": applied_changes,
                "side_effects": side_effects
            }'''

new_result = '''            return {
                "success": True,
                "response": {
                    "command_id": response.command_id,
                    "response_code": response.response_code,
                    "response_message": response.response_message,
                    "applied_changes": response.applied_changes,
                    "side_effects": response.side_effects,
                    "timestamp": response.timestamp
                },
                "applied_changes": applied_changes,
                "side_effects": side_effects
            }'''

# Replace the result return
content = content.replace(old_result, new_result)

# Write back
with open(r'n:\safe - depression med - tech\host_body_command_system.py', 'w') as f:
    f.write(content)

print("✅ Fixed JSON serialization issue")
