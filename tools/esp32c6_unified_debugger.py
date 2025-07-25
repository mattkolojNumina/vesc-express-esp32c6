#!/usr/bin/env python3
"""
ESP32-C6 Unified Debugging Workflow Tool
Combines all debugging tools into a single unified interface
"""

import os
import sys
import json
import time
import argparse
import subprocess
from pathlib import Path
from datetime import datetime

# Import our debugging modules
sys.path.append(str(Path(__file__).parent))
from esp32c6_openocd_setup import ESP32C6OpenOCDSetup
from esp32c6_gdb_automation import ESP32C6GDBAutomation
from esp32c6_memory_debug import ESP32C6MemoryDebugger
from wsl2_esp32_debug_setup import WSL2ESP32DebugSetup

class ESP32C6UnifiedDebugger:
    """
    ESP32-C6 Unified Debugging and Setup Wizard
    
    Comprehensive debugging environment management:
    - Interactive setup wizard for complete debugging environment
    - Environment validation and dependency checking
    - Integrated OpenOCD, GDB, and memory debugging workflows
    - Cross-platform support with WSL2 integration
    """
    def __init__(self, project_path=None):
        self.project_path = project_path or os.getcwd()
        self.config_file = Path(self.project_path) / 'debug_config.json'
        self.session_log = Path(self.project_path) / 'debug_session.log'
        
        # Set up ESP-IDF environment
        self._setup_esp_idf_environment()
        
        # Initialize component debuggers
        self.openocd_setup = ESP32C6OpenOCDSetup()
        self.gdb_automation = ESP32C6GDBAutomation(self.project_path)
        self.memory_debugger = ESP32C6MemoryDebugger(self.project_path)
        self.wsl2_setup = WSL2ESP32DebugSetup()
        
        self.load_config()
    
    def _setup_esp_idf_environment(self):
        """Set up ESP-IDF environment variables"""
        esp_idf_path = "/home/rds/esp/esp-idf"
        if os.path.exists(esp_idf_path):
            os.environ['IDF_PATH'] = esp_idf_path
            # Add ESP-IDF tools to PATH
            tools_path = f"{esp_idf_path}/tools"
            if tools_path not in os.environ.get('PATH', ''):
                os.environ['PATH'] = f"{tools_path}:{os.environ.get('PATH', '')}"

    def load_config(self):
        """Load debugging configuration"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    self.config = json.load(f)
            except (json.JSONDecodeError, FileNotFoundError, PermissionError) as e:
                print(f"⚠️  Config file corrupted ({e}), creating new one...")
                self.config = {
                    'openocd_config': 'esp32c6_optimized.cfg',
                    'default_debug_profile': 'basic',
                    'auto_setup_wsl2': True,
                    'enable_memory_debugging': True,
                    'session_history': []
                }
                self.save_config()
        else:
            self.config = {
                'openocd_config': 'esp32c6_optimized.cfg',
                'default_debug_profile': 'basic',
                'auto_setup_wsl2': True,
                'enable_memory_debugging': True,
                'session_history': []
            }
            self.save_config()

    def save_config(self):
        """Save debugging configuration"""
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)

    def log_session(self, action, details=None):
        """Log debugging session activity"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = {
            'timestamp': timestamp,
            'action': action,
            'details': details or {}
        }
        
        self.config['session_history'].append(log_entry)
        self.save_config()
        
        # Also write to session log file
        with open(self.session_log, 'a') as f:
            f.write(f"[{timestamp}] {action}: {details}\n")

    def check_environment(self):
        """Check debugging environment and dependencies"""
        print("🔍 Checking debugging environment...")
        
        checks = {
            'ESP-IDF': self.check_esp_idf(),
            'OpenOCD': self.check_openocd(),
            'GDB': self.check_gdb(),
            'Project Build': self.check_project_build(),
            'Device Connection': self.check_device_connection()
        }
        
        if self.wsl2_setup.is_wsl:
            checks['WSL2 Setup'] = self.check_wsl2_setup()
        
        print("\n📋 Environment Check Results:")
        print("=" * 40)
        
        all_good = True
        for check, result in checks.items():
            status = "✅" if result else "❌"
            print(f"{status} {check}")
            if not result:
                all_good = False
        
        self.log_session('environment_check', checks)
        return all_good

    def check_esp_idf(self):
        """Check ESP-IDF installation"""
        return bool(os.environ.get('IDF_PATH'))

    def check_openocd(self):
        """Check OpenOCD availability"""
        try:
            subprocess.run(['openocd', '--version'], capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError, OSError):
            return False

    def check_gdb(self):
        """Check GDB availability"""
        try:
            subprocess.run(['riscv32-esp-elf-gdb', '--version'], capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError, OSError):
            return False

    def check_project_build(self):
        """Check if project is built"""
        return (Path(self.project_path) / 'build' / 'project.elf').exists()

    def check_device_connection(self):
        """Check ESP32-C6 device connection"""
        return self.openocd_setup.detect_esp32c6()

    def check_wsl2_setup(self):
        """Check WSL2 debugging setup"""
        return self.wsl2_setup.verify_wsl_device_access()

    def setup_debugging_environment(self):
        """Setup complete debugging environment"""
        print("🏗️  Setting up debugging environment...")
        
        # Step 1: WSL2 setup if needed
        if self.wsl2_setup.is_wsl and self.config['auto_setup_wsl2']:
            print("\n1️⃣ Setting up WSL2 environment...")
            if not self.wsl2_setup.run_full_setup():
                print("❌ WSL2 setup failed")
                return False
        
        # Step 2: OpenOCD configuration
        print("\n2️⃣ Setting up OpenOCD...")
        if not self.openocd_setup.run_full_setup('optimized', test_connection=True):
            print("❌ OpenOCD setup failed")
            return False
        
        # Step 3: GDB automation setup
        print("\n3️⃣ Creating GDB debugging profiles...")
        self.gdb_automation.create_debug_profiles()
        self.gdb_automation.create_automation_scripts()
        
        # Step 4: Memory debugging tools
        if self.config['enable_memory_debugging']:
            print("\n4️⃣ Setting up memory debugging...")
            self.memory_debugger.create_memory_debugging_tools()
        
        print("\n✅ Debugging environment setup complete!")
        self.log_session('environment_setup', {'success': True})
        return True

    def interactive_debug_menu(self):
        """Interactive debugging menu"""
        while True:
            print("\n🐛 ESP32-C6 Unified Debugger")
            print("=" * 40)
            print("1. Quick Debug Session (basic)")
            print("2. Memory Debugging") 
            print("3. Crash Analysis")
            print("4. WiFi Stack Debugging")
            print("5. FreeRTOS Task Debugging")
            print("6. System Information Monitor")
            print("7. Memory Fragmentation Analysis")
            print("8. Environment Check")
            print("9. Setup Debugging Environment")
            print("0. Exit")
            
            try:
                choice = input("\nSelect option (0-9): ").strip()
                
                if choice == '0':
                    break
                elif choice == '1':
                    self.run_debug_session('basic')
                elif choice == '2':
                    self.run_debug_session('memory')
                elif choice == '3':
                    self.run_debug_session('crash')
                elif choice == '4':
                    self.run_debug_session('wifi')
                elif choice == '5':
                    self.run_debug_session('freertos')
                elif choice == '6':
                    self.monitor_system_info()
                elif choice == '7':
                    self.analyze_memory_fragmentation()
                elif choice == '8':
                    self.check_environment()
                elif choice == '9':
                    self.setup_debugging_environment()
                else:
                    print("❌ Invalid option")
                    
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except EOFError:
                break

    def run_debug_session(self, profile='basic'):
        """Run debugging session with specified profile"""
        print(f"🚀 Starting debug session: {profile}")
        
        self.log_session('debug_session_start', {'profile': profile})
        
        try:
            success = self.gdb_automation.run_interactive_debug(profile)
            
            self.log_session('debug_session_end', {
                'profile': profile,
                'success': success
            })
            
            if success:
                print("✅ Debug session completed")
            else:
                print("❌ Debug session failed")
                
        except KeyboardInterrupt:
            print("\n🛑 Debug session interrupted")
            self.log_session('debug_session_interrupted', {'profile': profile})

    def monitor_system_info(self):
        """Monitor system information"""
        print("📊 Monitoring system information...")
        self.log_session('system_monitor_start')
        
        try:
            self.gdb_automation.monitor_system_info()
            self.log_session('system_monitor_complete')
        except Exception as e:
            print(f"❌ System monitoring failed: {e}")
            self.log_session('system_monitor_failed', {'error': str(e)})

    def analyze_memory_fragmentation(self):
        """Analyze memory fragmentation"""
        print("🧠 Analyzing memory fragmentation...")
        self.log_session('memory_analysis_start')
        
        try:
            self.memory_debugger.analyze_memory_fragmentation()
            self.log_session('memory_analysis_complete')
        except Exception as e:
            print(f"❌ Memory analysis failed: {e}")
            self.log_session('memory_analysis_failed', {'error': str(e)})

    def generate_debug_report(self):
        """Generate comprehensive debugging report"""
        print("📋 Generating debugging report...")
        
        report_path = Path(self.project_path) / f'debug_report_{int(time.time())}.json'
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'project_path': str(self.project_path),
            'environment_check': {},
            'session_history': self.config['session_history'][-10:],  # Last 10 sessions
            'configuration': self.config.copy()
        }
        
        # Remove sensitive data
        if 'session_history' in report['configuration']:
            del report['configuration']['session_history']
        
        # Add environment check
        report['environment_check'] = {
            'ESP-IDF': self.check_esp_idf(),
            'OpenOCD': self.check_openocd(),
            'GDB': self.check_gdb(),
            'Project Build': self.check_project_build(),
            'Device Connection': self.check_device_connection()
        }
        
        if self.wsl2_setup.is_wsl:
            report['environment_check']['WSL2'] = self.check_wsl2_setup()
        
        # Add memory analysis if available
        try:
            memory_report_path = self.memory_debugger.generate_memory_report()
            if memory_report_path.exists():
                with open(memory_report_path, 'r') as f:
                    report['memory_analysis'] = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError, AttributeError, OSError) as e:
            # Memory report generation failed - not critical
            print(f"Warning: Could not include memory analysis in report: {e}")
        
        # Save report
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"✅ Debug report saved: {report_path}")
        self.log_session('debug_report_generated', {'report_path': str(report_path)})
        
        return report_path

    def quick_start_wizard(self):
        """Quick start wizard for first-time setup"""
        print("🧙 ESP32-C6 Debugging Quick Start Wizard")
        print("=" * 50)
        
        # Step 1: Environment check
        print("\n1️⃣ Checking environment...")
        if not self.check_environment():
            print("\n❌ Environment issues detected. Setting up...")
            if not self.setup_debugging_environment():
                print("❌ Setup failed. Please check manually.")
                return False
        
        # Step 2: Test basic debugging
        print("\n2️⃣ Testing basic debugging...")
        if not self.gdb_automation.check_build():
            print("💡 Building project...")
            try:
                subprocess.run(['idf.py', 'build'], cwd=self.project_path, check=True)
            except (subprocess.CalledProcessError, FileNotFoundError, OSError) as e:
                print(f"❌ Build failed: {e}. Please build manually: idf.py build")
                return False
        
        # Step 3: Quick debug test
        print("\n3️⃣ Running quick debug test...")
        
        # Create a minimal test instead of full interactive session
        openocd_process = self.gdb_automation.start_openocd()
        if openocd_process:
            print("✅ OpenOCD connection successful")
            openocd_process.terminate()
            openocd_process.wait()
        else:
            print("❌ OpenOCD connection failed")
            return False
        
        print("\n🎉 Quick start wizard completed successfully!")
        print("📚 Available debugging options:")
        print("   - Interactive menu: python3 tools/esp32c6_unified_debugger.py --interactive")
        print("   - Quick debug: python3 tools/esp32c6_unified_debugger.py --profile basic")
        print("   - Memory analysis: python3 tools/esp32c6_unified_debugger.py --memory")
        print("   - WiFi status: python3 tools/esp32c6_unified_debugger.py --wifi-status")
        print("   - Monitor device: python3 tools/esp32c6_unified_debugger.py --monitor")
        
        return True
    
    def get_wifi_status(self):
        """Get WiFi connection status and IP address using serial monitoring"""
        print("🔍 Getting WiFi status from ESP32-C6...")
        
        try:
            import serial
            import time
            from datetime import datetime
            
            # Find serial device
            serial_device = self._find_serial_device()
            if not serial_device:
                print("❌ No serial device found")
                return False
            
            print(f"📡 Monitoring {serial_device} for WiFi status...")
            
            with serial.Serial(serial_device, 115200, timeout=2) as ser:
                wifi_info = {'connected': False, 'ip': None, 'mode': None}
                start_time = time.time()
                
                while time.time() - start_time < 30:  # Monitor for 30 seconds
                    if ser.in_waiting:
                        line = ser.readline().decode('utf-8', errors='ignore').strip()
                        if line:
                            line_lower = line.lower()
                            
                            # Look for WiFi connection indicators
                            if 'connected to network' in line_lower or 'wifi connected' in line_lower:
                                wifi_info['connected'] = True
                                print(f"✅ WiFi Connected: {line}")
                            
                            # Look for IP address
                            if 'ip_event_sta_got_ip' in line_lower or 'got ip' in line_lower:
                                # Extract IP from line
                                import re
                                ip_match = re.search(r'(\d+\.\d+\.\d+\.\d+)', line)
                                if ip_match:
                                    wifi_info['ip'] = ip_match.group(1)
                                    print(f"🔧 IP Address: {wifi_info['ip']}")
                            
                            # Look for AP mode
                            if 'ap mode' in line_lower or 'access point' in line_lower:
                                wifi_info['mode'] = 'AP'
                                print(f"📡 Mode: Access Point")
                            
                            # Look for station mode
                            if 'sta mode' in line_lower or 'station' in line_lower:
                                wifi_info['mode'] = 'STA'
                                print(f"📡 Mode: Station")
                    else:
                        time.sleep(0.1)
                
                # Summary
                print("\n📊 WiFi Status Summary:")
                print(f"Connected: {'✅ Yes' if wifi_info['connected'] else '❌ No'}")
                if wifi_info['ip']:
                    print(f"IP Address: {wifi_info['ip']}")
                if wifi_info['mode']:
                    print(f"Mode: {wifi_info['mode']}")
                
                return wifi_info
                
        except Exception as e:
            print(f"❌ Error getting WiFi status: {e}")
            return False
    
    def get_system_info(self):
        """Get system information from device"""
        print("📊 Getting system information...")
        return self.get_wifi_status()
    
    def monitor_device(self):
        """Monitor device serial output"""
        print("📡 Starting device monitoring...")
        
        try:
            serial_device = self._find_serial_device()
            if not serial_device:
                print("❌ No serial device found")
                return False
            
            # Use the esp32_debug_monitor.py
            import subprocess
            monitor_script = str(Path(self.project_path) / 'tools' / 'esp32_debug_monitor.py')
            if os.path.exists(monitor_script):
                subprocess.run(['python3', monitor_script, serial_device])
            else:
                print(f"❌ Monitor script not found: {monitor_script}")
                return False
                
        except Exception as e:
            print(f"❌ Error starting monitor: {e}")
            return False
    
    def test_debug_ports(self):
        """Test debug port connectivity"""
        print("🔧 Testing debug port connectivity...")
        
        # Test serial port
        serial_device = self._find_serial_device()
        if serial_device:
            print(f"✅ Serial port available: {serial_device}")
        else:
            print("❌ No serial port found")
            return False
        
        # Test if WiFi debug ports are accessible
        wifi_info = self.get_wifi_status()
        if wifi_info and wifi_info.get('ip'):
            print(f"✅ WiFi debugging system verified with IP: {wifi_info['ip']}")
            
            # Test debug ports
            import socket
            ports_to_test = [23456, 80, 65102]
            for port in ports_to_test:
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(3)
                    result = sock.connect_ex((wifi_info['ip'], port))
                    if result == 0:
                        print(f"✅ Port {port} is accessible")
                    else:
                        print(f"❌ Port {port} is not accessible")
                    sock.close()
                except Exception as e:
                    print(f"❌ Error testing port {port}: {e}")
        else:
            print("⚠️  WiFi IP not found - cannot test network debug ports")
        
        return True
    
    def reset_and_monitor(self):
        """Reset ESP32-C6 and monitor boot messages to capture WiFi status"""
        print("🔄 Resetting ESP32-C6 and monitoring boot messages...")
        
        try:
            import serial
            import time
            from datetime import datetime
            
            # Find serial device
            serial_device = self._find_serial_device()
            if not serial_device:
                print("❌ No serial device found")
                return False
            
            print(f"📡 Using serial device: {serial_device}")
            
            with serial.Serial(serial_device, 115200, timeout=1) as ser:
                # Clear any existing data
                ser.reset_input_buffer()
                
                print("🔄 Triggering ESP32-C6 reset...")
                
                # Send reset signal (DTR low -> high)
                ser.setDTR(False)
                time.sleep(0.1)
                ser.setDTR(True)
                time.sleep(0.1)
                ser.setDTR(False)
                
                print("📡 Monitoring boot messages for WiFi debugging status...")
                
                wifi_info = {'connected': False, 'ip': None, 'mode': None, 'debug_services': []}
                start_time = time.time()
                message_count = 0
                
                while time.time() - start_time < 45:  # Monitor for 45 seconds after reset
                    if ser.in_waiting:
                        line = ser.readline().decode('utf-8', errors='ignore').strip()
                        if line:
                            message_count += 1
                            timestamp = datetime.now().strftime('%H:%M:%S.%f')[:-3]
                            line_lower = line.lower()
                            
                            # Look for WiFi connection indicators
                            if any(phrase in line_lower for phrase in ['connected to network', 'wifi connected', 'sta got ip']):
                                wifi_info['connected'] = True
                                print(f"✅ [{timestamp}] WiFi Connected: {line}")
                            
                            # Look for IP address
                            elif 'ip_event_sta_got_ip' in line_lower or 'got ip' in line_lower:
                                import re
                                ip_match = re.search(r'(\d+\.\d+\.\d+\.\d+)', line)
                                if ip_match:
                                    wifi_info['ip'] = ip_match.group(1)
                                    print(f"🔧 [{timestamp}] IP Address: {wifi_info['ip']}")
                            
                            # Look for WiFi debug initialization
                            elif any(phrase in line_lower for phrase in ['debug_wifi_delayed_init', 'wifi debugging', 'delayed wifi']):
                                print(f"🔧 [{timestamp}] WiFi Debug Init: {line}")
                                wifi_info['debug_services'].append('WiFi Debug Init')
                            
                            # Look for debug servers starting
                            elif any(phrase in line for phrase in ['port 23456', 'port 80', 'port 65102']):
                                print(f"🔧 [{timestamp}] Debug Port: {line}")
                                if 'port 23456' in line:
                                    wifi_info['debug_services'].append('TCP Debug Server (23456)')
                                elif 'port 80' in line:
                                    wifi_info['debug_services'].append('HTTP Server (80)')
                                elif 'port 65102' in line:
                                    wifi_info['debug_services'].append('VESC TCP (65102)')
                            
                            # Look for AP mode
                            elif any(phrase in line_lower for phrase in ['ap mode', 'access point', 'vesc wifi']):
                                wifi_info['mode'] = 'AP'
                                print(f"📡 [{timestamp}] AP Mode: {line}")
                            
                            # Look for station mode
                            elif 'sta mode' in line_lower or 'station' in line_lower:
                                wifi_info['mode'] = 'STA'
                                print(f"📡 [{timestamp}] STA Mode: {line}")
                            
                            # Show other important messages
                            elif any(keyword in line_lower for keyword in ['error', 'fail', 'warning']) and 'wifi' in line_lower:
                                print(f"⚠️  [{timestamp}] WiFi Issue: {line}")
                            
                            # Show periodic status
                            elif message_count % 100 == 0:
                                print(f"📊 [{timestamp}] Processed {message_count} boot messages...")
                    else:
                        time.sleep(0.1)
                
                # Final summary
                print(f"\n📊 Reset and Boot Analysis Complete ({message_count} messages)")
                print("=" * 60)
                print(f"WiFi Connected: {'✅ Yes' if wifi_info['connected'] else '❌ No'}")
                if wifi_info['ip']:
                    print(f"IP Address: {wifi_info['ip']}")
                if wifi_info['mode']:
                    print(f"WiFi Mode: {wifi_info['mode']}")
                if wifi_info['debug_services']:
                    print("Debug Services:")
                    for service in wifi_info['debug_services']:
                        print(f"  ✅ {service}")
                
                return wifi_info
                
        except Exception as e:
            print(f"❌ Error during reset and monitor: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _find_serial_device(self):
        """Find ESP32-C6 serial device"""
        import glob
        for pattern in ['/dev/ttyACM*', '/dev/ttyUSB*']:
            devices = glob.glob(pattern)
            if devices:
                return devices[0]
        return None

def main():
    parser = argparse.ArgumentParser(description='ESP32-C6 Unified Debugging Tool')
    parser.add_argument('--interactive', action='store_true',
                       help='Start interactive debugging menu')
    parser.add_argument('--profile', choices=['basic', 'crash', 'memory', 'wifi', 'freertos'],
                       help='Run debug session with specified profile')
    parser.add_argument('--setup', action='store_true',
                       help='Setup debugging environment')
    parser.add_argument('--check', action='store_true',
                       help='Check environment only')
    parser.add_argument('--memory', action='store_true',
                       help='Analyze memory fragmentation')
    parser.add_argument('--report', action='store_true',
                       help='Generate debugging report')
    parser.add_argument('--wizard', action='store_true',
                       help='Run quick start wizard')
    parser.add_argument('--project-path', type=str,
                       help='Project path (default: current directory)')
    parser.add_argument('--wifi-status', action='store_true', 
                       help='Get WiFi connection status and IP address')
    parser.add_argument('--system-info', action='store_true',
                       help='Get system information from device')
    parser.add_argument('--monitor', action='store_true',
                       help='Monitor device serial output')
    parser.add_argument('--debug-ports', action='store_true',
                       help='Test debug port connectivity')
    parser.add_argument('--reset', action='store_true',
                       help='Reset device and monitor boot messages')
    
    args = parser.parse_args()
    
    debugger = ESP32C6UnifiedDebugger(args.project_path)
    
    if args.wizard:
        debugger.quick_start_wizard()
        return
    
    if args.setup:
        debugger.setup_debugging_environment()
        return
    
    if args.check:
        debugger.check_environment()
        return
    
    if args.memory:
        debugger.analyze_memory_fragmentation()
        return
    
    if args.report:
        debugger.generate_debug_report()
        return
    
    if args.profile:
        debugger.run_debug_session(args.profile)
        return
    
    if args.wifi_status:
        debugger.get_wifi_status()
        return
        
    if args.system_info:
        debugger.get_system_info()
        return
        
    if args.monitor:
        debugger.monitor_device()
        return
        
    if args.debug_ports:
        debugger.test_debug_ports()
        return
        
    if args.reset:
        debugger.reset_and_monitor()
        return
    
    if args.interactive:
        debugger.interactive_debug_menu()
        return
    
    # Default: Run wizard
    print("🚀 ESP32-C6 Unified Debugger")
    print("💡 Use --help to see all options")
    print("🧙 Running quick start wizard...")
    debugger.quick_start_wizard()

# CLI wrapper functions for entry points
def cli_main():
    """CLI wrapper for entry point compatibility - safe version that doesn't parse args"""
    # Don't call main() directly as it parses sys.argv
    debugger = ESP32C6UnifiedDebugger()
    print("🚀 ESP32-C6 Unified Debugger")
    print("💡 Use 'esp32-debug wizard' for interactive wizard")
    return debugger

def quick_start_wizard_mcp():
    """MCP wrapper for quick start wizard"""
    debugger = ESP32C6UnifiedDebugger()
    return debugger.quick_start_wizard()

if __name__ == '__main__':
    main()