#!/usr/bin/env python3
"""
Test script for VESC Express custom config compatibility
Tests the new VESC controller compatible callback system
"""

import serial
import struct
import time

# VESC protocol constants
COMM_GET_CUSTOM_CONFIG = 93
COMM_GET_CUSTOM_CONFIG_XML = 92

def calculate_crc(data):
    """Calculate CRC16 for VESC protocol"""
    crc = 0
    for byte in data:
        crc ^= byte << 8
        for _ in range(8):
            if crc & 0x8000:
                crc = (crc << 1) ^ 0x1021
            else:
                crc <<= 1
            crc &= 0xFFFF
    return crc

def create_packet(command, data=b''):
    """Create VESC protocol packet"""
    payload = bytes([command]) + data
    payload_len = len(payload)
    
    if payload_len <= 256:
        packet = b'\x02' + bytes([payload_len]) + payload
    else:
        packet = b'\x03' + struct.pack('>H', payload_len) + payload
    
    crc = calculate_crc(payload)
    packet += struct.pack('>H', crc)
    packet += b'\x03'
    
    return packet

def test_custom_config():
    """Test custom config retrieval"""
    try:
        # Connect to VESC Express
        ser = serial.Serial('/dev/ttyACM0', 115200, timeout=2)
        time.sleep(0.1)
        
        print("🧪 Testing VESC Express Custom Config Compatibility")
        print("=" * 50)
        
        # Test 1: Get custom config
        print("1. Testing COMM_GET_CUSTOM_CONFIG...")
        packet = create_packet(COMM_GET_CUSTOM_CONFIG, b'\x00')  # Config index 0
        ser.write(packet)
        time.sleep(0.1)
        
        response = ser.read(1000)
        if len(response) > 10:
            print(f"   ✅ Received {len(response)} bytes")
            print(f"   📦 Response starts with: {response[:10].hex()}")
        else:
            print(f"   ❌ Short response: {len(response)} bytes")
        
        # Test 2: Get custom config XML
        print("\n2. Testing COMM_GET_CUSTOM_CONFIG_XML...")
        # Request XML: config_ind=0, len=100, offset=0
        xml_data = struct.pack('>BII', 0, 100, 0)
        packet = create_packet(COMM_GET_CUSTOM_CONFIG_XML, xml_data)
        ser.write(packet)
        time.sleep(0.1)
        
        response = ser.read(1000)
        if len(response) > 10:
            print(f"   ✅ Received {len(response)} bytes")
            # Try to decode XML content
            try:
                if b'xml' in response or b'config' in response:
                    print("   📄 XML content detected!")
                else:
                    print(f"   📦 Response: {response[:50]}")
            except:
                print(f"   📦 Binary response: {response[:20].hex()}")
        else:
            print(f"   ❌ Short response: {len(response)} bytes")
        
        ser.close()
        print("\n✅ Custom config compatibility test completed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    test_custom_config()