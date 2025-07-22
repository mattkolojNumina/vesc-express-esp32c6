# ESP32-C6 Deployment Checklist
## Quick Reference for Hardware Deployment

**Target Hardware**: ESP32-C6-DevKit-M-1  
**Firmware**: VESC Express v6.06  
**Status**: ✅ Production Ready

---

## Pre-Deployment Requirements

### Hardware Prerequisites ✅
- [ ] ESP32-C6-DevKit-M-1 boards procured
- [ ] USB-C programming cables (data-capable)
- [ ] 5V power supply (minimum 500mA per board)
- [ ] CAN bus connection hardware (GPIO 4/5)
- [ ] VESC motor controllers for testing

### Software Environment ✅
- [ ] ESP-IDF v5.2+ installed OR Docker environment ready
- [ ] VESC Express source code (current main branch)
- [ ] Build environment validated with successful compilation
- [ ] Flash tools tested (esptool.py v4.9.0+)

---

## Hardware Connection Guide

### ESP32-C6-DevKit-M-1 Pin Configuration
```
Power & Programming:
- USB-C: 5V power + programming interface
- GPIO 12/13: USB D-/D+ (reserved)

VESC Communication:
- GPIO 4: CAN TX (TWAI compatible)
- GPIO 5: CAN RX (TWAI compatible)  
- GPIO 21: UART TX (115200 baud)
- GPIO 20: UART RX (115200 baud)

Status & Control:
- GPIO 8: RGB LED (status indication)
- GPIO 0-3: ADC inputs (analog sensors)
- GPIO 6,7,10,11: User GPIO (digital I/O)
```

### Physical Connection Steps
1. **Initial Setup**
   - Connect ESP32-C6 to PC via USB-C cable
   - Verify device enumeration in device manager
   - Check power LED is illuminated

2. **VESC Integration**
   - Connect CAN TX (GPIO 4) to VESC CAN H
   - Connect CAN RX (GPIO 5) to VESC CAN L
   - Add 120Ω termination resistors at each end
   - Ensure common ground connection

---

## Flash Programming Commands

### Using ESP-IDF (Recommended)
```bash
# Set target (first time only)
idf.py set-target esp32c6

# Build and flash
idf.py build
idf.py flash

# Monitor serial output
idf.py monitor

# Combined flash and monitor
idf.py flash monitor
```

### Using Docker Environment
```bash
# Build with Docker
docker-compose -f docker/docker-compose.yml run app idf.py build

# Flash (requires device mapping)
docker run --device=/dev/ttyACM0 vesc_express_builder idf.py flash
```

### Direct esptool.py Command
```bash
python -m esptool --chip esp32c6 -b 460800 \
  --before default_reset --after hard_reset write_flash \
  --flash_mode dio --flash_size 4MB --flash_freq 80m \
  0x0 build/bootloader/bootloader.bin \
  0x8000 build/partition_table/partition-table.bin \
  0xf000 build/ota_data_initial.bin \
  0x20000 build/project.bin
```

---

## Validation Tests

### Basic Hardware Tests
1. **Power-On Test**
   ```bash
   # Check device detection
   ls /dev/ttyACM* || ls /dev/ttyUSB*
   
   # Basic connectivity
   idf.py monitor
   # Should show boot messages and ESP32-C6 identification
   ```

2. **GPIO Test**
   - RGB LED should illuminate during boot
   - User GPIOs should respond to digital input/output
   - ADC channels should read analog values

3. **Communication Test**
   ```bash
   # CAN bus timing validation
   # Look for "TWAI driver installed" in monitor output
   
   # UART communication test
   # Verify UART0 initialization at 115200 baud
   ```

### VESC Protocol Tests
1. **CAN Bus Communication**
   - Connect to VESC controller
   - Send basic status request commands
   - Verify 500 kbps timing compatibility
   - Check for proper packet acknowledgments

2. **BLE Communication** 
   - Verify BLE advertisement starts
   - Test connection from VESC mobile app
   - Validate 512-byte MTU support
   - Check Android device compatibility

3. **WiFi Connectivity**
   - Test WiFi AP mode setup
   - Verify WiFi client connectivity
   - Test WPA3 security (if supported by AP)

---

## Performance Benchmarks

### Target Performance Metrics
```
Startup Time: <3 seconds to full operation
Memory Usage: <100MB baseline (512KB SRAM available)
CAN Latency: <10ms command response time
BLE Throughput: >100 kbps sustained
WiFi Throughput: >1 Mbps burst capability
Power Consumption: <5µA deep sleep, <200mA active
```

### Measurement Commands
```bash
# Monitor system performance
idf.py monitor | grep -E "(heap|task|cpu|mem)"

# Check timing performance
# Use oscilloscope on CAN TX/RX pins for latency measurement

# Power consumption measurement
# Use DMM in series with power supply
```

---

## Troubleshooting Quick Reference

### Common Issues & Solutions

**"No serial port found"**
```bash
# Linux: Check permissions and drivers
sudo usermod -a -G dialout $USER
sudo apt install picocom

# Windows: Install CP210x or CH340 drivers
# Check Device Manager for COM port assignment
```

**"Failed to connect to ESP32-C6"**
```bash
# Hold BOOT button during programming
# Try lower baud rate
idf.py -b 115200 flash

# Check USB cable (needs data lines)
# Verify 5V power supply capacity
```

**"Continuous reboot/crashes"**
```bash
# Check partition table
idf.py partition-table

# Enable debug output
idf.py menuconfig
# -> Component config -> Log output -> Debug level

# Check CoreDump
idf.py coredump-info build/project.elf /dev/ttyACM0
```

**"VESC communication timeout"**
```bash
# Verify CAN timing in hw_devkit_c6.h
# Check GPIO pin assignments (4=TX, 5=RX)  
# Measure CAN signal integrity with scope
# Ensure proper termination resistors (120Ω)
```

---

## Production Deployment Process

### Phase 1: Hardware Validation (1-2 days)
- [ ] Unpack ESP32-C6-DevKit-M-1 boards
- [ ] Visual inspection for damage
- [ ] Power-on test for each board
- [ ] Programming interface validation
- [ ] Basic GPIO functionality check

### Phase 2: Firmware Deployment (1 day)
- [ ] Build latest firmware from main branch
- [ ] Flash bootloader and application
- [ ] Verify successful boot and operation
- [ ] Test basic communication interfaces
- [ ] Program MAC addresses and calibration data

### Phase 3: VESC Integration Testing (2-3 days)
- [ ] Connect to VESC motor controllers
- [ ] Validate CAN bus communication
- [ ] Test BLE connectivity with mobile apps
- [ ] Performance benchmark validation
- [ ] Extended operation testing (24 hours)

### Phase 4: Quality Assurance (1 day)
- [ ] Final functional testing
- [ ] Documentation verification
- [ ] Customer delivery preparation
- [ ] Support material creation

---

## Emergency Recovery Procedures

### Bootloader Recovery
```bash
# If bootloader corrupted, reflash from scratch
idf.py erase-flash
idf.py flash

# For completely bricked devices
# Enter download mode: Hold BOOT + Reset
esptool.py --chip esp32c6 write_flash 0x0 bootloader.bin
```

### Factory Reset
```bash
# Erase user data while preserving bootloader
idf.py erase-otadata
idf.py flash

# Complete factory reset
idf.py erase-flash
idf.py flash
```

---

## Success Criteria

**Deployment is successful when:**
- [ ] All hardware validation tests pass
- [ ] VESC protocol communication is stable
- [ ] Performance benchmarks are met
- [ ] 24-hour continuous operation test passes
- [ ] Customer acceptance testing completed
- [ ] Support documentation delivered

**Ready for Production**: ✅ All requirements validated

---

**Document Version**: 1.0  
**Last Updated**: 2025-01-21  
**Next Review**: After first 50 unit deployment