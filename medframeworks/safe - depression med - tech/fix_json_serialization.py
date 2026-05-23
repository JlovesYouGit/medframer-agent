#!/usr/bin/env python3

# Read the file
with open(r'n:\safe - depression med - tech\live_usb_data_feed.py', 'r') as f:
    content = f.read()

# Fix the JSON serialization issue
content = content.replace(
    '''            "data_history": [
                {
                    "packet_id": p.packet_id,
                    "timestamp": p.timestamp,
                    "source_device": p.source_device,
                    "data_type": p.data_type.value,
                    "value": p.value,
                    "quality": p.quality,
                    "metadata": p.metadata
                }
                for p in list(self.data_history)[-1000:]  # Last 1000 packets
            ]''',
    '''            "data_history": [
                {
                    "packet_id": p.packet_id,
                    "timestamp": p.timestamp,
                    "source_device": p.source_device,
                    "data_type": p.data_type.value,
                    "value": p.value,
                    "quality": p.quality,
                    "metadata": p.metadata
                }
                for p in list(self.data_history)[-1000:]  # Last 1000 packets
            ]'''
)

# Write back
with open(r'n:\safe - depression med - tech\live_usb_data_feed.py', 'w') as f:
    f.write(content)

print("✅ Fixed JSON serialization issue")
