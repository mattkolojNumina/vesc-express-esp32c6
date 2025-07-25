#!/usr/bin/env python3
"""
Automated ESP32-C6 VESC Express Network Test
Non-interactive testing for controller debugging
"""

import socket
import time
import struct
import sys
import threading

class AutoNetworkVESCTest:
    def __init__(self, host="192.168.5.107", port=65102):
        self.host = host
        self.port = port
        self.sock = None
        self.responses = []
        
        # VESC Commands
        self.COMM_FW_VERSION = 0
        self.COMM_GET_VALUES = 4
        self.COMM_ALIVE = 30
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
    
    def test_connection(self):
        """Test basic TCP connection"""
        self.log("🔗 Testing TCP connection...")
        
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.settimeout(5)
            self.sock.connect((self.host, self.port))
            self.log("✅ TCP connection successful")
            return True
        except Exception as e:
            self.log(f"❌ TCP connection failed: {e}", "ERROR")
            return False
    
    def send_and_monitor(self, command, command_name, timeout=5):
        """Send command and monitor for any response"""
        packet = self.create_vesc_packet(command)
        self.log(f"📤 Sending {command_name} ({len(packet)} bytes): {packet.hex()}")
        
        try:
            # Send command
            self.sock.send(packet)
            
            # Monitor for response
            self.sock.settimeout(timeout)
            response_data = b''
            
            start_time = time.time()
            while time.time() - start_time < timeout:
                try:
                    data = self.sock.recv(1024)
                    if data:
                        response_data += data
                        self.log(f"📥 Response data ({len(data)} bytes): {data.hex()}")
                    else:
                        break
                except socket.timeout:
                    break
            
            if response_data:
                self.log(f"✅ {command_name} got response: {len(response_data)} bytes total")
                self.responses.append((command_name, response_data))
                return True
            else:
                self.log(f"⚠️  {command_name} - no response received")
                return False
                
        except Exception as e:
            self.log(f"❌ {command_name} failed: {e}", "ERROR")
            return False
    
    def test_vesc_protocol_commands(self):
        """Test various VESC protocol commands"""
        self.log("🧪 Testing VESC protocol commands...")
        
        tests = [
            (self.COMM_ALIVE, "ALIVE"),
            (self.COMM_FW_VERSION, "FIRMWARE_VERSION"),
            (self.COMM_GET_VALUES, "GET_VALUES"),
        ]
        
        results = {}
        for command, name in tests:
            self.log(f"\n--- Testing {name} ---")
            success = self.send_and_monitor(command, name)
            results[name] = success
            time.sleep(1)  # Pause between commands
        
        return results
    
    def test_raw_data_sending(self):
        """Test sending various raw data formats"""
        self.log("\n🔬 Testing raw data formats...")
        
        test_data = [
            (b"hello\\n", "ASCII greeting"),
            (b"\\x02\\x01\\x1e\\xf3\\xff\\x03", "Manual ALIVE packet"),
            (b"\\x00\\x00\\x00\\x00", "Zero bytes"),
            (b"\\xff\\xff\\xff\\xff", "Max bytes"),
        ]
        
        for data, description in test_data:
            self.log(f"📤 Sending {description}: {data.hex()}")
            try:
                self.sock.send(data)
                time.sleep(0.5)
                
                # Check for any response
                self.sock.settimeout(1)
                try:
                    response = self.sock.recv(1024)
                    if response:
                        self.log(f"📥 Response: {response.hex()}")
                    else:
                        self.log("⚠️  No response")
                except socket.timeout:
                    self.log("⚠️  No response (timeout)")
                    
            except Exception as e:
                self.log(f"❌ Send failed: {e}", "ERROR")
    
    def run_comprehensive_test(self):
        """Run comprehensive automated test"""
        self.log("🚀 ESP32-C6 VESC Express - Automated Network Test")
        self.log("=" * 60)
        
        # Test 1: Basic connection
        if not self.test_connection():
            return False
        
        try:
            # Test 2: VESC protocol commands
            protocol_results = self.test_vesc_protocol_commands()
            
            # Test 3: Raw data sending
            self.test_raw_data_sending()
            
            # Test 4: Keep connection alive and monitor
            self.log("\n📡 Monitoring connection for 10 seconds...")
            monitor_start = time.time()
            while time.time() - monitor_start < 10:
                try:
                    self.sock.settimeout(1)
                    data = self.sock.recv(1024)
                    if data:
                        self.log(f"📥 Spontaneous data: {data.hex()}")
                except socket.timeout:
                    pass  # Normal timeout
                except Exception as e:
                    self.log(f"⚠️  Monitor error: {e}")
                    break
            
            # Summary
            self.log("\n📊 Test Summary:")
            self.log(f"   TCP Connection: ✅")
            
            working_commands = sum(1 for success in protocol_results.values() if success)
            total_commands = len(protocol_results)
            self.log(f"   VESC Commands: {working_commands}/{total_commands} working")
            
            for cmd, success in protocol_results.items():
                status = "✅" if success else "❌"
                self.log(f"     {cmd}: {status}")
            
            self.log(f"   Total Responses: {len(self.responses)}")
            
            if working_commands > 0:
                self.log("🎉 ESP32-C6 Controller Communication: FUNCTIONAL")
            else:
                self.log("⚠️  ESP32-C6 Controller: TCP connected but no VESC responses")
            
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
    
    tester = AutoNetworkVESCTest(host)
    success = tester.run_comprehensive_test()
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())