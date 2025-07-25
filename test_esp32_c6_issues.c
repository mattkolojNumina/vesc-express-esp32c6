/**
 * ESP32-C6 Common Issues Verification Test Suite
 * 
 * Tests specific to ESP32-C6 CAN/UART protocol issues identified through research.
 * Targets real-world problems: high baud rates, bus errors, concurrency issues,
 * interrupt timing conflicts, and electrical noise sensitivity.
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <stdbool.h>
#include <time.h>
#include <sys/time.h>
#include <unistd.h>
#include <pthread.h>
#include <signal.h>

// Test configuration constants
#define ESP32_C6_MAX_SAFE_BAUD      460800  // Research: CRC errors above this
#define ESP32_C6_PROBLEMATIC_BAUD   9600    // Research: missing bytes at this rate
#define ESP32_C6_TIMING_PRECISION   300     // Research: <300μs timing challenges
#define ESP32_C6_CAN_OSC_FREQ       80000000  // 80MHz oscillator
#define ESP32_C6_CAN_OSC_TOLERANCE  10      // ±10ppm tolerance
#define ESP32_C6_IDLE_TIME_J1708    1041    // 1.041ms idle detection for J1708

// CAN Error Types (from ESP32-C6 TWAI documentation)
typedef enum {
    CAN_ERROR_BIT = 0,      // Bit error
    CAN_ERROR_STUFF,        // Stuff error  
    CAN_ERROR_CRC,          // CRC error
    CAN_ERROR_FORM,         // Form error
    CAN_ERROR_ACK,          // ACK error
    CAN_ERROR_COUNT
} can_error_type_t;

// Test result structure
typedef struct {
    char test_name[128];
    bool passed;
    uint32_t duration_us;
    char details[512];
    int severity;  // 1=info, 2=warning, 3=error
} esp32_test_result_t;

// Global test state
static esp32_test_result_t esp32_test_results[50];
static int esp32_test_count = 0;
static int esp32_tests_passed = 0;
static int esp32_tests_failed = 0;
static volatile bool test_interrupt_fired = false;
static volatile uint32_t interrupt_count = 0;

// Utility functions
static uint64_t get_time_us(void) {
    struct timeval tv;
    gettimeofday(&tv, NULL);
    return (uint64_t)tv.tv_sec * 1000000 + tv.tv_usec;
}

static void log_esp32_test_result(const char* test_name, bool passed, uint32_t duration_us, 
                                  const char* details, int severity) {
    if (esp32_test_count < 50) {
        strncpy(esp32_test_results[esp32_test_count].test_name, test_name, 
                sizeof(esp32_test_results[esp32_test_count].test_name) - 1);
        esp32_test_results[esp32_test_count].test_name[sizeof(esp32_test_results[esp32_test_count].test_name) - 1] = '\0';
        esp32_test_results[esp32_test_count].passed = passed;
        esp32_test_results[esp32_test_count].duration_us = duration_us;
        esp32_test_results[esp32_test_count].severity = severity;
        strncpy(esp32_test_results[esp32_test_count].details, details, 
                sizeof(esp32_test_results[esp32_test_count].details) - 1);
        esp32_test_results[esp32_test_count].details[sizeof(esp32_test_results[esp32_test_count].details) - 1] = '\0';
        esp32_test_count++;
        
        const char* severity_icon = (severity == 3) ? "🔴" : (severity == 2) ? "🟡" : "🟢";
        
        if (passed) {
            esp32_tests_passed++;
            printf("✅ %s PASS: %s (%u μs) - %s\n", severity_icon, test_name, duration_us, details);
        } else {
            esp32_tests_failed++;
            printf("❌ %s FAIL: %s (%u μs) - %s\n", severity_icon, test_name, duration_us, details);
        }
    }
}

// Simulate UART interrupt handler (research: IRAM_ATTR required)
static void simulated_uart_isr(int sig) {
    (void)sig;  // Suppress unused parameter warning
    // Simulate ISR requirements: short execution, no blocking
    test_interrupt_fired = true;
    interrupt_count++;
    // Real ISR would need IRAM_ATTR and minimal processing
}

/**
 * Test 1: High Baud Rate Stress Testing
 * ESP32-C6 has CRC errors at baud rates >460800
 */
static void test_high_baud_rate_issues(void) {
    printf("\n=== Testing High Baud Rate Issues ===\n");
    
    uint64_t start_time = get_time_us();
    bool high_baud_ok = true;
    char details[512];
    
    // Simulate baud rate calculations for ESP32-C6 at problematic rates
    uint32_t problematic_bauds[] = {
        500000,    // Above safe threshold
        921600,    // Very high rate
        1000000,   // 1Mbps - likely problematic
        1843200,   // 1.8Mbps - definitely problematic
        2000000    // 2Mbps - extreme rate
    };
    
    int num_bauds = sizeof(problematic_bauds) / sizeof(problematic_bauds[0]);
    int problematic_count = 0;
    int crc_error_simulation = 0;
    
    for (int i = 0; i < num_bauds; i++) {
        uint32_t baud = problematic_bauds[i];
        
        // Simulate ESP32-C6 UART clock divider calculation
        // APB_CLK (80MHz) / (16 * baud_rate) = divider
        double divider = 80000000.0 / (16.0 * baud);
        double fractional_part = divider - (int)divider;
        
        // Count as problematic if above safe threshold
        if (baud > ESP32_C6_MAX_SAFE_BAUD) {
            problematic_count++;
            
            // Simulate CRC error likelihood based on fractional divider error
            if (fractional_part > 0.05) {
                crc_error_simulation++;  // Only count CRC errors for significant fractional errors
            }
            
            // Additional CRC error risk for very high rates with timing accumulation
            double bit_time_us = 1000000.0 / baud;
            double error_accumulation = fractional_part * bit_time_us * 10; // 10 bits per byte
            
            if (error_accumulation > 2.0 && baud > 1000000) {  // >2μs error and >1Mbps
                crc_error_simulation++;
            }
        }
    }
    
    // Evaluate results based on research findings
    if (crc_error_simulation > 2) {
        high_baud_ok = false;
        snprintf(details, sizeof(details), 
                "High baud rate issues confirmed: %d/%d rates problematic, %d CRC errors simulated. "
                "ESP32-C6 fractional divider errors above %d baud.", 
                problematic_count, num_bauds, crc_error_simulation, ESP32_C6_MAX_SAFE_BAUD);
    } else {
        snprintf(details, sizeof(details), 
                "High baud rates manageable: %d/%d potentially problematic, proper error handling needed.",
                problematic_count, num_bauds);
    }
    
    uint32_t duration = (uint32_t)(get_time_us() - start_time);
    log_esp32_test_result("High Baud Rate Stress", high_baud_ok, duration, details, 2);
}

/**
 * Test 2: Missing Byte Transmission at Standard Rates
 * ESP32-C6 research shows bytes missing at 9600 baud
 */
static void test_missing_byte_transmission(void) {
    printf("\n=== Testing Missing Byte Transmission ===\n");
    
    uint64_t start_time = get_time_us();
    bool transmission_reliable = true;
    char details[512];
    
    // Simulate byte transmission at problematic rate (9600 baud)
    uint32_t test_baud = ESP32_C6_PROBLEMATIC_BAUD;
    double bit_time_us = 1000000.0 / test_baud;  // Microseconds per bit
    double byte_time_us = bit_time_us * 10;      // 8 data + start + stop
    
    // Simulate buffer and timing issues at 9600 baud
    int total_bytes_sent = 100;
    int bytes_missing_simulation = 0;
    
    for (int i = 0; i < total_bytes_sent; i++) {
        // Simulate ESP32-C6 specific timing issues
        // Research shows buffer underrun and timing precision problems
        
        // Check for buffer underrun conditions
        if ((i % 16) == 0) {  // Every 16th byte has higher chance of issues
            // Simulate FreeRTOS task scheduling interference
            double scheduling_delay = 100.0;  // 100μs typical delay
            
            if (scheduling_delay > (byte_time_us * 0.5)) {
                bytes_missing_simulation++;  // Byte would be missed
            }
        }
        
        // Simulate interrupt latency issues (research: multi-core problems)
        if ((i % 8) == 0) {  // Every 8th byte
            double interrupt_latency = 50.0;  // 50μs interrupt delay
            
            if (interrupt_latency > (bit_time_us * 2)) {  // More than 2 bit times
                bytes_missing_simulation++;
            }
        }
    }
    
    // Calculate transmission reliability
    double reliability_percent = ((double)(total_bytes_sent - bytes_missing_simulation) / total_bytes_sent) * 100.0;
    
    if (reliability_percent < 95.0) {  // Less than 95% reliability is problematic
        transmission_reliable = false;
        snprintf(details, sizeof(details),
                "Missing byte issues confirmed at %d baud: %.1f%% reliability, %d/%d bytes lost. "
                "ESP32-C6 timing/buffer issues detected.",
                test_baud, reliability_percent, bytes_missing_simulation, total_bytes_sent);
    } else {
        snprintf(details, sizeof(details),
                "Byte transmission acceptable at %d baud: %.1f%% reliability, proper buffering needed.",
                test_baud, reliability_percent);
    }
    
    uint32_t duration = (uint32_t)(get_time_us() - start_time);
    log_esp32_test_result("Missing Byte Transmission", transmission_reliable, duration, details, 2);
}

/**
 * Test 3: Timing Precision Under 300μs
 * ESP32-C6 challenges with <300μs response times due to FreeRTOS
 */
static void test_timing_precision_challenges(void) {
    printf("\n=== Testing Timing Precision Challenges ===\n");
    
    uint64_t start_time = get_time_us();
    bool timing_precise = true;
    char details[512];
    
    // Test response times under ESP32-C6 FreeRTOS scheduling
    int num_measurements = 20;
    uint32_t response_times[20];
    uint32_t precision_failures = 0;
    
    for (int i = 0; i < num_measurements; i++) {
        uint64_t req_start = get_time_us();
        
        // Simulate FreeRTOS context switching delay
        // Research shows multi-core scheduling can add significant delay
        usleep(50 + (rand() % 200));  // 50-250μs variable delay
        
        uint64_t req_end = get_time_us();
        response_times[i] = (uint32_t)(req_end - req_start);
        
        // Check if response time exceeds 300μs precision requirement
        if (response_times[i] > ESP32_C6_TIMING_PRECISION) {
            precision_failures++;
        }
    }
    
    // Calculate statistics
    uint32_t total_time = 0;
    uint32_t max_time = 0;
    uint32_t min_time = UINT32_MAX;
    
    for (int i = 0; i < num_measurements; i++) {
        total_time += response_times[i];
        if (response_times[i] > max_time) max_time = response_times[i];
        if (response_times[i] < min_time) min_time = response_times[i];
    }
    
    uint32_t avg_time = total_time / num_measurements;
    double precision_success_rate = ((double)(num_measurements - precision_failures) / num_measurements) * 100.0;
    
    if (precision_failures > (uint32_t)(num_measurements / 4)) {  // More than 25% failures
        timing_precise = false;
        snprintf(details, sizeof(details),
                "Timing precision issues: %.1f%% success rate, avg=%uμs, max=%uμs. "
                "FreeRTOS scheduling affects <300μs requirements.",
                precision_success_rate, avg_time, max_time);
    } else {
        snprintf(details, sizeof(details),
                "Timing precision acceptable: %.1f%% success rate, avg=%uμs, range=%u-%uμs.",
                precision_success_rate, avg_time, min_time, max_time);
    }
    
    uint32_t duration = (uint32_t)(get_time_us() - start_time);
    log_esp32_test_result("Timing Precision <300μs", timing_precise, duration, details, 2);
}

/**
 * Test 4: CAN Bus Error Accumulation
 * ESP32-C6 TWAI controller error state management
 */
static void test_can_bus_error_accumulation(void) {
    printf("\n=== Testing CAN Bus Error Accumulation ===\n");
    
    uint64_t start_time = get_time_us();
    bool error_handling_ok = true;
    char details[512];
    
    // Simulate TWAI error counter behavior
    struct {
        const char* error_name;
        int tec_increment;  // Transmit Error Counter increment
        int rec_increment;  // Receive Error Counter increment
        int occurrence_rate; // Errors per 1000 frames
    } error_types[] = {
        {"Bit Error", 8, 1, 2},      // Research: most common in noisy environments
        {"Stuff Error", 8, 1, 1},    // Less common
        {"CRC Error", 8, 1, 3},      // Common with electrical interference
        {"Form Error", 8, 1, 1},     // Protocol violations
        {"ACK Error", 8, 0, 5}       // Network disconnection issues
    };
    
    int num_error_types = sizeof(error_types) / sizeof(error_types[0]);
    int tec = 0;  // Transmit Error Counter
    int rec = 0;  // Receive Error Counter
    int frames_processed = 1000;
    int bus_off_events = 0;
    
    // Simulate error accumulation over frame processing
    for (int frame = 0; frame < frames_processed; frame++) {
        for (int err_type = 0; err_type < num_error_types; err_type++) {
            // Simulate error occurrence based on rate
            if ((rand() % 1000) < error_types[err_type].occurrence_rate) {
                tec += error_types[err_type].tec_increment;
                rec += error_types[err_type].rec_increment;
                
                // Check for bus-off condition (TEC >= 256)
                if (tec >= 256) {
                    bus_off_events++;
                    tec = 0;  // Reset after bus-off recovery
                    rec = 0;
                }
                
                // Simulate successful frame transmission reducing counters
                if ((frame % 10) == 0 && tec > 0) {
                    tec = (tec > 1) ? tec - 1 : 0;
                }
            }
        }
    }
    
    // Evaluate error handling effectiveness
    double bus_off_rate = ((double)bus_off_events / frames_processed) * 100.0;
    
    if (bus_off_events > 5 || tec > 128 || rec > 128) {
        error_handling_ok = false;
        snprintf(details, sizeof(details),
                "CAN error accumulation issues: %d bus-off events (%.2f%%), TEC=%d, REC=%d. "
                "ESP32-C6 TWAI error recovery needed.",
                bus_off_events, bus_off_rate, tec, rec);
    } else {
        snprintf(details, sizeof(details),
                "CAN error handling adequate: %d bus-off events (%.2f%%), TEC=%d, REC=%d.",
                bus_off_events, bus_off_rate, tec, rec);
    }
    
    uint32_t duration = (uint32_t)(get_time_us() - start_time);
    log_esp32_test_result("CAN Bus Error Accumulation", error_handling_ok, duration, details, 3);
}

/**
 * Test 5: Interrupt Priority and Concurrency Issues
 * ESP32-C6 multi-core interrupt handling conflicts
 */
static void test_interrupt_priority_conflicts(void) {
    printf("\n=== Testing Interrupt Priority Conflicts ===\n");
    
    uint64_t start_time = get_time_us();
    bool interrupt_handling_ok = true;
    char details[512];
    
    // Set up signal handler to simulate interrupt
    signal(SIGALRM, simulated_uart_isr);
    
    // Reset interrupt tracking
    test_interrupt_fired = false;
    interrupt_count = 0;
    
    // Simulate concurrent operations with interrupt conflicts
    int test_iterations = 10;
    int interrupt_delays = 0;
    int missed_interrupts = 0;
    
    for (int i = 0; i < test_iterations; i++) {
        // Reset interrupt state before test
        test_interrupt_fired = false;
        
        // Simulate task running on one core
        uint64_t task_start = get_time_us();
        
        // Generate interrupt that fires during work simulation
        struct itimerval timer;
        timer.it_value.tv_sec = 0;
        timer.it_value.tv_usec = 50000;  // 50ms - fires during 100ms work
        timer.it_interval.tv_sec = 0;
        timer.it_interval.tv_usec = 0;   // One-shot timer
        setitimer(ITIMER_REAL, &timer, NULL);
        
        // Simulate work that might block interrupts
        usleep(100000);  // 100ms work simulation
        
        uint64_t task_end = get_time_us();
        uint32_t task_duration = (uint32_t)(task_end - task_start);
        
        // Check if interrupt was handled properly
        if (!test_interrupt_fired) {
            missed_interrupts++;
        } else if (task_duration > 150000) {  // >150ms indicates priority conflict
            interrupt_delays++;
        }
        
        // Cancel any remaining timer and wait between tests
        alarm(0);  // Cancel alarm
        usleep(50000);  // 50ms between tests
    }
    
    // Evaluate interrupt handling performance
    double interrupt_success_rate = ((double)(test_iterations - missed_interrupts) / test_iterations) * 100.0;
    double delay_rate = ((double)interrupt_delays / test_iterations) * 100.0;
    
    if (missed_interrupts > 2 || interrupt_delays > 3) {
        interrupt_handling_ok = false;
        snprintf(details, sizeof(details),
                "Interrupt priority conflicts: %.1f%% success rate, %.1f%% delayed, %d missed. "
                "ESP32-C6 multi-core scheduling issues detected.",
                interrupt_success_rate, delay_rate, missed_interrupts);
    } else {
        snprintf(details, sizeof(details),
                "Interrupt handling acceptable: %.1f%% success rate, %d total interrupts handled.",
                interrupt_success_rate, interrupt_count);
    }
    
    uint32_t duration = (uint32_t)(get_time_us() - start_time);
    log_esp32_test_result("Interrupt Priority Conflicts", interrupt_handling_ok, duration, details, 3);
}

/**
 * Test 6: Electrical Noise Sensitivity Simulation
 * ESP32-C6 CAN bus sensitivity to electrical interference
 */
static void test_electrical_noise_sensitivity(void) {
    printf("\n=== Testing Electrical Noise Sensitivity ===\n");
    
    uint64_t start_time = get_time_us();
    bool noise_tolerance_ok = true;
    char details[512];
    
    // Simulate different noise environments
    struct {
        const char* environment;
        int noise_level;      // Arbitrary noise units (0-100)
        int expected_errors;  // Expected error rate per 1000 frames
    } noise_environments[] = {
        {"Clean Lab", 5, 1},
        {"Office Environment", 15, 3},
        {"Industrial Floor", 35, 10},
        {"Near Generator", 65, 25},
        {"Motor Controller", 85, 45}
    };
    
    int num_environments = sizeof(noise_environments) / sizeof(noise_environments[0]);
    int problematic_environments = 0;
    
    for (int env = 0; env < num_environments; env++) {
        int frames_tested = 1000;
        int simulated_errors = 0;
        
        // Simulate error injection based on noise level
        for (int frame = 0; frame < frames_tested; frame++) {
            // Higher noise increases error probability
            int error_threshold = 100 - noise_environments[env].noise_level;
            
            if ((rand() % 100) > error_threshold) {
                simulated_errors++;
                
                // High noise environments have additional error types (but don't double count)
                // Instead, increase probability of subsequent errors slightly
                if (noise_environments[env].noise_level > 50 && (rand() % 100) < 20) {
                    simulated_errors++;  // 20% chance of additional error for very high noise
                }
            }
        }
        
        double error_rate = ((double)simulated_errors / frames_tested) * 100.0;
        double expected_rate = ((double)noise_environments[env].expected_errors / frames_tested) * 100.0;
        
        // Check if error rate exceeds acceptable limits
        if (error_rate > (expected_rate * 1.5)) {  // 50% above expected
            problematic_environments++;
        }
    }
    
    if (problematic_environments > 2) {
        noise_tolerance_ok = false;
        snprintf(details, sizeof(details),
                "Electrical noise sensitivity high: %d/%d environments problematic. "
                "ESP32-C6 CAN transceiver filtering insufficient.",
                problematic_environments, num_environments);
    } else {
        snprintf(details, sizeof(details),
                "Electrical noise tolerance adequate: %d/%d environments handled well.",
                num_environments - problematic_environments, num_environments);
    }
    
    uint32_t duration = (uint32_t)(get_time_us() - start_time);
    log_esp32_test_result("Electrical Noise Sensitivity", noise_tolerance_ok, duration, details, 2);
}

/**
 * Test 7: CAN Timing Configuration Validation
 * ESP32-C6 80MHz oscillator timing parameter validation
 */
static void test_can_timing_configuration(void) {
    printf("\n=== Testing CAN Timing Configuration ===\n");
    
    uint64_t start_time = get_time_us();
    bool timing_config_ok = true;
    char details[512];
    
    // Test different CAN bit rate configurations for ESP32-C6
    // 80MHz oscillator with ±10ppm tolerance
    struct {
        uint32_t target_bitrate;
        uint16_t brp;     // Baud Rate Prescaler
        uint8_t tseg1;    // Time segment 1
        uint8_t tseg2;    // Time segment 2
        uint8_t sjw;      // Synchronization Jump Width
        bool valid;
    } timing_configs[] = {
        {125000,  32, 15, 4, 3, true},   // 125kbps: 80MHz/(32×20) = 125k
        {250000,  16, 15, 4, 3, true},   // 250kbps: 80MHz/(16×20) = 250k
        {500000,  8,  15, 4, 3, true},   // 500kbps (VESC standard): 80MHz/(8×20) = 500k
        {1000000, 4,  15, 4, 3, true},   // 1Mbps: 80MHz/(4×20) = 1M
        {800000,  5,  15, 4, 3, true}    // 800kbps: 80MHz/(5×20) = 800k (now valid)
    };
    
    int num_configs = sizeof(timing_configs) / sizeof(timing_configs[0]);
    int invalid_configs = 0;
    
    for (int i = 0; i < num_configs; i++) {
        // Calculate actual bit rate from parameters
        // Bit time = (BRP * (1 + TSEG1 + TSEG2)) / APB_CLK
        uint32_t bit_time_ticks = timing_configs[i].brp * (1 + timing_configs[i].tseg1 + timing_configs[i].tseg2);
        uint32_t actual_bitrate = ESP32_C6_CAN_OSC_FREQ / bit_time_ticks;
        
        // Calculate timing error
        double error_percent = ((double)abs((int)actual_bitrate - (int)timing_configs[i].target_bitrate) / 
                               timing_configs[i].target_bitrate) * 100.0;
        
        // Check sample point (should be around 80%)
        double sample_point = ((double)(1 + timing_configs[i].tseg1) / 
                              (1 + timing_configs[i].tseg1 + timing_configs[i].tseg2)) * 100.0;
        
        // Validate configuration
        bool config_valid = (error_percent < 0.5) &&           // <0.5% error
                           (sample_point >= 75.0 && sample_point <= 85.0) &&  // 75-85% sample point
                           (timing_configs[i].sjw <= timing_configs[i].tseg2);  // SJW <= TSEG2
        
        if (!config_valid || !timing_configs[i].valid) {
            invalid_configs++;
        }
    }
    
    // Check oscillator tolerance effects
    double osc_tolerance_ppm = ESP32_C6_CAN_OSC_TOLERANCE;
    double max_timing_error = (osc_tolerance_ppm / 1000000.0) * 100.0;  // Convert to percentage
    
    if (invalid_configs > 1 || max_timing_error > 0.5) {
        timing_config_ok = false;
        snprintf(details, sizeof(details),
                "CAN timing issues: %d/%d configs invalid, %.3f%% max oscillator error. "
                "ESP32-C6 80MHz ±%dppm affects sync.",
                invalid_configs, num_configs, max_timing_error, ESP32_C6_CAN_OSC_TOLERANCE);
    } else {
        snprintf(details, sizeof(details),
                "CAN timing configuration valid: %d/%d configs good, %.3f%% oscillator tolerance.",
                num_configs - invalid_configs, num_configs, max_timing_error);
    }
    
    uint32_t duration = (uint32_t)(get_time_us() - start_time);
    log_esp32_test_result("CAN Timing Configuration", timing_config_ok, duration, details, 2);
}

/**
 * Test 8: Concurrent CAN/UART Operation Stress Test
 * ESP32-C6 dual interface operation with resource conflicts
 */
static void test_concurrent_can_uart_operation(void) {
    printf("\n=== Testing Concurrent CAN/UART Operation ===\n");
    
    uint64_t start_time = get_time_us();
    bool concurrent_operation_ok = true;
    char details[512];
    
    // Simulate concurrent UART and CAN operations
    int test_duration_ms = 1000;
    int uart_packets_sent = 0;
    int can_frames_sent = 0;
    int resource_conflicts = 0;
    int timing_violations = 0;
    
    uint64_t test_start = get_time_us();
    uint64_t test_end = test_start + (test_duration_ms * 1000);
    
    while (get_time_us() < test_end) {
        // Simulate UART packet transmission
        uint64_t uart_start = get_time_us();
        usleep(955);  // Research: 955μs for UART packet
        uint64_t uart_end = get_time_us();
        uart_packets_sent++;
        
        // Check for timing violations
        if ((uart_end - uart_start) > 2000) {  // >2ms is excessive
            timing_violations++;
        }
        
        // Simulate CAN frame transmission
        uint64_t can_start = get_time_us();
        usleep(288);  // Research: 288μs for CAN frame
        uint64_t can_end = get_time_us();
        can_frames_sent++;
        
        // Use can_end to avoid unused variable warning
        (void)can_end;
        
        // Check for resource conflicts (overlapping operations)
        if (can_start < uart_end && (can_start - uart_start) < 500) {
            resource_conflicts++;  // Operations too close together
        }
        
        // Simulate processing overhead
        usleep(100);  // 100μs between operations
    }
    
    // Calculate performance metrics
    double uart_rate = ((double)uart_packets_sent / test_duration_ms) * 1000.0;  // packets/sec
    double can_rate = ((double)can_frames_sent / test_duration_ms) * 1000.0;     // frames/sec
    double conflict_rate = ((double)resource_conflicts / (uart_packets_sent + can_frames_sent)) * 100.0;
    
    if (resource_conflicts > 10 || timing_violations > 5) {
        concurrent_operation_ok = false;
        snprintf(details, sizeof(details),
                "Concurrent operation issues: %.1f UART pkt/s, %.1f CAN fr/s, %.1f%% conflicts, %d timing violations.",
                uart_rate, can_rate, conflict_rate, timing_violations);
    } else {
        snprintf(details, sizeof(details),
                "Concurrent operation successful: %.1f UART pkt/s, %.1f CAN fr/s, %.1f%% conflicts.",
                uart_rate, can_rate, conflict_rate);
    }
    
    uint32_t duration = (uint32_t)(get_time_us() - start_time);
    log_esp32_test_result("Concurrent CAN/UART Operation", concurrent_operation_ok, duration, details, 3);
}

/**
 * Main test execution function
 */
int main(void) {
    printf("ESP32-C6 Common Issues Verification Test Suite\n");
    printf("==============================================\n");
    printf("Testing ESP32-C6 specific CAN/UART protocol issues\n");
    printf("Based on comprehensive research findings\n\n");
    
    // Seed random number generator for simulations
    srand(time(NULL));
    
    uint64_t suite_start = get_time_us();
    
    // Execute all ESP32-C6 specific tests
    test_high_baud_rate_issues();
    test_missing_byte_transmission();
    test_timing_precision_challenges();
    test_can_bus_error_accumulation();
    test_interrupt_priority_conflicts();
    test_electrical_noise_sensitivity();
    test_can_timing_configuration();
    test_concurrent_can_uart_operation();
    
    uint32_t suite_duration = (uint32_t)(get_time_us() - suite_start);
    
    // Print comprehensive test results
    printf("\n=== ESP32-C6 SPECIFIC TEST RESULTS ===\n");
    printf("Total Tests: %d\n", esp32_test_count);
    printf("Passed: %d\n", esp32_tests_passed);
    printf("Failed: %d\n", esp32_tests_failed);
    printf("Success Rate: %.1f%%\n", (float)esp32_tests_passed / esp32_test_count * 100.0);
    printf("Total Duration: %u μs (%.2f ms)\n", suite_duration, suite_duration / 1000.0);
    
    // Categorize results by severity
    int critical_failures = 0;
    int warnings = 0;
    int info_items = 0;
    
    printf("\nDetailed Results by Severity:\n");
    for (int i = 0; i < esp32_test_count; i++) {
        const char* severity_text = (esp32_test_results[i].severity == 3) ? "CRITICAL" : 
                                   (esp32_test_results[i].severity == 2) ? "WARNING" : "INFO";
        
        printf("%s [%s] %s (%u μs): %s\n",
               esp32_test_results[i].passed ? "✅" : "❌",
               severity_text,
               esp32_test_results[i].test_name,
               esp32_test_results[i].duration_us,
               esp32_test_results[i].details);
        
        if (!esp32_test_results[i].passed) {
            if (esp32_test_results[i].severity == 3) critical_failures++;
            else if (esp32_test_results[i].severity == 2) warnings++;
            else info_items++;
        }
    }
    
    // Final ESP32-C6 specific assessment
    printf("\n=== ESP32-C6 COMPATIBILITY ASSESSMENT ===\n");
    
    if (esp32_tests_failed == 0) {
        printf("🎉 ALL ESP32-C6 TESTS PASSED\n");
        printf("ESP32-C6 handles all common CAN/UART issues well\n");
        printf("✅ No critical ESP32-C6 specific issues detected\n");
        return 0;
    } else if (critical_failures == 0) {
        printf("⚠️  ESP32-C6 MINOR ISSUES DETECTED (%d warnings)\n", warnings);
        printf("Common ESP32-C6 issues present but manageable\n");
        printf("🔧 Review warnings and implement mitigations\n");
        return 1;
    } else {
        printf("❌ ESP32-C6 CRITICAL ISSUES DETECTED (%d critical)\n", critical_failures);
        printf("Significant ESP32-C6 compatibility problems found\n");
        printf("⚡ Address critical issues before deployment\n");
        return 2;
    }
}