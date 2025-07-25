#!/usr/bin/env python3
"""
ESP32-C6 Bluetooth Debug Monitor
Monitors ESP32-C6 serial output for Bluetooth-related information
"""

import serial
import time
import re
import sys
from datetime import datetime

class BluetoothDebugMonitor:
    def __init__(self, port='/dev/ttyACM0', baudrate=115200):
        self.port = port
        self.baudrate = baudrate
        self.ser = None
        
        # BLE-related log patterns
        self.ble_patterns = {
            'init': re.compile(r'BLE.*init', re.IGNORECASE),
            'advertising': re.compile(r'advertising|adv', re.IGNORECASE),
            'connection': re.compile(r'connect|disconnect', re.IGNORECASE),
            'gatt': re.compile(r'gatt|service|characteristic', re.IGNORECASE),
            'error': re.compile(r'error|fail|timeout', re.IGNORECASE),
            'mode': re.compile(r'BLE mode:', re.IGNORECASE),
            'device_name': re.compile(r'device.*name', re.IGNORECASE)
        }
        
        self.bluetooth_status = {
            'initialized': False,
            'advertising': False,
            'connected': False,
            'device_name': None,
            'mode': None,
            'errors': []
        }
    
    def connect(self):
        """Connect to ESP32-C6 serial port"""
        try:
            self.ser = serial.Serial(self.port, self.baudrate, timeout=1)
            print(f"✅ Connected to {self.port} at {self.baudrate} baud")
            return True
        except Exception as e:
            print(f"❌ Failed to connect to {self.port}: {e}")
            return False
    
    def parse_log_line(self, line):
        """Parse a log line for Bluetooth information"""
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        
        for pattern_name, pattern in self.ble_patterns.items():
            if pattern.search(line):
                print(f"[{timestamp}] 🔵 BLE-{pattern_name.upper()}: {line.strip()}")
                
                # Update status based on log content
                if pattern_name == 'init' and 'complete' in line.lower():
                    self.bluetooth_status['initialized'] = True
                    
                elif pattern_name == 'advertising' and 'start' in line.lower():
                    self.bluetooth_status['advertising'] = True
                    
                elif pattern_name == 'connection':
                    self.bluetooth_status['connected'] = 'connect' in line.lower()
                    
                elif pattern_name == 'mode' and 'BLE mode:' in line:
                    mode_match = re.search(r'BLE mode:\s*(\d+)', line)
                    if mode_match:
                        self.bluetooth_status['mode'] = int(mode_match.group(1))
                        
                elif pattern_name == 'device_name':
                    name_match = re.search(r'name.*?([A-Za-z\s]+)', line)
                    if name_match:
                        self.bluetooth_status['device_name'] = name_match.group(1).strip()
                        
                elif pattern_name == 'error':
                    self.bluetooth_status['errors'].append(line.strip())
                
                return True
        return False
    
    def monitor(self, duration=30):
        """Monitor serial output for specified duration"""
        if not self.connect():
            return False
            
        print(f"🔍 Monitoring Bluetooth activity for {duration} seconds...")
        print("📋 Looking for: initialization, advertising, connections, errors")
        print("-" * 70)
        
        start_time = time.time()
        line_buffer = ""
        
        try:
            while time.time() - start_time < duration:
                if self.ser.in_waiting > 0:
                    chunk = self.ser.read(self.ser.in_waiting).decode('utf-8', errors='ignore')
                    line_buffer += chunk
                    
                    while '\n' in line_buffer:
                        line, line_buffer = line_buffer.split('\n', 1)
                        if line.strip():
                            if not self.parse_log_line(line):
                                # Show non-BLE lines if they contain interesting keywords
                                if any(word in line.lower() for word in ['wifi', 'init', 'ready', 'start']):
                                    timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
                                    print(f"[{timestamp}] ℹ️  SYSTEM: {line.strip()}")
                
                time.sleep(0.01)  # Small delay to prevent excessive CPU usage
                
        except KeyboardInterrupt:
            print("\n⏹️  Monitoring stopped by user")
        except Exception as e:
            print(f"\n❌ Monitoring error: {e}")
        finally:
            if self.ser:
                self.ser.close()
                
        return True
    
    def print_status_summary(self):
        """Print Bluetooth status summary"""
        print("\n" + "="*70)
        print("🔵 BLUETOOTH STATUS SUMMARY")
        print("="*70)
        
        status_items = [
            ("Initialized", "✅" if self.bluetooth_status['initialized'] else "❌"),
            ("Advertising", "✅" if self.bluetooth_status['advertising'] else "❌"),
            ("Connected", "✅" if self.bluetooth_status['connected'] else "❌"),
            ("Device Name", self.bluetooth_status['device_name'] or "Unknown"),
            ("BLE Mode", self.bluetooth_status['mode'] or "Unknown"),
            ("Errors", len(self.bluetooth_status['errors']))
        ]
        
        for item, value in status_items:
            print(f"{item:15}: {value}")
            
        if self.bluetooth_status['errors']:
            print("\n🚨 ERRORS DETECTED:")
            for error in self.bluetooth_status['errors'][-5:]:  # Show last 5 errors
                print(f"   • {error}")
                
        # Provide recommendations
        print("\n💡 RECOMMENDATIONS:")
        if not self.bluetooth_status['initialized']:
            print("   • Check BLE initialization in main.c")
            print("   • Verify CONF_BLE_MODE is set to 1 (enabled)")
        elif not self.bluetooth_status['advertising']:
            print("   • Check gap_event_handler advertising logic")
            print("   • Verify esp_ble_gap_start_advertising calls")
        elif self.bluetooth_status['advertising']:
            print("   • BLE appears to be working - try scanning with phone")
            print("   • Look for 'VESC Express' in BLE scanner apps")

def main():
    if len(sys.argv) > 1:
        port = sys.argv[1]
    else:
        port = '/dev/ttyACM0'
        
    monitor = BluetoothDebugMonitor(port)
    
    print("🔧 ESP32-C6 Bluetooth Debug Monitor")
    print(f"📱 Monitoring: {port}")
    print("⏱️  Duration: 30 seconds")
    print()
    
    if monitor.monitor(30):
        monitor.print_status_summary()
    else:
        print("❌ Failed to start monitoring")
        return 1
        
    return 0

if __name__ == "__main__":
    sys.exit(main())