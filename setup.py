#!/usr/bin/env python3
"""
ESP32-C6 Debugging Tools Suite - Setup Configuration
Configures entry points for automatic tool discovery via Stevedore
"""

from setuptools import setup, find_packages

# Read version from __init__.py or set directly
VERSION = "1.0.0"

# Read long description from README
with open("tools/README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="esp32-debug-tools",
    version=VERSION,
    author="ESP32-C6 Debug Tools Suite",
    description="Comprehensive ESP32-C6 debugging and development tools",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(where="tools"),
    package_dir={"": "tools"},
    python_requires=">=3.8",
    
    # Dependencies
    install_requires=[
        "stevedore>=5.0.0",
        "click>=8.0.0",
        "fastmcp>=2.0.0",
        "pydantic>=2.0.0",
        "rich>=12.0.0",
        "typer>=0.9.0",
    ],
    
    # Entry points for automatic discovery
    entry_points={
        # Main CLI entry point
        "console_scripts": [
            "esp32-debug = esp32_debug_cli:main",
        ],
        
        # ESP32 debugging tools namespace
        "esp32_debug_tools": [
            "openocd_setup = esp32c6_openocd_setup:ESP32C6OpenOCDSetup",
            "gdb_automation = esp32c6_gdb_automation:ESP32C6GDBAutomation", 
            "memory_debug = esp32c6_memory_debug:ESP32C6MemoryDebugger",
            "wsl2_setup = wsl2_esp32_debug_setup:WSL2ESP32DebugSetup",
            "unified_debugger = esp32c6_unified_debugger:ESP32C6UnifiedDebugger",
        ],
        
        # Tool commands for CLI discovery
        "esp32_debug_commands": [
            "setup-openocd = esp32c6_openocd_setup:cli_main",
            "gdb-debug = esp32c6_gdb_automation:cli_main",
            "memory-analyze = esp32c6_memory_debug:cli_main", 
            "setup-wsl2 = wsl2_esp32_debug_setup:cli_main",
            "debug-wizard = esp32c6_unified_debugger:cli_main",
        ],
        
        # FastMCP tools for Claude Code integration
        "esp32_mcp_tools": [
            "openocd_config = esp32c6_openocd_setup:create_openocd_config",
            "run_debug_session = esp32c6_gdb_automation:run_debug_session_mcp",
            "analyze_memory = esp32c6_memory_debug:analyze_memory_mcp",
            "setup_wsl2 = wsl2_esp32_debug_setup:setup_wsl2_mcp",
            "debug_wizard = esp32c6_unified_debugger:quick_start_wizard_mcp",
            "list_tools = esp32_debug_mcp_server:list_debug_tools",
            "server_info = esp32_debug_mcp_server:get_server_info",
        ],
    },
    
    # Package data
    package_data={
        "": ["*.md", "*.txt", "*.cfg", "*.json", "*.sh", "*.gdb"],
    },
    
    # Metadata
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Debuggers",
        "Topic :: Software Development :: Embedded Systems",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    
    keywords="esp32 esp32c6 debugging openocd gdb jtag embedded wsl2",
    project_urls={
        "Bug Reports": "https://github.com/your-repo/esp32-debug-tools/issues",
        "Source": "https://github.com/your-repo/esp32-debug-tools",
        "Documentation": "https://github.com/your-repo/esp32-debug-tools/blob/main/ESP32_IDF_DEBUGGING_SIMPLIFIED.md",
    },
)