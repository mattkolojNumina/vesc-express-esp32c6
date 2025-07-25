#!/usr/bin/env python3
"""
ESP32-C6 GDB Debugging Automation Tool
Provides automated debugging workflows for ESP-IDF projects
"""

import os
import sys
import time
import json
import subprocess
import threading
from pathlib import Path
import argparse

class ESP32C6GDBAutomation:
    """
    ESP32-C6 GDB Debugging Automation Tool
    
    Provides automated GDB debugging with pre-configured profiles:
    - Interactive debugging sessions with breakpoints
    - Crash analysis and coredump handling  
    - Memory debugging with heap/stack monitoring
    - System monitoring and performance analysis
    """
    def __init__(self, project_path=None):
        self.project_path = project_path or os.getcwd()
        self.build_path = Path(self.project_path) / 'build'
        self.elf_file = self.build_path / 'project.elf'
        
        self.common_breakpoints = [
            'app_main',
            'esp_restart',
            'abort',
            'vTaskDelay',
            'esp_system_abort'
        ]
        
        self.gdb_init_commands = [
            'set confirm off',
            'set architecture riscv:rv32',
            'set print pretty on',
            'set print array on',
            'set print array-indexes on'
        ]

    def check_build(self):
        """Check if project is built and ELF file exists"""
        if not self.elf_file.exists():
            print(f"❌ ELF file not found: {self.elf_file}")
            print("💡 Build project first: idf.py build")
            return False
        
        print(f"✅ ELF file found: {self.elf_file}")
        return True

    def start_openocd(self, config_file='esp32c6_optimized.cfg'):
        """Start OpenOCD server in background"""
        config_path = Path(self.project_path) / config_file
        if not config_path.exists():
            print(f"❌ OpenOCD config not found: {config_path}")
            return None
        
        print("🚀 Starting OpenOCD server...")
        
        try:
            process = subprocess.Popen([
                'openocd', '-f', str(config_path)
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            
            # Wait for OpenOCD to start
            time.sleep(3)
            
            if process.poll() is None:  # Process is running
                print("✅ OpenOCD server started")
                return process
            else:
                print("❌ OpenOCD failed to start")
                stdout, stderr = process.communicate()
                print(f"Error: {stderr}")
                return None
                
        except FileNotFoundError:
            print("❌ OpenOCD not found. Ensure ESP-IDF is sourced.")
            return None

    def create_gdb_script(self, breakpoints=None, commands=None):
        """Create GDB initialization script"""
        breakpoints = breakpoints or self.common_breakpoints
        commands = commands or []
        
        script_path = Path(self.project_path) / 'gdbinit_esp32c6'
        
        with open(script_path, 'w') as f:
            # Basic setup
            f.write("# ESP32-C6 GDB Initialization Script\n\n")
            
            # Initial commands
            for cmd in self.gdb_init_commands:
                f.write(f"{cmd}\n")
            
            f.write(f"\n# Load ELF file\n")
            f.write(f"file {self.elf_file}\n")
            
            f.write(f"\n# Connect to target\n")
            f.write("target remote localhost:3333\n")
            
            f.write(f"\n# Reset and halt\n")
            f.write("monitor reset halt\n")
            
            # Set breakpoints
            if breakpoints:
                f.write(f"\n# Common breakpoints\n")
                for bp in breakpoints:
                    f.write(f"break {bp}\n")
            
            # Additional commands
            if commands:
                f.write(f"\n# Custom commands\n")
                for cmd in commands:
                    f.write(f"{cmd}\n")
            
            f.write(f"\n# Ready for debugging\n")
            f.write("echo \\n🐛 ESP32-C6 Debug Session Ready!\\n\n")
        
        print(f"✅ Created GDB script: {script_path}")
        return script_path

    def create_debug_profiles(self):
        """Create predefined debugging profiles"""
        profiles = {
            'basic': {
                'description': 'Basic debugging with app_main breakpoint',
                'breakpoints': ['app_main'],
                'commands': ['info registers']
            },
            'crash': {
                'description': 'Crash analysis debugging',
                'breakpoints': ['abort', 'esp_restart', 'esp_system_abort', '_esp_error_check_failed'],
                'commands': [
                    'set print symbol-filename on',
                    'bt',
                    'info registers'
                ]
            },
            'memory': {
                'description': 'Memory debugging and analysis',
                'breakpoints': ['malloc', 'free', 'heap_caps_malloc'],
                'commands': [
                    'info proc mappings',
                    'info heap',
                    'monitor esp heap_info'
                ]
            },
            'wifi': {
                'description': 'WiFi stack debugging',
                'breakpoints': ['wifi_init', 'esp_wifi_start', 'wifi_station_start'],
                'commands': [
                    'monitor esp wifi_info',
                    'info threads'
                ]
            },
            'freertos': {
                'description': 'FreeRTOS task debugging',
                'breakpoints': ['vTaskDelay', 'vTaskSuspend', 'xTaskCreate'],
                'commands': [
                    'info threads',
                    'thread apply all bt',
                    'monitor esp freertos_info'
                ]
            }
        }
        
        profiles_dir = Path(self.project_path) / 'debug_profiles'
        profiles_dir.mkdir(exist_ok=True)
        
        for name, profile in profiles.items():
            script_path = self.create_gdb_script(
                breakpoints=profile['breakpoints'],
                commands=profile['commands']
            )
            
            # Move to profiles directory
            new_path = profiles_dir / f'gdbinit_{name}'
            script_path.rename(new_path)
            
            print(f"✅ Profile '{name}': {profile['description']}")
        
        return profiles_dir

    def run_interactive_debug(self, profile='basic'):
        """Run interactive GDB debugging session"""
        if not self.check_build():
            return False
        
        # Start OpenOCD
        openocd_process = self.start_openocd()
        if not openocd_process:
            return False
        
        try:
            # Create GDB script for profile
            if profile == 'basic':
                gdb_script = self.create_gdb_script()
            else:
                profiles_dir = Path(self.project_path) / 'debug_profiles'
                gdb_script = profiles_dir / f'gdbinit_{profile}'
                if not gdb_script.exists():
                    print(f"❌ Profile '{profile}' not found")
                    return False
            
            # Start GDB
            print(f"🐛 Starting GDB with profile: {profile}")
            
            gdb_cmd = [
                'riscv32-esp-elf-gdb',
                '-x', str(gdb_script),
                str(self.elf_file)
            ]
            
            subprocess.run(gdb_cmd)
            
        finally:
            # Cleanup OpenOCD
            if openocd_process:
                print("🛑 Stopping OpenOCD...")
                openocd_process.terminate()
                openocd_process.wait()
        
        return True

    def analyze_coredump(self, coredump_file):
        """Analyze ESP32 coredump file"""
        if not Path(coredump_file).exists():
            print(f"❌ Coredump file not found: {coredump_file}")
            return False
        
        print(f"🔍 Analyzing coredump: {coredump_file}")
        
        try:
            # Use ESP-IDF coredump analysis tool
            result = subprocess.run([
                'esp-coredump', 'info_corefile',
                '-t', 'raw',
                '-c', coredump_file,
                str(self.elf_file)
            ], capture_output=True, text=True)
            
            print("📊 Coredump Analysis Results:")
            print("=" * 40)
            print(result.stdout)
            
            if result.stderr:
                print("⚠️ Warnings/Errors:")
                print(result.stderr)
            
            return True
            
        except FileNotFoundError:
            print("❌ esp-coredump tool not found")
            return False

    def monitor_system_info(self):
        """Monitor system information via OpenOCD"""
        openocd_process = self.start_openocd()
        if not openocd_process:
            return False
        
        try:
            time.sleep(2)  # Wait for OpenOCD to stabilize
            
            # Connect via telnet to OpenOCD
            import telnetlib
            
            tn = telnetlib.Telnet('localhost', 4444)
            
            commands = [
                'halt',
                'esp heap_info',
                'esp freertos_info', 
                'reg pc',
                'resume'
            ]
            
            print("📊 System Information:")
            print("=" * 40)
            
            for cmd in commands:
                tn.write(f"{cmd}\n".encode())
                time.sleep(1)
                response = tn.read_very_eager().decode()
                if response.strip():
                    print(f"🔧 {cmd}:")
                    print(response)
                    print("-" * 20)
            
            tn.close()
            
        except Exception as e:
            print(f"❌ System monitoring failed: {e}")
        
        finally:
            if openocd_process:
                openocd_process.terminate()
                openocd_process.wait()

    def create_automation_scripts(self):
        """Create automation scripts"""
        scripts_dir = Path(self.project_path) / 'debug_automation'
        scripts_dir.mkdir(exist_ok=True)
        
        # Quick debug script
        quick_debug = scripts_dir / 'quick_debug.py'
        with open(quick_debug, 'w') as f:
            f.write(f'''#!/usr/bin/env python3
# Quick ESP32-C6 Debug Script
import sys
import os
sys.path.append('{Path(__file__).parent.parent / "tools"}')

from esp32c6_gdb_automation import ESP32C6GDBAutomation

def main():
    debugger = ESP32C6GDBAutomation()
    debugger.run_interactive_debug('basic')

if __name__ == '__main__':
    main()
''')
        
        os.chmod(quick_debug, 0o755)
        
        # System monitor script
        monitor_script = scripts_dir / 'system_monitor.py'
        with open(monitor_script, 'w') as f:
            f.write(f'''#!/usr/bin/env python3
# ESP32-C6 System Monitor Script
import sys
sys.path.append('{Path(__file__).parent.parent / "tools"}')

from esp32c6_gdb_automation import ESP32C6GDBAutomation

def main():
    debugger = ESP32C6GDBAutomation()
    debugger.monitor_system_info()

if __name__ == '__main__':
    main()
''')
        
        os.chmod(monitor_script, 0o755)
        
        print(f"✅ Created automation scripts in: {scripts_dir}")
        return scripts_dir

def main():
    parser = argparse.ArgumentParser(description='ESP32-C6 GDB Automation Tool')
    parser.add_argument('--profile', choices=['basic', 'crash', 'memory', 'wifi', 'freertos'], 
                       default='basic', help='Debug profile to use')
    parser.add_argument('--create-profiles', action='store_true',
                       help='Create debug profiles')
    parser.add_argument('--coredump', type=str,
                       help='Analyze coredump file')
    parser.add_argument('--monitor', action='store_true',
                       help='Monitor system information')
    parser.add_argument('--project-path', type=str,
                       help='Project path (default: current directory)')
    
    args = parser.parse_args()
    
    debugger = ESP32C6GDBAutomation(args.project_path)
    
    if args.create_profiles:
        debugger.create_debug_profiles()
        debugger.create_automation_scripts()
        print("✅ Debug profiles and automation created!")
        return
    
    if args.coredump:
        debugger.analyze_coredump(args.coredump)
        return
    
    if args.monitor:
        debugger.monitor_system_info()
        return
    
    # Default: Run interactive debug
    success = debugger.run_interactive_debug(args.profile)
    sys.exit(0 if success else 1)

# CLI wrapper functions for entry points
def cli_main():
    """CLI wrapper for entry point compatibility - safe version that doesn't parse args"""
    # Don't call main() directly as it parses sys.argv
    debugger = ESP32C6GDBAutomation()
    print("🐛 ESP32-C6 GDB Automation Tool")
    print("💡 Use 'esp32-debug gdb-debug' for interactive debugging")
    return debugger

def run_debug_session_mcp(profile="basic"):
    """MCP wrapper for running debug session"""
    debugger = ESP32C6GDBAutomation()
    return debugger.run_interactive_debug(profile)

if __name__ == '__main__':
    main()