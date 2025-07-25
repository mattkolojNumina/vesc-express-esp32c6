#!/usr/bin/env python3

import socket
import time
import struct

def crc16(data):
    crc = 0x0000
    for byte in data:
        crc ^= byte << 8
        for _ in range(8):
            if crc & 0x8000:
                crc = (crc << 1) ^ 0x1021
            else:
                crc = crc << 1
            crc &= 0xFFFF
    return crc

def create_packet(command, payload=b''):
    packet_payload = bytes([command]) + payload
    payload_len = len(packet_payload)
    
    packet = bytes([0x02, payload_len]) if payload_len <= 255 else bytes([0x03, (payload_len >> 8) & 0xFF, payload_len & 0xFF])
    packet += packet_payload
    crc = crc16(packet_payload)
    packet += struct.pack('>H', crc) + bytes([0x03])
    return packet

print("Connecting...")
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.settimeout(5)

try:
    sock.connect(("192.168.5.107", 65102))
    print("Connected. Setting BLE to open mode...")
    
    # Send LispBM command to set BLE mode to 1 (OPEN)
    cmd = "(conf-set 'ble-mode 1)"
    packet = create_packet(20, cmd.encode())
    sock.send(packet)
    time.sleep(2)
    
    # Store configuration
    cmd = "(conf-store)"
    packet = create_packet(20, cmd.encode())
    sock.send(packet)
    time.sleep(2)
    
    print("✅ BLE mode set to OPEN")
    print("📱 Try connecting from your phone now")
    
except Exception as e:
    print(f"❌ Error: {e}")
finally:
    sock.close()