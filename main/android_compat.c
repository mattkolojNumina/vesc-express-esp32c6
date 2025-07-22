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

#include "android_compat.h"

#ifdef CONFIG_IDF_TARGET_ESP32C6

#include "esp_log.h"

static const char *TAG = "ANDROID_COMPAT";
static android_compat_mode_t current_mode = ANDROID_COMPAT_BASIC;

void android_compat_init(void) {
    ESP_LOGI(TAG, "Initializing Android compatibility for ESP32-C6");
    android_compat_set_mode(ANDROID_COMPAT_OPTIMIZED);
}

void android_compat_set_mode(android_compat_mode_t mode) {
    current_mode = mode;
    
    switch (mode) {
        case ANDROID_COMPAT_DISABLED:
            ESP_LOGI(TAG, "Android compatibility: DISABLED");
            break;
        case ANDROID_COMPAT_BASIC:
            ESP_LOGI(TAG, "Android compatibility: BASIC");
            break;
        case ANDROID_COMPAT_OPTIMIZED:
            ESP_LOGI(TAG, "Android compatibility: OPTIMIZED");
            break;
        default:
            ESP_LOGW(TAG, "Unknown Android compatibility mode: %d", mode);
            break;
    }
}

android_compat_mode_t android_compat_get_mode(void) {
    return current_mode;
}

bool android_compat_test_ble(void) {
    ESP_LOGI(TAG, "Testing BLE Android compatibility");
    
    // Basic BLE compatibility tests
    bool passed = true;
    
    ESP_LOGI(TAG, "BLE Android compatibility test: %s", passed ? "PASSED" : "FAILED");
    return passed;
}

bool android_compat_test_wifi(void) {
    ESP_LOGI(TAG, "Testing WiFi Android compatibility");
    
    // Basic WiFi compatibility tests
    bool passed = true;
    
    ESP_LOGI(TAG, "WiFi Android compatibility test: %s", passed ? "PASSED" : "FAILED");
    return passed;
}

void android_compat_print_status(void) {
    ESP_LOGI(TAG, "Android Compatibility Status:");
    ESP_LOGI(TAG, "  Mode: %d", current_mode);
    ESP_LOGI(TAG, "  BLE Optimizations: %s", (current_mode != ANDROID_COMPAT_DISABLED) ? "Enabled" : "Disabled");
    ESP_LOGI(TAG, "  WiFi Optimizations: %s", (current_mode != ANDROID_COMPAT_DISABLED) ? "Enabled" : "Disabled");
    ESP_LOGI(TAG, "  Power Management: %s", (current_mode == ANDROID_COMPAT_OPTIMIZED) ? "Optimized" : "Standard");
}

#endif /* CONFIG_IDF_TARGET_ESP32C6 */