#!/usr/bin/env python3
"""
Test ESP32-C6 Hardware Name Change
Verifies that ESP32-C6 now reports as "Devkit C3" for VESC Tool compatibility
"""

import socket
import struct
import time

def crc16_ccitt(data):
    """Calculate CRC16-CCITT checksum for VESC protocol"""
    crc = 0x0000
    for byte in data:
        crc ^= byte << 8
        for _ in range(8):
            if crc & 0x8000:
                crc = (crc << 1) ^ 0x1021
            else:
                crc <<= 1
            crc &= 0xFFFF
    return crc

def send_vesc_command(sock, command_id, payload=b''):
    """Send VESC protocol command and return response"""
    # VESC packet format: [START][LENGTH][PAYLOAD][CRC][END]
    start_byte = 0x02 if len(payload) < 256 else 0x03
    
    if start_byte == 0x02:
        length_bytes = struct.pack('B', len(payload) + 1)  # +1 for command
    else:
        length_bytes = struct.pack('>H', len(payload) + 1)
    
    # Build packet data (command + payload)
    packet_data = struct.pack('B', command_id) + payload
    
    # Calculate CRC on packet data only
    crc = crc16_ccitt(packet_data)
    
    # Build complete packet
    packet = struct.pack('B', start_byte) + length_bytes + packet_data + struct.pack('>H', crc) + struct.pack('B', 0x03)
    
    print(f"Sending command {command_id}: {packet.hex()}")
    sock.send(packet)
    
    # Read response
    response = sock.recv(1024)
    print(f"Received response: {response.hex()}")
    return response

def test_hardware_name():
    """Test hardware name via VESC protocol"""
    print("🔧 Testing ESP32-C6 Hardware Name Change")
    print("=" * 50)
    
    # Connect to ESP32-C6 via WiFi
    esp32_ip = "192.168.5.107"
    esp32_port = 65102
    
    try:
        print(f"Connecting to {esp32_ip}:{esp32_port}...")
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        sock.connect((esp32_ip, esp32_port))
        print("✅ Connected successfully")
        
        print("\n📊 Testing COMM_GET_VALUES (4) to verify connection...")
        response = send_vesc_command(sock, 4)
        if len(response) > 10:
            print("✅ COMM_GET_VALUES working - device is functional")
        else:
            print("❌ COMM_GET_VALUES failed")
            return
        
        print("\n🔍 Testing COMM_FW_VERSION (0) to get hardware name...")
        response = send_vesc_command(sock, 0)
        
        if len(response) > 10:
            print("✅ COMM_FW_VERSION response received")
            
            # Parse firmware version response
            # Format: [packet header][major][minor][hw_name][uuid][pairing_done][...][packet footer]
            try:
                # Skip packet header (start + length)
                if response[0] == 0x02:
                    data_start = 2  # 1 byte start + 1 byte length
                else:
                    data_start = 3  # 1 byte start + 2 bytes length
                
                # Skip command byte and version bytes
                hw_name_start = data_start + 1 + 2  # command + major + minor
                
                # Find hardware name (null-terminated string)
                hw_name_end = hw_name_start
                while hw_name_end < len(response) and response[hw_name_end] != 0:
                    hw_name_end += 1
                
                if hw_name_end > hw_name_start:
                    hw_name = response[hw_name_start:hw_name_end].decode('utf-8', errors='ignore')
                    print(f"\n🎯 Hardware Name: '{hw_name}'")
                    
                    if hw_name == "Devkit C3":
                        print("✅ SUCCESS: ESP32-C6 now reports as 'Devkit C3'")
                        print("✅ VESC Tool compatibility achieved!")
                        return True
                    elif "ESP32-C6" in hw_name:
                        print("❌ Still reporting original ESP32-C6 name")
                        print("❌ Firmware may not have been flashed yet")
                        return False
                    else:
                        print(f"⚠️  Unexpected hardware name: {hw_name}")
                        return False
                else:
                    print("❌ Could not extract hardware name from response")
                    return False
                    
            except Exception as e:
                print(f"❌ Error parsing firmware version: {e}")
                return False
        else:
            print("❌ COMM_FW_VERSION failed - no response")
            return False
            
    except socket.error as e:
        print(f"❌ Connection failed: {e}")
        print("ℹ️  Make sure ESP32-C6 is connected to WiFi and accessible")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False
    finally:
        try:
            sock.close()
        except:
            pass

def main():
    """Main test function"""
    print("ESP32-C6 → Devkit C3 Hardware Name Test")
    print("=" * 40)
    
    success = test_hardware_name()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 TEST PASSED: Hardware name change successful!")
        print("📱 ESP32-C6 is now compatible with official VESC Tool")
    else:
        print("⚠️  TEST NEEDS ATTENTION: Check results above")
        print("💡 You may need to flash the updated firmware first")

if __name__ == "__main__":
    main()