#!/usr/bin/env python3
"""
Verify VESC Express custom config signature compatibility
"""

import serial
import struct
import time

def test_signature():
    """Test if the signature is correct"""
    try:
        ser = serial.Serial('/dev/ttyACM0', 115200, timeout=2)
        time.sleep(0.1)
        
        # Send COMM_GET_CUSTOM_CONFIG request
        packet = b'\x02\x02\x5d\x00\x76\x1a\x03'  # Get custom config, index 0
        ser.write(packet)
        time.sleep(0.1)
        
        response = ser.read(1000)
        ser.close()
        
        if len(response) >= 10:
            # Parse response to find signature
            if response[0] == 0x49:  # Skip response headers
                # Find signature in response
                payload_start = 3  # Skip packet header
                if len(response) > payload_start + 6:
                    signature_bytes = response[payload_start + 2:payload_start + 6]
                    signature = struct.unpack('>I', signature_bytes)[0]
                    
                    print(f"📊 Custom Config Signature Analysis")
                    print(f"=" * 40)
                    print(f"Raw signature bytes: {signature_bytes.hex()}")
                    print(f"Signature value: {signature}")
                    print(f"Expected signature: 1954583969 (0x749D8EA1)")
                    
                    if signature == 1954583969:
                        print("✅ Signature matches! VESC controller compatibility confirmed")
                    else:
                        print("⚠️  Different signature - may indicate version difference")
                        print(f"   Hex: 0x{signature:08X}")
                    
                    return True
        
        print("❌ Could not extract signature from response")
        return False
        
    except Exception as e:
        print(f"❌ Signature test failed: {e}")
        return False

if __name__ == "__main__":
    test_signature()