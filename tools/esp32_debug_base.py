#!/usr/bin/env python3
"""
ESP32 Debug Tools Base Classes and Common Utilities
Provides common functionality and base classes for all ESP32 debugging tools
"""

import os
import sys
import json
import subprocess
import logging
import time
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Any, Optional, List, Union, Tuple
from dataclasses import dataclass
from contextlib import contextmanager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

@dataclass
class ESP32Config:
    """ESP32 debugging configuration container"""
    project_path: Path
    build_path: Path
    elf_file: Path
    idf_path: Optional[Path] = None
    target: str = "esp32c6"
    
    def __post_init__(self):
        """Initialize derived paths"""
        self.idf_path = Path(os.environ.get('IDF_PATH', '')) if os.environ.get('IDF_PATH') else None
        if not self.build_path.is_absolute():
            self.build_path = self.project_path / self.build_path
        if not self.elf_file.is_absolute():
            self.elf_file = self.build_path / self.elf_file

class ESP32ToolException(Exception):
    """Base exception for ESP32 debugging tools"""
    pass

class ESP32ConfigurationError(ESP32ToolException):
    """Raised when configuration is invalid or missing"""
    pass

class ESP32BuildError(ESP32ToolException):
    """Raised when build-related operations fail"""
    pass

class ESP32DeviceError(ESP32ToolException):
    """Raised when device communication fails"""
    pass

class ProcessManager:
    """Manages subprocess execution with consistent error handling"""
    
    @staticmethod
    def run_command(
        cmd: List[str], 
        cwd: Optional[Path] = None,
        timeout: Optional[int] = None,
        capture_output: bool = True,
        check: bool = True
    ) -> subprocess.CompletedProcess:
        """
        Run command with consistent error handling and logging
        
        Args:
            cmd: Command and arguments as list
            cwd: Working directory for command
            timeout: Command timeout in seconds
            capture_output: Whether to capture stdout/stderr
            check: Whether to raise exception on non-zero exit
            
        Returns:
            CompletedProcess result
            
        Raises:
            ESP32ToolException: If command fails and check=True
        """
        try:
            logging.debug(f"Running command: {' '.join(cmd)}")
            result = subprocess.run(
                cmd,
                cwd=cwd,
                timeout=timeout,
                capture_output=capture_output,
                text=True,
                check=check
            )
            return result
            
        except subprocess.CalledProcessError as e:
            error_msg = f"Command failed: {' '.join(cmd)}"
            if e.stderr:
                error_msg += f"\nError: {e.stderr}"
            logging.error(error_msg)
            raise ESP32ToolException(error_msg) from e
            
        except subprocess.TimeoutExpired as e:
            error_msg = f"Command timed out: {' '.join(cmd)}"
            logging.error(error_msg)
            raise ESP32ToolException(error_msg) from e
            
        except FileNotFoundError as e:
            error_msg = f"Command not found: {cmd[0]}"
            logging.error(error_msg)
            raise ESP32ToolException(error_msg) from e

    @staticmethod
    @contextmanager
    def background_process(cmd: List[str], cwd: Optional[Path] = None):
        """
        Context manager for background processes with automatic cleanup
        
        Args:
            cmd: Command and arguments as list
            cwd: Working directory for command
            
        Yields:
            subprocess.Popen: The background process
        """
        process = None
        try:
            logging.debug(f"Starting background process: {' '.join(cmd)}")
            process = subprocess.Popen(
                cmd,
                cwd=cwd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            yield process
            
        except Exception as e:
            logging.error(f"Background process failed: {e}")
            raise ESP32ToolException(f"Background process failed: {e}") from e
            
        finally:
            if process and process.poll() is None:
                logging.debug("Terminating background process")
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    logging.warning("Forcing background process termination")
                    process.kill()
                    process.wait()

class ConfigManager:
    """Manages configuration loading and saving"""
    
    def __init__(self, config_file: Path):
        self.config_file = config_file
        self._config: Dict[str, Any] = {}
    
    def load_config(self, defaults: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Load configuration from file with optional defaults
        
        Args:
            defaults: Default configuration values
            
        Returns:
            Configuration dictionary
        """
        self._config = defaults.copy() if defaults else {}
        
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    file_config = json.load(f)
                    self._config.update(file_config)
                logging.debug(f"Loaded configuration from {self.config_file}")
                
            except (json.JSONDecodeError, IOError) as e:
                logging.warning(f"Failed to load config from {self.config_file}: {e}")
                if defaults:
                    self.save_config()
        else:
            logging.info(f"Config file {self.config_file} not found, using defaults")
            if defaults:
                self.save_config()
        
        return self._config
    
    def save_config(self) -> None:
        """Save current configuration to file"""
        try:
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_file, 'w') as f:
                json.dump(self._config, f, indent=2)
            logging.debug(f"Saved configuration to {self.config_file}")
            
        except IOError as e:
            logging.error(f"Failed to save config to {self.config_file}: {e}")
            raise ESP32ConfigurationError(f"Failed to save configuration: {e}") from e
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        return self._config.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """Set configuration value"""
        self._config[key] = value
    
    def update(self, updates: Dict[str, Any]) -> None:
        """Update multiple configuration values"""
        self._config.update(updates)

class ESP32DebugToolBase(ABC):
    """
    Base class for all ESP32 debugging tools
    
    Provides common functionality and enforces consistent interface
    """
    
    def __init__(self, project_path: Optional[Union[str, Path]] = None):
        """
        Initialize ESP32 debugging tool
        
        Args:
            project_path: Path to ESP32 project (defaults to current directory)
        """
        self.project_path = Path(project_path) if project_path else Path.cwd()
        self.config = self._create_config()
        self.config_manager = ConfigManager(self.config.project_path / self.config_filename)
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Load tool-specific configuration
        self.tool_config = self.config_manager.load_config(self.default_config)
    
    @property
    @abstractmethod
    def config_filename(self) -> str:
        """Configuration filename for this tool"""
        pass
    
    @property
    @abstractmethod
    def default_config(self) -> Dict[str, Any]:
        """Default configuration for this tool"""
        pass
    
    def _create_config(self) -> ESP32Config:
        """Create ESP32 configuration"""
        return ESP32Config(
            project_path=self.project_path,
            build_path=Path('build'),
            elf_file=Path('project.elf')
        )
    
    def validate_environment(self) -> bool:
        """
        Validate ESP-IDF environment and project setup
        
        Returns:
            True if environment is valid
            
        Raises:
            ESP32ConfigurationError: If environment is invalid
        """
        issues = []
        
        # Check ESP-IDF path
        if not self.config.idf_path or not self.config.idf_path.exists():
            issues.append("ESP-IDF not found. Set IDF_PATH environment variable.")
        
        # Check project structure
        if not self.config.project_path.exists():
            issues.append(f"Project path not found: {self.config.project_path}")
        
        # Check for CMakeLists.txt (ESP-IDF project indicator)
        cmake_file = self.config.project_path / 'CMakeLists.txt'
        if not cmake_file.exists():
            issues.append(f"CMakeLists.txt not found in {self.config.project_path}")
        
        if issues:
            error_msg = "Environment validation failed:\\n" + "\\n".join(f"- {issue}" for issue in issues)
            self.logger.error(error_msg)
            raise ESP32ConfigurationError(error_msg)
        
        return True
    
    def check_build(self) -> bool:
        """
        Check if project is built and ELF file exists
        
        Returns:
            True if build is valid
        """
        if not self.config.elf_file.exists():
            self.logger.warning(f"ELF file not found: {self.config.elf_file}")
            self.logger.info("Build project first: idf.py build")
            return False
        
        self.logger.info(f"ELF file found: {self.config.elf_file}")
        return True
    
    def run_command(self, cmd: List[str], **kwargs) -> subprocess.CompletedProcess:
        """Run command using ProcessManager"""
        return ProcessManager.run_command(cmd, cwd=self.config.project_path, **kwargs)
    
    @contextmanager
    def background_process(self, cmd: List[str]):
        """Start background process using ProcessManager"""
        with ProcessManager.background_process(cmd, cwd=self.config.project_path) as process:
            yield process
    
    def log_session(self, action: str, details: Optional[Dict[str, Any]] = None) -> None:
        """
        Log debugging session activity
        
        Args:
            action: Action description
            details: Additional action details
        """
        log_entry = {
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'tool': self.__class__.__name__,
            'action': action,
            'details': details or {}
        }
        
        # Add to tool config session history
        session_history = self.tool_config.get('session_history', [])
        session_history.append(log_entry)
        
        # Keep only last 50 entries
        if len(session_history) > 50:
            session_history = session_history[-50:]
        
        self.tool_config['session_history'] = session_history
        self.config_manager.set('session_history', session_history)
        self.config_manager.save_config()
        
        self.logger.info(f"{action}: {details}")
    
    @abstractmethod
    def main(self, args: Optional[List[str]] = None) -> bool:
        """
        Main entry point for tool execution
        
        Args:
            args: Command line arguments
            
        Returns:
            True if successful
        """
        pass

# Constants used across tools
class ESP32Constants:
    """Constants for ESP32 debugging tools"""
    
    # ESP32-C6 Memory Layout
    MEMORY_REGIONS = {
        'ROM': {'start': 0x40000000, 'size': 0x20000, 'type': 'code'},
        'SRAM': {'start': 0x40800000, 'size': 0x80000, 'type': 'data'},
        'DRAM': {'start': 0x40800000, 'size': 0x80000, 'type': 'data'},
        'IRAM': {'start': 0x40800000, 'size': 0x80000, 'type': 'code'},
        'Flash': {'start': 0x42000000, 'size': 0x400000, 'type': 'code'},
        'External_RAM': {'start': 0x3C000000, 'size': 0x800000, 'type': 'data'}
    }
    
    # Common breakpoints for debugging
    COMMON_BREAKPOINTS = [
        'app_main',
        'esp_restart',
        'abort',
        'vTaskDelay',
        'esp_system_abort'
    ]
    
    # GDB initialization commands
    GDB_INIT_COMMANDS = [
        'set confirm off',
        'set architecture riscv:rv32',
        'set print pretty on',
        'set print array on',
        'set print array-indexes on'
    ]
    
    # OpenOCD configuration templates
    OPENOCD_CONFIGS = {
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
    
    # Device detection patterns
    USB_DEVICE_PATTERNS = ['303a:1001']  # ESP32-C6 USB device ID
    SERIAL_DEVICE_PATTERNS = ['/dev/ttyACM0', '/dev/ttyUSB0', '/dev/cu.usbmodem*']
    
    # File patterns and extensions
    PROJECT_FILES = ['CMakeLists.txt', 'sdkconfig', 'main/CMakeLists.txt']
    ELF_EXTENSIONS = ['.elf']
    CONFIG_EXTENSIONS = ['.json', '.cfg']
    
    # Timeouts (in seconds)
    DEFAULT_COMMAND_TIMEOUT = 30
    OPENOCD_START_TIMEOUT = 10
    GDB_CONNECT_TIMEOUT = 15
    DEVICE_DETECT_TIMEOUT = 5