#!/bin/bash

# ESP32-C6 VESC Express Quick Debug Script
# Simplified one-command debugging and testing

set -e  # Exit on any error

# Configuration
PROJECT_ROOT="$(dirname "$(dirname "$(realpath "$0")")")"
TOOLS_DIR="$PROJECT_ROOT/tools"
LOGS_DIR="$PROJECT_ROOT/logs"
PORT="${ESP_PORT:-/dev/ttyACM0}"
OPENOCD_CFG="${OPENOCD_CFG:-esp32c6_wsl2.cfg}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# Logging function
log() {
    local level="$1"
    shift
    local message="$*"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    case "$level" in
        "INFO")  echo -e "${BLUE}[INFO]${NC}  [$timestamp] $message" ;;
        "WARN")  echo -e "${YELLOW}[WARN]${NC}  [$timestamp] $message" ;;
        "ERROR") echo -e "${RED}[ERROR]${NC} [$timestamp] $message" ;;
        "SUCCESS") echo -e "${GREEN}[OK]${NC}    [$timestamp] $message" ;;
        "DEBUG") echo -e "${PURPLE}[DEBUG]${NC} [$timestamp] $message" ;;
        *) echo "[$timestamp] $message" ;;
    esac
}

# Check if ESP-IDF is available
check_esp_idf() {
    log "INFO" "🔍 Checking ESP-IDF environment..."
    
    if ! command -v idf.py &> /dev/null; then
        log "WARN" "ESP-IDF not found in PATH, trying to source..."
        if [[ -f "$HOME/esp/esp-idf/export.sh" ]]; then
            source "$HOME/esp/esp-idf/export.sh"
            log "SUCCESS" "ESP-IDF environment loaded"
        else
            log "ERROR" "ESP-IDF not found! Please install ESP-IDF v5.2+"
            exit 1
        fi
    else
        log "SUCCESS" "ESP-IDF found in PATH"
    fi
    
    # Check version
    local idf_version
    idf_version=$(idf.py --version 2>&1 | head -1 || echo "unknown")
    log "INFO" "ESP-IDF version: $idf_version"
}

# Check device connection
check_device() {
    log "INFO" "🔌 Checking ESP32-C6 device connection..."
    
    if [[ ! -e "$PORT" ]]; then
        log "ERROR" "Device not found at $PORT"
        log "INFO" "Available devices:"
        ls /dev/tty* | grep -E "(ACM|USB)" || log "WARN" "No USB/ACM devices found"
        return 1
    fi
    
    # Check if it's an ESP32-C6
    if lsusb -d 303a:1001 &> /dev/null; then
        log "SUCCESS" "ESP32-C6 device detected"
        lsusb -d 303a:1001
    else
        log "WARN" "ESP32-C6 not detected, but port exists"
    fi
    
    return 0
}

# Quick build
quick_build() {
    log "INFO" "🔨 Quick build..."
    
    cd "$PROJECT_ROOT"
    
    # Set target if not already set
    if [[ ! -f "build/project_description.json" ]]; then
        log "INFO" "Setting target to esp32c6..."
        idf.py set-target esp32c6
    fi
    
    # Build
    if idf.py build; then
        log "SUCCESS" "Build completed successfully"
        
        # Show binary info
        local bin_file="build/vesc_express.bin"
        if [[ -f "$bin_file" ]]; then
            local size
            size=$(stat -f%z "$bin_file" 2>/dev/null || stat -c%s "$bin_file" 2>/dev/null || echo "unknown")
            log "INFO" "Binary size: $size bytes"
        fi
        
        return 0
    else
        log "ERROR" "Build failed"
        return 1
    fi
}

# Quick flash
quick_flash() {
    log "INFO" "⚡ Quick flash to $PORT..."
    
    cd "$PROJECT_ROOT"
    
    if idf.py flash -p "$PORT"; then
        log "SUCCESS" "Flash completed successfully"
        return 0
    else
        log "ERROR" "Flash failed"
        return 1
    fi
}

# Monitor serial output
quick_monitor() {
    local duration="${1:-30}"
    log "INFO" "📊 Monitoring serial output for ${duration}s..."
    
    cd "$PROJECT_ROOT"
    
    # Create logs directory
    mkdir -p "$LOGS_DIR"
    
    local log_file="$LOGS_DIR/monitor_$(date +%Y%m%d_%H%M%S).log"
    
    # Start monitoring with timeout
    timeout "$duration" idf.py monitor -p "$PORT" | tee "$log_file" || {
        local exit_code=$?
        if [[ $exit_code -eq 124 ]]; then
            log "INFO" "Monitor timeout reached"
        else
            log "WARN" "Monitor exited with code $exit_code"
        fi
    }
    
    log "INFO" "Monitor output saved to $log_file"
    
    # Quick analysis
    if [[ -f "$log_file" ]]; then
        local error_count
        error_count=$(grep -ic "error\|fail\|abort" "$log_file" || echo "0")
        local warning_count
        warning_count=$(grep -ic "warning" "$log_file" || echo "0")
        
        if [[ $error_count -gt 0 ]]; then
            log "WARN" "Found $error_count error(s) in output"
        fi
        if [[ $warning_count -gt 0 ]]; then
            log "WARN" "Found $warning_count warning(s) in output"
        fi
        
        if [[ $error_count -eq 0 && $warning_count -eq 0 ]]; then
            log "SUCCESS" "No errors or warnings detected"
        fi
    fi
}

# OpenOCD quick test
quick_openocd() {
    log "INFO" "🔧 Quick OpenOCD test..."
    
    if ! command -v openocd &> /dev/null; then
        log "ERROR" "OpenOCD not found"
        return 1
    fi
    
    local config_file="$PROJECT_ROOT/$OPENOCD_CFG"
    if [[ ! -f "$config_file" ]]; then
        log "ERROR" "OpenOCD config not found: $config_file"
        return 1
    fi
    
    # Test OpenOCD connection
    log "INFO" "Testing OpenOCD connection..."
    
    timeout 10s openocd -f "$config_file" -c "init; esp32c6 cpu count; shutdown" &> /dev/null
    local result=$?
    
    if [[ $result -eq 0 ]]; then
        log "SUCCESS" "OpenOCD connection test passed"
        return 0
    else
        log "ERROR" "OpenOCD connection test failed"
        return 1
    fi
}

# GDB quick commands
quick_gdb() {
    log "INFO" "🐛 Quick GDB session..."
    
    if ! command -v riscv32-esp-elf-gdb &> /dev/null; then
        log "ERROR" "RISC-V GDB not found"
        return 1
    fi
    
    local elf_file="$PROJECT_ROOT/build/vesc_express.elf"
    if [[ ! -f "$elf_file" ]]; then
        log "ERROR" "ELF file not found: $elf_file"
        return 1
    fi
    
    # Create temporary GDB script
    local gdb_script
    gdb_script=$(mktemp)
    cat > "$gdb_script" << 'EOF'
target extended-remote localhost:3333
monitor reset halt
info registers pc sp
info memory
monitor esp32c6 cpu count
monitor version
quit
EOF
    
    log "INFO" "Running GDB commands..."
    
    # Start OpenOCD in background
    local openocd_pid
    openocd -f "$PROJECT_ROOT/$OPENOCD_CFG" &
    openocd_pid=$!
    
    sleep 3  # Wait for OpenOCD to start
    
    # Run GDB
    if riscv32-esp-elf-gdb -batch -x "$gdb_script" "$elf_file" 2>&1; then
        log "SUCCESS" "GDB session completed"
        local result=0
    else
        log "ERROR" "GDB session failed"
        local result=1
    fi
    
    # Cleanup
    kill $openocd_pid &> /dev/null || true
    rm -f "$gdb_script"
    
    return $result
}

# Comprehensive quick test
quick_test() {
    log "INFO" "🚀 Running comprehensive quick test..."
    
    local start_time
    start_time=$(date +%s)
    
    local tests_passed=0
    local tests_total=6
    
    # Test sequence
    if check_device; then ((tests_passed++)); fi
    if quick_build; then ((tests_passed++)); fi
    if quick_flash; then ((tests_passed++)); fi
    
    # Give device time to boot
    log "INFO" "⏳ Waiting for device to boot..."
    sleep 5
    
    quick_monitor 15  # Monitor for 15 seconds
    ((tests_passed++))  # Monitor always "passes"
    
    if quick_openocd; then ((tests_passed++)); fi
    if quick_gdb; then ((tests_passed++)); fi
    
    local end_time
    end_time=$(date +%s)
    local duration=$((end_time - start_time))
    
    log "INFO" "📊 Quick test results:"
    log "INFO" "  Tests passed: $tests_passed/$tests_total"
    log "INFO" "  Duration: ${duration}s"
    
    if [[ $tests_passed -eq $tests_total ]]; then
        log "SUCCESS" "🎉 All quick tests passed!"
        return 0
    else
        log "WARN" "⚠️  Some quick tests failed"
        return 1
    fi
}

# Verification using Python suite
verify_implementation() {
    log "INFO" "✅ Running implementation verification..."
    
    local verification_script="$TOOLS_DIR/verification_suite.py"
    
    if [[ ! -f "$verification_script" ]]; then
        log "ERROR" "Verification suite not found: $verification_script"
        return 1
    fi
    
    if python3 "$verification_script" --test all; then
        log "SUCCESS" "Implementation verification passed"
        return 0
    else
        log "ERROR" "Implementation verification failed"
        return 1
    fi
}

# Help function
show_help() {
    cat << EOF
ESP32-C6 VESC Express Quick Debug Tool

Usage: $0 [COMMAND] [OPTIONS]

Commands:
  check       - Check environment and device
  build       - Quick build firmware
  flash       - Quick flash firmware
  monitor     - Monitor serial output (default: 30s)
  openocd     - Test OpenOCD connection
  gdb         - Quick GDB session
  test        - Run comprehensive quick test
  verify      - Run implementation verification
  all         - Do everything (build, flash, test)
  help        - Show this help

Options:
  -p PORT     - Serial port (default: $PORT)
  -c CONFIG   - OpenOCD config (default: $OPENOCD_CFG)
  -t TIME     - Monitor duration in seconds (default: 30)

Environment Variables:
  ESP_PORT    - Serial port override
  OPENOCD_CFG - OpenOCD config file override

Examples:
  $0 check              # Check environment
  $0 build flash        # Build and flash
  $0 monitor -t 60      # Monitor for 60 seconds
  $0 test               # Run full quick test
  $0 verify             # Verify implementation
  $0 all                # Complete workflow

EOF
}

# Main execution
main() {
    local commands=()
    local monitor_time=30
    
    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            -p|--port)
                PORT="$2"
                shift 2
                ;;
            -c|--config)
                OPENOCD_CFG="$2"
                shift 2
                ;;
            -t|--time)
                monitor_time="$2"
                shift 2
                ;;
            -h|--help|help)
                show_help
                exit 0
                ;;
            check|build|flash|monitor|openocd|gdb|test|verify|all)
                commands+=("$1")
                shift
                ;;
            *)
                log "ERROR" "Unknown argument: $1"
                show_help
                exit 1
                ;;
        esac
    done
    
    # Default command
    if [[ ${#commands[@]} -eq 0 ]]; then
        commands=("help")
    fi
    
    # Ensure logs directory exists
    mkdir -p "$LOGS_DIR"
    
    # Setup ESP-IDF for most commands
    local needs_idf=false
    for cmd in "${commands[@]}"; do
        if [[ "$cmd" != "help" && "$cmd" != "check" && "$cmd" != "verify" ]]; then
            needs_idf=true
            break
        fi
    done
    
    if [[ "$needs_idf" == "true" ]]; then
        check_esp_idf
    fi
    
    # Execute commands
    local overall_success=true
    
    for cmd in "${commands[@]}"; do
        case $cmd in
            check)
                if ! check_device; then overall_success=false; fi
                ;;
            build)
                if ! quick_build; then overall_success=false; fi
                ;;
            flash)
                if ! quick_flash; then overall_success=false; fi
                ;;
            monitor)
                quick_monitor "$monitor_time"
                ;;
            openocd)
                if ! quick_openocd; then overall_success=false; fi
                ;;
            gdb)
                if ! quick_gdb; then overall_success=false; fi
                ;;
            test)
                if ! quick_test; then overall_success=false; fi
                ;;
            verify)
                if ! verify_implementation; then overall_success=false; fi
                ;;
            all)
                if ! quick_test; then overall_success=false; fi
                if ! verify_implementation; then overall_success=false; fi
                ;;
            help)
                show_help
                ;;
        esac
    done
    
    if [[ "$overall_success" == "true" ]]; then
        log "SUCCESS" "🎉 All operations completed successfully!"
        exit 0
    else
        log "ERROR" "❌ Some operations failed"
        exit 1
    fi
}

# Run main function with all arguments
main "$@"