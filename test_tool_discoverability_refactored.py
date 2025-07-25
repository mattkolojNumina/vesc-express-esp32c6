#!/usr/bin/env python3
"""
Comprehensive unit tests for refactored tool discoverability system.
Tests the modular components: ToolConfig, generators, and main class integration.
"""

import unittest
import tempfile
import shutil
from pathlib import Path
import sys
import os

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from tool_discoverability_templates import ToolConfig
from tool_discoverability_generators import (
    ScriptGenerator,
    ConfigurationGenerator, 
    SlashCommandGenerator,
    DocumentationGenerator
)


class TestToolConfig(unittest.TestCase):
    """Test ToolConfig dataclass functionality."""
    
    def test_tool_config_creation(self):
        """Test ToolConfig creation from tool name."""
        config = ToolConfig.from_tool_name("fastmcp")
        
        self.assertEqual(config.tool_name, "fastmcp")
        self.assertEqual(config.tool_title, "Fastmcp")
        self.assertEqual(config.tool_upper, "FASTMCP")
    
    def test_tool_config_edge_cases(self):
        """Test ToolConfig with various input formats."""
        # Test with underscores
        config1 = ToolConfig.from_tool_name("my_tool")
        self.assertEqual(config1.tool_name, "my_tool")
        self.assertEqual(config1.tool_title, "My_Tool")
        self.assertEqual(config1.tool_upper, "MY_TOOL")
        
        # Test with hyphens
        config2 = ToolConfig.from_tool_name("my-tool")
        self.assertEqual(config2.tool_name, "my-tool")
        self.assertEqual(config2.tool_title, "My-Tool")
        self.assertEqual(config2.tool_upper, "MY-TOOL")
        
        # Test with single character
        config3 = ToolConfig.from_tool_name("x")
        self.assertEqual(config3.tool_name, "x")
        self.assertEqual(config3.tool_title, "X")
        self.assertEqual(config3.tool_upper, "X")


class TestScriptGenerator(unittest.TestCase):
    """Test ScriptGenerator functionality."""
    
    def setUp(self):
        """Set up test configuration."""
        self.config = ToolConfig.from_tool_name("testool")
        self.generator = ScriptGenerator(self.config)
    
    def test_convenience_script_generation(self):
        """Test convenience script generation."""
        script = self.generator.generate_convenience_script()
        
        # Verify script contains essential components
        self.assertIn("#!/bin/bash", script)
        self.assertIn("testool", script.lower())
        self.assertIn("setup", script)
        self.assertIn("discover", script)
        self.assertIn("suggest", script)
        self.assertIn("dev", script)
        
        # Verify script structure
        self.assertIn('case "$1" in', script)
        self.assertIn("esac", script)
    
    def test_analytics_script_generation(self):
        """Test analytics script generation."""
        script = self.generator.generate_analytics_script()
        
        # Verify analytics components
        self.assertIn("#!/bin/bash", script)
        self.assertIn("testool", script.lower())
        self.assertIn("analytics", script.lower())
        self.assertIn("usage", script.lower())
        self.assertIn("report", script.lower())
        
        # Verify analytics functions
        self.assertIn("generate_analytics_report", script)


class TestConfigurationGenerator(unittest.TestCase):
    """Test ConfigurationGenerator functionality."""
    
    def setUp(self):
        """Set up test configuration."""
        self.config = ToolConfig.from_tool_name("testool")
        self.generator = ConfigurationGenerator(self.config)
    
    def test_smart_recommendations_generation(self):
        """Test smart recommendations configuration generation."""
        recommendations = self.generator.generate_recommendations_config()
        
        # Verify JSON structure
        self.assertIn("tool_name", recommendations)
        self.assertIn("recommendation_rules", recommendations)
        self.assertIn("context_patterns", recommendations)
        
        # Verify tool name is correct
        self.assertEqual(recommendations["tool_name"], "testool")
        
        # Verify rules structure
        rules = recommendations["recommendation_rules"]
        self.assertIsInstance(rules, list)
        self.assertGreater(len(rules), 0)
        
        # Verify rule structure
        first_rule = rules[0]
        self.assertIn("condition", first_rule)
        self.assertIn("recommendation", first_rule)
        self.assertIn("priority", first_rule)
        self.assertIn("description", first_rule)


class TestSlashCommandGenerator(unittest.TestCase):
    """Test SlashCommandGenerator functionality."""
    
    def setUp(self):
        """Set up test configuration."""
        self.config = ToolConfig.from_tool_name("testool")
        self.generator = SlashCommandGenerator(self.config)
    
    def test_slash_command_generation(self):
        """Test slash command generation."""
        # Test individual command generation since there's no generate_all method
        commands = {}
        command_names = ["troubleshoot", "analyze", "optimize", "discover", "debug"]
        
        for cmd_name in command_names:
            description = f"{cmd_name.title()} functionality"
            content = self.generator.generate_slash_command_content(cmd_name, description)
            commands[f"testool-{cmd_name}"] = content
        
        # Verify all expected commands are generated
        expected_commands = [
            "testool-troubleshoot",
            "testool-analyze", 
            "testool-optimize",
            "testool-discover",
            "testool-debug"
        ]
        
        self.assertEqual(len(commands), len(expected_commands))
        
        for cmd_name in expected_commands:
            self.assertIn(cmd_name, commands)
            
            # Verify command content structure
            content = commands[cmd_name]
            self.assertIn("# Testool", content)
            self.assertIn("**Usage Examples:**", content)
            self.assertIn("**Arguments:** $ARGUMENTS", content)
            self.assertIn("**Command to run:**", content)


class TestDocumentationGenerator(unittest.TestCase):
    """Test DocumentationGenerator functionality."""
    
    def setUp(self):
        """Set up test configuration."""
        self.config = ToolConfig.from_tool_name("testool")
        self.generator = DocumentationGenerator(self.config)
    
    def test_team_onboarding_doc_generation(self):
        """Test team onboarding documentation generation."""
        doc = self.generator.generate_team_onboarding_doc()
        
        # Verify documentation structure
        self.assertIn("# Testool Team Onboarding Guide", doc)
        self.assertIn("## 🚀 Quick Start", doc)
        self.assertIn("./testool_ultimate setup", doc)
        self.assertIn("./testool_ultimate check", doc)
        self.assertIn("./testool_ultimate dev", doc)
    
    def test_discovery_guide_doc_generation(self):
        """Test discovery guide documentation generation."""
        doc = self.generator.generate_discovery_guide_doc()
        
        # Verify discovery guide structure
        self.assertIn("# Testool Tool Discovery Guide", doc)
        self.assertIn("## 🎯 Discovery Methodology", doc)
        self.assertIn("./testool_ultimate discover", doc)
    
    def test_compatibility_doc_generation(self):
        """Test compatibility documentation generation."""
        doc = self.generator.generate_compatibility_doc()
        
        # Verify compatibility documentation
        self.assertIn("# Testool Cross-Platform Compatibility", doc)
        self.assertIn("## ✅ Platform Support Matrix", doc)
        self.assertIn("Linux", doc)
        self.assertIn("macOS", doc)
        self.assertIn("Windows", doc)
    
    def test_analytics_doc_generation(self):
        """Test analytics documentation generation."""
        doc = self.generator.generate_analytics_doc()
        
        # Verify analytics documentation
        self.assertIn("# Testool Analytics and Optimization", doc)
        self.assertIn("## 📊 Analytics Overview", doc)
        self.assertIn("./testool_analytics_report.sh", doc)


class TestIntegration(unittest.TestCase):
    """Test integration between components."""
    
    def setUp(self):
        """Set up integration test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.config = ToolConfig.from_tool_name("integration_test")
    
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_full_generation_workflow(self):
        """Test complete generation workflow using all components."""
        # Test ScriptGenerator
        script_gen = ScriptGenerator(self.config)
        convenience_script = script_gen.generate_convenience_script()
        analytics_script = script_gen.generate_analytics_script()
        
        # Test ConfigurationGenerator
        config_gen = ConfigurationGenerator(self.config)
        recommendations = config_gen.generate_recommendations_config()
        
        # Test SlashCommandGenerator
        slash_gen = SlashCommandGenerator(self.config)
        slash_command = slash_gen.generate_slash_command_content("troubleshoot", "Test troubleshooting")
        
        # Test DocumentationGenerator
        doc_gen = DocumentationGenerator(self.config)
        team_doc = doc_gen.generate_team_onboarding_doc()
        
        # Verify all components work together
        self.assertIsInstance(convenience_script, str)
        self.assertIsInstance(analytics_script, str)
        self.assertIsInstance(recommendations, dict)
        self.assertIsInstance(slash_command, str)
        self.assertIsInstance(team_doc, str)
        
        # Verify consistent tool naming across components
        tool_references = [
            convenience_script.lower().count("integration_test"),
            analytics_script.lower().count("integration_test"),
            team_doc.lower().count("integration_test")
        ]
        
        # All components should reference the tool multiple times
        for count in tool_references:
            self.assertGreater(count, 0)


if __name__ == "__main__":
    # Configure test runner
    unittest.main(verbosity=2, buffer=True)