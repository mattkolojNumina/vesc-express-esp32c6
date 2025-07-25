# ESP32-C6 Debugging Simplification Tools

This document provides a comprehensive guide to the debugging simplification tools created for ESP-IDF and ESP32-C6 development, specifically addressing common hardware debugging challenges with OpenOCD and JTAG.

## 🚀 Quick Start

```bash
# Run the unified debugging wizard
python3 tools/esp32c6_unified_debugger.py --wizard

# Or start with interactive menu
python3 tools/esp32c6_unified_debugger.py --interactive
```

## 🛠️ Tool Suite Overview

### 1. ESP32-C6 OpenOCD Setup Automation (`esp32c6_openocd_setup.py`)

**Purpose**: Simplifies OpenOCD configuration and connection setup for ESP32-C6 debugging.

**Key Features**:
- Automatic ESP32-C6 device detection (VID:PID 303a:1001)
- Three configuration profiles: basic, optimized, production
- Connection testing and validation
- VS Code debugging configuration generation
- Helper script creation

**Usage**:
```bash
# Full setup with optimized configuration
python3 tools/esp32c6_openocd_setup.py

# Test device detection only
python3 tools/esp32c6_openocd_setup.py --detect-only

# Use production configuration
python3 tools/esp32c6_openocd_setup.py --config production
```

**Generated Files**:
- `esp32c6_optimized.cfg` - OpenOCD configuration
- `debug_scripts/start_openocd.sh` - OpenOCD launcher
- `debug_scripts/start_gdb.sh` - GDB launcher  
- `debug_scripts/quick_debug.sh` - One-command debug session
- `.vscode/launch.json` - VS Code debugging configuration

### 2. Automated GDB Debugging Scripts (`esp32c6_gdb_automation.py`)

**Purpose**: Provides automated debugging workflows and profiles for common ESP-IDF debugging scenarios.

**Key Features**:
- Predefined debugging profiles (basic, crash, memory, wifi, freertos)
- Automatic GDB script generation
- Coredump analysis integration
- System information monitoring via OpenOCD
- Interactive debugging sessions

**Usage**:
```bash
# Run interactive debug with basic profile
python3 tools/esp32c6_gdb_automation.py --profile basic

# Create all debugging profiles
python3 tools/esp32c6_gdb_automation.py --create-profiles

# Analyze coredump file
python3 tools/esp32c6_gdb_automation.py --coredump core.dump

# Monitor system information
python3 tools/esp32c6_gdb_automation.py --monitor
```

**Debugging Profiles**:
- **basic**: Standard debugging with app_main breakpoint
- **crash**: Crash analysis with abort/restart breakpoints
- **memory**: Memory debugging with malloc/free tracking
- **wifi**: WiFi stack debugging
- **freertos**: FreeRTOS task analysis

### 3. WSL2-Specific Setup Tool (`wsl2_esp32_debug_setup.py`)

**Purpose**: Automates WSL2-specific configuration for ESP32-C6 debugging, addressing common USB passthrough issues.

**Key Features**:
- usbipd-win detection and setup instructions
- Automatic ESP32-C6 device binding and attachment
- Permission management and udev rules setup
- WSL2 device access verification
- Device management scripts

**Usage**:
```bash
# Full WSL2 setup
python3 tools/wsl2_esp32_debug_setup.py

# List available USB devices
python3 tools/wsl2_esp32_debug_setup.py --list-devices

# Verify device access only
python3 tools/wsl2_esp32_debug_setup.py --verify-access

# Setup udev rules only
sudo python3 tools/wsl2_esp32_debug_setup.py --setup-udev
```

**Generated Scripts**:
- `wsl2_debug_scripts/esp32_device_manager.py` - Device attach/detach management
- `wsl2_debug_scripts/start_wsl2_debug.sh` - WSL2 debug session starter

### 4. Memory Debugging Utilities (`esp32c6_memory_debug.py`)

**Purpose**: Advanced memory analysis and debugging tools for ESP-IDF projects.

**Key Features**:
- Memory layout analysis from ELF files
- Stack usage analysis
- Heap monitoring and fragmentation analysis
- GDB script generation for memory debugging
- Comprehensive memory reporting

**Usage**:
```bash
# Full memory analysis
python3 tools/esp32c6_memory_debug.py --analyze

# Memory fragmentation analysis (requires hardware connection)
python3 tools/esp32c6_memory_debug.py --fragmentation

# Generate memory report
python3 tools/esp32c6_memory_debug.py --report

# Create memory debugging toolset
python3 tools/esp32c6_memory_debug.py --create-tools
```

**Generated Tools**:
- `heap_monitor.gdb` - GDB script for heap monitoring
- `memory_debug_tools/memory_analyzer.py` - Memory layout analyzer
- `memory_debug_tools/heap_tracer.sh` - Heap tracing session

### 5. Unified Debugging Workflow Tool (`esp32c6_unified_debugger.py`)

**Purpose**: Combines all debugging tools into a single unified interface with interactive menu and workflow management.

**Key Features**:
- Interactive debugging menu
- Environment checking and setup automation
- Session logging and history
- Debugging report generation
- Quick start wizard for first-time setup
- Configuration management

**Usage**:
```bash
# Interactive debugging menu
python3 tools/esp32c6_unified_debugger.py --interactive

# Quick start wizard (recommended for first use)
python3 tools/esp32c6_unified_debugger.py --wizard

# Run specific debug profile
python3 tools/esp32c6_unified_debugger.py --profile crash

# Setup complete debugging environment
python3 tools/esp32c6_unified_debugger.py --setup

# Check environment and dependencies
python3 tools/esp32c6_unified_debugger.py --check

# Generate debugging report
python3 tools/esp32c6_unified_debugger.py --report
```

## 🎯 Common Debugging Scenarios

### Scenario 1: First-Time ESP32-C6 Debugging Setup

```bash
# 1. Run the wizard to set up everything
python3 tools/esp32c6_unified_debugger.py --wizard

# 2. If WSL2, the wizard will handle USB passthrough automatically
# 3. OpenOCD configuration will be created and tested
# 4. VS Code integration will be configured
```

### Scenario 2: Crash Analysis

```bash
# Start crash analysis debugging session
python3 tools/esp32c6_unified_debugger.py --profile crash

# Or use the interactive menu
python3 tools/esp32c6_unified_debugger.py --interactive
# Then select option 3 (Crash Analysis)
```

### Scenario 3: Memory Issues (Leaks, Corruption, Fragmentation)

```bash
# Memory debugging session
python3 tools/esp32c6_unified_debugger.py --profile memory

# Or analyze memory fragmentation
python3 tools/esp32c6_memory_debug.py --fragmentation

# Generate comprehensive memory report
python3 tools/esp32c6_memory_debug.py --report
```

### Scenario 4: WiFi Stack Issues

```bash
# WiFi-specific debugging
python3 tools/esp32c6_unified_debugger.py --profile wifi

# Monitor system information in real-time
python3 tools/esp32c6_gdb_automation.py --monitor
```

### Scenario 5: WSL2 USB Issues

```bash
# Full WSL2 setup and troubleshooting
python3 tools/wsl2_esp32_debug_setup.py

# List and manage USB devices
python3 wsl2_debug_scripts/esp32_device_manager.py

# Re-attach device if connection is lost
python3 wsl2_debug_scripts/esp32_device_manager.py attach 1-1
```

## 🔧 Configuration Files

### OpenOCD Configuration Templates

The tools generate three OpenOCD configuration templates:

**Basic Configuration** (`esp32c6_basic.cfg`):
- Simple setup for basic debugging
- 6MHz clock speed
- Minimal features

**Optimized Configuration** (`esp32c6_optimized.cfg`) - **Recommended**:
- 20MHz clock speed
- FreeRTOS support
- Enhanced debugging features
- WSL2 optimizations

**Production Configuration** (`esp32c6_production.cfg`):
- 40MHz clock speed
- All debugging features enabled
- Performance optimizations
- Production-ready settings

### GDB Scripts

**Common Breakpoints**:
- `app_main` - Application entry point
- `abort` - System abort calls
- `esp_restart` - System restart calls
- `malloc`/`free` - Memory allocation tracking

**Debugging Commands**:
- `heap_info` - Display heap information
- `stack_info` - Display stack and register state
- `memory_map` - Show memory mappings
- `freertos_tasks` - List FreeRTOS tasks

## 📊 Debugging Reports

The unified debugger can generate comprehensive debugging reports including:

- Environment check results
- Session history (last 10 sessions)
- Memory layout analysis
- Configuration details
- Hardware connection status

Reports are saved as JSON files with timestamps for easy tracking.

## 🚨 Troubleshooting

### Common Issues and Solutions

**1. OpenOCD Connection Failed**
```bash
# Check device connection
python3 tools/esp32c6_openocd_setup.py --detect-only

# Kill existing OpenOCD processes
sudo pkill openocd

# Retry connection test
python3 tools/esp32c6_openocd_setup.py --no-test
```

**2. WSL2 Device Not Found**
```bash
# Check Windows usbipd-win installation
usbipd.exe list

# Re-attach device
usbipd.exe detach --busid 1-1
usbipd.exe attach --wsl --busid 1-1 --auto-attach
```

**3. Permission Denied in WSL2**
```bash
# Add user to dialout group
sudo usermod -a -G dialout $USER
# Logout and login again

# Or setup udev rules
sudo python3 tools/wsl2_esp32_debug_setup.py --setup-udev
```

**4. Build Not Found**
```bash
# Build the project first
idf.py build

# Verify ELF file exists
ls -la build/project.elf
```

## 🎉 Benefits

These tools address the major ESP-IDF debugging pain points:

✅ **Simplified Setup**: One-command setup for complex debugging environment
✅ **WSL2 Support**: Automated USB passthrough and permission handling  
✅ **Profile-Based**: Predefined configurations for common debugging scenarios
✅ **Memory Analysis**: Advanced heap and stack debugging capabilities
✅ **Session Management**: Logging and history tracking for debugging sessions
✅ **Error Recovery**: Automatic detection and fixing of common issues
✅ **VS Code Integration**: Seamless IDE integration with proper configurations
✅ **Documentation**: Comprehensive guides and usage examples

## 🔗 Integration with Existing Workflows

These tools integrate seamlessly with existing ESP-IDF development workflows:

- Works with standard `idf.py build/flash/monitor` commands
- Compatible with ESP-IDF Docker containers
- Supports multiple ESP32-C6 devices
- Integrates with VS Code ESP-IDF extension
- Works with existing OpenOCD/GDB configurations

The tools are designed to be non-invasive and can be used alongside manual debugging when needed.