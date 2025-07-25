#!/usr/bin/env python3
"""
ESP32-C6 VESC Express Network Debugger
Debug VESC Express over WiFi network at 192.168.5.107
"""

import socket
import time
import struct
import sys
from threading import Thread
import json

class NetworkVESCDebugger:
    def __init__(self, host="192.168.5.107", port=65102):
        self.host = host
        self.port = port
        self.sock = None
        self.connected = False
        
        # VESC Commands
        self.COMM_FW_VERSION = 0
        self.COMM_JUMP_TO_BOOTLOADER = 1
        self.COMM_ERASE_NEW_APP = 2
        self.COMM_WRITE_NEW_APP_DATA = 3
        self.COMM_GET_VALUES = 4
        self.COMM_SET_DUTY = 5
        self.COMM_SET_CURRENT = 6
        self.COMM_SET_CURRENT_BRAKE = 7
        self.COMM_SET_RPM = 8
        self.COMM_SET_POS = 9
        self.COMM_SET_HANDBRAKE = 10
        self.COMM_SET_DETECT = 11
        self.COMM_SET_SERVO_POS = 12
        self.COMM_SET_MCCONF = 13
        self.COMM_GET_MCCONF = 14
        self.COMM_GET_MCCONF_DEFAULT = 15
        self.COMM_SET_APPCONF = 16
        self.COMM_GET_APPCONF = 17
        self.COMM_GET_APPCONF_DEFAULT = 18
        self.COMM_SAMPLE_PRINT = 19
        self.COMM_TERMINAL_CMD = 20
        self.COMM_PRINT = 21
        self.COMM_ROTOR_POSITION = 22
        self.COMM_EXPERIMENT_SAMPLE = 23
        self.COMM_DETECT_MOTOR_PARAM = 24
        self.COMM_DETECT_MOTOR_R_L = 25
        self.COMM_DETECT_MOTOR_FLUX_LINKAGE = 26
        self.COMM_DETECT_ENCODER = 27
        self.COMM_DETECT_HALL_FOC = 28
        self.COMM_REBOOT = 29
        self.COMM_ALIVE = 30
        self.COMM_GET_DECODED_PPM = 31
        self.COMM_GET_DECODED_ADC = 32
        self.COMM_GET_DECODED_CHUK = 33
        self.COMM_FORWARD_CAN = 34
        self.COMM_SET_CHUCK_DATA = 35
        self.COMM_CUSTOM_APP_DATA = 36
        self.COMM_NRF_START_PAIRING = 37
        
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
        """Connect to VESC Express over network"""
        self.log(f"🔗 Connecting to VESC Express at {self.host}:{self.port}")
        
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.settimeout(5)
            self.sock.connect((self.host, self.port))
            self.connected = True
            self.log("✅ Connected to VESC Express via WiFi")
            return True
        except Exception as e:
            self.log(f"❌ Connection failed: {e}", "ERROR")
            return False
    
    def disconnect(self):
        """Disconnect from VESC Express"""
        if self.sock:
            self.sock.close()
            self.connected = False
            self.log("🔌 Disconnected from VESC Express")
    
    def send_command(self, command, payload=b'', timeout=3):
        """Send VESC command and get response"""
        if not self.connected:
            self.log("❌ Not connected to device", "ERROR")
            return None
            
        packet = self.create_vesc_packet(command, payload)
        self.log(f"📤 Sending command {command} ({len(packet)} bytes): {packet.hex()}")
        
        try:
            self.sock.send(packet)
            
            # Wait for response
            self.sock.settimeout(timeout)
            response = b''
            
            start_time = time.time()
            while time.time() - start_time < timeout:
                try:
                    data = self.sock.recv(1024)
                    if data:
                        response += data
                        self.log(f"📥 Received {len(data)} bytes: {data.hex()}")
                        
                        # Check if we have a complete packet
                        if len(response) >= 4 and response[0] in [0x02, 0x03]:
                            if response[0] == 0x02 and len(response) >= response[1] + 4:
                                break
                            elif response[0] == 0x03 and len(response) >= 4:
                                expected_len = (response[1] << 8) | response[2]
                                if len(response) >= expected_len + 5:
                                    break
                except socket.timeout:
                    break
                    
            if response:
                self.log(f"📥 Complete response ({len(response)} bytes): {response.hex()}")
                return response
            else:
                self.log("⚠️  No response received")
                return None
                
        except Exception as e:
            self.log(f"❌ Send failed: {e}", "ERROR")
            return None
    
    def test_basic_communication(self):
        """Test basic VESC communication"""
        self.log("🔍 Testing basic VESC communication...")
        
        response = self.send_command(self.COMM_ALIVE)
        if response:
            self.log("✅ COMM_ALIVE successful - VESC is responding")
            return True
        else:
            self.log("❌ COMM_ALIVE failed - No response from VESC", "ERROR")
            return False
    
    def get_firmware_version(self):
        """Get firmware version information"""
        self.log("📋 Getting firmware version...")
        
        response = self.send_command(self.COMM_FW_VERSION)
        if response and len(response) > 4:
            self.log(f"📦 Firmware version response: {response.hex()}")
            
            # Try to parse version info (simplified)
            try:
                if len(response) >= 10:
                    major = response[2]
                    minor = response[3]
                    self.log(f"✅ Firmware version: {major}.{minor}")
            except:
                self.log("⚠️  Could not parse version info")
            return True
        else:
            self.log("❌ Failed to get firmware version", "ERROR")
            return False
    
    def get_motor_values(self):
        """Get real-time motor values"""
        self.log("⚡ Getting motor values...")
        
        response = self.send_command(self.COMM_GET_VALUES)
        if response and len(response) > 10:
            self.log(f"📊 Motor values response: {response.hex()}")
            
            # Parse basic motor values (simplified)
            try:
                if len(response) >= 20:
                    # This is a simplified parsing - real VESC values are more complex
                    self.log("✅ Motor values received (detailed parsing would show RPM, current, etc.)")
            except:
                self.log("⚠️  Could not parse motor values")
            return True
        else:
            self.log("❌ Failed to get motor values", "ERROR")
            return False
    
    def send_terminal_command(self, cmd_text):
        """Send terminal command to VESC"""
        self.log(f"💻 Sending terminal command: '{cmd_text}'")
        
        cmd_bytes = cmd_text.encode('utf-8')
        response = self.send_command(self.COMM_TERMINAL_CMD, cmd_bytes)
        
        if response:
            self.log("✅ Terminal command sent successfully")
            return True
        else:
            self.log("❌ Terminal command failed", "ERROR")
            return False
    
    def monitor_realtime_data(self, duration=30):
        """Monitor real-time data from VESC"""
        self.log(f"📡 Starting {duration}s real-time data monitoring...")
        
        start_time = time.time()
        sample_count = 0
        
        while time.time() - start_time < duration:
            response = self.send_command(self.COMM_GET_VALUES, timeout=1)
            if response:
                sample_count += 1
                self.log(f"📊 Sample {sample_count}: {len(response)} bytes received")
            else:
                self.log("⚠️  No data received")
                
            time.sleep(1)  # 1Hz sampling
            
        self.log(f"✅ Monitoring complete: {sample_count} samples in {duration}s")
    
    def comprehensive_debug_session(self):
        """Run comprehensive debugging session"""
        self.log("🔍 ESP32-C6 VESC Express Network Debug Session")
        self.log("=" * 60)
        
        # Step 1: Connect
        if not self.connect():
            return False
            
        try:
            # Step 2: Test basic communication
            if not self.test_basic_communication():
                return False
                
            # Step 3: Get firmware info
            self.get_firmware_version()
            
            # Step 4: Get motor values
            self.get_motor_values()
            
            # Step 5: Test terminal commands
            self.send_terminal_command("help")
            time.sleep(1)
            self.send_terminal_command("uptime")
            
            # Step 6: Short real-time monitoring
            self.monitor_realtime_data(10)
            
            self.log("🎉 Network debugging session completed successfully!")
            return True
            
        except KeyboardInterrupt:
            self.log("⚠️  Debug session interrupted by user")
            return False
        finally:
            self.disconnect()

def main():
    if len(sys.argv) > 1:
        host = sys.argv[1]
    else:
        host = "192.168.5.107"
        
    debugger = NetworkVESCDebugger(host)
    success = debugger.comprehensive_debug_session()
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())