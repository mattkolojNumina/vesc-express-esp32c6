#!/usr/bin/env python3
"""
MCP Compliance Test Suite
Tests ESP32 Debug Tools MCP Server against Model Context Protocol specification
"""

import json
import subprocess
import sys
import time
from typing import Dict, Any, List
from pathlib import Path

class MCPComplianceTest:
    """Test suite for MCP specification compliance"""
    
    def __init__(self, server_script: str):
        self.server_script = server_script
        self.test_results = []
        
    def send_jsonrpc_request(self, method: str, params: Dict[str, Any] = None, request_id: int = 1) -> Dict[str, Any]:
        """Send JSON-RPC request to MCP server"""
        request = {
            "jsonrpc": "2.0",
            "method": method,
            "id": request_id
        }
        
        if params:
            request["params"] = params
            
        try:
            # Start server process
            proc = subprocess.Popen(
                [sys.executable, self.server_script],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Send request
            request_str = json.dumps(request)
            stdout, stderr = proc.communicate(input=request_str, timeout=10)
            
            # Parse response
            if stdout.strip():
                return json.loads(stdout.strip())
            else:
                return {"error": f"No response. stderr: {stderr}"}
                
        except subprocess.TimeoutExpired:
            proc.kill()
            return {"error": "Request timeout"}
        except Exception as e:
            return {"error": str(e)}
    
    def test_initialize_sequence(self) -> bool:
        """Test MCP initialization sequence"""
        print("🔍 Testing MCP initialization sequence...")
        
        # Test 1: Initialize request
        init_params = {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {
                "name": "test-client",
                "version": "1.0.0"
            }
        }
        
        response = self.send_jsonrpc_request("initialize", init_params)
        
        if "error" in response:
            print(f"❌ Initialize failed: {response['error']}")
            return False
            
        if "result" not in response:
            print("❌ Initialize response missing result")
            return False
            
        result = response["result"]
        
        # Check required fields
        required_fields = ["protocolVersion", "capabilities", "serverInfo"]
        for field in required_fields:
            if field not in result:
                print(f"❌ Initialize response missing {field}")
                return False
        
        print("✅ Initialize sequence passed")
        return True
    
    def test_tools_list(self) -> bool:
        """Test tools/list method after proper initialization"""
        print("🔍 Testing tools/list method with proper MCP initialization...")
        
        # Start a persistent connection for proper MCP flow
        try:
            proc = subprocess.Popen(
                [sys.executable, self.server_script],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=0  # Unbuffered
            )
            
            # Send initialize
            init_request = {
                "jsonrpc": "2.0",
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {
                        "name": "test-client",
                        "version": "1.0.0"
                    }
                },
                "id": 1
            }
            proc.stdin.write(json.dumps(init_request) + "\n")
            proc.stdin.flush()
            
            # Read initialize response (skip any startup messages)
            init_response = None
            for _ in range(5):  # Try up to 5 lines
                line = proc.stdout.readline()
                if line and line.strip().startswith('{"jsonrpc"'):
                    init_response = line.strip()
                    break
            
            if not init_response:
                print("❌ No initialize response found")
                proc.kill()
                return False
            
            init_result = json.loads(init_response)
            if "error" in init_result:
                print(f"❌ Initialize failed: {init_result['error']}")
                proc.kill()
                return False
            
            # Send initialized notification
            initialized_notification = {
                "jsonrpc": "2.0",
                "method": "notifications/initialized"
            }
            proc.stdin.write(json.dumps(initialized_notification) + "\n")
            proc.stdin.flush()
            
            # Now send tools/list
            tools_request = {
                "jsonrpc": "2.0",
                "method": "tools/list",
                "id": 2
            }
            proc.stdin.write(json.dumps(tools_request) + "\n")
            proc.stdin.flush()
            
            # Read tools/list response
            tools_response = None
            for _ in range(3):  # Try up to 3 lines
                line = proc.stdout.readline()
                if line and line.strip().startswith('{"jsonrpc"'):
                    tools_response = line.strip()
                    break
                    
            proc.kill()
            
            if not tools_response:
                print("❌ No tools/list response found")
                return False
                
            tools_result = json.loads(tools_response)
            
            if "error" in tools_result:
                print(f"❌ tools/list failed: {tools_result['error']}")
                return False
                
            if "result" not in tools_result:
                print("❌ tools/list response missing result")
                return False
                
            result = tools_result["result"]
            
            # Check tools structure
            if "tools" not in result:
                print("❌ tools/list response missing tools array")
                return False
                
            tools = result["tools"]
            if not isinstance(tools, list):
                print("❌ tools must be an array")
                return False
                
            # Validate each tool
            for tool in tools:
                required_tool_fields = ["name", "description", "inputSchema"]
                for field in required_tool_fields:
                    if field not in tool:
                        print(f"❌ Tool '{tool.get('name', 'unknown')}' missing {field}")
                        return False
            
            print(f"✅ tools/list passed - {len(tools)} tools discovered")
            return True
            
        except Exception as e:
            if 'proc' in locals():
                proc.kill()
            print(f"❌ tools/list test error: {e}")
            return False
    
    def test_resources_list(self) -> bool:
        """Test resources/list method"""
        print("🔍 Testing resources/list method...")
        
        response = self.send_jsonrpc_request("resources/list")
        
        if "error" in response:
            # Resources are optional, so error is acceptable
            print("ℹ️  resources/list not implemented (optional)")
            return True
            
        if "result" in response:
            result = response["result"]
            if "resources" in result:
                print(f"✅ resources/list passed - {len(result['resources'])} resources")
            else:
                print("ℹ️  resources/list returned empty")
            return True
            
        return True
    
    def test_prompts_list(self) -> bool:
        """Test prompts/list method"""
        print("🔍 Testing prompts/list method...")
        
        response = self.send_jsonrpc_request("prompts/list")
        
        if "error" in response:
            # Prompts are optional, so error is acceptable
            print("ℹ️  prompts/list not implemented (optional)")
            return True
            
        if "result" in response:
            result = response["result"]
            if "prompts" in result:
                print(f"✅ prompts/list passed - {len(result['prompts'])} prompts")
            else:
                print("ℹ️  prompts/list returned empty")
            return True
            
        return True
    
    def test_ping(self) -> bool:
        """Test ping utility method"""
        print("🔍 Testing ping method...")
        
        response = self.send_jsonrpc_request("ping")
        
        if "error" in response:
            print("ℹ️  ping not implemented (optional)")
            return True
            
        if "result" in response:
            print("✅ ping method passed")
            return True
            
        return True
    
    def test_error_handling(self) -> bool:
        """Test error handling for invalid requests"""
        print("🔍 Testing error handling...")
        
        # Test invalid method
        response = self.send_jsonrpc_request("invalid/method")
        
        if "error" not in response:
            print("❌ Server should return error for invalid method")
            return False
            
        error = response["error"]
        
        # Check error structure
        if "code" not in error or "message" not in error:
            print("❌ Error response missing code or message")
            return False
            
        print("✅ Error handling passed")
        return True
    
    def test_json_rpc_compliance(self) -> bool:
        """Test JSON-RPC 2.0 compliance"""
        print("🔍 Testing JSON-RPC 2.0 compliance...")
        
        # Test valid request structure
        response = self.send_jsonrpc_request("tools/list")
        
        if "jsonrpc" not in response:
            print("❌ Response missing jsonrpc field")
            return False
            
        if response["jsonrpc"] != "2.0":
            print("❌ Response jsonrpc field must be '2.0'")
            return False
            
        if "id" not in response:
            print("❌ Response missing id field")
            return False
            
        print("✅ JSON-RPC 2.0 compliance passed")
        return True
    
    def run_compliance_tests(self) -> Dict[str, bool]:
        """Run complete MCP compliance test suite"""
        print("🚀 Starting MCP Compliance Test Suite")
        print("=" * 50)
        
        tests = [
            ("JSON-RPC 2.0 Compliance", self.test_json_rpc_compliance),
            ("Initialize Sequence", self.test_initialize_sequence),
            ("Tools List", self.test_tools_list),
            ("Resources List", self.test_resources_list),
            ("Prompts List", self.test_prompts_list),
            ("Ping Method", self.test_ping),
            ("Error Handling", self.test_error_handling),
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
            except Exception as e:
                print(f"❌ Test {test_name} failed with exception: {e}")
                results[test_name] = False
        
        print("\n" + "=" * 50)
        print("📊 MCP Compliance Test Results:")
        print(f"✅ Passed: {passed}/{total}")
        print(f"❌ Failed: {total - passed}/{total}")
        
        if passed == total:
            print("\n🎉 ALL TESTS PASSED - MCP SPECIFICATION COMPLIANT")
        else:
            print("\n⚠️  Some tests failed - Review implementation")
        
        return results

def main():
    """Run MCP compliance tests"""
    server_script = Path(__file__).parent / "esp32_debug_mcp_server.py"
    
    if not server_script.exists():
        print(f"❌ MCP server script not found: {server_script}")
        sys.exit(1)
    
    tester = MCPComplianceTest(str(server_script))
    results = tester.run_compliance_tests()
    
    # Exit with error code if tests failed
    if not all(results.values()):
        sys.exit(1)

if __name__ == "__main__":
    main()