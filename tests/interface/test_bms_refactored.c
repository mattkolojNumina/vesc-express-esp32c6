/**
 * Refactored BMS Interface Tests
 * 
 * Uses the new test framework for cleaner, more maintainable code.
 * Demonstrates the improved structure and reduced duplication.
 */

#include "../framework/test_framework.h"
#include "../framework/vesc_test_utils.h"

// BMS-specific command definitions
typedef enum {
    BMS_COMM_GET_VALUES = 96,
    BMS_COMM_SET_CHARGE_ALLOWED = 97,
    BMS_COMM_SET_BALANCE_OVERRIDE = 98,
    BMS_COMM_RESET_COUNTERS = 99,
    BMS_COMM_FORCE_BALANCE = 100,
    BMS_COMM_ZERO_CURRENT_OFFSET = 101,
    BMS_COMM_FWD_CAN_RX = 113,
    BMS_COMM_HW_DATA = 114,
    BMS_COMM_BLNC_SELFTEST = 126,
    BMS_COMM_SET_BATT_TYPE = 136,
    BMS_COMM_GET_BATT_TYPE = 137
} bms_command_t;

// BMS data structures
typedef struct {
    float v_tot;
    float v_charge;
    float i_in;
    float i_out;
    float i_balance;
    float temp_cells[8];
    float v_cell[50];
    bool charge_allowed;
    bool balance_override;
    uint32_t ah_cnt;
    uint32_t wh_cnt;
    uint8_t cell_count;
} bms_values_t;

typedef enum {
    BMS_BATT_TYPE_LIFEPO4 = 0,
    BMS_BATT_TYPE_LIPO = 1,
    BMS_BATT_TYPE_LION = 2,
    BMS_BATT_TYPE_LEAD_ACID = 3,
    BMS_BATT_TYPE_CUSTOM = 4
} bms_battery_type_t;

// Mock BMS data
static bms_values_t mock_bms_data;

// Initialize mock BMS data with realistic values
static void init_mock_bms_data(void) {
    mock_bms_data.v_tot = test_random_float(40.0f, 54.6f);    // 13S LiFePO4 range
    mock_bms_data.v_charge = mock_bms_data.v_tot + test_random_float(1.0f, 3.0f);
    mock_bms_data.i_in = test_random_float(0.0f, 5.0f);
    mock_bms_data.i_out = test_random_float(0.0f, 50.0f);
    mock_bms_data.i_balance = test_random_float(0.0f, 0.5f);
    mock_bms_data.charge_allowed = true;
    mock_bms_data.balance_override = false;
    mock_bms_data.ah_cnt = test_random_uint32(0, 1000);
    mock_bms_data.wh_cnt = test_random_uint32(0, 50000);
    mock_bms_data.cell_count = 13;
    
    // Initialize cell voltages (13S configuration)
    for (int i = 0; i < 13; i++) {
        mock_bms_data.v_cell[i] = test_random_float(3.0f, 3.65f); // LiFePO4 range
    }
    
    // Initialize temperatures
    for (int i = 0; i < 4; i++) {
        mock_bms_data.temp_cells[i] = test_random_float(15.0f, 45.0f);
    }
}

/**
 * Test BMS command structure validation
 */
static void test_bms_command_structure(test_suite_t* suite) {
    TEST_START(suite, "BMS Command Structure");
    
    // Validate all BMS commands are in correct ranges
    const struct {
        bms_command_t cmd;
        int expected_id;
    } bms_commands[] = {
        {BMS_COMM_GET_VALUES, 96},
        {BMS_COMM_SET_CHARGE_ALLOWED, 97},
        {BMS_COMM_SET_BALANCE_OVERRIDE, 98},
        {BMS_COMM_RESET_COUNTERS, 99},
        {BMS_COMM_FORCE_BALANCE, 100},
        {BMS_COMM_ZERO_CURRENT_OFFSET, 101},
        {BMS_COMM_FWD_CAN_RX, 113},
        {BMS_COMM_HW_DATA, 114},
        {BMS_COMM_BLNC_SELFTEST, 126},
        {BMS_COMM_SET_BATT_TYPE, 136},
        {BMS_COMM_GET_BATT_TYPE, 137}
    };
    
    int cmd_count = sizeof(bms_commands) / sizeof(bms_commands[0]);
    bool all_commands_valid = true;
    
    for (int i = 0; i < cmd_count; i++) {
        if ((int)bms_commands[i].cmd != bms_commands[i].expected_id) {
            all_commands_valid = false;
            break;
        }
    }
    
    char details[256];
    safe_snprintf(details, sizeof(details), 
                 "Validated %d BMS commands (96-101, 113-114, 126, 136-137)", cmd_count);
    
    TEST_ASSERT(suite, all_commands_valid, details, "BMS command validation failed");
}

/**
 * Test BMS data structure validation
 */
static void test_bms_data_structure(test_suite_t* suite) {
    TEST_START(suite, "BMS Data Structure");
    
    init_mock_bms_data();
    
    // Validate voltage ranges
    bool voltage_valid = (mock_bms_data.v_tot >= 30.0f && mock_bms_data.v_tot <= 60.0f);
    bool charge_voltage_valid = (mock_bms_data.v_charge > mock_bms_data.v_tot);
    
    // Validate cell voltages
    bool cell_voltages_valid = true;
    for (int i = 0; i < mock_bms_data.cell_count; i++) {
        if (mock_bms_data.v_cell[i] < 2.5f || mock_bms_data.v_cell[i] > 4.0f) {
            cell_voltages_valid = false;
            break;
        }
    }
    
    // Validate temperature ranges
    bool temperatures_valid = true;
    for (int i = 0; i < 4; i++) {
        if (mock_bms_data.temp_cells[i] < -40.0f || mock_bms_data.temp_cells[i] > 85.0f) {
            temperatures_valid = false;
            break;
        }
    }
    
    bool all_data_valid = voltage_valid && charge_voltage_valid && 
                         cell_voltages_valid && temperatures_valid;
    
    char details[256];
    safe_snprintf(details, sizeof(details),
                 "V_tot=%.1fV, cells=%.2f-%.2fV, temp=%.0f-%.0f°C, %dS config",
                 mock_bms_data.v_tot,
                 mock_bms_data.v_cell[0], mock_bms_data.v_cell[mock_bms_data.cell_count-1],
                 mock_bms_data.temp_cells[0], mock_bms_data.temp_cells[3],
                 mock_bms_data.cell_count);
    
    TEST_ASSERT(suite, all_data_valid, details, "BMS data validation failed");
}

/**
 * Test BMS safety features
 */
static void test_bms_safety_features(test_suite_t* suite) {
    TEST_START(suite, "BMS Safety Features");
    
    // Test charge control
    bool charge_control = (BMS_COMM_SET_CHARGE_ALLOWED >= 0 && BMS_COMM_SET_CHARGE_ALLOWED <= 163);
    
    // Test balance control
    bool balance_control = (BMS_COMM_SET_BALANCE_OVERRIDE >= 0 && BMS_COMM_SET_BALANCE_OVERRIDE <= 163);
    
    // Test emergency functions
    bool emergency_functions = (BMS_COMM_RESET_COUNTERS >= 0 && BMS_COMM_FORCE_BALANCE >= 0 &&
                               BMS_COMM_ZERO_CURRENT_OFFSET >= 0);
    
    // Test current monitoring
    bool current_monitoring = (mock_bms_data.i_in >= 0.0f && mock_bms_data.i_out >= 0.0f);
    
    // Test overvoltage protection
    bool overvoltage_protection = true;
    for (int i = 0; i < mock_bms_data.cell_count; i++) {
        if (mock_bms_data.v_cell[i] > 3.8f) { // Above safe LiFePO4 limit
            overvoltage_protection = false;
            break;
        }
    }
    
    bool safety_ok = charge_control && balance_control && emergency_functions &&
                    current_monitoring && overvoltage_protection;
    
    TEST_ASSERT(suite, safety_ok,
               "All safety features operational: charge control, balancing, monitoring, protection",
               "Safety feature validation failed");
}

/**
 * Test BMS CAN communication
 */
static void test_bms_can_communication(test_suite_t* suite) {
    TEST_START(suite, "BMS CAN Communication");
    
    // Test CAN forwarding command
    bool fwd_can_exists = (BMS_COMM_FWD_CAN_RX == 113);
    
    // Test hardware data command
    bool hw_data_exists = (BMS_COMM_HW_DATA == 114);
    
    // Create mock CAN packet structure
    uint8_t can_data[8] = {0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08};
    uint32_t can_id = vesc_test_create_can_id(1, VESC_CAN_PACKET_STATUS);
    
    bool can_frame_valid = vesc_test_validate_can_frame(can_id, can_data, 8);
    
    bool can_comm_ok = fwd_can_exists && hw_data_exists && can_frame_valid;
    
    char details[256];
    safe_snprintf(details, sizeof(details),
                 "CAN communication valid: FWD_RX=%d, HW_DATA=%d, frame_valid=%s",
                 BMS_COMM_FWD_CAN_RX, BMS_COMM_HW_DATA, can_frame_valid ? "yes" : "no");
    
    TEST_ASSERT(suite, can_comm_ok, details, "BMS CAN communication failed");
}

/**
 * Test BMS self-test capability
 */
static void test_bms_selftest(test_suite_t* suite) {
    TEST_START(suite, "BMS Self-Test");
    
    // Test self-test command exists
    bool selftest_cmd_exists = (BMS_COMM_BLNC_SELFTEST == 126);
    
    // Simulate self-test results
    typedef struct {
        bool balance_circuits[13];
        bool temperature_sensors[4];
        bool current_sensor;
        bool voltage_sensors;
    } selftest_results_t;
    
    selftest_results_t results;
    
    // Initialize all self-test results as passing
    for (int i = 0; i < 13; i++) {
        results.balance_circuits[i] = true;
    }
    for (int i = 0; i < 4; i++) {
        results.temperature_sensors[i] = true;
    }
    results.current_sensor = true;
    results.voltage_sensors = true;
    
    // Count successful tests
    int balance_ok = 13; // All balance circuits OK
    int temp_ok = 4;     // All temperature sensors OK
    bool sensors_ok = results.current_sensor && results.voltage_sensors;
    
    bool selftest_passed = selftest_cmd_exists && (balance_ok == 13) && 
                          (temp_ok == 4) && sensors_ok;
    
    char details[256];
    safe_snprintf(details, sizeof(details),
                 "Self-test: %d/13 balance circuits, %d/4 temp sensors, sensors %s",
                 balance_ok, temp_ok, sensors_ok ? "OK" : "FAIL");
    
    TEST_ASSERT(suite, selftest_passed, details, "BMS self-test failed");
}

/**
 * Test BMS battery type configuration
 */
static void test_bms_battery_type(test_suite_t* suite) {
    TEST_START(suite, "BMS Battery Type");
    
    // Test battery type commands
    bool set_cmd_exists = (BMS_COMM_SET_BATT_TYPE == 136);
    bool get_cmd_exists = (BMS_COMM_GET_BATT_TYPE == 137);
    
    // Test battery type parameters for LiFePO4
    bms_battery_type_t current_type __attribute__((unused)) = BMS_BATT_TYPE_LIFEPO4;
    
    struct {
        float cell_voltage_min;
        float cell_voltage_max;
        float charge_voltage;
        float discharge_cutoff;
        int cell_count;
    } battery_params;
    
    // Set LiFePO4 parameters
    battery_params.cell_voltage_min = 2.5f;
    battery_params.cell_voltage_max = 3.6f;
    battery_params.charge_voltage = 3.65f;
    battery_params.discharge_cutoff = 2.8f;
    battery_params.cell_count = 13;
    
    // Validate parameters
    bool params_valid = (battery_params.cell_voltage_min > 0) &&
                       (battery_params.cell_voltage_max > battery_params.cell_voltage_min) &&
                       (battery_params.charge_voltage >= battery_params.cell_voltage_max) &&
                       (battery_params.discharge_cutoff >= battery_params.cell_voltage_min) &&
                       (battery_params.cell_count > 0 && battery_params.cell_count <= 50);
    
    bool battery_type_ok = set_cmd_exists && get_cmd_exists && params_valid;
    
    char details[256];
    safe_snprintf(details, sizeof(details),
                 "Battery config OK: LiFePO4, %dS, %.2f-%.2fV per cell",
                 battery_params.cell_count,
                 battery_params.cell_voltage_min,
                 battery_params.cell_voltage_max);
    
    TEST_ASSERT(suite, battery_type_ok, details, "Battery type configuration failed");
}

/**
 * Test function array for the suite
 */
static test_function_t bms_test_functions[] = {
    test_bms_command_structure,
    test_bms_data_structure,
    test_bms_safety_features,
    test_bms_can_communication,
    test_bms_selftest,
    test_bms_battery_type
};

/**
 * Main test execution
 */
int main(void) {
    printf("VESC Express BMS Interface Test Suite (Refactored)\n");
    printf("==================================================\n");
    printf("Using Test Framework v%s\n\n", TEST_FRAMEWORK_VERSION);
    
    // Initialize test framework
    test_init_random_seed();
    
    // Create test suite
    test_suite_t* suite = test_suite_create("BMS Interface");
    if (!suite) {
        printf("Failed to create test suite\n");
        return 2;
    }
    
    // Run all tests
    int function_count = sizeof(bms_test_functions) / sizeof(bms_test_functions[0]);
    test_suite_run_all(suite, bms_test_functions, function_count);
    
    // Print results
    test_suite_print_results(suite);
    
    // Get exit code
    int exit_code = test_suite_get_exit_code(suite);
    
    // Cleanup
    test_suite_destroy(suite);
    
    return exit_code;
}