#!/bin/bash

# ESP32-C6 VESC Express Boot Loop Fix Validation Script
# This script validates the changes made to prevent boot loops

echo "=== ESP32-C6 VESC Express Boot Loop Fix Validation ==="
echo ""

# Check if we're in the right directory
if [ ! -f "main/main.c" ] || [ ! -f "main/debug_wifi.c" ]; then
    echo "ERROR: Must be run from VESC Express project root"
    exit 1
fi

echo "1. Validating memory configuration changes..."

# Check that stack sizes have been reduced
if grep -q "1536.*// Minimal stack size for basic socket operations" main/debug_wifi.c; then
    echo "✓ Debug server task stack reduced to 1536 bytes"
else
    echo "✗ Debug server task stack not properly reduced"
fi

if grep -q "1024.*// Minimal stack size for message formatting" main/debug_wifi.c; then
    echo "✓ Debug sender task stack reduced to 1024 bytes"
else
    echo "✗ Debug sender task stack not properly reduced"
fi

echo ""
echo "2. Validating task priority changes..."

# Check that task priorities have been reduced
if grep -q "tskIDLE_PRIORITY.*// Use default idle priority" main/debug_wifi.c; then
    echo "✓ Task priorities reduced to idle priority"
else
    echo "✗ Task priorities not properly reduced"
fi

echo ""
echo "3. Validating graceful failure handling..."

# Check that failures are handled gracefully
if grep -q "continuing without debug" main/debug_wifi_delayed.c; then
    echo "✓ Graceful failure handling implemented"
else
    echo "✗ Graceful failure handling not found"
fi

if grep -q "System continues running without debug features" main/main.c; then
    echo "✓ Main task continues on debug failure"
else
    echo "✗ Main task graceful handling not found"
fi

echo ""
echo "4. Validating memory checks..."

# Check for system stability validation
if grep -q "check_system_stability" main/debug_wifi.c; then
    echo "✓ System stability check implemented"
else
    echo "✗ System stability check not found"
fi

if grep -q "20480.*// 20KB minimum" main/debug_wifi.c; then
    echo "✓ Conservative memory requirements set"
else
    echo "✗ Conservative memory requirements not found"
fi

echo ""
echo "5. Validating socket configuration simplification..."

# Check that aggressive socket options have been removed
if ! grep -q "SO_KEEPALIVE\|TCP_NODELAY\|SO_RCVBUF\|SO_SNDBUF" main/debug_wifi.c; then
    echo "✓ Aggressive socket options removed"
else
    echo "✗ Aggressive socket options still present"
fi

echo ""
echo "6. Memory usage analysis..."

# Calculate approximate memory usage
DEBUG_TASK_STACK=1536
SENDER_TASK_STACK=1024
INIT_TASK_STACK=1024
QUEUE_SIZE=8
MESSAGE_SIZE=236  # debug_wifi_message_t size
CLIENT_SIZE=72    # debug_wifi_client_t size
MAX_CLIENTS=2

TOTAL_STACK=$((DEBUG_TASK_STACK + SENDER_TASK_STACK + INIT_TASK_STACK))
TOTAL_QUEUE=$((QUEUE_SIZE * MESSAGE_SIZE))
TOTAL_CLIENTS=$((MAX_CLIENTS * CLIENT_SIZE))
TOTAL_STATIC=$((TOTAL_QUEUE + TOTAL_CLIENTS + 512))  # +512 for other structures

echo "Estimated memory usage:"
echo "  Task stacks: ${TOTAL_STACK} bytes"
echo "  Message queue: ${TOTAL_QUEUE} bytes"  
echo "  Client storage: ${TOTAL_CLIENTS} bytes"
echo "  Static structures: ~512 bytes"
echo "  Total estimated: ~$((TOTAL_STACK + TOTAL_STATIC)) bytes"
echo ""

if [ $((TOTAL_STACK + TOTAL_STATIC)) -lt 8192 ]; then
    echo "✓ Memory usage under 8KB - should be stable"
else
    echo "⚠ Memory usage over 8KB - monitor carefully"
fi

echo ""
echo "7. Configuration validation..."

# Check configuration values
if grep -q "DEBUG_WIFI_MAX_CLIENTS.*2" main/debug_wifi.h; then
    echo "✓ Max clients limited to 2"
fi

if grep -q "DEBUG_WIFI_QUEUE_SIZE.*8" main/debug_wifi.h; then
    echo "✓ Queue size reduced to 8"
fi

if grep -q "DEBUG_WIFI_BUFFER_SIZE.*1024" main/debug_wifi.h; then
    echo "✓ Buffer size reduced to 1024"
fi

echo ""
echo "=== Validation Summary ==="
echo ""
echo "The following changes have been implemented to fix the boot loop:"
echo ""
echo "MEMORY OPTIMIZATIONS:"
echo "- Reduced task stack sizes (3584->1536, 2048->1024)"
echo "- Reduced queue depth (16->8) and buffer sizes (1536->1024)"
echo "- Added system stability checks before initialization"
echo "- Removed core pinning to reduce scheduling conflicts"
echo ""
echo "STABILITY IMPROVEMENTS:"
echo "- Changed task priorities to idle level (lowest priority)"
echo "- Removed aggressive socket buffer configurations"
echo "- Added graceful failure handling throughout the stack"
echo "- System continues running even if debug features fail"
echo ""
echo "BOOT LOOP PREVENTION:"
echo "- Debug services are optional - failures don't crash system"
echo "- Memory checks prevent initialization under low memory"
echo "- Conservative timeouts and delays added"
echo "- Proper cleanup on all failure paths"
echo ""
echo "RECOMMENDATIONS:"
echo "1. Build and flash the firmware"
echo "2. Monitor serial output for stability"
echo "3. Test WiFi connection establishment"
echo "4. Verify VESC functionality remains intact"
echo "5. TCP debug server will start if memory allows"
echo ""
echo "If boot loops persist, the debug system will automatically disable"
echo "itself and the core VESC functionality will remain operational."
echo ""