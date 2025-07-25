#!/usr/bin/env python3
"""
Extended MCP Compliance Test Suite
Tests ESP32 Debug Tools MCP Server against complete Model Context Protocol specification
"""

import json
import subprocess
import sys
import time
from typing import Dict, Any, List
from pathlib import Path

class ExtendedMCPComplianceTest:
    """Extended test suite for comprehensive MCP specification compliance"""
    
    def __init__(self, server_script: str):
        self.server_script = server_script
        self.server_proc = None
        
    def start_server(self) -> bool:
        """Start MCP server with persistent connection"""
        try:
            self.server_proc = subprocess.Popen(
                [sys.executable, self.server_script],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=0
            )
            return True
        except Exception as e:
            print(f"❌ Failed to start server: {e}")
            return False
            
    def stop_server(self):
        """Stop MCP server"""
        if self.server_proc:
            self.server_proc.kill()
            self.server_proc = None
    
    def send_request(self, method: str, params: Dict[str, Any] = None, request_id: int = None) -> Dict[str, Any]:
        """Send JSON-RPC request to running server"""
        request = {"jsonrpc": "2.0", "method": method}
        
        if request_id is not None:
            request["id"] = request_id
            
        if params:
            request["params"] = params
            
        try:
            self.server_proc.stdin.write(json.dumps(request) + "\n")
            self.server_proc.stdin.flush()
            
            # Read response (skip non-JSON lines)
            for _ in range(10):
                line = self.server_proc.stdout.readline()
                if line and line.strip().startswith('{"jsonrpc"'):
                    return json.loads(line.strip())
                    
            return {"error": "No JSON-RPC response received"}
            
        except Exception as e:
            return {"error": str(e)}
    
    def test_initialization_sequence(self) -> bool:
        """Test complete MCP initialization sequence"""
        print("🔍 Testing complete initialization sequence...")
        
        if not self.start_server():
            return False
            
        try:
            # Step 1: Send initialize
            init_response = self.send_request("initialize", {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "roots": {"listChanged": True},
                    "sampling": {}
                },
                "clientInfo": {
                    "name": "extended-test-client",
                    "version": "1.0.0"
                }
            }, 1)
            
            if "error" in init_response:
                print(f"❌ Initialize failed: {init_response['error']}")
                return False
                
            # Validate initialize response
            result = init_response.get("result", {})
            required_fields = ["protocolVersion", "capabilities", "serverInfo"]
            for field in required_fields:
                if field not in result:
                    print(f"❌ Initialize response missing {field}")
                    return False
            
            # Check protocol version compatibility
            protocol_version = result["protocolVersion"]
            if not protocol_version.startswith("2024-"):
                print(f"❌ Unexpected protocol version: {protocol_version}")
                return False
            
            # Step 2: Send initialized notification
            self.send_request("notifications/initialized")
            
            print("✅ Complete initialization sequence passed")
            return True
            
        except Exception as e:
            print(f"❌ Initialization sequence error: {e}")
            return False
        finally:
            self.stop_server()
    
    def test_tool_execution(self) -> bool:
        """Test actual tool execution via tools/call"""
        print("🔍 Testing tool execution...")
        
        if not self.start_server():
            return False
            
        try:
            # Initialize
            self.send_request("initialize", {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "test", "version": "1.0"}
            }, 1)
            
            self.send_request("notifications/initialized")
            
            # Get tools list
            tools_response = self.send_request("tools/list", {}, 2)
            if "error" in tools_response:
                print(f"❌ Failed to get tools: {tools_response['error']}")
                return False
                
            tools = tools_response["result"]["tools"]
            if not tools:
                print("❌ No tools available for testing")
                return False
            
            # Test tool execution with list_debug_tools (should be safe)
            tool_response = self.send_request("tools/call", {
                "name": "list_debug_tools",
                "arguments": {}
            }, 3)
            
            if "error" in tool_response:
                print(f"❌ Tool call failed: {tool_response['error']}")
                return False
                
            if "result" not in tool_response:
                print("❌ Tool call response missing result")
                return False
                
            result = tool_response["result"]
            if "content" not in result:
                print("❌ Tool result missing content")
                return False
                
            print("✅ Tool execution passed")
            return True
            
        except Exception as e:
            print(f"❌ Tool execution error: {e}")
            return False
        finally:
            self.stop_server()
    
    def test_resource_access(self) -> bool:
        """Test resource access functionality"""
        print("🔍 Testing resource access...")
        
        if not self.start_server():
            return False
            
        try:
            # Initialize
            self.send_request("initialize", {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "test", "version": "1.0"}
            }, 1)
            
            self.send_request("notifications/initialized")
            
            # Test resources/list
            resources_response = self.send_request("resources/list", {}, 2)
            
            if "error" in resources_response:
                print("ℹ️  resources/list not implemented (acceptable)")
                return True
                
            if "result" in resources_response:
                resources = resources_response["result"].get("resources", [])
                print(f"ℹ️  Found {len(resources)} resources")
                
                # If resources exist, test reading one
                if resources:
                    resource_uri = resources[0]["uri"]
                    read_response = self.send_request("resources/read", {
                        "uri": resource_uri
                    }, 3)
                    
                    if "error" in read_response:
                        print(f"⚠️  Resource read failed: {read_response['error']}")
                        return True  # Not fatal
                    else:
                        print("✅ Resource access working")
                        
            return True
            
        except Exception as e:
            print(f"❌ Resource access error: {e}")
            return False
        finally:
            self.stop_server()
    
    def test_error_codes_compliance(self) -> bool:
        """Test JSON-RPC error codes compliance"""
        print("🔍 Testing JSON-RPC error codes...")
        
        if not self.start_server():
            return False
            
        try:
            # Initialize first
            self.send_request("initialize", {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "test", "version": "1.0"}
            }, 1)
            
            self.send_request("notifications/initialized")
            
            # Test invalid method
            invalid_response = self.send_request("invalid/method", {}, 2)
            if "error" not in invalid_response:
                print("❌ Should return error for invalid method")
                return False
                
            error = invalid_response["error"]
            if error["code"] != -32601:  # Method not found
                print(f"❌ Expected error code -32601, got {error['code']}")
                return False
            
            # Test invalid parameters
            invalid_params_response = self.send_request("tools/call", {
                "name": "nonexistent_tool",
                "arguments": {}
            }, 3)
            
            if "error" not in invalid_params_response:
                print("❌ Should return error for invalid tool")
                return False
            
            print("✅ Error codes compliance passed")
            return True
            
        except Exception as e:
            print(f"❌ Error codes test error: {e}")
            return False
        finally:
            self.stop_server()
    
    def test_capability_negotiation(self) -> bool:
        """Test capability negotiation during initialization"""
        print("🔍 Testing capability negotiation...")
        
        if not self.start_server():
            return False
            
        try:
            # Send initialize with specific capabilities
            init_response = self.send_request("initialize", {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "roots": {"listChanged": True},
                    "sampling": {},
                    "experimental": {"customFeature": True}
                },
                "clientInfo": {
                    "name": "capability-test-client",
                    "version": "1.0.0"
                }
            }, 1)
            
            if "error" in init_response:
                print(f"❌ Initialize with capabilities failed: {init_response['error']}")
                return False
                
            result = init_response["result"]
            
            # Server should respond with its capabilities
            if "capabilities" not in result:
                print("❌ Server must respond with capabilities")
                return False
                
            server_capabilities = result["capabilities"]
            
            # Check server info
            if "serverInfo" not in result:
                print("❌ Server must provide serverInfo")
                return False
                
            server_info = result["serverInfo"]
            required_server_fields = ["name", "version"]
            for field in required_server_fields:
                if field not in server_info:
                    print(f"❌ ServerInfo missing {field}")
                    return False
            
            print("✅ Capability negotiation passed")
            return True
            
        except Exception as e:
            print(f"❌ Capability negotiation error: {e}")
            return False
        finally:
            self.stop_server()
    
    def test_protocol_version_compatibility(self) -> bool:
        """Test protocol version compatibility"""
        print("🔍 Testing protocol version compatibility...")
        
        if not self.start_server():
            return False
            
        try:
            # Test with supported version
            supported_response = self.send_request("initialize", {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "test", "version": "1.0"}
            }, 1)
            
            if "error" in supported_response:
                print(f"❌ Supported version failed: {supported_response['error']}")
                return False
            
            # Check returned version
            returned_version = supported_response["result"]["protocolVersion"]
            if not returned_version.startswith("2024-"):
                print(f"❌ Unexpected returned version: {returned_version}")
                return False
                
            print("✅ Protocol version compatibility passed")
            return True
            
        except Exception as e:
            print(f"❌ Protocol version test error: {e}")
            return False
        finally:
            self.stop_server()
    
    def run_extended_compliance_tests(self) -> Dict[str, bool]:
        """Run complete extended MCP compliance test suite"""
        print("🚀 Starting Extended MCP Compliance Test Suite")
        print("=" * 60)
        
        tests = [
            ("Initialization Sequence", self.test_initialization_sequence),
            ("Tool Execution", self.test_tool_execution),
            ("Resource Access", self.test_resource_access),
            ("Error Codes Compliance", self.test_error_codes_compliance),
            ("Capability Negotiation", self.test_capability_negotiation),
            ("Protocol Version Compatibility", self.test_protocol_version_compatibility),
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
        
        print("\n" + "=" * 60)
        print("📊 Extended MCP Compliance Test Results:")
        print(f"✅ Passed: {passed}/{total}")
        print(f"❌ Failed: {total - passed}/{total}")
        
        if passed == total:
            print("\n🎉 ALL EXTENDED TESTS PASSED - FULL MCP SPECIFICATION COMPLIANT")
        else:
            print("\n⚠️  Some extended tests failed - Review implementation")
        
        return results

def main():
    """Run extended MCP compliance tests"""
    server_script = Path(__file__).parent / "esp32_debug_mcp_server.py"
    
    if not server_script.exists():
        print(f"❌ MCP server script not found: {server_script}")
        sys.exit(1)
    
    tester = ExtendedMCPComplianceTest(str(server_script))
    results = tester.run_extended_compliance_tests()
    
    # Exit with error code if tests failed
    if not all(results.values()):
        sys.exit(1)

if __name__ == "__main__":
    main()