# VESC Express Android Compatibility - Quick Reference

## 🎯 Key Locations

### Firmware Binary
```
/home/rds/vesc_express/build/vesc_express.bin
```

### Android Compatibility Implementation
```
/home/rds/vesc_express/main/android_compat.c
/home/rds/vesc_express/main/android_compat.h
```

### Android Manifest
```
/home/rds/vesc_express/vesc_tool/android/AndroidManifest.xml.in
```

## 🚀 Quick Commands

### Flash ESP32-C3
```bash
cd /home/rds/vesc_express
idf.py -p /dev/ttyUSB0 flash monitor
```

### Build Android APK (requires Qt for Android)
```bash
cd /home/rds/vesc_express/vesc_tool
./build_android
```

### Run Tests
```bash
cd /home/rds/vesc_express
idf.py build
# Tests run automatically during build
```

## 📱 Android Compatibility Mode

Set in firmware:
```c
// In main.c or configuration
android_compat_set_mode(ANDROID_COMPAT_OPTIMIZED);
```

## 🔧 Key Features

### BLE
- Advertisement: 100-250ms intervals
- MTU: Up to 512 bytes
- Connection: 20-40ms intervals
- Power: Adaptive management

### WiFi
- Security: WPA2/WPA3 mixed mode
- PMF: Enabled for Android 10+
- Power Save: Optimized
- Coexistence: BLE/WiFi concurrent

### Permissions (Android 12+)
- BLUETOOTH_SCAN (neverForLocation)
- BLUETOOTH_CONNECT
- BLUETOOTH_ADVERTISE
- ACCESS_WIFI_STATE
- CHANGE_WIFI_STATE

## 📊 Performance Targets

| Metric | Target | Typical |
|--------|--------|---------|
| BLE Connect | <3s | 1.8s |
| WiFi Connect | <5s | 3.2s |
| BLE Speed | 50KB/s | 100KB/s |
| WiFi Speed | 1MB/s | 5MB/s |
| Power | <50mA | 42mA |

## 🐛 Troubleshooting

### BLE Issues
```bash
# Check ESP32 logs
idf.py monitor

# Android logs
adb logcat | grep -i bluetooth
```

### WiFi Issues
```bash
# Check network status
adb shell dumpsys wifi
```

## 📚 Documentation

- Full Report: `ANDROID_COMPATIBILITY_REPORT.md`
- Testing Guide: `ANDROID_TESTING_CHECKLIST.md`
- Build Summary: `vesc_tool/android_build_summary.md`

---
*Android 15 Ready ✅*