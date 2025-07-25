#!/usr/bin/env python3
"""
ESP32-C6 OpenOCD Setup Automation Tool
Simplifies OpenOCD configuration and connection for ESP32-C6 debugging
"""

import os
import sys
import json
import subprocess
import time
import argparse
from pathlib import Path

class ESP32C6OpenOCDSetup:
    """
    ESP32-C6 OpenOCD Setup and Configuration Tool
    
    Automates OpenOCD configuration for ESP32-C6 debugging including:
    - Device detection and USB JTAG setup
    - Configuration file generation with multiple profiles
    - VS Code integration and debug script creation
    - Connection testing and validation
    """
    def __init__(self):
        self.esp_idf_path = os.environ.get('IDF_PATH')
        self.project_path = os.getcwd()
        self.config_templates = {
            'basic': '''# ESP32-C6 Basic OpenOCD Configuration
adapter driver esp_usb_jtag
adapter speed 6000
esp_usb_jtag vid_pid 0x303a 0x1001
set ESP_RTOS none

source [find target/esp32c6.cfg]
reset_config srst_only srst_nogate
''',
            'optimized': '''# ESP32-C6 Optimized OpenOCD Configuration
adapter driver esp_usb_jtag
adapter speed 20000
esp_usb_jtag vid_pid 0x303a 0x1001
esp_usb_jtag caps_descriptor /dev/ttyACM0
set ESP_RTOS FreeRTOS

source [find target/esp32c6.cfg]
reset_config srst_only srst_nogate

# Enhanced debugging features
gdb_memory_map enable
gdb_flash_program enable
gdb_breakpoint_override hard

# WSL2 optimizations
adapter usb location any
''',
            'production': '''# ESP32-C6 Production Debug Configuration
adapter driver esp_usb_jtag
adapter speed 40000
esp_usb_jtag vid_pid 0x303a 0x1001
set ESP_RTOS FreeRTOS

source [find target/esp32c6.cfg]
reset_config srst_only srst_nogate

# Production debugging features
gdb_memory_map enable
gdb_flash_program enable
gdb_report_data_abort enable
monitor arm semihosting enable

# Performance optimizations
adapter usb location any
init
'''
        }

    def detect_esp32c6(self):
        """Detect ESP32-C6 device connection"""
        print("🔍 Detecting ESP32-C6 device...")
        
        # Check for USB device
        try:
            result = subprocess.run(['lsusb'], capture_output=True, text=True)
            if '303a:1001' in result.stdout:
                print("✅ ESP32-C6 USB device detected (303a:1001)")
                return True
        except (subprocess.SubprocessError, FileNotFoundError, OSError):
            # lsusb not available or failed
            pass
        
        # Check for serial device
        for device in ['/dev/ttyACM0', '/dev/ttyUSB0', '/dev/cu.usbmodem*']:
            if os.path.exists(device) or '*' in device:
                print(f"✅ Serial device found: {device}")
                return True
        
        print("❌ ESP32-C6 not detected. Check USB connection.")
        return False

    def check_dependencies(self):
        """Check required dependencies"""
        print("🔧 Checking dependencies...")
        
        dependencies = {
            'openocd': 'OpenOCD JTAG debugger',
            'riscv32-esp-elf-gdb': 'ESP32 GDB debugger'
        }
        
        missing = []
        for cmd, desc in dependencies.items():
            try:
                subprocess.run([cmd, '--version'], capture_output=True, check=True)
                print(f"✅ {desc} found")
            except (subprocess.CalledProcessError, FileNotFoundError):
                print(f"❌ {desc} not found")
                missing.append(cmd)
        
        if missing:
            print(f"\n❌ Missing dependencies: {', '.join(missing)}")
            if self.esp_idf_path:
                print(f"💡 Try: source {self.esp_idf_path}/export.sh")
            return False
        
        return True

    def create_config(self, config_type='optimized'):
        """Create OpenOCD configuration file"""
        config_path = Path(self.project_path) / f'esp32c6_{config_type}.cfg'
        
        with open(config_path, 'w') as f:
            f.write(self.config_templates[config_type])
        
        print(f"✅ Created OpenOCD config: {config_path}")
        return config_path

    def test_connection(self, config_path):
        """Test OpenOCD connection"""
        print("🔗 Testing OpenOCD connection...")
        
        cmd = [
            'openocd',
            '-f', str(config_path),
            '-c', 'init',
            '-c', 'reset halt',
            '-c', 'reg pc',
            '-c', 'exit'
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0 and 'JTAG tap: esp32c6.cpu tap/device found' in result.stdout:
                print("✅ OpenOCD connection successful!")
                # Extract useful info
                for line in result.stdout.split('\n'):
                    if 'tap/device found' in line or 'clock speed' in line:
                        print(f"   {line.strip()}")
                return True
            else:
                print("❌ OpenOCD connection failed")
                print(f"Error output:\n{result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print("❌ OpenOCD connection timeout (>30s)")
            return False

    def create_debug_scripts(self):
        """Create debugging helper scripts"""
        scripts_dir = Path(self.project_path) / 'debug_scripts'
        scripts_dir.mkdir(exist_ok=True)
        
        # OpenOCD launcher script
        openocd_script = scripts_dir / 'start_openocd.sh'
        with open(openocd_script, 'w') as f:
            f.write('''#!/bin/bash
# ESP32-C6 OpenOCD Launcher
echo "🚀 Starting OpenOCD for ESP32-C6..."
openocd -f esp32c6_optimized.cfg
''')
        os.chmod(openocd_script, 0o755)
        
        # GDB launcher script
        gdb_script = scripts_dir / 'start_gdb.sh'
        with open(gdb_script, 'w') as f:
            f.write('''#!/bin/bash
# ESP32-C6 GDB Launcher
if [ ! -f "build/project.elf" ]; then
    echo "❌ Build project first: idf.py build"
    exit 1
fi

echo "🐛 Starting GDB for ESP32-C6..."
riscv32-esp-elf-gdb build/project.elf \
    -ex "set architecture riscv:rv32" \
    -ex "target remote localhost:3333" \
    -ex "file build/project.elf"
''')
        os.chmod(gdb_script, 0o755)
        
        # Quick debug script
        quick_debug = scripts_dir / 'quick_debug.sh'
        with open(quick_debug, 'w') as f:
            f.write('''#!/bin/bash
# Quick ESP32-C6 Debug Session
echo "⚡ Quick ESP32-C6 Debug Setup"

# Start OpenOCD in background
echo "Starting OpenOCD..."
openocd -f esp32c6_optimized.cfg > openocd.log 2>&1 &
OPENOCD_PID=$!

# Wait for OpenOCD to start
sleep 3

# Check if project is built
if [ ! -f "build/project.elf" ]; then
    echo "Building project..."
    idf.py build
fi

# Start GDB
echo "Starting GDB session..."
riscv32-esp-elf-gdb build/project.elf \
    -ex "set architecture riscv:rv32" \
    -ex "target remote localhost:3333" \
    -ex "file build/project.elf" \
    -ex "monitor reset halt" \
    -ex "break app_main"

# Cleanup
echo "Stopping OpenOCD..."
kill $OPENOCD_PID
''')
        os.chmod(quick_debug, 0o755)
        
        print(f"✅ Created debug scripts in: {scripts_dir}")
        return scripts_dir

    def generate_vscode_config(self):
        """Generate VS Code debugging configuration"""
        vscode_dir = Path(self.project_path) / '.vscode'
        vscode_dir.mkdir(exist_ok=True)
        
        launch_config = {
            "version": "0.2.0",
            "configurations": [
                {
                    "name": "ESP32-C6 Debug",
                    "type": "cppdbg",
                    "request": "launch",
                    "program": "${workspaceFolder}/build/project.elf",
                    "args": [],
                    "stopAtEntry": False,
                    "cwd": "${workspaceFolder}",
                    "environment": [],
                    "externalConsole": False,
                    "MIMode": "gdb",
                    "miDebuggerPath": "riscv32-esp-elf-gdb",
                    "miDebuggerServerAddress": "localhost:3333",
                    "setupCommands": [
                        {
                            "description": "Set architecture",
                            "text": "set architecture riscv:rv32"
                        },
                        {
                            "description": "Reset and halt",
                            "text": "monitor reset halt"
                        }
                    ],
                    "preLaunchTask": "Start OpenOCD"
                }
            ]
        }
        
        tasks_config = {
            "version": "2.0.0",
            "tasks": [
                {
                    "label": "Start OpenOCD",
                    "type": "shell",
                    "command": "openocd",
                    "args": ["-f", "esp32c6_optimized.cfg"],
                    "group": "build",
                    "presentation": {
                        "echo": True,
                        "reveal": "always",
                        "focus": False,
                        "panel": "shared"
                    },
                    "runOptions": {
                        "runOn": "folderOpen"
                    }
                }
            ]
        }
        
        with open(vscode_dir / 'launch.json', 'w') as f:
            json.dump(launch_config, f, indent=2)
        
        with open(vscode_dir / 'tasks.json', 'w') as f:
            json.dump(tasks_config, f, indent=2)
        
        print(f"✅ Created VS Code debug configuration")

    def run_full_setup(self, config_type='optimized', test_connection=True):
        """Run complete setup process"""
        print("🔧 ESP32-C6 OpenOCD Setup Tool")
        print("=" * 40)
        
        # Step 1: Check dependencies
        if not self.check_dependencies():
            return False
        
        # Step 2: Detect device
        if not self.detect_esp32c6():
            print("💡 Ensure ESP32-C6 is connected via USB")
            return False
        
        # Step 3: Create configuration
        config_path = self.create_config(config_type)
        
        # Step 4: Test connection (optional)
        if test_connection:
            if not self.test_connection(config_path):
                return False
        
        # Step 5: Create helper scripts
        scripts_dir = self.create_debug_scripts()
        
        # Step 6: Generate VS Code config
        self.generate_vscode_config()
        
        print("\n✅ ESP32-C6 OpenOCD setup complete!")
        print(f"📁 Configuration: {config_path}")
        print(f"📁 Debug scripts: {scripts_dir}")
        print(f"📁 VS Code config: .vscode/")
        print("\n🚀 Quick start:")
        print(f"   ./debug_scripts/quick_debug.sh")
        
        return True

def main():
    parser = argparse.ArgumentParser(description='ESP32-C6 OpenOCD Setup Tool')
    parser.add_argument('--config', choices=['basic', 'optimized', 'production'], 
                       default='optimized', help='Configuration type')
    parser.add_argument('--no-test', action='store_true', 
                       help='Skip connection testing')
    parser.add_argument('--detect-only', action='store_true',
                       help='Only detect device, don\'t setup')
    
    args = parser.parse_args()
    
    setup = ESP32C6OpenOCDSetup()
    
    if args.detect_only:
        setup.detect_esp32c6()
        return
    
    success = setup.run_full_setup(
        config_type=args.config,
        test_connection=not args.no_test
    )
    
    sys.exit(0 if success else 1)

# CLI wrapper functions for entry points
def cli_main():
    """CLI wrapper for entry point compatibility - safe version that doesn't parse args"""
    # Don't call main() directly as it parses sys.argv
    setup = ESP32C6OpenOCDSetup()
    print("🔧 ESP32-C6 OpenOCD Setup Tool")
    print("💡 Use 'esp32-debug setup-openocd' for interactive setup")
    return setup

def create_openocd_config(config_type="optimized"):
    """MCP wrapper for creating OpenOCD config"""
    setup = ESP32C6OpenOCDSetup()
    return setup.run_full_setup(config_type, test_connection=False)

if __name__ == '__main__':
    main()