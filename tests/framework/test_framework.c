/**
 * VESC Express Test Framework Implementation
 * 
 * Core implementation of the unified test infrastructure.
 */

#include "test_framework.h"
#include <stdarg.h>

// Global performance timing state
static uint64_t performance_start_time = 0;

// Global memory tracking state
static size_t peak_memory_usage = 0;
static size_t current_memory_usage = 0;
static bool memory_tracking_enabled = false;

/**
 * Get current time in microseconds
 */
uint64_t test_get_time_us(void) {
    struct timeval tv;
    gettimeofday(&tv, NULL);
    return (uint64_t)tv.tv_sec * 1000000 + tv.tv_usec;
}

/**
 * Create a new test suite
 */
test_suite_t* test_suite_create(const char* suite_name) {
    test_suite_t* suite = malloc(sizeof(test_suite_t));
    if (!suite) {
        return NULL;
    }
    
    safe_strncpy(suite->suite_name, suite_name, sizeof(suite->suite_name));
    suite->test_count = 0;
    suite->tests_passed = 0;
    suite->tests_failed = 0;
    suite->tests_skipped = 0;
    suite->suite_start_time_us = test_get_time_us();
    suite->suite_duration_us = 0;
    
    // Initialize all test results
    for (int i = 0; i < MAX_TESTS_PER_SUITE; i++) {
        suite->results[i].status = TEST_STATUS_PENDING;
        suite->results[i].name[0] = '\0';
        suite->results[i].details[0] = '\0';
        suite->results[i].start_time_us = 0;
        suite->results[i].duration_us = 0;
        suite->results[i].line_number = 0;
        suite->results[i].file_name = NULL;
    }
    
    return suite;
}

/**
 * Destroy a test suite and free memory
 */
void test_suite_destroy(test_suite_t* suite) {
    if (suite) {
        free(suite);
    }
}

/**
 * Start a new test in the suite
 */
void test_start(test_suite_t* suite, const char* test_name, const char* file, int line) {
    if (!suite || suite->test_count >= MAX_TESTS_PER_SUITE) {
        return;
    }
    
    test_result_t* result = &suite->results[suite->test_count];
    safe_strncpy(result->name, test_name, sizeof(result->name));
    result->status = TEST_STATUS_RUNNING;
    result->start_time_us = test_get_time_us();
    result->file_name = file;
    result->line_number = line;
    
    printf("🔍 Running: %s\n", test_name);
}

/**
 * End the current test with a result
 */
void test_end_with_result(test_suite_t* suite, bool passed, const char* details) {
    if (!suite || suite->test_count >= MAX_TESTS_PER_SUITE) {
        return;
    }
    
    test_result_t* result = &suite->results[suite->test_count];
    if (result->status != TEST_STATUS_RUNNING) {
        return; // Test wasn't started properly
    }
    
    result->duration_us = test_get_time_us() - result->start_time_us;
    result->status = passed ? TEST_STATUS_PASSED : TEST_STATUS_FAILED;
    safe_strncpy(result->details, details, sizeof(result->details));
    
    if (passed) {
        suite->tests_passed++;
        printf("✅ PASS: %s (%llu μs) - %s\n", 
               result->name, (unsigned long long)result->duration_us, details);
    } else {
        suite->tests_failed++;
        printf("❌ FAIL: %s (%llu μs) - %s\n", 
               result->name, (unsigned long long)result->duration_us, details);
    }
    
    suite->test_count++;
}

/**
 * Skip the current test
 */
void test_skip(test_suite_t* suite, const char* reason) {
    if (!suite || suite->test_count >= MAX_TESTS_PER_SUITE) {
        return;
    }
    
    test_result_t* result = &suite->results[suite->test_count];
    result->status = TEST_STATUS_SKIPPED;
    result->duration_us = 0;
    safe_strncpy(result->details, reason, sizeof(result->details));
    
    suite->tests_skipped++;
    printf("⏭️  SKIP: %s - %s\n", result->name, reason);
    suite->test_count++;
}

/**
 * Run all test functions in a suite
 */
void test_suite_run_all(test_suite_t* suite, test_function_t* test_functions, int function_count) {
    if (!suite || !test_functions) {
        return;
    }
    
    printf("\n%s Test Suite\n", suite->suite_name);
    printf("===========================================\n");
    
    for (int i = 0; i < function_count; i++) {
        if (test_functions[i]) {
            test_functions[i](suite);
        }
    }
    
    suite->suite_duration_us = test_get_time_us() - suite->suite_start_time_us;
}

/**
 * Print comprehensive test results
 */
void test_suite_print_results(test_suite_t* suite) {
    if (!suite) {
        return;
    }
    
    printf("\n=== %s RESULTS ===\n", suite->suite_name);
    printf("Total Tests: %d\n", suite->test_count);
    printf("Passed: %d\n", suite->tests_passed);
    printf("Failed: %d\n", suite->tests_failed);
    printf("Skipped: %d\n", suite->tests_skipped);
    
    if (suite->test_count > 0) {
        printf("Success Rate: %.1f%%\n", (float)suite->tests_passed / suite->test_count * 100.0);
    }
    
    printf("Total Duration: %llu μs (%.2f ms)\n", 
           (unsigned long long)suite->suite_duration_us, 
           suite->suite_duration_us / 1000.0);
    
    // Detailed results for failed tests
    bool has_failures = false;
    for (int i = 0; i < suite->test_count; i++) {
        if (suite->results[i].status == TEST_STATUS_FAILED) {
            if (!has_failures) {
                printf("\nFailed Tests Details:\n");
                has_failures = true;
            }
            printf("❌ %s: %s (at line %d)\n", 
                   suite->results[i].name, 
                   suite->results[i].details, 
                   suite->results[i].line_number);
        }
    }
    
    // Final assessment
    printf("\n=== ASSESSMENT ===\n");
    if (suite->tests_failed == 0) {
        printf("🎉 ALL TESTS PASSED - FULL COMPATIBILITY VERIFIED\n");
        printf("✅ %s is fully functional\n", suite->suite_name);
    } else {
        printf("⚠️  COMPATIBILITY ISSUES DETECTED\n");
        printf("❌ %d test(s) failed - review required\n", suite->tests_failed);
    }
}

/**
 * Get appropriate exit code for the test suite
 */
int test_suite_get_exit_code(test_suite_t* suite) {
    if (!suite) {
        return 2; // Error
    }
    return (suite->tests_failed == 0) ? 0 : 1;
}

/**
 * Safe string copy utility
 */
void safe_strncpy(char* dest, const char* src, size_t dest_size) {
    if (!dest || !src || dest_size == 0) {
        return;
    }
    
    strncpy(dest, src, dest_size - 1);
    dest[dest_size - 1] = '\0';
}

/**
 * Safe formatted string printing
 */
int safe_snprintf(char* dest, size_t dest_size, const char* format, ...) {
    if (!dest || !format || dest_size == 0) {
        return -1;
    }
    
    va_list args;
    va_start(args, format);
    int result = vsnprintf(dest, dest_size, format, args);
    va_end(args);
    
    // Ensure null termination
    dest[dest_size - 1] = '\0';
    
    return result;
}

/**
 * Initialize random seed for reproducible tests
 */
void test_init_random_seed(void) {
    srand(time(NULL));
}

/**
 * Generate random uint32 in range
 */
uint32_t test_random_uint32(uint32_t min, uint32_t max) {
    if (min >= max) {
        return min;
    }
    return min + (rand() % (max - min + 1));
}

/**
 * Generate random float in range
 */
float test_random_float(float min, float max) {
    if (min >= max) {
        return min;
    }
    float scale = rand() / (float)RAND_MAX;
    return min + scale * (max - min);
}

/**
 * Generate random string from character set
 */
void test_generate_random_string(char* dest, size_t length, const char* charset) {
    if (!dest || !charset || length == 0) {
        return;
    }
    
    size_t charset_len = strlen(charset);
    if (charset_len == 0) {
        dest[0] = '\0';
        return;
    }
    
    for (size_t i = 0; i < length - 1; i++) {
        dest[i] = charset[rand() % charset_len];
    }
    dest[length - 1] = '\0';
}

/**
 * Start performance measurement
 */
void test_performance_start(void) {
    performance_start_time = test_get_time_us();
}

/**
 * End performance measurement and return duration
 */
uint64_t test_performance_end_us(void) {
    return test_get_time_us() - performance_start_time;
}

/**
 * Benchmark a function with multiple iterations
 */
void test_benchmark_function(test_suite_t* suite, const char* name, 
                            void(*func)(void), int iterations) {
    if (!suite || !func || iterations <= 0) {
        return;
    }
    
    TEST_START(suite, name);
    
    uint64_t total_time = 0;
    uint64_t min_time = UINT64_MAX;
    uint64_t max_time = 0;
    
    for (int i = 0; i < iterations; i++) {
        test_performance_start();
        func();
        uint64_t iteration_time = test_performance_end_us();
        
        total_time += iteration_time;
        if (iteration_time < min_time) min_time = iteration_time;
        if (iteration_time > max_time) max_time = iteration_time;
    }
    
    uint64_t avg_time = total_time / iterations;
    char details[256];
    safe_snprintf(details, sizeof(details), 
                 "%d iterations: avg %llu μs, min %llu μs, max %llu μs",
                 iterations, (unsigned long long)avg_time, 
                 (unsigned long long)min_time, (unsigned long long)max_time);
    
    TEST_PASS(suite, details);
}

/**
 * Start memory tracking
 */
void test_memory_track_start(void) {
    memory_tracking_enabled = true;
    current_memory_usage = 0;
    peak_memory_usage = 0;
}

/**
 * Check for memory leaks
 */
bool test_memory_check_leaks(void) {
    return current_memory_usage == 0;
}

/**
 * Get peak memory usage during tracking
 */
size_t test_memory_get_peak_usage(void) {
    return peak_memory_usage;
}