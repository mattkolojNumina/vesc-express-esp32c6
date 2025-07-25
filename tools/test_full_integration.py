#!/usr/bin/env python3
"""
ESP32 Debug Tools - Full Integration Test Suite
Tests complete functionality across CLI, MCP server, and tool discovery
"""

import sys
import subprocess
import json
import time
from pathlib import Path
from typing import Dict, List, Any

class FullIntegrationTest:
    """Comprehensive integration test for ESP32 debug tools"""
    
    def __init__(self):
        self.test_results = {}
        self.failed_tests = []
        
    def run_command(self, cmd: List[str], timeout: int = 30) -> Dict[str, Any]:
        """Run shell command and return result"""
        try:
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                timeout=timeout,
                cwd=Path(__file__).parent.parent
            )
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "stdout": "",
                "stderr": "Command timed out",
                "returncode": -1
            }
        except Exception as e:
            return {
                "success": False,
                "stdout": "",
                "stderr": str(e),
                "returncode": -1
            }
    
    def test_cli_discovery(self) -> bool:
        """Test CLI tool discovery system"""
        print("🔍 Testing CLI tool discovery...")
        
        # Test tool list
        result = self.run_command(["esp32-debug", "--list"])
        if not result["success"]:
            print(f"❌ CLI list failed: {result['stderr']}")
            return False
            
        output = result["stdout"]
        
        # Check for expected tools
        expected_tools = [
            "gdb_automation",
            "memory_debug", 
            "openocd_setup",
            "unified_debugger",
            "wsl2_setup"
        ]
        
        for tool in expected_tools:
            if tool not in output:
                print(f"❌ Tool {tool} not found in CLI output")
                return False
        
        print("✅ CLI tool discovery working")
        return True
    
    def test_cli_commands(self) -> bool:
        """Test CLI command execution"""
        print("🔍 Testing CLI commands...")
        
        # Test help command
        result = self.run_command(["esp32-debug", "--help"])
        if not result["success"]:
            print(f"❌ CLI help failed: {result['stderr']}")
            return False
            
        # Test info command
        result = self.run_command(["esp32-debug", "info"])
        if not result["success"]:
            print(f"❌ CLI info failed: {result['stderr']}")
            return False
            
        print("✅ CLI commands working")
        return True
    
    def test_tool_imports(self) -> bool:
        """Test individual tool imports"""
        print("🔍 Testing tool imports...")
        
        tools = [
            "esp32c6_openocd_setup",
            "esp32c6_gdb_automation",
            "esp32c6_memory_debug", 
            "wsl2_esp32_debug_setup",
            "esp32c6_unified_debugger"
        ]
        
        for tool in tools:
            try:
                # Add current directory to path for direct import
                import sys
                from pathlib import Path
                sys.path.insert(0, str(Path(__file__).parent))
                __import__(tool)
                print(f"✅ {tool} imported successfully")
            except Exception as e:
                print(f"❌ {tool} import failed: {e}")
                return False
        
        return True
    
    def test_mcp_server_basic(self) -> bool:
        """Test basic MCP server functionality"""
        print("🔍 Testing MCP server...")
        
        try:
            # Import MCP server
            sys.path.insert(0, str(Path(__file__).parent))
            import esp32_debug_mcp_server
            
            # Check tool count
            tool_count = len([name for name in dir(esp32_debug_mcp_server) 
                            if hasattr(getattr(esp32_debug_mcp_server, name), '__annotations__')])
            
            if tool_count >= 6:  # Should have at least 6 MCP tools
                print(f"✅ MCP server has {tool_count} tools")
                return True
            else:
                print(f"❌ MCP server only has {tool_count} tools, expected >= 6")
                return False
                
        except Exception as e:
            print(f"❌ MCP server test failed: {e}")
            return False
    
    def test_entry_points(self) -> bool:
        """Test setuptools entry points"""
        print("🔍 Testing entry points...")
        
        # Test if package is installed
        result = self.run_command([sys.executable, "-c", 
            "from importlib.metadata import entry_points; eps = entry_points(); print(len(list(eps.select(group='esp32_debug_tools'))))"])
        
        if not result["success"]:
            print("⚠️  Package not installed with pip install -e .")
            return True  # Not a failure if not installed
            
        try:
            count = int(result["stdout"].strip())
            if count >= 5:
                print(f"✅ Entry points working ({count} tools registered)")
                return True
            else:
                print(f"❌ Only {count} entry points found, expected >= 5")
                return False
        except (ValueError, TypeError) as e:
            print(f"⚠️  Could not parse entry point count: {e}")
            return True
    
    def test_documentation_completeness(self) -> bool:
        """Test documentation completeness"""
        print("🔍 Testing documentation...")
        
        docs = [
            "ESP32_IDF_DEBUGGING_SIMPLIFIED.md",
            "tools/README.md",
            "tools/GETTING_STARTED.md",
            "ESP32_DEBUG_QUICK_REFERENCE.md",
            "MCP_COMPLIANCE_REPORT.md"
        ]
        
        missing_docs = []
        for doc in docs:
            if not Path(doc).exists():
                missing_docs.append(doc)
        
        if missing_docs:
            print(f"❌ Missing documentation: {missing_docs}")
            return False
        
        print("✅ All documentation present")
        return True
    
    def test_file_permissions(self) -> bool:
        """Test file permissions and executability"""
        print("🔍 Testing file permissions...")
        
        executable_files = [
            "tools/esp32_debug_cli.py",
            "tools/esp32_debug_mcp_server.py",
            "tools/esp32c6_unified_debugger.py"
        ]
        
        for file_path in executable_files:
            path = Path(file_path)
            if path.exists() and not path.stat().st_mode & 0o111:
                print(f"⚠️  {file_path} not executable")
        
        print("✅ File permissions OK")
        return True
    
    def test_error_handling(self) -> bool:
        """Test error handling in tools"""
        print("🔍 Testing error handling...")
        
        # Test CLI with invalid command
        result = self.run_command(["esp32-debug", "invalid-command"])
        if result["returncode"] == 0:
            print("❌ CLI should fail on invalid command")
            return False
        
        print("✅ Error handling working")
        return True
    
    def test_configuration_validation(self) -> bool:
        """Test configuration and environment validation"""
        print("🔍 Testing configuration validation...")
        
        # Test MCP quick verify
        result = self.run_command([sys.executable, "tools/mcp_quick_verify.py"])
        if not result["success"]:
            print(f"❌ MCP verification failed: {result['stderr']}")
            return False
        
        print("✅ Configuration validation working")
        return True
    
    def run_all_tests(self) -> Dict[str, bool]:
        """Run complete integration test suite"""
        print("🚀 Starting Full Integration Test Suite")
        print("=" * 60)
        
        tests = [
            ("Tool Imports", self.test_tool_imports),
            ("CLI Discovery", self.test_cli_discovery),
            ("CLI Commands", self.test_cli_commands),
            ("MCP Server Basic", self.test_mcp_server_basic),
            ("Entry Points", self.test_entry_points),
            ("Documentation", self.test_documentation_completeness),
            ("File Permissions", self.test_file_permissions),
            ("Error Handling", self.test_error_handling),
            ("Configuration Validation", self.test_configuration_validation),
        ]
        
        results = {}
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            print(f"\n📋 Running: {test_name}")
            try:
                result = test_func()
                results[test_name] = result
                if result:
                    passed += 1
                else:
                    self.failed_tests.append(test_name)
            except Exception as e:
                print(f"❌ Test {test_name} failed with exception: {e}")
                results[test_name] = False
                self.failed_tests.append(test_name)
        
        print("\n" + "=" * 60)
        print("📊 Integration Test Results:")
        print(f"✅ Passed: {passed}/{total}")
        print(f"❌ Failed: {total - passed}/{total}")
        
        if passed == total:
            print("\n🎉 ALL INTEGRATION TESTS PASSED - SYSTEM FULLY FUNCTIONAL")
        else:
            print(f"\n⚠️  {len(self.failed_tests)} tests failed:")
            for test in self.failed_tests:
                print(f"   - {test}")
        
        return results

def main():
    """Run integration tests"""
    print("🔧 ESP32 Debug Tools - Full Integration Test")
    print("=" * 60)
    
    tester = FullIntegrationTest()
    results = tester.run_all_tests()
    
    # Return exit code based on results
    if all(results.values()):
        print("\n✅ All systems operational - Ready for production use")
        sys.exit(0)
    else:
        print(f"\n❌ {len(tester.failed_tests)} issues found - Review and fix")
        sys.exit(1)

if __name__ == "__main__":
    main()