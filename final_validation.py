#!/usr/bin/env python3
"""
Final validation script for the refactored tool discoverability system.
"""

import subprocess
import sys
import json
from pathlib import Path


def parse_json_output(stdout: str) -> dict:
    """Parse JSON output from mixed stdout content."""
    try:
        json_start = stdout.find('{')
        json_end = stdout.rfind('}') + 1
        
        if json_start >= 0 and json_end > json_start:
            json_str = stdout[json_start:json_end]
            return json.loads(json_str)
    except json.JSONDecodeError:
        pass
    return {}


def main():
    """Run final validation."""
    print("🎯 Final Refactoring Validation")
    print("=" * 40)
    
    tests = []
    
    # Test 1: Basic functionality
    print("1. Testing basic functionality...")
    result = subprocess.run([
        sys.executable, 'tool_discoverability_enhancer.py', 
        'finaltest', '--convenience-script', '--target-directory', './final_test'
    ], capture_output=True, text=True)
    
    if result.returncode == 0:
        output_data = parse_json_output(result.stdout)
        if output_data.get('success', False):
            tests.append(("Basic functionality", True))
            print("   ✅ PASSED")
        else:
            tests.append(("Basic functionality", False))
            print("   ❌ FAILED")
    else:
        tests.append(("Basic functionality", False))
        print(f"   ❌ FAILED: {result.stderr}")
    
    # Test 2: Full enhancement
    print("2. Testing full enhancement...")
    result = subprocess.run([
        sys.executable, 'tool_discoverability_enhancer.py',
        'finaltest_full', '--full', '--target-directory', './final_test_full'
    ], capture_output=True, text=True)
    
    if result.returncode == 0:
        output_data = parse_json_output(result.stdout)
        patterns = len(output_data.get('patterns_applied', []))
        files = len(output_data.get('files_created', []))
        
        if output_data.get('success', False) and patterns >= 5 and files >= 10:
            tests.append(("Full enhancement", True))
            print(f"   ✅ PASSED ({patterns} patterns, {files} files)")
        else:
            tests.append(("Full enhancement", False))
            print(f"   ❌ FAILED (patterns: {patterns}, files: {files})")
    else:
        tests.append(("Full enhancement", False))
        print(f"   ❌ FAILED: {result.stderr}")
    
    # Test 3: Slash command
    print("3. Testing slash command...")
    # Create directory first
    Path('./final_test_slash2').mkdir(exist_ok=True)
    result = subprocess.run([
        sys.executable, 'tool_discoverability_fix_slash_command.py',
        'finaltest_slash2', '--convenience-script', '--target-directory', './final_test_slash2'
    ], capture_output=True, text=True)
    
    if result.returncode == 0:
        output_data = parse_json_output(result.stdout)
        if output_data.get('success', False):
            tests.append(("Slash command", True))
            print("   ✅ PASSED")
        else:
            tests.append(("Slash command", False))
            print("   ❌ FAILED")
    else:
        tests.append(("Slash command", False))
        print(f"   ❌ FAILED: {result.stderr}")
    
    # Test 4: Syntax and imports
    print("4. Testing syntax and imports...")
    try:
        import tool_discoverability_enhancer
        import tool_discoverability_templates
        import tool_discoverability_generators
        tests.append(("Module imports", True))
        print("   ✅ PASSED")
    except Exception as e:
        tests.append(("Module imports", False))
        print(f"   ❌ FAILED: {e}")
    
    # Results summary
    print("\n" + "=" * 40)
    print("FINAL VALIDATION RESULTS")
    print("=" * 40)
    
    passed = sum(1 for _, success in tests if success)
    total = len(tests)
    success_rate = (passed / total) * 100
    
    for test_name, success in tests:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"  {test_name}: {status}")
    
    print(f"\nSUCCESS RATE: {passed}/{total} ({success_rate:.0f}%)")
    
    if success_rate >= 90:
        print("🎉 REFACTORING VALIDATION: ✅ SUCCESSFUL")
        return 0
    else:
        print("❌ REFACTORING VALIDATION: ❌ FAILED")
        return 1


if __name__ == "__main__":
    sys.exit(main())