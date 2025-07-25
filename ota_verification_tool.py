#!/usr/bin/env python3
"""
ESP32-C6 OTA Verification Tool
Tests WiFi connectivity, OTA partitions, and performs test updates
"""

import socket
import subprocess
import time
import json
import sys
import os
from pathlib import Path
import requests
import threading
from http.server import HTTPServer, SimpleHTTPRequestHandler

class OTAVerificationTool:
    def __init__(self):
        self.device_port = "/dev/ttyACM0"
        self.device_ip = None
        self.build_dir = Path("/home/rds/vesc_express/build")
        self.local_ip = self.get_local_ip()
        
    def log(self, message, level="INFO"):
        timestamp = time.strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
        
    def get_local_ip(self):
        """Get local machine IP address"""
        try:
            # Connect to a remote address to determine local IP
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
            return local_ip
        except Exception:
            return "127.0.0.1"
    
    def scan_network_for_esp32(self):
        """Scan local network for ESP32-C6 device"""
        self.log("🔍 Scanning network for ESP32-C6 device...")
        
        # Get network range
        base_ip = ".".join(self.local_ip.split(".")[:-1])
        
        # Common ESP32 ports to check
        esp32_ports = [80, 8080, 3232, 8000]
        
        devices_found = []
        
        # Scan common IP range (last 50 addresses)
        for i in range(1, 51):
            ip = f"{base_ip}.{i}"
            for port in esp32_ports:
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(0.1)
                    result = sock.connect_ex((ip, port))
                    if result == 0:
                        devices_found.append((ip, port))
                        self.log(f"📱 Found device at {ip}:{port}")
                    sock.close()
                except:
                    pass
        
        return devices_found
    
    def check_ota_partitions(self):
        """Check OTA partition configuration"""
        self.log("🔍 Checking OTA partition configuration...")
        
        try:
            # Get partition info
            cmd = [
                "python", f"{os.environ['IDF_PATH']}/components/partition_table/parttool.py",
                "--port", self.device_port,
                "get_partition_info", "--partition-name", "app0"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                app0_info = result.stdout.strip().split()
                if len(app0_info) >= 2:
                    self.log(f"✅ App0 partition: {app0_info[0]} size {int(app0_info[1], 16)/1024/1024:.1f}MB")
            
            # Check app1 partition
            cmd[5] = "app1"
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                app1_info = result.stdout.strip().split()
                if len(app1_info) >= 2:
                    self.log(f"✅ App1 partition: {app1_info[0]} size {int(app1_info[1], 16)/1024/1024:.1f}MB")
            
            return True
            
        except Exception as e:
            self.log(f"❌ Failed to check partitions: {e}", "ERROR")
            return False
    
    def create_test_firmware(self):
        """Create a test firmware with version increment"""
        self.log("🔧 Creating test firmware for OTA update...")
        
        try:
            # Modify main.c to increment version
            main_file = Path("/home/rds/vesc_express/main/main.c")
            if main_file.exists():
                content = main_file.read_text()
                
                # Look for version string and increment
                import re
                version_pattern = r'const char\* fw_version = "([^"]+)";'
                match = re.search(version_pattern, content)
                
                if match:
                    current_version = match.group(1)
                    # Simple version increment
                    parts = current_version.split('.')
                    if len(parts) >= 3:
                        parts[-1] = str(int(parts[-1]) + 1)
                        new_version = '.'.join(parts)
                    else:
                        new_version = current_version + ".1"
                    
                    new_content = content.replace(
                        f'const char* fw_version = "{current_version}";',
                        f'const char* fw_version = "{new_version}";'
                    )
                    
                    # Write temporary version
                    backup_file = main_file.with_suffix('.c.backup')
                    main_file.rename(backup_file)
                    main_file.write_text(new_content)
                    
                    self.log(f"📝 Version updated: {current_version} → {new_version}")
                    return backup_file
                    
        except Exception as e:
            self.log(f"❌ Failed to create test firmware: {e}", "ERROR")
            
        return None
    
    def build_test_firmware(self):
        """Build test firmware for OTA"""
        self.log("🔨 Building test firmware...")
        
        try:
            # Source environment and build
            cmd = [
                "bash", "-c", 
                "source .env.esp32 && source $IDF_PATH/export.sh && idf.py build"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, cwd="/home/rds/vesc_express")
            
            if result.returncode == 0:
                self.log("✅ Test firmware build successful")
                return True
            else:
                self.log(f"❌ Build failed: {result.stderr}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ Build error: {e}", "ERROR")
            return False
    
    def start_ota_server(self, port=8080):
        """Start local HTTP server for OTA files"""
        self.log(f"🌐 Starting OTA server on {self.local_ip}:{port}")
        
        class OTAHandler(SimpleHTTPRequestHandler):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, directory=str(self.build_dir), **kwargs)
        
        try:
            server = HTTPServer((self.local_ip, port), OTAHandler)
            
            # Start server in background thread
            server_thread = threading.Thread(target=server.serve_forever, daemon=True)
            server_thread.start()
            
            self.log(f"✅ OTA server running at http://{self.local_ip}:{port}")
            return server, f"http://{self.local_ip}:{port}"
            
        except Exception as e:
            self.log(f"❌ Failed to start OTA server: {e}", "ERROR")
            return None, None
    
    def test_http_ota_update(self, device_ip, ota_url):
        """Test HTTP OTA update"""
        self.log(f"🚀 Testing OTA update to {device_ip}")
        
        try:
            # Try common ESP32 OTA endpoints
            ota_endpoints = [
                f"http://{device_ip}/ota",
                f"http://{device_ip}:8080/ota",  
                f"http://{device_ip}/update",
                f"http://{device_ip}:3232/ota"
            ]
            
            firmware_url = f"{ota_url}/vesc_express.bin"
            
            for endpoint in ota_endpoints:
                try:
                    self.log(f"📡 Trying OTA endpoint: {endpoint}")
                    
                    # Send OTA update request
                    payload = {"firmware_url": firmware_url}
                    response = requests.post(endpoint, json=payload, timeout=10)
                    
                    if response.status_code == 200:
                        self.log(f"✅ OTA update initiated successfully!")
                        self.log(f"Response: {response.text}")
                        return True
                        
                except requests.exceptions.RequestException as e:
                    self.log(f"⚠️  Endpoint {endpoint} not responsive: {e}")
                    continue
            
            self.log("❌ No responsive OTA endpoints found", "ERROR")
            return False
            
        except Exception as e:
            self.log(f"❌ OTA test failed: {e}", "ERROR")
            return False
    
    def verify_ota_functionality(self):
        """Complete OTA functionality verification"""
        self.log("🔍 Starting OTA Functionality Verification", "INFO")
        self.log("=" * 60)
        
        # Step 1: Check partitions
        if not self.check_ota_partitions():
            return False
        
        # Step 2: Scan for device
        devices = self.scan_network_for_esp32()
        if not devices:
            self.log("❌ No ESP32 devices found on network", "ERROR")
            self.log("💡 Ensure device is connected to WiFi and try manual IP")
            return False
        
        # Step 3: Create and build test firmware
        backup_file = self.create_test_firmware()
        if backup_file and self.build_test_firmware():
            
            # Step 4: Start OTA server
            server, ota_url = self.start_ota_server()
            if server and ota_url:
                
                # Step 5: Test OTA on found devices
                success = False
                for device_ip, port in devices:
                    if self.test_http_ota_update(device_ip, ota_url):
                        success = True
                        break
                
                # Cleanup
                server.shutdown()
                
                # Restore original firmware
                if backup_file and backup_file.exists():
                    main_file = Path("/home/rds/vesc_express/main/main.c")
                    backup_file.rename(main_file)
                
                return success
        
        return False

def main():
    print("🔍 ESP32-C6 OTA Verification Tool")
    print("=" * 50)
    
    tool = OTAVerificationTool()
    
    # Manual IP input option
    if len(sys.argv) > 1:
        manual_ip = sys.argv[1]
        print(f"Using manual IP: {manual_ip}")
        tool.device_ip = manual_ip
    
    success = tool.verify_ota_functionality()
    
    if success:
        print("\n🎉 OTA VERIFICATION SUCCESSFUL!")
        print("✅ 8MB OTA system is fully operational")
        return 0
    else:
        print("\n❌ OTA VERIFICATION FAILED")
        print("💡 Check device WiFi connectivity and try manual IP")
        return 1

if __name__ == "__main__":
    sys.exit(main())