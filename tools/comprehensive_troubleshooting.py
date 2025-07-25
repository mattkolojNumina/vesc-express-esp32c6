#!/usr/bin/env python3
"""
Comprehensive Troubleshooting Automation
Implementation of all troubleshooting scenarios from ESP-IDF research document
"""

import subprocess
import os
import sys
import time
import re
import json
from pathlib import Path
from datetime import datetime

class ComprehensiveTroubleshooter:
    """
    Automated troubleshooting for ESP32-C6 VESC Express development
    Based on ESP-IDF research document troubleshooting section
    """
    
    def __init__(self):
        self.results = {}
        self.fixes_applied = []
        self.logs_dir = Path("troubleshooting_logs")
        self.logs_dir.mkdir(exist_ok=True)
        
    def log_result(self, test_name, status, details="", fix_applied=None):
        """Log troubleshooting results"""
        self.results[test_name] = {
            'status': status,
            'details': details,
            'timestamp': datetime.now().isoformat(),
            'fix_applied': fix_applied
        }
        
        if fix_applied:
            self.fixes_applied.append(fix_applied)
    
    def run_command(self, cmd, description=None, timeout=30):
        """Run command with error handling and logging"""
        if description:
            print(f"🔍 {description}")
        
        try:
            result = subprocess.run(
                cmd, shell=True, capture_output=True, text=True, 
                timeout=timeout, cwd=os.getcwd()
            )
            return result
        except subprocess.TimeoutExpired:
            print(f"⏰ Command timed out: {cmd}")
            return None
        except Exception as e:
            print(f"❌ Command failed: {e}")
            return None
    
    def check_device_permissions(self):
        """Check and fix device permission issues"""
        print("\n🔐 === DEVICE PERMISSIONS CHECK ===")
        print("From research document: Permission denied on /dev/ttyUSB0 or /dev/ttyACM0")
        
        # Check if device exists
        device_paths = ['/dev/ttyACM0', '/dev/ttyUSB0', '/dev/ttyACM1']
        found_device = None
        
        for device in device_paths:
            if os.path.exists(device):
                found_device = device
                break
        
        if not found_device:
            self.log_result(
                "device_permissions", 
                "FAIL", 
                "No ESP32 device found at common paths"
            )
            print("❌ No ESP32 device detected")
            print("💡 Solution: Check USB connection and run: lsusb | grep ESP")
            return False
        
        print(f"✅ Device found: {found_device}")
        
        # Check permissions
        stat_result = self.run_command(f"ls -la {found_device}")
        if stat_result and stat_result.returncode == 0:
            print(f"📋 Device permissions: {stat_result.stdout.strip()}")
            
            # Check if user is in dialout group
            groups_result = self.run_command("groups")
            if groups_result and 'dialout' not in groups_result.stdout:
                print("⚠️  User not in dialout group")
                fix_cmd = f"sudo usermod -aG dialout $USER"
                print(f"💡 Fix: {fix_cmd}")
                
                # Auto-apply fix
                fix_result = self.run_command(fix_cmd, "Adding user to dialout group")
                if fix_result and fix_result.returncode == 0:
                    self.log_result(
                        "device_permissions", 
                        "FIXED", 
                        "Added user to dialout group - logout/login required",
                        fix_cmd
                    )
                    print("✅ User added to dialout group")
                    print("⚠️  Please logout and login for changes to take effect")
                else:
                    self.log_result("device_permissions", "FAIL", "Could not add user to dialout group")
            else:
                self.log_result("device_permissions", "PASS", "User in dialout group")
                print("✅ User is in dialout group")
        
        # Check udev rules
        udev_files = [
            '/etc/udev/rules.d/99-esp-devices.rules',
            '/etc/udev/rules.d/99-esp32.rules',
            '/etc/udev/rules.d/99-esp32c6-jtag.rules'
        ]
        
        udev_exists = any(os.path.exists(f) for f in udev_files)
        if not udev_exists:
            print("⚠️  No ESP-specific udev rules found")
            
            # Create udev rules as per research document
            udev_content = '''# Espressif built-in USB JTAG/Serial (e.g., ESP32-S3, ESP32-C3, ESP32-C6)
SUBSYSTEM=="usb", ATTRS{idVendor}=="303a", ATTRS{idProduct}=="1001", MODE="0666", GROUP="plugdev"

# Silicon Labs CP210x UART Bridge
SUBSYSTEM=="usb", ATTRS{idVendor}=="10c4", ATTRS{idProduct}=="ea60", MODE="0666", GROUP="plugdev"

# WCH CH340/CH341 UART Bridge
SUBSYSTEM=="usb", ATTRS{idVendor}=="1a86", ATTRS{idProduct}=="7523", MODE="0666", GROUP="plugdev"
'''
            
            udev_file = '/etc/udev/rules.d/99-esp-devices.rules'
            try:
                with open('temp_udev_rules.txt', 'w') as f:
                    f.write(udev_content)
                
                fix_cmd = f"sudo cp temp_udev_rules.txt {udev_file} && sudo udevadm control --reload-rules && sudo udevadm trigger"
                fix_result = self.run_command(fix_cmd, "Creating ESP udev rules")
                
                if fix_result and fix_result.returncode == 0:
                    self.log_result(
                        "udev_rules",
                        "FIXED", 
                        "Created ESP device udev rules",
                        fix_cmd
                    )
                    print("✅ ESP udev rules created")
                else:
                    self.log_result("udev_rules", "FAIL", "Could not create udev rules")
                
                # Cleanup
                if os.path.exists('temp_udev_rules.txt'):
                    os.remove('temp_udev_rules.txt')
                    
            except Exception as e:
                self.log_result("udev_rules", "FAIL", f"Udev rules creation failed: {e}")
        else:
            self.log_result("udev_rules", "PASS", "ESP udev rules exist")
            print("✅ ESP udev rules found")
        
        return True
    
    def check_esp_idf_environment(self):
        """Check ESP-IDF environment issues"""
        print("\n🔧 === ESP-IDF ENVIRONMENT CHECK ===")
        print("From research document: Python environment and installation issues")
        
        # Check ESP-IDF path
        idf_path = os.environ.get('IDF_PATH')
        if not idf_path:
            print("❌ IDF_PATH not set")
            expected_path = '/home/rds/esp/esp-idf'
            if os.path.exists(expected_path):
                fix_cmd = f"export IDF_PATH={expected_path}"
                print(f"💡 Fix: {fix_cmd}")
                os.environ['IDF_PATH'] = expected_path
                self.log_result(
                    "idf_path",
                    "FIXED",
                    f"Set IDF_PATH to {expected_path}",
                    fix_cmd
                )
            else:
                self.log_result("idf_path", "FAIL", "ESP-IDF not found")
                return False
        else:
            print(f"✅ IDF_PATH: {idf_path}")
            self.log_result("idf_path", "PASS", f"IDF_PATH set to {idf_path}")
        
        # Check Python virtual environment
        python_env = os.environ.get('VIRTUAL_ENV')
        if not python_env or 'espressif' not in python_env:
            print("⚠️  ESP-IDF Python virtual environment not active")
            
            # Try to activate environment
            idf_path = os.environ.get('IDF_PATH', '/home/rds/esp/esp-idf')
            export_script = f"{idf_path}/export.sh"
            
            if os.path.exists(export_script):
                fix_cmd = f"source {export_script}"
                print(f"💡 Fix: {fix_cmd}")
                
                # Source environment and check idf.py
                env_result = self.run_command(f"bash -c 'source {export_script} && idf.py --version'")
                if env_result and env_result.returncode == 0:
                    self.log_result(
                        "python_env",
                        "FIXED",
                        "ESP-IDF environment activated",
                        fix_cmd
                    )
                    print("✅ ESP-IDF environment activated")
                else:
                    self.log_result("python_env", "FAIL", "Could not activate ESP-IDF environment")
            else:
                self.log_result("python_env", "FAIL", "export.sh not found")
        else:
            self.log_result("python_env", "PASS", "ESP-IDF Python environment active")
            print("✅ ESP-IDF Python environment active")
        
        # Check Python version
        python_result = self.run_command("python --version")
        if python_result and python_result.returncode == 0:
            version_str = python_result.stdout.strip()
            print(f"🐍 Python version: {version_str}")
            
            # Extract version number
            version_match = re.search(r'(\d+)\.(\d+)', version_str)
            if version_match:
                major, minor = int(version_match.group(1)), int(version_match.group(2))
                if major >= 3 and minor >= 9:
                    self.log_result("python_version", "PASS", f"Python {major}.{minor} compatible")
                    print("✅ Python version compatible")
                else:
                    self.log_result("python_version", "FAIL", f"Python {major}.{minor} too old (need 3.9+)")
                    print(f"❌ Python {major}.{minor} too old (ESP-IDF v5.5 requires 3.9+)")
        
        return True
    
    def check_connection_issues(self):
        """Check device connection issues"""
        print("\n🔌 === CONNECTION ISSUES CHECK ===")
        print("From research document: Failed to connect timeout issues")
        
        # Check USB device detection
        lsusb_result = self.run_command("lsusb | grep -i esp")
        if lsusb_result and lsusb_result.stdout.strip():
            print(f"✅ ESP device detected: {lsusb_result.stdout.strip()}")
            self.log_result("usb_detection", "PASS", "ESP device visible via USB")
        else:
            print("❌ No ESP device detected via USB")
            self.log_result("usb_detection", "FAIL", "Device not visible in lsusb")
            
            # WSL2 specific check
            if 'microsoft' in os.uname().release.lower():
                print("💡 WSL2 detected - check USB passthrough with:")
                print("   Windows PowerShell: usbipd list")
                print("   Windows PowerShell: usbipd attach --wsl --busid <BUSID>")
        
        # Check serial port availability
        serial_ports = ['/dev/ttyACM0', '/dev/ttyUSB0', '/dev/ttyACM1']
        available_port = None
        
        for port in serial_ports:
            if os.path.exists(port):
                available_port = port
                print(f"✅ Serial port available: {port}")
                break
        
        if not available_port:
            print("❌ No serial ports found")
            self.log_result("serial_port", "FAIL", "No serial device nodes found")
            return False
        
        # Test basic connection
        test_result = self.run_command(f"esptool.py -p {available_port} chip_id", timeout=10)
        if test_result and test_result.returncode == 0:
            print("✅ Basic esptool connection successful")
            self.log_result("basic_connection", "PASS", "esptool.py can communicate with device")
        else:
            print("❌ esptool connection failed")
            print("💡 Try manual bootloader mode:")
            print("   1. Hold BOOT button")
            print("   2. Press and release RESET button")
            print("   3. Release BOOT button")
            self.log_result("basic_connection", "FAIL", "esptool.py cannot communicate")
        
        return True
    
    def check_build_issues(self):
        """Check build system issues"""
        print("\n🔨 === BUILD SYSTEM CHECK ===")
        print("From research document: Build fails and path issues")
        
        # Check if we're in WSL2 mounted drive (common issue)
        cwd = os.getcwd()
        if cwd.startswith('/mnt/c') or cwd.startswith('/mnt/d'):
            print("⚠️  Project located on Windows drive mount")
            print("❌ This can cause build failures due to path length limits")
            print("💡 Solution: Move project to native WSL2 filesystem (~/)")
            self.log_result(
                "build_location", 
                "FAIL", 
                "Project on Windows mount - move to native filesystem"
            )
        else:
            print("✅ Project on native filesystem")
            self.log_result("build_location", "PASS", "Project on native filesystem")
        
        # Check for build directory issues
        build_dir = Path("build")
        if build_dir.exists():
            # Check for long path artifacts
            long_paths = []
            for file_path in build_dir.rglob("*"):
                if len(str(file_path)) > 200:  # Arbitrary long path threshold
                    long_paths.append(str(file_path))
            
            if long_paths:
                print(f"⚠️  Found {len(long_paths)} files with very long paths")
                print("💡 Solution: idf.py fullclean to remove build artifacts")
                
                # Auto-apply fix
                clean_result = self.run_command("idf.py fullclean", "Cleaning build directory")
                if clean_result and clean_result.returncode == 0:
                    self.log_result(
                        "long_paths",
                        "FIXED",
                        "Cleaned build directory with long paths",
                        "idf.py fullclean"
                    )
                    print("✅ Build directory cleaned")
            else:
                self.log_result("long_paths", "PASS", "No problematic long paths found")
        
        # Check CMake and build tools
        tools_check = [
            ("cmake", "CMake build system"),
            ("ninja", "Ninja build tool"),
            ("ccache", "Compiler cache (optional)")
        ]
        
        for tool, description in tools_check:
            tool_result = self.run_command(f"which {tool}")
            if tool_result and tool_result.returncode == 0:
                print(f"✅ {description} available")
                self.log_result(f"{tool}_available", "PASS", f"{tool} found")
            else:
                if tool == "ccache":
                    print(f"⚠️  {description} not available (optional)")
                    self.log_result(f"{tool}_available", "WARN", f"{tool} not found (optional)")
                else:
                    print(f"❌ {description} not available")
                    self.log_result(f"{tool}_available", "FAIL", f"{tool} not found")
        
        return True
    
    def check_openocd_issues(self):
        """Check OpenOCD debugging issues"""
        print("\n🔍 === OPENOCD DEBUGGING CHECK ===")
        print("From research document: OpenOCD permission and configuration issues")
        
        # Check OpenOCD availability
        openocd_result = self.run_command("which openocd")
        if not openocd_result or openocd_result.returncode != 0:
            print("❌ OpenOCD not found in PATH")
            self.log_result("openocd_available", "FAIL", "OpenOCD not in PATH")
            return False
        
        print("✅ OpenOCD available")
        
        # Check OpenOCD version
        version_result = self.run_command("openocd --version")
        if version_result and version_result.returncode == 0:
            version_info = version_result.stderr.split('\n')[0]  # OpenOCD prints version to stderr
            print(f"📋 OpenOCD version: {version_info}")
            self.log_result("openocd_version", "PASS", version_info)
        
        # Check for OpenOCD udev rules
        openocd_rules = [
            '/etc/udev/rules.d/60-openocd.rules',
            '/etc/udev/rules.d/99-openocd.rules'
        ]
        
        rules_exist = any(os.path.exists(rule) for rule in openocd_rules)
        if not rules_exist:
            print("⚠️  OpenOCD udev rules not found")
            print("💡 This may cause permission issues with JTAG adapters")
            
            # Create basic OpenOCD rules
            openocd_udev_content = '''# OpenOCD JTAG programmers
# Espressif USB JTAG
SUBSYSTEM=="usb", ATTRS{idVendor}=="303a", ATTRS{idProduct}=="1001", MODE="0666", GROUP="plugdev"
'''
            
            try:
                with open('temp_openocd_rules.txt', 'w') as f:
                    f.write(openocd_udev_content)
                
                fix_cmd = "sudo cp temp_openocd_rules.txt /etc/udev/rules.d/60-openocd.rules && sudo udevadm control --reload-rules"
                fix_result = self.run_command(fix_cmd, "Creating OpenOCD udev rules")
                
                if fix_result and fix_result.returncode == 0:
                    self.log_result(
                        "openocd_udev",
                        "FIXED",
                        "Created OpenOCD udev rules",
                        fix_cmd
                    )
                    print("✅ OpenOCD udev rules created")
                
                # Cleanup
                if os.path.exists('temp_openocd_rules.txt'):
                    os.remove('temp_openocd_rules.txt')
                    
            except Exception as e:
                self.log_result("openocd_udev", "FAIL", f"Could not create OpenOCD rules: {e}")
        else:
            self.log_result("openocd_udev", "PASS", "OpenOCD udev rules exist")
            print("✅ OpenOCD udev rules found")
        
        # Test OpenOCD configuration
        config_file = "tools/esp32c6_final.cfg"
        if os.path.exists(config_file):
            print(f"✅ OpenOCD config found: {config_file}")
            
            # Test OpenOCD startup (quick test)
            test_result = self.run_command(
                f"timeout 5 openocd -f {config_file} -c 'init; exit'",
                "Testing OpenOCD configuration",
                timeout=10
            )
            
            if test_result and test_result.returncode == 0:
                print("✅ OpenOCD configuration test passed")
                self.log_result("openocd_config", "PASS", "Configuration loads successfully")
            else:
                print("⚠️  OpenOCD configuration test failed")
                self.log_result("openocd_config", "FAIL", "Configuration issues detected")
        else:
            print(f"❌ OpenOCD config not found: {config_file}")
            self.log_result("openocd_config", "FAIL", "Configuration file missing")
        
        return True
    
    def check_monitor_issues(self):
        """Check serial monitor issues"""
        print("\n📡 === SERIAL MONITOR CHECK ===")
        print("From research document: Monitor output and baud rate issues")
        
        # Check for common baud rate issues
        print("🔍 Checking for common monitor issues...")
        
        # Check sdkconfig for XTAL frequency
        sdkconfig = Path("sdkconfig")
        if sdkconfig.exists():
            with open(sdkconfig, 'r') as f:
                config_content = f.read()
            
            xtal_configs = [
                'CONFIG_XTAL_FREQ_26',
                'CONFIG_XTAL_FREQ_40',
                'CONFIG_ESP32C6_DEFAULT_CPU_FREQ_MHZ'
            ]
            
            found_xtal = False
            for config in xtal_configs:
                if config in config_content:
                    print(f"✅ XTAL configuration found: {config}")
                    found_xtal = True
                    break
            
            if not found_xtal:
                print("⚠️  No XTAL frequency configuration found")
                print("💡 Check Component config -> Hardware Settings -> Main XTAL frequency")
                self.log_result("xtal_config", "WARN", "XTAL frequency not explicitly configured")
            else:
                self.log_result("xtal_config", "PASS", "XTAL frequency configured")
        
        # Check for native USB JTAG issues (ESP32-C6 specific)
        print("🔍 Checking ESP32-C6 native USB JTAG configuration...")
        print("💡 Note: If GPIO18/19 are reconfigured, native JTAG will stop working")
        print("💡 Recovery: Use separate UART port to flash known-good firmware")
        
        self.log_result("usb_jtag_warning", "INFO", "Native USB JTAG can be disabled by GPIO reconfiguration")
        
        return True
    
    def generate_comprehensive_report(self):
        """Generate comprehensive troubleshooting report"""
        print("\n📋 === COMPREHENSIVE TROUBLESHOOTING REPORT ===")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = self.logs_dir / f"troubleshooting_report_{timestamp}.json"
        
        # Detailed report
        report = {
            "timestamp": datetime.now().isoformat(),
            "system_info": {
                "os": os.uname().sysname,
                "release": os.uname().release,
                "cwd": os.getcwd(),
                "user": os.environ.get('USER', 'unknown')
            },
            "test_results": self.results,
            "fixes_applied": self.fixes_applied,
            "summary": {
                "total_tests": len(self.results),
                "passed": len([r for r in self.results.values() if r['status'] == 'PASS']),
                "failed": len([r for r in self.results.values() if r['status'] == 'FAIL']),
                "fixed": len([r for r in self.results.values() if r['status'] == 'FIXED']),
                "warnings": len([r for r in self.results.values() if r['status'] == 'WARN']),
                "fixes_count": len(self.fixes_applied)
            }
        }
        
        # Save JSON report
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        # Generate human-readable summary
        summary_file = self.logs_dir / f"troubleshooting_summary_{timestamp}.txt"
        with open(summary_file, 'w') as f:
            f.write("ESP32-C6 VESC Express Troubleshooting Report\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"Generated: {datetime.now().isoformat()}\n")
            f.write(f"System: {os.uname().sysname} {os.uname().release}\n")
            f.write(f"Directory: {os.getcwd()}\n\n")
            
            f.write("SUMMARY\n")
            f.write("-------\n")
            f.write(f"Total Tests: {report['summary']['total_tests']}\n")
            f.write(f"Passed: {report['summary']['passed']}\n")
            f.write(f"Failed: {report['summary']['failed']}\n")
            f.write(f"Fixed: {report['summary']['fixed']}\n")
            f.write(f"Warnings: {report['summary']['warnings']}\n")
            f.write(f"Auto-fixes Applied: {report['summary']['fixes_count']}\n\n")
            
            if self.fixes_applied:
                f.write("FIXES APPLIED\n")
                f.write("-------------\n")
                for i, fix in enumerate(self.fixes_applied, 1):
                    f.write(f"{i}. {fix}\n")
                f.write("\n")
            
            f.write("DETAILED RESULTS\n")
            f.write("----------------\n")
            for test_name, result in self.results.items():
                status_icon = {
                    'PASS': '✅',
                    'FAIL': '❌', 
                    'FIXED': '🔧',
                    'WARN': '⚠️',
                    'INFO': 'ℹ️'
                }.get(result['status'], '❓')
                
                f.write(f"{status_icon} {test_name}: {result['status']}\n")
                if result['details']:
                    f.write(f"   Details: {result['details']}\n")
                if result['fix_applied']:
                    f.write(f"   Fix: {result['fix_applied']}\n")
                f.write("\n")
        
        print(f"📄 Detailed report: {report_file}")
        print(f"📄 Summary report: {summary_file}")
        
        # Console summary
        summary = report['summary']
        print(f"\n🎯 TROUBLESHOOTING SUMMARY")
        print(f"   Total Tests: {summary['total_tests']}")
        print(f"   Passed: {summary['passed']} ✅")
        print(f"   Failed: {summary['failed']} ❌")
        print(f"   Fixed: {summary['fixed']} 🔧")
        print(f"   Warnings: {summary['warnings']} ⚠️")
        print(f"   Auto-fixes Applied: {summary['fixes_count']}")
        
        if self.fixes_applied:
            print(f"\n🔧 FIXES APPLIED:")
            for i, fix in enumerate(self.fixes_applied, 1):
                print(f"   {i}. {fix}")
        
        success_rate = (summary['passed'] + summary['fixed']) / summary['total_tests'] * 100
        print(f"\n📊 Overall Success Rate: {success_rate:.1f}%")
        
        return report_file
    
    def run_comprehensive_troubleshooting(self):
        """Run complete troubleshooting suite"""
        print("🎯 ESP32-C6 Comprehensive Troubleshooting Suite")
        print("=" * 55)
        print("Based on ESP-IDF research document troubleshooting section")
        print()
        
        # Run all troubleshooting checks
        self.check_device_permissions()
        self.check_esp_idf_environment()
        self.check_connection_issues()
        self.check_build_issues()
        self.check_openocd_issues()
        self.check_monitor_issues()
        
        # Generate comprehensive report
        report_file = self.generate_comprehensive_report()
        
        print("\n🎉 Comprehensive troubleshooting complete!")
        print("📚 All checks based on ESP-IDF research document")
        
        return report_file

def main():
    """Main troubleshooting function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='ESP32-C6 Comprehensive Troubleshooting')
    parser.add_argument('--permissions-only', action='store_true', help='Check permissions only')
    parser.add_argument('--environment-only', action='store_true', help='Check ESP-IDF environment only')
    parser.add_argument('--connection-only', action='store_true', help='Check device connection only')
    parser.add_argument('--auto-fix', action='store_true', help='Automatically apply fixes where possible')
    
    args = parser.parse_args()
    
    troubleshooter = ComprehensiveTroubleshooter()
    
    if args.permissions_only:
        troubleshooter.check_device_permissions()
    elif args.environment_only:
        troubleshooter.check_esp_idf_environment()
    elif args.connection_only:
        troubleshooter.check_connection_issues()
    else:
        troubleshooter.run_comprehensive_troubleshooting()

if __name__ == "__main__":
    main()