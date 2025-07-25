# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

---

## 🚀 **ESP32-C6 Development Tools - Quick Discovery**

### **📱 Slash Commands Available** (Type `/` to discover)
- `/esp-troubleshoot` - Comprehensive device troubleshooting with auto-fixes
- `/esp-analyze` - Advanced device analysis using esptool.py operations
- `/esp-debug` - Interactive debugging with OpenOCD and telnet interface
- `/esp-build` - Build, flash, monitor operations with smart workflows
- `/esp-discover` - Explore all 24+ available ESP32 development tools
- `/esp-analyze-code` - Static code analysis with clang-tidy and HTML reports

### **⚡ Ultimate Convenience Commands**
```bash
./vesc check          # Environment validation and device detection
./vesc dev            # Complete workflow: build + flash + monitor
./vesc debug          # Interactive debugging session
./vesc troubleshoot   # Automated problem diagnosis and fixes
./vesc quick          # Fast build + flash cycle
```

### **🔧 Specialized Tools** (24+ Python tools in `tools/` directory)
- **Troubleshooting**: `python tools/comprehensive_troubleshooting.py`
- **Device Analysis**: `python tools/esptool_advanced_suite.py --info-only`
- **Static Analysis**: `python tools/static_analysis_suite.py`
- **OpenOCD Automation**: `python tools/openocd_telnet_demo.py`
- **Memory Debugging**: `python tools/esp32c6_memory_debug.py`

### **📚 Documentation & Guides**
- `QUICK_START_GUIDE.md` - Complete developer reference
- `DEVELOPMENT_OPTIMIZATIONS_SUMMARY.md` - Implementation details
- `tools/GETTING_STARTED.md` - Tool-specific documentation

### **🎯 Current Device Status**
- **Device**: ESP32-C6 at `/dev/ttyACM0` ✅ CONNECTED
- **Features**: WiFi 6, BT 5, IEEE802.15.4, Built-in USB JTAG
- **Flash**: 8MB healthy, MAC: 40:4c:ca:43:b1:48
- **Environment**: ESP-IDF v5.5 ready, all tools verified working

---

## Project Overview

VESC Express is a WiFi and Bluetooth-enabled logger and IO-board firmware for ESP32 devices (primarily ESP32-C3). This project integrates the LispBM language interpreter for scriptable functionality and supports various hardware configurations through a modular hardware abstraction layer.

## Build System and Development Commands

### Prerequisites
- ESP-IDF version 5.2 or later is required
- The project uses the standard ESP-IDF CMake build system

### Build Commands
```bash
# Standard build
idf.py build

# Clean build (forces cmake reconfiguration)
idf.py fullclean && idf.py build

# Reconfigure (required when changing hardware environment variables)
idf.py reconfigure && idf.py build

# Flash firmware to device
idf.py flash

# Monitor serial output
idf.py monitor

# Flash and monitor in one command
idf.py flash monitor
```

### Hardware Configuration
The project supports custom hardware configurations through two methods:

**Method 1: Environment Variables**
```bash
export HW_SRC=/path/to/hw_custom.c
export HW_HEADER=/path/to/hw_custom.h
idf.py reconfigure  # Required after setting variables
idf.py build
```

**Method 2: Editing conf_general.h**
- Add hardware files to `main/hwconf/` directory
- Modify `HW_SOURCE` and `HW_HEADER` definitions in `main/conf_general.h:32-33`

### Testing
The project includes test suites in multiple locations:
```bash
# LispBM tests (if available)
cd main/lispBM/tests && ./run_tests.sh

# VESC Express specific tests
cd main/lispBM/vesc_express_tests && ./run_tests.sh
```

## Architecture Overview

### Core Components

**Main Application Layer (`main/`)**
- `main.c` - Entry point and main task management
- `conf_general.h` - Hardware configuration selection and firmware version
- Configuration management (`config/` directory) with auto-generated parsers

**Communication Stack**
- `comm_*.c` - Protocol handlers for UART, USB, CAN, BLE, and WiFi
- `packet.c/h` - Packet framing and validation
- `commands.c/h` - Command processing and routing
- `terminal.c/h` - Terminal interface for debugging

**Hardware Abstraction (`hwconf/`)**
- `hw.c/h` - Generic hardware interface
- Hardware-specific implementations organized by manufacturer:
  - `trampa/` - Trampa hardware variants
  - `vesc/` - VESC hardware variants
- Each hardware variant has its own configuration parser and defaults

**LispBM Integration (`lispBM/` and lisp interface files)**
- Embedded Lisp interpreter for user scripting
- `lispif*.c/h` - Interface between firmware and LispBM
- Extension modules for VESC-specific functionality, displays, WiFi, BLE, and RGB LEDs
- `lbm_vesc_utils.c/h` - VESC-specific utility functions

**Peripheral Drivers (`drivers/`)**
- `bme280/` - Environmental sensor support
- `imu/` - Inertial measurement unit drivers
- SPI, encoder, and other low-level drivers

**Display Support (`display/`)**
- Multiple display driver implementations (ILI9341, SSD1306, ST7789, etc.)
- LispBM extensions for display control

### Key Data Structures

**`main_config_t` (main.h:28-48)**
- Central configuration structure
- Includes CAN settings, WiFi/BLE configuration, and connectivity options
- Serialized/deserialized via auto-generated parser code

**`bms_values` (datatypes.h:31-63)**
- Battery Management System data structure
- Supports up to 50 cells and temperature sensors

**Communication Protocol (datatypes.h:112-299)**
- Extensive command set (`COMM_PACKET_ID` enum)
- CAN protocol commands for distributed systems
- Standardized packet format for all communication channels

### Build Configuration

**CMake Structure**
- Root `CMakeLists.txt` handles versioning and git integration
- Component-level `main/CMakeLists.txt` manages source files and includes
- Automatic git hash embedding for version tracking
- ESP-IDF component dependencies managed via `idf_component.yml`

**LispBM Integration**
- LispBM is included as a git subtree at `main/lispBM/`
- Selected source files compiled directly into main component
- Extensions loaded at runtime for VESC-specific functionality

## Development Guidelines

### Hardware Configuration Changes
- Always run `idf.py reconfigure` after changing `HW_SRC`/`HW_HEADER` environment variables
- Hardware files must provide both `.c` implementation and `.h` header
- Default hardware is Trampa XP-T (`hw_xp_t.c/h`)

### LispBM Development
- User scripts run in separate evaluation context
- Extensions provide bridge between Lisp and C code
- Script loading/saving handled through communication protocol
- Event system allows scripts to respond to system events

### Communication Protocol
- All communication uses standardized packet format
- Commands are handled through central dispatcher
- New commands should be added to `COMM_PACKET_ID` enum
- CAN messages use separate command space for distributed operation

### Configuration Management
- Configuration structures auto-generate serialization code
- Changes to config structures require updating parser generators
- Backup data structure handles persistence across firmware updates

## Android Compatibility

### Overview
VESC Express includes comprehensive Android compatibility optimizations for both BLE and WiFi functionality. These optimizations ensure reliable operation with modern Android devices (Android 8.0+).

### BLE Android Compatibility
- **Advertisement Intervals**: Optimized for Android 5.0+ background scanning (100-250ms)
- **MTU Support**: Supports up to 512 bytes for optimal Android performance
- **Power Management**: Adaptive power levels to prevent Android connection throttling
- **Connection Parameters**: Android-friendly intervals (20-40ms) for responsive communication

### WiFi Android Compatibility
- **Security**: WPA2/WPA3 mixed mode with PMF (Protected Management Frames)
- **Compliance**: Removes deprecated WEP support for Android 10+ compatibility
- **Power Management**: Optimized power saving for better battery integration
- **Coexistence**: Enhanced BLE/WiFi coexistence for dual-mode operation

### Configuration Options
The firmware includes Android compatibility modes:
- `ANDROID_COMPAT_DISABLED`: Legacy behavior
- `ANDROID_COMPAT_BASIC`: Basic Android optimizations
- `ANDROID_COMPAT_OPTIMIZED`: Full Android optimizations (default)

### Testing Android Compatibility
Use the built-in test suite to validate Android compatibility:
```c
#include "test_android_compat.h"
run_android_compatibility_tests();
```

### Android Device Support Matrix
| Android Version | BLE Support | WiFi Support | Notes |
|----------------|-------------|--------------|-------|
| 8.0 (API 26)   | ✓ | ✓ | Basic compatibility |
| 9.0 (API 28)   | ✓ | ✓ | Enhanced security |
| 10 (API 29)    | ✓ | ✓ | PMF requirements |
| 11 (API 30)    | ✓ | ✓ | WPA3 preference |
| 12+ (API 31+)  | ✓ | ✓ | Full modern support |

## Common Troubleshooting

### Build Issues
- If encountering CMake configuration errors, run `idf.py fullclean`
- Hardware configuration changes require `idf.py reconfigure`
- Check ESP-IDF version compatibility (5.2+ required)

### Hardware Variants
- Verify correct hardware files are selected in `conf_general.h`
- Each hardware variant may have different pin mappings and capabilities
- Some features may not be available on all hardware configurations

### Android Connection Issues
- Ensure Android device supports BLE and WiFi coexistence
- Check Android version compatibility (8.0+ recommended)
- Verify Android app permissions for BLE and WiFi access
- Test with Android compatibility mode enabled