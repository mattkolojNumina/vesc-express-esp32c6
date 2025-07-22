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

#include "test_c6_integration.h"

#ifdef CONFIG_IDF_TARGET_ESP32C6

#include "esp_log.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "comm_ble.h"
#include "comm_wifi.h"
#include "vesc_c6_integration.h"
#include "ble_c6_enhancements.h"
#include "wifi_c6_enhancements.h"
#include "power_management_c6.h"

static const char *TAG = "TEST_C6_INTEGRATION";

void test_c6_integration_basic(void) {
    ESP_LOGI(TAG, "=== ESP32-C6 Integration Basic Test ===");
    
    // Test 1: Verify integration layer is ready
    bool integration_ready = vesc_c6_is_integration_ready();
    ESP_LOGI(TAG, "Test 1 - Integration ready: %s", integration_ready ? "PASS" : "FAIL");
    
    // Test 2: Check VESC BLE compatibility
    bool ble_compatible = true;
    if (comm_ble_is_connected()) {
        int mtu = comm_ble_mtu_now();
        ble_compatible = (mtu >= 20);
        ESP_LOGI(TAG, "Test 2 - VESC BLE compatibility (MTU=%d): %s", mtu, ble_compatible ? "PASS" : "FAIL");
    } else {
        ESP_LOGI(TAG, "Test 2 - VESC BLE not active: SKIPPED");
    }
    
    // Test 3: Verify power management doesn't interfere with motor control
    pm_c6_mode_t power_mode = pm_c6_get_mode();
    bool power_ok = (power_mode == PM_C6_MODE_ACTIVE || power_mode == PM_C6_MODE_MODEM_SLEEP);
    ESP_LOGI(TAG, "Test 3 - Power mode compatible (mode=%d): %s", power_mode, power_ok ? "PASS" : "FAIL");
    
    // Test 4: Check ESP32-C6 feature availability
    bool features_ok = true;
    features_ok &= ble_c6_is_feature_supported("ext_adv");
    features_ok &= ble_c6_is_feature_supported("2m_phy");
    features_ok &= ble_c6_is_feature_supported("coded_phy");
    ESP_LOGI(TAG, "Test 4 - C6 features available: %s", features_ok ? "PASS" : "FAIL");
    
    // Test 5: Verify integration doesn't break VESC protocols
    bool protocols_ok = vesc_c6_check_compatibility();
    ESP_LOGI(TAG, "Test 5 - VESC protocol compatibility: %s", protocols_ok ? "PASS" : "FAIL");
    
    // Overall result
    bool all_tests_pass = integration_ready && ble_compatible && power_ok && features_ok && protocols_ok;
    ESP_LOGI(TAG, "=== Basic Integration Test: %s ===", all_tests_pass ? "PASS" : "FAIL");
}

void test_c6_integration_stress(void) {
    ESP_LOGI(TAG, "=== ESP32-C6 Integration Stress Test ===");
    
    // Stress Test 1: Multiple rapid configuration changes
    ESP_LOGI(TAG, "Stress Test 1: Rapid configuration changes");
    for (int i = 0; i < 10; i++) {
        vesc_c6_integration_config_t config = VESC_C6_INTEGRATION_CONFIG_DEFAULT();
        config.performance_mode = i % 3;  // Cycle through performance modes
        bool config_ok = vesc_c6_configure_integration(&config);
        if (!config_ok) {
            ESP_LOGW(TAG, "Configuration change %d failed", i);
        }
        vTaskDelay(50 / portTICK_PERIOD_MS);  // 50ms delay
    }
    ESP_LOGI(TAG, "Stress Test 1: COMPLETED");
    
    // Stress Test 2: Power mode cycling under load
    ESP_LOGI(TAG, "Stress Test 2: Power mode cycling");
    pm_c6_mode_t test_modes[] = {
        PM_C6_MODE_ACTIVE,
        PM_C6_MODE_MODEM_SLEEP,
        PM_C6_MODE_LIGHT_SLEEP,
        PM_C6_MODE_ACTIVE  // Return to active
    };
    
    for (int i = 0; i < 4; i++) {
        pm_c6_set_mode(test_modes[i]);
        vTaskDelay(100 / portTICK_PERIOD_MS);  // 100ms delay
        
        // Verify VESC compatibility after mode change
        bool compatible = vesc_c6_check_compatibility();
        if (!compatible) {
            ESP_LOGW(TAG, "Compatibility issue after power mode %d", test_modes[i]);
        }
    }
    ESP_LOGI(TAG, "Stress Test 2: COMPLETED");
    
    // Stress Test 3: Emergency safe mode and recovery
    ESP_LOGI(TAG, "Stress Test 3: Emergency safe mode");
    vesc_c6_emergency_safe_mode();
    vTaskDelay(200 / portTICK_PERIOD_MS);
    
    // Verify system is still functional
    bool recovery_ok = vesc_c6_check_compatibility();
    ESP_LOGI(TAG, "Stress Test 3: %s", recovery_ok ? "PASS" : "FAIL");
    
    // Restore normal operation
    vesc_c6_integration_config_t normal_config = VESC_C6_INTEGRATION_CONFIG_DEFAULT();
    vesc_c6_configure_integration(&normal_config);
    
    ESP_LOGI(TAG, "=== Stress Test: COMPLETED ===");
}

void test_c6_integration_performance(void) {
    ESP_LOGI(TAG, "=== ESP32-C6 Integration Performance Test ===");
    
    // Performance Test 1: BLE throughput with enhancements
    if (comm_ble_is_connected()) {
        int mtu_before = comm_ble_mtu_now();
        
        // Enable high-performance BLE mode
        ble_c6_enable_high_performance_mode();
        vTaskDelay(100 / portTICK_PERIOD_MS);
        
        int mtu_after = comm_ble_mtu_now();
        ESP_LOGI(TAG, "BLE Performance - MTU before: %d, after: %d", mtu_before, mtu_after);
        
        // Test packet timing (simulate VESC communication)
        uint32_t start_time = esp_timer_get_time();
        for (int i = 0; i < 100; i++) {
            // Simulate small VESC command packet
            uint8_t test_packet[20] = {0};
            comm_ble_send_packet(test_packet, sizeof(test_packet));
            vTaskDelay(1);  // Small delay between packets
        }
        uint32_t end_time = esp_timer_get_time();
        
        uint32_t duration_us = end_time - start_time;
        ESP_LOGI(TAG, "BLE Performance - 100 packets in %lu us (%.2f packets/ms)", 
                 duration_us, 100000.0 / duration_us);
    } else {
        ESP_LOGI(TAG, "BLE Performance test skipped - not connected");
    }
    
    // Performance Test 2: Power consumption estimation
    uint32_t power_estimate = pm_c6_get_power_consumption_estimate();
    ESP_LOGI(TAG, "Power Performance - Estimated consumption: %lu mA", power_estimate);
    
    // Performance Test 3: Memory usage check
    size_t free_heap = esp_get_free_heap_size();
    size_t min_free_heap = esp_get_minimum_free_heap_size();
    ESP_LOGI(TAG, "Memory Performance - Free: %u bytes, Min free: %u bytes", 
             free_heap, min_free_heap);
    
    ESP_LOGI(TAG, "=== Performance Test: COMPLETED ===");
}

void test_c6_integration_comprehensive(void) {
    ESP_LOGI(TAG, "Starting comprehensive ESP32-C6 integration test suite");
    
    // Run all test categories
    test_c6_integration_basic();
    vTaskDelay(500 / portTICK_PERIOD_MS);
    
    test_c6_integration_stress();
    vTaskDelay(500 / portTICK_PERIOD_MS);
    
    test_c6_integration_performance();
    vTaskDelay(500 / portTICK_PERIOD_MS);
    
    // Final status report
    ESP_LOGI(TAG, "=== COMPREHENSIVE TEST SUMMARY ===");
    vesc_c6_print_status();
    
    ESP_LOGI(TAG, "ESP32-C6 integration test suite completed");
}

#else
// Stub implementations for non-C6 targets
void test_c6_integration_basic(void) {}
void test_c6_integration_stress(void) {}
void test_c6_integration_performance(void) {}
void test_c6_integration_comprehensive(void) {}
#endif /* CONFIG_IDF_TARGET_ESP32C6 */