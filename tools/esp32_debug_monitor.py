#!/usr/bin/env python3
"""
ESP32-C6 WiFi Debugging Monitor
Monitors ESP32-C6 serial output for WiFi debugging status
"""

import os
import sys
import time
import serial
import threading
from datetime import datetime

class ESP32DebugMonitor:
    def __init__(self, port='/dev/ttyACM0', baudrate=115200):
        self.port = port
        self.baudrate = baudrate
        self.running = False
        self.ser = None
        
    def start_monitoring(self):
        """Start monitoring ESP32-C6 debug output"""
        try:
            # Install pyserial if not available
            try:
                import serial
            except ImportError:
                print("📦 Installing pyserial...")
                import subprocess
                subprocess.check_call([sys.executable, "-m", "pip", "install", "pyserial"])
                import serial
            
            # Check if port exists and find available ports
            available_ports = []
            for port_pattern in ["/dev/ttyACM*", "/dev/ttyUSB*"]:
                import glob
                available_ports.extend(glob.glob(port_pattern))
            
            if not available_ports:
                print("❌ No serial ports found")
                print("🔍 Make sure ESP32-C6 is connected via USB")
                return False
            
            # Use first available port if specified port doesn't exist
            if not os.path.exists(self.port):
                self.port = available_ports[0]
                print(f"🔄 Using available port: {self.port}")
            
            # Check permissions
            if not os.access(self.port, os.R_OK | os.W_OK):
                print(f"❌ No permission to access {self.port}")
                print(f"💡 Try: sudo chmod 666 {self.port}")
                print(f"💡 Or add user to dialout group: sudo usermod -a -G dialout $USER")
                return False
            
            print(f"🔍 ESP32-C6 WiFi Debug Monitor Started")
            print(f"📡 Port: {self.port} @ {self.baudrate} baud")
            print(f"⏰ Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print("🔎 Looking for WiFi debugging messages...")
            print("=" * 60)
            
            self.ser = serial.Serial(self.port, self.baudrate, timeout=1)
            self.running = True
            
            wifi_debug_keywords = [
                'wifi', 'debug', 'http', 'tcp', 'server', 'ap', 'sta',
                'connected', 'debug_wifi_delayed_init', 'debug_wifi_init',
                'port 23456', 'port 80', 'port 65102', 'VESC WiFi',
                '192.168.4.1', '192.168.5.', 'delayed wifi', 'wifi debugging'
            ]
            
            message_count = 0
            wifi_debug_count = 0
            
            while self.running:
                try:
                    if self.ser.in_waiting:
                        line = self.ser.readline().decode('utf-8', errors='ignore').strip()
                        if line:
                            message_count += 1
                            timestamp = datetime.now().strftime('%H:%M:%S.%f')[:-3]
                            
                            # Check for WiFi debugging related messages
                            line_lower = line.lower()
                            is_wifi_debug = any(keyword in line_lower for keyword in wifi_debug_keywords)
                            
                            if is_wifi_debug:
                                wifi_debug_count += 1
                                if 'error' in line_lower or 'fail' in line_lower:
                                    print(f"❌ [{timestamp}] {line}")
                                elif 'connected' in line_lower or 'start' in line_lower or 'init' in line_lower:
                                    print(f"✅ [{timestamp}] {line}")
                                elif any(port in line for port in ['23456', '65102', '80']):
                                    print(f"🔧 [{timestamp}] {line}")
                                else:
                                    print(f"📡 [{timestamp}] {line}")
                            elif 'error' in line_lower or 'warning' in line_lower:
                                print(f"⚠️  [{timestamp}] {line}")
                            elif message_count % 50 == 0:  # Show periodic status
                                print(f"📊 [{timestamp}] Messages: {message_count}, WiFi Debug: {wifi_debug_count}")
                    else:
                        time.sleep(0.1)
                        
                except KeyboardInterrupt:
                    print("\n🛑 Monitoring stopped by user")
                    print(f"📊 Total messages: {message_count}, WiFi debug messages: {wifi_debug_count}")
                    break
                except Exception as e:
                    print(f"❌ Error reading serial: {e}")
                    time.sleep(1)
                    
        except Exception as e:
            print(f"❌ Failed to start monitoring: {e}")
            import traceback
            traceback.print_exc()
            return False
            
        finally:
            if self.ser:
                self.ser.close()
            print("📋 WiFi debugging verification session ended")
            
        return True
    
    def stop_monitoring(self):
        """Stop monitoring"""
        self.running = False

def main():
    if len(sys.argv) > 1:
        port = sys.argv[1]
    else:
        port = '/dev/ttyACM0'
    
    monitor = ESP32DebugMonitor(port)
    
    try:
        monitor.start_monitoring()
    except KeyboardInterrupt:
        print("\n🛑 Monitoring stopped")
    finally:
        monitor.stop_monitoring()

if __name__ == "__main__":
    main()