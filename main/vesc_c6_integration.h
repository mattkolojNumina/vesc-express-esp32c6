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

#ifndef VESC_C6_INTEGRATION_H_
#define VESC_C6_INTEGRATION_H_

#include <stdbool.h>
#include <stdint.h>

#ifdef CONFIG_IDF_TARGET_ESP32C6

// VESC ESP32-C6 integration configuration
typedef struct {
    bool enhanced_ble_enable;           // Enable ESP32-C6 BLE enhancements
    bool enhanced_wifi_enable;          // Enable ESP32-C6 WiFi 6 enhancements
    bool power_optimization_enable;     // Enable power optimization for VESC
    bool android_compatibility;         // Enable Android compatibility mode
    bool preserve_vesc_protocols;       // Always preserve VESC core protocols
    uint8_t performance_mode;           // 0=conservative, 1=balanced, 2=maximum
} vesc_c6_integration_config_t;

// Default integration configuration (safe for VESC operations)
#define VESC_C6_INTEGRATION_CONFIG_DEFAULT() { \
    .enhanced_ble_enable = true, \
    .enhanced_wifi_enable = true, \
    .power_optimization_enable = true, \
    .android_compatibility = true, \
    .preserve_vesc_protocols = true, \
    .performance_mode = 1, \
}

// Conservative configuration for maximum compatibility
#define VESC_C6_INTEGRATION_CONFIG_CONSERVATIVE() { \
    .enhanced_ble_enable = false, \
    .enhanced_wifi_enable = false, \
    .power_optimization_enable = true, \
    .android_compatibility = true, \
    .preserve_vesc_protocols = true, \
    .performance_mode = 0, \
}

// High performance configuration (when VESC protocols allow)
#define VESC_C6_INTEGRATION_CONFIG_PERFORMANCE() { \
    .enhanced_ble_enable = true, \
    .enhanced_wifi_enable = true, \
    .power_optimization_enable = true, \
    .android_compatibility = true, \
    .preserve_vesc_protocols = true, \
    .performance_mode = 2, \
}

// Function declarations
void vesc_c6_integration_init(void);
bool vesc_c6_configure_integration(const vesc_c6_integration_config_t *config);

// Component configuration functions
void vesc_c6_configure_enhanced_ble(void);
void vesc_c6_configure_enhanced_wifi(void);
void vesc_c6_configure_power_optimization(void);
void vesc_c6_optimize_for_android(void);

// Status and monitoring functions
bool vesc_c6_check_compatibility(void);
void vesc_c6_print_status(void);
bool vesc_c6_is_integration_ready(void);

// Safety functions
void vesc_c6_emergency_safe_mode(void);

#else
// Stub functions for non-C6 targets
static inline void vesc_c6_integration_init(void) {}
static inline bool vesc_c6_configure_integration(const void *config) { return false; }
static inline void vesc_c6_configure_enhanced_ble(void) {}
static inline void vesc_c6_configure_enhanced_wifi(void) {}
static inline void vesc_c6_configure_power_optimization(void) {}
static inline void vesc_c6_optimize_for_android(void) {}
static inline bool vesc_c6_check_compatibility(void) { return true; }
static inline void vesc_c6_print_status(void) {}
static inline bool vesc_c6_is_integration_ready(void) { return false; }
static inline void vesc_c6_emergency_safe_mode(void) {}
#endif

#endif /* VESC_C6_INTEGRATION_H_ */