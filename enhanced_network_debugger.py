#!/usr/bin/env python3
"""
Enhanced ESP32-C6 VESC Express Network Debugger
Fixed packet handling and real-time debugging
"""

import socket
import time
import struct
import sys
import threading
from threading import Thread, Event

class EnhancedNetworkVESCDebugger:
    def __init__(self, host="192.168.5.107", port=65102):
        self.host = host
        self.port = port
        self.sock = None
        self.connected = False
        self.monitoring = False
        self.stop_event = Event()
        
        # VESC Commands
        self.COMM_FW_VERSION = 0
        self.COMM_GET_VALUES = 4
        self.COMM_ALIVE = 30
        self.COMM_TERMINAL_CMD = 20
        self.COMM_GET_MCCONF = 14
        
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
        """Create VESC protocol packet with exact format"""
        packet_payload = bytes([command]) + payload
        payload_len = len(packet_payload)
        
        packet = b''
        
        # Length encoding based on VESC protocol
        if payload_len <= 255:
            packet += bytes([0x02, payload_len])  # Short packet
        elif payload_len <= 65535:
            packet += bytes([0x03, (payload_len >> 8) & 0xFF, payload_len & 0xFF])  # Long packet
        else:
            packet += bytes([0x04, (payload_len >> 16) & 0xFF, (payload_len >> 8) & 0xFF, payload_len & 0xFF])
            
        # Add payload
        packet += packet_payload
        
        # Calculate CRC on payload only
        crc = self.crc16(packet_payload)
        
        # Add CRC (big-endian) and end byte
        packet += struct.pack('>H', crc) + bytes([0x03])
        
        return packet
    
    def connect_persistent(self):
        """Create persistent connection with proper socket options"""
        self.log(f"🔗 Establishing persistent connection to {self.host}:{self.port}")
        
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            
            # Set socket options for reliable communication
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
            self.sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)  # Disable Nagle
            self.sock.settimeout(10)  # Longer timeout for network
            
            self.sock.connect((self.host, self.port))
            self.connected = True
            self.log("✅ Persistent connection established")
            
            # Start response monitor thread
            self.monitor_thread = Thread(target=self.response_monitor, daemon=True)
            self.monitor_thread.start()
            
            return True
        except Exception as e:
            self.log(f"❌ Connection failed: {e}", "ERROR")
            return False
    
    def response_monitor(self):
        """Monitor incoming responses continuously"""
        buffer = b''
        
        while self.connected and not self.stop_event.is_set():
            try:
                self.sock.settimeout(1.0)  # 1 second timeout for monitoring
                data = self.sock.recv(1024)
                
                if data:
                    buffer += data
                    self.log(f"📥 Raw data ({len(data)} bytes): {data.hex()}")
                    
                    # Try to parse complete packets from buffer
                    while len(buffer) >= 4:
                        packet, remaining = self.extract_packet(buffer)
                        if packet:
                            self.parse_vesc_response(packet)
                            buffer = remaining
                        else:
                            break
                            
            except socket.timeout:
                continue  # Normal timeout, keep monitoring
            except Exception as e:
                if self.connected:  # Only log if we expect to be connected
                    self.log(f"⚠️  Monitor error: {e}")
                break
    
    def extract_packet(self, buffer):
        """Extract a complete VESC packet from buffer"""
        if len(buffer) < 4:
            return None, buffer
            
        # Check start byte
        if buffer[0] not in [0x02, 0x03, 0x04]:
            # Skip invalid start byte
            return None, buffer[1:]
        
        try:
            if buffer[0] == 0x02:  # Short packet
                if len(buffer) < 2:
                    return None, buffer
                length = buffer[1]
                total_len = length + 4  # start + len + payload + crc + end
                
            elif buffer[0] == 0x03:  # Long packet
                if len(buffer) < 3:
                    return None, buffer
                length = (buffer[1] << 8) | buffer[2]
                total_len = length + 5  # start + len2 + payload + crc + end
                
            elif buffer[0] == 0x04:  # Very long packet
                if len(buffer) < 4:
                    return None, buffer
                length = (buffer[1] << 16) | (buffer[2] << 8) | buffer[3]
                total_len = length + 6  # start + len3 + payload + crc + end
            
            if len(buffer) >= total_len:
                packet = buffer[:total_len]
                remaining = buffer[total_len:]
                
                # Verify end byte
                if packet[-1] == 0x03:
                    return packet, remaining
                else:
                    self.log(f"⚠️  Invalid end byte: {packet[-1]:02x}")
                    
        except Exception as e:
            self.log(f"⚠️  Packet extraction error: {e}")
            
        return None, buffer[1:]  # Skip first byte and try again
    
    def parse_vesc_response(self, packet):
        """Parse and display VESC response packet"""
        self.log(f"📦 Complete packet ({len(packet)} bytes): {packet.hex()}")
        
        try:
            if packet[0] == 0x02:
                payload_start = 2
                payload_len = packet[1]
            elif packet[0] == 0x03:
                payload_start = 3
                payload_len = (packet[1] << 8) | packet[2]
            else:
                payload_start = 4
                payload_len = (packet[1] << 16) | (packet[2] << 8) | packet[3]
            
            if len(packet) >= payload_start + payload_len:
                payload = packet[payload_start:payload_start + payload_len]
                if len(payload) > 0:
                    command = payload[0]
                    data = payload[1:]
                    self.log(f"✅ Response - Command: {command}, Data: {data.hex()}")
                    
                    # Parse specific responses
                    if command == self.COMM_ALIVE:
                        self.log("💓 ALIVE response received")
                    elif command == self.COMM_FW_VERSION:
                        self.parse_firmware_version(data)
                    elif command == self.COMM_GET_VALUES:
                        self.log(f"⚡ Motor values received ({len(data)} bytes)")
                        
        except Exception as e:
            self.log(f"⚠️  Response parsing error: {e}")
    
    def parse_firmware_version(self, data):
        """Parse firmware version response"""
        try:
            if len(data) >= 2:
                major = data[0]
                minor = data[1]
                self.log(f"📦 Firmware version: {major}.{minor}")
        except:
            self.log("⚠️  Could not parse firmware version")
    
    def send_command_async(self, command, payload=b''):
        """Send command without waiting for specific response"""
        if not self.connected:
            self.log("❌ Not connected", "ERROR")
            return False
            
        packet = self.create_vesc_packet(command, payload)
        self.log(f"📤 Sending command {command} ({len(packet)} bytes): {packet.hex()}")
        
        try:
            self.sock.send(packet)
            return True
        except Exception as e:
            self.log(f"❌ Send failed: {e}", "ERROR")
            return False
    
    def interactive_debug_session(self):
        """Interactive debugging session"""
        self.log("🎮 ESP32-C6 VESC Express Interactive Debug Session")
        self.log("=" * 60)
        
        if not self.connect_persistent():
            return
            
        try:
            self.log("📋 Available commands:")
            self.log("  1 - Send ALIVE command")
            self.log("  2 - Get firmware version")
            self.log("  3 - Get motor values")
            self.log("  4 - Send terminal command")
            self.log("  5 - Start continuous monitoring")
            self.log("  q - Quit")
            
            while True:
                try:
                    cmd = input("\n👉 Enter command: ").strip().lower()
                    
                    if cmd == 'q':
                        break
                    elif cmd == '1':
                        self.send_command_async(self.COMM_ALIVE)
                    elif cmd == '2':
                        self.send_command_async(self.COMM_FW_VERSION)
                    elif cmd == '3':
                        self.send_command_async(self.COMM_GET_VALUES)
                    elif cmd == '4':
                        term_cmd = input("Terminal command: ")
                        self.send_command_async(self.COMM_TERMINAL_CMD, term_cmd.encode())
                    elif cmd == '5':
                        self.continuous_monitoring()
                    else:
                        self.log("❓ Unknown command")
                        
                except KeyboardInterrupt:
                    break
        
        finally:
            self.cleanup()
    
    def continuous_monitoring(self):
        """Start continuous monitoring of motor values"""
        self.log("📡 Starting continuous monitoring (press Enter to stop)...")
        
        def monitor_loop():
            while not self.stop_event.is_set():
                self.send_command_async(self.COMM_GET_VALUES)
                time.sleep(1)  # 1Hz
        
        monitor_thread = Thread(target=monitor_loop, daemon=True)
        monitor_thread.start()
        
        input()  # Wait for user input
        self.stop_event.set()
        self.log("🛑 Monitoring stopped")
    
    def cleanup(self):
        """Clean up connection and threads"""
        self.log("🔌 Cleaning up connection...")
        self.connected = False
        self.stop_event.set()
        
        if self.sock:
            try:
                self.sock.close()
            except:
                pass
                
        self.log("✅ Cleanup complete")

def main():
    host = sys.argv[1] if len(sys.argv) > 1 else "192.168.5.107"
    
    debugger = EnhancedNetworkVESCDebugger(host)
    debugger.interactive_debug_session()

if __name__ == "__main__":
    main()