# Fastmcp Cross-Platform Compatibility

Comprehensive platform support matrix and setup guidelines for Fastmcp tool discovery ecosystem.

## ✅ Platform Support Matrix

| Platform | Core Tools | Analytics | Slash Commands | Status |
|----------|------------|-----------|----------------|---------|
| **Linux (Ubuntu/Debian)** | ✅ Native | ✅ Full | ✅ Complete | **Fully Supported** |
| **WSL2 (Windows)** | ✅ Native | ✅ Full | ✅ Complete | **Recommended** |
| **macOS** | ✅ Native | ✅ Full | ✅ Complete | **Supported** |
| **Windows Native** | ⚠️ Limited | ⚠️ Limited | ✅ Complete | **Basic Support** |

## 🐧 Linux (Primary Platform)

### Compatibility Status: **EXCELLENT**
- **Core Tools**: Native support, optimal performance
- **Analytics**: Full tracking and reporting capabilities
- **Discovery**: All patterns fully functional
- **Claude Code**: Complete MCP server integration

### Verified Distributions
- Ubuntu 20.04 LTS, 22.04 LTS, 24.04 LTS
- Debian 11, 12
- Fedora 38+
- Arch Linux (community support)

### Setup Requirements
```bash
# Basic dependencies
sudo apt update
sudo apt install git curl bash

# Project setup
./fastmcp_ultimate setup
```

## 🪟 WSL2 (Recommended for Windows)

### Compatibility Status: **VERY GOOD**
- **Core Tools**: Full compatibility via Linux environment
- **Analytics**: Complete functionality
- **Performance**: Near-native Linux performance

### WSL2 Setup
```bash
# Install WSL2 with Ubuntu
wsl --install Ubuntu

# In WSL2 terminal
cd fastmcp_project
./fastmcp_ultimate setup
./fastmcp_ultimate check
```

### Known WSL2 Limitations
- **File System**: Slight performance impact for large file operations
- **Service Integration**: May require manual service management
- **Analytics**: Full functionality with minimal setup

## 🍎 macOS

### Compatibility Status: **GOOD**
- **Core Tools**: Native support with Homebrew
- **Analytics**: Full functionality
- **Silicon**: Both Intel and Apple Silicon supported

### macOS Setup
```bash
# Install Homebrew (if not installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install dependencies
brew install git curl bash

# Project setup
./fastmcp_ultimate setup
```

### macOS-Specific Considerations
- **Shell**: Use bash for full script compatibility
- **Security**: Gatekeeper may require permission for scripts
- **Analytics**: Full functionality with system integration

## 🪟 Windows Native

### Compatibility Status: **LIMITED**
- **Core Tools**: PowerShell compatibility layer
- **Analytics**: Limited shell script support
- **Recommendation**: Use WSL2 instead

### Windows Native Setup (Not Recommended)
```powershell
# Use Git Bash for better compatibility
# Install: https://git-scm.com/downloads

# In Git Bash
cd fastmcp_project
bash ./fastmcp_ultimate setup
```

## 🔧 Tool Compatibility Matrix

### Scripts and Analytics
| Tool | Linux | WSL2 | macOS | Windows |
|------|-------|------|-------|---------|
| `fastmcp_ultimate` | ✅ | ✅ | ✅ | ⚠️ Git Bash |
| `fastmcp_analytics_report.sh` | ✅ | ✅ | ✅ | ⚠️ Git Bash |
| Analytics tracking | ✅ | ✅ | ✅ | ⚠️ Limited |

### Claude Code Integration
| Feature | Linux | WSL2 | macOS | Windows |
|---------|-------|------|-------|---------|
| Slash commands | ✅ | ✅ | ✅ | ✅ |
| MCP servers | ✅ | ✅ | ✅ | ✅ |
| File operations | ✅ | ✅ | ✅ | ⚠️ |

## 🚀 Platform-Specific Optimizations

### Linux Optimizations
```bash
# High-performance analytics
export ANALYTICS_PERFORMANCE=true
./fastmcp_analytics_report.sh

# Real-time monitoring
watch -n 1 './fastmcp_ultimate health'
```

### WSL2 Optimizations
```bash
# Improve I/O performance
echo "[wsl2]
memory=8GB
processors=4" > ~/.wslconfig

# Restart WSL2 (in Windows PowerShell)
wsl --shutdown
```

### macOS Optimizations
```bash
# Use Homebrew tools for better performance
export PATH="/opt/homebrew/bin:$PATH"

# Increase file descriptor limits
ulimit -n 65536
```

## 🧪 Platform Testing Results

### Test Suite: Fastmcp Discovery Patterns
Tested on all platforms with the following scenarios:

#### ✅ Basic Functionality (All Platforms)
- Tool setup: `./fastmcp_ultimate setup`
- Environment check: `./fastmcp_ultimate check`
- Discovery: `./fastmcp_ultimate discover`
- Analytics: `./fastmcp_analytics_report.sh`

#### ✅ Advanced Features (Linux, WSL2, macOS)
- Smart recommendations: `./fastmcp_ultimate suggest`
- Performance analytics with detailed insights
- Cross-platform script compatibility
- Claude Code integration

#### ⚠️ Known Issues
- **Windows Native**: Limited shell script support
- **WSL2**: Occasional file system performance impact
- **macOS**: Security warnings for unsigned scripts

## 📋 Platform Recommendations

### For Development Teams
1. **Primary**: Linux (Ubuntu 22.04 LTS) - Best performance and compatibility
2. **Secondary**: WSL2 on Windows - Good compromise for Windows users
3. **Alternative**: macOS - Excellent for mixed development environments
4. **Avoid**: Windows Native - Limited functionality

### For Individual Developers
- **Linux Users**: Use native Linux setup
- **Windows Users**: Use WSL2 with full integration
- **macOS Users**: Native setup with Homebrew
- **Mixed Teams**: Standardize on WSL2 for consistency

---

**Platform Compatibility Summary**: Fastmcp provides excellent cross-platform support with Linux as the primary platform, WSL2 as the recommended Windows solution, and good macOS compatibility. All major discovery patterns are supported across platforms.**
