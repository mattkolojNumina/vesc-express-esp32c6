/**
 * VESC Express Test Framework
 * 
 * Unified test infrastructure providing common utilities for all test suites.
 * Eliminates code duplication and provides consistent test patterns.
 */

#ifndef TEST_FRAMEWORK_H
#define TEST_FRAMEWORK_H

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <stdbool.h>
#include <time.h>
#include <sys/time.h>

// Framework version and metadata
#define TEST_FRAMEWORK_VERSION "1.0.0"
#define MAX_TEST_NAME_LENGTH 128
#define MAX_TEST_DETAILS_LENGTH 256
#define MAX_TESTS_PER_SUITE 50

// Test result status codes
typedef enum {
    TEST_STATUS_PENDING = 0,
    TEST_STATUS_RUNNING = 1,
    TEST_STATUS_PASSED = 2,
    TEST_STATUS_FAILED = 3,
    TEST_STATUS_SKIPPED = 4
} test_status_t;

// Test result structure
typedef struct {
    char name[MAX_TEST_NAME_LENGTH];
    test_status_t status;
    uint64_t start_time_us;
    uint64_t duration_us;
    char details[MAX_TEST_DETAILS_LENGTH];
    int line_number;
    const char* file_name;
} test_result_t;

// Test suite structure
typedef struct {
    char suite_name[MAX_TEST_NAME_LENGTH];
    test_result_t results[MAX_TESTS_PER_SUITE];
    int test_count;
    int tests_passed;
    int tests_failed;
    int tests_skipped;
    uint64_t suite_start_time_us;
    uint64_t suite_duration_us;
} test_suite_t;

// Test function pointer type
typedef void (*test_function_t)(test_suite_t* suite);

// Core framework functions
extern test_suite_t* test_suite_create(const char* suite_name);
extern void test_suite_destroy(test_suite_t* suite);
extern uint64_t test_get_time_us(void);
extern void test_start(test_suite_t* suite, const char* test_name, const char* file, int line);
extern void test_end_with_result(test_suite_t* suite, bool passed, const char* details);
extern void test_skip(test_suite_t* suite, const char* reason);
extern void test_suite_run_all(test_suite_t* suite, test_function_t* test_functions, int function_count);
extern void test_suite_print_results(test_suite_t* suite);
extern int test_suite_get_exit_code(test_suite_t* suite);

// Utility macros for easier test writing
#define TEST_START(suite, name) \
    test_start(suite, name, __FILE__, __LINE__)

#define TEST_PASS(suite, details) \
    test_end_with_result(suite, true, details)

#define TEST_FAIL(suite, details) \
    test_end_with_result(suite, false, details)

#define TEST_SKIP(suite, reason) \
    test_skip(suite, reason)

#define TEST_ASSERT(suite, condition, success_msg, fail_msg) \
    do { \
        if (condition) { \
            TEST_PASS(suite, success_msg); \
        } else { \
            TEST_FAIL(suite, fail_msg); \
        } \
    } while(0)

// Common test patterns
#define TEST_ASSERT_EQUAL_INT(suite, expected, actual, name) \
    TEST_ASSERT(suite, (expected) == (actual), \
                name " passed: values match", \
                name " failed: expected " #expected ", got " #actual)

#define TEST_ASSERT_EQUAL_STR(suite, expected, actual, name) \
    TEST_ASSERT(suite, strcmp(expected, actual) == 0, \
                name " passed: strings match", \
                name " failed: strings differ")

#define TEST_ASSERT_RANGE(suite, value, min, max, name) \
    TEST_ASSERT(suite, ((value) >= (min) && (value) <= (max)), \
                name " passed: value in range", \
                name " failed: value out of range")

// String safety utilities
extern void safe_strncpy(char* dest, const char* src, size_t dest_size);
extern int safe_snprintf(char* dest, size_t dest_size, const char* format, ...);

// Mock data generation utilities
extern void test_init_random_seed(void);
extern uint32_t test_random_uint32(uint32_t min, uint32_t max);
extern float test_random_float(float min, float max);
extern void test_generate_random_string(char* dest, size_t length, const char* charset);

// Performance measurement utilities
extern void test_performance_start(void);
extern uint64_t test_performance_end_us(void);
extern void test_benchmark_function(test_suite_t* suite, const char* name, 
                                   void(*func)(void), int iterations);

// Memory leak detection utilities
extern void test_memory_track_start(void);
extern bool test_memory_check_leaks(void);
extern size_t test_memory_get_peak_usage(void);

#endif // TEST_FRAMEWORK_H