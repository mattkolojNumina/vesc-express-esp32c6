#!/usr/bin/env python3
"""
ESP32-C6 VESC Express CAN Bus Tester
Test CAN communication between ESP32-C6 and VESC controller
"""

import socket
import time
import struct
import sys
import threading
from threading import Event

class CANBusTester:
    def __init__(self, host="192.168.5.107", port=65102):
        self.host = host
        self.port = port
        self.sock = None
        self.connected = False
        self.monitoring = False
        self.stop_event = Event()
        
        # VESC CAN Commands
        self.COMM_PING_CAN = 15
        self.COMM_FORWARD_CAN = 34
        self.COMM_CAN_FWD_FRAME = 35
        self.COMM_TERMINAL_CMD = 20
        
        # CAN-specific commands
        self.CAN_PACKET_SET_DUTY = 0
        self.CAN_PACKET_SET_CURRENT = 1
        self.CAN_PACKET_SET_CURRENT_BRAKE = 2
        self.CAN_PACKET_SET_RPM = 3
        self.CAN_PACKET_SET_POS = 4
        self.CAN_PACKET_FILL_RX_BUFFER = 5
        self.CAN_PACKET_FILL_RX_BUFFER_LONG = 6
        self.CAN_PACKET_PROCESS_RX_BUFFER = 7
        self.CAN_PACKET_PROCESS_SHORT_BUFFER = 8
        self.CAN_PACKET_STATUS = 9
        self.CAN_PACKET_SET_CURRENT_REL = 10
        self.CAN_PACKET_SET_CURRENT_BRAKE_REL = 11
        self.CAN_PACKET_SET_CURRENT_HANDBRAKE = 12
        self.CAN_PACKET_SET_CURRENT_HANDBRAKE_REL = 13
        self.CAN_PACKET_STATUS_2 = 14
        self.CAN_PACKET_STATUS_3 = 15
        self.CAN_PACKET_STATUS_4 = 16
        self.CAN_PACKET_PING = 17
        self.CAN_PACKET_PONG = 18
        self.CAN_PACKET_DETECT_APPLY_ALL_FOC = 19
        self.CAN_PACKET_DETECT_APPLY_ALL_FOC_RES = 20
        self.CAN_PACKET_CONF_CURRENT_LIMITS = 21
        self.CAN_PACKET_CONF_STORE_CURRENT_LIMITS = 22
        self.CAN_PACKET_CONF_CURRENT_LIMITS_IN = 23
        self.CAN_PACKET_CONF_STORE_CURRENT_LIMITS_IN = 24
        self.CAN_PACKET_CONF_FOC_ERPMS = 25
    
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
        """Connect to ESP32-C6 VESC Express"""
        self.log(f"🔗 Connecting to ESP32-C6 at {self.host}:{self.port}")
        
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.settimeout(10)
            self.sock.connect((self.host, self.port))
            self.connected = True
            self.log("✅ Connected to ESP32-C6 VESC Express")
            return True
        except Exception as e:
            self.log(f"❌ Connection failed: {e}", "ERROR")
            return False
    
    def send_command(self, command, payload=b'', timeout=5):
        """Send VESC command and monitor response"""
        if not self.connected:
            self.log("❌ Not connected", "ERROR")
            return None
            
        packet = self.create_vesc_packet(command, payload)
        self.log(f"📤 Sending command {command} ({len(packet)} bytes): {packet.hex()}")
        
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
                        self.log(f"📥 Response ({len(data)} bytes): {data.hex()}")
                    else:
                        break
                except socket.timeout:
                    break
            
            return response if response else None
                
        except Exception as e:
            self.log(f"❌ Send failed: {e}", "ERROR")
            return None
    
    def ping_can_devices(self):
        """Ping CAN devices to discover connected controllers"""
        self.log("🔍 Scanning for CAN devices (IDs 0-10)...")
        
        discovered_devices = []
        
        for can_id in range(11):  # Common VESC CAN IDs 0-10
            self.log(f"📡 Pinging CAN ID {can_id}...")
            
            # Create COMM_PING_CAN payload with target ID
            payload = struct.pack('B', can_id)
            response = self.send_command(self.COMM_PING_CAN, payload, timeout=3)
            
            if response and len(response) > 5:
                self.log(f"✅ CAN ID {can_id}: Device responded!")
                discovered_devices.append(can_id)
                
                # Try to parse response
                try:
                    if len(response) >= 10:
                        # Parse the ping response (simplified)
                        self.log(f"📦 Response data: {response.hex()}")
                except:
                    pass
            else:
                self.log(f"❌ CAN ID {can_id}: No response")
            
            time.sleep(0.5)  # Small delay between pings
        
        if discovered_devices:
            self.log(f"🎉 Found {len(discovered_devices)} CAN devices: {discovered_devices}")
        else:
            self.log("⚠️  No CAN devices responded to ping")
            
        return discovered_devices
    
    def test_can_communication(self, can_id=0):
        """Test CAN communication with specific device"""
        self.log(f"🧪 Testing CAN communication with device ID {can_id}...")
        
        # Test 1: Send CAN Ping
        self.log(f"📡 Sending CAN PING to ID {can_id}")
        can_ping_payload = bytes([can_id, self.CAN_PACKET_PING])
        response = self.send_command(self.COMM_FORWARD_CAN, can_ping_payload)
        
        if response:
            self.log("✅ CAN PING successful")
        else:
            self.log("❌ CAN PING failed")
        
        time.sleep(1)
        
        # Test 2: Request Status
        self.log(f"📊 Requesting status from CAN ID {can_id}")
        can_status_payload = bytes([can_id, self.CAN_PACKET_STATUS])
        response = self.send_command(self.COMM_FORWARD_CAN, can_status_payload)
        
        if response:
            self.log("✅ CAN Status request successful")
            if len(response) > 10:
                self.log("📈 Received motor status data")
        else:
            self.log("❌ CAN Status request failed")
        
        time.sleep(1)
        
        # Test 3: Send minimal current command (0A - safe)
        self.log(f"🔧 Sending safe current command (0A) to CAN ID {can_id}")
        current_amps = 0.0  # Safe 0A current
        current_payload = bytes([can_id, self.CAN_PACKET_SET_CURRENT]) + struct.pack('>f', current_amps)
        response = self.send_command(self.COMM_FORWARD_CAN, current_payload)
        
        if response:
            self.log("✅ CAN current command successful")
        else:
            self.log("❌ CAN current command failed")
        
        return response is not None
    
    def send_terminal_can_commands(self):
        """Send terminal commands related to CAN"""
        self.log("💻 Sending CAN-related terminal commands...")
        
        can_commands = [
            "can list",      # List CAN devices
            "can scan",      # Scan for CAN devices  
            "can status",    # CAN bus status
            "help can",      # CAN help
        ]
        
        for cmd in can_commands:
            self.log(f"💻 Terminal command: '{cmd}'")
            response = self.send_command(self.COMM_TERMINAL_CMD, cmd.encode())
            
            if response:
                self.log(f"✅ Command '{cmd}' sent successfully")
                # Parse terminal response if available
                try:
                    if len(response) > 10:
                        # Terminal responses are usually longer
                        self.log("📄 Terminal output received")
                except:
                    pass
            else:
                self.log(f"❌ Command '{cmd}' failed")
            
            time.sleep(2)  # Wait for command processing
    
    def monitor_can_traffic(self, duration=30):
        """Monitor CAN traffic for specified duration"""
        self.log(f"📡 Monitoring CAN traffic for {duration} seconds...")
        self.log("   (This will capture any spontaneous CAN messages)")
        
        start_time = time.time()
        message_count = 0
        
        while time.time() - start_time < duration:
            try:
                self.sock.settimeout(1)
                data = self.sock.recv(1024)
                
                if data:
                    message_count += 1
                    self.log(f"📥 CAN traffic #{message_count}: {data.hex()}")
                    
            except socket.timeout:
                pass  # Normal timeout
            except Exception as e:
                self.log(f"⚠️  Monitor error: {e}")
                break
        
        self.log(f"📊 Monitoring complete: {message_count} messages captured")
    
    def comprehensive_can_test(self):
        """Run comprehensive CAN bus testing"""
        self.log("🚀 ESP32-C6 CAN Bus Comprehensive Test")
        self.log("=" * 60)
        
        # Step 1: Connect
        if not self.connect():
            return False
        
        try:
            # Step 2: Terminal CAN commands
            self.send_terminal_can_commands()
            
            # Step 3: Ping CAN devices
            discovered_devices = self.ping_can_devices()
            
            # Step 4: Test communication with discovered devices
            if discovered_devices:
                for device_id in discovered_devices[:3]:  # Test up to 3 devices
                    self.log(f"\n--- Testing CAN Device {device_id} ---")
                    self.test_can_communication(device_id)
            else:
                self.log("\n🧪 Testing default CAN ID 0 (even if no ping response)...")
                self.test_can_communication(0)
            
            # Step 5: Monitor for spontaneous CAN traffic
            self.log("\n📡 Monitoring for CAN traffic...")
            self.monitor_can_traffic(15)  # 15 second monitoring
            
            # Step 6: Summary
            self.log("\n📊 CAN Bus Test Summary:")
            self.log(f"   ESP32-C6 Connection: ✅")
            self.log(f"   CAN Devices Found: {len(discovered_devices)}")
            if discovered_devices:
                self.log(f"   Device IDs: {discovered_devices}")
                self.log("🎉 CAN BUS COMMUNICATION: FUNCTIONAL")
            else:
                self.log("⚠️  CAN BUS STATUS: No devices responded to ping")
                self.log("   (This could mean: no VESC connected, different CAN IDs, or bus issues)")
            
            return True
            
        except Exception as e:
            self.log(f"❌ Test failed: {e}", "ERROR")
            return False
        finally:
            if self.sock:
                self.sock.close()
                self.log("🔌 Connection closed")

def main():
    host = sys.argv[1] if len(sys.argv) > 1 else "192.168.5.107"
    
    tester = CANBusTester(host)
    success = tester.comprehensive_can_test()
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())