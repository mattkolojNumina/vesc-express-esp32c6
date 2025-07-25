#!/usr/bin/env python3
"""
Patch VESC Tool to add ESP32-C6 support
"""

import os

file_path = "vesc_tool/vesc_tool_official/mobile/fwhelper.cpp"

# Read the original file
try:
    with open(file_path, 'r') as f:
        content = f.read()
    
    print(f"✅ Found file: {file_path}")
    
    # Find the insertion point (after VL Link entry)
    target = '    } else if (params.hw == "VL Link") {\n        hws.insert(params.hw, "://res/firmwares_esp/ESP32-C3/VL Link");\n    }'
    
    if target in content:
        # Add ESP32-C6 support
        replacement = target + '\n    } else if (params.hw == "ESP32-C6-DevKitM-1") {\n        hws.insert(params.hw, "://res/firmwares_esp/ESP32-C6/DevKitM-1");\n    } else if (params.hw == "ESP32-C6 VESC Express") {\n        hws.insert(params.hw, "://res/firmwares_esp/ESP32-C6/VESC Express");'
        
        # Apply the patch
        patched_content = content.replace(target, replacement)
        
        # Create backup
        with open(file_path + ".backup", 'w') as f:
            f.write(content)
        print(f"✅ Created backup: {file_path}.backup")
        
        # Write patched file
        with open(file_path, 'w') as f:
            f.write(patched_content)
        print(f"✅ Applied ESP32-C6 patch to {file_path}")
        
        # Verify the change
        if "ESP32-C6-DevKitM-1" in patched_content:
            print("✅ ESP32-C6 support successfully added!")
        else:
            print("❌ Patch verification failed")
            
    else:
        print(f"❌ Target string not found in {file_path}")
        print("File might have different structure than expected")
        
except FileNotFoundError:
    print(f"❌ File not found: {file_path}")
    print("Current directory:", os.getcwd())
    print("Available files:")
    if os.path.exists("vesc_tool_official"):
        for root, dirs, files in os.walk("vesc_tool_official"):
            for file in files:
                if "fwhelper" in file:
                    print(f"  Found: {os.path.join(root, file)}")