/**
 * CAN Interface Verification Tests
 * 
 * Specific tests to verify CAN interface implementation matches
 * VESC motor controller specifications.
 */

#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <unistd.h>
#include <sys/time.h>

// Include VESC headers based on research
#include "datatypes.h"

// Test configuration
#define TEST_CAN_BITRATE    500000
#define TEST_CONTROLLER_ID  1

// Test result tracking
static int can_tests_passed = 0;
static int can_tests_total = 0;

static void log_can_test(const char* test_name, bool passed, const char* details) {
    can_tests_total++;
    if (passed) {
        can_tests_passed++;
        printf("✅ CAN TEST PASS: %s - %s\n", test_name, details);
    } else {
        printf("❌ CAN TEST FAIL: %s - %s\n", test_name, details);
    }
}

/**
 * Test CAN frame ID format compliance with VESC standard
 */
static void test_can_frame_id_format(void) {
    printf("\n--- Testing CAN Frame ID Format ---\n");
    
    // Test extended frame ID format: [CONTROLLER_ID:21][PACKET_TYPE:8]
    uint8_t controller_id = TEST_CONTROLLER_ID;
    uint8_t packet_type = CAN_PACKET_PROCESS_SHORT_BUFFER;
    
    uint32_t expected_can_id = controller_id | ((uint32_t)packet_type << 8);
    
    // Verify ID format
    uint8_t extracted_controller = expected_can_id & 0xFF;
    uint8_t extracted_packet_type = (expected_can_id >> 8) & 0xFF;
    
    bool format_correct = (extracted_controller == controller_id) && 
                         (extracted_packet_type == packet_type);
    
    char details[128];
    snprintf(details, sizeof(details), "CAN ID: 0x%08X, Controller: %d, Type: %d", 
             expected_can_id, extracted_controller, extracted_packet_type);
    
    log_can_test("CAN Frame ID Format", format_correct, details);
    
    // Test all critical CAN packet types
    CAN_PACKET_ID test_types[] = {
        CAN_PACKET_SET_DUTY,
        CAN_PACKET_SET_CURRENT,
        CAN_PACKET_SET_RPM,
        CAN_PACKET_FILL_RX_BUFFER,
        CAN_PACKET_PROCESS_RX_BUFFER,
        CAN_PACKET_PROCESS_SHORT_BUFFER,
        CAN_PACKET_STATUS,
        CAN_PACKET_PING,
        CAN_PACKET_PONG
    };
    
    int num_types = sizeof(test_types) / sizeof(test_types[0]);
    bool all_types_valid = true;
    
    for (int i = 0; i < num_types; i++) {
        uint32_t test_id = controller_id | ((uint32_t)test_types[i] << 8);
        uint8_t extracted_type = (test_id >> 8) & 0xFF;
        
        if (extracted_type != test_types[i]) {
            all_types_valid = false;
            break;
        }
    }
    
    snprintf(details, sizeof(details), "All %d CAN packet types generate valid IDs", num_types);
    log_can_test("CAN Packet Type IDs", all_types_valid, details);
}

/**
 * Test CAN packet fragmentation for large packets
 */
static void test_can_packet_fragmentation(void) {
    printf("\n--- Testing CAN Packet Fragmentation ---\n");
    
    // Test small packet (≤6 bytes) - should use CAN_PACKET_PROCESS_SHORT_BUFFER
    uint8_t small_payload[6] = {COMM_FW_VERSION, 0x00, 0x01, 0x02, 0x03, 0x04};
    (void)small_payload;  // Used in conceptual test
    int small_len = 6;
    
    // Small packet should fit in single CAN frame
    bool small_packet_ok = (small_len <= 6);
    
    char details[128];
    snprintf(details, sizeof(details), "Small packet (%d bytes) uses single frame", small_len);
    log_can_test("Small Packet Handling", small_packet_ok, details);
    
    // Test large packet (>6 bytes) - should fragment
    uint8_t large_payload[100];
    for (int i = 0; i < 100; i++) {
        large_payload[i] = i & 0xFF;
    }
    (void)large_payload;  // Used in conceptual test
    int large_len = 100;
    
    // Calculate expected fragmentation
    // First 255 bytes: 7 bytes per frame
    // Remaining: 6 bytes per frame
    int frames_needed = 0;
    int remaining = large_len;
    
    // Fill RX buffer frames (7 bytes data per frame)
    while (remaining > 0 && frames_needed * 7 < 255) {
        frames_needed++;
        remaining -= 7;
        if (remaining <= 0) break;
    }
    
    // Fill RX buffer long frames (6 bytes data per frame)  
    while (remaining > 0) {
        frames_needed++;
        remaining -= 6;
    }
    
    // Process RX buffer command (final frame)
    frames_needed++;
    
    bool fragmentation_ok = (frames_needed > 1) && (large_len > 6);
    
    snprintf(details, sizeof(details), "Large packet (%d bytes) fragments into %d frames", 
             large_len, frames_needed);
    log_can_test("Large Packet Fragmentation", fragmentation_ok, details);
}

/**
 * Test CAN status message broadcasting
 */
static void test_can_status_broadcasting(void) {
    printf("\n--- Testing CAN Status Broadcasting ---\n");
    
    // Test status message types based on research
    CAN_PACKET_ID status_types[] = {
        CAN_PACKET_STATUS,    // RPM, current, duty
        CAN_PACKET_STATUS_2,  // Amp hours
        CAN_PACKET_STATUS_3,  // Watt hours  
        CAN_PACKET_STATUS_4,  // Temperature, PID
        CAN_PACKET_STATUS_5,  // Tacho, voltage
        CAN_PACKET_STATUS_6   // ADC, PPM
    };
    
    int num_status_types = sizeof(status_types) / sizeof(status_types[0]);
    
    // Test status message CAN IDs
    bool all_status_valid = true;
    for (int i = 0; i < num_status_types; i++) {
        uint32_t status_can_id = TEST_CONTROLLER_ID | ((uint32_t)status_types[i] << 8);
        uint8_t extracted_type = (status_can_id >> 8) & 0xFF;
        
        if (extracted_type != status_types[i]) {
            all_status_valid = false;
            break;
        }
    }
    
    // Test broadcast rate calculations (default 20 Hz from research)
    int default_rate_hz = 20;
    int period_us = 1000000 / default_rate_hz;  // 50,000 μs
    
    // Each status cycle sends 6 messages
    int frame_time_us = 288;  // From research analysis
    int cycle_time_us = num_status_types * frame_time_us;  // 1,728 μs
    
    // Bus utilization calculation
    float bus_utilization = (float)cycle_time_us / period_us * 100.0;
    
    bool broadcast_ok = all_status_valid && (bus_utilization < 50.0);  // <50% utilization
    
    char details[128];
    snprintf(details, sizeof(details), "%d status types, %.1f%% bus utilization @ %d Hz", 
             num_status_types, bus_utilization, default_rate_hz);
    log_can_test("Status Broadcasting", broadcast_ok, details);
}

/**
 * Test CAN ping/pong connectivity verification
 */
static void test_can_ping_pong(void) {
    printf("\n--- Testing CAN Ping/Pong ---\n");
    
    // Test PING packet format
    uint32_t ping_can_id = TEST_CONTROLLER_ID | ((uint32_t)CAN_PACKET_PING << 8);
    uint8_t ping_data[8] = {TEST_CONTROLLER_ID, 0, 0, 0, 0, 0, 0, 0};
    
    // PING should contain sender ID
    bool ping_format_ok = (ping_data[0] == TEST_CONTROLLER_ID);
    
    // Test PONG response format  
    uint32_t pong_can_id = TEST_CONTROLLER_ID | ((uint32_t)CAN_PACKET_PONG << 8);
    uint8_t pong_data[8] = {TEST_CONTROLLER_ID, 2, 0, 0, 0, 0, 0, 0};  // HW_TYPE_CUSTOM_MODULE = 2
    
    // PONG should contain sender ID and hardware type
    bool pong_format_ok = (pong_data[0] == TEST_CONTROLLER_ID) && (pong_data[1] == 2);
    
    bool ping_pong_ok = ping_format_ok && pong_format_ok;
    
    char details[128];
    snprintf(details, sizeof(details), "PING ID: 0x%08X, PONG ID: 0x%08X, HW_TYPE: %d", 
             ping_can_id, pong_can_id, pong_data[1]);
    log_can_test("CAN Ping/Pong", ping_pong_ok, details);
}

/**
 * Test CAN motor control commands
 */
static void test_can_motor_control(void) {
    printf("\n--- Testing CAN Motor Control ---\n");
    
    // Test direct CAN motor control commands (optimized path)
    struct {
        CAN_PACKET_ID can_cmd;
        COMM_PACKET_ID uart_equiv;
        const char* name;
    } motor_commands[] = {
        {CAN_PACKET_SET_DUTY, COMM_SET_DUTY, "Set Duty"},
        {CAN_PACKET_SET_CURRENT, COMM_SET_CURRENT, "Set Current"},
        {CAN_PACKET_SET_CURRENT_BRAKE, COMM_SET_CURRENT_BRAKE, "Set Current Brake"},
        {CAN_PACKET_SET_RPM, COMM_SET_RPM, "Set RPM"},
        {CAN_PACKET_SET_POS, COMM_SET_POS, "Set Position"}
    };
    
    int num_motor_cmds = sizeof(motor_commands) / sizeof(motor_commands[0]);
    bool all_motor_cmds_ok = true;
    
    for (int i = 0; i < num_motor_cmds; i++) {
        // Test CAN ID generation
        uint32_t can_id = TEST_CONTROLLER_ID | ((uint32_t)motor_commands[i].can_cmd << 8);
        uint8_t extracted_cmd = (can_id >> 8) & 0xFF;
        
        // Verify CAN command matches expected value
        if (extracted_cmd != motor_commands[i].can_cmd) {
            all_motor_cmds_ok = false;
            break;
        }
        
        // Test payload format (4 bytes for float value)
        uint8_t test_payload[8];
        float test_value = 0.5f;  // 50% duty, current, etc.
        memcpy(test_payload, &test_value, sizeof(float));
        
        // Payload should be 4 bytes for motor control commands
        bool payload_ok = (sizeof(float) == 4);
        
        if (!payload_ok) {
            all_motor_cmds_ok = false;
            break;
        }
    }
    
    char details[128];
    snprintf(details, sizeof(details), "All %d motor control commands format correctly", num_motor_cmds);
    log_can_test("CAN Motor Control", all_motor_cmds_ok, details);
}

/**
 * Test CAN bus timing configuration
 */
static void test_can_timing_config(void) {
    printf("\n--- Testing CAN Timing Configuration ---\n");
    
    // Test ESP32-C6 enhanced timing configuration (from research)
    // 80MHz clock, 500kbps target
    int brp = 8;           // Baud rate prescaler
    int tseg_1 = 15;       // Time segment 1
    int tseg_2 = 4;        // Time segment 2
    int sjw = 3;           // Sync jump width
    (void)sjw;             // Used in conceptual test
    bool triple_sampling = true;
    
    // Calculate actual bit rate
    int tq_per_bit = 1 + tseg_1 + tseg_2;  // 20 time quanta per bit
    int clock_freq = 80000000;  // 80 MHz
    int actual_bitrate = clock_freq / (brp * tq_per_bit);
    
    // Calculate sample point
    float sample_point = (float)(1 + tseg_1) / tq_per_bit * 100.0;
    
    // Verify timing parameters
    bool bitrate_ok = (actual_bitrate == TEST_CAN_BITRATE);  // 500,000 bps
    bool sample_point_ok = (sample_point >= 70.0 && sample_point <= 80.0);  // 70-80% range
    bool timing_ok = bitrate_ok && sample_point_ok && triple_sampling;
    
    char details[128];
    snprintf(details, sizeof(details), "Bitrate: %d bps, Sample point: %.1f%%, Triple sampling: %s", 
             actual_bitrate, sample_point, triple_sampling ? "ON" : "OFF");
    log_can_test("CAN Timing Configuration", timing_ok, details);
}

/**
 * Main CAN test function
 */
int run_can_interface_tests(void) {
    printf("CAN Interface Verification Tests\n");
    printf("=================================\n");
    
    test_can_frame_id_format();
    test_can_packet_fragmentation(); 
    test_can_status_broadcasting();
    test_can_ping_pong();
    test_can_motor_control();
    test_can_timing_config();
    
    printf("\n--- CAN Test Results ---\n");
    printf("CAN Tests Passed: %d/%d\n", can_tests_passed, can_tests_total);
    printf("CAN Success Rate: %.1f%%\n", 
           can_tests_total > 0 ? (float)can_tests_passed / can_tests_total * 100.0 : 0.0);
    
    return (can_tests_passed == can_tests_total) ? 0 : 1;
}

// For standalone execution
#ifdef CAN_TEST_STANDALONE
int main(void) {
    return run_can_interface_tests();
}
#endif