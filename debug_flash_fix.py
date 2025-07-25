#!/usr/bin/env python3
"""
ESP32-C6 Flash Debug and Fix Tool
Automated recovery and flashing solution for ESP32-C6 connectivity issues
"""

import serial
import time
import subprocess
import sys
import os
from pathlib import Path

class ESP32C6FlashFix:
    def __init__(self, port="/dev/ttyACM0", baudrate=115200):
        self.port = port
        self.baudrate = baudrate
        self.timeout = 10
        
    def log(self, message, level="INFO"):
        timestamp = time.strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
        
    def check_device_presence(self):
        """Check if ESP32-C6 device is present and accessible"""
        self.log("Checking ESP32-C6 device presence...")
        
        # Check USB device
        try:
            result = subprocess.run(['lsusb'], capture_output=True, text=True)
            if "303a:1001" in result.stdout:
                self.log("✅ ESP32-C6 USB device detected")
            else:
                self.log("❌ ESP32-C6 USB device not found", "ERROR")
                return False
        except Exception as e:
            self.log(f"Error checking USB devices: {e}", "ERROR")
            return False
            
        # Check serial port
        if os.path.exists(self.port):
            self.log(f"✅ Serial port {self.port} exists")
            return True
        else:
            self.log(f"❌ Serial port {self.port} not found", "ERROR")
            return False
    
    def force_bootloader_mode(self):
        """Force ESP32-C6 into bootloader mode using RTS/DTR control"""
        self.log("Attempting to force bootloader mode...")
        
        try:
            # Open serial connection
            ser = serial.Serial(self.port, self.baudrate, timeout=1)
            
            # ESP32-C6 bootloader entry sequence
            self.log("Sending bootloader entry sequence...")
            
            # Hold BOOT (GPIO9) low and pulse RESET
            ser.setRTS(True)   # RTS controls RESET (active low)
            ser.setDTR(True)   # DTR controls GPIO0/BOOT (active low)
            time.sleep(0.1)
            
            ser.setRTS(False)  # Release RESET
            time.sleep(0.1)
            ser.setDTR(False)  # Release BOOT
            time.sleep(0.5)
            
            # Try alternative sequence
            ser.setRTS(True)
            ser.setDTR(False)
            time.sleep(0.1)
            ser.setRTS(False)
            time.sleep(0.5)
            
            ser.close()
            self.log("✅ Bootloader entry sequence completed")
            return True
            
        except Exception as e:
            self.log(f"❌ Failed to control serial lines: {e}", "ERROR")
            return False
    
    def test_esptool_connection(self):
        """Test esptool connection with ESP32-C6"""
        self.log("Testing esptool connection...")
        
        try:
            cmd = [
                'python', '-m', 'esptool',
                '--chip', 'esp32c6',
                '--port', self.port,
                '--baud', str(self.baudrate),
                'chip_id'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                self.log("✅ Esptool connection successful")
                self.log(f"Device info: {result.stdout.strip()}")
                return True
            else:
                self.log(f"❌ Esptool connection failed: {result.stderr}", "ERROR")
                return False
                
        except subprocess.TimeoutExpired:
            self.log("❌ Esptool connection timeout", "ERROR")
            return False
        except Exception as e:
            self.log(f"❌ Esptool test error: {e}", "ERROR")
            return False
    
    def flash_via_esptool(self):
        """Flash firmware using direct esptool commands"""
        self.log("Attempting direct esptool flash...")
        
        build_dir = Path("/home/rds/vesc_express/build")
        if not build_dir.exists():
            self.log("❌ Build directory not found", "ERROR")
            return False
        
        # Flash files mapping
        flash_files = {
            '0x0': 'bootloader/bootloader.bin',
            '0x8000': 'partition_table/partition-table.bin',
            '0xf000': 'ota_data_initial.bin',
            '0x20000': 'vesc_express.bin'
        }
        
        # Verify all files exist
        for offset, filename in flash_files.items():
            filepath = build_dir / filename
            if not filepath.exists():
                self.log(f"❌ Flash file not found: {filepath}", "ERROR")
                return False
        
        try:
            # Build esptool command
            cmd = [
                'python', '-m', 'esptool',
                '--chip', 'esp32c6',
                '--port', self.port,
                '--baud', str(self.baudrate),
                '--before', 'default_reset',
                '--after', 'hard_reset',
                'write_flash',
                '--flash_mode', 'dio',
                '--flash_freq', '80m',
                '--flash_size', '8MB'
            ]
            
            # Add flash file arguments
            for offset, filename in flash_files.items():
                cmd.extend([offset, str(build_dir / filename)])
            
            self.log(f"Executing: {' '.join(cmd[:10])}...")
            
            # Execute with real-time output
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, 
                                     universal_newlines=True, cwd=str(build_dir))
            
            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    print(output.strip())
            
            rc = process.poll()
            
            if rc == 0:
                self.log("✅ Direct esptool flash successful!", "SUCCESS")
                return True
            else:
                self.log(f"❌ Direct esptool flash failed with code {rc}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ Flash error: {e}", "ERROR")
            return False
    
    def recovery_sequence(self):
        """Complete recovery sequence for ESP32-C6 flashing issues"""
        self.log("🔧 Starting ESP32-C6 Flash Recovery Sequence", "INFO")
        
        # Step 1: Check device presence
        if not self.check_device_presence():
            self.log("❌ Device check failed - cannot proceed", "ERROR")
            return False
        
        # Step 2: Multiple bootloader mode attempts
        for attempt in range(3):
            self.log(f"Bootloader mode attempt {attempt + 1}/3")
            
            if self.force_bootloader_mode():
                time.sleep(2)  # Wait for bootloader to initialize
                
                # Test connection
                if self.test_esptool_connection():
                    break
            
            if attempt < 2:
                self.log("Retrying bootloader entry...")
                time.sleep(1)
        else:
            self.log("❌ Failed to establish connection after 3 attempts", "ERROR")
            # Continue anyway - sometimes flashing works even without chip_id
        
        # Step 3: Attempt flashing
        return self.flash_via_esptool()

def main():
    print("ESP32-C6 Flash Debug and Fix Tool")
    print("=" * 50)
    
    fixer = ESP32C6FlashFix()
    success = fixer.recovery_sequence()
    
    if success:
        print("\n🎉 ESP32-C6 Flash Recovery SUCCESSFUL!")
        print("✅ 8MB OTA Configuration Active")
        return 0
    else:
        print("\n❌ ESP32-C6 Flash Recovery FAILED")
        print("Manual intervention may be required")
        return 1

if __name__ == "__main__":
    sys.exit(main())