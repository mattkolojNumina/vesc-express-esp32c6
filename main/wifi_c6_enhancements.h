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

#ifndef WIFI_C6_ENHANCEMENTS_H_
#define WIFI_C6_ENHANCEMENTS_H_

#include <stdbool.h>
#include <stdint.h>
#include "sdkconfig.h"

#ifdef CONFIG_IDF_TARGET_ESP32C6

// WiFi 6 specific features (Enhanced for ESP32-C6 capabilities)
typedef struct {
    bool twt_enable;                // Enable Target Wake Time
    uint32_t twt_wake_interval_us;  // Wake interval in microseconds
    uint32_t twt_wake_duration_us;  // Wake duration in microseconds
    bool ofdma_enable;              // Enable OFDMA (automatic)
    bool mu_mimo_enable;            // Enable MU-MIMO (automatic)
    uint8_t he_mcs_max;             // Maximum HE MCS (0-11, 255 = auto)
    bool advanced_security;         // Enable WPA3/PMF advanced features
    bool high_performance_mode;     // Enable high-performance configuration
    uint8_t static_rx_buffers;      // Static RX buffer count (C6 can handle more)
    uint8_t dynamic_rx_buffers;     // Dynamic RX buffer count
    uint8_t dynamic_tx_buffers;     // Dynamic TX buffer count
    uint8_t rx_ba_window;           // RX block ack window size
    bool amsdu_tx_enable;           // Enable A-MSDU TX (WiFi 6 feature)
    uint8_t max_tx_power;           // Maximum TX power (C6 can handle higher)
} wifi_c6_config_t;

// Default WiFi 6 configuration (Enhanced for ESP32-C6 superior hardware)
#define WIFI_C6_CONFIG_DEFAULT() { \
    .twt_enable = true,             /* C6 has better TWT support */ \
    .twt_wake_interval_us = 32768,  /* Faster intervals due to C6 power */ \
    .twt_wake_duration_us = 32768,  /* Optimized for C6 capabilities */ \
    .ofdma_enable = true, \
    .mu_mimo_enable = true, \
    .he_mcs_max = 255, \
    .advanced_security = true,      /* Enable WPA3/PMF features */ \
    .high_performance_mode = true,  /* Leverage C6's processing power */ \
    .static_rx_buffers = 16,        /* More buffers (C6 has more RAM) */ \
    .dynamic_rx_buffers = 32,       /* Enhanced RX capability */ \
    .dynamic_tx_buffers = 32,       /* Enhanced TX capability */ \
    .rx_ba_window = 16,             /* Larger window (WiFi 6 + more memory) */ \
    .amsdu_tx_enable = true,        /* A-MSDU aggregation (C6 can handle) */ \
    .max_tx_power = 84,             /* Higher power (21 dBm, C6 capability) */ \
}

// Function declarations
void wifi_c6_init_enhancements(void);
bool wifi_c6_configure_twt(const wifi_c6_config_t *config);
void wifi_c6_enable_power_save_features(void);
bool wifi_c6_is_wifi6_connected(void);
void wifi_c6_print_connection_info(void);

// Motor control specific functions
void wifi_c6_configure_motor_control_features(void);      // Motor control optimization

// Advanced ESP32-C6 WiFi functions (leveraging superior hardware)
void wifi_c6_configure_advanced_security(void);           // Enhanced security features
void wifi_c6_enable_advanced_power_management(void);      // Advanced power management
void wifi_c6_configure_advanced_aggregation(void);        // Enhanced aggregation
void wifi_c6_configure_qos_features(void);               // QoS optimization
void wifi_c6_configure_security_features(void);          // Legacy compatibility

#else
// Stub functions for non-C6 targets
static inline void wifi_c6_init_enhancements(void) {}
static inline bool wifi_c6_configure_twt(const void *config) { return false; }
static inline void wifi_c6_enable_power_save_features(void) {}
static inline bool wifi_c6_is_wifi6_connected(void) { return false; }
static inline void wifi_c6_print_connection_info(void) {}
static inline void wifi_c6_configure_advanced_security(void) {}
static inline void wifi_c6_enable_advanced_power_management(void) {}
static inline void wifi_c6_configure_advanced_aggregation(void) {}
static inline void wifi_c6_configure_qos_features(void) {}
static inline void wifi_c6_configure_security_features(void) {}
#endif

#endif /* WIFI_C6_ENHANCEMENTS_H_ */