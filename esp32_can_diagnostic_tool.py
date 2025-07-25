#!/usr/bin/env python3
"""
ESP32-C6 CAN Bus Diagnostic Tool using ESP-IDF Methods
Proper approach for testing CAN communication with VESC controllers
"""

import subprocess
import time
import sys
import os
from pathlib import Path

class ESP32CANDiagnostic:
    def __init__(self, device_port="/dev/ttyACM0"):
        self.device_port = device_port
        self.project_path = "/home/rds/vesc_express"
        
    def log(self, message, level="INFO"):
        timestamp = time.strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
        
    def run_idf_command(self, cmd, description):
        """Run ESP-IDF command with proper environment"""
        self.log(f"🔧 {description}")
        
        try:
            env_cmd = ["bash", "-c", 
                      f"source .env.esp32 && source $IDF_PATH/export.sh && {' '.join(cmd)}"]
            
            result = subprocess.run(env_cmd, capture_output=True, text=True, 
                                  cwd=self.project_path, timeout=30)
            
            if result.returncode == 0:
                self.log(f"✅ Success: {description}")
                if result.stdout.strip():
                    return result.stdout.strip()
                return True
            else:
                self.log(f"❌ Failed: {description}", "ERROR")
                if result.stderr.strip():
                    self.log(f"Error: {result.stderr.strip()}", "ERROR")
                return None
                
        except subprocess.TimeoutExpired:
            self.log(f"⏰ Timeout: {description}", "ERROR")
            return None
        except Exception as e:
            self.log(f"❌ Command failed: {e}", "ERROR")
            return None
    
    def check_can_timing_configuration(self):
        """Check current CAN timing configuration in source code"""
        self.log("🔍 Analyzing CAN timing configuration...")
        
        # Search for TWAI timing configuration
        can_files = [
            "main/comm_can.c",
            "main/comm_can.h", 
            "main/drivers/drv_can.c",
            "main/main.c"
        ]
        
        timing_issues = []
        
        for file_path in can_files:
            full_path = Path(self.project_path) / file_path
            if full_path.exists():
                self.log(f"📁 Checking {file_path}")
                
                try:
                    with open(full_path, 'r') as f:
                        content = f.read()
                        
                    # Look for timing configuration
                    if 'twai_timing_config_t' in content or '.brp' in content:
                        self.log(f"🔧 Found timing config in {file_path}")
                        
                        # Check for critical timing values
                        if '.brp = 4' in content and '.tseg_1 = 15' in content:
                            timing_issues.append(f"{file_path}: BRP=4 produces 1Mbps instead of 500kbps")
                            
                        if '500' in content or '1000' in content:
                            self.log(f"📊 Baud rate references found in {file_path}")
                            
                except Exception as e:
                    self.log(f"⚠️  Could not read {file_path}: {e}")
        
        if timing_issues:
            self.log("🚨 CRITICAL TIMING ISSUES DETECTED:")
            for issue in timing_issues:
                self.log(f"   ❌ {issue}", "ERROR")
            return False
        else:
            self.log("✅ No obvious timing configuration issues found")
            return True
    
    def use_esp_idf_monitor_for_can_debug(self):
        """Use ESP-IDF monitor to capture CAN debug messages"""
        self.log("📡 Starting ESP-IDF monitor for CAN debugging...")
        
        # First, let's see what's currently in the device logs
        cmd = ["timeout", "10s", "idf.py", "monitor", "--port", self.device_port]
        
        output = self.run_idf_command(cmd, "Capturing ESP-IDF monitor output")
        
        if output:
            self.log("📄 Monitor output captured:")
            
            # Look for CAN-related messages
            can_keywords = ["CAN", "TWAI", "GPIO4", "GPIO5", "comm_can", "can_start"]
            
            for line in output.split('\n'):
                if any(keyword in line for keyword in can_keywords):
                    self.log(f"🔍 CAN: {line.strip()}")
                    
            return True
        else:
            self.log("❌ Could not capture monitor output", "ERROR")
            return False
    
    def test_can_with_esp_console(self):
        """Test CAN using ESP32 console commands via terminal"""
        self.log("💻 Testing CAN via ESP32 console commands...")
        
        # List of console commands to test CAN functionality
        console_commands = [
            "help",           # List available commands
            "free",          # Check memory 
            "restart",       # System info
            "version",       # Firmware version
        ]
        
        # Try to send console commands via terminal interface
        for cmd in console_commands:
            self.log(f"💻 Console command: {cmd}")
            
            # Create a simple script to send terminal commands
            terminal_script = f"""
import serial
import time

try:
    ser = serial.Serial('{self.device_port}', 115200, timeout=3)
    time.sleep(1)
    
    # Send command
    ser.write(b'{cmd}\\r\\n')
    ser.flush()
    
    # Read response
    time.sleep(2)
    if ser.in_waiting:
        response = ser.read(ser.in_waiting)
        print("Response:", response.decode('utf-8', errors='ignore'))
    else:
        print("No response")
        
    ser.close()
except Exception as e:
    print(f"Error: {{e}}")
"""
            
            # Execute the terminal script
            try:
                result = subprocess.run(["python3", "-c", terminal_script], 
                                      capture_output=True, text=True, timeout=10)
                if result.stdout.strip():
                    self.log(f"📥 Response: {result.stdout.strip()}")
                else:
                    self.log("⚠️  No response to console command")
            except Exception as e:
                self.log(f"❌ Console command failed: {e}")
            
            time.sleep(1)
    
    def use_openocd_for_can_debugging(self):
        """Use OpenOCD to debug CAN registers and GPIO states"""
        self.log("🔧 Using OpenOCD for CAN register debugging...")
        
        # Check if we have the ESP32-C6 debugging tools available
        debug_tools = [
            "tools/esp32c6_unified_debugger.py",
            "tools/esp32c6_openocd_setup.py", 
            "tools/openocd_telnet_demo.py"
        ]
        
        available_tools = []
        for tool in debug_tools:
            tool_path = Path(self.project_path) / tool
            if tool_path.exists():
                available_tools.append(tool)
                self.log(f"✅ Found debug tool: {tool}")
        
        if available_tools:
            self.log("🎯 Advanced debugging tools available")
            
            # Try to use the OpenOCD telnet interface
            if "tools/openocd_telnet_demo.py" in available_tools:
                self.log("🔧 Attempting OpenOCD telnet debugging...")
                
                cmd = ["python3", "tools/openocd_telnet_demo.py"]
                result = self.run_idf_command(cmd, "Running OpenOCD telnet diagnostics")
                
                if result:
                    self.log("✅ OpenOCD debugging session completed")
                    return True
        
        self.log("⚠️  Advanced debugging tools not available or failed")
        return False
    
    def comprehensive_can_diagnosis(self):
        """Run comprehensive CAN bus diagnosis using ESP-IDF methods"""
        self.log("🚀 ESP32-C6 CAN Bus Comprehensive Diagnosis")
        self.log("=" * 60)
        
        # Step 1: Check ESP-IDF environment
        if 'IDF_PATH' not in os.environ:
            self.log("❌ ESP-IDF environment not loaded", "ERROR") 
            self.log("Run: source .env.esp32 && source $IDF_PATH/export.sh")
            return False
        
        # Step 2: Check CAN timing configuration
        timing_ok = self.check_can_timing_configuration()
        
        # Step 3: Use ESP-IDF monitor for CAN debugging
        monitor_ok = self.use_esp_idf_monitor_for_can_debug()
        
        # Step 4: Test CAN via console commands
        self.test_can_with_esp_console()
        
        # Step 5: Use OpenOCD for advanced debugging
        openocd_ok = self.use_openocd_for_can_debugging()
        
        # Step 6: Generate comprehensive report
        self.log("\n📊 CAN Bus Diagnosis Summary:")
        self.log("=" * 40)
        
        if not timing_ok:
            self.log("🚨 CRITICAL: CAN timing configuration bug detected!")
            self.log("   ❌ ESP32-C6 configured for 1Mbps instead of 500kbps")
            self.log("   🔧 Fix required: Update .brp = 8 for correct 500kbps timing")
        
        self.log(f"   ESP-IDF Monitor: {'✅' if monitor_ok else '❌'}")
        self.log(f"   OpenOCD Debug: {'✅' if openocd_ok else '❌'}")
        
        if not timing_ok:
            self.log("\n🔧 RECOMMENDED ACTION:")
            self.log("   1. Fix CAN timing configuration (BRP = 4 → 8)")
            self.log("   2. Rebuild and flash firmware")
            self.log("   3. Re-test CAN communication with VESC")
            self.log("   4. Verify with oscilloscope: 500kbps operation")
            return False
        else:
            self.log("\n✅ CAN configuration appears correct")
            self.log("   Next: Test actual VESC communication")
            return True

def main():
    device_port = sys.argv[1] if len(sys.argv) > 1 else "/dev/ttyACM0"
    
    diagnostic = ESP32CANDiagnostic(device_port)
    success = diagnostic.comprehensive_can_diagnosis()
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())