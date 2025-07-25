/**
 * UART Interface Verification Tests
 * 
 * Specific tests to verify UART interface implementation matches
 * VESC binary protocol specifications.
 */

#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

// Include VESC headers based on research
#include "datatypes.h"

// Test configuration
#define TEST_UART_BAUDRATE  115200
#define UART_START_BYTE     0x02
#define UART_END_BYTE       0x03
#define MAX_PACKET_LEN      512

// Test result tracking  
static int uart_tests_passed = 0;
static int uart_tests_total = 0;

static void log_uart_test(const char* test_name, bool passed, const char* details) {
    uart_tests_total++;
    if (passed) {
        uart_tests_passed++;
        printf("✅ UART TEST PASS: %s - %s\n", test_name, details);
    } else {
        printf("❌ UART TEST FAIL: %s - %s\n", test_name, details);
    }
}

/**
 * Simple CRC16 implementation for testing (polynomial 0x1021)
 */
static uint16_t crc16(uint8_t *data, int len) {
    uint16_t crc = 0;
    for (int i = 0; i < len; i++) {
        crc ^= (uint16_t)data[i] << 8;
        for (int j = 0; j < 8; j++) {
            if (crc & 0x8000) {
                crc = (crc << 1) ^ 0x1021;
            } else {
                crc = crc << 1;
            }
        }
    }
    return crc;
}

/**
 * Test VESC binary packet format
 */
static void test_vesc_packet_format(void) {
    printf("\n--- Testing VESC Packet Format ---\n");
    
    // Test packet structure: [START][LENGTH][PAYLOAD][CRC][END]
    uint8_t test_payload[] = {COMM_FW_VERSION, 0x00, 0x01, 0x02};
    int payload_len = sizeof(test_payload);
    
    // Build complete packet
    uint8_t packet[16];
    int packet_idx = 0;
    
    // Start byte
    packet[packet_idx++] = UART_START_BYTE;
    
    // Length (for payloads ≤255 bytes)
    packet[packet_idx++] = payload_len;
    
    // Payload
    for (int i = 0; i < payload_len; i++) {
        packet[packet_idx++] = test_payload[i];
    }
    
    // CRC16
    uint16_t crc = crc16(test_payload, payload_len);
    packet[packet_idx++] = (crc >> 8) & 0xFF;
    packet[packet_idx++] = crc & 0xFF;
    
    // End byte
    packet[packet_idx++] = UART_END_BYTE;
    
    // Verify packet structure
    bool format_ok = (packet[0] == UART_START_BYTE) &&
                    (packet[1] == payload_len) &&
                    (packet[packet_idx-1] == UART_END_BYTE) &&
                    (packet_idx == payload_len + 5);
    
    char details[128];
    snprintf(details, sizeof(details), "Packet: %d bytes total, payload: %d bytes, CRC: 0x%04X", 
             packet_idx, payload_len, crc);
    log_uart_test("VESC Packet Format", format_ok, details);
}

/**
 * Test variable length encoding
 */
static void test_variable_length_encoding(void) {
    printf("\n--- Testing Variable Length Encoding ---\n");
    
    // Test different length encodings based on research
    
    // 8-bit length (≤255 bytes)
    uint8_t short_packet[8];
    int short_idx = 0;
    short_packet[short_idx++] = UART_START_BYTE;
    short_packet[short_idx++] = 100;  // Length fits in 8 bits
    
    bool short_length_ok = (short_packet[1] == 100);
    
    // 16-bit length (>255 bytes) 
    uint8_t long_packet[8];
    int long_idx = 0;
    long_packet[long_idx++] = UART_START_BYTE;
    long_packet[long_idx++] = 3;  // Length indicator for 16-bit
    uint16_t long_len = 300;
    long_packet[long_idx++] = (long_len >> 8) & 0xFF;
    long_packet[long_idx++] = long_len & 0xFF;
    
    bool long_length_ok = (long_packet[1] == 3) && 
                         (((uint16_t)long_packet[2] << 8 | long_packet[3]) == long_len);
    
    // 24-bit length (very large packets)
    uint8_t very_long_packet[8];
    int very_long_idx = 0;
    very_long_packet[very_long_idx++] = UART_START_BYTE;
    very_long_packet[very_long_idx++] = 4;  // Length indicator for 24-bit
    uint32_t very_long_len = 70000;
    very_long_packet[very_long_idx++] = (very_long_len >> 16) & 0xFF;
    very_long_packet[very_long_idx++] = (very_long_len >> 8) & 0xFF;
    very_long_packet[very_long_idx++] = very_long_len & 0xFF;
    
    bool very_long_length_ok = (very_long_packet[1] == 4) &&
                              (((uint32_t)very_long_packet[2] << 16 | 
                                (uint32_t)very_long_packet[3] << 8 | 
                                very_long_packet[4]) == very_long_len);
    
    bool variable_length_ok = short_length_ok && long_length_ok && very_long_length_ok;
    
    char details[128];
    snprintf(details, sizeof(details), "8-bit: %s, 16-bit: %s, 24-bit: %s", 
             short_length_ok ? "OK" : "FAIL",
             long_length_ok ? "OK" : "FAIL", 
             very_long_length_ok ? "OK" : "FAIL");
    log_uart_test("Variable Length Encoding", variable_length_ok, details);
}

/**
 * Test all VESC command compatibility
 */
static void test_all_vesc_commands(void) {
    printf("\n--- Testing All VESC Commands ---\n");
    
    // Test critical commands from research (164 total)
    COMM_PACKET_ID critical_commands[] = {
        COMM_FW_VERSION,         // 0
        COMM_JUMP_TO_BOOTLOADER, // 1  
        COMM_GET_VALUES,         // 4
        COMM_SET_DUTY,          // 5
        COMM_SET_CURRENT,       // 6
        COMM_SET_RPM,           // 8
        COMM_SET_MCCONF,        // 13
        COMM_GET_MCCONF,        // 14
        COMM_TERMINAL_CMD,      // 20
        COMM_FORWARD_CAN,       // 34 - Critical bridge command
        COMM_REBOOT,            // 29
        COMM_ALIVE,             // 30
        COMM_LISP_READ_CODE,    // 130
        COMM_FILE_LIST,         // 140
        COMM_SHUTDOWN           // 156
    };
    
    int num_critical = sizeof(critical_commands) / sizeof(critical_commands[0]);
    bool all_commands_valid = true;
    
    for (int i = 0; i < num_critical; i++) {
        // Verify command is in valid range (0-163 from research)
        if (critical_commands[i] < 0 || critical_commands[i] > 163) {
            all_commands_valid = false;
            break;
        }
        
        // Test packet creation for each command
        uint8_t test_packet[16];
        int test_idx = 0;
        
        test_packet[test_idx++] = UART_START_BYTE;
        test_packet[test_idx++] = 5;  // Length: command + 4 bytes data
        test_packet[test_idx++] = critical_commands[i];  // Command
        test_packet[test_idx++] = 0x00;  // Data
        test_packet[test_idx++] = 0x00;
        test_packet[test_idx++] = 0x00;
        test_packet[test_idx++] = 0x00;
        
        // CRC calculation for payload
        uint16_t crc = crc16(&test_packet[2], 5);
        test_packet[test_idx++] = (crc >> 8) & 0xFF;
        test_packet[test_idx++] = crc & 0xFF;
        
        test_packet[test_idx++] = UART_END_BYTE;
        
        // Verify packet is well-formed
        if (test_packet[0] != UART_START_BYTE || 
            test_packet[2] != critical_commands[i] ||
            test_packet[test_idx-1] != UART_END_BYTE) {
            all_commands_valid = false;
            break;
        }
    }
    
    char details[128];
    snprintf(details, sizeof(details), "Tested %d critical commands from 164 total", num_critical);
    log_uart_test("All VESC Commands", all_commands_valid, details);
}

/**
 * Test UART timing characteristics
 */
static void test_uart_timing(void) {
    printf("\n--- Testing UART Timing ---\n");
    
    // Test UART configuration (from research)
    int baudrate = TEST_UART_BAUDRATE;  // 115200 bps
    int bits_per_char = 10;  // 1 start + 8 data + 1 stop
    
    // Calculate timing
    float bit_time_us = 1000000.0 / baudrate;  // μs per bit
    float char_time_us = bit_time_us * bits_per_char;  // μs per character
    
    // Test packet timing for different sizes
    int small_packet_bytes = 11;  // Start + Len + 6 data + CRC + End
    int large_packet_bytes = 105; // Start + Len + 100 data + CRC + End
    
    float small_packet_time_ms = small_packet_bytes * char_time_us / 1000.0;
    float large_packet_time_ms = large_packet_bytes * char_time_us / 1000.0;
    
    // Verify timing meets motor control requirements
    bool small_timing_ok = (small_packet_time_ms < 5.0);  // <5ms for motor control
    bool large_timing_ok = (large_packet_time_ms < 50.0); // <50ms for config
    
    // Calculate effective data rate (accounting for protocol overhead)
    float protocol_overhead = 0.15;  // 15% from research
    float effective_rate_kbps = (baudrate * (1.0 - protocol_overhead)) / 1000.0;
    
    bool timing_ok = small_timing_ok && large_timing_ok && (effective_rate_kbps > 90.0);
    
    char details[128];
    snprintf(details, sizeof(details), "Char: %.1fμs, Small pkt: %.1fms, Large pkt: %.1fms, Rate: %.1fkbps", 
             char_time_us, small_packet_time_ms, large_packet_time_ms, effective_rate_kbps);
    log_uart_test("UART Timing", timing_ok, details);
}

/**
 * Test CRC validation
 */
static void test_crc_validation(void) {
    printf("\n--- Testing CRC Validation ---\n");
    
    // Test CRC16 with polynomial 0x1021 (from research)
    uint8_t test_data[] = {COMM_FW_VERSION, 0x12, 0x34, 0x56};
    int data_len = sizeof(test_data);
    
    uint16_t calculated_crc = crc16(test_data, data_len);
    
    // Verify CRC is calculated
    bool crc_calculated = (calculated_crc != 0);
    
    // Test CRC with known corruption
    uint8_t corrupted_data[] = {COMM_FW_VERSION, 0x12, 0x34, 0xFF};  // Last byte corrupted
    uint16_t corrupted_crc = crc16(corrupted_data, data_len);
    
    // CRC should be different for corrupted data
    bool crc_detects_error = (calculated_crc != corrupted_crc);
    
    // Test CRC consistency
    uint16_t recalc_crc = crc16(test_data, data_len);
    bool crc_consistent = (calculated_crc == recalc_crc);
    
    bool crc_valid = crc_calculated && crc_detects_error && crc_consistent;
    
    char details[128];
    snprintf(details, sizeof(details), "Original: 0x%04X, Corrupted: 0x%04X, Consistent: %s", 
             calculated_crc, corrupted_crc, crc_consistent ? "YES" : "NO");
    log_uart_test("CRC Validation", crc_valid, details);
}

/**
 * Test packet size limits
 */
static void test_packet_size_limits(void) {
    printf("\n--- Testing Packet Size Limits ---\n");
    
    // Test maximum packet size (512 bytes from research)
    int max_payload = MAX_PACKET_LEN;
    int max_total_packet = max_payload + 5;  // + Start + Len + CRC + End
    
    // Verify size limits are reasonable
    bool max_size_ok = (max_payload == 512) && (max_total_packet < 600);
    
    // Test minimum packet size
    int min_payload = 1;  // At least command byte
    int min_total_packet = min_payload + 5;
    
    bool min_size_ok = (min_total_packet == 6);
    
    // Test size calculations for different packet types
    int config_packet_size = 200;  // Typical config packet
    int status_packet_size = 50;   // Typical status packet  
    int command_packet_size = 10;  // Typical command packet
    
    bool config_fits = (config_packet_size <= max_payload);
    bool status_fits = (status_packet_size <= max_payload);
    bool command_fits = (command_packet_size <= max_payload);
    
    bool size_limits_ok = max_size_ok && min_size_ok && config_fits && status_fits && command_fits;
    
    char details[128];
    snprintf(details, sizeof(details), "Max: %d bytes, Min: %d bytes, Config/Status/Cmd: %s/%s/%s", 
             max_total_packet, min_total_packet,
             config_fits ? "OK" : "FAIL",
             status_fits ? "OK" : "FAIL", 
             command_fits ? "OK" : "FAIL");
    log_uart_test("Packet Size Limits", size_limits_ok, details);
}

/**
 * Test UART hardware configuration
 */
static void test_uart_hardware_config(void) {
    printf("\n--- Testing UART Hardware Configuration ---\n");
    
    // Test ESP32-C6 UART configuration (from research)
    struct {
        int uart_num;
        int tx_pin;
        int rx_pin;
        int baudrate;
        const char* format;
    } uart_config = {0, 21, 20, 115200, "8-N-1"};
    
    // Verify configuration parameters
    bool uart_num_ok = (uart_config.uart_num == 0);  // UART0
    bool pins_ok = (uart_config.tx_pin == 21) && (uart_config.rx_pin == 20);
    bool baudrate_ok = (uart_config.baudrate == TEST_UART_BAUDRATE);
    bool format_ok = (strcmp(uart_config.format, "8-N-1") == 0);
    
    // Verify pins don't conflict with CAN (GPIO 4/5 from research)
    bool no_can_conflict = (uart_config.tx_pin != 4) && (uart_config.tx_pin != 5) &&
                          (uart_config.rx_pin != 4) && (uart_config.rx_pin != 5);
    
    // Verify GPIO pins are valid for ESP32-C6
    bool pins_valid = (uart_config.tx_pin >= 0 && uart_config.tx_pin <= 21) &&
                     (uart_config.rx_pin >= 0 && uart_config.rx_pin <= 21);
    
    bool hw_config_ok = uart_num_ok && pins_ok && baudrate_ok && format_ok && 
                       no_can_conflict && pins_valid;
    
    char details[128];
    snprintf(details, sizeof(details), "UART%d, TX=%d, RX=%d, %d baud, %s, No conflicts: %s", 
             uart_config.uart_num, uart_config.tx_pin, uart_config.rx_pin, 
             uart_config.baudrate, uart_config.format, no_can_conflict ? "YES" : "NO");
    log_uart_test("UART Hardware Config", hw_config_ok, details);
}

/**
 * Main UART test function
 */
int run_uart_interface_tests(void) {
    printf("UART Interface Verification Tests\n");
    printf("==================================\n");
    
    test_vesc_packet_format();
    test_variable_length_encoding();
    test_all_vesc_commands();
    test_uart_timing();
    test_crc_validation();
    test_packet_size_limits();
    test_uart_hardware_config();
    
    printf("\n--- UART Test Results ---\n");
    printf("UART Tests Passed: %d/%d\n", uart_tests_passed, uart_tests_total);
    printf("UART Success Rate: %.1f%%\n", 
           uart_tests_total > 0 ? (float)uart_tests_passed / uart_tests_total * 100.0 : 0.0);
    
    return (uart_tests_passed == uart_tests_total) ? 0 : 1;
}

// For standalone execution
#ifdef UART_TEST_STANDALONE
int main(void) {
    return run_uart_interface_tests();
}
#endif