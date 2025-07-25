# ESP32-C6 Debugging Tools Suite

A comprehensive collection of debugging simplification tools for ESP-IDF and ESP32-C6 development, addressing common hardware debugging challenges with OpenOCD, JTAG, and WSL2.

## 🚀 Quick Start

```bash
# For first-time setup, run the wizard:
python3 esp32c6_unified_debugger.py --wizard

# For daily debugging, use the interactive menu:
python3 esp32c6_unified_debugger.py --interactive
```

## 📁 Tool Overview

| Tool | Purpose | Key Features |
|------|---------|-------------|
| `esp32c6_unified_debugger.py` | **Main Interface** | Interactive menu, wizard, session management |
| `esp32c6_openocd_setup.py` | OpenOCD Configuration | Auto-detection, profiles, VS Code integration |
| `esp32c6_gdb_automation.py` | GDB Automation | Debug profiles, coredump analysis, monitoring |
| `esp32c6_memory_debug.py` | Memory Analysis | Layout analysis, heap monitoring, fragmentation |
| `wsl2_esp32_debug_setup.py` | WSL2 Setup | USB passthrough, permissions, device management |

## 💡 Usage Examples

### Interactive Debugging Menu
```bash
python3 esp32c6_unified_debugger.py --interactive
```
Provides a menu-driven interface for all debugging operations.

### Quick Debug Sessions
```bash
# Basic debugging
python3 esp32c6_unified_debugger.py --profile basic

# Crash analysis
python3 esp32c6_unified_debugger.py --profile crash

# Memory debugging
python3 esp32c6_unified_debugger.py --profile memory
```

### Memory Analysis
```bash
# Analyze memory layout
python3 esp32c6_memory_debug.py --analyze

# Check memory fragmentation (requires hardware)
python3 esp32c6_memory_debug.py --fragmentation
```

### WSL2 Setup
```bash
# Full WSL2 debugging setup
python3 wsl2_esp32_debug_setup.py

# Device management
python3 wsl2_debug_scripts/esp32_device_manager.py
```

## 🎯 Debug Profiles

| Profile | Use Case | Breakpoints |
|---------|----------|-------------|
| **basic** | General debugging | `app_main` |
| **crash** | System crashes | `abort`, `esp_restart`, `_esp_error_check_failed` |
| **memory** | Memory issues | `malloc`, `free`, `heap_caps_malloc` |
| **wifi** | WiFi stack issues | `wifi_init`, `esp_wifi_start` |
| **freertos** | Task debugging | `vTaskDelay`, `vTaskSuspend`, `xTaskCreate` |

## 🔧 Generated Files and Scripts

### OpenOCD Configurations
- `esp32c6_basic.cfg` - Simple configuration (6MHz)
- `esp32c6_optimized.cfg` - **Recommended** (20MHz, FreeRTOS support)
- `esp32c6_production.cfg` - Full features (40MHz)

### Helper Scripts
- `debug_scripts/quick_debug.sh` - One-command debug session
- `debug_scripts/start_openocd.sh` - OpenOCD launcher
- `debug_scripts/start_gdb.sh` - GDB launcher
- `wsl2_debug_scripts/start_wsl2_debug.sh` - WSL2-specific launcher

### VS Code Integration
- `.vscode/launch.json` - Debug configuration
- `.vscode/tasks.json` - OpenOCD task automation

### Memory Debugging
- `heap_monitor.gdb` - GDB heap monitoring script
- `memory_debug_tools/heap_tracer.sh` - Heap tracing session
- `memory_report.json` - Comprehensive memory analysis

## 🛠️ Environment Requirements

- ESP-IDF v5.2+ (v5.5 recommended)
- OpenOCD with ESP32-C6 support
- `riscv32-esp-elf-gdb`
- Python 3.6+

### WSL2 Additional Requirements
- usbipd-win installed on Windows host
- ESP32-C6 device with built-in USB JTAG (VID:PID 303a:1001)

## 🚨 Common Troubleshooting

### "OpenOCD connection failed"
```bash
# Check device detection
python3 esp32c6_openocd_setup.py --detect-only

# Kill existing processes
sudo pkill openocd
```

### "Device not found in WSL2"
```bash
# Re-attach USB device
usbipd.exe detach --busid 1-1
usbipd.exe attach --wsl --busid 1-1 --auto-attach
```

### "Permission denied"
```bash
# Fix permissions
sudo usermod -a -G dialout $USER
# Logout and login again
```

### "Build not found"
```bash
# Build project first
idf.py build
```

## 📊 Session Management

The unified debugger tracks debugging sessions with:
- Session history and logging
- Environment check results
- Configuration management
- Comprehensive debugging reports

Access session information:
```bash
# View session history
cat debug_session.log

# Generate detailed report
python3 esp32c6_unified_debugger.py --report
```

## 🎉 Benefits

✅ **One-Command Setup**: Automated environment configuration
✅ **WSL2 Compatible**: Full USB passthrough automation  
✅ **Profile-Based**: Predefined configurations for common scenarios
✅ **Memory Analysis**: Advanced heap/stack debugging
✅ **Session Tracking**: History and logging for debugging sessions
✅ **VS Code Integration**: Seamless IDE debugging setup
✅ **Error Recovery**: Automatic issue detection and fixes

## 🔗 Integration

These tools integrate with existing ESP-IDF workflows:
- Compatible with `idf.py` commands
- Works with ESP-IDF Docker containers
- Supports multiple devices
- Non-invasive - can coexist with manual setups

---

**For detailed documentation, see**: `../ESP32_IDF_DEBUGGING_SIMPLIFIED.md`