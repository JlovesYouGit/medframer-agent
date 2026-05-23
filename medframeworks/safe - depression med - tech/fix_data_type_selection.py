#!/usr/bin/env python3

# Read the file
with open(r'n:\safe - depression med - tech\live_usb_data_feed.py', 'r') as f:
    content = f.read()

# Fix the data type selection issue
old_data_type_selection = '''            # Select random data type from supported types
            import random
            data_type = random.choice(supported_types)'''

new_data_type_selection = '''            # Select random data type from supported types
            import random
            data_type_name = random.choice(supported_types)
            data_type = USBDataType(data_type_name)'''

# Replace the data type selection
content = content.replace(old_data_type_selection, new_data_type_selection)

# Write back
with open(r'n:\safe - depression med - tech\live_usb_data_feed.py', 'w') as f:
    f.write(content)

print("✅ Fixed data type selection issue")
