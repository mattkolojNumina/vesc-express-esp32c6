/**
 * VESC-Specific Test Utilities Implementation
 */

#define _GNU_SOURCE  // Enable GNU extensions including usleep
#include "vesc_test_utils.h"
#include <unistd.h>

// Static state for mock functions
static bool mock_uart_initialized = false;
static bool mock_can_initialized = false;
static int mock_packets_sent = 0;

/**
 * Initialize mock VESC values with realistic data
 */
void vesc_test_init_mock_values(vesc_values_t* values) {
    if (!values) return;
    
    // Realistic motor controller values
    values->temp_mos = test_random_float(25.0f, 65.0f);      // MOSFET temperature
    values->temp_motor = test_random_float(20.0f, 80.0f);    // Motor temperature
    values->current_motor = test_random_float(-50.0f, 50.0f); // Motor current (A)
    values->current_in = test_random_float(0.0f, 30.0f);     // Input current (A)
    values->duty_now = test_random_float(-1.0f, 1.0f);       // Duty cycle (-100% to +100%)
    values->rpm = test_random_float(-5000.0f, 5000.0f);      // Motor RPM
    values->v_in = test_random_float(36.0f, 84.0f);          // Input voltage (typical range)
    values->amp_hours = test_random_float(0.0f, 100.0f);     // Amp hours used
    values->amp_hours_charged = test_random_float(0.0f, 100.0f); // Amp hours charged
    values->watt_hours = test_random_float(0.0f, 5000.0f);   // Watt hours used
    values->watt_hours_charged = test_random_float(0.0f, 5000.0f); // Watt hours charged
    values->tachometer = test_random_uint32(0, 1000000);     // Tachometer
    values->tachometer_abs = test_random_uint32(0, 1000000); // Absolute tachometer
    values->fault_code = 0; // No fault
}

/**
 * Validate VESC packet structure
 */
bool vesc_test_validate_packet_structure(const vesc_packet_t* packet) {
    if (!packet) return false;
    
    // Check frame bytes
    if (packet->start_byte != VESC_PACKET_START_BYTE) return false;
    if (packet->end_byte != VESC_PACKET_END_BYTE) return false;
    
    // Check length consistency - skip this check as length is uint8_t (max 255) and VESC_MAX_PACKET_SIZE is 512
    // This check would always be false, so we comment it out to avoid the warning
    // if (packet->length > VESC_MAX_PACKET_SIZE) return false;
    if (packet->total_size != (packet->length + 5)) return false; // +5 for framing
    
    return true;
}

/**
 * Calculate CRC16 using VESC polynomial (0x1021)
 */
uint16_t vesc_test_calculate_crc16(const uint8_t* data, int length) {
    if (!data || length <= 0) return 0;
    
    uint16_t crc = 0;
    for (int i = 0; i < length; i++) {
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
 * Create a VESC UART packet
 */
int vesc_test_create_uart_packet(uint8_t command, const uint8_t* data, int data_len, 
                                uint8_t* packet_buffer) {
    if (!packet_buffer || data_len < 0 || data_len > VESC_MAX_PACKET_SIZE - 1) {
        return -1;
    }
    
    int packet_idx = 0;
    
    // Start byte
    packet_buffer[packet_idx++] = VESC_PACKET_START_BYTE;
    
    // Length (command + data)
    uint8_t payload_len = 1 + data_len;
    packet_buffer[packet_idx++] = payload_len;
    
    // Command
    packet_buffer[packet_idx++] = command;
    
    // Data payload
    if (data && data_len > 0) {
        memcpy(&packet_buffer[packet_idx], data, data_len);
        packet_idx += data_len;
    }
    
    // Calculate CRC over payload
    uint16_t crc = vesc_test_calculate_crc16(&packet_buffer[2], payload_len);
    packet_buffer[packet_idx++] = (crc >> 8) & 0xFF;
    packet_buffer[packet_idx++] = crc & 0xFF;
    
    // End byte
    packet_buffer[packet_idx++] = VESC_PACKET_END_BYTE;
    
    return packet_idx;
}

/**
 * Create CAN ID with VESC format
 */
uint32_t vesc_test_create_can_id(uint8_t controller_id, vesc_can_packet_id_t packet_type) {
    return controller_id | ((uint32_t)packet_type << 8);
}

/**
 * Validate CAN frame format
 */
bool vesc_test_validate_can_frame(uint32_t can_id, const uint8_t* data, int length) {
    if (!data || length < 0 || length > 8) return false;
    
    // Extract controller ID and packet type
    uint8_t controller_id = can_id & 0xFF;
    uint8_t packet_type = (can_id >> 8) & 0xFF;
    
    // Validate controller ID range
    if (controller_id > 254) return false;
    
    // Validate packet type range (basic check)
    if (packet_type > 50) return false; // Reasonable upper bound
    
    // Validate data length for specific packet types
    switch (packet_type) {
        case VESC_CAN_PACKET_SET_DUTY:
        case VESC_CAN_PACKET_SET_CURRENT:
        case VESC_CAN_PACKET_SET_RPM:
            return length >= 4; // At least 4 bytes for these commands
        
        case VESC_CAN_PACKET_STATUS:
            return length >= 6; // Status packets need more data
        
        default:
            return length <= 8; // General CAN frame size limit
    }
}

/**
 * Validate bridge packet format
 */
bool vesc_test_validate_bridge_packet(const uint8_t* packet, int length, 
                                     uint8_t expected_controller_id, 
                                     uint8_t expected_command) {
    if (!packet || length < 7) return false; // Minimum bridge packet size
    
    // Check UART framing
    if (packet[0] != VESC_PACKET_START_BYTE) return false;
    if (packet[length-1] != VESC_PACKET_END_BYTE) return false;
    
    // Check payload length
    if (packet[1] != (length - 5)) return false; // Subtract framing bytes
    
    // Check bridge command
    if (packet[2] != VESC_COMM_FORWARD_CAN) return false;
    
    // Check target controller ID
    if (packet[3] != expected_controller_id) return false;
    
    // Check forwarded command
    if (packet[4] != expected_command) return false;
    
    return true;
}

/**
 * Validate timing requirements for VESC operations
 */
bool vesc_test_validate_timing_requirements(uint64_t latency_us, const char* operation) {
    if (!operation) return false;
    
    // Define timing requirements for different operations
    const struct {
        const char* op_name;
        uint64_t max_latency_us;
    } timing_requirements[] = {
        {"UART_PACKET", 5000},      // 5ms max for UART packet processing
        {"CAN_FRAME", 2000},        // 2ms max for CAN frame processing
        {"BRIDGE", 10000},          // 10ms max for bridge operations
        {"COMMAND", 15000},         // 15ms max for command processing
        {"CONFIG", 50000},          // 50ms max for configuration changes
    };
    
    int req_count = sizeof(timing_requirements) / sizeof(timing_requirements[0]);
    
    for (int i = 0; i < req_count; i++) {
        if (strstr(operation, timing_requirements[i].op_name) != NULL) {
            return latency_us <= timing_requirements[i].max_latency_us;
        }
    }
    
    // Default requirement: 20ms for unknown operations
    return latency_us <= 20000;
}

/**
 * Validate throughput requirements
 */
bool vesc_test_validate_throughput_requirements(float kbps, const char* interface) {
    if (!interface) return false;
    
    // Define minimum throughput requirements
    if (strstr(interface, "UART") != NULL) {
        return kbps >= 50.0f; // Minimum 50 kbps effective throughput
    } else if (strstr(interface, "CAN") != NULL) {
        return kbps >= 200.0f; // Minimum 200 kbps effective throughput
    }
    
    return kbps > 0.0f; // At least some throughput
}

/**
 * Validate GPIO pin assignments
 */
bool vesc_test_validate_gpio_assignment(int pin, const char* function) {
    if (!function || pin < 0 || pin > 21) return false; // ESP32-C6 GPIO range
    
    // Check for known pin conflicts or invalid assignments
    if (strstr(function, "CAN_TX") && pin != 4) return false;
    if (strstr(function, "CAN_RX") && pin != 5) return false;
    if (strstr(function, "UART_TX") && pin != 21) return false;
    if (strstr(function, "UART_RX") && pin != 20) return false;
    
    return true;
}

/**
 * Validate interface parameters
 */
bool vesc_test_validate_interface_parameters(const char* interface, int baudrate) {
    if (!interface) return false;
    
    if (strstr(interface, "UART") != NULL) {
        return baudrate == VESC_UART_BAUDRATE;
    } else if (strstr(interface, "CAN") != NULL) {
        return baudrate == VESC_CAN_BITRATE;
    }
    
    return baudrate > 0;
}

/**
 * Mock UART send function
 */
void vesc_test_mock_uart_send(const uint8_t* data, int length) {
    (void)data; // Suppress unused parameter warning
    if (length > 0) {
        mock_uart_initialized = true;
        mock_packets_sent++;
    }
}

/**
 * Mock CAN transmit function
 */
void vesc_test_mock_can_transmit(uint32_t id, const uint8_t* data, int length) {
    (void)id; (void)data; // Suppress unused parameter warnings
    if (length > 0) {
        mock_can_initialized = true;
        mock_packets_sent++;
    }
}

/**
 * Mock GPIO setup function
 */
bool vesc_test_mock_gpio_setup(int pin, const char* mode) {
    (void)mode; // Suppress unused parameter warning
    return vesc_test_validate_gpio_assignment(pin, mode);
}

/**
 * Inject CRC error for testing error handling
 */
void vesc_test_inject_crc_error(uint8_t* packet, int packet_size) {
    if (!packet || packet_size < 7) return;
    
    // Corrupt the CRC bytes (second to last and third to last bytes)
    packet[packet_size - 3] ^= 0xFF; // Flip CRC high byte
    packet[packet_size - 2] ^= 0xFF; // Flip CRC low byte
}

/**
 * Inject timeout error (simulation)
 */
void vesc_test_inject_timeout_error(void) {
    // In a real implementation, this would set up timeout conditions
    // For testing, we just simulate the delay
    usleep(50000); // 50ms delay to simulate timeout
}

/**
 * Inject buffer overflow (simulation)
 */
void vesc_test_inject_buffer_overflow(void) {
    // In a real implementation, this would attempt to overflow buffers
    // For testing, we just mark that an overflow condition was simulated
    (void)0; // No-op for safety in testing
}

/**
 * Generate realistic motor values for testing
 */
void vesc_test_generate_motor_values(vesc_values_t* values, bool realistic) {
    if (!values) return;
    
    if (realistic) {
        vesc_test_init_mock_values(values);
    } else {
        // Generate extreme/edge case values for stress testing
        values->temp_mos = test_random_float(-40.0f, 150.0f);
        values->temp_motor = test_random_float(-40.0f, 200.0f);
        values->current_motor = test_random_float(-1000.0f, 1000.0f);
        values->current_in = test_random_float(-100.0f, 100.0f);
        values->duty_now = test_random_float(-2.0f, 2.0f);
        values->rpm = test_random_float(-50000.0f, 50000.0f);
        values->v_in = test_random_float(0.0f, 200.0f);
        values->amp_hours = test_random_float(0.0f, 10000.0f);
        values->amp_hours_charged = test_random_float(0.0f, 10000.0f);
        values->watt_hours = test_random_float(0.0f, 100000.0f);
        values->watt_hours_charged = test_random_float(0.0f, 100000.0f);
        values->tachometer = test_random_uint32(0, UINT32_MAX);
        values->tachometer_abs = test_random_uint32(0, UINT32_MAX);
        values->fault_code = test_random_uint32(0, 15); // Various fault codes
    }
}

/**
 * Generate CAN traffic for load testing
 */
void vesc_test_generate_can_traffic(uint8_t controller_count, int packet_count) {
    if (controller_count == 0 || packet_count <= 0) return;
    
    for (int i = 0; i < packet_count; i++) {
        uint8_t controller_id = test_random_uint32(1, controller_count);
        vesc_can_packet_id_t packet_type = test_random_uint32(0, 10);
        uint32_t can_id = vesc_test_create_can_id(controller_id, packet_type);
        
        uint8_t data[8];
        int data_length = test_random_uint32(1, 8);
        for (int j = 0; j < data_length; j++) {
            data[j] = test_random_uint32(0, 255);
        }
        
        vesc_test_mock_can_transmit(can_id, data, data_length);
    }
}

/**
 * Generate UART commands for load testing
 */
void vesc_test_generate_uart_commands(int command_count) {
    if (command_count <= 0) return;
    
    const uint8_t common_commands[] = {
        VESC_COMM_FW_VERSION,
        VESC_COMM_GET_VALUES,
        VESC_COMM_SET_DUTY,
        VESC_COMM_SET_CURRENT,
        VESC_COMM_GET_MCCONF
    };
    
    int cmd_types = sizeof(common_commands) / sizeof(common_commands[0]);
    
    for (int i = 0; i < command_count; i++) {
        uint8_t command = common_commands[test_random_uint32(0, cmd_types - 1)];
        uint8_t data[32];
        int data_length = test_random_uint32(0, 32);
        
        for (int j = 0; j < data_length; j++) {
            data[j] = test_random_uint32(0, 255);
        }
        
        uint8_t packet[64];
        int packet_size = vesc_test_create_uart_packet(command, data, data_length, packet);
        if (packet_size > 0) {
            vesc_test_mock_uart_send(packet, packet_size);
        }
    }
}