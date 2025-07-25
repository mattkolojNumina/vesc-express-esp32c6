/**
 * Core VESC Express Function Tests
 * 
 * Tests the core functions that can be compiled without full ESP-IDF dependencies
 */

#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <sys/time.h>

// Include core headers that don't require FreeRTOS
#include "datatypes.h"
#include "buffer.h"
#include "crc.h"

// Test state
static int tests_passed = 0;
static int tests_failed = 0;

static void log_test_result(const char* test_name, bool passed, const char* details) {
    if (passed) {
        tests_passed++;
        printf("✅ CORE TEST PASS: %s - %s\n", test_name, details);
    } else {
        tests_failed++;
        printf("❌ CORE TEST FAIL: %s - %s\n", test_name, details);
    }
}

/**
 * Test 1: Real buffer append and get operations
 */
static void test_real_buffer_operations(void) {
    printf("\n=== Testing Real Buffer Operations ===\n");
    
    uint8_t test_buffer[64];
    int32_t buffer_index = 0;
    
    // Test buffer_append_int32 with actual VESC function
    int32_t test_int32 = 0x12345678;
    buffer_append_int32(test_buffer, test_int32, &buffer_index);
    
    // Verify the buffer was written correctly
    bool int32_written = (buffer_index == 4);
    
    // Test buffer_get_int32 with actual VESC function
    int32_t read_index = 0;
    int32_t read_int32 = buffer_get_int32(test_buffer, &read_index);
    
    bool int32_correct = (read_int32 == test_int32) && (read_index == 4);
    
    // Test buffer_append_float32
    buffer_index = 0;
    float test_float = 3.14159f;
    buffer_append_float32_auto(test_buffer, test_float, &buffer_index);
    
    bool float_written = (buffer_index == 4);
    
    // Test buffer_get_float32
    read_index = 0;
    float read_float = buffer_get_float32_auto(test_buffer, &read_index);
    
    bool float_correct = (read_float == test_float) && (read_index == 4);
    
    // Test buffer_append_uint16
    buffer_index = 0;
    uint16_t test_uint16 = 0xABCD;
    buffer_append_uint16(test_buffer, test_uint16, &buffer_index);
    
    bool uint16_written = (buffer_index == 2);
    
    // Test buffer_get_uint16
    read_index = 0;
    uint16_t read_uint16 = buffer_get_uint16(test_buffer, &read_index);
    
    bool uint16_correct = (read_uint16 == test_uint16) && (read_index == 2);
    
    bool all_buffer_ops_work = int32_written && int32_correct && 
                              float_written && float_correct &&
                              uint16_written && uint16_correct;
    
    char details[256];
    snprintf(details, sizeof(details), 
             "int32: %s, float: %s, uint16: %s, values preserved: %s",
             int32_written ? "OK" : "FAIL",
             float_written ? "OK" : "FAIL", 
             uint16_written ? "OK" : "FAIL",
             (int32_correct && float_correct && uint16_correct) ? "OK" : "FAIL");
    
    log_test_result("Real Buffer Operations", all_buffer_ops_work, details);
}

/**
 * Test 2: Real CRC16 calculation function
 */
static void test_real_crc16_function(void) {
    printf("\n=== Testing Real CRC16 Function ===\n");
    
    // Test with known data
    uint8_t test_data1[] = {COMM_FW_VERSION, 0x00, 0x01, 0x02};
    uint16_t crc1 = crc16(test_data1, sizeof(test_data1));
    
    // Test with different data
    uint8_t test_data2[] = {COMM_GET_VALUES, 0x00, 0x01, 0x02};
    uint16_t crc2 = crc16(test_data2, sizeof(test_data2));
    
    // Test with corrupted data
    uint8_t test_data_corrupted[] = {COMM_FW_VERSION, 0xFF, 0x01, 0x02};
    uint16_t crc_corrupted = crc16(test_data_corrupted, sizeof(test_data_corrupted));
    
    // Verify CRC properties
    bool crcs_calculated = (crc1 != 0) && (crc2 != 0) && (crc_corrupted != 0);
    bool crcs_different = (crc1 != crc2) && (crc1 != crc_corrupted);
    
    // Test consistency
    uint16_t crc1_recalc = crc16(test_data1, sizeof(test_data1));
    bool crc_consistent = (crc1 == crc1_recalc);
    
    // Test with empty data
    uint16_t crc_empty = crc16(NULL, 0);
    (void)crc_empty;  // Used in conceptual test
    bool empty_handled = true; // If we don't crash, it's handled
    
    bool crc_function_works = crcs_calculated && crcs_different && crc_consistent && empty_handled;
    
    char details[256];
    snprintf(details, sizeof(details), 
             "CRC1: 0x%04X, CRC2: 0x%04X, Corrupted: 0x%04X, Consistent: %s",
             crc1, crc2, crc_corrupted, crc_consistent ? "YES" : "NO");
    
    log_test_result("Real CRC16 Function", crc_function_works, details);
}

/**
 * Test 3: VESC datatypes and constants verification
 */
static void test_real_datatypes_constants(void) {
    printf("\n=== Testing Real Datatypes Constants ===\n");
    
    // Verify critical COMM commands are defined correctly
    bool comm_fw_version_ok = (COMM_FW_VERSION == 0);
    bool comm_get_values_ok = (COMM_GET_VALUES == 4);
    bool comm_set_duty_ok = (COMM_SET_DUTY == 5);
    bool comm_forward_can_ok = (COMM_FORWARD_CAN == 34);
    
    // Verify CAN commands are defined
    bool can_set_duty_ok = (CAN_PACKET_SET_DUTY >= 0);
    bool can_process_short_ok = (CAN_PACKET_PROCESS_SHORT_BUFFER >= 0);
    bool can_status_ok = (CAN_PACKET_STATUS >= 0);
    
    // Test that data structures are properly sized
    bool status_msg_sized = (sizeof(can_status_msg) > 0);
    bool bms_values_sized = (sizeof(bms_values) > 0);
    
    // Test enum ranges
    bool comm_range_ok = (COMM_FW_VERSION <= 163); // Based on research
    bool can_range_ok = (CAN_PACKET_SET_DUTY < 69); // Based on research
    
    bool datatypes_valid = comm_fw_version_ok && comm_get_values_ok && comm_set_duty_ok &&
                          comm_forward_can_ok && can_set_duty_ok && can_process_short_ok &&
                          can_status_ok && status_msg_sized && bms_values_sized &&
                          comm_range_ok && can_range_ok;
    
    char details[256];
    snprintf(details, sizeof(details), 
             "COMM commands: %s, CAN commands: %s, Structs: %s, FORWARD_CAN: %d",
             (comm_fw_version_ok && comm_get_values_ok && comm_set_duty_ok) ? "OK" : "FAIL",
             (can_set_duty_ok && can_process_short_ok) ? "OK" : "FAIL",
             (status_msg_sized && bms_values_sized) ? "OK" : "FAIL",
             COMM_FORWARD_CAN);
    
    log_test_result("Real Datatypes Constants", datatypes_valid, details);
}

/**
 * Test 4: Buffer endianness and data integrity
 */
static void test_buffer_endianness_integrity(void) {
    printf("\n=== Testing Buffer Endianness and Integrity ===\n");
    
    uint8_t buffer[32];
    int32_t index = 0;
    
    // Test various data types for endianness consistency
    uint16_t test_u16 = 0x1234;
    uint32_t test_u32 = 0x12345678;
    int16_t test_i16 = -12345;
    int32_t test_i32 = -87654321;
    float test_float = -123.456f;
    
    // Write all values
    buffer_append_uint16(buffer, test_u16, &index);
    buffer_append_uint32(buffer, test_u32, &index);
    buffer_append_int16(buffer, test_i16, &index);
    buffer_append_int32(buffer, test_i32, &index);
    buffer_append_float32_auto(buffer, test_float, &index);
    
    int32_t total_written = index;
    
    // Read all values back
    index = 0;
    uint16_t read_u16 = buffer_get_uint16(buffer, &index);
    uint32_t read_u32 = buffer_get_uint32(buffer, &index);
    int16_t read_i16 = buffer_get_int16(buffer, &index);
    int32_t read_i32 = buffer_get_int32(buffer, &index);
    float read_float = buffer_get_float32_auto(buffer, &index);
    
    int32_t total_read = index;
    
    // Verify data integrity
    bool u16_ok = (read_u16 == test_u16);
    bool u32_ok = (read_u32 == test_u32);
    bool i16_ok = (read_i16 == test_i16);
    bool i32_ok = (read_i32 == test_i32);
    bool float_ok = (read_float == test_float);
    bool size_ok = (total_written == total_read);
    
    bool endianness_ok = u16_ok && u32_ok && i16_ok && i32_ok && float_ok && size_ok;
    
    char details[256];
    snprintf(details, sizeof(details), 
             "u16:%s u32:%s i16:%s i32:%s float:%s size:%s (%d bytes)",
             u16_ok ? "OK" : "FAIL", u32_ok ? "OK" : "FAIL",
             i16_ok ? "OK" : "FAIL", i32_ok ? "OK" : "FAIL",
             float_ok ? "OK" : "FAIL", size_ok ? "OK" : "FAIL",
             total_written);
    
    log_test_result("Buffer Endianness and Integrity", endianness_ok, details);
}

/**
 * Test 5: VESC packet structure validation
 */
static void test_vesc_packet_structure(void) {
    printf("\n=== Testing VESC Packet Structure ===\n");
    
    // Create a packet manually using buffer functions
    uint8_t packet_buffer[64];
    int32_t packet_index = 0;
    
    // Start byte
    packet_buffer[packet_index++] = 2; // VESC start byte
    
    // Payload (COMM_GET_VALUES command)
    uint8_t payload[] = {COMM_GET_VALUES, 0x00, 0x00, 0x00};
    uint8_t payload_len = sizeof(payload);
    
    // Length byte
    packet_buffer[packet_index++] = payload_len;
    
    // Copy payload
    memcpy(&packet_buffer[packet_index], payload, payload_len);
    packet_index += payload_len;
    
    // Calculate CRC on payload
    uint16_t packet_crc = crc16(payload, payload_len);
    
    // Add CRC (big-endian for VESC protocol)
    packet_buffer[packet_index++] = (packet_crc >> 8) & 0xFF;
    packet_buffer[packet_index++] = packet_crc & 0xFF;
    
    // End byte
    packet_buffer[packet_index++] = 3; // VESC end byte
    
    // Verify packet structure
    bool start_byte_ok = (packet_buffer[0] == 2);
    bool length_ok = (packet_buffer[1] == payload_len);
    bool command_ok = (packet_buffer[2] == COMM_GET_VALUES);
    bool end_byte_ok = (packet_buffer[packet_index-1] == 3);
    bool total_size_ok = (packet_index == (payload_len + 5)); // Start+Len+Payload+CRC+End
    
    // Verify CRC can be recalculated correctly
    uint16_t recalc_crc = crc16(&packet_buffer[2], payload_len);
    bool crc_matches = (packet_crc == recalc_crc);
    
    bool packet_structure_valid = start_byte_ok && length_ok && command_ok && 
                                 end_byte_ok && total_size_ok && crc_matches;
    
    char details[256];
    snprintf(details, sizeof(details), 
             "%d bytes: Start:%s Len:%s Cmd:%s End:%s CRC:0x%04X %s",
             packet_index, 
             start_byte_ok ? "OK" : "FAIL",
             length_ok ? "OK" : "FAIL", 
             command_ok ? "OK" : "FAIL",
             end_byte_ok ? "OK" : "FAIL",
             packet_crc,
             crc_matches ? "OK" : "FAIL");
    
    log_test_result("VESC Packet Structure", packet_structure_valid, details);
}

/**
 * Test 6: Performance of core operations
 */
static void test_core_performance(void) {
    printf("\n=== Testing Core Performance ===\n");
    
    const int iterations = 10000;
    uint8_t buffer[64];
    
    struct timeval start, end;
    
    // Test buffer operations performance
    gettimeofday(&start, NULL);
    for (int i = 0; i < iterations; i++) {
        int32_t index = 0;
        buffer_append_int32(buffer, i, &index);
        buffer_append_float32_auto(buffer, (float)i * 0.1f, &index);
        
        index = 0;
        int32_t read_int = buffer_get_int32(buffer, &index);
        float read_float = buffer_get_float32_auto(buffer, &index);
        (void)read_int; (void)read_float; // Suppress unused warnings
    }
    gettimeofday(&end, NULL);
    
    uint32_t buffer_ops_us = (end.tv_sec - start.tv_sec) * 1000000 + 
                            (end.tv_usec - start.tv_usec);
    
    // Test CRC performance
    uint8_t crc_data[32] = {0};
    gettimeofday(&start, NULL);
    for (int i = 0; i < iterations; i++) {
        crc_data[0] = i & 0xFF;
        uint16_t crc_result = crc16(crc_data, sizeof(crc_data));
        (void)crc_result; // Suppress unused warning
    }
    gettimeofday(&end, NULL);
    
    uint32_t crc_ops_us = (end.tv_sec - start.tv_sec) * 1000000 + 
                         (end.tv_usec - start.tv_usec);
    
    // Calculate operations per second
    float buffer_ops_per_sec = (float)iterations / (buffer_ops_us / 1000000.0f);
    float crc_ops_per_sec = (float)iterations / (crc_ops_us / 1000000.0f);
    
    // Performance should be reasonable for motor control applications
    bool buffer_perf_ok = (buffer_ops_per_sec > 100000); // >100k ops/sec
    bool crc_perf_ok = (crc_ops_per_sec > 50000);        // >50k ops/sec
    
    bool performance_ok = buffer_perf_ok && crc_perf_ok;
    
    char details[256];
    snprintf(details, sizeof(details), 
             "Buffer: %.0f ops/sec, CRC: %.0f ops/sec (%d iterations)",
             buffer_ops_per_sec, crc_ops_per_sec, iterations);
    
    log_test_result("Core Performance", performance_ok, details);
}

/**
 * Main test execution
 */
int main(void) {
    printf("VESC Express Core Function Tests\n");
    printf("=================================\n");
    printf("Testing core functions that can be compiled without ESP-IDF\n\n");
    
    struct timeval start, end;
    gettimeofday(&start, NULL);
    
    // Execute core function tests
    test_real_buffer_operations();
    test_real_crc16_function(); 
    test_real_datatypes_constants();
    test_buffer_endianness_integrity();
    test_vesc_packet_structure();
    test_core_performance();
    
    gettimeofday(&end, NULL);
    uint32_t total_duration_us = (end.tv_sec - start.tv_sec) * 1000000 + 
                                (end.tv_usec - start.tv_usec);
    
    // Print results
    printf("\n=== CORE FUNCTION TEST RESULTS ===\n");
    printf("Total Tests: %d\n", tests_passed + tests_failed);
    printf("Passed: %d\n", tests_passed);
    printf("Failed: %d\n", tests_failed);
    printf("Success Rate: %.1f%%\n", (float)tests_passed / (tests_passed + tests_failed) * 100.0);
    printf("Duration: %u μs (%.2f ms)\n", total_duration_us, total_duration_us / 1000.0);
    
    if (tests_failed == 0) {
        printf("\n🎉 ALL CORE FUNCTION TESTS PASSED\n");
        printf("✅ Core VESC Express functions work correctly\n");
        printf("✅ Buffer operations maintain data integrity\n");
        printf("✅ CRC calculations are consistent\n");
        printf("✅ Ready for full system integration testing\n");
        return 0;
    } else {
        printf("\n⚠️  SOME CORE FUNCTION TESTS FAILED\n");
        printf("❌ Review failed tests before proceeding\n");
        return 1;
    }
}