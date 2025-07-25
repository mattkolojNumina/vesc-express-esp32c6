#!/usr/bin/env python3
"""
ESP32 Debug Tools CLI - Unified Command Interface
Uses Stevedore for automatic tool discovery and Click for CLI management
"""

import sys
import os
from pathlib import Path
from typing import Dict, Any, Optional

import click
from rich.console import Console
from rich.table import Table
from rich.text import Text
from rich import box

# Import stevedore for plugin discovery
try:
    from stevedore import extension, named
except ImportError:
    print("❌ stevedore not installed. Run: pip install stevedore")
    sys.exit(1)

console = Console()

class ESP32DebugToolsRegistry:
    """Registry for ESP32 debugging tools using Stevedore"""
    
    def __init__(self):
        self.tools_namespace = 'esp32_debug_tools'
        self.commands_namespace = 'esp32_debug_commands'
        self._tools_cache = None
        self._commands_cache = None

    def discover_tools(self) -> Dict[str, Any]:
        """Discover all available ESP32 debugging tools"""
        if self._tools_cache is not None:
            return self._tools_cache
            
        try:
            mgr = extension.ExtensionManager(
                namespace=self.tools_namespace,
                invoke_on_load=True
            )
            
            tools = {}
            for ext in mgr.extensions:
                try:
                    # Get tool instance and metadata
                    tool_instance = ext.obj
                    tools[ext.name] = {
                        'name': ext.name,
                        'class': tool_instance.__class__,
                        'instance': tool_instance,
                        'description': (getattr(tool_instance.__class__, '__doc__', 'No description available') or 'No description available').strip(),
                        'module': tool_instance.__class__.__module__,
                        'entry_point': ext.entry_point
                    }
                except Exception as e:
                    console.print(f"⚠️  Failed to load tool {ext.name}: {e}", style="yellow")
                    
            self._tools_cache = tools
            return tools
            
        except Exception as e:
            console.print(f"❌ Failed to discover tools: {e}", style="red")
            return {}

    def discover_commands(self) -> Dict[str, Any]:
        """Discover all available CLI commands"""
        if self._commands_cache is not None:
            return self._commands_cache
            
        try:
            mgr = extension.ExtensionManager(
                namespace=self.commands_namespace,
                invoke_on_load=True
            )
            
            commands = {}
            for ext in mgr.extensions:
                try:
                    command_obj = ext.obj
                    # Handle both function callables and returned objects from cli_main
                    if callable(command_obj):
                        # It's a function
                        func_name = getattr(command_obj, '__name__', str(command_obj))
                        description = getattr(command_obj, '__doc__', 'No description available') or 'No description available'
                        module = getattr(command_obj, '__module__', 'unknown')
                    else:
                        # It's an object returned by cli_main - get info from its class
                        func_name = command_obj.__class__.__name__
                        description = getattr(command_obj.__class__, '__doc__', 'No description available') or 'No description available'
                        module = command_obj.__class__.__module__
                    
                    commands[ext.name] = {
                        'name': ext.name,
                        'function': command_obj,
                        'description': description.strip(),
                        'module': module,
                        'entry_point': ext.entry_point,
                        'function_name': func_name
                    }
                except Exception as e:
                    console.print(f"⚠️  Failed to load command {ext.name}: {e}", style="yellow")
                    
            self._commands_cache = commands
            return commands
            
        except Exception as e:
            console.print(f"❌ Failed to discover commands: {e}", style="red")
            return {}

    def get_tool(self, tool_name: str) -> Optional[Any]:
        """Get a specific tool by name"""
        tools = self.discover_tools()
        if tool_name in tools:
            return tools[tool_name]['instance']
        return None

    def get_command(self, command_name: str) -> Optional[Any]:
        """Get a specific command by name"""
        commands = self.discover_commands()
        if command_name in commands:
            return commands[command_name]['function']
        return None

# Global registry instance
registry = ESP32DebugToolsRegistry()

@click.group(invoke_without_command=True)
@click.option('--list', 'list_tools', is_flag=True, help='List all available tools')
@click.option('--verbose', '-v', is_flag=True, help='Verbose output')
@click.pass_context
def cli(ctx, list_tools, verbose):
    """
    ESP32-C6 Debugging Tools Suite - Unified CLI Interface
    
    Automatically discovers and provides access to all ESP32 debugging tools.
    """
    ctx.ensure_object(dict)
    ctx.obj['verbose'] = verbose
    
    if ctx.invoked_subcommand is None:
        if list_tools:
            show_available_tools()
        else:
            console.print("\n🔧 ESP32-C6 Debugging Tools Suite", style="bold blue")
            console.print("Use --help to see available commands or --list to see all tools")
            console.print("\n💡 Quick start: esp32-debug wizard")

def show_available_tools():
    """Display all discovered tools in a nice table"""
    tools = registry.discover_tools()
    commands = registry.discover_commands()
    
    if not tools and not commands:
        console.print("❌ No tools discovered. Run 'pip install -e .' to register tools.", style="red")
        return
    
    # Tools table
    if tools:
        console.print("\n📋 Available Debug Tools:", style="bold green")
        table = Table(box=box.ROUNDED, show_header=True, header_style="bold magenta")
        table.add_column("Tool", style="cyan", no_wrap=True)
        table.add_column("Description", style="white")
        table.add_column("Module", style="dim")
        
        for tool_name, tool_info in sorted(tools.items()):
            description = tool_info['description'].split('\n')[0] if tool_info['description'] else 'No description'
            table.add_row(
                tool_name,
                description[:80] + "..." if len(description) > 80 else description,
                tool_info['module']
            )
        
        console.print(table)
    
    # Commands table
    if commands:
        console.print("\n⚡ Available CLI Commands:", style="bold green")
        table = Table(box=box.ROUNDED, show_header=True, header_style="bold magenta")
        table.add_column("Command", style="cyan", no_wrap=True)
        table.add_column("Description", style="white")
        table.add_column("Usage", style="dim")
        
        for cmd_name, cmd_info in sorted(commands.items()):
            description = cmd_info['description'].split('\n')[0] if cmd_info['description'] else 'No description'
            table.add_row(
                cmd_name,
                description[:60] + "..." if len(description) > 60 else description,
                f"esp32-debug {cmd_name.replace('_', '-')}"
            )
        
        console.print(table)

@cli.command()
@click.option('--profile', default='basic', help='Debug profile to use')
@click.option('--interactive', is_flag=True, help='Interactive mode')
def wizard(profile, interactive):
    """Run the unified debugging wizard"""
    console.print("🧙 Starting ESP32-C6 Debug Wizard...", style="bold blue")
    
    # Get unified debugger tool
    unified_debugger = registry.get_tool('unified_debugger')
    if unified_debugger:
        if interactive:
            unified_debugger.interactive_debug_menu()
        else:
            unified_debugger.quick_start_wizard()
    else:
        console.print("❌ Unified debugger not found. Install tools with 'pip install -e .'", style="red")

@cli.command(name='setup-openocd')
@click.option('--config', default='optimized', help='OpenOCD configuration type')
@click.option('--test', is_flag=True, help='Test connection after setup')
def setup_openocd(config, test):
    """Setup ESP32-C6 OpenOCD configuration"""
    console.print("🔧 Setting up OpenOCD configuration...", style="blue")
    
    openocd_setup = registry.get_tool('openocd_setup')
    if openocd_setup:
        success = openocd_setup.run_full_setup(config, test_connection=test)
        if success:
            console.print("✅ OpenOCD setup completed successfully!", style="green")
        else:
            console.print("❌ OpenOCD setup failed", style="red")
    else:
        console.print("❌ OpenOCD setup tool not found", style="red")

@cli.command(name='gdb-debug')
@click.option('--profile', default='basic', help='Debug profile')
@click.option('--create-profiles', is_flag=True, help='Create all debug profiles')
def gdb_debug(profile, create_profiles):
    """Run GDB debugging session"""
    console.print(f"🐛 Starting GDB debug session: {profile}", style="blue")
    
    gdb_automation = registry.get_tool('gdb_automation')
    if gdb_automation:
        if create_profiles:
            gdb_automation.create_debug_profiles()
            console.print("✅ Debug profiles created", style="green")
        else:
            success = gdb_automation.run_interactive_debug(profile)
            if success:
                console.print("✅ Debug session completed", style="green")
            else:
                console.print("❌ Debug session failed", style="red")
    else:
        console.print("❌ GDB automation tool not found", style="red")

@cli.command(name='memory-analyze')
@click.option('--report', is_flag=True, help='Generate memory report')
@click.option('--fragmentation', is_flag=True, help='Analyze memory fragmentation')
def memory_analyze(report, fragmentation):
    """Analyze ESP32-C6 memory usage"""
    console.print("🧠 Analyzing memory usage...", style="blue")
    
    memory_debugger = registry.get_tool('memory_debug')
    if memory_debugger:
        if fragmentation:
            memory_debugger.analyze_memory_fragmentation()
        elif report:
            report_path = memory_debugger.generate_memory_report()
            console.print(f"✅ Memory report generated: {report_path}", style="green")
        else:
            memory_debugger.analyze_memory_layout()
            memory_debugger.analyze_stack_usage()
    else:
        console.print("❌ Memory debugger tool not found", style="red")

@cli.command(name='setup-wsl2')
@click.option('--verify', is_flag=True, help='Verify setup only')
def setup_wsl2(verify):
    """Setup WSL2 environment for ESP32 debugging"""
    console.print("🐧 Setting up WSL2 environment...", style="blue")
    
    wsl2_setup = registry.get_tool('wsl2_setup')
    if wsl2_setup:
        if verify:
            success = wsl2_setup.verify_wsl_device_access()
            if success:
                console.print("✅ WSL2 setup verified", style="green")
            else:
                console.print("❌ WSL2 setup verification failed", style="red")
        else:
            success = wsl2_setup.run_full_setup()
            if success:
                console.print("✅ WSL2 setup completed", style="green")
            else:
                console.print("❌ WSL2 setup failed", style="red")
    else:
        console.print("❌ WSL2 setup tool not found", style="red")

@cli.command()
@click.argument('tool_name')
@click.argument('args', nargs=-1)
def run(tool_name, args):
    """Run a specific tool by name with arguments"""
    console.print(f"🚀 Running tool: {tool_name}", style="blue")
    
    # Try to get tool from registry
    tool = registry.get_tool(tool_name)
    if tool:
        try:
            # Attempt to call main method with args
            if hasattr(tool, 'main'):
                tool.main(list(args))
            elif hasattr(tool, '__call__'):
                tool(*args)
            else:
                console.print(f"⚠️  Tool {tool_name} has no callable interface", style="yellow")
        except Exception as e:
            console.print(f"❌ Tool execution failed: {e}", style="red")
    else:
        console.print(f"❌ Tool {tool_name} not found", style="red")

@cli.command()
def info():
    """Show detailed information about the tools suite"""
    console.print("\n🔧 ESP32-C6 Debugging Tools Suite", style="bold blue")
    console.print("=" * 50)
    
    tools = registry.discover_tools()
    commands = registry.discover_commands()
    
    console.print(f"📊 Statistics:", style="bold green")
    console.print(f"   • Tools discovered: {len(tools)}")
    console.print(f"   • Commands available: {len(commands)}")
    console.print(f"   • Namespaces: {registry.tools_namespace}, {registry.commands_namespace}")
    
    # Check environment
    console.print(f"\n🌍 Environment:", style="bold green")
    console.print(f"   • Python: {sys.version.split()[0]}")
    console.print(f"   • Working directory: {os.getcwd()}")
    console.print(f"   • Tools path: {Path(__file__).parent}")
    
    # Show example usage
    console.print(f"\n💡 Quick Examples:", style="bold green")
    console.print("   esp32-debug wizard                    # Interactive setup wizard")
    console.print("   esp32-debug setup-openocd --test      # Setup and test OpenOCD")
    console.print("   esp32-debug gdb-debug --profile crash # Debug crashes")
    console.print("   esp32-debug memory-analyze --report   # Memory analysis")
    console.print("   esp32-debug --list                    # List all tools")

def main():
    """Main entry point for CLI"""
    try:
        cli()
    except KeyboardInterrupt:
        console.print("\n\n👋 Interrupted by user", style="yellow")
        sys.exit(130)
    except Exception as e:
        console.print(f"\n❌ Unexpected error: {e}", style="red")
        sys.exit(1)

if __name__ == '__main__':
    main()