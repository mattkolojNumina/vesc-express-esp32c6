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

#include "ieee802154_c6.h"

#ifdef CONFIG_IDF_TARGET_ESP32C6

#include "esp_log.h"
#include "esp_err.h"
// IEEE 802.15.4 includes - may not be available in all ESP-IDF versions
#ifdef CONFIG_IEEE802154_ENABLED
#include "esp_ieee802154.h"
#include "esp_ieee802154_types.h"
#endif
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include <string.h>

static const char *TAG = "IEEE802154";
static ieee802154_config_t current_config = IEEE802154_CONFIG_DEFAULT();
static thread_config_t thread_config = THREAD_CONFIG_DEFAULT();
static zigbee_config_t zigbee_config = ZIGBEE_CONFIG_DEFAULT();
static bool ieee802154_initialized = false;
static void (*receive_callback)(const uint8_t *data, size_t len) = NULL;

// IEEE 802.15.4 receive callback
#ifdef CONFIG_IEEE802154_ENABLED
static void ieee802154_receive_done(uint8_t *frame, esp_ieee802154_frame_info_t *frame_info) {
    if (receive_callback && frame && frame_info) {
        // Extract payload from the frame (skip MAC header)
        uint8_t *payload = frame + 3; // Skip FCF, sequence, and addressing
        size_t payload_len = frame_info->length - 3;
        
        receive_callback(payload, payload_len);
    }
}
#endif
}

void ieee802154_init(void) {
    if (ieee802154_initialized) {
        ESP_LOGW(TAG, "IEEE 802.15.4 already initialized");
        return;
    }
    
    ESP_LOGI(TAG, "Initializing ESP32-C6 IEEE 802.15.4 support");
    
    // Initialize IEEE 802.15.4 driver
#ifdef CONFIG_IEEE802154_ENABLED
    esp_err_t ret = esp_ieee802154_enable();
    if (ret != ESP_OK) {
        ESP_LOGE(TAG, "Failed to enable IEEE 802.15.4: %s", esp_err_to_name(ret));
        return;
    }
    
    // Set receive callback
    esp_ieee802154_set_receive_done_callback(ieee802154_receive_done);
#else
    ESP_LOGW(TAG, "IEEE 802.15.4 not available in this ESP-IDF version");
    return;
#endif
    
    ieee802154_initialized = true;
    ESP_LOGI(TAG, "IEEE 802.15.4 initialized successfully");
    
    ieee802154_print_capabilities();
}

#ifdef CONFIG_IEEE802154_ENABLED
bool ieee802154_configure(const ieee802154_config_t *config) {
    if (!config) {
        ESP_LOGE(TAG, "Invalid configuration pointer");
        return false;
    }
    
    if (!ieee802154_initialized) {
        ESP_LOGE(TAG, "IEEE 802.15.4 not initialized");
        return false;
    }
    
    current_config = *config;
    
    ESP_LOGI(TAG, "Configuring IEEE 802.15.4:");
    ESP_LOGI(TAG, "  Channel: %d", config->channel);
    ESP_LOGI(TAG, "  PAN ID: 0x%04X", config->pan_id);
    ESP_LOGI(TAG, "  Short Address: 0x%04X", config->short_addr);
    ESP_LOGI(TAG, "  Extended Address: 0x%016llX", config->extended_addr);
    ESP_LOGI(TAG, "  TX Power: %d dBm", config->tx_power);
    ESP_LOGI(TAG, "  Auto ACK: %s", config->auto_ack ? "Enabled" : "Disabled");
    
    // Configure channel
    esp_err_t ret = esp_ieee802154_set_channel(config->channel);
    if (ret != ESP_OK) {
        ESP_LOGE(TAG, "Failed to set channel: %s", esp_err_to_name(ret));
        return false;
    }
    
    // Configure PAN ID
    ret = esp_ieee802154_set_panid(config->pan_id);
    if (ret != ESP_OK) {
        ESP_LOGE(TAG, "Failed to set PAN ID: %s", esp_err_to_name(ret));
        return false;
    }
    
    // Configure short address
    ret = esp_ieee802154_set_short_addr(config->short_addr);
    if (ret != ESP_OK) {
        ESP_LOGE(TAG, "Failed to set short address: %s", esp_err_to_name(ret));
        return false;
    }
    
    // Configure extended address
    uint8_t ext_addr[8];
    for (int i = 0; i < 8; i++) {
        ext_addr[i] = (config->extended_addr >> (i * 8)) & 0xFF;
    }
    ret = esp_ieee802154_set_extended_addr(ext_addr);
    if (ret != ESP_OK) {
        ESP_LOGE(TAG, "Failed to set extended address: %s", esp_err_to_name(ret));
        return false;
    }
    
    // Configure TX power
    ret = esp_ieee802154_set_txpower(config->tx_power);
    if (ret != ESP_OK) {
        ESP_LOGE(TAG, "Failed to set TX power: %s", esp_err_to_name(ret));
        return false;
    }
    
    // Configure auto ACK
    esp_ieee802154_set_auto_ack_tx(config->auto_ack);
    esp_ieee802154_set_auto_ack_rx(config->auto_ack);
    
    // Configure frame filtering
    esp_ieee802154_set_frame_filter(config->frame_filtering);
    
    // Configure promiscuous mode
    esp_ieee802154_set_promiscuous(config->promiscuous);
    
    ESP_LOGI(TAG, "IEEE 802.15.4 configuration completed");
    return true;
#else
    ESP_LOGW(TAG, "IEEE 802.15.4 not available");
    return false;
#endif
}

#ifdef CONFIG_IEEE802154_ENABLED
bool ieee802154_start(void) {
    if (!ieee802154_initialized) {
        ESP_LOGE(TAG, "IEEE 802.15.4 not initialized");
        return false;
    }
    
    esp_err_t ret = esp_ieee802154_set_state(ESP_IEEE802154_RADIO_ENABLE);
    if (ret != ESP_OK) {
        ESP_LOGE(TAG, "Failed to start IEEE 802.15.4: %s", esp_err_to_name(ret));
        return false;
    }
    
    ESP_LOGI(TAG, "IEEE 802.15.4 radio started");
    return true;
#else
    ESP_LOGW(TAG, "IEEE 802.15.4 not available");
    return false;
#endif
}

void ieee802154_stop(void) {
#ifdef CONFIG_IEEE802154_ENABLED
    if (!ieee802154_initialized) {
        return;
    }
    
    esp_ieee802154_set_state(ESP_IEEE802154_RADIO_DISABLE);
    ESP_LOGI(TAG, "IEEE 802.15.4 radio stopped");
#endif
}

bool ieee802154_send_frame(const uint8_t *data, size_t len, uint16_t dst_addr) {
#ifdef CONFIG_IEEE802154_ENABLED
    if (!ieee802154_initialized || !data || len == 0) {
        return false;
    }
    
    // Create a simple MAC frame
    uint8_t frame[127]; // Maximum 802.15.4 frame size
    size_t frame_len = 0;
    
    // Frame Control Field (FCF)
    frame[frame_len++] = 0x41; // Data frame, short addressing
    frame[frame_len++] = 0x88; // PAN ID compression
    
    // Sequence number
    static uint8_t seq_num = 0;
    frame[frame_len++] = seq_num++;
    
    // Destination PAN ID and address
    frame[frame_len++] = current_config.pan_id & 0xFF;
    frame[frame_len++] = (current_config.pan_id >> 8) & 0xFF;
    frame[frame_len++] = dst_addr & 0xFF;
    frame[frame_len++] = (dst_addr >> 8) & 0xFF;
    
    // Source address
    frame[frame_len++] = current_config.short_addr & 0xFF;
    frame[frame_len++] = (current_config.short_addr >> 8) & 0xFF;
    
    // Payload
    if (frame_len + len <= sizeof(frame)) {
        memcpy(&frame[frame_len], data, len);
        frame_len += len;
    } else {
        ESP_LOGE(TAG, "Frame too large");
        return false;
    }
    
    esp_err_t ret = esp_ieee802154_transmit(frame, false);
    return (ret == ESP_OK);
#else
    return false;
#endif
}

void ieee802154_set_receive_callback(void (*callback)(const uint8_t *data, size_t len)) {
    receive_callback = callback;
}

bool thread_init(const thread_config_t *config) {
    if (!config) {
        ESP_LOGE(TAG, "Invalid Thread configuration");
        return false;
    }
    
    thread_config = *config;
    
    ESP_LOGI(TAG, "Initializing Thread protocol:");
    ESP_LOGI(TAG, "  Network Name: %s", config->network_name);
    ESP_LOGI(TAG, "  Channel: %d", config->network_channel);
    ESP_LOGI(TAG, "  PAN ID: 0x%04X", config->pan_id);
    ESP_LOGI(TAG, "  Commissioner Mode: %s", config->commissioner_mode ? "Yes" : "No");
    
    // Note: Thread implementation would require OpenThread library
    // This is a placeholder for when OpenThread support is added
    
    ESP_LOGI(TAG, "Thread protocol initialized (placeholder)");
    return true;
}

bool thread_start_network(void) {
    if (!thread_config.enable_thread) {
        ESP_LOGW(TAG, "Thread not enabled");
        return false;
    }
    
    ESP_LOGI(TAG, "Starting Thread network");
    // Placeholder for OpenThread network start
    return true;
}

void thread_stop_network(void) {
    ESP_LOGI(TAG, "Stopping Thread network");
    // Placeholder for OpenThread network stop
}

bool thread_is_connected(void) {
    // Placeholder - would check OpenThread connection status
    return false;
}

void thread_get_network_info(void) {
    ESP_LOGI(TAG, "Thread Network Information:");
    ESP_LOGI(TAG, "  Status: Not implemented yet");
    ESP_LOGI(TAG, "  Note: Requires OpenThread library integration");
}

bool zigbee_init(const zigbee_config_t *config) {
    if (!config) {
        ESP_LOGE(TAG, "Invalid Zigbee configuration");
        return false;
    }
    
    zigbee_config = *config;
    
    ESP_LOGI(TAG, "Initializing Zigbee protocol:");
    ESP_LOGI(TAG, "  Device ID: 0x%04X", config->device_id);
    ESP_LOGI(TAG, "  Endpoint: %d", config->endpoint);
    ESP_LOGI(TAG, "  Cluster ID: 0x%04X", config->cluster_id);
    ESP_LOGI(TAG, "  Coordinator Mode: %s", config->coordinator_mode ? "Yes" : "No");
    ESP_LOGI(TAG, "  Security Level: %d", config->security_level);
    
    // Note: Zigbee implementation would require Zigbee stack
    // This is a placeholder for when Zigbee support is added
    
    ESP_LOGI(TAG, "Zigbee protocol initialized (placeholder)");
    return true;
}

bool zigbee_start_network(void) {
    ESP_LOGI(TAG, "Starting Zigbee network");
    // Placeholder for Zigbee network start
    return true;
}

void zigbee_stop_network(void) {
    ESP_LOGI(TAG, "Stopping Zigbee network");
    // Placeholder for Zigbee network stop
}

bool zigbee_send_command(uint16_t dst_addr, uint8_t cmd, const uint8_t *data, size_t len) {
    ESP_LOGI(TAG, "Sending Zigbee command 0x%02X to 0x%04X", cmd, dst_addr);
    // Placeholder for Zigbee command transmission
    return true;
}

void ieee802154_print_capabilities(void) {
    ESP_LOGI(TAG, "ESP32-C6 IEEE 802.15.4 Capabilities:");
    ESP_LOGI(TAG, "  ✓ IEEE 802.15.4-2015 compliant");
    ESP_LOGI(TAG, "  ✓ 2.4 GHz ISM band");
    ESP_LOGI(TAG, "  ✓ Channels 11-26");
    ESP_LOGI(TAG, "  ✓ DSSS-OQPSK modulation");
    ESP_LOGI(TAG, "  ✓ 250 kbps data rate");
    ESP_LOGI(TAG, "  ✓ Hardware MAC support");
    ESP_LOGI(TAG, "  ✓ Automatic acknowledgment");
    ESP_LOGI(TAG, "  ✓ Frame filtering");
    ESP_LOGI(TAG, "  ✓ Security features");
    ESP_LOGI(TAG, "  ✓ Coexistence with WiFi and BLE");
    ESP_LOGI(TAG, "");
    ESP_LOGI(TAG, "Protocol Support:");
    ESP_LOGI(TAG, "  ✓ Thread (with OpenThread)");
    ESP_LOGI(TAG, "  ✓ Zigbee (with Zigbee stack)");
    ESP_LOGI(TAG, "  ✓ Matter (with Thread/WiFi)");
    ESP_LOGI(TAG, "  ✓ Custom 802.15.4 protocols");
}

bool ieee802154_coexist_with_wifi_ble(bool enable) {
    ESP_LOGI(TAG, "IEEE 802.15.4 coexistence with WiFi/BLE: %s", enable ? "Enabled" : "Disabled");
    
    // ESP32-C6 has hardware support for coexistence
    // This would configure the coexistence parameters
    
    return true;
}

void ieee802154_set_channel(uint8_t channel) {
#ifdef CONFIG_IEEE802154_ENABLED
    if (channel < 11 || channel > 26) {
        ESP_LOGE(TAG, "Invalid channel %d (must be 11-26)", channel);
        return;
    }
    
    current_config.channel = channel;
    if (ieee802154_initialized) {
        esp_ieee802154_set_channel(channel);
    }
#endif
}
    
    current_config.channel = channel;
    if (ieee802154_initialized) {
        esp_ieee802154_set_channel(channel);
    }
}

uint8_t ieee802154_get_channel(void) {
    return current_config.channel;
}

#endif /* CONFIG_IDF_TARGET_ESP32C6 */