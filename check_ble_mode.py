#!/usr/bin/env python3
"""
Check current BLE mode configuration on ESP32-C6 VESC Express
"""

import socket
import time
import struct
import sys

class BLEModeChecker:
    def __init__(self, host="192.168.5.107", port=65102):
        self.host = host
        self.port = port
        self.sock = None
        self.COMM_TERMINAL_CMD = 20
        
    def log(self, message, level="INFO"):
        timestamp = time.strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
        
    def crc16(self, data):
        """Calculate CRC16-CCITT for VESC protocol"""
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
    
    def create_vesc_packet(self, command, payload=b''):
        """Create VESC protocol packet"""
        packet_payload = bytes([command]) + payload
        payload_len = len(packet_payload)
        
        packet = b''
        if payload_len <= 255:
            packet += bytes([0x02, payload_len])
        else:
            packet += bytes([0x03, (payload_len >> 8) & 0xFF, payload_len & 0xFF])
            
        packet += packet_payload
        crc = self.crc16(packet_payload)
        packet += struct.pack('>H', crc) + bytes([0x03])
        
        return packet
    
    def connect(self):
        """Connect to ESP32-C6"""
        self.log(f"🔗 Connecting to ESP32-C6 at {self.host}:{self.port}")
        
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.settimeout(10)
            self.sock.connect((self.host, self.port))
            self.log("✅ Connected successfully")
            return True
        except Exception as e:
            self.log(f"❌ Connection failed: {e}", "ERROR")
            return False
    
    def send_terminal_command(self, cmd):
        """Send terminal command and get response"""
        self.log(f"💻 Sending terminal command: '{cmd}'")
        
        packet = self.create_vesc_packet(self.COMM_TERMINAL_CMD, cmd.encode())
        
        try:
            self.sock.send(packet)
            
            # Monitor for response
            self.sock.settimeout(5)
            response = b''
            
            start_time = time.time()
            while time.time() - start_time < 5:
                try:
                    data = self.sock.recv(1024)
                    if data:
                        response += data
                    else:
                        break
                except socket.timeout:
                    break
            
            if response:
                # Try to decode response
                try:
                    # Response format: 02 len [15 response_text] crc 03
                    # Look for text content
                    text_start = -1
                    for i in range(len(response)):
                        if response[i] == 0x15:  # Terminal response command
                            text_start = i + 1
                            break
                    
                    if text_start > 0:
                        # Find end of text (before CRC)
                        text_end = len(response) - 3  # Skip CRC and end byte
                        text_data = response[text_start:text_end]
                        decoded_text = text_data.decode('utf-8', errors='ignore')
                        self.log(f"📄 Response: {decoded_text}")
                        return decoded_text
                    else:
                        self.log(f"📥 Raw response: {response.hex()}")
                        return response.hex()
                except:
                    self.log(f"📥 Raw response: {response.hex()}")
                    return response.hex()
            else:
                self.log("❌ No response received")
                return None
                
        except Exception as e:
            self.log(f"❌ Command failed: {e}", "ERROR")
            return None
    
    def check_ble_configuration(self):
        """Check BLE mode configuration"""
        self.log("🔍 Checking BLE configuration...")
        
        if not self.connect():
            return False
        
        try:
            # Commands to check BLE status
            commands = [
                "help",           # List available commands
                "debug_info",     # System debug info 
                "fw_info",        # Firmware info
            ]
            
            for cmd in commands:
                self.log(f"\n--- Executing: {cmd} ---")
                response = self.send_terminal_command(cmd)
                time.sleep(1)
            
            # Try to get specific BLE information
            self.log("\n--- Checking for BLE-specific commands ---")
            ble_commands = [
                "conf_get ble_mode",     # Get BLE mode setting
                "ble",                   # Check if BLE command exists
                "bluetooth",             # Check if bluetooth command exists
            ]
            
            for cmd in ble_commands:
                self.log(f"\n--- Executing: {cmd} ---")
                response = self.send_terminal_command(cmd)
                time.sleep(1)
            
            return True
            
        except Exception as e:
            self.log(f"❌ Check failed: {e}", "ERROR")
            return False
        finally:
            if self.sock:
                self.sock.close()
                self.log("🔌 Connection closed")

def main():
    checker = BLEModeChecker()
    success = checker.check_ble_configuration()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())