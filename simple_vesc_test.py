#!/usr/bin/env python3
"""
Simple VESC communication test with debug output
"""

import serial
import time

def test_vesc_communication():
    try:
        ser = serial.Serial('/dev/ttyACM0', 115200, timeout=1)
        time.sleep(0.5)
        
        # Clear buffers
        ser.flushInput()
        ser.flushOutput()
        
        print("Testing simple VESC ALIVE command...")
        
        # Simple ALIVE command: [0x02, 0x01, 0x1E, CRC16_HIGH, CRC16_LOW, 0x03]
        # Command 30 (0x1E) = ALIVE, payload length = 1
        # CRC16 of [0x1E] = 0xF3FF
        alive_packet = bytes([0x02, 0x01, 0x1E, 0xF3, 0xFF, 0x03])
        
        print(f"Sending: {alive_packet.hex()}")
        ser.write(alive_packet)
        ser.flush()
        
        # Wait and read response
        time.sleep(1)
        
        if ser.in_waiting:
            response = ser.read(ser.in_waiting)
            print(f"Response: {response.hex()}")
            print(f"Response ASCII: {response}")
        else:
            print("No response received")
            
        # Try a different approach - send raw bytes and see what happens
        print("\nTrying raw command bytes...")
        ser.write(b'help\r\n')
        ser.flush()
        
        time.sleep(1)
        if ser.in_waiting:
            response = ser.read(ser.in_waiting)
            print(f"Help response: {response}")
        else:
            print("No help response")
            
        ser.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_vesc_communication()