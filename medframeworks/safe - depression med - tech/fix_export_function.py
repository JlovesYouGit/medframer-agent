#!/usr/bin/env python3

# Read the file
with open(r'n:\safe - depression med - tech\live_usb_data_feed.py', 'r') as f:
    content = f.read()

# Fix the export function to handle JSON serialization properly
old_export_function = '''    def export_live_feed_data(self, filename: str = None) -> str:
        """Export live feed data"""
        if filename is None:
            filename = f"live_feed_{self.feed_session_id}.json"
        
        export_data = {
            "session_info": {
                "session_id": self.feed_session_id,
                "timestamp": time.time(),
                "usb_port": self.usb_port
            },
            "device_info": self.device_info,
            "feed_statistics": self.get_feed_statistics(),
            "data_history": [
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
            ]
        }
        
        with open(filename, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        print(f"  Live feed data exported to: {filename}")
        return filename'''

new_export_function = '''    def export_live_feed_data(self, filename: str = None) -> str:
        """Export live feed data"""
        if filename is None:
            filename = f"live_feed_{self.feed_session_id}.json"
        
        # Convert data history to JSON-serializable format
        serializable_history = []
        for p in list(self.data_history)[-1000:]:  # Last 1000 packets
            serializable_history.append({
                "packet_id": p.packet_id,
                "timestamp": p.timestamp,
                "source_device": p.source_device,
                "data_type": p.data_type.value,
                "value": p.value,
                "quality": p.quality,
                "metadata": p.metadata
            })
        
        export_data = {
            "session_info": {
                "session_id": self.feed_session_id,
                "timestamp": time.time(),
                "usb_port": self.usb_port
            },
            "device_info": self.device_info,
            "feed_statistics": self.get_feed_statistics(),
            "data_history": serializable_history
        }
        
        with open(filename, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        print(f"  Live feed data exported to: {filename}")
        return filename'''

# Replace the export function
content = content.replace(old_export_function, new_export_function)

# Write back
with open(r'n:\safe - depression med - tech\live_usb_data_feed.py', 'w') as f:
    f.write(content)

print("✅ Fixed JSON serialization in export function")
