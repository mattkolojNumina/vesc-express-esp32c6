# ESP32-C6 VESC Express Development Tools

Enhanced debugging and verification tools for simplified ESP32-C6 development workflow.

## 🛠️ Tool Suite Overview

### 1. Debug Helper (`debug_helper.py`)
**Comprehensive hardware debugging utility with intelligent automation**

```bash
# Run comprehensive hardware test
python3 tools/debug_helper.py --test

# Build and flash only
python3 tools/debug_helper.py --build --flash

# Monitor serial output for 60 seconds
python3 tools/debug_helper.py --monitor 60

# Check environment setup
python3 tools/debug_helper.py --check
```

**Features:**
- ✅ Automated environment validation (ESP-IDF, device, OpenOCD)
- ✅ Intelligent build system with error handling
- ✅ Flash verification with hash checking
- ✅ Serial output capture and parsing
- ✅ OpenOCD hardware debugging integration
- ✅ GDB command execution automation
- ✅ Boot sequence analysis with service detection
- ✅ Comprehensive test reporting with JSON output

### 2. Verification Suite (`verification_suite.py`)
**Implementation correctness verification with scoring system**

```bash
# Run complete verification
python3 tools/verification_suite.py --test all

# Verify specific components
python3 tools/verification_suite.py --test android
python3 tools/verification_suite.py --test esp32c6
python3 tools/verification_suite.py --test comm
```

**Verification Categories:**
- 🏗️ **Build System**: CMakeLists.txt dependencies and ESP-IDF integration
- 🔧 **ESP32-C6 Features**: Hardware abstraction and enhancement files
- 📱 **Android Compatibility**: Optimization modes and compatibility layers
- 📡 **Communication Stack**: WiFi, BLE, CAN, UART protocol implementation
- 🧠 **LispBM Integration**: Embedded scripting and VESC extensions
- 🔒 **Security Implementation**: WPA3, secure boot, encryption features
- 💾 **Memory Optimization**: Flash usage and memory layout analysis
- 📚 **Documentation**: Completeness and quality assessment

**Scoring System:**
- **Perfect (5/5)**: All critical tests passed with optimizations
- **Good (4/5)**: Most tests passed with minor issues
- **Acceptable (3/5)**: Core functionality present with warnings
- **Issues (2/5)**: Significant problems requiring attention
- **Failed (1/5)**: Critical failures preventing operation

### 3. Quick Debug (`quick_debug.sh`)
**One-command debugging and testing workflow**

```bash
# Complete workflow: build, flash, test, verify
./tools/quick_debug.sh all

# Quick test sequence
./tools/quick_debug.sh test

# Individual operations
./tools/quick_debug.sh check build flash monitor
```

**Commands:**
- `check` - Environment and device validation
- `build` - Quick firmware build with size reporting
- `flash` - Flash with verification
- `monitor` - Serial monitoring with log analysis
- `openocd` - OpenOCD connection testing
- `gdb` - Quick GDB hardware debugging session
- `test` - Comprehensive quick test sequence
- `verify` - Implementation verification via Python suite
- `all` - Complete development workflow

**Features:**
- 🎨 **Colored Output**: Visual status indication
- ⚡ **Fast Execution**: Optimized command sequences
- 🔧 **Error Handling**: Graceful failure management
- 📊 **Progress Reporting**: Real-time status updates
- 🔗 **Tool Integration**: Seamless integration with Python tools

### 4. Log Monitor (`log_monitor.py`)
**Real-time intelligent log analysis and system monitoring**

```bash
# Start real-time monitoring
python3 tools/log_monitor.py -p /dev/ttyACM0

# Monitor with timeout
python3 tools/log_monitor.py -t 300  # 5 minutes

# Custom serial settings
python3 tools/log_monitor.py -p /dev/ttyUSB0 -b 460800
```

**Intelligent Features:**
- 🔍 **Pattern Recognition**: ESP-IDF and VESC log format parsing
- 🚨 **Error Detection**: Critical error pattern matching
- ⚠️ **Warning Analysis**: Performance warning identification  
- 📊 **Metrics Extraction**: Heap, stack, WiFi, uptime tracking
- 📈 **Real-time Reporting**: Live system metrics dashboard
- 📁 **Data Persistence**: Raw logs, parsed data, metrics history
- 🎯 **Issue Categorization**: Automatic error and warning classification

**Monitored Metrics:**
- **Memory**: Free heap, stack usage per task
- **Connectivity**: WiFi RSSI, BLE connections, packet counts
- **System**: Uptime, CPU usage, error rates
- **Performance**: Response times, connection stability

## 🚀 Quick Start Workflows

### Development Workflow
```bash
# 1. Initial setup verification
./tools/quick_debug.sh check

# 2. Complete development cycle
./tools/quick_debug.sh all

# 3. Monitor runtime behavior
python3 tools/log_monitor.py -t 60
```

### Debugging Workflow
```bash
# 1. Comprehensive hardware test
python3 tools/debug_helper.py --test

# 2. Specific issue investigation
./tools/quick_debug.sh gdb

# 3. Real-time monitoring
python3 tools/log_monitor.py
```

### Verification Workflow  
```bash
# 1. Implementation verification
python3 tools/verification_suite.py --test all

# 2. Component-specific checks
python3 tools/verification_suite.py --test android
python3 tools/verification_suite.py --test esp32c6

# 3. Continuous verification
./tools/quick_debug.sh verify
```

### Production Validation
```bash
# Complete production readiness check
./tools/quick_debug.sh all && \
python3 tools/verification_suite.py --test all && \
python3 tools/log_monitor.py -t 120
```

## 📁 Output Files

### Log Directory Structure
```
logs/
├── debug_YYYYMMDD.log              # Debug helper logs
├── test_results_YYYYMMDD_HHMMSS.json  # Test results
├── verification_YYYYMMDD_HHMMSS.json  # Verification reports
├── raw_monitor_YYYYMMDD_HHMMSS.log    # Raw serial output
├── parsed_monitor_YYYYMMDD_HHMMSS.json # Parsed log entries
├── metrics_YYYYMMDD_HHMMSS.json       # System metrics
└── monitor_report_YYYYMMDD_HHMMSS.json # Final monitoring report
```

### Report Formats
All tools generate structured JSON reports for:
- **Automated Analysis**: Machine-readable results
- **CI/CD Integration**: Build pipeline compatibility  
- **Trend Analysis**: Historical comparison
- **Issue Tracking**: Error pattern identification

## 🔧 Configuration

### Environment Variables
```bash
export ESP_PORT="/dev/ttyACM0"        # Default serial port
export OPENOCD_CFG="esp32c6_wsl2.cfg" # OpenOCD configuration
export ESP_LOG_LEVEL="INFO"           # Log level filtering
```

### Tool Dependencies
- **Python 3.7+** with packages: `pyserial`, `dataclasses`
- **ESP-IDF v5.2+** properly configured
- **OpenOCD** with ESP32-C6 support
- **RISC-V GDB** (`riscv32-esp-elf-gdb`)

## 📊 Integration Examples

### GitHub Actions CI/CD
```yaml
- name: Hardware Validation
  run: |
    ./tools/quick_debug.sh build
    python3 tools/verification_suite.py --test all
```

### Pre-commit Hooks
```bash
#!/bin/sh
python3 tools/verification_suite.py --test build
```

### Automated Testing
```python
from tools.debug_helper import VESCDebugHelper
from tools.verification_suite import VESCVerificationSuite

# Automated test execution
helper = VESCDebugHelper()
results = helper.run_comprehensive_test()

suite = VESCVerificationSuite()
verification = suite.run_comprehensive_verification()
```

## 🎯 Best Practices

### Development Workflow
1. **Start with Verification**: `./tools/quick_debug.sh check`
2. **Iterative Development**: `./tools/quick_debug.sh build flash monitor`
3. **Regular Testing**: `python3 tools/debug_helper.py --test`
4. **Production Validation**: Complete verification before release

### Debugging Strategy
1. **Environment Check**: Verify all tools and connections
2. **Build Analysis**: Ensure clean compilation
3. **Hardware Testing**: OpenOCD and GDB validation
4. **Runtime Monitoring**: Real-time log analysis
5. **Issue Classification**: Use pattern recognition for root cause analysis

### Performance Monitoring
1. **Baseline Metrics**: Establish normal operation parameters
2. **Continuous Monitoring**: Real-time system health tracking
3. **Trend Analysis**: Historical performance comparison
4. **Alert Thresholds**: Automated issue detection

## 🆘 Troubleshooting

### Common Issues
- **Device Not Found**: Check USB connection and permissions
- **ESP-IDF Missing**: Source ESP-IDF environment: `. ~/esp/esp-idf/export.sh`
- **OpenOCD Fails**: Verify configuration file and device permissions
- **Build Errors**: Run verification suite for detailed analysis

### Support Resources
- **Logs Directory**: All tools save detailed logs for analysis
- **Verbose Output**: Most tools support debug/verbose modes
- **JSON Reports**: Machine-readable results for automated analysis
- **Error Categorization**: Intelligent issue classification and suggestions

---

**🎉 Happy Debugging!** These tools are designed to simplify ESP32-C6 VESC Express development with intelligent automation and comprehensive analysis.