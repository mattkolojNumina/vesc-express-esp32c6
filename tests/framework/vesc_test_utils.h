/**
 * VESC-Specific Test Utilities
 * 
 * Common utilities and patterns specific to VESC Express testing.
 */

#ifndef VESC_TEST_UTILS_H
#define VESC_TEST_UTILS_H

#include "test_framework.h"

// Feature test macros for usleep
#ifndef _GNU_SOURCE
#define _GNU_SOURCE
#endif

// VESC protocol constants
#define VESC_PACKET_START_BYTE     0x02
#define VESC_PACKET_END_BYTE       0x03
#define VESC_MAX_PACKET_SIZE       512
#define VESC_UART_BAUDRATE         115200
#define VESC_CAN_BITRATE          500000

// Common VESC command IDs (subset for testing)
typedef enum {
    VESC_COMM_FW_VERSION = 0,
    VESC_COMM_GET_VALUES = 4,
    VESC_COMM_SET_DUTY = 5,
    VESC_COMM_SET_CURRENT = 6,
    VESC_COMM_FORWARD_CAN = 34,
    VESC_COMM_GET_MCCONF = 14,
    VESC_COMM_SET_MCCONF = 15
} vesc_comm_packet_id_t;

// VESC CAN packet types
typedef enum {
    VESC_CAN_PACKET_SET_DUTY = 0,
    VESC_CAN_PACKET_SET_CURRENT = 1,
    VESC_CAN_PACKET_SET_RPM = 3,
    VESC_CAN_PACKET_FILL_RX_BUFFER = 5,
    VESC_CAN_PACKET_PROCESS_RX_BUFFER = 6,
    VESC_CAN_PACKET_PROCESS_SHORT_BUFFER = 7,
    VESC_CAN_PACKET_STATUS = 9
} vesc_can_packet_id_t;

// VESC packet structure
typedef struct {
    uint8_t start_byte;
    uint8_t length;
    uint8_t payload[VESC_MAX_PACKET_SIZE];
    uint16_t crc;
    uint8_t end_byte;
    int total_size;
} vesc_packet_t;

// Mock VESC data structures
typedef struct {
    float temp_mos;
    float temp_motor;
    float current_motor;
    float current_in;
    float duty_now;
    float rpm;
    float v_in;
    float amp_hours;
    float amp_hours_charged;
    float watt_hours;
    float watt_hours_charged;
    int tachometer;
    int tachometer_abs;
    uint8_t fault_code;
} vesc_values_t;

// VESC test utilities
extern void vesc_test_init_mock_values(vesc_values_t* values);
extern bool vesc_test_validate_packet_structure(const vesc_packet_t* packet);
extern uint16_t vesc_test_calculate_crc16(const uint8_t* data, int length);
extern int vesc_test_create_uart_packet(uint8_t command, const uint8_t* data, int data_len, 
                                        uint8_t* packet_buffer);
extern uint32_t vesc_test_create_can_id(uint8_t controller_id, vesc_can_packet_id_t packet_type);
extern bool vesc_test_validate_can_frame(uint32_t can_id, const uint8_t* data, int length);

// Protocol bridge testing
extern bool vesc_test_validate_bridge_packet(const uint8_t* packet, int length, 
                                            uint8_t expected_controller_id, 
                                            uint8_t expected_command);

// Performance validation
extern bool vesc_test_validate_timing_requirements(uint64_t latency_us, const char* operation);
extern bool vesc_test_validate_throughput_requirements(float kbps, const char* interface);

// Hardware configuration validation
extern bool vesc_test_validate_gpio_assignment(int pin, const char* function);
extern bool vesc_test_validate_interface_parameters(const char* interface, int baudrate);

// Mock hardware functions
extern void vesc_test_mock_uart_send(const uint8_t* data, int length);
extern void vesc_test_mock_can_transmit(uint32_t id, const uint8_t* data, int length);
extern bool vesc_test_mock_gpio_setup(int pin, const char* mode);

// Error injection for robustness testing
extern void vesc_test_inject_crc_error(uint8_t* packet, int packet_size);
extern void vesc_test_inject_timeout_error(void);
extern void vesc_test_inject_buffer_overflow(void);

// Test data generators
extern void vesc_test_generate_motor_values(vesc_values_t* values, bool realistic);
extern void vesc_test_generate_can_traffic(uint8_t controller_count, int packet_count);
extern void vesc_test_generate_uart_commands(int command_count);

#endif // VESC_TEST_UTILS_H