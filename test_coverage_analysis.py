#!/usr/bin/env python3
"""
Enhanced test coverage analysis for refactored tool discoverability system.
Tests edge cases, error conditions, and comprehensive functionality.
"""

import unittest
import tempfile
import shutil
import json
import os
import sys
from pathlib import Path
from unittest.mock import patch, Mock

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from tool_discoverability_templates import ToolConfig
from tool_discoverability_generators import (
    ScriptGenerator,
    ConfigurationGenerator, 
    SlashCommandGenerator,
    DocumentationGenerator
)
from tool_discoverability_enhancer import ToolDiscoverabilityEnhancer


class TestEdgeCasesAndErrorHandling(unittest.TestCase):
    """Test edge cases and error handling scenarios."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.config = ToolConfig.from_tool_name("test_tool")
    
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_tool_config_empty_name(self):
        """Test ToolConfig with empty tool name."""
        config = ToolConfig.from_tool_name("")
        self.assertEqual(config.tool_name, "")
        self.assertEqual(config.tool_title, "")
        self.assertEqual(config.tool_upper, "")
    
    def test_tool_config_special_characters(self):
        """Test ToolConfig with special characters."""
        config = ToolConfig.from_tool_name("my-tool_v2.0")
        self.assertEqual(config.tool_name, "my-tool_v2.0")
        self.assertEqual(config.tool_title, "My-Tool_V2.0")
        self.assertEqual(config.tool_upper, "MY-TOOL_V2.0")
    
    def test_script_generator_content_validation(self):
        """Test script generator produces valid content."""
        generator = ScriptGenerator(self.config)
        
        convenience_script = generator.generate_convenience_script()
        analytics_script = generator.generate_analytics_script()
        
        # Verify shell script structure
        self.assertTrue(convenience_script.startswith("#!/bin/bash"))
        self.assertTrue(analytics_script.startswith("#!/bin/bash"))
        
        # Verify essential commands are present
        self.assertIn("case \"$1\" in", convenience_script)
        self.assertIn("esac", convenience_script)
        self.assertIn("generate_analytics_report", analytics_script)
    
    def test_configuration_generator_json_structure(self):
        """Test configuration generator produces valid JSON structure."""
        generator = ConfigurationGenerator(self.config)
        config_data = generator.generate_recommendations_config()
        
        # Verify it's valid JSON-serializable
        json_str = json.dumps(config_data)
        parsed = json.loads(json_str)
        
        self.assertEqual(parsed["tool_name"], "test_tool")
        self.assertIn("recommendation_rules", parsed)
        self.assertIn("context_patterns", parsed)
        
        # Verify rules structure
        for rule in parsed["recommendation_rules"]:
            self.assertIn("condition", rule)
            self.assertIn("recommendation", rule)
            self.assertIn("priority", rule)
            self.assertIn("description", rule)
    
    def test_slash_command_generator_markdown_validity(self):
        """Test slash command generator produces valid markdown."""
        generator = SlashCommandGenerator(self.config)
        content = generator.generate_slash_command_content("troubleshoot", "Test troubleshooting")
        
        # Verify markdown structure
        self.assertIn("# Test_Tool Troubleshoot", content)
        self.assertIn("**Usage Examples:**", content)
        self.assertIn("**Arguments:** $ARGUMENTS", content)
        self.assertIn("```bash", content)
    
    def test_documentation_generator_comprehensive_docs(self):
        """Test documentation generator produces comprehensive documentation."""
        generator = DocumentationGenerator(self.config)
        
        team_doc = generator.generate_team_onboarding_doc()
        discovery_doc = generator.generate_discovery_guide_doc()
        compatibility_doc = generator.generate_compatibility_doc()
        analytics_doc = generator.generate_analytics_doc()
        
        # Verify all docs have proper structure
        docs = [team_doc, discovery_doc, compatibility_doc, analytics_doc]
        for doc in docs:
            self.assertIn("# Test_Tool", doc)
            self.assertIn("## ", doc)  # Has sections
            self.assertIn("test_tool", doc.lower())  # References tool
    
    def test_enhancer_initialization_edge_cases(self):
        """Test enhancer initialization with edge cases."""
        # Test with non-existent directory
        enhancer1 = ToolDiscoverabilityEnhancer("test", "/tmp/non_existent_dir_12345")
        self.assertTrue(enhancer1.target_directory.exists())  # Should be created
        
        # Test with existing directory
        enhancer2 = ToolDiscoverabilityEnhancer("test", self.temp_dir)
        self.assertEqual(str(enhancer2.target_directory), str(Path(self.temp_dir).resolve()))
        
        # Clean up created directory
        shutil.rmtree("/tmp/non_existent_dir_12345", ignore_errors=True)


class TestPerformanceAndLoad(unittest.TestCase):
    """Test performance characteristics and load handling."""
    
    def setUp(self):
        """Set up performance test environment."""
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up performance test environment."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_multiple_tool_generation_performance(self):
        """Test performance with multiple tool generations."""
        import time
        
        tools = ["tool1", "tool2", "tool3", "tool4", "tool5"]
        start_time = time.time()
        
        for tool_name in tools:
            config = ToolConfig.from_tool_name(tool_name)
            
            # Test all generators
            script_gen = ScriptGenerator(config)
            config_gen = ConfigurationGenerator(config)
            slash_gen = SlashCommandGenerator(config)
            doc_gen = DocumentationGenerator(config)
            
            # Generate content
            script_gen.generate_convenience_script()
            script_gen.generate_analytics_script()
            config_gen.generate_recommendations_config()
            slash_gen.generate_slash_command_content("test", "Test command")
            doc_gen.generate_team_onboarding_doc()
        
        end_time = time.time()
        generation_time = end_time - start_time
        
        # Should complete within reasonable time (< 1 second for 5 tools)
        self.assertLess(generation_time, 1.0)
        print(f"✅ Generated content for {len(tools)} tools in {generation_time:.3f}s")
    
    def test_large_tool_name_handling(self):
        """Test handling of very long tool names."""
        long_name = "very_long_tool_name_with_many_components_and_underscores_that_could_cause_issues"
        
        config = ToolConfig.from_tool_name(long_name)
        generator = ScriptGenerator(config)
        
        script = generator.generate_convenience_script()
        self.assertIn(long_name, script)
        
        # Verify script is still valid
        self.assertTrue(script.startswith("#!/bin/bash"))
        self.assertIn("case \"$1\" in", script)


class TestErrorConditions(unittest.TestCase):
    """Test error conditions and exception handling."""
    
    def setUp(self):
        """Set up error condition tests."""
        self.temp_dir = tempfile.mkdtemp()
        self.config = ToolConfig.from_tool_name("error_test")
    
    def tearDown(self):
        """Clean up error condition tests."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_invalid_tool_names(self):
        """Test handling of potentially problematic tool names."""
        problematic_names = [
            "tool with spaces",
            "tool/with/slashes", 
            "tool;with;semicolons",
            "tool'with'quotes",
            'tool"with"doublequotes'
        ]
        
        for name in problematic_names:
            config = ToolConfig.from_tool_name(name)
            generator = ScriptGenerator(config)
            
            # Should not raise exceptions
            try:
                script = generator.generate_convenience_script()
                self.assertIsInstance(script, str)
                self.assertGreater(len(script), 0)
            except Exception as e:
                self.fail(f"Generator failed for tool name '{name}': {e}")


class TestCrossComponentIntegration(unittest.TestCase):
    """Test integration between different components."""
    
    def setUp(self):
        """Set up integration tests."""
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up integration tests."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_consistent_tool_references(self):
        """Test that all components consistently reference the same tool."""
        tool_name = "integration_test"
        config = ToolConfig.from_tool_name(tool_name)
        
        # Generate content from all components
        script_gen = ScriptGenerator(config)
        config_gen = ConfigurationGenerator(config)
        doc_gen = DocumentationGenerator(config)
        
        convenience_script = script_gen.generate_convenience_script()
        recommendations = config_gen.generate_recommendations_config()
        team_doc = doc_gen.generate_team_onboarding_doc()
        
        # All should reference the same tool name
        self.assertIn(tool_name, convenience_script.lower())
        self.assertEqual(recommendations["tool_name"], tool_name)
        self.assertIn(tool_name, team_doc.lower())
    
    def test_template_consistency(self):
        """Test that templates produce consistent output across generators."""
        config = ToolConfig.from_tool_name("consistency_test")
        
        # Generate multiple pieces of content
        script_gen = ScriptGenerator(config)
        doc_gen = DocumentationGenerator(config)
        
        script = script_gen.generate_convenience_script()
        doc = doc_gen.generate_team_onboarding_doc()
        
        # Both should reference the convenience script consistently
        script_name = f"{config.tool_name}_ultimate"
        self.assertIn(script_name, script)
        self.assertIn(script_name, doc)


def run_coverage_analysis():
    """Run comprehensive test coverage analysis."""
    print("🧪 Running Enhanced Test Coverage Analysis...")
    
    # Discover and run all tests
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    test_classes = [
        TestEdgeCasesAndErrorHandling,
        TestPerformanceAndLoad,
        TestErrorConditions,
        TestCrossComponentIntegration
    ]
    
    for test_class in test_classes:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    # Run tests with detailed output
    runner = unittest.TextTestRunner(verbosity=2, buffer=True)
    result = runner.run(suite)
    
    # Calculate coverage metrics
    total_tests = result.testsRun
    failures = len(result.failures)
    errors = len(result.errors)
    success_rate = ((total_tests - failures - errors) / total_tests) * 100 if total_tests > 0 else 0
    
    print(f"\n📊 Coverage Analysis Results:")
    print(f"  Total Tests: {total_tests}")
    print(f"  Successful: {total_tests - failures - errors}")
    print(f"  Failures: {failures}")
    print(f"  Errors: {errors}")
    print(f"  Success Rate: {success_rate:.1f}%")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_coverage_analysis()
    sys.exit(0 if success else 1)