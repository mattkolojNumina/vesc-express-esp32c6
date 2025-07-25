#!/usr/bin/env python3
"""
Simple BLE Scanner using Python bleak library
Scans for VESC Express BLE device
"""

import asyncio
import sys

try:
    from bleak import BleakScanner
    bleak_available = True
except ImportError:
    bleak_available = False

async def scan_for_vesc():
    """Scan for VESC Express BLE device"""
    print("🔍 Scanning for BLE devices...")
    print("📱 Looking for: VESC Express")
    print()
    
    try:
        devices = await BleakScanner.discover(timeout=10.0)
        
        vesc_found = False
        print(f"📋 Found {len(devices)} BLE devices:")
        
        for device in devices:
            name = device.name or "Unknown"
            print(f"  • {name} [{device.address}] RSSI: {device.rssi}dBm")
            
            if any(keyword in name.lower() for keyword in ['vesc', 'express']):
                print(f"    ✅ FOUND VESC EXPRESS DEVICE!")
                vesc_found = True
                
        if not vesc_found:
            print()
            print("❌ VESC Express device not found")
            print("💡 Possible issues:")
            print("   • ESP32-C6 BLE not advertising")
            print("   • Device name might be different")
            print("   • BLE initialization failed")
        else:
            print()
            print("✅ VESC Express BLE device is advertising successfully!")
            
    except Exception as e:
        print(f"❌ BLE scan error: {e}")
        return False
        
    return vesc_found

def main():
    if not bleak_available:
        print("❌ Python 'bleak' library not available")
        print("💡 Install with: pip install bleak")
        print()
        print("🔄 Using alternative scan method...")
        
        # Alternative using hcitool
        import subprocess
        try:
            print("🔍 Using hcitool lescan...")
            result = subprocess.run(['timeout', '10', 'sudo', 'hcitool', 'lescan'], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                print("📋 BLE scan results:")
                for line in result.stdout.split('\n'):
                    if line.strip() and 'LE Scan' not in line:
                        print(f"  • {line.strip()}")
                        if 'vesc' in line.lower() or 'express' in line.lower():
                            print("    ✅ FOUND VESC EXPRESS!")
            else:
                print(f"❌ hcitool scan failed: {result.stderr}")
                
        except Exception as e:
            print(f"❌ Alternative scan failed: {e}")
            print()
            print("🔧 Manual check recommendations:")
            print("   1. Use Android/iOS BLE scanner app")
            print("   2. Look for 'VESC Express' device")
            print("   3. Check ESP32-C6 is running and BLE enabled")
        
        return 0
    
    # Run async scan
    try:
        vesc_found = asyncio.run(scan_for_vesc())
        return 0 if vesc_found else 1
    except Exception as e:
        print(f"❌ Async scan failed: {e}")
        return 1

if __name__ == "__main__":
    print("🔧 Simple BLE Scanner for VESC Express")
    print("=" * 50)
    sys.exit(main())