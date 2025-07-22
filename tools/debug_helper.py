#!/usr/bin/env python3
"""
ESP32-C6 VESC Express Debug Helper
Simplified hardware debugging and verification tool
"""

import subprocess
import sys
import time
import serial
import json
import os
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple
import threading
import queue

@dataclass
class DebugSession:
    """Debug session configuration"""
    target: str = "esp32c6"
    port: str = "/dev/ttyACM0"
    baud: int = 115200
    openocd_config: str = "esp32c6_wsl2.cfg"
    timeout: int = 30

class VESCDebugHelper:
    """Main debugging helper class"""
    
    def __init__(self, config: DebugSession = None):
        self.config = config or DebugSession()
        self.project_root = Path(__file__).parent.parent
        self.logs_dir = self.project_root / "logs"
        self.logs_dir.mkdir(exist_ok=True)
        
    def log(self, message: str, level: str = "INFO"):
        """Enhanced logging with timestamps"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {level}: {message}"
        print(log_entry)
        
        # Write to log file
        log_file = self.logs_dir / f"debug_{datetime.now().strftime('%Y%m%d')}.log"
        with open(log_file, "a") as f:
            f.write(log_entry + "\n")
    
    def check_environment(self) -> Dict[str, bool]:
        """Verify development environment setup"""
        self.log("🔍 Checking development environment...")
        
        checks = {
            "ESP-IDF": self._check_esp_idf(),
            "ESP32-C6 Device": self._check_device_connection(),
            "OpenOCD": self._check_openocd(),
            "Build System": self._check_build_system(),
            "Git Repository": self._check_git_status()
        }
        
        for name, status in checks.items():
            status_icon = "✅" if status else "❌"
            self.log(f"{status_icon} {name}: {'OK' if status else 'FAILED'}")
        
        return checks
    
    def _check_esp_idf(self) -> bool:
        """Check ESP-IDF installation and version"""
        try:
            result = subprocess.run(
                ". $HOME/esp/esp-idf/export.sh && idf.py --version",
                shell=True, capture_output=True, text=True
            )
            if result.returncode == 0:
                version_info = result.stdout.strip()
                self.log(f"ESP-IDF version: {version_info}")
                return "v5." in version_info  # Check for v5.x
            return False
        except Exception as e:
            self.log(f"ESP-IDF check failed: {e}", "ERROR")
            return False
    
    def _check_device_connection(self) -> bool:
        """Check ESP32-C6 device connection"""
        try:
            if not os.path.exists(self.config.port):
                return False
            
            # Try to get device info
            result = subprocess.run([
                "lsusb", "-d", "303a:1001"
            ], capture_output=True, text=True)
            
            return "Espressif" in result.stdout
        except Exception:
            return False
    
    def _check_openocd(self) -> bool:
        """Check OpenOCD availability"""
        try:
            result = subprocess.run(
                ["which", "openocd"], capture_output=True
            )
            return result.returncode == 0
        except Exception:
            return False
    
    def _check_build_system(self) -> bool:
        """Check build system status"""
        try:
            build_dir = self.project_root / "build"
            return build_dir.exists() and (build_dir / "vesc_express.elf").exists()
        except Exception:
            return False
    
    def _check_git_status(self) -> bool:
        """Check git repository status"""
        try:
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            return result.returncode == 0
        except Exception:
            return False
    
    def build_firmware(self, clean: bool = False) -> bool:
        """Build firmware with enhanced error handling"""
        self.log("🔨 Building firmware...")
        
        try:
            commands = []
            if clean:
                commands.append("idf.py fullclean")
            commands.append("idf.py build")
            
            for cmd in commands:
                self.log(f"Executing: {cmd}")
                result = subprocess.run(
                    f". $HOME/esp/esp-idf/export.sh && {cmd}",
                    shell=True,
                    cwd=self.project_root,
                    capture_output=True,
                    text=True
                )
                
                if result.returncode != 0:
                    self.log(f"Build failed: {result.stderr}", "ERROR")
                    return False
                
                self.log("Build step completed successfully")
            
            # Verify build artifacts
            build_dir = self.project_root / "build"
            elf_file = build_dir / "vesc_express.elf"
            bin_file = build_dir / "vesc_express.bin"
            
            if elf_file.exists() and bin_file.exists():
                elf_size = elf_file.stat().st_size
                bin_size = bin_file.stat().st_size
                self.log(f"Build artifacts: ELF {elf_size:,} bytes, BIN {bin_size:,} bytes")
                return True
            else:
                self.log("Build artifacts missing", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"Build error: {e}", "ERROR")
            return False
    
    def flash_firmware(self) -> bool:
        """Flash firmware with verification"""
        self.log("⚡ Flashing firmware to ESP32-C6...")
        
        try:
            flash_cmd = f". $HOME/esp/esp-idf/export.sh && idf.py flash -p {self.config.port}"
            
            result = subprocess.run(
                flash_cmd,
                shell=True,
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                self.log("Flash completed successfully")
                # Parse flash output for verification
                if "Hash of data verified" in result.stdout:
                    self.log("✅ Flash verification passed")
                    return True
                else:
                    self.log("⚠️ Flash verification status unclear")
                    return True
            else:
                self.log(f"Flash failed: {result.stderr}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"Flash error: {e}", "ERROR")
            return False
    
    def start_serial_monitor(self, duration: int = 30) -> List[str]:
        """Capture serial output with parsing"""
        self.log(f"📊 Starting serial monitor for {duration}s...")
        
        lines = []
        try:
            with serial.Serial(self.config.port, self.config.baud, timeout=1) as ser:
                start_time = time.time()
                
                while time.time() - start_time < duration:
                    try:
                        line = ser.readline().decode('utf-8', errors='ignore').strip()
                        if line:
                            timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
                            formatted_line = f"[{timestamp}] {line}"
                            lines.append(formatted_line)
                            print(formatted_line)
                    except Exception:
                        continue
                        
        except Exception as e:
            self.log(f"Serial monitor error: {e}", "ERROR")
        
        # Save to file
        if lines:
            log_file = self.logs_dir / f"serial_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
            with open(log_file, "w") as f:
                f.write("\n".join(lines))
            self.log(f"Serial output saved to {log_file}")
        
        return lines
    
    def start_openocd_session(self) -> Optional[subprocess.Popen]:
        """Start OpenOCD for hardware debugging"""
        self.log("🔧 Starting OpenOCD session...")
        
        try:
            config_file = self.project_root / self.config.openocd_config
            if not config_file.exists():
                self.log(f"OpenOCD config not found: {config_file}", "ERROR")
                return None
            
            cmd = ["openocd", "-f", str(config_file)]
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Give OpenOCD time to start
            time.sleep(3)
            
            if process.poll() is None:
                self.log("OpenOCD started successfully")
                return process
            else:
                stdout, stderr = process.communicate()
                self.log(f"OpenOCD failed to start: {stderr}", "ERROR")
                return None
                
        except Exception as e:
            self.log(f"OpenOCD start error: {e}", "ERROR")
            return None
    
    def run_gdb_commands(self, commands: List[str]) -> Dict[str, str]:
        """Execute GDB commands for hardware debugging"""
        self.log("🐛 Running GDB commands...")
        
        results = {}
        
        try:
            # Create temporary GDB script
            gdb_script = self.project_root / "temp_debug.gdb"
            
            with open(gdb_script, "w") as f:
                f.write("target extended-remote localhost:3333\n")
                for cmd in commands:
                    f.write(f"{cmd}\n")
                f.write("quit\n")
            
            # Run GDB
            gdb_cmd = [
                "riscv32-esp-elf-gdb",
                "-batch",
                "-x", str(gdb_script),
                str(self.project_root / "build" / "vesc_express.elf")
            ]
            
            result = subprocess.run(
                gdb_cmd,
                capture_output=True,
                text=True,
                cwd=self.project_root
            )
            
            if result.returncode == 0:
                results["stdout"] = result.stdout
                results["stderr"] = result.stderr
                self.log("GDB commands completed successfully")
            else:
                self.log(f"GDB commands failed: {result.stderr}", "ERROR")
                results["error"] = result.stderr
            
            # Cleanup
            if gdb_script.exists():
                gdb_script.unlink()
            
        except Exception as e:
            self.log(f"GDB error: {e}", "ERROR")
            results["error"] = str(e)
        
        return results
    
    def analyze_boot_sequence(self, serial_output: List[str]) -> Dict[str, any]:
        """Analyze boot sequence for issues"""
        self.log("🔍 Analyzing boot sequence...")
        
        analysis = {
            "boot_successful": False,
            "services_started": [],
            "errors_found": [],
            "warnings_found": [],
            "boot_time": None,
            "memory_info": {}
        }
        
        for line in serial_output:
            line_content = line.split("] ", 1)[-1] if "] " in line else line
            
            # Check for successful services
            if "wifi_manager_init" in line_content.lower():
                analysis["services_started"].append("WiFi Manager")
            elif "ble" in line_content.lower() and "init" in line_content.lower():
                analysis["services_started"].append("BLE Controller")
            elif "vesc_express ready" in line_content.lower():
                analysis["boot_successful"] = True
            
            # Check for errors
            if any(error in line_content.lower() for error in ["error", "fail", "abort", "exception"]):
                analysis["errors_found"].append(line_content)
            
            # Check for warnings
            if "warning" in line_content.lower():
                analysis["warnings_found"].append(line_content)
            
            # Extract memory information
            if "free heap" in line_content.lower():
                try:
                    heap_size = int([x for x in line_content.split() if x.isdigit()][-1])
                    analysis["memory_info"]["free_heap"] = heap_size
                except:
                    pass
        
        # Generate summary
        self.log(f"Boot Analysis: {'✅ SUCCESS' if analysis['boot_successful'] else '❌ FAILED'}")
        self.log(f"Services Started: {len(analysis['services_started'])}")
        self.log(f"Errors Found: {len(analysis['errors_found'])}")
        self.log(f"Warnings Found: {len(analysis['warnings_found'])}")
        
        return analysis
    
    def run_comprehensive_test(self) -> Dict[str, any]:
        """Run comprehensive hardware verification"""
        self.log("🚀 Starting comprehensive hardware verification...")
        
        test_results = {
            "timestamp": datetime.now().isoformat(),
            "environment_check": None,
            "build_success": False,
            "flash_success": False,
            "boot_analysis": None,
            "hardware_debug": None,
            "overall_status": "FAILED"
        }
        
        try:
            # 1. Environment Check
            test_results["environment_check"] = self.check_environment()
            
            # 2. Build firmware
            test_results["build_success"] = self.build_firmware()
            if not test_results["build_success"]:
                self.log("❌ Build failed, stopping test", "ERROR")
                return test_results
            
            # 3. Flash firmware
            test_results["flash_success"] = self.flash_firmware()
            if not test_results["flash_success"]:
                self.log("❌ Flash failed, stopping test", "ERROR")
                return test_results
            
            # 4. Monitor boot sequence
            serial_output = self.start_serial_monitor(duration=15)
            test_results["boot_analysis"] = self.analyze_boot_sequence(serial_output)
            
            # 5. Hardware debugging
            openocd_process = self.start_openocd_session()
            if openocd_process:
                try:
                    gdb_commands = [
                        "info registers",
                        "info memory",
                        "monitor esp32c6 cpu count"
                    ]
                    test_results["hardware_debug"] = self.run_gdb_commands(gdb_commands)
                finally:
                    openocd_process.terminate()
                    openocd_process.wait(timeout=5)
            
            # 6. Overall assessment
            if (test_results["build_success"] and 
                test_results["flash_success"] and 
                test_results["boot_analysis"]["boot_successful"]):
                test_results["overall_status"] = "PASSED"
                self.log("🎉 Comprehensive test PASSED!")
            else:
                self.log("❌ Comprehensive test FAILED")
            
        except Exception as e:
            self.log(f"Test execution error: {e}", "ERROR")
            test_results["error"] = str(e)
        
        # Save results
        results_file = self.logs_dir / f"test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(results_file, "w") as f:
            json.dump(test_results, f, indent=2, default=str)
        
        self.log(f"Test results saved to {results_file}")
        
        return test_results

def main():
    """Main entry point for debug helper"""
    import argparse
    
    parser = argparse.ArgumentParser(description="ESP32-C6 VESC Express Debug Helper")
    parser.add_argument("--port", default="/dev/ttyACM0", help="Serial port")
    parser.add_argument("--config", default="esp32c6_wsl2.cfg", help="OpenOCD config")
    parser.add_argument("--test", action="store_true", help="Run comprehensive test")
    parser.add_argument("--build", action="store_true", help="Build firmware only")
    parser.add_argument("--flash", action="store_true", help="Flash firmware only")
    parser.add_argument("--monitor", type=int, metavar="SECONDS", help="Monitor serial output")
    parser.add_argument("--check", action="store_true", help="Check environment only")
    
    args = parser.parse_args()
    
    # Create debug session
    config = DebugSession(
        port=args.port,
        openocd_config=args.config
    )
    
    helper = VESCDebugHelper(config)
    
    try:
        if args.check:
            helper.check_environment()
        elif args.build:
            helper.build_firmware()
        elif args.flash:
            helper.flash_firmware()
        elif args.monitor:
            helper.start_serial_monitor(args.monitor)
        elif args.test:
            results = helper.run_comprehensive_test()
            print(f"\n🏁 Final Status: {results['overall_status']}")
        else:
            print("Use --help for usage information")
            
    except KeyboardInterrupt:
        helper.log("🛑 Operation cancelled by user")
    except Exception as e:
        helper.log(f"💥 Unexpected error: {e}", "ERROR")
        sys.exit(1)

if __name__ == "__main__":
    main()