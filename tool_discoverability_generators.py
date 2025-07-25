#!/usr/bin/env python3
"""
Tool Discoverability Generators Module
======================================

Specialized generators for creating scripts and configuration files.
This module uses templates to create consistent, maintainable outputs.

Author: Claude Code - Refactored with Serena tools
Date: 2025-07-24
"""

from typing import Dict, Any, List, Tuple

from tool_discoverability_templates import (
    ToolConfig,
    BashScriptTemplate,
    AnalyticsScriptTemplate,
    ConfigurationTemplates,
    SlashCommandTemplates,
    CommandCaseTemplates
)


class ScriptGenerator:
    """Generates bash scripts using modular templates."""

    def __init__(self, config: ToolConfig):
        """Initialize generator with tool configuration."""
        self.config = config

    def generate_convenience_script(self) -> str:
        """Generate complete convenience script."""
        sections = [
            BashScriptTemplate.get_convenience_script_header(self.config),
            "",
            BashScriptTemplate.get_logo_function(self.config),
            "",
            BashScriptTemplate.get_help_function(self.config),
            "",
            BashScriptTemplate.get_utility_functions(self.config),
            "",
            BashScriptTemplate.get_suggestions_function(self.config),
            "",
            self._generate_case_statement(),
            ""
        ]

        return "\n".join(sections)

    def generate_analytics_script(self) -> str:
        """Generate analytics reporting script."""
        sections = [
            AnalyticsScriptTemplate.get_analytics_header(self.config),
            "",
            AnalyticsScriptTemplate.get_analytics_logo_function(self.config),
            "",
            AnalyticsScriptTemplate.get_analytics_report_function(self.config),
            "",
            self._generate_analytics_case_statement(),
            ""
        ]

        return "\n".join(sections)

    def _generate_case_statement(self) -> str:
        """Generate main case statement for convenience script."""
        case_parts = [
            'case "$1" in',
            CommandCaseTemplates.get_core_commands(self.config),
            CommandCaseTemplates.get_discovery_commands(self.config),
            CommandCaseTemplates.get_standard_commands(self.config),
            'esac'
        ]

        return "\n".join(case_parts)

    def _generate_analytics_case_statement(self) -> str:
        """Generate case statement for analytics script."""
        return f'''case "$1" in
    "clear")
        if [ -f ".{self.config.tool_name}_analytics.log" ]; then
            rm .{self.config.tool_name}_analytics.log
            echo -e "${{GREEN}}✅ Analytics data cleared${{NC}}"
        else
            echo -e "${{YELLOW}}No analytics data to clear${{NC}}"
        fi
        ;;
    "export")
        if [ -f ".{self.config.tool_name}_analytics.log" ]; then
            export_file="{self.config.tool_name}_analytics_$(date '+%Y%m%d_%H%M%S').log"
            cp .{self.config.tool_name}_analytics.log "$export_file"
            echo -e "${{GREEN}}✅ Analytics exported to: $export_file${{NC}}"
        else
            echo -e "${{YELLOW}}No analytics data to export${{NC}}"
        fi
        ;;
    *)
        generate_analytics_report
        ;;
esac'''


class ConfigurationGenerator:
    """Generates configuration files using templates."""

    def __init__(self, config: ToolConfig):
        """Initialize generator with tool configuration."""
        self.config = config

    def generate_recommendations_config(self) -> Dict[str, Any]:
        """Generate smart recommendations configuration."""
        return ConfigurationTemplates.get_recommendations_config(self.config)


class SlashCommandGenerator:
    """Generates Claude Code slash commands."""

    def __init__(self, config: ToolConfig):
        """Initialize generator with tool configuration."""
        self.config = config

    def get_default_commands(self) -> List[Tuple[str, str]]:
        """Get default slash commands to create."""
        return [
            ('troubleshoot', 'Comprehensive troubleshooting and automated fixes'),
            ('analyze', 'Advanced analysis and insights'),
            ('optimize', 'Performance optimization and tuning'),
            ('discover', 'Tool exploration and discovery'),
            ('debug', 'Interactive debugging and diagnostics')
        ]

    def generate_slash_command_content(self, command_name: str, description: str) -> str:
        """Generate individual slash command content."""
        return SlashCommandTemplates.get_slash_command_content(
            self.config, command_name, description
        )


class DocumentationGenerator:
    """Generates documentation files using templates."""

    def __init__(self, config: ToolConfig):
        """Initialize generator with tool configuration."""
        self.config = config

    def generate_team_onboarding_doc(self) -> str:
        """Generate team onboarding documentation."""
        return f'''# {self.config.tool_title} Team Onboarding Guide

Welcome to the {self.config.tool_title} development team! This guide will get you up and running with our comprehensive tool discovery ecosystem.

## 🚀 Quick Start (5 Minutes)

### 1. Initial Setup
```bash
# Clone/navigate to the project
cd {self.config.tool_name}_project

# Run automated setup
./{self.config.tool_name}_ultimate setup

# Verify everything works
./{self.config.tool_name}_ultimate check
```

### 2. First Development Cycle
```bash
# Complete development workflow
./{self.config.tool_name}_ultimate dev
```

That's it! You're now developing with {self.config.tool_title}.

## 📋 Development Environment Overview

### Core Components
- **{self.config.tool_title} Core**: Main functionality and services
- **Discovery Ecosystem**: Comprehensive tool discovery and analytics
- **Claude Code Integration**: AI-powered development assistance
- **Analytics System**: Usage tracking and optimization insights

### Available Tools
- **{self.config.tool_name}_ultimate**: Ultimate convenience script (15+ commands)
- **Analytics Reports**: Usage insights and recommendations
- **Slash Commands**: Claude Code integration
- **Documentation Suite**: Complete reference materials

## 🛠️ Essential Commands

### Development Workflow
```bash
./{self.config.tool_name}_ultimate dev       # Complete development cycle
./{self.config.tool_name}_ultimate setup     # Initial environment setup
./{self.config.tool_name}_ultimate start     # Start services
./{self.config.tool_name}_ultimate check     # Environment validation
```

### Discovery & Analytics
```bash
./{self.config.tool_name}_ultimate discover  # Show all available capabilities
./{self.config.tool_name}_ultimate suggest   # Smart recommendations
./{self.config.tool_name}_ultimate analytics # View usage analytics
./{self.config.tool_name}_analytics_report.sh # Detailed analytics report
```

### Debugging & Troubleshooting
```bash
./{self.config.tool_name}_ultimate debug       # Interactive debugging
./{self.config.tool_name}_ultimate troubleshoot # Automated problem resolution
./{self.config.tool_name}_ultimate health       # System health check
```

## 🎯 Claude Code Integration

### Slash Commands (Type `/` in Claude Code)
- `/{self.config.tool_name}-troubleshoot` - Comprehensive troubleshooting
- `/{self.config.tool_name}-analyze` - Advanced analysis
- `/{self.config.tool_name}-optimize` - Performance optimization
- `/{self.config.tool_name}-discover` - Tool exploration
- `/{self.config.tool_name}-debug` - Interactive debugging

## 📊 Analytics & Optimization

### Usage Analytics
```bash
./{self.config.tool_name}_analytics_report.sh     # View detailed report
./{self.config.tool_name}_analytics_report.sh export  # Export data
./{self.config.tool_name}_analytics_report.sh clear   # Clear data
```

### Performance Monitoring
- Smart recommendations based on usage patterns
- Context-aware suggestions
- Performance optimization insights
- Error tracking and resolution

## 🔧 Best Practices

### Development Workflow
1. Always run `./{self.config.tool_name}_ultimate check` before starting
2. Use `./{self.config.tool_name}_ultimate suggest` for context-aware recommendations
3. Monitor analytics to optimize your workflow
4. Leverage Claude Code slash commands for complex tasks

### Team Collaboration
- Share analytics insights to improve team workflows
- Document new patterns in the discovery system
- Use consistent naming conventions
- Leverage cross-platform compatibility guidelines

## 💡 Tips for New Team Members

### Day 1 Checklist
- [ ] Complete initial setup: `./{self.config.tool_name}_ultimate setup`
- [ ] Verify environment: `./{self.config.tool_name}_ultimate check`
- [ ] Explore capabilities: `./{self.config.tool_name}_ultimate discover`
- [ ] Try Claude integration: `/{self.config.tool_name}-troubleshoot`

### Advanced Features
- Customize analytics tracking for personal insights
- Create custom slash commands for team-specific workflows
- Contribute to the discovery system documentation
- Share optimization patterns with the team

---

**Welcome to the team! This environment provides world-class {self.config.tool_title} development with comprehensive tool discovery. Happy coding! 🚀**
'''

    def generate_discovery_guide_doc(self) -> str:
        """Generate tool discovery guide documentation."""
        return f'''# {self.config.tool_title} Tool Discovery Guide

Comprehensive guide to discovering and utilizing all {self.config.tool_title} capabilities using proven methodologies.

## 🎯 Discovery Methodology

This system implements proven patterns from ESP32-C6 VESC Express project, providing:
- **Multi-layered Discovery**: Convenience scripts, analytics, documentation, slash commands
- **Smart Recommendations**: Context-aware suggestions based on project state
- **Usage Analytics**: Learning from patterns to optimize workflows
- **Cross-platform Support**: Works on Linux, macOS, Windows (WSL2)

## 🔍 Discovery Layers

### 1. Convenience Script Discovery
```bash
./{self.config.tool_name}_ultimate discover   # Show all capabilities
./{self.config.tool_name}_ultimate suggest    # Context-aware recommendations
./{self.config.tool_name}_ultimate             # Full help system
```

### 2. Analytics-Driven Discovery
```bash
./{self.config.tool_name}_analytics_report.sh # Usage insights
# Automatically suggests underutilized features
# Recommends optimizations based on patterns
```

### 3. Claude Code Integration
```bash
# In Claude Code, type:
/{self.config.tool_name}-discover    # Comprehensive tool exploration
/{self.config.tool_name}-analyze     # Advanced analysis
/{self.config.tool_name}-troubleshoot # Problem resolution
```

### 4. Documentation Discovery
- `TEAM_ONBOARDING.md` - Getting started guide
- `CROSS_PLATFORM_COMPATIBILITY.md` - Platform support
- `ANALYTICS_AND_OPTIMIZATION.md` - Performance insights

## 🤖 Smart Recommendation Engine

### Context Analysis
The system analyzes:
- Project configuration state
- Service running status
- Usage history patterns
- Error frequency
- Performance metrics

### Recommendation Types
1. **Immediate Actions**: High-priority items requiring attention
2. **Optimization Opportunities**: Performance improvements
3. **Learning Suggestions**: Discover new capabilities
4. **Best Practices**: Follow proven patterns

### Examples
```bash
# No configuration detected
🎯 Recommended: ./{self.config.tool_name}_ultimate setup

# Service not running
🎯 Recommended: ./{self.config.tool_name}_ultimate start

# High usage detected
🎯 Recommended: ./{self.config.tool_name}_ultimate optimize
```

## 📊 Analytics Integration

### Usage Tracking
- Command frequency analysis
- Category-based usage (Development, Debugging, Discovery)
- Time-based activity patterns
- Performance impact measurement

### Optimization Insights
- Identify most valuable tools
- Suggest workflow improvements
- Highlight underutilized capabilities
- Recommend training focus areas

---

**This discovery system provides comprehensive {self.config.tool_title} capability exploration with intelligent recommendations and analytics-driven optimization.**
'''

    def generate_compatibility_doc(self) -> str:
        """Generate cross-platform compatibility documentation."""
        return f'''# {self.config.tool_title} Cross-Platform Compatibility

Comprehensive platform support matrix and setup guidelines for {self.config.tool_title} tool discovery ecosystem.

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
./{self.config.tool_name}_ultimate setup
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
cd {self.config.tool_name}_project
./{self.config.tool_name}_ultimate setup
./{self.config.tool_name}_ultimate check
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
./{self.config.tool_name}_ultimate setup
```

### macOS-Specific Considerations
- **Shell**: Use bash for full script compatibility
- **Security**: Gatekeeper may require permission for scripts
- **Analytics**: Full functionality with system integration

---

**Platform Compatibility Summary**: {self.config.tool_title} provides excellent cross-platform support with Linux as the primary platform, WSL2 as the recommended Windows solution, and good macOS compatibility. All major discovery patterns are supported across platforms.**
'''

    def generate_analytics_doc(self) -> str:
        """Generate analytics and optimization documentation."""
        return f'''# {self.config.tool_title} Analytics and Optimization

Comprehensive guide to usage analytics, performance monitoring, and optimization insights for {self.config.tool_title} tool discovery ecosystem.

## 📊 Analytics Overview

The {self.config.tool_title} analytics system provides:
- **Usage Tracking**: Command frequency and patterns
- **Performance Metrics**: Execution times and resource usage
- **Smart Recommendations**: Context-aware optimization suggestions
- **Trend Analysis**: Historical usage patterns and improvements

## 🔍 Analytics Collection

### Automatic Tracking
Every command execution is automatically logged:
```bash
# Logged automatically when using convenience script
./{self.config.tool_name}_ultimate <command>

# Analytics file location
.{self.config.tool_name}_analytics.log
```

### Tracked Metrics
- **Command Name**: Which commands are used most frequently
- **Timestamp**: When commands are executed
- **Context**: Project state and environment conditions
- **Performance**: Execution duration and resource usage
- **Success Rate**: Command completion status

## 📈 Analytics Reports

### Basic Analytics Report
```bash
# View comprehensive analytics
./{self.config.tool_name}_analytics_report.sh

# Export analytics data
./{self.config.tool_name}_analytics_report.sh export

# Clear analytics history
./{self.config.tool_name}_analytics_report.sh clear
```

### Report Components

#### 1. Usage Summary
- Total commands executed
- Most popular commands (top 5)
- Usage timeline (last 10 entries)
- Daily activity patterns

#### 2. Command Categories
- **Development**: setup, start, dev, check commands
- **Debugging**: debug, troubleshoot, analyze commands
- **Discovery**: suggest, discover, analytics commands

#### 3. Performance Insights
- Average command execution time
- Resource usage patterns
- Optimization opportunities
- Error frequency analysis

#### 4. Smart Recommendations
- Based on usage patterns
- Context-aware suggestions
- Performance optimization tips
- Best practice guidance

---

**The {self.config.tool_title} analytics system provides comprehensive insights for continuous optimization, enabling data-driven development workflow improvements and enhanced team productivity.**
'''
