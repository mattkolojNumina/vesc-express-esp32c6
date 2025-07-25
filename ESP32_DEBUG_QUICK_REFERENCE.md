# ESP32-C6 Debugging Tools - Quick Reference Guide

## 🚀 **Instant Access Command**

```bash
esp32-debug --list
```
*Shows all available tools with descriptions and usage*

---

## ⚡ **Common Workflows**

### **🧙 Quick Setup Wizard** (Recommended for first-time users)
```bash
esp32-debug wizard
```

### **🔧 Setup OpenOCD for JTAG Debugging**
```bash
esp32-debug setup-openocd --test
```

### **🐛 Start Interactive GDB Debugging Session**
```bash
esp32-debug gdb-debug --profile basic
```

### **🧠 Analyze Memory Usage**
```bash
esp32-debug memory-analyze --report
```

### **🐧 Setup WSL2 Environment** (Windows users only)
```bash
esp32-debug setup-wsl2
```

---

## 📋 **All Available Commands**

| Command | Purpose | Quick Usage |
|---------|---------|-------------|
| `wizard` | Interactive setup wizard | `esp32-debug wizard` |
| `setup-openocd` | Configure JTAG debugging | `esp32-debug setup-openocd --test` |
| `gdb-debug` | Start debugging session | `esp32-debug gdb-debug --profile crash` |
| `memory-analyze` | Memory analysis | `esp32-debug memory-analyze --report` |
| `setup-wsl2` | WSL2 environment setup | `esp32-debug setup-wsl2 --verify` |
| `info` | System information | `esp32-debug info` |
| `run` | Execute specific tool | `esp32-debug run <tool_name>` |

---

## 🔍 **Help System**

```bash
esp32-debug --help              # Main help
esp32-debug <command> --help    # Command-specific help
esp32-debug info                # Detailed system information
```

---

## 🤖 **Claude Code Integration**

Add to Claude Code for AI-assisted debugging:
```bash
claude mcp add -t stdio -s user esp32-debug-tools \
  python3 /home/rds/vesc_express/tools/esp32_debug_mcp_server.py
```

Available MCP tools:
- `setup_openocd_config` - Configure OpenOCD
- `run_debug_session` - Start debugging
- `analyze_memory` - Memory analysis  
- `setup_wsl2_environment` - WSL2 setup
- `quick_start_wizard` - Interactive wizard
- `list_available_tools` - Tool discovery

---

## 💡 **Pro Tips**

1. **Start with the wizard**: `esp32-debug wizard` handles most common setup automatically
2. **Check environment**: `esp32-debug info` shows system status and tool availability
3. **Test connections**: Use `--test` flags to verify setup before debugging
4. **WSL2 users**: Run `esp32-debug setup-wsl2` once for USB device forwarding
5. **Memory issues**: Use `esp32-debug memory-analyze --fragmentation` for detailed analysis

---

## 🛟 **Troubleshooting**

| Issue | Solution |
|-------|----------|
| Tools not found | Run `pip install -e .` in project root |
| OpenOCD fails | Check USB connections and device permissions |
| WSL2 device access | Run `esp32-debug setup-wsl2` with sudo |
| GDB connection issues | Verify ESP32-C6 is in download mode |
| Permission errors | Add user to `dialout` group: `sudo usermod -a -G dialout $USER` |

---

## 📚 **Complete Documentation**

- **Full Guide**: `ESP32_IDF_DEBUGGING_SIMPLIFIED.md`
- **Tool Details**: `tools/README.md`
- **Getting Started**: `tools/GETTING_STARTED.md`
- **Technical Summary**: `DEBUGGING_SOLUTION_COMPLETE.md`

---

*For detailed explanations and advanced usage, refer to the complete documentation files listed above.*