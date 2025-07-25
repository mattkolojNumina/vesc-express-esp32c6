# Android Testing Checklist for VESC Express

## Pre-Testing Setup

### Hardware Requirements
- [ ] ESP32-C3 development board
- [ ] Android device (Android 8.0 or higher)
- [ ] USB cable for ESP32 flashing
- [ ] VESC motor controller (optional for full testing)

### Software Requirements
- [ ] ESP-IDF 5.2 or later installed
- [ ] VESC Tool Android app (once built)
- [ ] Serial terminal for debugging

## ESP32 Firmware Testing

### 1. Flash Firmware
```bash
cd /home/rds/vesc_express
idf.py -p /dev/ttyUSB0 flash monitor
```

### 2. BLE Testing
- [ ] Enable Bluetooth on Android device
- [ ] Open VESC Tool app
- [ ] Scan for BLE devices
- [ ] Verify VESC Express appears in scan results
- [ ] Connect to VESC Express via BLE
- [ ] Verify connection time < 2 seconds
- [ ] Send test commands
- [ ] Monitor data transfer rate
- [ ] Test background operation (minimize app)
- [ ] Verify reconnection after app returns to foreground

### 3. WiFi Testing
- [ ] Configure WiFi credentials in VESC Express
- [ ] Connect Android device to same network
- [ ] Connect VESC Tool to VESC Express via WiFi
- [ ] Test data transfer
- [ ] Switch between BLE and WiFi
- [ ] Test concurrent BLE/WiFi operation

### 4. Android Version Specific Tests

#### Android 12+ (API 31+)
- [ ] Verify app requests BLUETOOTH_SCAN permission
- [ ] Verify app requests BLUETOOTH_CONNECT permission
- [ ] Test with location services disabled
- [ ] Verify neverForLocation flag works correctly

#### Android 13+ (API 33+)
- [ ] Test media permissions if using file access
- [ ] Verify notification permissions (if applicable)

#### Android 15 (API 35)
- [ ] Test all new permission models
- [ ] Verify no deprecated API warnings
- [ ] Test background BLE scanning restrictions

## Performance Testing

### BLE Performance
- [ ] Connection establishment time: Target < 3s
- [ ] Data throughput: Target > 50KB/s
- [ ] Packet loss rate: Target < 1%
- [ ] Connection stability over 1 hour

### WiFi Performance
- [ ] Connection establishment time: Target < 5s
- [ ] Data throughput: Target > 1MB/s
- [ ] Latency: Target < 50ms
- [ ] Connection stability over 1 hour

### Power Consumption
- [ ] Measure idle current with BLE advertising
- [ ] Measure active BLE connection current
- [ ] Measure WiFi connection current
- [ ] Verify average < 50mA

## Compatibility Testing

### Device Testing Matrix
Test on at least one device from each Android version:

- [ ] Android 8.0 (API 26)
- [ ] Android 9.0 (API 28)
- [ ] Android 10 (API 29)
- [ ] Android 11 (API 30)
- [ ] Android 12 (API 31)
- [ ] Android 13 (API 33)
- [ ] Android 14 (API 34)
- [ ] Android 15 (API 35) - if available

### Manufacturer Specific Testing
Test on devices from different manufacturers:

- [ ] Samsung
- [ ] Google Pixel
- [ ] OnePlus
- [ ] Xiaomi
- [ ] Other

## Error Handling

### Connection Failures
- [ ] Test BLE connection with Bluetooth disabled
- [ ] Test WiFi connection with wrong password
- [ ] Test connection timeout handling
- [ ] Test graceful disconnection

### Permission Denials
- [ ] Test app behavior when BLE permissions denied
- [ ] Test app behavior when location permission denied
- [ ] Verify appropriate error messages

## Security Testing

### BLE Security
- [ ] Verify pairing process works correctly
- [ ] Test encrypted communication
- [ ] Verify no sensitive data in advertisements

### WiFi Security
- [ ] Test WPA2 connection
- [ ] Test WPA3 connection (if available)
- [ ] Verify certificate validation (if applicable)

## Regression Testing

### Existing Features
- [ ] Verify all existing VESC Tool features work
- [ ] Test motor control commands
- [ ] Test configuration read/write
- [ ] Test firmware updates
- [ ] Test data logging

## Debug Information

### Logs to Collect
- ESP32 serial output
- Android logcat during testing
- VESC Tool debug logs
- BLE HCI snoop logs (if needed)

### Common Issues and Solutions

1. **BLE Connection Fails**
   - Check Android Bluetooth settings
   - Verify permissions granted
   - Try clearing Bluetooth cache

2. **WiFi Connection Fails**
   - Verify network credentials
   - Check firewall settings
   - Ensure devices on same network

3. **Poor Performance**
   - Check for interference
   - Verify power supply adequate
   - Monitor CPU usage

## Sign-off

- [ ] All tests passed
- [ ] Performance targets met
- [ ] No critical bugs found
- [ ] Documentation updated
- [ ] Ready for release

---
*Testing Date: _______________*
*Tester: _______________*
*Version: VESC Express with Android 15 compatibility*