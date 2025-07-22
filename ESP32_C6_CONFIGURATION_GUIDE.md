# ESP32-C6 Configuration Guide for VESC Express

This guide provides comprehensive information for configuring and using ESP32-C6 with VESC Express firmware.

## Table of Contents
1. [Hardware Configuration](#hardware-configuration)
2. [Build Configuration](#build-configuration)
3. [WiFi 6 Features](#wifi-6-features)
4. [Bluetooth 5.3 Features](#bluetooth-53-features)
5. [IEEE 802.15.4 Support](#ieee-80215-4-support)
6. [Power Management](#power-management)
7. [Android Compatibility](#android-compatibility)
8. [GPIO Configuration](#gpio-configuration)
9. [Troubleshooting](#troubleshooting)

## Hardware Configuration

### Selecting ESP32-C6 Hardware
To build for ESP32-C6, modify `main/conf_general.h`:

```c
// Comment out the default hardware
//#define HW_HEADER					"hw_xp_t.h"
//#define HW_SOURCE					"hw_xp_t.c"

// Enable ESP32-C6 DevKit hardware
#define HW_HEADER					"hw_devkit_c6.h"
#define HW_SOURCE					"hw_devkit_c6.c"
```

Or use environment variables:
```bash
export HW_SRC=main/hwconf/hw_devkit_c6.c
export HW_HEADER=main/hwconf/hw_devkit_c6.h
```

### ESP32-C6 Pin Configuration
The ESP32-C6 DevKit configuration includes:
- **RGB LED**: GPIO8
- **ADC Channels**: GPIO0-3 (ADC1_CH0-3)
- **User GPIOs**: GPIO6, 7, 10, 11
- **Strapping Pins**: GPIO4, 5, 8, 9, 15 (use with caution)
- **SPI Flash**: GPIO24-30 (avoid for general use)
- **USB-JTAG**: GPIO12, 13

## Build Configuration

### ESP-IDF Target Configuration
```bash
# Set target to ESP32-C6
idf.py set-target esp32c6

# Configure project
idf.py menuconfig
```

### Important ESP-IDF Settings
In `idf.py menuconfig`:

1. **Component config → Wi-Fi**:
   - Enable "WiFi 6 support (802.11ax)"
   - Set "WiFi Task Core ID" to 0
   - Configure "WiFi AMPDU TX/RX" for better performance

2. **Component config → Bluetooth**:
   - Enable "Bluetooth"
   - Select "Bluetooth controller mode" → "BLE Only"
   - Enable "BLE 5.0 features"

3. **Component config → IEEE 802.15.4**:
   - Enable "IEEE 802.15.4"
   - Configure coexistence settings

4. **Component config → Power Management**:
   - Enable "Support for power management"
   - Configure "Power down MAC and baseband of Wi-Fi and Bluetooth"

### Build Commands
```bash
# Full build for ESP32-C6
idf.py build

# Flash firmware
idf.py flash

# Monitor output
idf.py monitor
```

## WiFi 6 Features

### Automatic WiFi 6 Support
WiFi 6 features are enabled automatically when connecting to WiFi 6 access points:
- **OFDMA**: Uplink and downlink support
- **MU-MIMO**: Downlink support
- **BSS Color**: Automatic configuration
- **20MHz bandwidth**: 802.11ax mode

### Target Wake Time (TWT) Configuration
```c
#include "wifi_c6_enhancements.h"

wifi_c6_config_t wifi_config = WIFI_C6_CONFIG_DEFAULT();
wifi_config.twt_enable = true;
wifi_config.twt_wake_interval_us = 65536;  // 65.536ms intervals
wifi_config.twt_wake_duration_us = 32768;  // 32.768ms wake duration

wifi_c6_configure_twt(&wifi_config);
```

### WiFi 6 Initialization
```c
void app_main() {
    // Initialize WiFi 6 enhancements
    wifi_c6_init_enhancements();
    
    // Enable power save features
    wifi_c6_enable_power_save_features();
    
    // Check if connected to WiFi 6 AP
    if (wifi_c6_is_wifi6_connected()) {
        ESP_LOGI("WIFI", "Connected to WiFi 6 access point");
        wifi_c6_print_connection_info();
    }
}
```

## Bluetooth 5.3 Features

### Enhanced BLE Configuration
```c
#include "ble_c6_enhancements.h"

// Android-optimized configuration
ble_c6_config_t ble_config = BLE_C6_ANDROID_CONFIG();

// Or custom configuration
ble_c6_config_t custom_config = {
    .extended_advertising = true,
    .coded_phy = true,  // Enable long-range
    .adv_interval_min = 160,  // 100ms
    .adv_interval_max = 400,  // 250ms
    .tx_power_level = 0,      // 0 dBm
    .connection_interval_min = 16,  // 20ms
    .connection_interval_max = 32,  // 40ms
};

ble_c6_configure_features(&custom_config);
```

### BLE 5.3 Features
- **Extended Advertising**: Up to 1650 bytes payload
- **Coded PHY**: Up to 4x range improvement
- **2 Mbps PHY**: High throughput mode
- **Channel Selection Algorithm #2**: Improved reliability
- **Android Compatibility**: Optimized parameters

### Initialization
```c
void app_main() {
    // Initialize BLE 5.3 enhancements
    ble_c6_init_enhancements();
    
    // Apply Android compatibility settings
    ble_c6_optimize_for_android();
    
    // Print capabilities
    ble_c6_print_capabilities();
}
```

## IEEE 802.15.4 Support

### Basic 802.15.4 Configuration
```c
#include "ieee802154_c6.h"

ieee802154_config_t config = IEEE802154_CONFIG_DEFAULT();
config.enable_802154 = true;
config.channel = 15;
config.pan_id = 0xABCD;
config.short_addr = 0x1234;

ieee802154_init();
ieee802154_configure(&config);
ieee802154_start();
```

### Thread Network Configuration
```c
thread_config_t thread_config = THREAD_CONFIG_DEFAULT();
thread_config.enable_thread = true;
strcpy(thread_config.network_name, "VESC-Network");
thread_config.network_channel = 15;

thread_init(&thread_config);
thread_start_network();
```

### Zigbee Configuration
```c
zigbee_config_t zigbee_config = ZIGBEE_CONFIG_DEFAULT();
zigbee_config.enable_zigbee = true;
zigbee_config.coordinator_mode = true;

zigbee_init(&zigbee_config);
zigbee_start_network();
```

### Coexistence with WiFi/BLE
```c
// Enable coexistence for optimal performance
ieee802154_coexist_with_wifi_ble(true);
```

## Power Management

### Power Management Configuration
```c
#include "power_management_c6.h"

// Ultra-low power configuration
pm_c6_config_t pm_config = PM_C6_ULTRA_LOW_POWER_CONFIG();

// Custom configuration
pm_c6_config_t custom_config = {
    .default_mode = PM_C6_MODE_LIGHT_SLEEP,
    .auto_light_sleep = true,
    .wifi_twt_enable = true,
    .ble_power_save = true,
    .cpu_freq_mhz = 80,
    .gpio_hold_mask = 0xFF,  // Hold all GPIOs during sleep
};

pm_c6_configure(&custom_config);
```

### Power Modes
- **PM_C6_MODE_ACTIVE**: Full performance (45mA)
- **PM_C6_MODE_MODEM_SLEEP**: CPU active, radio sleep (15mA)
- **PM_C6_MODE_LIGHT_SLEEP**: CPU and radio sleep (5mA)
- **PM_C6_MODE_DEEP_SLEEP**: Minimal power (15µA)
- **PM_C6_MODE_ULTRA_LOW_POWER**: Battery optimized (2mA)

### Sleep Functions
```c
// Enter light sleep for 10 seconds
pm_c6_enter_light_sleep(10000);

// Configure wake sources
pm_c6_configure_wake_source(PM_C6_WAKE_GPIO, 5);  // GPIO5 wake
pm_c6_configure_wake_source(PM_C6_WAKE_TIMER, 30000);  // 30s timer

// GPIO hold during sleep
pm_c6_gpio_hold_enable(8);  // Hold RGB LED state
```

### Power Monitoring
```c
// Get power consumption estimate
uint32_t consumption = pm_c6_get_power_consumption_estimate();
ESP_LOGI("POWER", "Estimated consumption: %lu mA", consumption);

// Print detailed power statistics
pm_c6_print_power_stats();
```

## Android Compatibility

### Optimized Android Configuration
The firmware includes specific optimizations for Android devices:

```c
#include "android_compat.h"

// Set Android compatibility mode
android_compat_set_mode(ANDROID_COMPAT_OPTIMIZED);

// BLE optimizations for Android
ble_c6_optimize_for_android();

// WiFi optimizations
wifi_c6_enable_power_save_features();
```

### Android Compatibility Features
- **BLE Advertisement Intervals**: 100-250ms (Android-friendly)
- **Connection Parameters**: 20-40ms intervals
- **PMF Support**: Protected Management Frames for WiFi security
- **Power Management**: Optimized for Android power saving
- **Coexistence**: Enhanced BLE/WiFi coexistence

### Testing Android Compatibility
```c
// Run compatibility tests
if (android_compat_test_ble() && android_compat_test_wifi()) {
    ESP_LOGI("ANDROID", "All compatibility tests passed");
} else {
    ESP_LOGW("ANDROID", "Some compatibility issues detected");
}
```

## GPIO Configuration

### ESP32-C6 GPIO Restrictions
```c
// Safe GPIOs for general use
#define SAFE_GPIO_0    0   // ADC1_CH0
#define SAFE_GPIO_1    1   // ADC1_CH1
#define SAFE_GPIO_2    2   // ADC1_CH2
#define SAFE_GPIO_3    3   // ADC1_CH3
#define SAFE_GPIO_6    6   // General purpose
#define SAFE_GPIO_7    7   // General purpose
#define SAFE_GPIO_10   10  // General purpose
#define SAFE_GPIO_11   11  // General purpose

// Strapping pins (use with caution)
#define STRAPPING_GPIO_4   4
#define STRAPPING_GPIO_5   5
#define STRAPPING_GPIO_8   8   // Also RGB LED
#define STRAPPING_GPIO_9   9
#define STRAPPING_GPIO_15  15

// Reserved pins (avoid)
#define RESERVED_GPIO_12   12  // USB D-
#define RESERVED_GPIO_13   13  // USB D+
// GPIO24-30 reserved for SPI flash
```

### GPIO Hold Configuration
```c
// Hold GPIO states during sleep
pm_c6_gpio_hold_enable(8);  // Hold RGB LED
pm_c6_gpio_hold_enable(6);  // Hold user GPIO

// Or hold multiple GPIOs
pm_c6_config_t config = {
    .gpio_hold_mask = 0b11000001,  // Hold GPIO0, 6, 7
};
```

## Troubleshooting

### Common Build Issues

#### 1. Target Configuration
```bash
# If build fails, ensure correct target
idf.py set-target esp32c6
idf.py fullclean
idf.py build
```

#### 2. Memory Issues
If running out of memory, adjust partition table:
```csv
# partitions_esp32c6.csv
nvs,      data, nvs,     0x9000,  0x6000,
otadata,  data, ota,     0xf000,  0x2000,
app0,     app,  ota_0,   0x20000, 0x180000,
app1,     app,  ota_1,   0x1A0000,0x180000,
lisp,     data, nvs,     0x320000,0x60000,
qml,      data, nvs,     0x380000,0x20000,
coredump, data, coredump,0x3A0000,0x60000,
```

#### 3. Compilation Errors
```bash
# For missing headers
export IDF_PATH=/path/to/esp-idf
source $IDF_PATH/export.sh

# For Bluetooth header issues
idf.py menuconfig
# Component config → Bluetooth → Enable
```

### Runtime Issues

#### 1. WiFi 6 Not Working
- Ensure access point supports WiFi 6
- Check ESP-IDF version (≥5.2 recommended)
- Verify WiFi 6 is enabled in menuconfig

#### 2. BLE Connection Issues
- Check Android version (≥8.0 recommended)
- Verify BLE permissions in Android app
- Use `ble_c6_optimize_for_android()`

#### 3. Power Consumption Higher Than Expected
- Verify power management configuration
- Check for active peripherals
- Enable all available power saving features

#### 4. 802.15.4 Not Working
- Ensure IEEE 802.15.4 is enabled in menuconfig
- Check channel conflicts with WiFi
- Verify coexistence configuration

### Debug Commands
```bash
# Monitor with filters
idf.py monitor --port /dev/ttyACM0 --baud 115200

# Enable debug logs
idf.py menuconfig
# Component config → Log output → Default log verbosity → Debug

# Flash with debugging
idf.py flash monitor
```

### Performance Optimization
1. **CPU Frequency**: Use 160MHz for performance, 80MHz for power saving
2. **WiFi Power Save**: Enable for battery operation
3. **BLE Parameters**: Optimize connection intervals for your use case
4. **Coexistence**: Enable for multi-protocol operation
5. **Peripheral Retention**: Enable to maintain state across sleep

### Support Resources
- ESP32-C6 Technical Reference Manual
- ESP-IDF Programming Guide
- ESP32-C6 Examples in ESP-IDF
- VESC Express GitHub Repository
- ESP32 Forum Community

This guide covers the essential aspects of ESP32-C6 configuration for VESC Express. For specific use cases or advanced configurations, refer to the individual module documentation and ESP-IDF examples.