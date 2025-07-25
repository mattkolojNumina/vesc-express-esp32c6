# VESC Express Team Onboarding Guide

Welcome to the VESC Express ESP32-C6 development team! This guide will get you up and running with our comprehensive development environment.

## 🚀 Quick Start (5 Minutes)

### 1. Initial Setup
```bash
# Clone the repository
git clone <repository-url>
cd vesc_express

# Run automated setup
./vesc setup

# Verify everything works
./vesc check
```

### 2. First Development Cycle
```bash
# Complete development workflow: build + flash + monitor
./vesc dev
```

That's it! You're now developing on ESP32-C6 VESC Express.

## 📋 Development Environment Overview

### Core Components
- **ESP-IDF v5.5**: Official Espressif development framework
- **ESP32-C6**: Target microcontroller with WiFi 6, Bluetooth 5, IEEE802.15.4
- **VESC Express**: Motor controller firmware with LispBM scripting
- **Claude Code Integration**: AI-powered development assistance with MCP servers

### Available Tools
- **./vesc**: Ultimate convenience script (15+ commands)
- **24+ Python tools**: Specialized debugging, analysis, and automation
- **6 Slash commands**: Claude Code integration (`/esp-troubleshoot`, `/esp-debug`, etc.)
- **OpenOCD/GDB**: Hardware-level debugging with built-in USB JTAG
- **Analytics**: Usage tracking and smart recommendations

## 🛠️ Essential Commands

### Development Workflow
```bash
./vesc dev         # Complete cycle: build + flash + monitor
./vesc quick       # Fast: check + build + flash
./vesc build       # Build firmware only
./vesc flash       # Flash to device only
./vesc monitor     # Serial monitor only
./vesc clean       # Clean build artifacts
```

### Debugging & Analysis
```bash
./vesc debug       # Interactive debugging session
./vesc check       # Environment validation
./vesc troubleshoot # Automated problem resolution
./vesc analyze     # Device analysis with esptool.py
./vesc memory      # Memory usage analysis
```

### Tool Discovery
```bash
./vesc discover    # Show all available tools
./vesc suggest     # Smart recommendations based on project state
./vesc tools       # List specialized Python tools
./vesc_analytics_report.sh  # View usage analytics
```

## 🎯 Claude Code Integration

Our project includes comprehensive Claude Code integration for AI-powered development.

### Slash Commands (Type `/` in Claude Code)
- `/esp-troubleshoot` - Comprehensive device troubleshooting
- `/esp-analyze` - Advanced device analysis  
- `/esp-debug` - Interactive debugging
- `/esp-build` - Build and flash operations
- `/esp-discover` - Tool exploration
- `/esp-analyze-code` - Static code analysis

### MCP Server Capabilities
- **7 Active MCP Servers**: 180+ tools across development, research, debugging
- **FastMCP**: System operations, analytics, databases (59 tools)
- **GitHub**: Complete repository management & CI/CD (26 tools)
- **Serena**: Semantic code analysis and intelligent editing (25+ tools)
- **Filesystem**: Secure file operations (12 tools)
- **Perplexity**: Advanced AI research (2 tools)

## 🏗️ Project Architecture

### Hardware Support
- **ESP32-C6**: Primary target with WiFi 6, BT 5, IEEE802.15.4
- **8MB Flash**: Adequate for full VESC firmware + user scripts
- **Built-in USB JTAG**: Hardware debugging without external tools
- **Hardware Variants**: Modular abstraction layer supports multiple boards

### Software Stack
```
┌─────────────────────────────────────┐
│ LispBM Scripts (User Code)          │
├─────────────────────────────────────┤
│ VESC Express (Motor Control + Comm) │
├─────────────────────────────────────┤
│ ESP-IDF v5.5 (Framework)           │
├─────────────────────────────────────┤
│ ESP32-C6 Hardware                  │
└─────────────────────────────────────┘
```

### Key Features
- **Motor Control**: Advanced FOC algorithms with sensor support
- **Communication**: BLE, WiFi, UART, CAN bus protocols
- **Scripting**: LispBM interpreter for user customization
- **Logging**: Comprehensive telemetry and debugging
- **OTA Updates**: Wireless firmware updates
- **Android Compatibility**: Optimized for modern Android devices

## 🐛 Debugging Workflows

### Quick Debugging
```bash
# Environment issues
./vesc check

# Device connection problems
./vesc troubleshoot

# Memory analysis
./vesc memory

# Advanced device analysis
./vesc analyze
```

### Interactive Debugging
```bash
# Start unified debugger
./vesc debug

# OpenOCD + GDB (separate terminals)
./vesc openocd    # Terminal 1: Start OpenOCD server
./vesc gdb        # Terminal 2: Connect GDB
```

### Claude Code Debugging
```bash
# In Claude Code, type:
/esp-troubleshoot   # Automated troubleshooting
/esp-debug          # Interactive debugging guide
/esp-analyze        # Device analysis
```

## 📊 Analytics & Optimization

### Usage Analytics
```bash
./vesc_analytics_report.sh     # View detailed usage report
./vesc_analytics_report.sh export  # Export analytics data
./vesc_analytics_report.sh clear   # Clear analytics
```

### Performance Monitoring
- Build size analysis: `./vesc size`
- Memory usage: `./vesc memory`
- Static code analysis: `/esp-analyze-code` in Claude Code
- Real-time monitoring: `./vesc monitor`

## 🔧 Common Troubleshooting

### Device Not Detected
```bash
# Check USB connection
lsusb | grep 303a

# Fix permissions (if needed)
sudo usermod -a -G dialout $USER
# Logout and login again

# Comprehensive check
./vesc troubleshoot
```

### Build Issues
```bash
# Clean rebuild
./vesc clean
./vesc build

# Environment reset
./vesc setup
```

### ESP-IDF Environment
```bash
# Check environment
echo $IDF_PATH

# Reload environment
source ~/esp/esp-idf/export.sh

# Full reinstall
cd ~/esp/esp-idf && ./install.sh all
```

## 📚 Documentation & Resources

### Project Documentation
- `CLAUDE.md` - Project context and MCP capabilities
- `QUICK_START_GUIDE.md` - Complete developer reference
- `tools/GETTING_STARTED.md` - Tool-specific documentation
- `esp-idf-openocd-research.md` - ESP-IDF research and best practices

### ESP-IDF Documentation
- [ESP-IDF Programming Guide](https://docs.espressif.com/projects/esp-idf/en/latest/)
- [ESP32-C6 Technical Reference](https://www.espressif.com/sites/default/files/documentation/esp32-c6_technical_reference_manual_en.pdf)
- [Hardware Design Guidelines](https://www.espressif.com/sites/default/files/documentation/esp32-c6_hardware_design_guidelines_en.pdf)

### VESC Resources
- [VESC Project](https://vesc-project.com/)
- [LispBM Documentation](https://github.com/svenssonjoel/lispBM)
- [VESC Tool](https://vesc-project.com/vesc_tool)

## 🔐 Security & Best Practices

### Development Security
- **No secrets in code**: Use environment variables or secure storage
- **Code review**: All changes reviewed before merge
- **Static analysis**: Use `/esp-analyze-code` for security checks
- **Secure communications**: Proper encryption for WiFi/BLE

### Production Considerations
- **OTA Security**: Signed firmware updates
- **Device Authentication**: Unique device certificates
- **Network Security**: WPA3 and certificate validation
- **Debug Interface**: Disabled in production builds

## 🎯 Development Best Practices

### Code Style
- Follow existing VESC coding conventions
- Use meaningful variable and function names
- Comment complex algorithms and hardware interactions
- Run static analysis before commits

### Git Workflow
```bash
# Create feature branch
git checkout -b feature/my-feature

# Make changes, test thoroughly
./vesc dev

# Run analysis
/esp-analyze-code   # In Claude Code

# Commit with descriptive message
git commit -m "feat: Add motor temperature monitoring"

# Push and create PR
git push origin feature/my-feature
```

### Testing Strategy
- **Unit Tests**: Test individual functions
- **Integration Tests**: Test hardware interactions  
- **Hardware-in-Loop**: Test with actual motor systems
- **Analytics**: Use `./vesc_analytics_report.sh` to track tool usage

## 🚨 Emergency Procedures

### Bricked Device Recovery
```bash
# Force bootloader mode
# Hold BOOT button while connecting USB

# Emergency flash
python tools/esptool_advanced_suite.py --emergency-flash

# Full recovery
./vesc troubleshoot
```

### Build System Recovery
```bash
# Nuclear option: clean everything
./vesc clean
rm -rf build/
./vesc setup
./vesc build
```

### Environment Reset
```bash
# Backup project settings
cp sdkconfig sdkconfig.backup

# Full ESP-IDF reinstall
cd ~/esp/esp-idf
git pull
./install.sh all
source export.sh

# Restore project
cd /path/to/vesc_express
cp sdkconfig.backup sdkconfig
./vesc build
```

## 💡 Tips for New Team Members

### Day 1 Checklist
- [ ] Complete initial setup: `./vesc setup`
- [ ] Verify environment: `./vesc check`
- [ ] Run first build: `./vesc dev`
- [ ] Explore tools: `./vesc discover`
- [ ] Try Claude integration: `/esp-troubleshoot`

### Week 1 Goals
- [ ] Understand project architecture
- [ ] Complete first bug fix or feature
- [ ] Master debugging workflow
- [ ] Contribute to documentation

### Advanced Usage
- Customize `.vesc_analytics.log` for personal tracking
- Create custom Python tools in `tools/` directory
- Extend slash commands in `.claude/commands/`
- Contribute to MCP server enhancements

## 📞 Getting Help

### Internal Resources
1. **Claude Code Integration**: Type `/esp-troubleshoot` for immediate help
2. **Tool Discovery**: Run `./vesc discover` to explore capabilities
3. **Analytics**: Use `./vesc_analytics_report.sh` to understand common issues

### External Resources
1. **ESP-IDF Community**: [GitHub Issues](https://github.com/espressif/esp-idf/issues)
2. **VESC Community**: [VESC Forums](https://vesc-project.com/forum)
3. **ESP32 Community**: [ESP32 Forum](https://esp32.com/)

### Escalation Path
1. **Self-Service**: Use automated tools (`./vesc troubleshoot`)
2. **Documentation**: Check project docs and ESP-IDF guides
3. **Team Discussion**: Discuss in team channels
4. **Expert Consultation**: Escalate complex hardware/firmware issues

---

**Welcome to the team! This environment represents the state-of-the-art in ESP32 development with AI integration. Happy coding! 🚀**