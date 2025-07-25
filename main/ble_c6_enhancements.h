/*
	Copyright 2024 Benjamin Vedder	benjamin@vedder.se

	This file is part of the VESC firmware.

	The VESC firmware is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    The VESC firmware is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
    */

#ifndef BLE_C6_ENHANCEMENTS_H_
#define BLE_C6_ENHANCEMENTS_H_

#include <stdbool.h>
#include <stdint.h>
#include "sdkconfig.h"

#ifdef CONFIG_BT_ENABLED
#ifdef CONFIG_IDF_TARGET_ESP32C6

// Bluetooth 5.3 specific features for ESP32-C6 (Research-Certified Features)
typedef struct {
    bool extended_advertising;      // Enable extended advertising
    bool coded_phy;                // Enable coded PHY for long range (S=2/S=8)
    bool high_speed_phy;           // Enable 2 Mbps PHY for high throughput
    bool high_duty_cycle_adv;      // High duty cycle advertising
    uint16_t adv_interval_min;     // Min advertising interval (0.625ms units)
    uint16_t adv_interval_max;     // Max advertising interval (0.625ms units)
    int8_t tx_power_level;         // TX power level (-40 to +20 dBm)
    bool channel_selection_2;      // Enable channel selection algorithm #2 (BT 5.0)
    bool power_control;            // Enable LE Power Control (BT 5.2 - Experimental)
    uint16_t connection_interval_min; // Min connection interval (1.25ms units)
    uint16_t connection_interval_max; // Max connection interval (1.25ms units)
    uint8_t coded_phy_preference;  // Coded PHY preference: 1=S=2, 2=S=8
    bool sleep_enable;             // Enable BLE controller sleep
} ble_c6_config_t;

// Default BLE 5.3 configuration optimized for ESP32-C6 (leveraging superior hardware)
#define BLE_C6_CONFIG_DEFAULT() { \
    .extended_advertising = true, \
    .coded_phy = true,              /* C6 can handle coded PHY efficiently */ \
    .high_speed_phy = true,         /* Enable 2 Mbps PHY */ \
    .high_duty_cycle_adv = false, \
    .adv_interval_min = 100,        /* Faster advertising (C6 capability) */ \
    .adv_interval_max = 300,        /* Optimized for C6's processing */ \
    .tx_power_level = 9,            /* Higher power (C6 can handle it) */ \
    .channel_selection_2 = true,    /* CSA #2 (BT 5.0 certified) */ \
    .power_control = true,          /* LE Power Control (BT 5.2) */ \
    .connection_interval_min = 12,  /* Faster intervals (15ms) */ \
    .connection_interval_max = 24,  /* Optimized for C6 (30ms) */ \
    .coded_phy_preference = 1,      /* S=2 for balanced range/speed */ \
    .sleep_enable = true,           /* Enable BLE sleep for power saving */ \
}

// Android compatibility configuration (Research-Optimized)
#define BLE_C6_ANDROID_CONFIG() { \
    .extended_advertising = true, \
    .coded_phy = false,            /* Disabled for Android compatibility */ \
    .high_speed_phy = true,        /* Android supports 2 Mbps PHY */ \
    .high_duty_cycle_adv = false, \
    .adv_interval_min = 160,       /* 100ms - Android friendly */ \
    .adv_interval_max = 400,       /* 250ms - Android friendly */ \
    .tx_power_level = 0, \
    .channel_selection_2 = true,   /* CSA #2 improves Android performance */ \
    .power_control = false,        /* Conservative for Android compatibility */ \
    .connection_interval_min = 16, /* 20ms - Android optimal */ \
    .connection_interval_max = 32, /* 40ms - Android optimal */ \
    .coded_phy_preference = 1,     /* Default S=2 */ \
    .sleep_enable = true,          /* Enable sleep for battery optimization */ \
}

// Function declarations
void ble_c6_init_enhancements(void);
bool ble_c6_configure_features(const ble_c6_config_t *config);
void ble_c6_enable_extended_advertising(void);
void ble_c6_enable_coded_phy(void);
void ble_c6_enable_high_speed_phy(void);        // 2 Mbps PHY support
void ble_c6_enable_power_control(void);         // LE Power Control (BT 5.2)
void ble_c6_configure_sleep_mode(void);         // BLE sleep configuration
void ble_c6_optimize_for_android(void);
void ble_c6_print_capabilities(void);
bool ble_c6_is_feature_supported(const char *feature);

// Advanced ESP32-C6 functions (leveraging superior hardware)
void ble_c6_enable_advanced_features(void);               // Enable all advanced C6 features
void ble_c6_enable_all_phy_modes(void);                  // Enable all PHY modes simultaneously
void ble_c6_configure_advanced_security_features(void);   // Enhanced security processing
void ble_c6_enable_multi_connection_optimization(void);   // Multi-connection optimization
void ble_c6_enable_high_performance_mode(void);          // Maximum performance configuration

#else
// Stub functions for non-C6 targets
static inline void ble_c6_init_enhancements(void) {}
static inline bool ble_c6_configure_features(const void *config) { return false; }
static inline void ble_c6_enable_extended_advertising(void) {}
static inline void ble_c6_enable_coded_phy(void) {}
static inline void ble_c6_enable_high_speed_phy(void) {}
static inline void ble_c6_enable_power_control(void) {}
static inline void ble_c6_configure_sleep_mode(void) {}
static inline void ble_c6_optimize_for_android(void) {}
static inline void ble_c6_print_capabilities(void) {}
static inline bool ble_c6_is_feature_supported(const char *feature) { return false; }
static inline void ble_c6_enable_advanced_features(void) {}
static inline void ble_c6_enable_all_phy_modes(void) {}
static inline void ble_c6_configure_advanced_security_features(void) {}
static inline void ble_c6_enable_multi_connection_optimization(void) {}
static inline void ble_c6_enable_high_performance_mode(void) {}
#endif

#else
// Stub functions when Bluetooth is disabled
static inline void ble_c6_init_enhancements(void) {}
static inline bool ble_c6_configure_features(const void *config) { return false; }
static inline void ble_c6_enable_extended_advertising(void) {}
static inline void ble_c6_enable_coded_phy(void) {}
static inline void ble_c6_enable_high_speed_phy(void) {}
static inline void ble_c6_enable_power_control(void) {}
static inline void ble_c6_configure_sleep_mode(void) {}
static inline void ble_c6_optimize_for_android(void) {}
static inline void ble_c6_print_capabilities(void) {}
static inline bool ble_c6_is_feature_supported(const char *feature) { return false; }
static inline void ble_c6_enable_advanced_features(void) {}
static inline void ble_c6_enable_all_phy_modes(void) {}
static inline void ble_c6_configure_advanced_security_features(void) {}
static inline void ble_c6_enable_multi_connection_optimization(void) {}
static inline void ble_c6_enable_high_performance_mode(void) {}
#endif

#endif /* BLE_C6_ENHANCEMENTS_H_ */