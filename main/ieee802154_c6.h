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

#ifndef IEEE802154_C6_H_
#define IEEE802154_C6_H_

#include <stdbool.h>
#include <stdint.h>
#include <stddef.h>

#ifdef CONFIG_IDF_TARGET_ESP32C6

// IEEE 802.15.4 configuration for Thread/Zigbee support
typedef struct {
    bool enable_802154;             // Enable IEEE 802.15.4 radio
    uint8_t channel;                // 802.15.4 channel (11-26)
    uint16_t pan_id;                // PAN ID
    uint16_t short_addr;            // Short address
    uint64_t extended_addr;         // Extended (IEEE) address
    int8_t tx_power;                // TX power (-24 to +6 dBm)
    bool auto_ack;                  // Enable automatic acknowledgment
    bool frame_filtering;           // Enable frame filtering
    bool promiscuous;               // Promiscuous mode
    bool coordinator;               // Act as coordinator
} ieee802154_config_t;

// Default 802.15.4 configuration
#define IEEE802154_CONFIG_DEFAULT() { \
    .enable_802154 = false, \
    .channel = 15, \
    .pan_id = 0xABCD, \
    .short_addr = 0x1234, \
    .extended_addr = 0x0123456789ABCDEF, \
    .tx_power = 0, \
    .auto_ack = true, \
    .frame_filtering = true, \
    .promiscuous = false, \
    .coordinator = false, \
}

// Thread network configuration
typedef struct {
    bool enable_thread;             // Enable Thread protocol
    char network_name[16];          // Thread network name
    uint8_t network_key[16];        // Thread network key
    uint16_t network_channel;       // Thread network channel
    uint16_t pan_id;                // Thread PAN ID
    bool commissioner_mode;         // Enable commissioner mode
} thread_config_t;

#define THREAD_CONFIG_DEFAULT() { \
    .enable_thread = false, \
    .network_name = "VESC-Thread", \
    .network_key = {0x00, 0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x77, \
                    0x88, 0x99, 0xAA, 0xBB, 0xCC, 0xDD, 0xEE, 0xFF}, \
    .network_channel = 15, \
    .pan_id = 0xFACE, \
    .commissioner_mode = false, \
}

// Zigbee configuration
typedef struct {
    bool enable_zigbee;             // Enable Zigbee protocol
    uint16_t device_id;             // Zigbee device ID
    uint8_t endpoint;               // Zigbee endpoint
    uint16_t cluster_id;            // Zigbee cluster ID
    bool coordinator_mode;          // Act as Zigbee coordinator
    uint8_t security_level;         // Security level (0-7)
} zigbee_config_t;

#define ZIGBEE_CONFIG_DEFAULT() { \
    .enable_zigbee = false, \
    .device_id = 0x0001, \
    .endpoint = 1, \
    .cluster_id = 0x0006, \
    .coordinator_mode = false, \
    .security_level = 5, \
}

// Function declarations
void ieee802154_init(void);
bool ieee802154_configure(const ieee802154_config_t *config);
bool ieee802154_start(void);
void ieee802154_stop(void);
bool ieee802154_send_frame(const uint8_t *data, size_t len, uint16_t dst_addr);
void ieee802154_set_receive_callback(void (*callback)(const uint8_t *data, size_t len));

// Thread protocol functions
bool thread_init(const thread_config_t *config);
bool thread_start_network(void);
void thread_stop_network(void);
bool thread_is_connected(void);
void thread_get_network_info(void);

// Zigbee protocol functions
bool zigbee_init(const zigbee_config_t *config);
bool zigbee_start_network(void);
void zigbee_stop_network(void);
bool zigbee_send_command(uint16_t dst_addr, uint8_t cmd, const uint8_t *data, size_t len);

// Utility functions
void ieee802154_print_capabilities(void);
bool ieee802154_coexist_with_wifi_ble(bool enable);
void ieee802154_set_channel(uint8_t channel);
uint8_t ieee802154_get_channel(void);

#else
// Stub functions for non-C6 targets
static inline void ieee802154_init(void) {}
static inline bool ieee802154_configure(const void *config) { return false; }
static inline bool ieee802154_start(void) { return false; }
static inline void ieee802154_stop(void) {}
static inline bool ieee802154_send_frame(const uint8_t *data, size_t len, uint16_t dst_addr) { return false; }
static inline void ieee802154_set_receive_callback(void (*callback)(const uint8_t *data, size_t len)) {}
static inline bool thread_init(const void *config) { return false; }
static inline bool thread_start_network(void) { return false; }
static inline void thread_stop_network(void) {}
static inline bool thread_is_connected(void) { return false; }
static inline void thread_get_network_info(void) {}
static inline bool zigbee_init(const void *config) { return false; }
static inline bool zigbee_start_network(void) { return false; }
static inline void zigbee_stop_network(void) {}
static inline bool zigbee_send_command(uint16_t dst_addr, uint8_t cmd, const uint8_t *data, size_t len) { return false; }
static inline void ieee802154_print_capabilities(void) {}
static inline bool ieee802154_coexist_with_wifi_ble(bool enable) { return false; }
static inline void ieee802154_set_channel(uint8_t channel) {}
static inline uint8_t ieee802154_get_channel(void) { return 0; }
#endif

#endif /* IEEE802154_C6_H_ */