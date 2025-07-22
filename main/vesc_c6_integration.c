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

#include "vesc_c6_integration.h"

#ifdef CONFIG_IDF_TARGET_ESP32C6

#include "esp_log.h"
#include "comm_ble.h"
#include "comm_wifi.h"
#include "ble_c6_enhancements.h"
#include "wifi_c6_enhancements.h"
#include "power_management_c6.h"

static const char *TAG = "VESC_C6_INTEGRATION";
static bool integration_initialized = false;
static vesc_c6_integration_config_t current_config = VESC_C6_INTEGRATION_CONFIG_DEFAULT();

void vesc_c6_integration_init(void) {
    if (integration_initialized) {
        ESP_LOGW(TAG, "Integration already initialized");
        return;
    }
    
    ESP_LOGI(TAG, "Initializing VESC ESP32-C6 integration layer");
    
    // Configure enhanced BLE to work alongside VESC core BLE
    vesc_c6_configure_enhanced_ble();
    
    // Configure enhanced WiFi without interfering with VESC WiFi
    vesc_c6_configure_enhanced_wifi();
    
    // Configure power management to optimize VESC operations
    vesc_c6_configure_power_optimization();
    
    integration_initialized = true;
    ESP_LOGI(TAG, "VESC ESP32-C6 integration layer initialized successfully");
}

bool vesc_c6_configure_integration(const vesc_c6_integration_config_t *config) {
    if (!config) {
        ESP_LOGE(TAG, "Invalid integration configuration");
        return false;
    }
    
    current_config = *config;
    
    ESP_LOGI(TAG, "Configuring VESC ESP32-C6 integration:");
    ESP_LOGI(TAG, "  Enhanced BLE: %s", config->enhanced_ble_enable ? "Enabled" : "Disabled");
    ESP_LOGI(TAG, "  Enhanced WiFi: %s", config->enhanced_wifi_enable ? "Enabled" : "Disabled");
    ESP_LOGI(TAG, "  Power Optimization: %s", config->power_optimization_enable ? "Enabled" : "Disabled");
    ESP_LOGI(TAG, "  Android Compatibility: %s", config->android_compatibility ? "Enabled" : "Disabled");
    
    if (config->enhanced_ble_enable) {
        vesc_c6_configure_enhanced_ble();
    }
    
    if (config->enhanced_wifi_enable) {
        vesc_c6_configure_enhanced_wifi();
    }
    
    if (config->power_optimization_enable) {
        vesc_c6_configure_power_optimization();
    }
    
    if (config->android_compatibility) {
        vesc_c6_optimize_for_android();
    }
    
    return true;
}

void vesc_c6_configure_enhanced_ble(void) {
    ESP_LOGI(TAG, "Configuring enhanced BLE (preserving VESC core compatibility)");
    
    // Check if VESC BLE is active
    if (comm_ble_is_connected()) {
        ESP_LOGI(TAG, "VESC BLE is active - configuring enhancements in compatible mode");
        
        // Configure Android compatibility optimizations
        ble_c6_optimize_for_android();
        
        // Enable advanced features that don't interfere with VESC protocol
        if (current_config.enhanced_ble_enable) {
            // Enable advanced PHY modes for better performance
            ble_c6_enable_high_speed_phy();
            
            // Configure advanced security features
            ble_c6_configure_advanced_security_features();
            
            ESP_LOGI(TAG, "Enhanced BLE features configured (VESC compatible)");
        }
    } else {
        ESP_LOGI(TAG, "VESC BLE not active - full enhancement suite available");
        
        if (current_config.enhanced_ble_enable) {
            // Enable all advanced features when VESC BLE is not in use
            ble_c6_enable_advanced_features();
        }
    }
}

void vesc_c6_configure_enhanced_wifi(void) {
    ESP_LOGI(TAG, "Configuring enhanced WiFi (preserving VESC core compatibility)");
    
    if (current_config.enhanced_wifi_enable) {
        // Configure WiFi 6 enhancements that work alongside VESC WiFi
        wifi_c6_configure_advanced_security();
        wifi_c6_configure_advanced_aggregation();
        wifi_c6_configure_qos_features();
        
        // Enable power management features
        wifi_c6_enable_advanced_power_management();
        
        ESP_LOGI(TAG, "Enhanced WiFi features configured (VESC compatible)");
        ESP_LOGI(TAG, "WiFi 6 features will activate when connected to compatible AP");
    }
}

void vesc_c6_configure_power_optimization(void) {
    ESP_LOGI(TAG, "Configuring power optimization for VESC operations");
    
    if (current_config.power_optimization_enable) {
        // Configure power management that optimizes VESC performance
        pm_c6_config_t power_config = PM_C6_CONFIG_DEFAULT();
        
        // Optimize for VESC motor control operations
        power_config.cpu_freq_mhz = 160;  // Full performance for motor control
        power_config.auto_light_sleep = true;  // Sleep when motor is idle
        power_config.wifi_twt_enable = true;   // WiFi 6 power saving
        power_config.ble_power_save = true;    // BLE power optimization
        
        pm_c6_configure(&power_config);
        
        // Configure production optimizations
        pm_c6_configure_production_optimizations();
        
        ESP_LOGI(TAG, "Power optimization configured for VESC operations");
    }
}

void vesc_c6_optimize_for_android(void) {
    ESP_LOGI(TAG, "Optimizing ESP32-C6 for Android compatibility");
    
    // Optimize BLE for Android devices
    ble_c6_optimize_for_android();
    
    // Configure WiFi for Android compatibility
    wifi_c6_configure_advanced_security();  // Enable WPA3/PMF for Android
    
    ESP_LOGI(TAG, "Android compatibility optimizations applied");
}

bool vesc_c6_check_compatibility(void) {
    ESP_LOGI(TAG, "Checking VESC ESP32-C6 compatibility");
    
    bool compatible = true;
    
    // Check BLE compatibility
    if (comm_ble_is_connected()) {
        int mtu = comm_ble_mtu_now();
        ESP_LOGI(TAG, "VESC BLE active - MTU: %d bytes", mtu);
        
        if (mtu < 20) {
            ESP_LOGW(TAG, "BLE MTU below minimum - may affect performance");
            compatible = false;
        }
    }
    
    // Check power management compatibility
    pm_c6_mode_t power_mode = pm_c6_get_mode();
    ESP_LOGI(TAG, "Power management mode: %d", power_mode);
    
    // Print compatibility status
    ESP_LOGI(TAG, "VESC ESP32-C6 compatibility check: %s", compatible ? "PASSED" : "WARNINGS");
    
    return compatible;
}

void vesc_c6_print_status(void) {
    ESP_LOGI(TAG, "=== VESC ESP32-C6 Integration Status ===");
    ESP_LOGI(TAG, "Integration initialized: %s", integration_initialized ? "Yes" : "No");
    ESP_LOGI(TAG, "Enhanced BLE: %s", current_config.enhanced_ble_enable ? "Enabled" : "Disabled");
    ESP_LOGI(TAG, "Enhanced WiFi: %s", current_config.enhanced_wifi_enable ? "Enabled" : "Disabled");
    ESP_LOGI(TAG, "Power optimization: %s", current_config.power_optimization_enable ? "Enabled" : "Disabled");
    ESP_LOGI(TAG, "Android compatibility: %s", current_config.android_compatibility ? "Enabled" : "Disabled");
    
    // Print VESC core status
    ESP_LOGI(TAG, "VESC BLE connected: %s", comm_ble_is_connected() ? "Yes" : "No");
    if (comm_ble_is_connected()) {
        ESP_LOGI(TAG, "VESC BLE MTU: %d bytes", comm_ble_mtu_now());
    }
    
    // Print ESP32-C6 enhanced capabilities
    ble_c6_print_capabilities();
    wifi_c6_print_connection_info();
    pm_c6_print_power_stats();
    
    ESP_LOGI(TAG, "======================================");
}

bool vesc_c6_is_integration_ready(void) {
    return integration_initialized;
}

void vesc_c6_emergency_safe_mode(void) {
    ESP_LOGW(TAG, "Activating ESP32-C6 emergency safe mode");
    
    // Disable all enhancements to ensure VESC core functionality
    current_config.enhanced_ble_enable = false;
    current_config.enhanced_wifi_enable = false;
    current_config.power_optimization_enable = false;
    
    // Set conservative power mode
    pm_c6_set_mode(PM_C6_MODE_ACTIVE);
    
    ESP_LOGI(TAG, "Emergency safe mode activated - VESC core preserved");
}

#endif /* CONFIG_IDF_TARGET_ESP32C6 */