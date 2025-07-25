#!/usr/bin/env python3
"""
WSL2 ESP32-C6 Debugging Setup Tool
Automates WSL2-specific configuration for ESP32-C6 debugging
"""

import os
import sys
import json
import subprocess
import platform
import time
from pathlib import Path
import argparse

class WSL2ESP32DebugSetup:
    """
    WSL2 ESP32-C6 Debugging Environment Setup Tool
    
    Configures WSL2 for ESP32 debugging including:
    - USB device passthrough with usbipd-win
    - Device permissions and udev rules setup
    - ESP32-C6 device detection and attachment
    - WSL2-specific debugging scripts and utilities
    """
    def __init__(self):
        self.is_wsl = self.detect_wsl()
        self.usbipd_installed = False
        self.esp32_devices = []

    def detect_wsl(self):
        """Detect if running in WSL2"""
        try:
            with open('/proc/version', 'r') as f:
                version = f.read().lower()
                if 'microsoft' in version and 'wsl' in version:
                    return True
        except (FileNotFoundError, OSError, PermissionError):
            # Not in WSL or can't read proc files
            pass
        
        return False

    def check_usbipd_windows(self):
        """Check if usbipd-win is installed on Windows host"""
        print("🔍 Checking for usbipd-win on Windows host...")
        
        try:
            # Try to run usbipd from WSL (it should be accessible if installed)
            result = subprocess.run(['usbipd.exe', '--version'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ usbipd-win is installed")
                self.usbipd_installed = True
                return True
        except FileNotFoundError:
            pass
        
        print("❌ usbipd-win not found")
        self.show_usbipd_install_instructions()
        return False

    def show_usbipd_install_instructions(self):
        """Show instructions for installing usbipd-win"""
        print("\n📋 usbipd-win Installation Instructions:")
        print("=" * 50)
        print("1. Open PowerShell as Administrator on Windows")
        print("2. Run: winget install --interactive --exact dorssel.usbipd-win")
        print("3. Restart your computer")
        print("4. Re-run this script\n")

    def list_usb_devices(self):
        """List USB devices via usbipd"""
        if not self.usbipd_installed:
            return []
        
        try:
            result = subprocess.run(['usbipd.exe', 'list'], 
                                  capture_output=True, text=True)
            
            devices = []
            esp32_devices = []
            
            for line in result.stdout.split('\n')[1:]:  # Skip header
                if line.strip():
                    parts = line.split()
                    if len(parts) >= 2:
                        busid = parts[0]
                        vid_pid = parts[1]
                        description = ' '.join(parts[2:])
                        
                        device = {
                            'busid': busid,
                            'vid_pid': vid_pid,
                            'description': description
                        }
                        
                        devices.append(device)
                        
                        # Check for ESP32-C6
                        if '303a:1001' in vid_pid:
                            esp32_devices.append(device)
                            print(f"🎯 Found ESP32-C6: {busid} - {description}")
            
            self.esp32_devices = esp32_devices
            return devices
            
        except Exception as e:
            print(f"❌ Failed to list USB devices: {e}")
            return []

    def bind_esp32_device(self, busid):
        """Bind ESP32 device for WSL2 sharing"""
        print(f"🔗 Binding ESP32 device {busid}...")
        
        try:
            # Bind command
            result = subprocess.run(['usbipd.exe', 'bind', '-b', busid], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"✅ Device {busid} bound successfully")
                return True
            else:
                print(f"❌ Failed to bind device {busid}")
                print(f"Error: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Bind operation failed: {e}")
            return False

    def attach_esp32_device(self, busid, auto_attach=True):
        """Attach ESP32 device to WSL2"""
        print(f"📎 Attaching ESP32 device {busid} to WSL2...")
        
        try:
            cmd = ['usbipd.exe', 'attach', '--wsl', '--busid', busid]
            if auto_attach:
                cmd.extend(['--auto-attach'])
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"✅ Device {busid} attached to WSL2")
                return True
            else:
                print(f"❌ Failed to attach device {busid}")
                print(f"Error: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Attach operation failed: {e}")
            return False

    def verify_wsl_device_access(self):
        """Verify ESP32 device is accessible in WSL2"""
        print("🔍 Verifying device access in WSL2...")
        
        # Check for ttyACM devices
        tty_devices = []
        for device in ['/dev/ttyACM0', '/dev/ttyACM1', '/dev/ttyUSB0', '/dev/ttyUSB1']:
            if os.path.exists(device):
                tty_devices.append(device)
                print(f"✅ Found device: {device}")
        
        if not tty_devices:
            print("❌ No ESP32 devices found in WSL2")
            return False
        
        # Check permissions
        for device in tty_devices:
            try:
                stat = os.stat(device)
                mode = stat.st_mode
                print(f"📋 {device} permissions: {oct(mode)[-3:]}")
                
                # Check if user can access
                if os.access(device, os.R_OK | os.W_OK):
                    print(f"✅ {device} is accessible")
                else:
                    print(f"⚠️  {device} requires permission fix")
                    self.fix_device_permissions(device)
                    
            except Exception as e:
                print(f"❌ Error checking {device}: {e}")
        
        return len(tty_devices) > 0

    def fix_device_permissions(self, device):
        """Fix device permissions for current user"""
        print(f"🔧 Fixing permissions for {device}...")
        
        try:
            # Add user to dialout group
            username = os.getenv('USER')
            result = subprocess.run(['sudo', 'usermod', '-a', '-G', 'dialout', username], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"✅ Added {username} to dialout group")
                print("⚠️  Please logout and login again for changes to take effect")
            else:
                print(f"❌ Failed to add user to dialout group: {result.stderr}")
                
        except Exception as e:
            print(f"❌ Permission fix failed: {e}")

    def setup_udev_rules(self):
        """Setup udev rules for ESP32 devices"""
        print("📋 Setting up udev rules for ESP32 devices...")
        
        udev_rules = '''# ESP32-C6 USB JTAG/Serial Debug Unit
SUBSYSTEM=="tty", ATTRS{idVendor}=="303a", ATTRS{idProduct}=="1001", MODE="0666", GROUP="dialout"
SUBSYSTEM=="usb", ATTRS{idVendor}=="303a", ATTRS{idProduct}=="1001", MODE="0666", GROUP="dialout"

# ESP32-S2/S3 USB DFU/CDC
SUBSYSTEM=="tty", ATTRS{idVendor}=="303a", ATTRS{idProduct}=="0002", MODE="0666", GROUP="dialout"
SUBSYSTEM=="usb", ATTRS{idVendor}=="303a", ATTRS{idProduct}=="0002", MODE="0666", GROUP="dialout"

# CP2102 USB to UART Bridge (common ESP32 boards)
SUBSYSTEM=="tty", ATTRS{idVendor}=="10c4", ATTRS{idProduct}=="ea60", MODE="0666", GROUP="dialout"

# FT232R USB UART (ESP-PROG and others)
SUBSYSTEM=="tty", ATTRS{idVendor}=="0403", ATTRS{idProduct}=="6001", MODE="0666", GROUP="dialout"
'''
        
        rules_file = '/etc/udev/rules.d/99-esp32-wsl2.rules'
        
        try:
            # Write udev rules
            with open(rules_file, 'w') as f:
                f.write(udev_rules)
            
            # Reload udev rules
            subprocess.run(['sudo', 'udevadm', 'control', '--reload-rules'], check=True)
            subprocess.run(['sudo', 'udevadm', 'trigger'], check=True)
            
            print(f"✅ udev rules created: {rules_file}")
            
        except PermissionError:
            print("❌ Permission denied. Run with sudo to create udev rules.")
        except Exception as e:
            print(f"❌ Failed to setup udev rules: {e}")

    def create_wsl_debug_scripts(self):
        """Create WSL2-specific debugging scripts"""
        scripts_dir = Path.cwd() / 'wsl2_debug_scripts'
        scripts_dir.mkdir(exist_ok=True)
        
        # ESP32 device management script
        device_manager = scripts_dir / 'esp32_device_manager.py'
        with open(device_manager, 'w') as f:
            f.write('''#!/usr/bin/env python3
"""ESP32 Device Manager for WSL2"""
import subprocess
import sys

def list_devices():
    """List ESP32 devices"""
    print("ESP32 Devices:")
    try:
        result = subprocess.run(['usbipd.exe', 'list'], capture_output=True, text=True)
        for line in result.stdout.split('\\n'):
            if '303a:1001' in line:
                print(f"  {line}")
    except:
        print("  usbipd not available")

def attach_device(busid):
    """Attach device to WSL2"""
    try:
        subprocess.run(['usbipd.exe', 'attach', '--wsl', '--busid', busid, '--auto-attach'], check=True)
        print(f"✅ Device {busid} attached")
    except:
        print(f"❌ Failed to attach {busid}")

def detach_device(busid):
    """Detach device from WSL2"""
    try:
        subprocess.run(['usbipd.exe', 'detach', '--busid', busid], check=True)
        print(f"✅ Device {busid} detached")
    except:
        print(f"❌ Failed to detach {busid}")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        list_devices()
    elif sys.argv[1] == 'attach' and len(sys.argv) == 3:
        attach_device(sys.argv[2])
    elif sys.argv[1] == 'detach' and len(sys.argv) == 3:
        detach_device(sys.argv[2])
    else:
        print("Usage: esp32_device_manager.py [attach|detach] <busid>")
''')
        os.chmod(device_manager, 0o755)
        
        # WSL2 debug session starter
        debug_starter = scripts_dir / 'start_wsl2_debug.sh'
        with open(debug_starter, 'w') as f:
            f.write('''#!/bin/bash
# WSL2 ESP32-C6 Debug Session Starter

echo "🚀 Starting WSL2 ESP32-C6 Debug Session"

# Check for ESP32 device
if [ ! -e /dev/ttyACM0 ]; then
    echo "❌ ESP32 device not found at /dev/ttyACM0"
    echo "💡 Try: python3 wsl2_debug_scripts/esp32_device_manager.py"
    exit 1
fi

# Check permissions
if [ ! -w /dev/ttyACM0 ]; then
    echo "⚠️  Device permissions issue. Adding to dialout group..."
    sudo usermod -a -G dialout $USER
    echo "🔄 Please logout and login again, then retry"
    exit 1
fi

# Start debug session
echo "✅ Device ready, starting debug session..."
cd .. && python3 tools/esp32c6_gdb_automation.py --profile basic
''')
        os.chmod(debug_starter, 0o755)
        
        print(f"✅ Created WSL2 debug scripts: {scripts_dir}")
        return scripts_dir

    def run_full_setup(self):
        """Run complete WSL2 ESP32 debugging setup"""
        print("🏗️  WSL2 ESP32-C6 Debugging Setup")
        print("=" * 40)
        
        if not self.is_wsl:
            print("⚠️  This tool is designed for WSL2 environments")
            return False
        
        # Step 1: Check usbipd-win
        if not self.check_usbipd_windows():
            return False
        
        # Step 2: List and setup ESP32 devices
        devices = self.list_usb_devices()
        
        if not self.esp32_devices:
            print("❌ No ESP32-C6 devices found")
            print("💡 Ensure ESP32-C6 is connected to Windows host")
            return False
        
        # Step 3: Setup first ESP32 device found
        esp32_device = self.esp32_devices[0]
        busid = esp32_device['busid']
        
        print(f"🎯 Setting up ESP32-C6: {busid}")
        
        # Bind device
        if not self.bind_esp32_device(busid):
            return False
        
        # Attach device  
        if not self.attach_esp32_device(busid):
            return False
        
        # Wait for device to appear
        print("⏳ Waiting for device to appear in WSL2...")
        time.sleep(3)
        
        # Step 4: Verify device access
        if not self.verify_wsl_device_access():
            print("❌ Device verification failed")
            return False
        
        # Step 5: Setup udev rules
        self.setup_udev_rules()
        
        # Step 6: Create WSL2-specific scripts
        scripts_dir = self.create_wsl_debug_scripts()
        
        print("\n✅ WSL2 ESP32-C6 debugging setup complete!")
        print(f"📁 WSL2 scripts: {scripts_dir}")
        print("\n🚀 Quick start:")
        print("   ./wsl2_debug_scripts/start_wsl2_debug.sh")
        
        return True

def main():
    parser = argparse.ArgumentParser(description='WSL2 ESP32-C6 Debugging Setup Tool')
    parser.add_argument('--list-devices', action='store_true',
                       help='List available USB devices')
    parser.add_argument('--verify-access', action='store_true',
                       help='Verify device access only')
    parser.add_argument('--setup-udev', action='store_true',
                       help='Setup udev rules only')
    
    args = parser.parse_args()
    
    setup = WSL2ESP32DebugSetup()
    
    if args.list_devices:
        setup.check_usbipd_windows()
        setup.list_usb_devices()
        return
    
    if args.verify_access:
        setup.verify_wsl_device_access()
        return
    
    if args.setup_udev:
        setup.setup_udev_rules()
        return
    
    # Default: Full setup
    success = setup.run_full_setup()
    sys.exit(0 if success else 1)

# CLI wrapper functions for entry points
def cli_main():
    """CLI wrapper for entry point compatibility - safe version that doesn't parse args"""
    # Don't call main() directly as it parses sys.argv
    setup = WSL2ESP32DebugSetup()
    print("🐧 WSL2 ESP32-C6 Debugging Setup Tool")
    print("💡 Use 'esp32-debug setup-wsl2' for interactive setup")
    return setup

def setup_wsl2_mcp():
    """MCP wrapper for WSL2 setup"""
    setup = WSL2ESP32DebugSetup()
    return setup.run_full_setup()

if __name__ == '__main__':
    main()