# ESP32-C6 JTAG Debugging Setup for WSL2

Based on research and testing, here's the complete setup for ESP32-C6 USB JTAG debugging in WSL2.

## Prerequisites

### 1. Install usbipd-win (Windows)
```powershell
# Install via winget
winget install --interactive --exact dorssel.usbipd-win
```

### 2. Verify WSL2 Version
```bash
wsl --version
# Should show WSL version 2.x.x
```

## ESP32-C6 USB JTAG Configuration

### Step 1: Windows PowerShell (Administrator)

```powershell
# 1. List USB devices to find ESP32-C6
usbipd list

# Expected output for ESP32-C6:
# BUSID  VID:PID    DEVICE                                          STATE
# 1-1    303a:1001  USB Serial Device (COM4), USB JTAG/serial debug unit  Not shared

# 2. Bind the ESP32-C6 device (replace 1-1 with your BUSID)
usbipd bind -b 1-1

# 3. Attach to WSL2 with auto-attach for persistent connection
usbipd attach --wsl --busid 1-1 --auto-attach
```

### Step 2: Verify in WSL2

```bash
# Check USB device attachment
ls /dev/ttyACM*
# Expected: /dev/ttyACM0 (or similar)

# Verify permissions
ls -l /dev/ttyACM*
# Should show crw-rw----+ permissions
```

## ESP-IDF OpenOCD Configuration

### ESP32-C6 Built-in JTAG Features

The ESP32-C6 has **built-in USB JTAG circuitry** requiring only a USB cable connected to D+/D- pins:
- **VID:PID**: `303a:1001` 
- **Device Name**: `/dev/ttyACM0` (in WSL2)
- **Dual Function**: Serial communication + JTAG debugging
- **No External Hardware**: No ESP-PROG or FT2232H required

### OpenOCD Configuration File

Create `esp32c6_openocd.cfg`:
```tcl
# ESP32-C6 Built-in USB JTAG Configuration
adapter driver esp_usb_jtag
adapter speed 40000
esp_usb_jtag vid_pid 0x303a 0x1001
set ESP_RTOS none

# ESP32-C6 Target Configuration  
source [find target/esp32c6.cfg]

# Optional: Reset configuration
reset_config srst_only srst_nogate
```

### Launch OpenOCD

```bash
# Method 1: Using ESP-IDF provided configuration
openocd -f board/esp32c6-builtin.cfg

# Method 2: Using custom configuration  
openocd -f esp32c6_openocd.cfg

# Expected output:
# Info : esp_usb_jtag: Device found. Base speed 40000KHz, div range 1 to 255
# Info : clock speed 40000 kHz  
# Info : JTAG tap: esp32c6.cpu tap/device found: 0x0000dc25
```

## GDB Debugging Setup

### 1. Terminal 1 (OpenOCD Server)
```bash
# Start OpenOCD server
openocd -f board/esp32c6-builtin.cfg
```

### 2. Terminal 2 (GDB Client) 
```bash
# Launch ESP32-C6 GDB
riscv32-esp-elf-gdb build/project.elf

# In GDB prompt:
(gdb) set architecture riscv:rv32
(gdb) target remote localhost:3333
(gdb) file build/project.elf
(gdb) monitor reset halt
(gdb) break app_main
(gdb) continue
```

## Docker Integration

### For ESP-IDF Docker Container

```bash
# Run ESP-IDF container with USB device access
docker run --rm -it \
  -v "$(pwd):/project" \
  -w /project \
  --device=/dev/ttyACM0 \
  --privileged \
  espressif/idf:release-v5.2 bash

# Inside container:
openocd -f board/esp32c6-builtin.cfg &
riscv32-esp-elf-gdb build/project.elf
```

## Troubleshooting

### Common Issues

1. **Permission Denied**: 
   ```bash
   sudo usermod -a -G dialout $USER
   # Logout and login again
   ```

2. **Device Not Found**:
   ```powershell
   # Windows: Re-attach device
   usbipd detach --busid 1-1
   usbipd attach --wsl --busid 1-1 --auto-attach
   ```

3. **OpenOCD Connection Failed**:
   ```bash
   # Check if device is accessible
   ls -l /dev/ttyACM*
   
   # Kill existing OpenOCD processes  
   sudo pkill openocd
   ```

### Verification Commands

```bash
# Test serial communication
echo "test" > /dev/ttyACM0

# Check USB device info
udevadm info --name=/dev/ttyACM0 | grep ID_

# Verify JTAG connectivity
openocd -f board/esp32c6-builtin.cfg -c "init; reset halt; exit"
```

## Advanced Features

### Multiple ESP32-C6 Devices
```bash
# List all ESP32-C6 devices
usbipd list | grep "303a:1001"

# Attach multiple devices with different BUSID
usbipd attach --wsl --busid 1-1 --auto-attach  # First device -> /dev/ttyACM0
usbipd attach --wsl --busid 1-2 --auto-attach  # Second device -> /dev/ttyACM1
```

### Persistent Configuration
Add to `~/.bashrc`:
```bash
# ESP32-C6 JTAG Debugging Aliases
alias esp32c6-openocd='openocd -f board/esp32c6-builtin.cfg'
alias esp32c6-gdb='riscv32-esp-elf-gdb build/project.elf'
```

## Summary

This setup enables:
- ✅ **Built-in USB JTAG**: No external hardware required
- ✅ **WSL2 Integration**: Full development in Linux environment  
- ✅ **Real-time Debugging**: Breakpoints, step debugging, register access
- ✅ **Docker Support**: Containerized ESP-IDF development
- ✅ **Persistent Connection**: Auto-attach for seamless workflow

The ESP32-C6's built-in USB JTAG interface combined with usbipd-win provides a robust debugging solution for WSL2-based development environments.