#!/usr/bin/env python3
"""
WiFi Debug Client for ESP32-C6 VESC Express
Connects to the WiFi debugging interface and displays real-time logs
"""

import socket
import time
import threading
import json
import urllib.request

class VESCWiFiDebugClient:
    def __init__(self, host='192.168.5.107', tcp_port=23456, web_port=80):
        self.host = host
        self.tcp_port = tcp_port
        self.web_port = web_port
        self.tcp_sock = None
        self.running = False
        
    def test_connectivity(self):
        """Test basic connectivity to VESC Express"""
        print(f"🔍 Testing connectivity to {self.host}")
        
        # Test ping
        import subprocess
        try:
            result = subprocess.run(['ping', '-c', '1', self.host], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                print("✅ Ping: Success")
            else:
                print("❌ Ping: Failed")
        except:
            print("❌ Ping: Failed")
        
        # Test web dashboard
        try:
            response = urllib.request.urlopen(f'http://{self.host}:{self.web_port}', timeout=5)
            if response.status == 200:
                print("✅ Web Dashboard: Online")
            else:
                print(f"❌ Web Dashboard: HTTP {response.status}")
        except Exception as e:
            print(f"❌ Web Dashboard: {e}")
            
        # Test TCP debug port
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex((self.host, self.tcp_port))
            if result == 0:
                print("✅ TCP Debug Server: Online")
                sock.close()
            else:
                print("❌ TCP Debug Server: Not responding")
        except Exception as e:
            print(f"❌ TCP Debug Server: {e}")
    
    def get_system_status(self):
        """Get system status from web API"""
        try:
            response = urllib.request.urlopen(f'http://{self.host}:{self.web_port}/api/status', timeout=5)
            data = json.loads(response.read().decode())
            
            print("\n📊 System Status:")
            print(f"   Uptime: {data['uptime_ms']/1000:.1f}s")
            print(f"   Free Heap: {data['free_heap']/1024:.1f}KB")
            print(f"   Min Free Heap: {data['min_free_heap']/1024:.1f}KB")
            print(f"   Task Count: {data['task_count']}")
            print(f"   Debug Clients: {data['debug_clients_connected']}")
            print(f"   Debug Messages: {data['debug_messages_sent']}")
            
        except Exception as e:
            print(f"❌ Failed to get system status: {e}")
    
    def get_vesc_status(self):
        """Get VESC status from web API"""
        try:
            response = urllib.request.urlopen(f'http://{self.host}:{self.web_port}/api/vesc', timeout=5)
            data = json.loads(response.read().decode())
            
            print("\n🚗 VESC Status:")
            print(f"   CAN Connected: {'✅' if data['can_connected'] else '❌'}")
            print(f"   Last Command: {data['last_command']}")
            print(f"   Motor RPM: {data['motor_rpm']}")
            print(f"   Battery Voltage: {data['battery_voltage']}V")
            print(f"   Motor Current: {data['motor_current']}A")
            print(f"   Motor Temp: {data['motor_temp']}°C")
            
        except Exception as e:
            print(f"❌ Failed to get VESC status: {e}")
    
    def connect_tcp_debug(self):
        """Connect to TCP debug server"""
        try:
            self.tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.tcp_sock.settimeout(10)
            self.tcp_sock.connect((self.host, self.tcp_port))
            print(f"✅ Connected to TCP debug server at {self.host}:{self.tcp_port}")
            return True
        except Exception as e:
            print(f"❌ Failed to connect to TCP debug server: {e}")
            return False
    
    def tcp_receiver(self):
        """Receive and display TCP debug messages"""
        print("\n📡 Real-time debug logs:")
        print("-" * 60)
        
        while self.running:
            try:
                if self.tcp_sock:
                    self.tcp_sock.settimeout(1)
                    data = self.tcp_sock.recv(1024)
                    if data:
                        message = data.decode('utf-8', errors='ignore')
                        print(message, end='')
                    else:
                        print("🔌 TCP connection closed by server")
                        break
            except socket.timeout:
                continue
            except Exception as e:
                print(f"\n❌ TCP receive error: {e}")
                break
    
    def start_monitoring(self):
        """Start monitoring debug output"""
        print("🚀 Starting VESC Express WiFi Debug Monitor")
        print("=" * 60)
        
        self.test_connectivity()
        self.get_system_status()
        self.get_vesc_status()
        
        if self.connect_tcp_debug():
            self.running = True
            tcp_thread = threading.Thread(target=self.tcp_receiver)
            tcp_thread.daemon = True
            tcp_thread.start()
            
            try:
                while self.running:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n\n⏹️  Monitoring stopped by user")
                self.running = False
        
        if self.tcp_sock:
            self.tcp_sock.close()
    
    def send_test_commands(self):
        """Send test VESC commands via TCP to generate debug output"""
        print("\n🧪 Sending test commands to generate debug logs...")
        
        # This would connect to the VESC TCP port and send commands
        try:
            vesc_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            vesc_sock.settimeout(5)
            vesc_sock.connect((self.host, 65102))
            
            # Send VESC firmware version request
            cmd = bytes([0x02, 0x01, 0x00, 0x01, 0x03])
            vesc_sock.send(cmd)
            print("📤 Sent: Get Firmware Version")
            
            time.sleep(0.5)
            
            # Send VESC values request  
            cmd = bytes([0x02, 0x01, 0x04, 0x05, 0x03])
            vesc_sock.send(cmd)
            print("📤 Sent: Get Values")
            
            vesc_sock.close()
            print("✅ Test commands sent")
            
        except Exception as e:
            print(f"❌ Failed to send test commands: {e}")

def main():
    import sys
    
    print("🔧 ESP32-C6 VESC Express WiFi Debug Client")
    print("==========================================")
    
    if len(sys.argv) > 1:
        host = sys.argv[1]
    else:
        host = '192.168.5.107'
    
    client = VESCWiFiDebugClient(host)
    
    if len(sys.argv) > 2 and sys.argv[2] == 'test':
        # Just run connectivity tests
        client.test_connectivity()
        client.get_system_status() 
        client.get_vesc_status()
        client.send_test_commands()
    else:
        # Start full monitoring
        client.start_monitoring()

if __name__ == "__main__":
    main()