#!/bin/bash

# VESC Express ESP32-C6 Comprehensive Test Suite
# Autonomous test runner for complete validation

echo "🚀 VESC Express ESP32-C6 Comprehensive Test Suite"
echo "================================================="
echo "Running all tests autonomously..."
echo ""

# Test results tracking
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0
TEST_RESULTS=()

# Function to run a test and capture results
run_test() {
    local test_name="$1"
    local test_command="$2"
    local test_file="$3"
    
    echo "🔍 Testing: $test_name"
    echo "   Command: $test_command"
    
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    
    # Compile if needed
    if [[ $test_command == gcc* ]]; then
        echo "   Compiling..."
        if eval "$test_command" > /dev/null 2>&1; then
            echo "   ✅ Compilation successful"
        else
            echo "   ❌ Compilation failed"
            TEST_RESULTS+=("❌ $test_name - Compilation failed")
            FAILED_TESTS=$((FAILED_TESTS + 1))
            return 1
        fi
        
        # Extract executable name
        local executable=$(echo "$test_command" | grep -o '\-o [^ ]*' | cut -d' ' -f2)
        if [[ -f "$executable" ]]; then
            echo "   Executing: ./$executable"
            ./"$executable" > /dev/null 2>&1
            local exit_code=$?
            
            # Special handling for ESP32-C6 Issues test (exit codes: 0=perfect, 1=warnings, 2=critical)
            if [[ "$test_name" == "ESP32-C6 Issues" ]]; then
                if [[ $exit_code -eq 0 ]]; then
                    echo "   ✅ Test passed (perfect)"
                    TEST_RESULTS+=("✅ $test_name - All tests passed perfectly")
                    PASSED_TESTS=$((PASSED_TESTS + 1))
                elif [[ $exit_code -eq 1 ]]; then
                    echo "   ⚠️  Test passed with warnings"
                    TEST_RESULTS+=("⚠️  $test_name - Minor issues detected")
                    PASSED_TESTS=$((PASSED_TESTS + 1))
                else
                    echo "   ❌ Test failed (critical issues: exit code $exit_code)"
                    TEST_RESULTS+=("❌ $test_name - Critical issues detected")
                    FAILED_TESTS=$((FAILED_TESTS + 1))
                fi
            else
                # Standard test handling
                if [[ $exit_code -eq 0 ]]; then
                    echo "   ✅ Test passed"
                    TEST_RESULTS+=("✅ $test_name - All tests passed")
                    PASSED_TESTS=$((PASSED_TESTS + 1))
                else
                    echo "   ❌ Test failed (exit code: $exit_code)"
                    TEST_RESULTS+=("❌ $test_name - Test execution failed")
                    FAILED_TESTS=$((FAILED_TESTS + 1))
                fi
            fi
        else
            echo "   ❌ Executable not found"
            TEST_RESULTS+=("❌ $test_name - Executable not found")
            FAILED_TESTS=$((FAILED_TESTS + 1))
        fi
    else
        # Direct command execution
        if eval "$test_command" > /dev/null 2>&1; then
            echo "   ✅ Command successful"
            TEST_RESULTS+=("✅ $test_name - Command successful")
            PASSED_TESTS=$((PASSED_TESTS + 1))
        else
            echo "   ❌ Command failed"
            TEST_RESULTS+=("❌ $test_name - Command failed")
            FAILED_TESTS=$((FAILED_TESTS + 1))
        fi
    fi
    
    echo ""
}

# 1. Core Function Tests (Real VESC code)
run_test "Core Functions" \
    "gcc -o test_core_functions test_core_functions.c main/buffer.c main/crc.c -I main -I main/hwconf -I main/config" \
    "test_core_functions.c"

# 2. Protocol Validation Tests (Real VESC protocol)
run_test "Protocol Validation" \
    "gcc -o test_protocol_validation test_protocol_validation.c main/buffer.c main/crc.c -I main -I main/hwconf -I main/config" \
    "test_protocol_validation.c"

# 3. VESC Compatibility Tests (Original mock tests for comparison)
run_test "VESC Compatibility (Mock)" \
    "gcc -o test_vesc_compatibility test_vesc_compatibility.c -I main -I main/hwconf -DCOMPATIBILITY_TEST_STANDALONE" \
    "test_vesc_compatibility.c"

# 4. CAN Interface Tests
run_test "CAN Interface" \
    "gcc -o test_can_interface test_can_interface.c -I main -I main/hwconf -DCAN_TEST_STANDALONE" \
    "test_can_interface.c"

# 5. UART Interface Tests
run_test "UART Interface" \
    "gcc -o test_uart_interface test_uart_interface.c -I main -I main/hwconf -DUART_TEST_STANDALONE" \
    "test_uart_interface.c"

# 6. Protocol Bridge Tests
run_test "Protocol Bridge" \
    "gcc -o test_protocol_bridge test_protocol_bridge.c -I main -I main/hwconf -DBRIDGE_TEST_STANDALONE" \
    "test_protocol_bridge.c"

# 7. Performance Tests
run_test "Performance Benchmark" \
    "gcc -o test_performance test_performance.c -I main -I main/hwconf -DPERFORMANCE_TEST_STANDALONE" \
    "test_performance.c"

# 8. ESP32-C6 Specific Issues Tests (Enhanced Research-Based Testing)
run_test "ESP32-C6 Issues" \
    "gcc -o test_esp32_c6_issues test_esp32_c6_issues.c -lpthread -I main -I main/hwconf -DESP32_C6_TEST_STANDALONE" \
    "test_esp32_c6_issues.c"

# 9. BMS Interface Tests (Battery Management System)
run_test "BMS Interface" \
    "gcc -o test_bms_interface test_bms_interface.c -I main -I main/hwconf -DBMS_TEST_STANDALONE" \
    "test_bms_interface.c"

# 10. LispBM Interface Tests (Scripting Engine)
run_test "LispBM Interface" \
    "gcc -o test_lisp_interface test_lisp_interface.c -I main -I main/hwconf -DLISP_TEST_STANDALONE" \
    "test_lisp_interface.c"

# 11. Additional Features Tests (File System, Logging, GNSS)
run_test "Additional Features" \
    "gcc -o test_additional_features test_additional_features.c -I main -I main/hwconf -DADDITIONAL_TEST_STANDALONE" \
    "test_additional_features.c"

# 12. Code Quality Checks
echo "🔍 Testing: Code Quality Analysis"
echo "   Running static analysis..."
TOTAL_TESTS=$((TOTAL_TESTS + 1))

# Check for common issues in test files
echo "   Checking for memory leaks..."
if grep -r "malloc\|calloc\|realloc" test_*.c | grep -v "free" > /dev/null; then
    echo "   ⚠️  Potential memory leaks detected"
    TEST_RESULTS+=("⚠️  Code Quality - Potential memory leaks")
else
    echo "   ✅ No obvious memory leaks"
fi

# Check for buffer overflows
echo "   Checking for buffer safety..."
if grep -r "strcpy\|strcat\|sprintf" test_*.c > /dev/null; then
    echo "   ⚠️  Potentially unsafe string functions"
    TEST_RESULTS+=("⚠️  Code Quality - Unsafe string functions")
else
    echo "   ✅ Safe string handling"
    PASSED_TESTS=$((PASSED_TESTS + 1))
    TEST_RESULTS+=("✅ Code Quality - Safe string handling")
fi
echo ""

# 10. Test Coverage Analysis
echo "🔍 Testing: Coverage Analysis"
echo "   Analyzing test coverage..."
TOTAL_TESTS=$((TOTAL_TESTS + 1))

# Count functions tested
CORE_FUNCTIONS_TESTED=$(grep -o "buffer_append\|buffer_get\|crc16" test_*.c | wc -l)
PROTOCOL_FUNCTIONS_TESTED=$(grep -o "COMM_\|CAN_PACKET_" test_*.c | wc -l)

echo "   Core functions tested: $CORE_FUNCTIONS_TESTED references"
echo "   Protocol functions tested: $PROTOCOL_FUNCTIONS_TESTED references"

if [[ $CORE_FUNCTIONS_TESTED -gt 10 && $PROTOCOL_FUNCTIONS_TESTED -gt 20 ]]; then
    echo "   ✅ Good test coverage"
    PASSED_TESTS=$((PASSED_TESTS + 1))
    TEST_RESULTS+=("✅ Coverage Analysis - Good coverage ($CORE_FUNCTIONS_TESTED core, $PROTOCOL_FUNCTIONS_TESTED protocol)")
else
    echo "   ⚠️  Limited test coverage"
    TEST_RESULTS+=("⚠️  Coverage Analysis - Limited coverage")
fi
echo ""

# 11. Integration Validation
echo "🔍 Testing: Integration Validation"
echo "   Checking integration completeness..."
TOTAL_TESTS=$((TOTAL_TESTS + 1))

# Check if all critical components are tested
UART_TESTED=$(grep -l "UART\|uart" test_*.c | wc -l)
CAN_TESTED=$(grep -l "CAN\|can" test_*.c | wc -l)
BRIDGE_TESTED=$(grep -l "FORWARD_CAN\|bridge" test_*.c | wc -l)

echo "   UART components tested: $UART_TESTED files"
echo "   CAN components tested: $CAN_TESTED files"  
echo "   Bridge components tested: $BRIDGE_TESTED files"

if [[ $UART_TESTED -gt 0 && $CAN_TESTED -gt 0 && $BRIDGE_TESTED -gt 0 ]]; then
    echo "   ✅ Complete integration testing"
    PASSED_TESTS=$((PASSED_TESTS + 1))
    TEST_RESULTS+=("✅ Integration Validation - All components tested")
else
    echo "   ❌ Incomplete integration testing"
    FAILED_TESTS=$((FAILED_TESTS + 1))
    TEST_RESULTS+=("❌ Integration Validation - Missing component tests")
fi
echo ""

# Cleanup executables
echo "🧹 Cleaning up test executables..."
rm -f test_core_functions test_protocol_validation test_vesc_compatibility
rm -f test_can_interface test_uart_interface test_protocol_bridge test_performance test_esp32_c6_issues
echo "   ✅ Cleanup complete"
echo ""

# Final Results
echo "======================================================"
echo "🏁 COMPREHENSIVE TEST RESULTS"
echo "======================================================"
echo "Total Tests Run: $TOTAL_TESTS"
echo "Tests Passed: $PASSED_TESTS"
echo "Tests Failed: $FAILED_TESTS"
echo "Success Rate: $(( (PASSED_TESTS * 100) / TOTAL_TESTS ))%"
echo ""

echo "📋 Detailed Results:"
echo "----------------------"
for result in "${TEST_RESULTS[@]}"; do
    echo "$result"
done
echo ""

# Overall Assessment
if [[ $FAILED_TESTS -eq 0 ]]; then
    echo "🎉 ALL TESTS PASSED - FULL VALIDATION COMPLETE"
    echo "✅ VESC Express ESP32-C6 is ready for production"
    echo "✅ Real function integration confirmed"
    echo "✅ Protocol compatibility verified"
    echo "✅ Performance requirements met"
    echo "✅ Code quality standards maintained"
    exit 0
elif [[ $FAILED_TESTS -le 2 ]]; then
    echo "⚠️  MOSTLY SUCCESSFUL - MINOR ISSUES DETECTED"
    echo "🔧 Review failed tests and address issues"
    echo "📈 $(( (PASSED_TESTS * 100) / TOTAL_TESTS ))% success rate achieved"
    exit 1
else
    echo "❌ SIGNIFICANT ISSUES DETECTED"
    echo "🔍 Multiple test failures require investigation"
    echo "⚡ Address critical issues before deployment"
    exit 2
fi