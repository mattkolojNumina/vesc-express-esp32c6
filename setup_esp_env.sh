#!/bin/bash
# ESP-IDF Environment Setup Script
# Based on ESP32-C6 VESC Express Research Document
# Automatically sets up complete ESP-IDF debugging environment

set -e

echo "🚀 ESP32-C6 VESC Express - Development Environment Setup"
echo "========================================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# ESP-IDF Configuration
ESP_IDF_PATH="$HOME/esp/esp-idf"
ESP_IDF_TOOLS_PATH="$HOME/.espressif"

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Check if ESP-IDF is installed
if [ ! -d "$ESP_IDF_PATH" ]; then
    print_error "ESP-IDF not found at $ESP_IDF_PATH"
    echo "Please install ESP-IDF first:"
    echo "  git clone --recursive https://github.com/espressif/esp-idf.git $ESP_IDF_PATH"
    echo "  cd $ESP_IDF_PATH && ./install.sh all"
    exit 1
fi

print_status "ESP-IDF installation found at $ESP_IDF_PATH"

# Source ESP-IDF environment
print_info "Setting up ESP-IDF environment..."
source $ESP_IDF_PATH/export.sh

# Verify ESP-IDF tools
print_info "Verifying ESP-IDF tools..."
which idf.py >/dev/null 2>&1 && print_status "idf.py found" || { print_error "idf.py not found"; exit 1; }
which openocd >/dev/null 2>&1 && print_status "OpenOCD found" || { print_error "OpenOCD not found"; exit 1; }
which riscv32-esp-elf-gdb >/dev/null 2>&1 && print_status "RISC-V GDB found" || { print_error "RISC-V GDB not found"; exit 1; }
which esptool.py >/dev/null 2>&1 && print_status "esptool.py found" || { print_error "esptool.py not found"; exit 1; }

# Show versions
print_info "Tool versions:"
echo "  ESP-IDF: $(idf.py --version 2>&1 | head -1)"
echo "  OpenOCD: $(openocd --version 2>&1 | head -1 | cut -d' ' -f1-4)"
echo "  GDB: $(riscv32-esp-elf-gdb --version 2>&1 | head -1 | cut -d' ' -f1-4)"
echo "  esptool: $(esptool.py version 2>&1 | head -1)"

# Check for ESP32-C6 device
print_info "Checking for ESP32-C6 device..."
if lsusb | grep -q "303a:1001"; then
    print_status "ESP32-C6 device detected"
    # Find the serial port
    if ls /dev/ttyACM* >/dev/null 2>&1; then
        DEVICE_PORT=$(ls /dev/ttyACM* | head -1)
        print_status "Device available at: $DEVICE_PORT"
        export ESPPORT=$DEVICE_PORT
    fi
else
    print_warning "ESP32-C6 device not detected. Please ensure device is connected."
fi

# Set up convenient aliases
print_info "Setting up convenient aliases..."

# Create aliases for common ESP-IDF operations
cat << 'EOF' >> ~/.bashrc

# ESP32-C6 VESC Express Development Aliases
alias esp-setup='source $HOME/esp/esp-idf/export.sh'
alias esp-build='idf.py build'
alias esp-flash='idf.py flash'
alias esp-monitor='idf.py monitor'
alias esp-clean='idf.py fullclean'
alias esp-debug='python tools/esp32c6_unified_debugger.py --interactive'
alias esp-check='python tools/debug_helper.py --check'

# Quick debugging commands
alias openocd-start='openocd -f tools/esp32c6_final.cfg'
alias gdb-connect='riscv32-esp-elf-gdb build/*.elf -ex "target remote :3333"'
EOF

print_status "Development aliases added to ~/.bashrc"

# Create VS Code settings if .vscode directory exists
if [ ! -d ".vscode" ]; then
    mkdir -p .vscode
fi

# VS Code tasks for ESP32-C6 development
cat << 'EOF' > .vscode/tasks.json
{
    "version": "2.0.0",
    "tasks": [
        {
            "label": "ESP-IDF: Build",
            "type": "shell",
            "command": "idf.py",
            "args": ["build"],
            "group": {
                "kind": "build",
                "isDefault": true
            },
            "presentation": {
                "echo": true,
                "reveal": "always",
                "focus": false,
                "panel": "shared"
            },
            "problemMatcher": "$gcc"
        },
        {
            "label": "ESP-IDF: Flash",
            "type": "shell",
            "command": "idf.py",
            "args": ["flash"],
            "group": "build",
            "dependsOn": "ESP-IDF: Build"
        },
        {
            "label": "ESP-IDF: Monitor",
            "type": "shell",
            "command": "idf.py",
            "args": ["monitor"],
            "group": "build"
        },
        {
            "label": "ESP-IDF: Clean Build",
            "type": "shell",
            "command": "idf.py",
            "args": ["fullclean", "build"],
            "group": "build"
        },
        {
            "label": "Debug Check",
            "type": "shell",
            "command": "python",
            "args": ["tools/debug_helper.py", "--check"],
            "group": "build"
        }
    ]
}
EOF

print_status "VS Code tasks configured"

# Create launch configuration for debugging
cat << 'EOF' > .vscode/launch.json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "ESP32-C6 Debug",
            "type": "cppdbg",
            "request": "launch",
            "program": "${workspaceFolder}/build/${workspaceFolderBasename}.elf",
            "cwd": "${workspaceFolder}",
            "MIMode": "gdb",
            "miDebuggerPath": "riscv32-esp-elf-gdb",
            "miDebuggerServerAddress": "localhost:3333",
            "setupCommands": [
                {
                    "description": "Enable pretty-printing for gdb",
                    "text": "-enable-pretty-printing",
                    "ignoreFailures": true
                },
                {
                    "description": "Set target to remote",
                    "text": "target remote :3333",
                    "ignoreFailures": false
                },
                {
                    "description": "Load symbols",
                    "text": "monitor reset halt",
                    "ignoreFailures": false
                },
                {
                    "description": "Set breakpoint at app_main",
                    "text": "b app_main",
                    "ignoreFailures": true
                }
            ],
            "preLaunchTask": "ESP-IDF: Build",
            "postDebugTask": "",
            "logging": {
                "engineLogging": false
            }
        }
    ]
}
EOF

print_status "VS Code debugging configuration created"

# Project-specific environment file
cat << EOF > .env.esp32
# ESP32-C6 VESC Express Environment Configuration
export IDF_PATH=$ESP_IDF_PATH
export IDF_TOOLS_PATH=$ESP_IDF_TOOLS_PATH
export ESPPORT=${DEVICE_PORT:-/dev/ttyACM0}
export ESPBAUD=115200
export ESP_TARGET=esp32c6

# OpenOCD Configuration
export OPENOCD_SCRIPTS=\$IDF_PATH/components/esptool_py/esptool/targets/stub_flasher/
export OPENOCD_CONFIG=tools/esp32c6_final.cfg

# Development paths
export VESC_EXPRESS_ROOT=\$(pwd)
export DEBUG_TOOLS_PATH=\$VESC_EXPRESS_ROOT/tools

# Aliases for this project
alias build='idf.py build'
alias flash='idf.py flash'
alias monitor='idf.py monitor'
alias debug='python tools/esp32c6_unified_debugger.py --interactive'
alias quick-check='python tools/debug_helper.py --check'
EOF

print_status "Project environment file created (.env.esp32)"

# Make script executable
chmod +x setup_esp_env.sh

echo ""
echo "🎉 ESP32-C6 VESC Express development environment setup complete!"
echo ""
echo "Next steps:"
echo "1. Run: source .env.esp32        (to load project environment)"  
echo "2. Run: build                    (to build the project)"
echo "3. Run: debug                    (to start interactive debugging)"
echo "4. Run: quick-check              (to verify environment)"
echo ""
echo "For VS Code users:"
echo "- Press Ctrl+Shift+P and type 'Tasks: Run Task' to see available tasks"  
echo "- Use F5 to start debugging with breakpoints"
echo ""
print_status "Environment setup successful! Happy debugging! 🚀"