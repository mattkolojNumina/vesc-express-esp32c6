#!/usr/bin/env python3
"""
TCP Debug Server Connectivity Test for ESP32-C6 VESC Express
Tests the TCP debug server accessibility and functionality
"""

import socket
import threading
import time
import sys
import subprocess
import select

class TCPDebugTester:
    def __init__(self, host="192.168.5.107", ports=[23456, 23457, 23458]):
        self.host = host
        self.ports = ports
        self.connected_socket = None
        self.receive_thread = None
        self.running = False
        
    def test_network_connectivity(self):
        """Test basic network connectivity to the device"""
        print(f"=== Testing Network Connectivity to {self.host} ===")
        
        try:
            # Ping test
            result = subprocess.run(['ping', '-c', '3', '-W', '2', self.host], 
                                   capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                print("✅ PING successful - device is reachable")
                # Extract ping time
                for line in result.stdout.split('\n'):
                    if 'time=' in line:
                        time_part = line.split('time=')[1].split()[0]
                        print(f"   Ping time: {time_part}")
                        break
                return True
            else:
                print("❌ PING failed - device not reachable")
                print(f"Error: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Network test failed: {e}")
            return False
    
    def test_port_accessibility(self):
        """Test TCP port accessibility"""
        print(f"\n=== Testing TCP Port Accessibility ===")
        
        accessible_ports = []
        
        for port in self.ports:
            print(f"Testing port {port}...")
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5.0)  # 5 second timeout
            
            try:
                result = sock.connect_ex((self.host, port))
                if result == 0:
                    print(f"✅ Port {port}: ACCESSIBLE")
                    accessible_ports.append(port)
                    sock.close()
                else:
                    print(f"❌ Port {port}: CONNECTION REFUSED (error {result})")
                    
            except socket.timeout:
                print(f"❌ Port {port}: TIMEOUT")
            except Exception as e:
                print(f"❌ Port {port}: ERROR - {e}")
            finally:
                try:
                    sock.close()
                except:
                    pass
                    
        return accessible_ports
    
    def test_tcp_connection(self, port):
        """Test full TCP connection and communication"""
        print(f"\n=== Testing TCP Debug Connection on Port {port} ===")
        
        try:
            # Create socket with extended timeout
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(10.0)
            
            print(f"Connecting to {self.host}:{port}...")
            sock.connect((self.host, port))
            print("✅ TCP connection established")
            
            # Make socket non-blocking for receive operations
            sock.setblocking(False)
            
            # Wait for welcome message
            print("Waiting for welcome message...")
            start_time = time.time()
            welcome_received = False
            
            while time.time() - start_time < 5.0:
                try:
                    data = sock.recv(1024)
                    if data:
                        message = data.decode('utf-8', errors='ignore')
                        print(f"✅ Received welcome message:")
                        for line in message.split('\n'):
                            if line.strip():
                                print(f"   > {line.strip()}")
                        welcome_received = True
                        break
                except socket.error:
                    time.sleep(0.1)
                    continue
            
            if not welcome_received:
                print("⚠️  No welcome message received (but connection successful)")
            
            # Test sending a command
            print("\nTesting command sending...")
            test_command = "test\r\n"
            sock.send(test_command.encode('utf-8'))
            print(f"Sent test command: {repr(test_command)}")
            
            # Wait for response
            time.sleep(1.0)
            try:
                response = sock.recv(1024)
                if response:
                    print(f"✅ Received response: {repr(response.decode('utf-8', errors='ignore'))}")
                else:
                    print("ℹ️  No response to test command (normal for debug server)")
            except socket.error:
                print("ℹ️  No immediate response (normal for debug server)")
            
            # Keep connection alive for a few seconds to test stability
            print("\nTesting connection stability...")
            for i in range(3):
                time.sleep(1)
                try:
                    # Send keepalive
                    sock.send(b'\r\n')
                    print(f"   Keepalive {i+1}/3 sent")
                except Exception as e:
                    print(f"   Keepalive {i+1}/3 failed: {e}")
                    break
            
            sock.close()
            print("✅ TCP debug connection test SUCCESSFUL")
            return True
            
        except socket.timeout:
            print("❌ Connection timeout - server not responding")
            return False
        except ConnectionRefusedError:
            print("❌ Connection refused - server not listening")
            return False
        except Exception as e:
            print(f"❌ Connection test failed: {e}")
            return False
    
    def interactive_session(self, port):
        """Start an interactive debug session"""
        print(f"\n=== Interactive Debug Session on Port {port} ===")
        print("Commands: 'quit' to exit, 'help' for help")
        print("-" * 50)
        
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((self.host, port))
            self.connected_socket = sock
            self.running = True
            
            # Start receive thread
            self.receive_thread = threading.Thread(target=self._receive_handler)
            self.receive_thread.daemon = True
            self.receive_thread.start()
            
            print(f"Connected to {self.host}:{port}")
            print("Type messages and press Enter. Type 'quit' to exit.")
            
            while self.running:
                try:
                    user_input = input("> ")
                    if user_input.lower() in ['quit', 'exit']:
                        break
                    
                    # Send command
                    message = user_input + '\r\n'
                    sock.send(message.encode('utf-8'))
                    
                except KeyboardInterrupt:
                    break
                except Exception as e:
                    print(f"Send error: {e}")
                    break
            
            self.running = False
            sock.close()
            print("\nSession ended.")
            
        except Exception as e:
            print(f"Interactive session failed: {e}")
    
    def _receive_handler(self):
        """Handle incoming messages"""
        sock = self.connected_socket
        sock.settimeout(1.0)
        
        while self.running:
            try:
                data = sock.recv(1024)
                if data:
                    message = data.decode('utf-8', errors='ignore')
                    # Print received data with timestamp
                    timestamp = time.strftime("%H:%M:%S")
                    for line in message.split('\n'):
                        if line.strip():
                            print(f"[{timestamp}] {line.strip()}")
                else:
                    # Connection closed
                    break
            except socket.timeout:
                continue
            except Exception as e:
                if self.running:
                    print(f"Receive error: {e}")
                break

def main():
    print("ESP32-C6 VESC Express TCP Debug Server Connectivity Test")
    print("=" * 60)
    
    if len(sys.argv) > 1:
        host = sys.argv[1]
    else:
        host = "192.168.5.107"
    
    tester = TCPDebugTester(host)
    
    # Test network connectivity
    if not tester.test_network_connectivity():
        print("❌ Basic network connectivity failed. Check device connection.")
        return 1
    
    # Test port accessibility
    accessible_ports = tester.test_port_accessibility()
    
    if not accessible_ports:
        print("\n❌ CRITICAL: No TCP debug ports are accessible!")
        print("Possible issues:")
        print("  - TCP debug server not started")
        print("  - Network interface not up")
        print("  - Socket binding failed")
        print("  - Firewall blocking connections")
        return 1
    
    # Test full connection on first accessible port
    working_port = accessible_ports[0]
    if tester.test_tcp_connection(working_port):
        print(f"\n🎉 SUCCESS: TCP debug server is working on port {working_port}")
        
        # Ask if user wants interactive session
        try:
            choice = input(f"\nStart interactive debug session on port {working_port}? (y/n): ")
            if choice.lower() == 'y':
                tester.interactive_session(working_port)
        except KeyboardInterrupt:
            pass
        
        return 0
    else:
        print(f"\n❌ FAILURE: TCP debug server not responding properly")
        return 1

if __name__ == "__main__":
    sys.exit(main())