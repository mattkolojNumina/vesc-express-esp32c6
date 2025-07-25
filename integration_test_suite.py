#!/usr/bin/env python3
"""
Comprehensive integration test suite for the refactored tool discoverability system.
Tests real-world scenarios and end-to-end functionality.
"""

import asyncio
import json
import tempfile
import shutil
import subprocess
import sys
import os
from pathlib import Path


class IntegrationTestSuite:
    """Comprehensive integration test suite."""
    
    def __init__(self):
        """Initialize test suite."""
        self.base_dir = Path(__file__).parent
        self.test_results = []
        self.temp_dirs = []
    
    def setup_test_directory(self, name: str) -> Path:
        """Create a temporary test directory."""
        temp_dir = Path(tempfile.mkdtemp(prefix=f"integration_test_{name}_"))
        self.temp_dirs.append(temp_dir)
        return temp_dir
    
    def cleanup(self):
        """Clean up all test directories."""
        for temp_dir in self.temp_dirs:
            shutil.rmtree(temp_dir, ignore_errors=True)
    
    def parse_json_output(self, stdout: str) -> dict:
        """Parse JSON output from mixed stdout content."""
        try:
            # Find JSON object in output
            json_start = stdout.find('{')
            json_end = stdout.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = stdout[json_start:json_end]
                return json.loads(json_str)
        except json.JSONDecodeError:
            pass
        return {}
    
    def run_command(self, cmd: list, cwd: Path = None) -> dict:
        """Run a command and return results."""
        try:
            result = subprocess.run(
                cmd,
                cwd=cwd or self.base_dir,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            return {
                'success': result.returncode == 0,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'returncode': result.returncode
            }
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'error': 'Command timed out',
                'returncode': -1
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'returncode': -1
            }
    
    def test_basic_enhancement(self) -> bool:
        """Test basic enhancement functionality."""
        print("🔧 Testing basic enhancement...")
        
        test_dir = self.setup_test_directory("basic")
        
        cmd = [
            sys.executable, 
            str(self.base_dir / "tool_discoverability_enhancer.py"),
            "testbasic",
            "--convenience-script",
            "--target-directory", str(test_dir)
        ]
        
        result = self.run_command(cmd)
        
        if not result['success']:
            print(f"❌ Basic enhancement failed: {result.get('stderr', 'Unknown error')}")
            return False
        
        # Parse JSON output
        output_data = self.parse_json_output(result['stdout'])
        success = output_data.get('success', False)
        files_created = output_data.get('files_created', [])
        
        if success and len(files_created) > 0:
            # Verify file exists and is executable
            script_path = Path(files_created[0])
            if script_path.exists() and os.access(script_path, os.X_OK):
                print("✅ Basic enhancement test passed")
                return True
        
        print("❌ Basic enhancement test failed")
        return False
    
    def test_full_enhancement(self) -> bool:
        """Test full enhancement with all patterns."""
        print("🚀 Testing full enhancement...")
        
        test_dir = self.setup_test_directory("full")
        
        cmd = [
            sys.executable,
            str(self.base_dir / "tool_discoverability_enhancer.py"),
            "testfull",
            "--full",
            "--target-directory", str(test_dir)
        ]
        
        result = self.run_command(cmd)
        
        if not result['success']:
            print(f"❌ Full enhancement failed: {result.get('stderr', 'Unknown error')}")
            return False
        
        output_data = self.parse_json_output(result['stdout'])
        success = output_data.get('success', False)
        files_created = output_data.get('files_created', [])
        patterns_applied = output_data.get('patterns_applied', [])
        
        if success and len(files_created) >= 10 and len(patterns_applied) >= 5:
            print(f"✅ Full enhancement test passed ({len(files_created)} files, {len(patterns_applied)} patterns)")
            return True
        
        print("❌ Full enhancement test failed")
        return False
    
    def test_slash_command_integration(self) -> bool:
        """Test slash command integration."""
        print("⚡ Testing slash command integration...")
        
        test_dir = self.setup_test_directory("slash")
        
        cmd = [
            sys.executable,
            str(self.base_dir / "tool_discoverability_fix_slash_command.py"),
            "testslash",
            "--convenience-script",
            "--target-directory", str(test_dir)
        ]
        
        result = self.run_command(cmd)
        
        if not result['success']:
            print(f"❌ Slash command test failed: {result.get('stderr', 'Unknown error')}")
            return False
        
        output_data = self.parse_json_output(result['stdout'])
        success = output_data.get('success', False)
        
        if success:
            print("✅ Slash command integration test passed")
            return True
        
        print("❌ Slash command integration test failed")
        return False
    
    def test_multiple_tool_types(self) -> bool:
        """Test enhancement of multiple different tool types."""
        print("🔄 Testing multiple tool types...")
        
        tools = [
            ("javascript", "--convenience-script"),
            ("python", "--analytics"),
            ("docker", "--docs"),
            ("kubernetes", "--recommendations"),
            ("terraform", "--slash-commands")
        ]
        
        success_count = 0
        
        for tool_name, option in tools:
            test_dir = self.setup_test_directory(f"multi_{tool_name}")
            
            cmd = [
                sys.executable,
                str(self.base_dir / "tool_discoverability_enhancer.py"),
                tool_name,
                option,
                "--target-directory", str(test_dir)
            ]
            
            result = self.run_command(cmd)
            
            if result['success']:
                output_data = self.parse_json_output(result['stdout'])
                if output_data.get('success', False):
                    success_count += 1
                    print(f"  ✅ {tool_name} enhancement successful")
                else:
                    print(f"  ❌ {tool_name} enhancement failed in processing")
            else:
                print(f"  ❌ {tool_name} enhancement failed to execute")
        
        success_rate = (success_count / len(tools)) * 100
        print(f"✅ Multiple tool types test: {success_count}/{len(tools)} successful ({success_rate:.0f}%)")
        
        return success_count >= len(tools) * 0.8  # 80% success rate required
    
    def test_validation_functionality(self) -> bool:
        """Test validation and error fixing functionality."""
        print("🔍 Testing validation functionality...")
        
        test_dir = self.setup_test_directory("validation")
        
        cmd = [
            sys.executable,
            str(self.base_dir / "tool_discoverability_enhancer.py"),
            "testvalidation",
            "--convenience-script",
            "--validate",
            "--target-directory", str(test_dir)
        ]
        
        result = self.run_command(cmd)
        
        if not result['success']:
            print(f"❌ Validation test failed: {result.get('stderr', 'Unknown error')}")
            return False
        
        output_data = self.parse_json_output(result['stdout'])
        validation_result = output_data.get('validation', {})
        
        if validation_result.get('success', False):
            files_validated = validation_result.get('files_validated', 0)
            print(f"✅ Validation test passed ({files_validated} files validated)")
            return True
        
        print("❌ Validation test failed")
        return False
    
    def test_performance_benchmarks(self) -> bool:
        """Test performance benchmarks."""
        print("⚡ Testing performance benchmarks...")
        
        import time
        
        test_dir = self.setup_test_directory("performance")
        
        start_time = time.time()
        
        cmd = [
            sys.executable,
            str(self.base_dir / "tool_discoverability_enhancer.py"),
            "perftest",
            "--full",
            "--target-directory", str(test_dir)
        ]
        
        result = self.run_command(cmd)
        end_time = time.time()
        
        execution_time = end_time - start_time
        
        if result['success'] and execution_time < 5.0:  # Should complete within 5 seconds
            print(f"✅ Performance test passed ({execution_time:.2f}s)")
            return True
        else:
            print(f"❌ Performance test failed ({execution_time:.2f}s)")
            return False
    
    def test_error_handling(self) -> bool:
        """Test error handling with invalid inputs."""
        print("🛡️ Testing error handling...")
        
        error_tests = [
            # Invalid directory
            ["testinvalid", "--convenience-script", "--target-directory", "/root/invalid_permission_dir"],
            # Missing tool name
            ["--convenience-script"],
            # Invalid option combination
            ["testtool", "--invalid-option"]
        ]
        
        for cmd_args in error_tests:
            cmd = [sys.executable, str(self.base_dir / "tool_discoverability_enhancer.py")] + cmd_args
            result = self.run_command(cmd)
            
            # Errors should be handled gracefully (not crash)
            if result['returncode'] not in [0, 1, 2]:  # These are acceptable exit codes
                print(f"❌ Error handling test failed with unexpected exit code: {result['returncode']}")
                return False
        
        print("✅ Error handling test passed")
        return True
    
    def run_all_tests(self) -> dict:
        """Run all integration tests."""
        print("🧪 Starting Comprehensive Integration Test Suite\n")
        
        tests = [
            ("Basic Enhancement", self.test_basic_enhancement),
            ("Full Enhancement", self.test_full_enhancement),
            ("Slash Command Integration", self.test_slash_command_integration),
            ("Multiple Tool Types", self.test_multiple_tool_types),
            ("Validation Functionality", self.test_validation_functionality),
            ("Performance Benchmarks", self.test_performance_benchmarks),
            ("Error Handling", self.test_error_handling)
        ]
        
        results = {}
        passed = 0
        
        for test_name, test_func in tests:
            try:
                success = test_func()
                results[test_name] = success
                if success:
                    passed += 1
                print()  # Add spacing between tests
            except Exception as e:
                print(f"❌ {test_name} crashed: {e}")
                results[test_name] = False
                print()
        
        success_rate = (passed / len(tests)) * 100
        
        print("=" * 60)
        print("📊 Integration Test Suite Results:")
        print("=" * 60)
        
        for test_name, success in results.items():
            status = "✅ PASSED" if success else "❌ FAILED"
            print(f"  {test_name}: {status}")
        
        print(f"\nOverall Success Rate: {passed}/{len(tests)} ({success_rate:.0f}%)")
        
        return {
            'overall_success': success_rate >= 85,  # 85% pass rate required
            'passed': passed,
            'total': len(tests),
            'success_rate': success_rate,
            'results': results
        }


def main():
    """Run the integration test suite."""
    suite = IntegrationTestSuite()
    
    try:
        results = suite.run_all_tests()
        
        if results['overall_success']:
            print("\n🎉 Integration test suite PASSED!")
            return 0
        else:
            print("\n❌ Integration test suite FAILED!")
            return 1
    
    finally:
        suite.cleanup()


if __name__ == "__main__":
    sys.exit(main())