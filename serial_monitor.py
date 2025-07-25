#!/usr/bin/env python3
"""
Simple serial monitor to check ESP32-C6 boot messages and WiFi status
"""

import serial
import time
import sys
import re

def monitor_serial(port="/dev/ttyACM0", baudrate=115200, duration=30):
    """Monitor serial output for boot messages and WiFi info"""
    print(f"🔍 Monitoring ESP32-C6 serial output on {port}")
    print("=" * 50)
    
    try:
        ser = serial.Serial(port, baudrate, timeout=1)
        
        print("📡 Waiting for device messages...")
        start_time = time.time()
        wifi_connected = False
        device_ip = None
        
        while time.time() - start_time < duration:
            if ser.in_waiting:
                try:
                    line = ser.readline().decode('utf-8', errors='ignore').strip()
                    if line:
                        print(f"📟 {line}")
                        
                        # Look for WiFi connection indicators
                        if "WiFi connected" in line or "WIFI_EVENT_STA_GOT_IP" in line:
                            wifi_connected = True
                            print("✅ WiFi connection detected!")
                        
                        # Look for IP address
                        ip_match = re.search(r'IP:\s*(\d+\.\d+\.\d+\.\d+)', line)
                        if ip_match:
                            device_ip = ip_match.group(1)
                            print(f"🌐 Device IP found: {device_ip}")
                        
                        # Look for OTA indicators
                        if "OTA" in line:
                            print(f"🔄 OTA message: {line}")
                            
                except UnicodeDecodeError:
                    pass
            
            time.sleep(0.1)
        
        ser.close()
        
        print("\n" + "=" * 50)
        if wifi_connected and device_ip:
            print(f"✅ Device connected to WiFi at IP: {device_ip}")
            return device_ip
        elif wifi_connected:
            print("⚠️  WiFi connected but IP not captured")
            return "connected"
        else:
            print("❌ No WiFi connection detected")
            return None
            
    except serial.SerialException as e:
        print(f"❌ Serial connection failed: {e}")
        return None
    except KeyboardInterrupt:
        print("\n👋 Monitoring stopped by user")
        return None

if __name__ == "__main__":
    duration = 60 if len(sys.argv) < 2 else int(sys.argv[1])
    result = monitor_serial(duration=duration)
    if result and result != "connected":
        print(f"\n💡 Use this IP for OTA testing: {result}")