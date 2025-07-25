#!/usr/bin/env python3
"""
ESP32-C6 OpenOCD Setup Automation Tool (Refactored)
Simplifies OpenOCD configuration and connection for ESP32-C6 debugging
"""

import os
import time
from pathlib import Path
from typing import Dict, Optional, Any, List, Tuple

from esp32_debug_base import (
    ESP32DebugToolBase, ESP32Constants, ESP32ToolException,
    ESP32DeviceError, ESP32ConfigurationError
)

class DeviceDetector:
    """Handles ESP32-C6 device detection"""
    
    @staticmethod
    def detect_usb_device() -> bool:
        """
        Detect ESP32-C6 USB device
        
        Returns:
            True if USB device detected
        """
        try:
            from esp32_debug_base import ProcessManager
            result = ProcessManager.run_command(['lsusb'], check=False)
            
            for pattern in ESP32Constants.USB_DEVICE_PATTERNS:
                if pattern in result.stdout:
                    return True
            
            return False
            
        except Exception:
            # lsusb not available or failed
            return False
    
    @staticmethod
    def detect_serial_device() -> Optional[str]:
        """
        Detect ESP32-C6 serial device
        
        Returns:
            Path to serial device if found, None otherwise
        """
        for device_pattern in ESP32Constants.SERIAL_DEVICE_PATTERNS:
            if '*' in device_pattern:
                # Handle glob patterns
                import glob
                matches = glob.glob(device_pattern)
                if matches:
                    return matches[0]
            else:
                device_path = Path(device_pattern)
                if device_path.exists():
                    return str(device_path)
        
        return None
    
    @classmethod
    def detect_esp32c6(cls) -> Tuple[bool, List[str]]:
        """
        Comprehensive ESP32-C6 device detection
        
        Returns:
            Tuple of (detected, detection_info)
        """
        detection_info = []
        detected = False
        
        # Check USB device
        if cls.detect_usb_device():
            detection_info.append("USB device detected (303a:1001)")
            detected = True
        
        # Check serial device
        serial_device = cls.detect_serial_device()
        if serial_device:
            detection_info.append(f"Serial device found: {serial_device}")
            detected = True
        
        if not detected:
            detection_info.append("No ESP32-C6 device detected")
        
        return detected, detection_info

class OpenOCDConfigGenerator:
    """Generates OpenOCD configuration files"""
    
    def __init__(self, project_path: Path):
        self.project_path = project_path
        self.templates = ESP32Constants.OPENOCD_CONFIGS
    
    def generate_config(self, config_type: str = 'optimized', 
                       custom_settings: Optional[Dict[str, Any]] = None) -> Path:
        """
        Generate OpenOCD configuration file
        
        Args:
            config_type: Type of configuration ('basic', 'optimized', 'production')
            custom_settings: Custom configuration settings
            
        Returns:
            Path to generated configuration file
        """
        if config_type not in self.templates:
            raise ESP32ConfigurationError(f"Unknown config type: {config_type}")
        
        config_path = self.project_path / f'esp32c6_{config_type}.cfg'
        config_content = self.templates[config_type]
        
        # Apply custom settings if provided
        if custom_settings:
            config_content = self._apply_custom_settings(config_content, custom_settings)
        
        try:
            with open(config_path, 'w') as f:
                f.write(config_content)
            
            return config_path
            
        except IOError as e:
            raise ESP32ToolException(f"Failed to create config file: {e}") from e
    
    def _apply_custom_settings(self, config_content: str, 
                              custom_settings: Dict[str, Any]) -> str:
        """Apply custom settings to configuration content"""
        # Simple template substitution for common settings
        replacements = {
            'adapter_speed': custom_settings.get('speed', 20000),
            'usb_vid_pid': custom_settings.get('vid_pid', '0x303a 0x1001'),
            'rtos_type': custom_settings.get('rtos', 'FreeRTOS')
        }
        
        modified_content = config_content
        for key, value in replacements.items():
            if key in custom_settings:
                # Replace specific patterns in config
                if key == 'adapter_speed':
                    modified_content = modified_content.replace('adapter speed 20000', f'adapter speed {value}')
                elif key == 'usb_vid_pid':
                    modified_content = modified_content.replace('esp_usb_jtag vid_pid 0x303a 0x1001', 
                                                              f'esp_usb_jtag vid_pid {value}')
                elif key == 'rtos_type':
                    modified_content = modified_content.replace('set ESP_RTOS FreeRTOS', f'set ESP_RTOS {value}')
        
        return modified_content

class ESP32C6OpenOCDSetup(ESP32DebugToolBase):
    """
    ESP32-C6 OpenOCD Setup and Configuration Tool
    
    Automates OpenOCD configuration for ESP32-C6 debugging including:
    - Device detection and USB JTAG setup
    - Configuration file generation with multiple profiles
    - VS Code integration and debug script creation
    - Connection testing and validation
    """
    
    @property
    def config_filename(self) -> str:
        return "openocd_setup_config.json"
    
    @property
    def default_config(self) -> Dict[str, Any]:
        return {
            'default_config_type': 'optimized',
            'auto_detect_device': True,
            'create_vscode_config': True,
            'test_connection': True,
            'custom_speed': None,
            'session_history': []
        }
    
    def __init__(self, project_path: Optional[str] = None):
        super().__init__(project_path)
        self.device_detector = DeviceDetector()
        self.config_generator = OpenOCDConfigGenerator(self.config.project_path)
    
    def detect_esp32c6(self) -> bool:
        """
        Detect ESP32-C6 device connection
        
        Returns:
            True if device detected
        """
        self.logger.info("Detecting ESP32-C6 device...")
        
        detected, detection_info = self.device_detector.detect_esp32c6()
        
        for info in detection_info:
            if "detected" in info.lower() and "no" not in info.lower():
                self.logger.info(f"✅ {info}")
            else:
                self.logger.warning(f"❌ {info}")
        
        if detected:
            self.log_session('device_detected', {'info': detection_info})
        else:
            self.logger.warning("Check USB connection and ensure device is in download mode")
            self.log_session('device_detection_failed', {'info': detection_info})
        
        return detected
    
    def check_dependencies(self) -> bool:
        """
        Check OpenOCD and related dependencies
        
        Returns:
            True if all dependencies are available
        """
        self.logger.info("Checking OpenOCD dependencies...")
        
        dependencies = [
            ('openocd', 'OpenOCD debugger'),
            ('riscv32-esp-elf-gdb', 'RISC-V GDB debugger'),
        ]
        
        missing_deps = []
        
        for cmd, description in dependencies:
            try:
                result = self.run_command([cmd, '--version'], check=False)
                if result.returncode == 0:
                    self.logger.info(f"✅ {description}: available")
                else:
                    missing_deps.append((cmd, description))
            except ESP32ToolException:
                missing_deps.append((cmd, description))
        
        if missing_deps:
            self.logger.error("Missing dependencies:")
            for cmd, desc in missing_deps:
                self.logger.error(f"❌ {desc} ({cmd})")
            self.logger.info("Ensure ESP-IDF environment is properly sourced")
            return False
        
        self.log_session('dependencies_checked', {'status': 'all_available'})
        return True
    
    def create_openocd_config(self, config_type: str = 'optimized',
                             custom_settings: Optional[Dict[str, Any]] = None) -> Path:
        """
        Create OpenOCD configuration file
        
        Args:
            config_type: Configuration type
            custom_settings: Custom configuration settings
            
        Returns:
            Path to created configuration file
        """
        self.logger.info(f"Creating OpenOCD configuration: {config_type}")
        
        # Apply tool config settings
        if not custom_settings:
            custom_settings = {}
        
        if self.tool_config.get('custom_speed'):
            custom_settings['speed'] = self.tool_config['custom_speed']
        
        config_path = self.config_generator.generate_config(config_type, custom_settings)
        
        self.logger.info(f"✅ Configuration created: {config_path}")
        self.log_session('config_created', {
            'type': config_type,
            'path': str(config_path),
            'custom_settings': custom_settings or {}
        })
        
        return config_path
    
    def test_openocd_connection(self, config_file: Optional[str] = None) -> bool:
        """
        Test OpenOCD connection to ESP32-C6
        
        Args:
            config_file: OpenOCD configuration file to test
            
        Returns:
            True if connection successful
        """
        config_file = config_file or f"esp32c6_{self.tool_config['default_config_type']}.cfg"
        config_path = self.config.project_path / config_file
        
        if not config_path.exists():
            raise ESP32ConfigurationError(f"Config file not found: {config_path}")
        
        self.logger.info(f"Testing OpenOCD connection with {config_file}")
        
        try:
            # Use ESP-IDF OpenOCD with ESP32-C6 support
            openocd_esp_path = "/home/rds/.espressif/tools/openocd-esp32/v0.12.0-esp32-20250422/openocd-esp32/bin/openocd"
            openocd_scripts_path = "/home/rds/.espressif/tools/openocd-esp32/v0.12.0-esp32-20250422/openocd-esp32/share/openocd/scripts"
            
            if os.path.exists(openocd_esp_path):
                openocd_cmd = openocd_esp_path
                # Set OpenOCD scripts environment variable
                os.environ['OPENOCD_SCRIPTS'] = openocd_scripts_path
            else:
                openocd_cmd = "openocd"
            
            with self.background_process([openocd_cmd, '-f', str(config_path)]) as process:
                # Wait for OpenOCD to start
                time.sleep(3)
                
                if process.poll() is None:
                    self.logger.info("✅ OpenOCD connection successful")
                    
                    # Test basic communication
                    if self._test_basic_communication():
                        self.log_session('connection_test_passed', {'config': config_file})
                        return True
                    else:
                        self.logger.warning("OpenOCD started but basic communication failed")
                        return False
                else:
                    stdout, stderr = process.communicate()
                    self.logger.error(f"OpenOCD failed to start: {stderr}")
                    self.log_session('connection_test_failed', {
                        'config': config_file,
                        'error': stderr
                    })
                    return False
                    
        except Exception as e:
            self.logger.error(f"Connection test failed: {e}")
            return False
    
    def _test_basic_communication(self) -> bool:
        """Test basic communication with target via socket"""
        try:
            import socket
            
            # Connect to OpenOCD telnet interface
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(5)
                sock.connect(('localhost', 4444))
                
                # Send halt command
                sock.send(b"halt\\n")
                time.sleep(1)
                
                # Send reg command to test communication
                sock.send(b"reg pc\\n")
                time.sleep(1)
                
                try:
                    response = sock.recv(1024).decode()
                    # Check if we got a valid response
                    return 'pc' in response.lower() or '0x' in response
                except socket.timeout:
                    return False
            
        except Exception as e:
            self.logger.debug(f"Basic communication test details: {e}")
            return False
    
    def create_vscode_config(self) -> None:
        """Create VS Code debugging configuration"""
        vscode_dir = self.config.project_path / '.vscode'
        vscode_dir.mkdir(exist_ok=True)
        
        # Create launch.json for debugging
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
                            "description": "Enable pretty-printing for gdb",
                            "text": "set print pretty on",
                            "ignoreFailures": True
                        },
                        {
                            "description": "Set architecture",
                            "text": "set architecture riscv:rv32",
                            "ignoreFailures": False
                        }
                    ],
                    "preLaunchTask": "Start OpenOCD"
                }
            ]
        }
        
        # Create tasks.json for OpenOCD startup
        tasks_config = {
            "version": "2.0.0",
            "tasks": [
                {
                    "label": "Start OpenOCD",
                    "type": "shell",
                    "command": "openocd",
                    "args": [
                        "-f",
                        f"esp32c6_{self.tool_config['default_config_type']}.cfg"
                    ],
                    "group": "build",
                    "isBackground": True,
                    "presentation": {
                        "echo": True,
                        "reveal": "always",
                        "focus": False,
                        "panel": "new"
                    },
                    "problemMatcher": []
                }
            ]
        }
        
        # Save configurations
        try:
            import json
            
            with open(vscode_dir / 'launch.json', 'w') as f:
                json.dump(launch_config, f, indent=4)
            
            with open(vscode_dir / 'tasks.json', 'w') as f:
                json.dump(tasks_config, f, indent=4)
            
            self.logger.info(f"✅ VS Code configuration created in {vscode_dir}")
            self.log_session('vscode_config_created', {'path': str(vscode_dir)})
            
        except IOError as e:
            self.logger.error(f"Failed to create VS Code config: {e}")
    
    def run_full_setup(self, config_type: str = 'optimized', 
                      test_connection: bool = True) -> bool:
        """
        Run complete OpenOCD setup process
        
        Args:
            config_type: Configuration type to create
            test_connection: Whether to test connection after setup
            
        Returns:
            True if setup completed successfully
        """
        self.logger.info("Running full OpenOCD setup...")
        
        try:
            # Step 1: Check dependencies
            if not self.check_dependencies():
                return False
            
            # Step 2: Detect device (optional - continue even if not detected)
            if self.tool_config.get('auto_detect_device', True):
                self.detect_esp32c6()
            
            # Step 3: Create OpenOCD configuration
            config_path = self.create_openocd_config(config_type)
            
            # Step 4: Create VS Code configuration
            if self.tool_config.get('create_vscode_config', True):
                self.create_vscode_config()
            
            # Step 5: Test connection
            if test_connection and self.tool_config.get('test_connection', True):
                if not self.test_openocd_connection(config_path.name):
                    self.logger.warning("Connection test failed, but setup completed")
                    self.log_session('setup_complete_with_warnings', {'config_type': config_type})
                    return True
            
            self.logger.info("✅ OpenOCD setup completed successfully!")
            self.log_session('setup_complete', {'config_type': config_type})
            return True
            
        except Exception as e:
            self.logger.error(f"Setup failed: {e}")
            self.log_session('setup_failed', {'error': str(e)})
            return False
    
    def main(self, args: Optional[List[str]] = None) -> bool:
        """
        Main entry point for OpenOCD setup tool
        
        Args:
            args: Command line arguments
            
        Returns:
            True if successful
        """
        import argparse
        
        parser = argparse.ArgumentParser(description='ESP32-C6 OpenOCD Setup Tool')
        parser.add_argument('--config', choices=['basic', 'optimized', 'production'],
                          default='optimized', help='Configuration type')
        parser.add_argument('--test', action='store_true',
                          help='Test connection after setup')
        parser.add_argument('--detect-only', action='store_true',
                          help='Only detect device, no setup')
        parser.add_argument('--check-deps', action='store_true',
                          help='Only check dependencies')
        parser.add_argument('--vscode', action='store_true',
                          help='Create VS Code configuration only')
        parser.add_argument('--speed', type=int,
                          help='Custom adapter speed')
        
        parsed_args = parser.parse_args(args)
        
        try:
            # Apply custom speed if provided
            if parsed_args.speed:
                self.tool_config['custom_speed'] = parsed_args.speed
                self.config_manager.set('custom_speed', parsed_args.speed)
                self.config_manager.save_config()
            
            if parsed_args.detect_only:
                return self.detect_esp32c6()
            
            if parsed_args.check_deps:
                return self.check_dependencies()
            
            if parsed_args.vscode:
                self.create_vscode_config()
                return True
            
            # Default: run full setup
            return self.run_full_setup(parsed_args.config, parsed_args.test)
            
        except Exception as e:
            self.logger.error(f"OpenOCD setup failed: {e}")
            return False

# MCP integration functions
def cli_main():
    """CLI wrapper for entry point compatibility"""
    return ESP32C6OpenOCDSetup()

def create_openocd_config(config_type: str = 'optimized', 
                         project_path: Optional[str] = None) -> Dict[str, Any]:
    """MCP wrapper for OpenOCD configuration creation"""
    tool = ESP32C6OpenOCDSetup(project_path)
    
    try:
        config_path = tool.create_openocd_config(config_type)
        return {
            'success': True,
            'config_path': str(config_path),
            'config_type': config_type,
            'project_path': str(tool.config.project_path)
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'config_type': config_type,
            'project_path': str(tool.config.project_path)
        }

if __name__ == '__main__':
    tool = ESP32C6OpenOCDSetup()
    success = tool.main()
    exit(0 if success else 1)