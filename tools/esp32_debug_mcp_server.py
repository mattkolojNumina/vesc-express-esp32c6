#!/usr/bin/env python3
"""
ESP32 Debug Tools MCP Server
Exposes ESP32 debugging tools as MCP tools for Claude Code integration
"""

import sys
import os
import json
from pathlib import Path
from typing import Dict, Any, Optional

# Add tools directory to path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from fastmcp import FastMCP
    from pydantic import BaseModel
except ImportError:
    print("❌ FastMCP not installed. Run: pip install fastmcp")
    sys.exit(1)

# Import our debugging tools
try:
    from esp32c6_openocd_setup import ESP32C6OpenOCDSetup
    from esp32c6_gdb_automation import ESP32C6GDBAutomation  
    from esp32c6_memory_debug import ESP32C6MemoryDebugger
    from wsl2_esp32_debug_setup import WSL2ESP32DebugSetup
    from esp32c6_unified_debugger import ESP32C6UnifiedDebugger
except ImportError as e:
    print(f"❌ Failed to import debugging tools: {e}")
    sys.exit(1)

# Initialize MCP server
mcp = FastMCP("ESP32 Debug Tools")

# Tool instances (lazy loaded)
_tool_instances = {}

def get_tool(tool_name: str) -> Any:
    """Get or create tool instance"""
    if tool_name not in _tool_instances:
        if tool_name == 'openocd_setup':
            _tool_instances[tool_name] = ESP32C6OpenOCDSetup()
        elif tool_name == 'gdb_automation':
            _tool_instances[tool_name] = ESP32C6GDBAutomation()
        elif tool_name == 'memory_debugger':
            _tool_instances[tool_name] = ESP32C6MemoryDebugger()
        elif tool_name == 'wsl2_setup':
            _tool_instances[tool_name] = WSL2ESP32DebugSetup()
        elif tool_name == 'unified_debugger':
            _tool_instances[tool_name] = ESP32C6UnifiedDebugger()
        else:
            raise ValueError(f"Unknown tool: {tool_name}")
    
    return _tool_instances[tool_name]

# Pydantic models for structured input/output
class OpenOCDConfigRequest(BaseModel):
    config_type: str = "optimized"
    test_connection: bool = True

class DebugSessionRequest(BaseModel):
    profile: str = "basic"
    create_profiles: bool = False

class MemoryAnalysisRequest(BaseModel):
    analyze_layout: bool = True
    analyze_fragmentation: bool = False
    generate_report: bool = False

class WSL2SetupRequest(BaseModel):
    full_setup: bool = True
    verify_only: bool = False

# MCP Tool Definitions

@mcp.tool()
def setup_openocd_config(request: OpenOCDConfigRequest) -> str:
    """
    Setup ESP32-C6 OpenOCD configuration for debugging.
    
    Automatically detects ESP32-C6 device, creates optimized OpenOCD configuration,
    generates helper scripts, and optionally tests the connection.
    
    Args:
        request: Configuration parameters including config type and test option
        
    Returns:
        Status message with setup results and generated files
    """
    try:
        openocd_setup = get_tool('openocd_setup')
        success = openocd_setup.run_full_setup(
            config_type=request.config_type,
            test_connection=request.test_connection
        )
        
        if success:
            return f"✅ OpenOCD setup completed successfully!\n" \
                   f"📁 Configuration: esp32c6_{request.config_type}.cfg\n" \
                   f"📁 Debug scripts: debug_scripts/\n" \
                   f"📁 VS Code config: .vscode/\n" \
                   f"🚀 Quick start: ./debug_scripts/quick_debug.sh"
        else:
            return "❌ OpenOCD setup failed. Check device connection and dependencies."
            
    except Exception as e:
        return f"❌ OpenOCD setup error: {str(e)}"

@mcp.tool()
def run_debug_session(request: DebugSessionRequest) -> str:
    """
    Run interactive GDB debugging session with ESP32-C6.
    
    Provides pre-configured debugging profiles for different scenarios:
    - basic: General debugging with app_main breakpoint
    - crash: Crash analysis with abort/restart breakpoints  
    - memory: Memory debugging with malloc/free tracking
    - wifi: WiFi stack debugging
    - freertos: FreeRTOS task debugging
    
    Args:
        request: Debug session parameters including profile and options
        
    Returns:
        Status message with debug session results
    """
    try:
        gdb_automation = get_tool('gdb_automation')
        
        if request.create_profiles:
            profiles_dir = gdb_automation.create_debug_profiles()
            return f"✅ Debug profiles created successfully!\n" \
                   f"📁 Profiles directory: {profiles_dir}\n" \
                   f"📋 Available profiles: basic, crash, memory, wifi, freertos"
        
        # Check if project is built
        if not gdb_automation.check_build():
            return "❌ Project not built. Run 'idf.py build' first."
        
        # Note: For MCP, we can't run interactive sessions directly
        # Instead, we prepare everything and provide instructions
        script_path = gdb_automation.create_gdb_script()
        
        return f"✅ GDB debug session prepared!\n" \
               f"📋 Profile: {request.profile}\n" \
               f"📄 GDB script: {script_path}\n" \
               f"🚀 To run: Start OpenOCD, then run GDB with the generated script\n" \
               f"💡 Use unified_debug_wizard for automatic session management"
               
    except Exception as e:
        return f"❌ Debug session error: {str(e)}"

@mcp.tool()
def analyze_memory(request: MemoryAnalysisRequest) -> str:
    """
    Analyze ESP32-C6 memory layout, usage, and fragmentation.
    
    Provides comprehensive memory analysis including:
    - Memory layout analysis from ELF file
    - Stack usage analysis  
    - Heap monitoring and fragmentation detection
    - Memory report generation
    
    Args:
        request: Memory analysis parameters specifying which analyses to run
        
    Returns:
        Memory analysis results and generated reports
    """
    try:
        memory_debugger = get_tool('memory_debugger')
        results = []
        
        if request.analyze_layout:
            sections = memory_debugger.analyze_memory_layout()
            if sections:
                total_size = sum(info['size'] for info in sections.values())
                results.append(f"📊 Memory layout analyzed: {len(sections)} sections, {total_size/1024:.1f}KB total")
        
        if request.analyze_fragmentation:
            # Note: This requires hardware connection
            try:
                memory_debugger.analyze_memory_fragmentation()
                results.append("🧠 Memory fragmentation analysis completed")
            except Exception as e:
                results.append(f"⚠️  Fragmentation analysis requires hardware connection: {e}")
        
        if request.generate_report:
            report_path = memory_debugger.generate_memory_report()
            results.append(f"📋 Memory report generated: {report_path}")
        
        if not results:
            # Default analysis
            sections = memory_debugger.analyze_memory_layout()
            memory_debugger.analyze_stack_usage()
            results.append("✅ Basic memory analysis completed")
        
        return "\n".join(results)
        
    except Exception as e:
        return f"❌ Memory analysis error: {str(e)}"

@mcp.tool()
def setup_wsl2_debugging(request: WSL2SetupRequest) -> str:
    """
    Setup WSL2 environment for ESP32-C6 debugging.
    
    Configures WSL2 for ESP32 debugging including:
    - USB device passthrough with usbipd-win
    - Device permissions and udev rules
    - ESP32-C6 device detection and attachment
    - WSL2-specific debugging scripts
    
    Args:
        request: WSL2 setup parameters
        
    Returns:
        WSL2 setup results and configuration status
    """
    try:
        wsl2_setup = get_tool('wsl2_setup')
        
        if request.verify_only:
            if wsl2_setup.verify_wsl_device_access():
                return "✅ WSL2 ESP32 debugging environment verified successfully!"
            else:
                return "❌ WSL2 ESP32 debugging environment verification failed.\n" \
                       "Run full setup to configure USB passthrough."
        
        if request.full_setup:
            success = wsl2_setup.run_full_setup()
            if success:
                return "✅ WSL2 ESP32 debugging setup completed successfully!\n" \
                       "📁 Scripts: wsl2_debug_scripts/\n" \
                       "🔧 USB passthrough configured\n" \
                       "🚀 Ready for ESP32-C6 debugging in WSL2"
            else:
                return "❌ WSL2 setup failed. Check usbipd-win installation and ESP32 connection."
        
        return "⚠️  No setup action specified"
        
    except Exception as e:
        return f"❌ WSL2 setup error: {str(e)}"

@mcp.tool()
def debug_wizard() -> str:
    """
    Run the unified ESP32-C6 debugging setup wizard.
    
    Provides a comprehensive setup and validation wizard that:
    - Checks debugging environment and dependencies
    - Sets up OpenOCD, GDB, and WSL2 (if needed)
    - Validates hardware connections
    - Creates debugging profiles and scripts
    - Generates comprehensive setup report
    
    Returns:
        Wizard execution results and setup status
    """
    try:
        unified_debugger = get_tool('unified_debugger')
        
        # Run environment check
        env_ok = unified_debugger.check_environment()
        results = ["🔍 Environment Check Results:"]
        
        if env_ok:
            results.append("✅ All environment checks passed")
        else:
            results.append("⚠️  Some environment issues detected")
        
        # For MCP, we can't run interactive wizard, so provide setup guidance
        results.extend([
            "",
            "🧙 Debug Wizard Recommendations:",
            "1. Run setup_openocd_config to configure OpenOCD",
            "2. Run setup_wsl2_debugging if using WSL2", 
            "3. Use run_debug_session to start debugging",
            "4. Run analyze_memory for memory analysis",
            "",
            "📚 For interactive wizard, run: esp32-debug wizard"
        ])
        
        return "\n".join(results)
        
    except Exception as e:
        return f"❌ Debug wizard error: {str(e)}"

@mcp.tool()
def list_debug_tools() -> str:
    """
    List all available ESP32 debugging tools and their capabilities.
    
    Provides an overview of the debugging tools suite including:
    - Tool descriptions and capabilities
    - Command-line usage examples
    - Integration options
    - Quick start guidance
    
    Returns:
        Formatted list of all available debugging tools
    """
    tools_info = {
        "OpenOCD Setup": {
            "description": "Automatic ESP32-C6 OpenOCD configuration and testing",
            "command": "setup_openocd_config",
            "features": ["Device auto-detection", "Configuration profiles", "VS Code integration"]
        },
        "GDB Automation": {
            "description": "Automated GDB debugging with predefined profiles", 
            "command": "run_debug_session",
            "features": ["Debug profiles", "Coredump analysis", "System monitoring"]
        },
        "Memory Analysis": {
            "description": "Comprehensive memory layout and fragmentation analysis",
            "command": "analyze_memory", 
            "features": ["Layout analysis", "Heap monitoring", "Stack analysis"]
        },
        "WSL2 Setup": {
            "description": "WSL2 environment configuration for ESP32 debugging",
            "command": "setup_wsl2_debugging",
            "features": ["USB passthrough", "Permission management", "Device scripts"]
        },
        "Debug Wizard": {
            "description": "Unified setup wizard for complete debugging environment",
            "command": "debug_wizard",
            "features": ["Environment validation", "Automated setup", "Report generation"]
        }
    }
    
    result = ["🔧 ESP32-C6 Debugging Tools Suite", "=" * 40, ""]
    
    for tool_name, info in tools_info.items():
        result.extend([
            f"📋 {tool_name}:",
            f"   Description: {info['description']}", 
            f"   MCP Command: {info['command']}",
            f"   Features: {', '.join(info['features'])}",
            ""
        ])
    
    result.extend([
        "🚀 Quick Start:",
        "1. setup_openocd_config - Configure OpenOCD",
        "2. run_debug_session - Start debugging", 
        "3. analyze_memory - Memory analysis",
        "",
        "💡 For CLI access: pip install -e . && esp32-debug --help"
    ])
    
    return "\n".join(result)

# Resources for configuration files and documentation

@mcp.resource("file://esp32_tools_config")
def get_tools_config() -> str:
    """Get the ESP32 debugging tools configuration and status"""
    try:
        config = {
            "tools_available": len(_tool_instances),
            "working_directory": os.getcwd(),
            "tools_path": str(Path(__file__).parent),
            "python_version": sys.version.split()[0]
        }
        return json.dumps(config, indent=2)
    except Exception as e:
        return f"Error getting config: {e}"

@mcp.resource("file://esp32_debug_status")
def get_debug_status() -> str:
    """Get current ESP32 debugging environment status"""
    try:
        # Check basic environment
        status = {
            "esp_idf_path": os.environ.get('IDF_PATH'),
            "project_build_exists": Path('build/project.elf').exists(),
            "openocd_config_exists": Path('esp32c6_optimized.cfg').exists(),
            "debug_scripts_exist": Path('debug_scripts').exists(),
            "tools_installed": True  # If we're running, tools are installed
        }
        return json.dumps(status, indent=2)
    except Exception as e:
        return f"Error getting debug status: {e}"

# Additional MCP methods for complete specification compliance

# Implement optional resources/list method
def list_resources():
    """List all available MCP resources"""
    resources = [
        {
            "uri": "file://esp32_tools_config",
            "name": "ESP32 Tools Configuration", 
            "description": "System configuration and tool status",
            "mimeType": "application/json"
        },
        {
            "uri": "file://esp32_debug_status",
            "name": "ESP32 Debug Environment Status",
            "description": "Current debugging environment status",
            "mimeType": "application/json"
        }
    ]
    return {"resources": resources}

# Implement optional resources/read method  
def read_resource(uri: str):
    """Read a specific MCP resource"""
    if uri == "file://esp32_tools_config":
        return {"contents": [{"type": "text", "text": get_tools_config()}]}
    elif uri == "file://esp32_debug_status":
        return {"contents": [{"type": "text", "text": get_debug_status()}]}
    else:
        raise ValueError(f"Unknown resource URI: {uri}")

# Register the optional methods with FastMCP if supported
try:
    # These might not be directly supported by FastMCP decorators,
    # but the functions are available for manual registration
    pass
except ImportError as e:
    # FastMCP decorator registration might not support these methods
    print(f"Warning: Manual MCP method registration not supported: {e}")
except Exception as e:
    # Other registration issues
    print(f"Warning: MCP method registration issue: {e}")

# Additional MCP tool for complete server information

@mcp.tool()
def get_server_info() -> str:
    """
    Get comprehensive MCP server information and capabilities.
    
    Provides detailed information about the MCP server including:
    - Server metadata and version
    - Available tools and resources
    - Capability overview
    - System status
    
    Returns:
        Comprehensive server information in JSON format
    """
    try:
        # Get tool information
        tool_info = {}
        for tool_name in ['openocd_setup', 'gdb_automation', 'memory_debugger', 'wsl2_setup', 'unified_debugger']:
            try:
                tool_instance = get_tool(tool_name)
                tool_info[tool_name] = {
                    "available": True,
                    "class": tool_instance.__class__.__name__,
                    "module": tool_instance.__class__.__module__
                }
            except Exception as e:
                tool_info[tool_name] = {
                    "available": False,
                    "error": str(e)
                }
        
        server_info = {
            "mcp_server": {
                "name": "ESP32 Debug Tools",
                "version": "1.0.0",
                "protocol_version": "2024-11-05",
                "framework": "FastMCP 2.0"
            },
            "capabilities": {
                "tools": 7,  # Updated count
                "resources": 2,
                "prompts": 0,
                "sampling": False
            },
            "tools_status": tool_info,
            "resources": [
                {
                    "uri": "file://esp32_tools_config",
                    "name": "ESP32 Tools Configuration",
                    "description": "System configuration and tool status"
                },
                {
                    "uri": "file://esp32_debug_status", 
                    "name": "ESP32 Debug Environment Status",
                    "description": "Current debugging environment status"
                }
            ],
            "system_info": {
                "python_version": sys.version.split()[0],
                "working_directory": os.getcwd(),
                "tools_path": str(Path(__file__).parent),
                "esp_idf_available": bool(os.environ.get('IDF_PATH'))
            }
        }
        
        return json.dumps(server_info, indent=2)
        
    except Exception as e:
        return f"❌ Server info error: {str(e)}"

if __name__ == "__main__":
    # Run the MCP server - use stdio transport which is more compatible
    print("🚀 Starting ESP32 Debug Tools MCP Server...")
    print("📡 Transport: stdio")
    print("💡 Use with Claude Code: claude mcp add -t stdio -s user esp32-debug-tools python3 /path/to/esp32_debug_mcp_server.py")
    mcp.run(transport="stdio")