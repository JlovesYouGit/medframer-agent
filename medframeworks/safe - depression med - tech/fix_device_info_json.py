#!/usr/bin/env python3

# Read the file
with open(r'n:\safe - depression med - tech\live_usb_data_feed.py', 'r') as f:
    content = f.read()

# Fix the device_info to convert enum values to strings
old_device_info = '''                self.device_info = {
                    "device_id": f"USB_ELECTRODE_{self.usb_port}",
                    "firmware_version": "2.1.3",
                    "serial_number": f"USB{self.usb_port:04d}{int(time.time()) % 10000:04d}",
                    "manufacturer": "BioElectrode Systems",
                    "supported_data_types": [
                        USBDataType.ELECTRODE_VOLTAGE,
                        USBDataType.ELECTRODE_CURRENT,
                        USBDataType.BODY_IMPEDANCE,
                        USBDataType.TEMPERATURE,
                        USBDataType.PH_LEVEL
                    ],
                    "sampling_rate": 1000.0,  # Hz
                    "data_format": "binary_float",
                    "checksum_enabled": True
                }'''

new_device_info = '''                self.device_info = {
                    "device_id": f"USB_ELECTRODE_{self.usb_port}",
                    "firmware_version": "2.1.3",
                    "serial_number": f"USB{self.usb_port:04d}{int(time.time()) % 10000:04d}",
                    "manufacturer": "BioElectrode Systems",
                    "supported_data_types": [
                        "electrode_voltage",
                        "electrode_current",
                        "body_impedance",
                        "temperature",
                        "ph_level"
                    ],
                    "sampling_rate": 1000.0,  # Hz
                    "data_format": "binary_float",
                    "checksum_enabled": True
                }'''

# Replace the device_info initialization
content = content.replace(old_device_info, new_device_info)

# Also fix the export function to handle device_info properly
old_export_data = '''        export_data = {
            "session_info": {
                "session_id": self.feed_session_id,
                "timestamp": time.time(),
                "usb_port": self.usb_port
            },
            "device_info": self.device_info,
            "feed_statistics": self.get_feed_statistics(),
            "data_history": serializable_history
        }'''

new_export_data = '''        export_data = {
            "session_info": {
                "session_id": self.feed_session_id,
                "timestamp": time.time(),
                "usb_port": self.usb_port
            },
            "device_info": self.device_info,
            "feed_statistics": self.get_feed_statistics(),
            "data_history": serializable_history
        }'''

# Replace the export_data assignment
content = content.replace(old_export_data, new_export_data)

# Write back
with open(r'n:\safe - depression med - tech\live_usb_data_feed.py', 'w') as f:
    f.write(content)

print("✅ Fixed device_info JSON serialization")
