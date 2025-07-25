# ESP32-C6 VESC Express - Quick Start Guide

## 🚀 Complete Development Environment (Ready!)

Your ESP32-C6 VESC Express development environment is now fully configured and operational.

### ✅ What's Been Set Up

#### **ESP-IDF Environment (v5.5)**
- ✅ ESP-IDF v5.5 with Python virtual environment
- ✅ OpenOCD v0.12.0-esp32-20250422 (latest)
- ✅ RISC-V GDB 16.2_20250324 (latest)
- ✅ esptool.py v4.9.0 (latest)
- ✅ ESP32-C6 device detected at /dev/ttyACM0

#### **Advanced Debugging Tools**
- ✅ Unified debugging environment (`esp32c6_unified_debugger.py`)
- ✅ Comprehensive debug helper (`debug_helper.py`)
- ✅ OpenOCD configuration optimized for ESP32-C6
- ✅ GDB automation scripts with memory debugging
- ✅ WSL2 USB passthrough working correctly

#### **VS Code Integration**
- ✅ Build, Flash, Monitor tasks configured
- ✅ Debugging configuration with breakpoint support
- ✅ Problem matchers for error detection
- ✅ ESP32-C6 specific launch configuration

#### **Convenient Development Aliases**
- ✅ `esp-setup` - Quick ESP-IDF environment activation
- ✅ `esp-build`, `esp-flash`, `esp-monitor` - Standard operations
- ✅ `esp-debug` - Interactive debugging session
- ✅ `esp-check` - Environment validation

---

## ⚡ Quick Commands

### **Daily Development Workflow**

```bash
# 1. Set up environment (run once per terminal session)
source .env.esp32

# 2. Build project
build                    # or: idf.py build

# 3. Flash to device  
flash                    # or: idf.py flash

# 4. Monitor serial output
monitor                  # or: idf.py monitor

# 5. Start debugging session
debug                    # or: python tools/esp32c6_unified_debugger.py --interactive
```

### **Debugging Commands**

```bash
# Quick environment check
quick-check              # or: python tools/debug_helper.py --check

# Comprehensive debugging
python tools/esp32c6_unified_debugger.py --wizard    # Full setup wizard
python tools/esp32c6_unified_debugger.py --test      # Run all tests

# Manual OpenOCD + GDB
openocd -f tools/esp32c6_final.cfg                   # Terminal 1
riscv32-esp-elf-gdb build/*.elf -ex "target remote :3333"  # Terminal 2
```

### **VS Code Integration**

```
Ctrl+Shift+P → Tasks: Run Task → ESP-IDF: Build      # Build project
Ctrl+Shift+P → Tasks: Run Task → ESP-IDF: Flash      # Flash firmware
F5                                                    # Start debugging
```

---

## 🎯 Development Modes

### **1. Standard Development**
Perfect for code changes, build testing, and basic debugging:
```bash
source .env.esp32
build && flash && monitor
```

### **2. Interactive Debugging**
Full breakpoint debugging with VS Code or GDB:
```bash
# VS Code (recommended)
F5 to start debugging

# Command line GDB
openocd -f tools/esp32c6_final.cfg  # Terminal 1
riscv32-esp-elf-gdb build/*.elf -ex "target remote :3333"  # Terminal 2
```

### **3. Memory Analysis**
Advanced memory debugging and optimization:
```bash
python tools/esp32c6_memory_debug.py --analyze
python tools/esp32c6_memory_debug.py --heap-trace
```

### **4. Automated Testing**
Comprehensive system validation:
```bash
python tools/esp32c6_unified_debugger.py --test
python tools/debug_helper.py --test
```

---

## 📁 Project Structure

```
vesc_express/
├── main/                          # Main application code
│   ├── conf_general.h            # Hardware configuration (ESP32-C6)
│   ├── main.c                    # Application entry point
│   ├── commands.c                # VESC protocol + debug commands
│   └── hwconf/hw_devkit_c6.*     # ESP32-C6 hardware abstraction
├── tools/                         # Advanced debugging suite
│   ├── esp32c6_unified_debugger.py  # Main debugging interface
│   ├── debug_helper.py           # Quick debugging operations
│   ├── esp32c6_final.cfg         # OpenOCD configuration
│   └── *.py                      # Specialized debug tools
├── .vscode/                       # VS Code configuration
│   ├── tasks.json                # Build/flash/debug tasks
│   └── launch.json               # Debugging configuration
├── .env.esp32                     # Project environment variables
└── setup_esp_env.sh              # Environment setup script
```

---

## 🔧 Hardware Configuration

### **Current Hardware Target**
- **Target**: ESP32-C6 Development Kit
- **Hardware Files**: `hw_devkit_c6.c/h`
- **Serial Port**: `/dev/ttyACM0`
- **Debug Interface**: USB JTAG (built-in)

### **Switching Hardware Targets**
To use different hardware (optional):
```bash
export HW_SRC=main/hwconf/hw_custom.c
export HW_HEADER=main/hwconf/hw_custom.h
idf.py reconfigure build
```

---

## 🐛 Troubleshooting

### **Common Issues & Solutions**

| Issue | Solution |
|-------|----------|
| "ESP-IDF not found" | Run: `source ~/esp/esp-idf/export.sh` |
| "Device not detected" | Check USB connection, run: `lsusb \| grep ESP` |
| "Permission denied /dev/ttyACM0" | Run: `sudo usermod -a -G dialout $USER`, then logout/login |
| "Build errors" | Run: `idf.py fullclean build` |
| "VS Code debugging not working" | Ensure OpenOCD is running: `openocd -f tools/esp32c6_final.cfg` |

### **Environment Validation**
```bash
# Complete environment check
python tools/debug_helper.py --check

# Tool versions
idf.py --version
openocd --version
riscv32-esp-elf-gdb --version
```

### **Reset Everything**
If something goes wrong, reset the complete environment:
```bash
./setup_esp_env.sh                # Re-run setup
source .env.esp32                  # Reload environment
python tools/debug_helper.py --check  # Verify
```

---

## 📚 Advanced Features

### **Protocol-Based Debugging**
The firmware includes integrated debug commands in the VESC protocol:
- `COMM_DEBUG_GET_SYSTEM_INFO` - System status and memory usage
- `COMM_DEBUG_SET_LOG_LEVEL` - Dynamic log level control
- `COMM_DEBUG_GET_MEMORY_STATS` - Heap and task memory analysis
- `COMM_DEBUG_WIFI_STATUS` - WiFi connection diagnostics
- `COMM_DEBUG_BLE_STATUS` - Bluetooth connection diagnostics

Access via terminal:
```bash
debug_info              # System information
debug_level <0-4>       # Set debug verbosity
```

### **Memory Optimization**
The debug system uses only ~2KB RAM through protocol integration instead of separate debug servers (~12KB), preventing ESP32-C6 memory exhaustion.

### **Cross-Platform Support**
- ✅ **Linux** (native)
- ✅ **WSL2** (with USB passthrough)
- ✅ **macOS** (with minor path adjustments)
- ✅ **Windows** (via WSL2)

---

## 🎉 You're Ready!

Your ESP32-C6 VESC Express development environment is production-ready with:

- **Complete ESP-IDF toolchain** (latest versions)
- **Advanced debugging capabilities** (OpenOCD + GDB + custom tools)
- **VS Code integration** (build, flash, debug)
- **Memory-efficient debug protocol** (integrated with VESC commands)
- **Automated testing and validation** (comprehensive test suite)

### **Start developing:**
```bash
source .env.esp32
build
flash
monitor
```

### **Happy coding! 🚀**