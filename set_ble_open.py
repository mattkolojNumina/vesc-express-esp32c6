#!/usr/bin/env python3
"""
Set BLE mode to open (no pairing required) on ESP32-C6 VESC Express
Uses LispBM configuration commands to change ble_mode to 1
"""

import socket
import time
import struct
import sys

class BLEModeConfigurer:
    def __init__(self, host="192.168.5.107", port=65102):
        self.host = host
        self.port = port
        self.sock = None
        self.COMM_TERMINAL_CMD = 20
        self.COMM_LISP_SET_RUNNING = 26
        self.COMM_LISP_GET_STATS = 27
        
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
    
    def send_terminal_command(self, cmd, timeout=10):
        """Send terminal command and get response"""
        self.log(f"💻 Sending terminal command: '{cmd}'")
        
        packet = self.create_vesc_packet(self.COMM_TERMINAL_CMD, cmd.encode())
        
        try:
            self.sock.send(packet)
            
            # Monitor for response
            self.sock.settimeout(timeout)
            response = b''
            
            start_time = time.time()
            while time.time() - start_time < timeout:
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
                    # Look for terminal response (command 0x15)
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
                except Exception as e:
                    self.log(f"📥 Raw response: {response.hex()}")
                    return response.hex()
            else:
                self.log("❌ No response received")
                return None
                
        except Exception as e:
            self.log(f"❌ Command failed: {e}", "ERROR")
            return None
    
    def configure_ble_open_mode(self):
        """Configure BLE to open mode (no pairing)"""
        self.log("🔧 Configuring BLE to open mode...")
        
        if not self.connect():
            return False
        
        try:
            # Step 1: Check current BLE mode using LispBM
            self.log("\n--- Step 1: Check current BLE mode ---")
            response = self.send_terminal_command("(conf-get 'ble-mode)")
            if response:
                if "2" in response:
                    self.log("🔍 Current BLE mode: ENCRYPTED (2)")
                elif "1" in response:
                    self.log("🔍 Current BLE mode: OPEN (1) - Already correct!")
                    return True
                elif "0" in response:
                    self.log("🔍 Current BLE mode: DISABLED (0)")
            
            # Step 2: Set BLE mode to OPEN (1)
            self.log("\n--- Step 2: Set BLE mode to OPEN (1) ---")
            response = self.send_terminal_command("(conf-set 'ble-mode 1)")
            if response and ("t" in response or "nil" not in response):
                self.log("✅ BLE mode set to OPEN successfully")
            else:
                self.log("⚠️  BLE mode setting response unclear")
            
            # Step 3: Store configuration to make it persistent
            self.log("\n--- Step 3: Store configuration to NVS ---")
            response = self.send_terminal_command("(conf-store)")
            if response and ("t" in response or "Stored" in response or response.strip() == ""):
                self.log("✅ Configuration stored to NVS")
            else:
                self.log("⚠️  Configuration store response unclear")
            
            # Step 4: Verify the change
            self.log("\n--- Step 4: Verify BLE mode change ---")
            response = self.send_terminal_command("(conf-get 'ble-mode)")
            if response and "1" in response:
                self.log("✅ BLE mode confirmed as OPEN (1)")
                
                # Step 5: Restart BLE to apply changes
                self.log("\n--- Step 5: Restart to apply BLE changes ---") 
                self.log("💡 Note: Device restart required for BLE changes to take effect")
                response = self.send_terminal_command("reboot")
                self.log("🔄 Reboot command sent")
                
                return True
            else:
                self.log("❌ BLE mode verification failed")
                return False
            
        except Exception as e:
            self.log(f"❌ Configuration failed: {e}", "ERROR")
            return False
        finally:
            if self.sock:
                try:
                    self.sock.close()
                except:
                    pass
                self.log("🔌 Connection closed")

def main():
    configurer = BLEModeConfigurer()
    
    print("🚀 ESP32-C6 VESC Express - BLE Open Mode Configuration")
    print("=" * 60)
    print("This will configure BLE to open mode (no pairing required)")
    print("Current: BLE requires pairing code")
    print("Target:  BLE connects without pairing")
    print("")
    
    success = configurer.configure_ble_open_mode()
    
    if success:
        print("\n🎉 SUCCESS: BLE configured to open mode!")
        print("📱 Your phone should now connect without pairing codes")
        print("⏰ Please wait 30-60 seconds for device to restart")
    else:
        print("\n❌ FAILED: Could not configure BLE mode")
        print("💡 Try manually using LispBM: (conf-set 'ble-mode 1) (conf-store)")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())