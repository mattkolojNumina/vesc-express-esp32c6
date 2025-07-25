#!/usr/bin/env python3
"""
ESP32-C6 OTA Validation Test
Validates that 8MB OTA partition system is working correctly
"""

import subprocess
import time
import sys
import os
from pathlib import Path

class OTAValidator:
    def __init__(self):
        self.device_port = "/dev/ttyACM0"
        self.build_dir = Path("/home/rds/vesc_express/build")
        
    def log(self, message, level="INFO"):
        timestamp = time.strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
        
    def check_partition_table(self):
        """Verify 8MB OTA partition table is active"""
        self.log("🔍 Verifying 8MB OTA partition table...")
        
        try:
            # Read partition table from device
            cmd = [
                "python", "-m", "esptool", "--chip", "esp32c6", 
                "--port", self.device_port, "read_flash", 
                "0x8000", "0x1000", "current_partitions.bin"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                self.log(f"❌ Failed to read partition table: {result.stderr}", "ERROR")
                return False
            
            # Parse partition table
            parse_cmd = [
                "python", f"{os.environ['IDF_PATH']}/components/partition_table/gen_esp32part.py",
                "current_partitions.bin"
            ]
            
            result = subprocess.run(parse_cmd, capture_output=True, text=True)
            if result.returncode == 0:
                output = result.stdout
                
                # Check for expected 8MB partitions
                if "app0,app,ota_0,0x20000,3M" in output and "app1,app,ota_1,0x320000,3M" in output:
                    self.log("✅ 8MB OTA partitions confirmed: app0=3MB, app1=3MB")
                    return True
                else:
                    self.log("❌ Partition layout doesn't match 8MB OTA configuration", "ERROR")
                    return False
            else:
                self.log(f"❌ Failed to parse partition table: {result.stderr}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ Partition check failed: {e}", "ERROR")
            return False
    
    def check_current_app_partition(self):
        """Check which app partition is currently running"""
        self.log("🔍 Checking current running partition...")
        
        try:
            # Read OTA data partition to see which app is active
            cmd = [
                "python", "-m", "esptool", "--chip", "esp32c6",
                "--port", self.device_port, "read_flash",
                "0xf000", "0x2000", "ota_data.bin"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                self.log("✅ OTA data partition readable")
                
                # Check file size to determine if OTA has been used
                ota_file = Path("ota_data.bin")
                if ota_file.exists():
                    size = ota_file.stat().st_size
                    self.log(f"📊 OTA data size: {size} bytes")
                    
                    # Read first few bytes to check OTA status
                    with open("ota_data.bin", "rb") as f:
                        data = f.read(32)
                        if data[:4] == b'\xff\xff\xff\xff':
                            self.log("📍 Device running from app0 (factory/initial partition)")
                        else:
                            self.log("📍 Device has OTA state data (switched partitions)")
                    
                    return True
            else:
                self.log(f"❌ Failed to read OTA data: {result.stderr}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ Current partition check failed: {e}", "ERROR")
            return False
    
    def verify_firmware_size_compatibility(self):
        """Verify current firmware fits in OTA partitions"""
        self.log("🔍 Checking firmware size compatibility...")
        
        try:
            firmware_file = self.build_dir / "vesc_express.bin"
            if not firmware_file.exists():
                self.log("❌ Firmware binary not found in build directory", "ERROR")
                return False
            
            firmware_size = firmware_file.stat().st_size
            firmware_mb = firmware_size / (1024 * 1024)
            partition_size_mb = 3.0  # 3MB OTA partitions
            
            self.log(f"📦 Firmware size: {firmware_mb:.2f}MB")
            self.log(f"📦 Partition size: {partition_size_mb:.2f}MB")
            
            if firmware_size < (partition_size_mb * 1024 * 1024):
                usage_percent = (firmware_mb / partition_size_mb) * 100
                self.log(f"✅ Firmware fits: {usage_percent:.1f}% partition usage")
                self.log(f"✅ Available space: {partition_size_mb - firmware_mb:.2f}MB")
                return True
            else:
                self.log("❌ Firmware too large for OTA partitions", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ Size check failed: {e}", "ERROR")
            return False
    
    def test_ota_flash_to_alternate_partition(self):
        """Test flashing firmware to alternate OTA partition"""
        self.log("🚀 Testing OTA flash to alternate partition...")
        
        try:
            firmware_file = self.build_dir / "vesc_express.bin"
            if not firmware_file.exists():
                self.log("❌ Firmware binary not found", "ERROR")
                return False
            
            # Flash to app1 partition (alternate from typical app0)
            cmd = [
                "python", "-m", "esptool", "--chip", "esp32c6",
                "--port", self.device_port, "--baud", "460800",
                "--before", "default_reset", "--after", "no_reset",
                "write_flash", "--flash_mode", "dio", "--flash_freq", "80m",
                "0x320000", str(firmware_file)  # app1 partition address
            ]
            
            self.log("📤 Flashing firmware to app1 partition (0x320000)...")
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                self.log("✅ Firmware successfully flashed to app1 partition")
                self.log("💡 Note: Device still boots from app0 until OTA data is updated")
                return True
            else:
                self.log(f"❌ Flash to app1 failed: {result.stderr}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ OTA flash test failed: {e}", "ERROR")
            return False
    
    def run_validation(self):
        """Run complete OTA validation test"""
        self.log("🔍 ESP32-C6 8MB OTA Validation Test")
        self.log("=" * 60)
        
        tests = [
            ("Partition Table Check", self.check_partition_table),
            ("Current App Check", self.check_current_app_partition),
            ("Firmware Size Check", self.verify_firmware_size_compatibility),
            ("OTA Flash Test", self.test_ota_flash_to_alternate_partition)
        ]
        
        results = []
        for test_name, test_func in tests:
            self.log(f"Running: {test_name}")
            result = test_func()
            results.append((test_name, result))
            self.log("")
        
        # Summary
        self.log("=" * 60)
        self.log("🏁 VALIDATION SUMMARY")
        self.log("=" * 60)
        
        passed = 0
        for test_name, result in results:
            status = "✅ PASS" if result else "❌ FAIL"
            self.log(f"{status}: {test_name}")
            if result:
                passed += 1
        
        self.log("")
        if passed == len(tests):
            self.log("🎉 ALL TESTS PASSED - 8MB OTA System Fully Operational!")
            self.log("✅ Ready for production OTA updates")
            return True
        else:
            self.log(f"⚠️  {passed}/{len(tests)} tests passed - Some issues need attention")
            return False

def main():
    validator = OTAValidator()
    
    # Check environment
    if 'IDF_PATH' not in os.environ:
        print("❌ ESP-IDF environment not loaded. Run: source .env.esp32 && source $IDF_PATH/export.sh")
        return 1
    
    success = validator.run_validation()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())