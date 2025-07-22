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

#ifndef POWER_MANAGEMENT_C6_H_
#define POWER_MANAGEMENT_C6_H_

#include <stdbool.h>
#include <stdint.h>

#ifdef CONFIG_IDF_TARGET_ESP32C6

// ESP32-C6 specific power management features
typedef enum {
    PM_C6_MODE_ACTIVE,              // Full performance mode
    PM_C6_MODE_MODEM_SLEEP,         // CPU active, radio sleep
    PM_C6_MODE_LIGHT_SLEEP,         // CPU and radio sleep, fast wake
    PM_C6_MODE_DEEP_SLEEP,          // Minimal power, slow wake
    PM_C6_MODE_ULTRA_LOW_POWER,     // Optimized for battery operation
} pm_c6_mode_t;

// Power management configuration
typedef struct {
    pm_c6_mode_t default_mode;      // Default power mode
    bool auto_light_sleep;          // Enable automatic light sleep
    bool wifi_twt_enable;           // Enable WiFi TWT power saving
    bool ble_power_save;            // Enable BLE power saving
    bool peripheral_retention;     // Enable peripheral state retention
    uint32_t light_sleep_threshold_ms; // Threshold for light sleep entry
    uint32_t cpu_freq_mhz;          // CPU frequency (80/160 MHz)
    bool dynamic_freq_scaling;      // Enable dynamic frequency scaling
    uint8_t gpio_hold_mask;         // GPIO pins to hold during sleep
} pm_c6_config_t;

// Default power management configuration (leveraging ESP32-C6 capabilities)
#define PM_C6_CONFIG_DEFAULT() { \
    .default_mode = PM_C6_MODE_ACTIVE, \
    .auto_light_sleep = true, \
    .wifi_twt_enable = true,            /* C6 has better WiFi 6/TWT support */ \
    .ble_power_save = true, \
    .peripheral_retention = true, \
    .light_sleep_threshold_ms = 50,     /* Faster response due to C6's power */ \
    .cpu_freq_mhz = 160,               /* C6 handles 160MHz efficiently */ \
    .dynamic_freq_scaling = true, \
    .gpio_hold_mask = 0, \
}

// Ultra-low power configuration for battery operation
#define PM_C6_ULTRA_LOW_POWER_CONFIG() { \
    .default_mode = PM_C6_MODE_ULTRA_LOW_POWER, \
    .auto_light_sleep = true, \
    .wifi_twt_enable = true, \
    .ble_power_save = true, \
    .peripheral_retention = true, \
    .light_sleep_threshold_ms = 50, \
    .cpu_freq_mhz = 80, \
    .dynamic_freq_scaling = true, \
    .gpio_hold_mask = 0xFF, \
}

// Sleep wake sources
typedef enum {
    PM_C6_WAKE_TIMER,               // Timer wake up
    PM_C6_WAKE_GPIO,                // GPIO wake up
    PM_C6_WAKE_UART,                // UART wake up
    PM_C6_WAKE_WIFI,                // WiFi wake up (TWT)
    PM_C6_WAKE_BLE,                 // BLE wake up
    PM_C6_WAKE_TOUCH,               // Touch wake up
    PM_C6_WAKE_ULP,                 // ULP coprocessor wake up
} pm_c6_wake_source_t;

// Function declarations
void pm_c6_init(void);
bool pm_c6_configure(const pm_c6_config_t *config);
void pm_c6_set_mode(pm_c6_mode_t mode);
pm_c6_mode_t pm_c6_get_mode(void);

// Sleep functions
void pm_c6_enter_light_sleep(uint32_t duration_ms);
void pm_c6_enter_deep_sleep(uint32_t duration_ms);
void pm_c6_configure_wake_source(pm_c6_wake_source_t source, uint32_t param);

// Power optimization functions
void pm_c6_enable_wifi_power_save(bool enable);
void pm_c6_enable_ble_power_save(bool enable);
void pm_c6_enable_peripheral_retention(bool enable);
void pm_c6_set_cpu_frequency(uint32_t freq_mhz);

// Research-Enhanced Power Management Functions
void pm_c6_configure_power_domains(void);
void pm_c6_configure_gpio_power_management(void);
void pm_c6_enable_ultra_low_power_mode(void);
void pm_c6_configure_production_optimizations(void);
void pm_c6_enable_wifi_twt(bool enable);
void pm_c6_configure_ledc_power_management(void);
void pm_c6_configure_adc_power_management(void);

// Advanced monitoring functions
uint32_t pm_c6_get_power_consumption_estimate(void);
uint32_t pm_c6_get_advanced_power_estimate(pm_c6_mode_t mode, bool wifi_active, bool ble_active);
void pm_c6_print_power_stats(void);
pm_c6_wake_source_t pm_c6_get_last_wake_source(void);

// GPIO hold functions for ESP32-C6
void pm_c6_gpio_hold_enable(uint8_t gpio_num);
void pm_c6_gpio_hold_disable(uint8_t gpio_num);
void pm_c6_gpio_hold_all(void);
void pm_c6_gpio_unhold_all(void);

#else
// Stub functions for non-C6 targets
static inline void pm_c6_init(void) {}
static inline bool pm_c6_configure(const void *config) { return false; }
static inline void pm_c6_set_mode(int mode) {}
static inline int pm_c6_get_mode(void) { return 0; }
static inline void pm_c6_enter_light_sleep(uint32_t duration_ms) {}
static inline void pm_c6_enter_deep_sleep(uint32_t duration_ms) {}
static inline void pm_c6_configure_wake_source(int source, uint32_t param) {}
static inline void pm_c6_enable_wifi_power_save(bool enable) {}
static inline void pm_c6_enable_ble_power_save(bool enable) {}
static inline void pm_c6_enable_peripheral_retention(bool enable) {}
static inline void pm_c6_set_cpu_frequency(uint32_t freq_mhz) {}
static inline uint32_t pm_c6_get_power_consumption_estimate(void) { return 0; }
static inline void pm_c6_print_power_stats(void) {}
static inline int pm_c6_get_last_wake_source(void) { return 0; }
static inline void pm_c6_gpio_hold_enable(uint8_t gpio_num) {}
static inline void pm_c6_gpio_hold_disable(uint8_t gpio_num) {}
static inline void pm_c6_gpio_hold_all(void) {}
static inline void pm_c6_gpio_unhold_all(void) {}
#endif

#endif /* POWER_MANAGEMENT_C6_H_ */