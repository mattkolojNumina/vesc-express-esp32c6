# Getting Started with VESC Express ESP32-C6 Debugging

This guide will walk you through setting up and using the debugging tools for the first time.

## 🎯 Prerequisites

Before starting, ensure you have:

### Required Software
- **ESP-IDF v5.2+** (v5.5 recommended)
- **Python 3.8+** with pip
- **OpenOCD** with ESP32 support
- **GDB for RISC-V** (`riscv32-esp-elf-gdb`)

### Hardware
- **ESP32-C6 device** with built-in USB JTAG
- **USB-C cable** for connection
- **Host computer** (Linux, macOS, or Windows with WSL2)

### WSL2 Users (Windows)
- **WSL2** with Ubuntu/Debian distribution
- **usbipd-win** installed on Windows host
- **Windows Terminal** (recommended)

## 🚀 Quick Setup (5 Minutes)

### Step 1: Run the Setup Wizard
```bash
cd /path/to/vesc_express
python tools/esp32c6_unified_debugger.py --wizard
```

The wizard will:
- ✅ Check your environment and dependencies
- ✅ Detect your ESP32-C6 device
- ✅ Configure OpenOCD with optimal settings
- ✅ Set up VS Code debugging (if available)
- ✅ Create debugging helper scripts
- ✅ Test the complete debugging setup

### Step 2: Build Your Project
```bash
idf.py build
```

### Step 3: Start Debugging
```bash
# Interactive debugging menu
python tools/esp32c6_unified_debugger.py --interactive

# Or quick debug session
python tools/esp32c6_unified_debugger.py --profile basic
```

## 📋 Manual Setup (If Wizard Fails)

### 1. Environment Check
```bash
# Verify ESP-IDF installation
python tools/debug_helper.py --check

# Fix any issues reported before continuing
```

### 2. WSL2 Setup (Windows Users Only)
```bash
# Install usbipd-win on Windows (run in PowerShell as Administrator)
winget install usbipd

# In WSL2, run the setup tool
python tools/wsl2_esp32_debug_setup.py
```

### 3. OpenOCD Configuration
```bash
# Auto-configure OpenOCD for ESP32-C6
python tools/esp32c6_openocd_setup.py --config optimized

# Test the configuration
python tools/esp32c6_openocd_setup.py --test
```

### 4. GDB Automation Setup
```bash
# Create debugging profiles
python tools/esp32c6_gdb_automation.py --create-profiles

# Test basic debugging
python tools/esp32c6_gdb_automation.py --profile basic
```

## 🎯 Your First Debugging Session

### 1. Start OpenOCD (Terminal 1)
```bash
# Option A: Use generated script
./debug_scripts/start_openocd.sh

# Option B: Manual command
openocd -f esp32c6_optimized.cfg
```

### 2. Start GDB (Terminal 2)
```bash
# Option A: Use generated script
./debug_scripts/start_gdb.sh

# Option B: Manual GDB session
riscv32-esp-elf-gdb build/vesc_express.elf
(gdb) target remote localhost:3333
(gdb) monitor reset halt
(gdb) load
(gdb) break app_main
(gdb) continue
```

### 3. Debug Your Code
```bash
# Set breakpoints
(gdb) break my_function

# Examine variables
(gdb) print my_variable

# Step through code
(gdb) step
(gdb) next

# View call stack
(gdb) backtrace
```

## 🧪 Verify Your Setup

### Test 1: Environment Check
```bash
python tools/debug_helper.py --check
```
Expected: All checks should pass (✅)

### Test 2: Device Detection
```bash
python tools/esp32c6_openocd_setup.py --detect-only
```
Expected: ESP32-C6 device detected

### Test 3: OpenOCD Connection
```bash
python tools/esp32c6_openocd_setup.py --test
```
Expected: Connection test passes

### Test 4: Memory Analysis
```bash
python tools/esp32c6_memory_debug.py --analyze
```
Expected: Memory layout displayed without errors

## 🎲 Common Scenarios

### Debugging Application Crashes
```bash
# Use crash analysis profile
python tools/esp32c6_unified_debugger.py --profile crash

# This will set breakpoints on:
# - abort()
# - esp_restart()
# - panic handlers
```

### Memory Leak Investigation
```bash
# Run memory debugging profile
python tools/esp32c6_unified_debugger.py --profile memory

# Or analyze memory fragmentation
python tools/esp32c6_memory_debug.py --fragmentation
```

### WiFi Stack Issues
```bash
# WiFi-specific debugging
python tools/esp32c6_unified_debugger.py --profile wifi

# Monitor WiFi events and connections
```

### FreeRTOS Task Problems
```bash
# FreeRTOS task analysis
python tools/esp32c6_unified_debugger.py --profile freertos

# This monitors task states and scheduling
```

## 🔧 VS Code Integration

If you have VS Code installed, the wizard automatically creates debugging configurations:

### 1. Open Project in VS Code
```bash
code .
```

### 2. Start Debugging
- Press `F5` or go to **Run and Debug** panel
- Select **ESP32-C6 Debug** configuration
- OpenOCD will start automatically
- Set breakpoints and debug as usual

### 3. Configuration Files Created
- `.vscode/launch.json` - Debug configuration
- `.vscode/tasks.json` - OpenOCD task automation

## 🚨 Troubleshooting Common Issues

### Issue: "ESP-IDF not found"
**Solution:**
```bash
# Source ESP-IDF environment
. $HOME/esp/esp-idf/export.sh

# Verify installation
idf.py --version
```

### Issue: "Device not detected"
**Solution:**
```bash
# Check USB connection
lsusb | grep 303a

# WSL2: Re-attach device
usbipd.exe attach --wsl --busid X-X --auto-attach
```

### Issue: "OpenOCD connection failed"
**Solution:**
```bash
# Kill existing OpenOCD processes
sudo pkill openocd

# Check if device is in download mode
# Try different USB cable
```

### Issue: "Permission denied /dev/ttyUSB0"
**Solution:**
```bash
# Add user to dialout group
sudo usermod -a -G dialout $USER

# Logout and login again
# Or use udev rules setup
sudo python tools/wsl2_esp32_debug_setup.py --setup-udev
```

### Issue: "Build files not found"
**Solution:**
```bash
# Build the project first
idf.py build

# Verify ELF file exists
ls -la build/*.elf
```

## 📚 Next Steps

Once you have basic debugging working:

1. **Explore Debug Profiles**: Try different profiles for specific scenarios
2. **Memory Analysis**: Use memory debugging tools for optimization
3. **Session Logging**: Review debug session logs for insights
4. **Custom Profiles**: Create custom debugging profiles for your needs
5. **Integration**: Integrate with your development workflow

## 📖 Additional Resources

- [Tool Suite Overview](README.md) - Detailed tool documentation
- [ESP32-C6 Debugging Simplified](../ESP32_IDF_DEBUGGING_SIMPLIFIED.md) - Advanced techniques
- [Quick Reference](../ESP32_DEBUG_QUICK_REFERENCE.md) - Command cheat sheet

## 🆘 Getting Help

If you encounter issues not covered here:

1. Check the tool logs in `debug_session.log`
2. Run with debug mode: `DEBUG=1 python tools/...`
3. Review the troubleshooting section in the main documentation
4. Check OpenOCD and GDB logs for specific error messages

Happy debugging! 🎉