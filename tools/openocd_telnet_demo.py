#!/usr/bin/env python3
"""
OpenOCD Telnet Interface Demo
Implementation of research document recommendations for advanced OpenOCD usage
"""

import telnetlib
import time
import subprocess
import threading
import sys
import os
from pathlib import Path

class OpenOCDTelnetDemo:
    """
    Advanced OpenOCD telnet interface for ESP32-C6 debugging
    Based on ESP-IDF research document recommendations
    """
    
    def __init__(self, host='localhost', port=4444):
        self.host = host
        self.port = port
        self.telnet = None
        self.openocd_process = None
        
    def start_openocd(self, config_file="tools/esp32c6_final.cfg"):
        """Start OpenOCD server with ESP32-C6 configuration"""
        try:
            print(f"🚀 Starting OpenOCD with config: {config_file}")
            self.openocd_process = subprocess.Popen(
                ['openocd', '-f', config_file],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Give OpenOCD time to start
            time.sleep(3)
            
            if self.openocd_process.poll() is None:
                print("✅ OpenOCD started successfully")
                return True
            else:
                print("❌ OpenOCD failed to start")
                return False
                
        except Exception as e:
            print(f"❌ Error starting OpenOCD: {e}")
            return False
    
    def connect_telnet(self):
        """Connect to OpenOCD telnet interface"""
        try:
            print(f"🔗 Connecting to OpenOCD telnet at {self.host}:{self.port}")
            self.telnet = telnetlib.Telnet(self.host, self.port, timeout=10)
            
            # Wait for OpenOCD prompt
            response = self.telnet.read_until(b"> ", timeout=5)
            print("✅ Connected to OpenOCD telnet interface")
            return True
            
        except Exception as e:
            print(f"❌ Failed to connect to telnet: {e}")
            return False
    
    def send_command(self, command):
        """Send command to OpenOCD and return response"""
        if not self.telnet:
            print("❌ Not connected to telnet")
            return None
            
        try:
            print(f"📤 Sending command: {command}")
            self.telnet.write(f"{command}\n".encode())
            
            # Read response until prompt
            response = self.telnet.read_until(b"> ", timeout=10)
            response_str = response.decode('utf-8', errors='ignore').strip()
            
            # Remove the command echo and prompt
            lines = response_str.split('\n')
            if len(lines) > 1:
                response_str = '\n'.join(lines[1:-1])  # Remove first (command) and last (prompt) lines
            
            print(f"📥 Response: {response_str}")
            return response_str
            
        except Exception as e:
            print(f"❌ Error sending command: {e}")
            return None
    
    def demonstrate_target_control(self):
        """Demonstrate target control commands from research document"""
        print("\n🎯 === TARGET CONTROL DEMONSTRATION ===")
        print("Based on ESP-IDF OpenOCD research document")
        
        commands = [
            ("halt", "Halt the CPU"),
            ("reg", "Display all core registers"), 
            ("reset halt", "Reset target and leave CPU halted"),
            ("resume", "Resume execution"),
            ("halt", "Halt CPU again for next demos")
        ]
        
        for cmd, description in commands:
            print(f"\n🔸 {description}")
            response = self.send_command(cmd)
            if response:
                # Truncate long responses for readability
                if len(response) > 200:
                    print(f"   (Response truncated: {len(response)} characters)")
                time.sleep(1)  # Brief pause between commands
    
    def demonstrate_memory_access(self):
        """Demonstrate memory access commands from research document"""
        print("\n🧠 === MEMORY ACCESS DEMONSTRATION ===")
        
        # ESP32-C6 memory addresses
        memory_demos = [
            ("mdw 0x40000000 4", "Read 4 words from IROM base"),
            ("mdw 0x600fe000 4", "Read 4 words from RTC memory"), 
            ("mdw 0x40800000 4", "Read 4 words from DROM base"),
            ("mdb 0x40000000 16", "Read 16 bytes from IROM (byte access)")
        ]
        
        for cmd, description in memory_demos:
            print(f"\n🔸 {description}")
            response = self.send_command(cmd)
            time.sleep(0.5)
    
    def demonstrate_flash_operations(self):
        """Demonstrate flash operations from research document"""
        print("\n💾 === FLASH OPERATIONS DEMONSTRATION ===")
        
        flash_commands = [
            ("flash probe 0", "Probe and identify flash chip"),
            ("flash banks", "List flash banks"),
            ("flash info 0", "Display flash chip information")
        ]
        
        for cmd, description in flash_commands:
            print(f"\n🔸 {description}")
            response = self.send_command(cmd)
            time.sleep(0.5)
    
    def demonstrate_advanced_scripting(self):
        """Demonstrate advanced OpenOCD scripting capabilities"""
        print("\n🔧 === ADVANCED SCRIPTING DEMONSTRATION ===")
        
        # Multi-command script example
        script_commands = [
            "echo 'Starting advanced demo...'",
            "reset halt",
            "echo 'Target reset and halted'", 
            "reg pc",
            "echo 'Program counter displayed'",
            "resume",
            "echo 'Target resumed'",
            "sleep 100",
            "halt", 
            "echo 'Advanced demo complete'"
        ]
        
        print("🔸 Executing multi-command script")
        for cmd in script_commands:
            response = self.send_command(cmd)
            time.sleep(0.3)
    
    def run_complete_demo(self):
        """Run complete OpenOCD telnet demonstration"""
        print("🎯 ESP32-C6 OpenOCD Telnet Interface Demo")
        print("=========================================")
        print("Based on ESP-IDF OpenOCD research document")
        print()
        
        # Start OpenOCD if not already running
        if not self.connect_telnet():
            if self.start_openocd():
                time.sleep(2)
                if not self.connect_telnet():
                    print("❌ Failed to establish telnet connection")
                    return False
            else:
                print("❌ Failed to start OpenOCD")
                return False
        
        try:
            # Run demonstrations
            self.demonstrate_target_control()
            self.demonstrate_memory_access()
            self.demonstrate_flash_operations()
            self.demonstrate_advanced_scripting()
            
            print("\n🎉 OpenOCD telnet demonstration complete!")
            print("📚 All commands based on ESP-IDF research document")
            return True
            
        except Exception as e:
            print(f"❌ Demo error: {e}")
            return False
        
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Clean up connections and processes"""
        if self.telnet:
            try:
                self.telnet.close()
                print("🔌 Telnet connection closed")
            except:
                pass
        
        if self.openocd_process and self.openocd_process.poll() is None:
            try:
                self.openocd_process.terminate()
                self.openocd_process.wait(timeout=5)
                print("🛑 OpenOCD process stopped")
            except:
                self.openocd_process.kill()

def main():
    """Main demo function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='OpenOCD Telnet Interface Demo')
    parser.add_argument('--host', default='localhost', help='OpenOCD host')
    parser.add_argument('--port', type=int, default=4444, help='OpenOCD telnet port')
    parser.add_argument('--config', default='tools/esp32c6_final.cfg', help='OpenOCD config file')
    parser.add_argument('--connect-only', action='store_true', help='Connect to existing OpenOCD instance')
    
    args = parser.parse_args()
    
    demo = OpenOCDTelnetDemo(args.host, args.port)
    
    if args.connect_only:
        print("🔗 Connecting to existing OpenOCD instance...")
        if demo.connect_telnet():
            demo.demonstrate_target_control()
            demo.demonstrate_memory_access()
            demo.demonstrate_flash_operations()
            demo.cleanup()
        else:
            print("❌ Failed to connect to existing OpenOCD instance")
            print("💡 Start OpenOCD manually: openocd -f tools/esp32c6_final.cfg")
    else:
        demo.run_complete_demo()

if __name__ == "__main__":
    main()