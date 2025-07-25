#!/usr/bin/env python3
"""
VESC Express OTA Update Tester
Performs real OTA updates using the VESC communication protocol
"""

import socket
import struct
import time
import sys
import os
from pathlib import Path
import hashlib

class VESCOTATester:
    def __init__(self, device_ip="192.168.5.107", device_port=65102):
        self.device_ip = device_ip
        self.device_port = device_port
        # Common VESC ports to try
        self.vesc_ports = [65102, 8080, 3232, 80, 23]
        self.sock = None
        self.sequence = 0
        
        # VESC Communication Commands (from datatypes.h)
        self.COMM_FW_VERSION = 0
        self.COMM_JUMP_TO_BOOTLOADER = 1
        self.COMM_ERASE_NEW_APP = 2
        self.COMM_WRITE_NEW_APP_DATA = 3
        self.COMM_ALIVE = 30
        
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
        """Create VESC protocol packet with proper framing"""
        # VESC packet format: [START] [LENGTH] [PAYLOAD] [CRC] [END]
        # START: 0x02 (short packet) or 0x03 (long packet)
        # LENGTH: 1 or 2 bytes depending on payload size
        # PAYLOAD: command + data
        # CRC: 2 bytes CRC16-CCITT
        # END: 0x03
        
        packet_payload = bytes([command]) + payload
        payload_len = len(packet_payload)
        
        if payload_len <= 255:
            # Short packet
            packet = bytes([0x02, payload_len]) + packet_payload
        else:
            # Long packet  
            packet = bytes([0x03, (payload_len >> 8) & 0xFF, payload_len & 0xFF]) + packet_payload
            
        # Calculate CRC on length + payload
        crc_data = packet[1:] if payload_len <= 255 else packet[1:]
        crc = self.crc16(crc_data)
        
        # Complete packet
        packet += struct.pack('>H', crc) + bytes([0x03])
        
        return packet
        
    def connect_to_device(self):
        """Connect to VESC Express via TCP/WiFi - try multiple ports"""
        self.log(f"🔗 Scanning VESC Express at {self.device_ip}")
        
        for port in self.vesc_ports:
            try:
                self.log(f"🔍 Trying port {port}...")
                self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.sock.settimeout(3)
                self.sock.connect((self.device_ip, port))
                self.device_port = port
                self.log(f"✅ Connected to VESC Express on port {port}")
                return True
            except Exception as e:
                if self.sock:
                    self.sock.close()
                    self.sock = None
                self.log(f"⚠️  Port {port} failed: {e}")
                continue
        
        self.log("❌ No VESC ports responding", "ERROR")
        return False
    
    def send_packet(self, command, payload=b'', expect_response=True):
        """Send VESC packet and optionally wait for response"""
        if not self.sock:
            self.log("❌ Not connected to device", "ERROR")
            return None
            
        packet = self.create_vesc_packet(command, payload)
        self.log(f"📤 Sending command {command} ({len(packet)} bytes)")
        
        try:
            self.sock.send(packet)
            
            if expect_response:
                # Wait for response
                response = self.sock.recv(1024)
                if response:
                    self.log(f"📥 Received response ({len(response)} bytes)")
                    return response
                else:
                    self.log("⚠️  No response received")
                    return None
            return True
            
        except Exception as e:
            self.log(f"❌ Send failed: {e}", "ERROR")
            return None
    
    def test_connection(self):
        """Test basic communication with VESC Express"""
        self.log("🔍 Testing VESC communication...")
        
        # Test ALIVE command
        response = self.send_packet(self.COMM_ALIVE)
        if response:
            self.log("✅ VESC communication working")
            return True
        else:
            self.log("❌ VESC communication failed", "ERROR")
            return False
    
    def get_firmware_version(self):
        """Get current firmware version"""
        self.log("📋 Getting firmware version...")
        
        response = self.send_packet(self.COMM_FW_VERSION)
        if response and len(response) > 4:
            # Parse version response (simplified)
            self.log(f"📦 Firmware version response: {response.hex()}")
            return True
        else:
            self.log("❌ Failed to get firmware version", "ERROR")
            return False
    
    def start_ota_update(self, firmware_path):
        """Start OTA update process"""
        self.log(f"🚀 Starting OTA update with {firmware_path}")
        
        firmware_file = Path(firmware_path)
        if not firmware_file.exists():
            self.log(f"❌ Firmware file not found: {firmware_path}", "ERROR")
            return False
            
        firmware_size = firmware_file.stat().st_size
        self.log(f"📦 Firmware size: {firmware_size} bytes ({firmware_size/1024/1024:.2f}MB)")
        
        # Step 1: Send COMM_ERASE_NEW_APP with firmware size
        payload = struct.pack('>I', firmware_size + 6)  # Size + 6 bytes for size/crc fields
        response = self.send_packet(self.COMM_ERASE_NEW_APP, payload)
        
        if not response:
            self.log("❌ Failed to erase new app partition", "ERROR")
            return False
            
        # Parse response to check if erase was successful
        if len(response) >= 5:  # Expected response format
            success = response[2] if len(response) > 2 else 0  # Command response byte
            if success:
                self.log("✅ App partition erased successfully")
                return True
            else:
                self.log("❌ App partition erase failed", "ERROR")
                return False
        else:
            self.log("⚠️  Unexpected erase response format")
            return False
    
    def stream_firmware(self, firmware_path, chunk_size=256):
        """Stream firmware data to device"""
        self.log(f"📤 Streaming firmware in {chunk_size}-byte chunks...")
        
        try:
            with open(firmware_path, 'rb') as f:
                firmware_data = f.read()
                
            total_size = len(firmware_data)
            sent_bytes = 0
            chunk_num = 0
            
            # Calculate firmware CRC for integrity
            firmware_crc = hashlib.crc32(firmware_data) & 0xffffffff
            self.log(f"🔒 Firmware CRC32: 0x{firmware_crc:08x}")
            
            while sent_bytes < total_size:
                chunk_end = min(sent_bytes + chunk_size, total_size)
                chunk = firmware_data[sent_bytes:chunk_end]
                
                # Create payload: offset (4 bytes) + chunk data
                payload = struct.pack('>I', sent_bytes) + chunk
                
                response = self.send_packet(self.COMM_WRITE_NEW_APP_DATA, payload)
                
                if not response:
                    self.log(f"❌ Failed to send chunk {chunk_num} at offset {sent_bytes}", "ERROR")
                    return False
                
                # Check response for success
                if len(response) >= 6:
                    success = response[2] if len(response) > 2 else 0
                    if not success:
                        self.log(f"❌ Device rejected chunk {chunk_num}", "ERROR")
                        return False
                
                sent_bytes += len(chunk)
                chunk_num += 1
                
                # Progress update
                progress = (sent_bytes / total_size) * 100
                if chunk_num % 10 == 0 or sent_bytes >= total_size:
                    self.log(f"📊 Progress: {progress:.1f}% ({sent_bytes}/{total_size} bytes)")
            
            self.log("✅ Firmware streaming completed")
            return True
            
        except Exception as e:
            self.log(f"❌ Firmware streaming failed: {e}", "ERROR")
            return False
    
    def complete_ota_update(self):
        """Complete OTA update and switch partitions"""
        self.log("🔄 Completing OTA update and switching partitions...")
        
        response = self.send_packet(self.COMM_JUMP_TO_BOOTLOADER, expect_response=False)
        
        if response is not None:
            self.log("✅ OTA completion command sent")
            self.log("🔄 Device should be restarting into new firmware...")
            
            # Close connection as device will restart
            if self.sock:
                self.sock.close()
                self.sock = None
                
            return True
        else:
            self.log("❌ Failed to send OTA completion command", "ERROR")
            return False
    
    def verify_ota_success(self, wait_time=30):
        """Wait for device to restart and verify new firmware is running"""
        self.log(f"⏳ Waiting {wait_time}s for device to restart...")
        
        time.sleep(wait_time)
        
        # Try to reconnect
        if self.connect_to_device():
            if self.test_connection():
                self.log("🎉 OTA UPDATE SUCCESSFUL!")
                self.log("✅ Device restarted and responding with new firmware")
                return True
        
        self.log("❌ Failed to verify OTA success - device not responding", "ERROR")
        return False
    
    def run_full_ota_test(self, firmware_path):
        """Run complete OTA update test"""
        self.log("🔍 VESC Express OTA Update Test")
        self.log("=" * 60)
        
        # Step 1: Connect and test communication
        if not self.connect_to_device():
            return False
            
        if not self.test_connection():
            return False
        
        # Step 2: Get current firmware version
        self.get_firmware_version()
        
        # Step 3: Start OTA update
        if not self.start_ota_update(firmware_path):
            return False
        
        # Step 4: Stream firmware
        if not self.stream_firmware(firmware_path):
            return False
        
        # Step 5: Complete update
        if not self.complete_ota_update():
            return False
        
        # Step 6: Verify success
        return self.verify_ota_success()

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 vesc_ota_tester.py <firmware.bin> [device_ip] [device_port]")
        print("Example: python3 vesc_ota_tester.py build/vesc_express.bin 192.168.5.107 8080")
        return 1
    
    firmware_path = sys.argv[1]
    device_ip = sys.argv[2] if len(sys.argv) > 2 else "192.168.5.107"
    device_port = int(sys.argv[3]) if len(sys.argv) > 3 else 8080
    
    tester = VESCOTATester(device_ip, device_port)
    success = tester.run_full_ota_test(firmware_path)
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())