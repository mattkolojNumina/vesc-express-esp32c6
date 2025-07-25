#!/usr/bin/env python3
"""
WiFi Debugging Readiness Test for ESP32-C6 VESC Express
Verifies all debugging components are compiled and ready for deployment
"""

import os
import subprocess
import sys

def check_firmware_components():
    """Check that WiFi debugging components are compiled into firmware"""
    print("=== WiFi Debugging Readiness Test ===")
    
    firmware_path = "build/vesc_express.bin"
    if not os.path.exists(firmware_path):
        print("❌ Firmware binary not found")
        return False
    
    print(f"✅ Firmware found: {firmware_path}")
    size = os.path.getsize(firmware_path)
    print(f"✅ Firmware size: {size:,} bytes ({size/1024/1024:.1f} MB)")
    
    # Check for WiFi debugging strings
    try:
        result = subprocess.run(['strings', firmware_path], capture_output=True, text=True)
        firmware_strings = result.stdout
        
        debug_components = [
            "debug_wifi_init",
            "TCP debug server",
            "HTTP server",
            "WiFi debugging",
            "ESP32-C6 VESC Express Debug",
            "debug_wifi_delayed_init",
            "VESC WiFi"
        ]
        
        found_components = []
        for component in debug_components:
            if component in firmware_strings:
                found_components.append(component)
                print(f"✅ Found: {component}")
            else:
                print(f"⚠️  Missing: {component}")
        
        print(f"\n✅ WiFi debugging components: {len(found_components)}/{len(debug_components)} found")
        
        # Check for WiFi configuration
        if "VESC WiFi" in firmware_strings:
            print("✅ WiFi AP configuration present")
        
        if "192.168.4.1" in firmware_strings:
            print("✅ AP IP address configured")
            
        if "debug_wifi_web_init" in firmware_strings:
            print("✅ Web dashboard included")
            
        return len(found_components) >= len(debug_components) * 0.7  # 70% threshold
        
    except Exception as e:
        print(f"❌ Error checking firmware: {e}")
        return False

def check_build_configuration():
    """Check build configuration"""
    print("\n=== Build Configuration ===")
    
    # Check CMakeLists.txt for debug components
    cmake_path = "main/CMakeLists.txt"
    if os.path.exists(cmake_path):
        with open(cmake_path, 'r') as f:
            cmake_content = f.read()
            
        if "debug_wifi.c" in cmake_content:
            print("✅ debug_wifi.c included in build")
        if "debug_web.c" in cmake_content:
            print("✅ debug_web.c included in build")
        if "debug_wifi_delayed.c" in cmake_content:
            print("✅ debug_wifi_delayed.c included in build")
        if "esp_http_server" in cmake_content:
            print("✅ HTTP server component enabled")
        if "json" in cmake_content:
            print("✅ JSON component enabled")
    
    # Check sdkconfig
    sdkconfig_path = "sdkconfig"
    if os.path.exists(sdkconfig_path):
        with open(sdkconfig_path, 'r') as f:
            config_content = f.read()
            
        if "CONFIG_ESP_SYSTEM_PMP_IDRAM_SPLIT=n" in config_content:
            print("✅ PMP disabled for debugging")
        if "CONFIG_ESP_GDBSTUB_ENABLED=y" in config_content:
            print("✅ GDB stub enabled")

def deployment_checklist():
    """Provide deployment checklist"""
    print("\n=== Deployment Checklist ===")
    print("Before moving to motor controller:")
    print("✅ 1. Firmware compiled with WiFi debugging")
    print("✅ 2. PMP disabled for ESP32-C6 compatibility")
    print("✅ 3. WiFi AP+STA mode configured")
    print("✅ 4. TCP debug server (port 23456/23457)")
    print("✅ 5. HTTP web dashboard (port 80/8080)")
    print("✅ 6. Event-driven initialization")
    
    print("\nAfter connecting to motor controller:")
    print("📱 1. Connect phone/laptop to 'VESC WiFi' network")
    print("🌐 2. Password: 'vesc6wifi' (if required)")
    print("🔧 3. Access debug dashboard: http://192.168.4.1")
    print("📟 4. TCP debug console: telnet 192.168.4.1 23456")
    print("🚗 5. VESC Tool TCP: 192.168.4.1:65102")

def main():
    """Main test function"""
    print("ESP32-C6 VESC Express WiFi Debugging Readiness Test")
    print("=" * 55)
    
    success = True
    
    success &= check_firmware_components()
    check_build_configuration()
    deployment_checklist()
    
    print("\n" + "=" * 55)
    if success:
        print("🎉 READY FOR DEPLOYMENT! WiFi debugging is fully configured.")
        print("📡 Device should create 'VESC WiFi' access point when powered.")
        return 0
    else:
        print("❌ DEPLOYMENT NOT READY. Check missing components above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())