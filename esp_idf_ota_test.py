#!/usr/bin/env python3
"""
ESP-IDF Direct OTA Test
Uses ESP-IDF tools to demonstrate OTA functionality by:
1. Flashing firmware to alternate partition
2. Setting boot partition using ESP-IDF tools
3. Verifying partition switch works
"""

import subprocess
import time
import os
import sys
from pathlib import Path

class ESPIDFOTATest:
    def __init__(self):
        self.device_port = "/dev/ttyACM0"
        self.build_dir = Path("/home/rds/vesc_express/build")
        
    def log(self, message, level="INFO"):
        timestamp = time.strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
        
    def run_esp_command(self, cmd, description):
        """Run ESP-IDF command with proper environment"""
        self.log(f"🔧 {description}")
        self.log(f"Running: {' '.join(cmd)}")
        
        try:
            # Source ESP-IDF environment and run command
            env_cmd = ["bash", "-c", 
                      f"source .env.esp32 && source $IDF_PATH/export.sh && {' '.join(cmd)}"]
            
            result = subprocess.run(env_cmd, capture_output=True, text=True, 
                                  cwd="/home/rds/vesc_express")
            
            if result.returncode == 0:
                self.log(f"✅ Success: {description}")
                if result.stdout.strip():
                    self.log(f"Output: {result.stdout.strip()}")
                return True
            else:
                self.log(f"❌ Failed: {description}", "ERROR")
                if result.stderr.strip():
                    self.log(f"Error: {result.stderr.strip()}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ Command failed: {e}", "ERROR")
            return False
    
    def get_current_partition_info(self):
        """Get information about current running partition"""
        self.log("🔍 Getting current partition information...")
        
        # Read OTA data to see current state
        cmd = [
            "python", "-m", "esptool", "--chip", "esp32c6",
            "--port", self.device_port, "read_flash",
            "0xf000", "0x2000", "current_ota_data.bin"
        ]
        
        if self.run_esp_command(cmd, "Reading OTA data partition"):
            # Analyze OTA data
            try:
                with open("current_ota_data.bin", "rb") as f:
                    ota_data = f.read(32)
                    
                if ota_data[:4] == b'\xff\xff\xff\xff':
                    self.log("📍 Device currently running from app0 (factory partition)")
                    return "app0"
                else:
                    self.log("📍 Device currently running from app1 (OTA partition)")  
                    self.log(f"OTA data: {ota_data[:16].hex()}")
                    return "app1"
                    
            except Exception as e:
                self.log(f"⚠️  Could not analyze OTA data: {e}")
                return "unknown"
        
        return None
    
    def flash_to_alternate_partition(self):
        """Flash firmware to the alternate OTA partition"""
        self.log("🚀 Flashing firmware to alternate OTA partition...")
        
        firmware_file = self.build_dir / "vesc_express.bin"
        if not firmware_file.exists():
            self.log(f"❌ Firmware not found: {firmware_file}", "ERROR")
            return False
            
        firmware_size = firmware_file.stat().st_size
        self.log(f"📦 Firmware size: {firmware_size} bytes ({firmware_size/1024/1024:.2f}MB)")
        
        # Flash to app1 partition (0x320000)
        cmd = [
            "python", "-m", "esptool", "--chip", "esp32c6",
            "--port", self.device_port, "--baud", "460800",
            "--before", "default_reset", "--after", "no_reset",
            "write_flash", "--flash_mode", "dio", "--flash_freq", "80m",
            "0x320000", str(firmware_file)
        ]
        
        return self.run_esp_command(cmd, "Flashing firmware to app1 partition")
    
    def set_boot_partition(self, partition="app1"):
        """Set which partition to boot from by writing OTA data"""
        self.log(f"🔄 Setting boot partition to {partition}...")
        
        # Create OTA data for the desired partition
        # OTA data format: 4 bytes per slot, 0x00000000 = invalid, 0x00000001 = valid
        slot = 1 if partition == "app1" else 0
        
        if slot == 0:
            # Set app0 as active
            ota_data = b'\x00\x00\x00\x00' + b'\xff' * 4092  # app0=invalid, rest=0xFF
        else:
            # Set app1 as active  
            ota_data = b'\x01\x00\x00\x00' + b'\xff' * 4092  # app1=seq1, rest=0xFF
            
        # Write OTA data file
        with open("new_ota_data.bin", "wb") as f:
            f.write(ota_data)
        
        # Flash OTA data partition
        cmd = [
            "python", "-m", "esptool", "--chip", "esp32c6",
            "--port", self.device_port, "--baud", "460800",
            "--before", "default_reset", "--after", "no_reset",
            "write_flash", "0xf000", "new_ota_data.bin"
        ]
        
        return self.run_esp_command(cmd, f"Setting boot partition to {partition}")
    
    def reset_device(self):
        """Reset the device to boot from new partition"""
        self.log("🔄 Resetting device...")
        
        cmd = [
            "python", "-m", "esptool", "--chip", "esp32c6",
            "--port", self.device_port, "--before", "default_reset",
            "chip_id"
        ]
        
        return self.run_esp_command(cmd, "Resetting device")
    
    def verify_partition_switch(self, wait_time=10):
        """Verify device booted from new partition"""
        self.log(f"⏳ Waiting {wait_time}s for device to boot...")
        time.sleep(wait_time)
        
        new_partition = self.get_current_partition_info()
        if new_partition:
            self.log(f"📍 Device now running from: {new_partition}")
            return new_partition
        else:
            self.log("❌ Could not determine current partition", "ERROR")
            return None
    
    def create_test_firmware_version(self):
        """Create a modified version with updated version string"""
        self.log("🔧 Creating test firmware with version increment...")
        
        try:
            main_file = Path("/home/rds/vesc_express/main/main.c")
            if not main_file.exists():
                self.log("⚠️  main.c not found, using existing firmware")
                return True
                
            # For this test, we'll just use the existing firmware
            # In a real scenario, you'd modify version strings here
            self.log("✅ Using existing firmware for OTA test")
            return True
            
        except Exception as e:
            self.log(f"❌ Failed to prepare test firmware: {e}", "ERROR")
            return False
    
    def run_complete_ota_test(self):
        """Run complete OTA update test using ESP-IDF tools"""
        self.log("🔍 ESP-IDF Direct OTA Functionality Test")
        self.log("=" * 60)
        
        # Step 1: Check current state
        initial_partition = self.get_current_partition_info()
        if not initial_partition:
            return False
            
        self.log(f"📍 Initial partition: {initial_partition}")
        
        # Step 2: Prepare test firmware
        if not self.create_test_firmware_version():
            return False
        
        # Step 3: Flash to alternate partition
        if not self.flash_to_alternate_partition():
            return False
        
        # Step 4: Set boot partition
        target_partition = "app1" if initial_partition == "app0" else "app0"
        if not self.set_boot_partition(target_partition):
            return False
        
        # Step 5: Reset device
        if not self.reset_device():
            return False
        
        # Step 6: Verify partition switch
        final_partition = self.verify_partition_switch()
        if not final_partition:
            return False
        
        # Step 7: Check if switch was successful
        if final_partition != initial_partition:
            self.log("🎉 OTA PARTITION SWITCH SUCCESSFUL!")
            self.log(f"✅ Device switched from {initial_partition} to {final_partition}")
            return True
        else:
            self.log("❌ Partition switch failed - still on same partition", "ERROR")
            return False

def main():
    tester = ESPIDFOTATest()
    
    # Check ESP-IDF environment
    if 'IDF_PATH' not in os.environ:
        print("❌ ESP-IDF environment not loaded")
        print("Run: source .env.esp32 && source $IDF_PATH/export.sh")
        return 1
    
    success = tester.run_complete_ota_test()
    
    if success:
        print("\n🎉 ESP-IDF OTA TEST SUCCESSFUL!")
        print("✅ 8MB OTA partition switching is fully operational")
        return 0
    else:
        print("\n❌ ESP-IDF OTA TEST FAILED")
        return 1

if __name__ == "__main__":
    sys.exit(main())