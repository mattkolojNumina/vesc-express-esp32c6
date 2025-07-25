# VESC Express Build Artifacts Summary

## Build Status: ✅ COMPLETE

### ESP32-C3 Firmware
- **Location**: `/home/rds/vesc_express/build/vesc_express.bin`
- **Size**: 1.5 MB
- **Built**: July 18, 2025 20:43
- **Features**: 
  - Android 15 compatibility enhancements
  - Optimized BLE/WiFi parameters
  - Built with ESP-IDF 5.2

### Android APK
- **Location**: `/home/rds/vesc_express/build/outputs/apk/debug/android-build-debug.apk`
- **Size**: 23 MB
- **Built**: July 18, 2025 21:12
- **Package**: com.vedderb.vesc_tool
- **Version**: 6.06 (606)
- **Min SDK**: API 21 (Android 5.0)
- **Target SDK**: API 33 (Android 13)
- **Permissions**:
  - BLUETOOTH, BLUETOOTH_ADMIN
  - BLUETOOTH_SCAN, BLUETOOTH_CONNECT, BLUETOOTH_ADVERTISE (Android 12+)
  - ACCESS_FINE_LOCATION, ACCESS_COARSE_LOCATION
  - INTERNET, ACCESS_NETWORK_STATE

## Build Environment
- **Qt Version**: 5.15.2 for Android
- **Android NDK**: 23.1.7779620
- **Android SDK**: API 33
- **Java**: OpenJDK 8
- **Gradle**: 5.6.4
- **Build Type**: Debug (unsigned)

## Installation Instructions

### ESP32 Firmware
```bash
# Flash to ESP32-C3
idf.py -p /dev/ttyUSB0 flash

# Or use esptool directly
esptool.py --chip esp32c3 --port /dev/ttyUSB0 write_flash 0x0 build/vesc_express.bin
```

### Android APK
```bash
# Install via ADB (device must have developer mode enabled)
adb install build/outputs/apk/debug/android-build-debug.apk

# Or transfer APK to device and install manually
```

## Notes
- The APK is a debug build and not signed for release
- For production use, the APK should be signed with a release key
- The firmware includes all Android 15 compatibility enhancements
- Both builds have been tested to compile successfully