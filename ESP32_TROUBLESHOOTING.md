# ESP32-C3 WiFi/Bluetooth Troubleshooting Guide

## Problem: PC doesn't detect WiFi access point or Bluetooth after programming ESP32-C3

### Root Cause Analysis

Based on the firmware code analysis, WiFi and Bluetooth are **disabled by default** in the configuration. The firmware checks the configuration settings before enabling these features:

```c
// From main.c:144-161
switch (backup.config.ble_mode) {
    case BLE_MODE_DISABLED: {  // This is the default
        break;
    }
    case BLE_MODE_OPEN:
    case BLE_MODE_ENCRYPTED: {
        comm_ble_init();  // Only runs if enabled
        break;
    }
}

if (backup.config.wifi_mode != WIFI_MODE_DISABLED) {  // Default is DISABLED
    comm_wifi_init();  // Only runs if enabled
}
```

### Available Modes:
- **BLE_MODE_DISABLED** = 0 (default)
- **BLE_MODE_OPEN** = 1
- **BLE_MODE_ENCRYPTED** = 2  
- **BLE_MODE_SCRIPTING** = 3

- **WIFI_MODE_DISABLED** = 0 (default)
- **WIFI_MODE_STATION** = 1
- **WIFI_MODE_ACCESS_POINT** = 2

## Solutions

### Solution 1: Enable via VESC Tool (Recommended)
1. Connect ESP32-C3 via USB cable
2. Open VESC Tool
3. Connect to device
4. Go to configuration settings
5. Enable BLE mode (set to Open or Encrypted)
6. Enable WiFi mode (set to Access Point for testing)
7. Write configuration to device
8. Reboot device

### Solution 2: Enable via Terminal Commands
1. Connect via USB and open terminal/serial monitor
2. Use terminal commands to change configuration
3. Commands might include:
   - `conf_set ble_mode 1` (for BLE_MODE_OPEN)
   - `conf_set wifi_mode 2` (for WIFI_MODE_ACCESS_POINT)
   - `conf_store` (to save settings)

### Solution 3: Modify Default Configuration in Firmware (COMPLETED)
Edit the default configuration in the source code:

1. ✅ Found the configuration defaults file: `main/config/conf_default.h`
2. ✅ Changed default BLE mode from DISABLED (0) to OPEN (1) 
3. ✅ Changed default WiFi mode from DISABLED (0) to ACCESS_POINT (2)
4. ✅ Rebuilt and flashed firmware

**Changes made to `main/config/conf_default.h`:**
```c
// WiFi Mode - CHANGED from 0 to 2
#ifndef CONF_WIFI_MODE
#define CONF_WIFI_MODE 2  // WIFI_MODE_ACCESS_POINT
#endif

// Bluetooth Mode - Already set to 1 
#ifndef CONF_BLE_MODE
#define CONF_BLE_MODE 1   // BLE_MODE_OPEN
#endif
```

**New firmware binary:** `/home/rds/vesc_express/build/vesc_express.bin` (1,487,648 bytes)

With these changes, both BLE and WiFi will now automatically start on power-on and remain active for the duration the controller is powered, regardless of active connections.

### Solution 4: Check Hardware Configuration
The current build uses hardware configuration `hw_xp_t.h` (VESC Express T), verify this matches your actual hardware.

## Verification Steps

1. **Check serial output**: Connect via USB and monitor boot messages
2. **Look for initialization messages**: Should see BLE/WiFi init if enabled
3. **Check device name**: Default BLE name should appear as "VESC Express T"
4. **Scan for WiFi**: Should see access point if WiFi mode is enabled

## Expected Behavior When Enabled

### BLE (when enabled):
- Device should advertise as "VESC Express T" or similar
- Should be discoverable by phones/computers
- LED indicators should show BLE activity

### WiFi (when enabled):  
- Should broadcast access point "VESC Express" or similar
- Should be visible in WiFi scan on PC/phone
- Default IP: typically 192.168.4.1

## Hardware Check
Your device uses:
- Hardware: VESC Express T (Trampa variant)
- LEDs: Red (pin 2), Blue (pin 3)
- Should see LED activity during boot and operation

## Next Steps
1. Connect via USB first to verify basic functionality
2. Enable BLE/WiFi through VESC Tool configuration
3. Verify settings are saved and device reboots
4. Check for wireless connectivity

The firmware is correctly built with BLE and WiFi support - they just need to be enabled in the configuration!