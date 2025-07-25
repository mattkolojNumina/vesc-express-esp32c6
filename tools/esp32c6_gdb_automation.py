#!/usr/bin/env python3
"""
ESP32-C6 GDB Debugging Automation Tool (Refactored)
Provides automated debugging workflows for ESP-IDF projects
"""

import time
import socket
from pathlib import Path
from typing import Dict, List, Optional, Any

from esp32_debug_base import (
    ESP32DebugToolBase, ESP32Constants, ESP32ToolException,
    ESP32DeviceError, ESP32BuildError
)

class GDBProfile:
    """Represents a GDB debugging profile"""
    
    def __init__(self, name: str, description: str, 
                 breakpoints: List[str], commands: List[str]):
        self.name = name
        self.description = description
        self.breakpoints = breakpoints
        self.commands = commands

class ESP32C6GDBAutomation(ESP32DebugToolBase):
    """
    ESP32-C6 GDB Debugging Automation Tool
    
    Provides automated GDB debugging with pre-configured profiles:
    - Interactive debugging sessions with breakpoints
    - Crash analysis and coredump handling  
    - Memory debugging with heap/stack monitoring
    - System monitoring and performance analysis
    """
    
    @property
    def config_filename(self) -> str:
        return "gdb_automation_config.json"
    
    @property
    def default_config(self) -> Dict[str, Any]:
        return {
            'openocd_config': 'esp32c6_optimized.cfg',
            'default_profile': 'basic',
            'gdb_timeout': 30,
            'openocd_port': 3333,
            'telnet_port': 4444,
            'session_history': []
        }
    
    def __init__(self, project_path: Optional[str] = None):
        super().__init__(project_path)
        self._profiles = self._create_debug_profiles()
        self._openocd_process = None
    
    def _create_debug_profiles(self) -> Dict[str, GDBProfile]:
        """Create predefined debugging profiles"""
        return {
            'basic': GDBProfile(
                name='basic',
                description='Basic debugging with app_main breakpoint',
                breakpoints=['app_main'],
                commands=['info registers']
            ),
            'crash': GDBProfile(
                name='crash',
                description='Crash analysis debugging',
                breakpoints=['abort', 'esp_restart', 'esp_system_abort', '_esp_error_check_failed'],
                commands=[
                    'set print symbol-filename on',
                    'bt',
                    'info registers'
                ]
            ),
            'memory': GDBProfile(
                name='memory',
                description='Memory debugging and analysis',
                breakpoints=['malloc', 'free', 'heap_caps_malloc'],
                commands=[
                    'info proc mappings',
                    'info heap',
                    'monitor esp heap_info'
                ]
            ),
            'wifi': GDBProfile(
                name='wifi',
                description='WiFi stack debugging',
                breakpoints=['wifi_init', 'esp_wifi_start', 'wifi_station_start'],
                commands=[
                    'monitor esp wifi_info',
                    'info threads'
                ]
            ),
            'freertos': GDBProfile(
                name='freertos',
                description='FreeRTOS task debugging',
                breakpoints=['vTaskDelay', 'vTaskSuspend', 'xTaskCreate'],
                commands=[
                    'info threads',
                    'thread apply all bt',
                    'monitor esp freertos_info'
                ]
            )
        }
    
    def start_openocd(self, config_file: Optional[str] = None) -> bool:
        """
        Start OpenOCD server in background
        
        Args:
            config_file: OpenOCD configuration file (optional)
            
        Returns:
            True if OpenOCD started successfully
            
        Raises:
            ESP32DeviceError: If OpenOCD fails to start
        """
        config_file = config_file or self.tool_config.get('openocd_config', 'esp32c6_optimized.cfg')
        config_path = self.config.project_path / config_file
        
        if not config_path.exists():
            raise ESP32DeviceError(f"OpenOCD config not found: {config_path}")
        
        self.logger.info("Starting OpenOCD server...")
        
        try:
            with self.background_process(['openocd', '-f', str(config_path)]) as process:
                self._openocd_process = process
                
                # Wait for OpenOCD to start
                time.sleep(ESP32Constants.OPENOCD_START_TIMEOUT)
                
                if process.poll() is None:  # Process is running
                    self.logger.info("OpenOCD server started successfully")
                    self.log_session('openocd_started', {'config': str(config_path)})
                    return True
                else:
                    stdout, stderr = process.communicate()
                    error_msg = f"OpenOCD failed to start: {stderr}"
                    self.logger.error(error_msg)
                    raise ESP32DeviceError(error_msg)
                    
        except FileNotFoundError as e:
            error_msg = "OpenOCD not found. Ensure ESP-IDF is sourced."
            self.logger.error(error_msg)
            raise ESP32DeviceError(error_msg) from e
    
    def create_gdb_script(self, profile_name: str = 'basic', 
                         custom_breakpoints: Optional[List[str]] = None,
                         custom_commands: Optional[List[str]] = None) -> Path:
        """
        Create GDB initialization script
        
        Args:
            profile_name: Name of debugging profile to use
            custom_breakpoints: Additional custom breakpoints
            custom_commands: Additional custom commands
            
        Returns:
            Path to generated GDB script
            
        Raises:
            ESP32ToolException: If profile not found or script creation fails
        """
        if profile_name not in self._profiles:
            raise ESP32ToolException(f"Profile '{profile_name}' not found")
        
        profile = self._profiles[profile_name]
        script_path = self.config.project_path / f'gdbinit_{profile_name}'
        
        try:
            with open(script_path, 'w') as f:
                self._write_gdb_header(f, profile)
                self._write_gdb_init_commands(f)
                self._write_gdb_connection(f)
                self._write_gdb_breakpoints(f, profile.breakpoints, custom_breakpoints)
                self._write_gdb_commands(f, profile.commands, custom_commands)
                self._write_gdb_footer(f)
            
            self.logger.info(f"Created GDB script: {script_path}")
            return script_path
            
        except IOError as e:
            raise ESP32ToolException(f"Failed to create GDB script: {e}") from e
    
    def _write_gdb_header(self, f, profile: GDBProfile) -> None:
        """Write GDB script header"""
        f.write(f"# ESP32-C6 GDB Script - {profile.name.title()} Profile\\n")
        f.write(f"# {profile.description}\\n\\n")
    
    def _write_gdb_init_commands(self, f) -> None:
        """Write GDB initialization commands"""
        f.write("# GDB Initialization\\n")
        for cmd in ESP32Constants.GDB_INIT_COMMANDS:
            f.write(f"{cmd}\\n")
        f.write("\\n")
    
    def _write_gdb_connection(self, f) -> None:
        """Write GDB connection commands"""
        port = self.tool_config.get('openocd_port', 3333)
        f.write(f"# Load ELF and connect to target\\n")
        f.write(f"file {self.config.elf_file}\\n")
        f.write(f"target remote localhost:{port}\\n")
        f.write("monitor reset halt\\n\\n")
    
    def _write_gdb_breakpoints(self, f, profile_breakpoints: List[str], 
                              custom_breakpoints: Optional[List[str]] = None) -> None:
        """Write breakpoint commands"""
        all_breakpoints = profile_breakpoints.copy()
        if custom_breakpoints:
            all_breakpoints.extend(custom_breakpoints)
        
        if all_breakpoints:
            f.write("# Breakpoints\\n")
            for bp in all_breakpoints:
                f.write(f"break {bp}\\n")
            f.write("\\n")
    
    def _write_gdb_commands(self, f, profile_commands: List[str], 
                           custom_commands: Optional[List[str]] = None) -> None:
        """Write custom commands"""
        all_commands = profile_commands.copy()
        if custom_commands:
            all_commands.extend(custom_commands)
        
        if all_commands:
            f.write("# Custom Commands\\n")
            for cmd in all_commands:
                f.write(f"{cmd}\\n")
            f.write("\\n")
    
    def _write_gdb_footer(self, f) -> None:
        """Write GDB script footer"""
        f.write("# Debug session ready\\n")
        f.write("echo \\\\n🐛 ESP32-C6 Debug Session Ready!\\\\n\\n")
    
    def create_debug_profiles(self) -> Path:
        """
        Create all predefined debugging profiles
        
        Returns:
            Path to profiles directory
        """
        profiles_dir = self.config.project_path / 'debug_profiles'
        profiles_dir.mkdir(exist_ok=True)
        
        for name, profile in self._profiles.items():
            script_path = self.create_gdb_script(name)
            
            # Move to profiles directory
            new_path = profiles_dir / f'gdbinit_{name}'
            if script_path.exists():
                script_path.rename(new_path)
            
            self.logger.info(f"Profile '{name}': {profile.description}")
        
        self.log_session('profiles_created', {'count': len(self._profiles)})
        return profiles_dir
    
    def run_interactive_debug(self, profile: str = 'basic') -> bool:
        """
        Run interactive GDB debugging session
        
        Args:
            profile: Debugging profile to use
            
        Returns:
            True if debugging session completed successfully
        """
        self.log_session('debug_session_start', {'profile': profile})
        
        try:
            # Validate environment and build
            self.validate_environment()
            if not self.check_build():
                raise ESP32BuildError("Project build validation failed")
            
            # Start OpenOCD
            if not self.start_openocd():
                raise ESP32DeviceError("Failed to start OpenOCD")
            
            # Get or create GDB script
            gdb_script = self._get_gdb_script_path(profile)
            
            # Start GDB session
            self.logger.info(f"Starting GDB with profile: {profile}")
            
            gdb_cmd = [
                'riscv32-esp-elf-gdb',
                '-x', str(gdb_script),
                str(self.config.elf_file)
            ]
            
            # Run GDB interactively
            result = self.run_command(gdb_cmd, check=False, capture_output=False)
            
            success = result.returncode == 0
            self.log_session('debug_session_end', {
                'profile': profile,
                'success': success,
                'return_code': result.returncode
            })
            
            return success
            
        except (ESP32ToolException, ESP32BuildError, ESP32DeviceError) as e:
            self.logger.error(f"Debug session failed: {e}")
            self.log_session('debug_session_failed', {'error': str(e), 'profile': profile})
            return False
        
        finally:
            self._cleanup_openocd()
    
    def _get_gdb_script_path(self, profile: str) -> Path:
        """Get path to GDB script for profile"""
        if profile == 'basic':
            return self.create_gdb_script(profile)
        
        profiles_dir = self.config.project_path / 'debug_profiles'
        gdb_script = profiles_dir / f'gdbinit_{profile}'
        
        if not gdb_script.exists():
            self.logger.warning(f"Profile '{profile}' not found, creating it")
            self.create_debug_profiles()
        
        return gdb_script
    
    def _cleanup_openocd(self) -> None:
        """Clean up OpenOCD process"""
        if self._openocd_process and self._openocd_process.poll() is None:
            self.logger.info("Stopping OpenOCD...")
            self._openocd_process.terminate()
            try:
                self._openocd_process.wait(timeout=5)
            except TimeoutError:
                self.logger.warning("Force killing OpenOCD")
                self._openocd_process.kill()
            self._openocd_process = None
    
    def analyze_coredump(self, coredump_file: str) -> bool:
        """
        Analyze ESP32 coredump file
        
        Args:
            coredump_file: Path to coredump file
            
        Returns:
            True if analysis completed successfully
        """
        coredump_path = Path(coredump_file)
        if not coredump_path.exists():
            raise ESP32ToolException(f"Coredump file not found: {coredump_file}")
        
        self.logger.info(f"Analyzing coredump: {coredump_file}")
        
        try:
            # Use ESP-IDF coredump analysis tool
            result = self.run_command([
                'esp-coredump', 'info_corefile',
                '-t', 'raw',
                '-c', str(coredump_path),
                str(self.config.elf_file)
            ])
            
            self.logger.info("Coredump Analysis Results:")
            self.logger.info("=" * 40)
            self.logger.info(result.stdout)
            
            if result.stderr:
                self.logger.warning(f"Analysis warnings: {result.stderr}")
            
            self.log_session('coredump_analyzed', {'file': coredump_file})
            return True
            
        except ESP32ToolException as e:
            if "esp-coredump" in str(e):
                raise ESP32ToolException("esp-coredump tool not found") from e
            raise
    
    def monitor_system_info(self) -> bool:
        """
        Monitor system information via OpenOCD telnet interface
        
        Returns:
            True if monitoring completed successfully
        """
        if not self.start_openocd():
            return False
        
        try:
            time.sleep(2)  # Wait for OpenOCD to stabilize
            
            # Connect via socket to OpenOCD telnet interface
            telnet_port = self.tool_config.get('telnet_port', 4444)
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(10)
                sock.connect(('localhost', telnet_port))
                
                commands = [
                    'halt',
                    'esp heap_info',
                    'esp freertos_info', 
                    'reg pc',
                    'resume'
                ]
                
                self.logger.info("System Information:")
                self.logger.info("=" * 40)
                
                for cmd in commands:
                    sock.send(f"{cmd}\\n".encode())
                    time.sleep(1)
                    try:
                        response = sock.recv(1024).decode()
                        if response.strip():
                            self.logger.info(f"🔧 {cmd}:")
                            self.logger.info(response)
                            self.logger.info("-" * 20)
                    except socket.timeout:
                        self.logger.warning(f"Timeout waiting for response to: {cmd}")
            
            self.log_session('system_monitoring_complete')
            return True
            
        except Exception as e:
            error_msg = f"System monitoring failed: {e}"
            self.logger.error(error_msg)
            self.log_session('system_monitoring_failed', {'error': str(e)})
            return False
        
        finally:
            self._cleanup_openocd()
    
    def create_automation_scripts(self) -> None:
        """Create automation scripts for common debugging tasks"""
        scripts_dir = self.config.project_path / 'debug_scripts'
        scripts_dir.mkdir(exist_ok=True)
        
        # Create profile-specific scripts
        for profile_name in self._profiles.keys():
            script_content = f"""#!/bin/bash
# Automated debugging script for {profile_name} profile
echo "🚀 Starting {profile_name} debugging session..."
python3 tools/esp32c6_gdb_automation.py --profile {profile_name}
"""
            script_path = scripts_dir / f"debug_{profile_name}.sh"
            with open(script_path, 'w') as f:
                f.write(script_content)
            script_path.chmod(0o755)
        
        self.logger.info(f"Created automation scripts in {scripts_dir}")
    
    def main(self, args: Optional[List[str]] = None) -> bool:
        """
        Main entry point for GDB automation tool
        
        Args:
            args: Command line arguments
            
        Returns:
            True if successful
        """
        import argparse
        
        parser = argparse.ArgumentParser(description='ESP32-C6 GDB Debugging Automation')
        parser.add_argument('--profile', choices=list(self._profiles.keys()),
                          default='basic', help='Debugging profile to use')
        parser.add_argument('--create-profiles', action='store_true',
                          help='Create all debugging profiles')
        parser.add_argument('--monitor', action='store_true',
                          help='Monitor system information')
        parser.add_argument('--coredump', type=str,
                          help='Analyze coredump file')
        parser.add_argument('--create-scripts', action='store_true',
                          help='Create automation scripts')
        
        parsed_args = parser.parse_args(args)
        
        try:
            if parsed_args.create_profiles:
                self.create_debug_profiles()
                return True
            
            if parsed_args.create_scripts:
                self.create_automation_scripts()
                return True
            
            if parsed_args.monitor:
                return self.monitor_system_info()
            
            if parsed_args.coredump:
                return self.analyze_coredump(parsed_args.coredump)
            
            # Default: run interactive debugging
            return self.run_interactive_debug(parsed_args.profile)
            
        except Exception as e:
            self.logger.error(f"GDB automation failed: {e}")
            return False

# MCP integration functions
def cli_main():
    """CLI wrapper for entry point compatibility"""
    return ESP32C6GDBAutomation()

def run_debug_session_mcp(profile: str = 'basic', project_path: Optional[str] = None) -> Dict[str, Any]:
    """MCP wrapper for debug session execution"""
    tool = ESP32C6GDBAutomation(project_path)
    success = tool.run_interactive_debug(profile)
    
    return {
        'success': success,
        'profile': profile,
        'project_path': str(tool.config.project_path),
        'session_logged': True
    }

if __name__ == '__main__':
    tool = ESP32C6GDBAutomation()
    success = tool.main()
    exit(0 if success else 1)