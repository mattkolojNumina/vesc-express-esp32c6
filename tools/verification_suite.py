#!/usr/bin/env python3
"""
ESP32-C6 VESC Express Verification Suite
Automated implementation correctness verification
"""

import subprocess
import re
import json
import time
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Dict, List, Tuple, Optional
from datetime import datetime
import hashlib

@dataclass
class VerificationResult:
    """Result of a verification check"""
    test_name: str
    passed: bool
    details: str
    timestamp: str
    score: float = 0.0
    critical: bool = False

class VESCVerificationSuite:
    """Comprehensive verification suite for VESC Express implementation"""
    
    def __init__(self, project_root: Path = None):
        self.project_root = project_root or Path(__file__).parent.parent
        self.results: List[VerificationResult] = []
        self.logs_dir = self.project_root / "logs"
        self.logs_dir.mkdir(exist_ok=True)
        
    def log(self, message: str, level: str = "INFO"):
        """Enhanced logging"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
    
    def add_result(self, test_name: str, passed: bool, details: str, 
                   score: float = 0.0, critical: bool = False):
        """Add verification result"""
        result = VerificationResult(
            test_name=test_name,
            passed=passed,
            details=details,
            timestamp=datetime.now().isoformat(),
            score=score,
            critical=critical
        )
        self.results.append(result)
        
        status = "✅ PASS" if passed else "❌ FAIL"
        criticality = " [CRITICAL]" if critical else ""
        self.log(f"{status}{criticality} {test_name}: {details}")
        
        return result
    
    def verify_build_system(self) -> VerificationResult:
        """Verify build system integrity"""
        self.log("🔍 Verifying build system...")
        
        try:
            # Check CMakeLists.txt
            cmake_file = self.project_root / "main" / "CMakeLists.txt"
            if not cmake_file.exists():
                return self.add_result(
                    "Build System", False,
                    "main/CMakeLists.txt not found", 0.0, True
                )
            
            with open(cmake_file) as f:
                cmake_content = f.read()
            
            # Verify ESP-IDF components
            required_components = [
                "esp_wifi", "bt", "esp_netif", "nvs_flash", "driver", "esp_coex"
            ]
            
            missing_components = []
            for component in required_components:
                if component not in cmake_content:
                    missing_components.append(component)
            
            if missing_components:
                return self.add_result(
                    "Build System", False,
                    f"Missing components: {missing_components}", 0.3, True
                )
            
            # Check for ESP32-C6 specific components
            c6_components = ["esp_adc", "esp_pm", "esp_timer"]
            c6_score = sum(1 for comp in c6_components if comp in cmake_content) / len(c6_components)
            
            return self.add_result(
                "Build System", True,
                f"All required components present, C6 optimization: {c6_score:.1%}",
                0.8 + (c6_score * 0.2)
            )
            
        except Exception as e:
            return self.add_result(
                "Build System", False,
                f"Verification error: {e}", 0.0, True
            )
    
    def verify_esp32c6_features(self) -> List[VerificationResult]:
        """Verify ESP32-C6 specific features"""
        self.log("🔍 Verifying ESP32-C6 features...")
        
        results = []
        
        # Check for ESP32-C6 enhancement files
        c6_files = {
            "hw_devkit_c6.c": "Hardware configuration",
            "hw_devkit_c6.h": "Hardware header",
            "wifi_c6_enhancements.c": "WiFi 6 enhancements",
            "ble_c6_enhancements.c": "BLE 5.3 enhancements",
            "power_management_c6.c": "Power management",
            "ieee802154_c6.c": "IEEE 802.15.4 support",
            "vesc_c6_integration.c": "VESC integration"
        }
        
        for filename, description in c6_files.items():
            filepath = self.project_root / "main" / filename
            if filename.startswith("hw_"):
                filepath = self.project_root / "main" / "hwconf" / filename
            
            exists = filepath.exists()
            results.append(self.add_result(
                f"ESP32-C6 {description}", exists,
                f"File {filename}: {'Found' if exists else 'Missing'}",
                1.0 if exists else 0.0,
                critical=(filename in ["hw_devkit_c6.c", "hw_devkit_c6.h"])
            ))
        
        return results
    
    def verify_android_compatibility(self) -> List[VerificationResult]:
        """Verify Android compatibility implementation"""
        self.log("🔍 Verifying Android compatibility...")
        
        results = []
        
        # Check Android compatibility files
        android_files = [
            "main/android_compat.c",
            "main/android_compat.h",
            "main/test_android_compat.c"
        ]
        
        for filepath in android_files:
            full_path = self.project_root / filepath
            exists = full_path.exists()
            results.append(self.add_result(
                f"Android Compatibility", exists,
                f"File {filepath}: {'Found' if exists else 'Missing'}",
                1.0 if exists else 0.0
            ))
        
        # Check for Android optimization modes in code
        try:
            compat_file = self.project_root / "main" / "android_compat.h"
            if compat_file.exists():
                with open(compat_file) as f:
                    content = f.read()
                
                modes_found = 0
                android_modes = ["ANDROID_COMPAT_DISABLED", "ANDROID_COMPAT_BASIC", "ANDROID_COMPAT_OPTIMIZED"]
                for mode in android_modes:
                    if mode in content:
                        modes_found += 1
                
                results.append(self.add_result(
                    "Android Optimization Modes", modes_found == 3,
                    f"Found {modes_found}/3 Android optimization modes",
                    modes_found / 3.0
                ))
            
        except Exception as e:
            results.append(self.add_result(
                "Android Compatibility Check", False,
                f"Error checking Android features: {e}", 0.0
            ))
        
        return results
    
    def verify_communication_stack(self) -> List[VerificationResult]:
        """Verify communication protocol implementation"""
        self.log("🔍 Verifying communication stack...")
        
        results = []
        
        # Check communication files
        comm_files = {
            "main/comm_wifi.c": "WiFi communication",
            "main/comm_ble.c": "BLE communication", 
            "main/comm_can.c": "CAN communication",
            "main/comm_uart.c": "UART communication",
            "main/commands.c": "Command processing",
            "main/packet.c": "Packet handling"
        }
        
        for filepath, description in comm_files.items():
            full_path = self.project_root / filepath
            exists = full_path.exists()
            
            if exists:
                # Check for ESP32-C6 optimizations
                try:
                    with open(full_path) as f:
                        content = f.read()
                    
                    # Look for stack size optimizations
                    if "4096" in content and "1024" not in content:
                        score = 1.0
                        detail = f"{description}: Found with stack optimizations"
                    elif filepath.endswith("comm_wifi.c") and "udp_multicast" in content:
                        score = 0.8
                        detail = f"{description}: Found, checking stack sizes"
                    else:
                        score = 0.6
                        detail = f"{description}: Found, basic implementation"
                        
                except Exception:
                    score = 0.4
                    detail = f"{description}: Found but couldn't analyze"
            else:
                score = 0.0
                detail = f"{description}: Missing"
            
            results.append(self.add_result(
                f"Communication {description}", exists,
                detail, score,
                critical=(filepath in ["main/commands.c", "main/packet.c"])
            ))
        
        return results
    
    def verify_lispbm_integration(self) -> VerificationResult:
        """Verify LispBM integration"""
        self.log("🔍 Verifying LispBM integration...")
        
        try:
            # Check LispBM directory
            lispbm_dir = self.project_root / "main" / "lispBM"
            if not lispbm_dir.exists():
                return self.add_result(
                    "LispBM Integration", False,
                    "LispBM directory not found", 0.0, True
                )
            
            # Check for VESC extensions
            extensions_file = self.project_root / "main" / "lispif_vesc_extensions.c"
            if not extensions_file.exists():
                return self.add_result(
                    "LispBM Integration", False,
                    "VESC extensions file not found", 0.2, True
                )
            
            # Check for test suite
            test_dir = lispbm_dir / "vesc_express_tests"
            test_score = 1.0 if test_dir.exists() else 0.7
            
            return self.add_result(
                "LispBM Integration", True,
                f"LispBM integrated with {'test suite' if test_score == 1.0 else 'basic functionality'}",
                test_score
            )
            
        except Exception as e:
            return self.add_result(
                "LispBM Integration", False,
                f"Verification error: {e}", 0.0, True
            )
    
    def verify_security_implementation(self) -> List[VerificationResult]:
        """Verify security features implementation"""
        self.log("🔍 Verifying security implementation...")
        
        results = []
        
        # Check for security-related configurations
        security_patterns = {
            "WPA3": "WiFi WPA3 security",
            "PMF": "Protected Management Frames",
            "secure_boot": "Secure boot configuration", 
            "flash_encryption": "Flash encryption",
            "esp_encrypted": "ESP encryption features"
        }
        
        # Search in configuration and source files
        search_files = [
            "sdkconfig",
            "main/comm_wifi.c",
            "main/conf_general.h"
        ]
        
        found_features = []
        
        for filepath in search_files:
            full_path = self.project_root / filepath
            if full_path.exists():
                try:
                    with open(full_path) as f:
                        content = f.read().lower()
                    
                    for pattern, description in security_patterns.items():
                        if pattern.lower() in content:
                            found_features.append(description)
                            
                except Exception:
                    continue
        
        # Remove duplicates
        found_features = list(set(found_features))
        
        security_score = len(found_features) / len(security_patterns)
        
        results.append(self.add_result(
            "Security Features", len(found_features) > 0,
            f"Found {len(found_features)}/{len(security_patterns)} security features: {', '.join(found_features)}",
            security_score
        ))
        
        return results
    
    def verify_memory_optimization(self) -> VerificationResult:
        """Verify memory usage optimization"""
        self.log("🔍 Verifying memory optimization...")
        
        try:
            # Check if build exists to analyze memory usage
            build_dir = self.project_root / "build"
            map_file = build_dir / "vesc_express.map"
            
            if not map_file.exists():
                return self.add_result(
                    "Memory Optimization", False,
                    "Build map file not available for analysis", 0.0
                )
            
            # Analyze binary size
            bin_file = build_dir / "vesc_express.bin"
            if bin_file.exists():
                bin_size = bin_file.stat().st_size
                
                # Optimal size for ESP32-C6 (4MB flash)
                # Target: < 1.5MB for good utilization
                if bin_size < 1024 * 1024:  # < 1MB
                    score = 1.0
                    detail = f"Excellent size: {bin_size:,} bytes"
                elif bin_size < 1536 * 1024:  # < 1.5MB
                    score = 0.8
                    detail = f"Good size: {bin_size:,} bytes"
                elif bin_size < 2048 * 1024:  # < 2MB
                    score = 0.6
                    detail = f"Acceptable size: {bin_size:,} bytes"
                else:
                    score = 0.3
                    detail = f"Large size: {bin_size:,} bytes"
                
                return self.add_result(
                    "Memory Optimization", score > 0.5,
                    detail, score
                )
            
            return self.add_result(
                "Memory Optimization", False,
                "Binary file not available for analysis", 0.0
            )
            
        except Exception as e:
            return self.add_result(
                "Memory Optimization", False,
                f"Analysis error: {e}", 0.0
            )
    
    def verify_documentation(self) -> List[VerificationResult]:
        """Verify documentation completeness"""
        self.log("🔍 Verifying documentation...")
        
        results = []
        
        # Check for key documentation files
        doc_files = {
            "README_ESP32C6.md": "Main project README",
            "ANDROID_COMPATIBILITY_REPORT.md": "Android compatibility guide",
            "ESP32_C6_CONFIGURATION_GUIDE.md": "Configuration documentation",
            "PRODUCTION_DEPLOYMENT_SUMMARY.md": "Deployment guide",
            "WSL2_JTAG_DEBUGGING_SETUP.md": "Debugging setup guide"
        }
        
        for filename, description in doc_files.items():
            filepath = self.project_root / filename
            exists = filepath.exists()
            
            if exists:
                # Check documentation quality (basic length check)
                try:
                    with open(filepath) as f:
                        content = f.read()
                    
                    if len(content) > 1000:  # Substantial documentation
                        score = 1.0
                        detail = f"{description}: Complete ({len(content):,} chars)"
                    elif len(content) > 500:  # Basic documentation
                        score = 0.7
                        detail = f"{description}: Basic ({len(content):,} chars)"
                    else:  # Minimal documentation
                        score = 0.4
                        detail = f"{description}: Minimal ({len(content):,} chars)"
                        
                except Exception:
                    score = 0.3
                    detail = f"{description}: Found but unreadable"
            else:
                score = 0.0
                detail = f"{description}: Missing"
            
            results.append(self.add_result(
                f"Documentation", exists and score > 0.5,
                detail, score,
                critical=(filename == "README_ESP32C6.md")
            ))
        
        return results
    
    def run_comprehensive_verification(self) -> Dict[str, any]:
        """Run complete verification suite"""
        self.log("🚀 Starting comprehensive verification suite...")
        
        start_time = time.time()
        
        # Run all verification tests
        verification_tests = [
            ("Build System", self.verify_build_system),
            ("ESP32-C6 Features", self.verify_esp32c6_features),
            ("Android Compatibility", self.verify_android_compatibility),
            ("Communication Stack", self.verify_communication_stack),
            ("LispBM Integration", self.verify_lispbm_integration),
            ("Security Implementation", self.verify_security_implementation),
            ("Memory Optimization", self.verify_memory_optimization),
            ("Documentation", self.verify_documentation)
        ]
        
        for test_name, test_func in verification_tests:
            try:
                self.log(f"Running {test_name} verification...")
                result = test_func()
                
                # Handle both single results and lists
                if not isinstance(result, list):
                    result = [result]
                    
            except Exception as e:
                self.log(f"❌ {test_name} verification failed: {e}", "ERROR")
                self.add_result(test_name, False, f"Test execution error: {e}", 0.0, True)
        
        # Calculate overall scores
        execution_time = time.time() - start_time
        
        # Overall statistics
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r.passed)
        critical_failed = sum(1 for r in self.results if not r.passed and r.critical)
        
        average_score = sum(r.score for r in self.results) / total_tests if total_tests > 0 else 0
        
        # Determine overall status
        if critical_failed > 0:
            overall_status = "CRITICAL_ISSUES"
        elif passed_tests / total_tests >= 0.8:
            overall_status = "PASSED"
        elif passed_tests / total_tests >= 0.6:
            overall_status = "WARNINGS"
        else:
            overall_status = "FAILED"
        
        # Create summary
        summary = {
            "timestamp": datetime.now().isoformat(),
            "execution_time": execution_time,
            "overall_status": overall_status,
            "statistics": {
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": total_tests - passed_tests,
                "critical_failures": critical_failed,
                "pass_rate": passed_tests / total_tests if total_tests > 0 else 0,
                "average_score": average_score
            },
            "results": [asdict(r) for r in self.results]
        }
        
        # Log summary
        self.log("="*60)
        self.log(f"📊 VERIFICATION COMPLETE - Status: {overall_status}")
        self.log(f"🎯 Tests: {passed_tests}/{total_tests} passed ({summary['statistics']['pass_rate']:.1%})")
        self.log(f"⭐ Average Score: {average_score:.2f}/1.0")
        self.log(f"⏱️  Execution Time: {execution_time:.1f}s")
        
        if critical_failed > 0:
            self.log(f"🚨 CRITICAL: {critical_failed} critical test(s) failed!", "ERROR")
        
        # Save results
        results_file = self.logs_dir / f"verification_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(results_file, "w") as f:
            json.dump(summary, f, indent=2, default=str)
        
        self.log(f"📄 Results saved to {results_file}")
        
        return summary

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="ESP32-C6 VESC Express Verification Suite")
    parser.add_argument("--project-root", type=Path, help="Project root directory")
    parser.add_argument("--test", choices=[
        "build", "esp32c6", "android", "comm", "lispbm", 
        "security", "memory", "docs", "all"
    ], default="all", help="Specific test to run")
    
    args = parser.parse_args()
    
    suite = VESCVerificationSuite(args.project_root)
    
    try:
        if args.test == "all":
            results = suite.run_comprehensive_verification()
            exit_code = 0 if results["overall_status"] in ["PASSED", "WARNINGS"] else 1
        else:
            # Run specific test
            test_map = {
                "build": suite.verify_build_system,
                "esp32c6": suite.verify_esp32c6_features,
                "android": suite.verify_android_compatibility,
                "comm": suite.verify_communication_stack,
                "lispbm": suite.verify_lispbm_integration,
                "security": suite.verify_security_implementation,
                "memory": suite.verify_memory_optimization,
                "docs": suite.verify_documentation
            }
            
            result = test_map[args.test]()
            if isinstance(result, list):
                exit_code = 0 if all(r.passed for r in result) else 1
            else:
                exit_code = 0 if result.passed else 1
        
        exit(exit_code)
        
    except KeyboardInterrupt:
        suite.log("🛑 Verification cancelled by user")
        exit(130)
    except Exception as e:
        suite.log(f"💥 Unexpected error: {e}", "ERROR")
        exit(1)

if __name__ == "__main__":
    main()