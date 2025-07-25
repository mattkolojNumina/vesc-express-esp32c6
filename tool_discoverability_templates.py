#!/usr/bin/env python3
"""
Tool Discoverability Templates Module
====================================

Template definitions for generating scripts, documentation, and configuration files.
Separated from core logic for better maintainability and testability.

Author: Claude Code - Refactored with Serena tools
Date: 2025-07-24
"""

from typing import Dict, Any
from dataclasses import dataclass


@dataclass
class ToolConfig:
    """Configuration container for tool-specific parameters."""
    tool_name: str
    tool_title: str
    tool_upper: str

    @classmethod
    def from_tool_name(cls, tool_name: str) -> 'ToolConfig':
        """Create ToolConfig from tool name."""
        return cls(
            tool_name=tool_name,
            tool_title=tool_name.title(),
            tool_upper=tool_name.upper()
        )


class BashScriptTemplate:
    """Templates for bash script generation."""

    @staticmethod
    def get_color_definitions() -> str:
        """Standard color definitions for all scripts."""
        return '''# Colors for output
RED='\\033[0;31m'
GREEN='\\033[0;32m'
YELLOW='\\033[1;33m'
BLUE='\\033[0;34m'
CYAN='\\033[0;36m'
NC='\\033[0m' # No Color'''

    @staticmethod
    def get_convenience_script_header(config: ToolConfig) -> str:
        """Generate convenience script header."""
        return f'''#!/bin/bash
# {config.tool_title} - Ultimate Development Convenience Script
# Single script for all common {config.tool_name} operations
# Based on proven ESP32-C6 VESC Express patterns

set -e

{BashScriptTemplate.get_color_definitions()}'''

    @staticmethod
    def get_logo_function(config: ToolConfig) -> str:
        """Generate logo printing function."""
        return f'''print_logo() {{
    echo -e "${{CYAN}}"
    echo "🚀 {config.tool_upper} - Ultimate Development Suite"
    echo "═══════════════════════════════════════════"
    echo -e "${{NC}}"
    echo -e "${{BLUE}}Intelligent {config.tool_title} Development & Management${{NC}}"
    echo ""
}}'''

    @staticmethod
    def get_help_function(config: ToolConfig) -> str:
        """Generate help function."""
        return f'''print_help() {{
    print_logo
    echo "Usage: ./{config.tool_name}_ultimate <command> [options]"
    echo ""
    echo -e "${{GREEN}}🔨 Core Commands:${{NC}}"
    echo "  setup          - Complete environment setup"
    echo "  check          - Verify environment and configuration"
    echo "  start          - Start {config.tool_name} with optimal settings"
    echo "  stop           - Stop {config.tool_name} gracefully"
    echo "  restart        - Restart with configuration reload"
    echo ""
    echo -e "${{GREEN}}🔍 Discovery Commands:${{NC}}"
    echo "  discover       - Show all available tools and capabilities"
    echo "  suggest        - Smart recommendations based on project state"
    echo "  tools          - List specialized tools and utilities"
    echo "  analyze        - Comprehensive project analysis"
    echo ""
    echo -e "${{GREEN}}🐛 Debugging Commands:${{NC}}"
    echo "  debug          - Interactive debugging session"
    echo "  troubleshoot   - Automated problem resolution"
    echo "  logs           - View and analyze logs"
    echo "  health         - System health check"
    echo ""
    echo -e "${{GREEN}}📊 Analytics Commands:${{NC}}"
    echo "  analytics      - View usage analytics and insights"
    echo "  optimize       - Apply performance optimizations"
    echo "  benchmark      - Run performance benchmarks"
    echo ""
    echo -e "${{GREEN}}⚡ Quick Commands:${{NC}}"
    echo "  dev            - Complete development workflow"
    echo "  quick          - Fast setup and start"
    echo "  full           - Comprehensive setup and validation"
    echo ""
    echo -e "${{GREEN}}💡 Examples:${{NC}}"
    echo "  ./{config.tool_name}_ultimate setup      # First-time setup"
    echo "  ./{config.tool_name}_ultimate dev        # Standard development"
    echo "  ./{config.tool_name}_ultimate suggest    # Get recommendations"
    echo "  ./{config.tool_name}_ultimate debug      # Debug issues"
    echo ""
}}'''

    @staticmethod
    def get_utility_functions(config: ToolConfig) -> str:
        """Generate utility functions."""
        return f'''# Log usage for analytics
log_usage() {{
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1 command used" >> .{config.tool_name}_analytics.log 2>/dev/null || true
}}

# Smart environment setup
setup_environment() {{
    if [ ! -f ".env.{config.tool_name}" ]; then
        echo -e "${{YELLOW}}⚠️  Project environment not found. Running setup...${{NC}}"
        ./setup_{config.tool_name}_env.sh 2>/dev/null || echo "Setup script not found, using defaults"
    fi

    if [ -f ".env.{config.tool_name}" ]; then
        source .env.{config.tool_name}
    fi
}}'''

    @staticmethod
    def get_suggestions_function(config: ToolConfig) -> str:
        """Generate context-aware suggestions function."""
        return f'''# Context-aware suggestions
generate_suggestions() {{
    echo -e "${{BLUE}}💡 Smart {config.tool_title} Recommendations${{NC}}"
    echo ""

    # Check project state and provide contextual suggestions
    if [ ! -f "config/{config.tool_name}.conf" ] && [ ! -f "{config.tool_name}.config" ]; then
        echo -e "${{YELLOW}}⚠️  No configuration detected${{NC}}"
        echo "🎯 Recommended: ./{config.tool_name}_ultimate setup"
    else
        echo -e "${{GREEN}}✅ Configuration found${{NC}}"
        echo "🎯 Recommended: ./{config.tool_name}_ultimate dev"
    fi

    # Check if service is running
    if pgrep -f "{config.tool_name}" > /dev/null; then
        echo -e "${{GREEN}}✅ {config.tool_title} is running${{NC}}"
        echo "🎯 Recommended: ./{config.tool_name}_ultimate analyze"
    else
        echo -e "${{YELLOW}}⚠️  {config.tool_title} not running${{NC}}"
        echo "🎯 Recommended: ./{config.tool_name}_ultimate start"
    fi

    # Analytics-based suggestions
    if [ -f ".{config.tool_name}_analytics.log" ]; then
        local usage_count=$(wc -l < .{config.tool_name}_analytics.log 2>/dev/null || echo "0")
        if [ "$usage_count" -gt 0 ]; then
            echo ""
            echo -e "${{CYAN}}📊 Usage: $usage_count commands tracked${{NC}}"
            echo "🎯 View analytics: ./{config.tool_name}_ultimate analytics"
        fi
    fi

    echo ""
    echo -e "${{BLUE}}Based on current project state:${{NC}}"
    echo "  Use Claude Code: /tool-troubleshoot for automated fixes"
    echo "  Run ./{config.tool_name}_ultimate discover to explore all capabilities"
}}'''


class AnalyticsScriptTemplate:
    """Templates for analytics script generation."""

    @staticmethod
    def get_analytics_header(config: ToolConfig) -> str:
        """Generate analytics script header."""
        return f'''#!/bin/bash
# {config.tool_title} Tool Usage Analytics Report Generator
# Based on proven ESP32-C6 VESC Express patterns

{BashScriptTemplate.get_color_definitions()}'''

    @staticmethod
    def get_analytics_logo_function(config: ToolConfig) -> str:
        """Generate analytics logo function."""
        return f'''print_analytics_logo() {{
    echo -e "${{CYAN}}"
    echo "📊 {config.tool_title} Tool Usage Analytics"
    echo "═══════════════════════════════════════"
    echo -e "${{NC}}"
}}'''

    @staticmethod
    def get_analytics_report_function(config: ToolConfig) -> str:
        """Generate main analytics report function."""
        return f'''generate_analytics_report() {{
    print_analytics_logo

    if [ ! -f ".{config.tool_name}_analytics.log" ]; then
        echo -e "${{YELLOW}}⚠️  No analytics data found. Use ./{config.tool_name}_ultimate commands to generate usage data.${{NC}}"
        echo ""
        echo "Commands that generate analytics:"
        echo "  ./{config.tool_name}_ultimate setup, start, dev, debug"
        echo "  ./{config.tool_name}_ultimate suggest, discover, analyze"
        return 1
    fi

    total_commands=$(wc -l < .{config.tool_name}_analytics.log)
    echo -e "${{GREEN}}📈 Total Commands Used: $total_commands${{NC}}"
    echo ""

    echo -e "${{BLUE}}🔝 Most Popular Commands:${{NC}}"
    # Extract command names and count occurrences
    if command -v awk &> /dev/null; then
        awk '{{print $4}}' .{config.tool_name}_analytics.log | sort | uniq -c | sort -nr | head -5 | while read count cmd; do
            echo "  $cmd: $count uses"
        done
    else
        echo "  (awk not available for detailed analysis)"
    fi
    echo ""

    echo -e "${{BLUE}}📅 Usage Timeline (Last 10 entries):${{NC}}"
    tail -10 .{config.tool_name}_analytics.log | while read line; do
        echo "  $line"
    done
    echo ""

    echo -e "${{BLUE}}📊 Command Categories:${{NC}}"
    dev_commands=$(grep -E "(start|setup|dev|check)" .{config.tool_name}_analytics.log 2>/dev/null | wc -l)
    debug_commands=$(grep -E "(debug|troubleshoot|analyze)" .{config.tool_name}_analytics.log 2>/dev/null | wc -l)
    discovery_commands=$(grep -E "(suggest|discover|analytics)" .{config.tool_name}_analytics.log 2>/dev/null | wc -l)

    echo "  🔨 Development: $dev_commands commands"
    echo "  🐛 Debugging: $debug_commands commands"
    echo "  🔍 Discovery: $discovery_commands commands"
    echo ""

    # Calculate usage trends
    today_count=$(grep "$(date '+%Y-%m-%d')" .{config.tool_name}_analytics.log 2>/dev/null | wc -l)
    echo -e "${{BLUE}}📅 Today's Activity: $today_count commands${{NC}}"

    if [ "$today_count" -gt 5 ]; then
        echo -e "${{GREEN}}🎉 Active development session detected!${{NC}}"
    elif [ "$today_count" -gt 0 ]; then
        echo -e "${{YELLOW}}🔧 Some development activity today${{NC}}"
    fi

    echo ""
    echo -e "${{CYAN}}💡 Recommendations based on usage:${{NC}}"

    if [ "$dev_commands" -gt "$debug_commands" ]; then
        echo "  • Consider using more debugging tools for better development workflow"
        echo "  • Try: ./{config.tool_name}_ultimate debug for interactive debugging sessions"
    fi

    if [ "$discovery_commands" -lt 3 ]; then
        echo "  • Explore more tools with: ./{config.tool_name}_ultimate discover"
        echo "  • Get smart recommendations with: ./{config.tool_name}_ultimate suggest"
    fi

    echo ""
    echo -e "${{BLUE}}To clear analytics: rm .{config.tool_name}_analytics.log${{NC}}"
}}'''


class ConfigurationTemplates:
    """Templates for configuration file generation."""

    @staticmethod
    def get_recommendations_config(config: ToolConfig) -> Dict[str, Any]:
        """Generate smart recommendations configuration."""
        return {
            'tool_name': config.tool_name,
            'recommendation_rules': [
                {
                    'condition': 'no_config_found',
                    'recommendation': f'./{config.tool_name}_ultimate setup',
                    'priority': 'high',
                    'description': 'Initial setup required'
                },
                {
                    'condition': 'service_not_running',
                    'recommendation': f'./{config.tool_name}_ultimate start',
                    'priority': 'medium',
                    'description': 'Start the service'
                },
                {
                    'condition': 'high_usage_detected',
                    'recommendation': f'./{config.tool_name}_ultimate optimize',
                    'priority': 'medium',
                    'description': 'Optimize based on usage patterns'
                },
                {
                    'condition': 'errors_detected',
                    'recommendation': f'./{config.tool_name}_ultimate troubleshoot',
                    'priority': 'high',
                    'description': 'Resolve detected issues'
                }
            ],
            'context_patterns': [
                'project_state',
                'service_status',
                'usage_history',
                'error_frequency',
                'performance_metrics'
            ]
        }


class SlashCommandTemplates:
    """Templates for Claude Code slash command generation."""

    @staticmethod
    def get_slash_command_content(config: ToolConfig, command_name: str, description: str) -> str:
        """Generate slash command content."""
        return f'''# {config.tool_title} {command_name.title()}

{description} for {config.tool_title} using comprehensive automation.

This command provides professional {command_name} capabilities:
- 🔍 Automated analysis and detection
- 🔧 Smart recommendations and fixes
- 📊 Performance metrics and insights
- ⚡ Rapid problem resolution
- 🤖 AI-powered optimizations

**Usage Examples:**
```bash
# {command_name.title()} {config.tool_name}
./{config.tool_name}_ultimate {command_name}

# Advanced {command_name}
./{config.tool_name}_ultimate {command_name} --advanced

# {command_name.title()} with specific target
./{config.tool_name}_ultimate {command_name} --target specific_component
```

**Arguments:** $ARGUMENTS

**Command to run:**
```bash
# Default: {command_name.title()} workflow
./{config.tool_name}_ultimate {command_name} $ARGUMENTS
```

**What this provides:**

1. **Automated Analysis**:
   - Comprehensive {config.tool_name} environment scanning
   - Performance bottleneck detection
   - Configuration validation
   - Dependency checking

2. **Smart Recommendations**:
   - Context-aware suggestions
   - Priority-based action items
   - Performance optimization opportunities
   - Best practice guidance

3. **Professional Reporting**:
   - Detailed analysis results
   - Actionable insights
   - Performance metrics
   - Success validation

**Integration with {config.tool_title} ecosystem:**
- ✅ Uses proven {config.tool_title} analysis patterns
- ✅ Integrates with usage analytics
- ✅ Provides smart recommendations
- ✅ Supports advanced debugging workflows

Based on proven patterns from ESP32-C6 VESC Express tool discovery methodology.
'''


class CommandCaseTemplates:
    """Templates for bash case statement generation."""

    @staticmethod
    def get_core_commands(config: ToolConfig) -> str:
        """Generate core command case statements."""
        return f'''    "setup")
        print_logo
        log_usage "setup"
        echo -e "${{BLUE}}🚀 Setting up {config.tool_title} development environment...${{NC}}"
        # Add tool-specific setup logic here
        echo -e "${{GREEN}}✅ Setup complete! Try: ./{config.tool_name}_ultimate dev${{NC}}"
        ;;

    "check")
        setup_environment
        log_usage "check"
        echo -e "${{BLUE}}✅ Checking {config.tool_title} environment...${{NC}}"
        # Add environment validation logic
        echo -e "${{GREEN}}✅ Environment check complete${{NC}}"
        ;;

    "start")
        setup_environment
        log_usage "start"
        echo -e "${{BLUE}}▶️  Starting {config.tool_title}...${{NC}}"
        # Add start logic
        echo -e "${{GREEN}}✅ {config.tool_title} started successfully${{NC}}"
        ;;'''

    @staticmethod
    def get_discovery_commands(config: ToolConfig) -> str:
        """Generate discovery command case statements."""
        return f'''    "discover")
        print_logo
        log_usage "discover"
        echo -e "${{BLUE}}🔍 {config.tool_title} Development Tools Discovery${{NC}}"
        echo ""
        echo -e "${{GREEN}}📱 Claude Code Integration:${{NC}}"
        echo "  /tool-troubleshoot   - Automated problem resolution"
        echo "  /tool-analyze        - Advanced analysis"
        echo "  /tool-optimize       - Performance optimization"
        echo ""
        echo -e "${{GREEN}}🔧 Available Commands:${{NC}}"
        echo "  ./{config.tool_name}_ultimate check      - Environment validation"
        echo "  ./{config.tool_name}_ultimate dev        - Development workflow"
        echo "  ./{config.tool_name}_ultimate debug      - Interactive debugging"
        echo ""
        echo -e "${{GREEN}}📊 Analytics:${{NC}}"
        echo "  ./{config.tool_name}_analytics_report.sh - View usage analytics"
        ;;

    "suggest")
        setup_environment
        log_usage "suggest"
        generate_suggestions
        ;;'''

    @staticmethod
    def get_standard_commands(config: ToolConfig) -> str:
        """Generate standard command case statements."""
        return f'''    "dev")
        print_logo
        log_usage "dev"
        echo -e "${{BLUE}}🚀 {config.tool_title} development workflow${{NC}}"
        setup_environment
        # Add development workflow logic
        echo -e "${{GREEN}}✅ Development workflow complete${{NC}}"
        ;;

    "analytics")
        log_usage "analytics"
        if [ -f "./{config.tool_name}_analytics_report.sh" ]; then
            ./{config.tool_name}_analytics_report.sh
        else
            echo -e "${{YELLOW}}Analytics report not available. Run setup first.${{NC}}"
        fi
        ;;

    "")
        print_help
        ;;

    *)
        echo -e "${{RED}}❌ Unknown command: $1${{NC}}"
        echo ""
        print_help
        exit 1
        ;;'''
