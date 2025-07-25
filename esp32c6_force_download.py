#!/usr/bin/env python3
"""
ESP32-C6 Force Download Mode Recovery
Hardware-level recovery for completely unresponsive ESP32-C6
"""

import serial
import time
import subprocess
import sys

def force_download_mode(port="/dev/ttyACM0"):
    """Force ESP32-C6 into download mode using hardware control"""
    print("🔧 Forcing ESP32-C6 into download mode...")
    
    try:
        # Open serial port with specific settings for ESP32-C6
        ser = serial.Serial(port, 115200, timeout=0.5)
        
        print("📍 Applying download mode sequence...")
        
        # ESP32-C6 specific download mode sequence
        # RTS = RESET, DTR = GPIO9 (BOOT)
        
        # Hold both reset and boot
        ser.setRTS(True)   # Assert RESET (low)
        ser.setDTR(True)   # Assert GPIO9/BOOT (low) 
        time.sleep(0.5)
        
        # Release reset while keeping boot low
        ser.setRTS(False)  # Release RESET
        time.sleep(0.2)
        
        # Release boot
        ser.setDTR(False)  # Release GPIO9/BOOT
        time.sleep(0.5)
        
        # Additional reset pulse
        ser.setRTS(True)   
        time.sleep(0.1)
        ser.setRTS(False)
        time.sleep(1.0)
        
        ser.close()
        print("✅ Download mode sequence completed")
        return True
        
    except Exception as e:
        print(f"❌ Failed to control download mode: {e}")
        return False

def test_download_mode(port="/dev/ttyACM0"):
    """Test if device is responding in download mode"""
    print("🔍 Testing download mode response...")
    
    try:
        # Try esptool with reduced baud rate for stability
        cmd = [
            'python', '-m', 'esptool',
            '--chip', 'esp32c6',
            '--port', port,
            '--baud', '9600',
            '--before', 'no_reset',
            '--after', 'no_reset',
            'chip_id'
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        
        if result.returncode == 0:
            print("✅ Device responding in download mode!")
            return True
        else:
            print(f"⚠️  Download mode test failed: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("⏱️  Download mode test timeout")
        return False
    except Exception as e:
        print(f"❌ Download mode test error: {e}")
        return False

def force_flash_erase(port="/dev/ttyACM0"):
    """Force flash erase in download mode"""
    print("🔥 Attempting forced flash erase...")
    
    try:
        cmd = [
            'python', '-m', 'esptool',
            '--chip', 'esp32c6',
            '--port', port,
            '--baud', '9600',
            '--before', 'no_reset',
            '--after', 'no_reset',
            'erase_flash'
        ]
        
        print("Executing flash erase...")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            print("✅ Flash erase completed successfully!")
            print(result.stdout)
            return True
        else:
            print(f"❌ Flash erase failed: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("⏱️  Flash erase timeout")
        return False
    except Exception as e:
        print(f"❌ Flash erase error: {e}")
        return False

def flash_recovery_firmware(port="/dev/ttyACM0"):
    """Flash the recovery firmware"""
    print("💾 Flashing recovery firmware...")
    
    build_dir = "/home/rds/vesc_express/build"
    
    try:
        cmd = [
            'python', '-m', 'esptool',
            '--chip', 'esp32c6',
            '--port', port,
            '--baud', '9600',
            '--before', 'no_reset',
            '--after', 'hard_reset',
            'write_flash',
            '--flash_mode', 'dio',
            '--flash_freq', '80m',
            '--flash_size', '8MB',
            '0x0', f'{build_dir}/bootloader/bootloader.bin',
            '0x8000', f'{build_dir}/partition_table/partition-table.bin',
            '0xf000', f'{build_dir}/ota_data_initial.bin',
            '0x20000', f'{build_dir}/vesc_express.bin'
        ]
        
        print("Flashing firmware...")
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, 
                                 universal_newlines=True)
        
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                print(output.strip())
        
        rc = process.poll()
        
        if rc == 0:
            print("✅ Firmware flash completed successfully!")
            return True
        else:
            print(f"❌ Firmware flash failed with code {rc}")
            return False
            
    except Exception as e:
        print(f"❌ Flash error: {e}")
        return False

def main():
    print("ESP32-C6 Force Download Mode Recovery")
    print("=" * 50)
    
    port = "/dev/ttyACM0"
    
    # Step 1: Force download mode
    for attempt in range(5):
        print(f"\n🔄 Download mode attempt {attempt + 1}/5")
        
        if force_download_mode(port):
            time.sleep(2)
            
            if test_download_mode(port):
                break
        
        if attempt < 4:
            print("⏳ Waiting before retry...")
            time.sleep(3)
    else:
        print("❌ Failed to enter download mode after 5 attempts")
        print("💡 Try manual reset: Hold BOOT button, press RESET, release BOOT")
        return 1
    
    # Step 2: Flash erase
    if not force_flash_erase(port):
        print("❌ Flash erase failed")
        return 1
    
    # Step 3: Flash recovery firmware  
    if not flash_recovery_firmware(port):
        print("❌ Recovery flash failed")
        return 1
    
    print("\n🎉 ESP32-C6 Recovery Completed Successfully!")
    print("✅ Device should now boot with 8MB OTA configuration")
    return 0

if __name__ == "__main__":
    sys.exit(main())