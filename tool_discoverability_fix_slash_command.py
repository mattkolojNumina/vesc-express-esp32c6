#!/usr/bin/env python3
"""
Tool Discoverability Fix Slash Command Implementation
====================================================

Implements the /tool-discoverability-fix slash command for Claude Code integration.
This command applies proven tool discovery patterns from the ESP32-C6 VESC Express
project to any specified tool, creating a comprehensive discovery ecosystem.

Author: Claude Code with ESP32 proven patterns
Date: 2025-07-24
"""

import asyncio
import json
import logging
import tempfile
import subprocess
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
import argparse
import shlex

# Setup logging for slash commands
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

class ToolDiscoverabilityFixSlashCommand:
    """
    Implements /tool-discoverability-fix slash command for Claude Code.
    
    Applies comprehensive tool discovery patterns to any specified tool using
    the proven methodologies from ESP32-C6 VESC Express project.
    """
    
    def __init__(self):
        self.command_name = "tool-discoverability-fix"
        self.description = "Apply comprehensive tool discovery patterns to any tool"
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Path to the enhancement script (adjust as needed for deployment)
        self.enhancer_script_path = Path(__file__).parent / "tool_discoverability_enhancer.py"
        
        self.usage = """
/tool-discoverability-fix <tool_name> [options]

Apply comprehensive tool discovery patterns using proven ESP32-C6 VESC Express methodologies.

Options:
  --full               Complete implementation (all patterns)
  --convenience-script Ultimate tool wrapper creation
  --analytics          Usage analytics and smart recommendations
  --slash-commands     Claude Code integration
  --docs               Documentation suite generation
  --recommendations    Smart recommendation system
  --validate           Test implementation and fix issues
  --target-directory   Target directory for enhancement (default: current)
  --dry-run           Show implementation plan without changes

Examples:
  /tool-discoverability-fix fastmcp --full
  /tool-discoverability-fix openocd --analytics --docs
  /tool-discoverability-fix npm --convenience-script --validate
  /tool-discoverability-fix docker --slash-commands --recommendations
"""
    
    async def execute(self, args: List[str]) -> Dict[str, Any]:
        """Execute the tool discoverability fix command"""
        
        self.logger.info(f"🎯 Executing tool-discoverability-fix with args: {args}")
        
        try:
            # Parse arguments
            parsed_args = self._parse_args(args)
            
            if parsed_args.get("help") or not parsed_args.get("tool_name"):
                return {
                    "success": True,
                    "result": self.get_help(),
                    "timestamp": datetime.now().isoformat()
                }
            
            # Execute enhancement workflow
            result = await self._run_enhancement_workflow(parsed_args)
            
            return {
                "success": result.get("success", False),
                "result": result,
                "command": self.command_name,
                "tool_name": parsed_args.get("tool_name"),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"❌ Tool discoverability fix failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "command": self.command_name,
                "timestamp": datetime.now().isoformat()
            }
    
    def _parse_args(self, args: List[str]) -> Dict[str, Any]:
        """Parse command line arguments"""
        
        # Create argument parser
        parser = argparse.ArgumentParser(
            description='Tool Discoverability Fix',
            add_help=False  # We'll handle help manually
        )
        
        parser.add_argument('tool_name', nargs='?', help='Name of the tool to enhance')
        parser.add_argument('--full', action='store_true', help='Complete implementation (all patterns)')
        parser.add_argument('--convenience-script', action='store_true', help='Ultimate tool wrapper creation')
        parser.add_argument('--analytics', action='store_true', help='Usage analytics and smart recommendations')
        parser.add_argument('--slash-commands', action='store_true', help='Claude Code integration')
        parser.add_argument('--docs', action='store_true', help='Documentation suite generation')
        parser.add_argument('--recommendations', action='store_true', help='Smart recommendation system')
        parser.add_argument('--validate', action='store_true', help='Test implementation and fix issues')
        parser.add_argument('--target-directory', default='.', help='Target directory for enhancement')
        parser.add_argument('--dry-run', action='store_true', help='Show implementation plan without changes')
        parser.add_argument('--help', action='store_true', help='Show help message')
        
        try:
            # Parse args manually to handle errors gracefully
            parsed = parser.parse_args(args)
            return vars(parsed)
        except SystemExit:
            # ArgumentParser calls sys.exit on error, catch and return help request
            return {"help": True}
        except Exception as e:
            self.logger.warning(f"Argument parsing error: {e}")
            return {"help": True}
    
    async def _run_enhancement_workflow(self, parsed_args: Dict[str, Any]) -> Dict[str, Any]:
        """Run the enhancement workflow using the tool_discoverability_enhancer.py script"""
        
        tool_name = parsed_args.get("tool_name")
        target_directory = parsed_args.get("target_directory", ".")
        
        self.logger.info(f"🚀 Running enhancement workflow for {tool_name} in {target_directory}")
        
        # Build command line arguments for the enhancer script
        cmd_args = [sys.executable, str(self.enhancer_script_path), tool_name]
        
        # Add target directory
        cmd_args.extend(["--target-directory", target_directory])
        
        # Add enhancement options
        if parsed_args.get("full"):
            cmd_args.append("--full")
        if parsed_args.get("convenience_script"):
            cmd_args.append("--convenience-script")
        if parsed_args.get("analytics"):
            cmd_args.append("--analytics")
        if parsed_args.get("slash_commands"):
            cmd_args.append("--slash-commands")
        if parsed_args.get("docs"):
            cmd_args.append("--docs")
        if parsed_args.get("recommendations"):
            cmd_args.append("--recommendations")
        if parsed_args.get("validate"):
            cmd_args.append("--validate")
        if parsed_args.get("dry_run"):
            cmd_args.append("--dry-run")
        
        try:
            # Run the enhancement script
            self.logger.debug(f"Executing: {' '.join(cmd_args)}")
            
            process = await asyncio.create_subprocess_exec(
                *cmd_args,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=target_directory
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                # Parse the JSON result from stdout (extract JSON from mixed output)
                try:
                    stdout_str = stdout.decode()
                    
                    # Find the JSON object in the output
                    # JSON should start with '{' and end with '}'
                    json_start = stdout_str.find('{')
                    json_end = stdout_str.rfind('}') + 1
                    
                    if json_start >= 0 and json_end > json_start:
                        json_str = stdout_str[json_start:json_end]
                        result = json.loads(json_str)
                        
                        # Enhance result with additional information
                        result.update({
                            "slash_command": self.command_name,
                            "execution_method": "enhancement_script",
                            "script_path": str(self.enhancer_script_path)
                        })
                        
                        self.logger.info(f"✅ Enhancement workflow completed successfully for {tool_name}")
                        return result
                    else:
                        # No JSON found, return the full output for debugging
                        return {
                            "success": False,
                            "error": "No JSON found in enhancement script output",
                            "stdout": stdout_str,
                            "stderr": stderr.decode()
                        }
                    
                except json.JSONDecodeError as e:
                    self.logger.error(f"Failed to parse enhancement script output: {e}")
                    return {
                        "success": False,
                        "error": f"Failed to parse enhancement output: {e}",
                        "stdout": stdout.decode(),
                        "stderr": stderr.decode()
                    }
            else:
                self.logger.error(f"Enhancement script failed with return code {process.returncode}")
                return {
                    "success": False,
                    "error": f"Enhancement script failed with return code {process.returncode}",
                    "stdout": stdout.decode(),
                    "stderr": stderr.decode()
                }
                
        except Exception as e:
            self.logger.error(f"Failed to execute enhancement script: {e}")
            return {
                "success": False,
                "error": f"Failed to execute enhancement script: {e}"
            }
    
    def get_help(self) -> str:
        """Get help text for the command"""
        return self.usage


# Slash command entry point for Claude Code integration
async def tool_discoverability_fix(*args) -> Dict[str, Any]:
    """
    Slash command: /tool-discoverability-fix
    
    Apply comprehensive tool discovery patterns to any specified tool using
    proven methodologies from ESP32-C6 VESC Express project.
    """
    handler = ToolDiscoverabilityFixSlashCommand()
    return await handler.execute(list(args))


# FastMCP server integration function
def register_tool_discoverability_fix_slash_command(mcp_server):
    """
    Register the tool-discoverability-fix slash command with FastMCP server.
    
    Args:
        mcp_server: The MCP server instance to register with
    """
    
    @mcp_server.tool
    async def tool_discoverability_fix(
        tool_name: str,
        full: bool = False,
        convenience_script: bool = False,
        analytics: bool = False,
        slash_commands: bool = False,
        docs: bool = False,
        recommendations: bool = False,
        validate: bool = False,
        target_directory: str = ".",
        dry_run: bool = False
    ) -> Dict[str, Any]:
        """
        Apply comprehensive tool discovery patterns to any specified tool.
        
        Uses proven methodologies from ESP32-C6 VESC Express project to create:
        - Convenience scripts with smart recommendations
        - Usage analytics and tracking
        - Claude Code slash command integration
        - Comprehensive documentation suite
        - Cross-platform compatibility
        - Team onboarding materials
        
        Args:
            tool_name: Name of the tool to enhance
            full: Complete implementation (all patterns)
            convenience_script: Ultimate tool wrapper creation
            analytics: Usage analytics and smart recommendations
            slash_commands: Claude Code integration
            docs: Documentation suite generation
            recommendations: Smart recommendation system
            validate: Test implementation and fix issues
            target_directory: Target directory for enhancement
            dry_run: Show implementation plan without changes
            
        Returns:
            Enhancement results with success metrics and created files
        """
        
        # Build arguments list
        args = [tool_name]
        
        if target_directory != ".":
            args.extend(["--target-directory", target_directory])
            
        if full:
            args.append("--full")
        if convenience_script:
            args.append("--convenience-script")
        if analytics:
            args.append("--analytics")
        if slash_commands:
            args.append("--slash-commands")
        if docs:
            args.append("--docs")
        if recommendations:
            args.append("--recommendations")
        if validate:
            args.append("--validate")
        if dry_run:
            args.append("--dry-run")
        
        # Execute the slash command
        return await tool_discoverability_fix(*args)


# CLI interface for direct execution and testing
async def main():
    """CLI interface for testing the slash command outside Claude Code."""
    if len(sys.argv) < 2:
        print("Usage: python tool_discoverability_fix_slash_command.py <tool_name> [options]")
        print("Example: python tool_discoverability_fix_slash_command.py fastmcp --full")
        return 1
    
    # Remove script name from args
    args = sys.argv[1:]
    
    # Execute slash command
    handler = ToolDiscoverabilityFixSlashCommand()
    result = await handler.execute(args)
    
    # Pretty print results
    print(json.dumps(result, indent=2))
    
    return 0 if result.get('success', False) else 1


if __name__ == '__main__':
    sys.exit(asyncio.run(main()))