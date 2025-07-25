#!/usr/bin/env python3
"""
Advanced esptool.py Usage Suite
Implementation of research document recommendations for low-level flash operations
"""

import subprocess
import os
import sys
import json
import time
from pathlib import Path
from datetime import datetime

class AdvancedESPTool:
    """
    Advanced esptool.py operations for ESP32-C6 VESC Express
    Based on ESP-IDF research document recommendations
    """
    
    def __init__(self, port="/dev/ttyACM0", baud=115200):
        self.port = port
        self.baud = baud
        self.backup_dir = Path("flash_backups")
        self.backup_dir.mkdir(exist_ok=True)
        
    def run_esptool_command(self, args, description=None):
        """Run esptool.py command with error handling"""
        if description:
            print(f"🔸 {description}")
        
        cmd = ['esptool.py', '-p', self.port, '-b', str(self.baud)] + args
        print(f"💻 Running: {' '.join(cmd)}")
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            print(f"✅ Success")
            if result.stdout.strip():
                print(f"📤 Output: {result.stdout.strip()}")
            return result.stdout
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed: {e}")
            if e.stderr:
                print(f"❌ Error: {e.stderr}")
            return None
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            return None
    
    def demonstrate_chip_info(self):
        """Demonstrate chip identification commands"""
        print("\n🔍 === CHIP IDENTIFICATION ===")
        print("Based on ESP-IDF research document")
        
        # Chip ID
        self.run_esptool_command(['chip_id'], "Get chip ID")
        
        # Flash ID
        self.run_esptool_command(['flash_id'], "Get SPI flash manufacturer and device ID")
        
        # MAC Address
        self.run_esptool_command(['read_mac'], "Read base MAC address from eFuse")
        
        # Flash status
        self.run_esptool_command(['read_flash_status'], "Read SPI flash status register")
    
    def demonstrate_flash_operations(self):
        """Demonstrate flash read/write operations"""
        print("\n💾 === FLASH OPERATIONS ===")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Read flash regions
        flash_reads = [
            (0x0, 0x8000, f"bootloader_{timestamp}.bin", "Bootloader sector"),
            (0x8000, 0x1000, f"partition_table_{timestamp}.bin", "Partition table"),
            (0x9000, 0x6000, f"nvs_{timestamp}.bin", "NVS partition"),
            (0x10000, 0x10000, f"app_sample_{timestamp}.bin", "Application sample (64KB)")
        ]
        
        for addr, size, filename, description in flash_reads:
            backup_file = self.backup_dir / filename
            result = self.run_esptool_command([
                'read_flash', hex(addr), hex(size), str(backup_file)
            ], f"Backup {description} -> {backup_file}")
            
            if result is not None and backup_file.exists():
                file_size = backup_file.stat().st_size
                print(f"   📁 Saved {file_size} bytes to {backup_file}")
    
    def demonstrate_flash_analysis(self):
        """Demonstrate flash analysis and verification"""
        print("\n🔍 === FLASH ANALYSIS ===")
        
        # Read flash SFDP (Serial Flash Discoverable Parameters)
        self.run_esptool_command(['read_flash_sfdp'], "Read flash SFDP information")
        
        # Get security info
        self.run_esptool_command(['get_security_info'], "Get security configuration")
        
        # Dump memory regions
        memory_dumps = [
            (0x40000000, 0x100, "irom_sample.bin", "IROM sample"),
            (0x600fe000, 0x100, "rtc_memory_sample.bin", "RTC memory sample")
        ]
        
        for addr, size, filename, description in memory_dumps:
            dump_file = self.backup_dir / filename
            result = self.run_esptool_command([
                'dump_mem', hex(addr), hex(size), str(dump_file)
            ], f"Dump {description} -> {dump_file}")
    
    def demonstrate_advanced_flashing(self):
        """Demonstrate advanced flashing techniques"""
        print("\n⚡ === ADVANCED FLASHING ===")
        
        # Check if we have build artifacts
        build_dir = Path("build")
        if not build_dir.exists():
            print("⚠️  No build directory found. Run 'idf.py build' first for flashing demos.")
            return
        
        # Find bootloader
        bootloader = build_dir / "bootloader" / "bootloader.bin"
        if bootloader.exists():
            print(f"🔸 Bootloader found: {bootloader}")
            # Demonstrate bootloader-only flash (commented for safety)
            print(f"💡 Bootloader flash command would be:")
            print(f"   esptool.py -p {self.port} write_flash 0x0 {bootloader}")
        
        # Find partition table
        partition_table = build_dir / "partition_table" / "partition-table.bin"
        if partition_table.exists():
            print(f"🔸 Partition table found: {partition_table}")
            print(f"💡 Partition table flash command would be:")
            print(f"   esptool.py -p {self.port} write_flash 0x8000 {partition_table}")
        
        # Find application
        app_files = list(build_dir.glob("*.bin"))
        if app_files:
            app_file = app_files[0]
            print(f"🔸 Application found: {app_file}")
            print(f"💡 Application flash command would be:")
            print(f"   esptool.py -p {self.port} write_flash 0x10000 {app_file}")
    
    def demonstrate_merge_bin(self):
        """Demonstrate binary merging for single-file flashing"""
        print("\n🔄 === BINARY MERGING ===")
        
        build_dir = Path("build")
        if not build_dir.exists():
            print("⚠️  No build directory found. Run 'idf.py build' first.")
            return
        
        # Look for flasher_args.json which contains flash layout
        flasher_args = build_dir / "flasher_args.json"
        if flasher_args.exists():
            print(f"🔸 Found flasher arguments: {flasher_args}")
            
            try:
                with open(flasher_args, 'r') as f:
                    flash_info = json.load(f)
                
                print("📋 Flash layout:")
                flash_files = flash_info.get('flash_files', {})
                for addr, filename in flash_files.items():
                    file_path = build_dir / filename
                    if file_path.exists():
                        size = file_path.stat().st_size
                        print(f"   {addr}: {filename} ({size} bytes)")
                
                # Create merge command
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                merged_file = self.backup_dir / f"merged_firmware_{timestamp}.bin"
                
                merge_args = ['merge_bin', '-o', str(merged_file)]
                for addr, filename in flash_files.items():
                    file_path = build_dir / filename
                    if file_path.exists():
                        merge_args.extend([addr, str(file_path)])
                
                if len(merge_args) > 3:  # Has files to merge
                    result = self.run_esptool_command(
                        merge_args,
                        f"Merge binaries into single file: {merged_file}"
                    )
                    
                    if result is not None and merged_file.exists():
                        size = merged_file.stat().st_size
                        print(f"✅ Merged firmware created: {size} bytes")
                        print(f"💡 Flash merged file with:")
                        print(f"   esptool.py -p {self.port} write_flash 0x0 {merged_file}")
                
            except Exception as e:
                print(f"❌ Failed to parse flasher_args.json: {e}")
        else:
            print("⚠️  No flasher_args.json found. Build project first.")
    
    def demonstrate_erase_operations(self):
        """Demonstrate flash erase operations (CAUTION)"""
        print("\n🗑️  === ERASE OPERATIONS (DEMONSTRATION ONLY) ===")
        print("⚠️  WARNING: These operations are destructive!")
        print("💡 For safety, showing commands without execution")
        
        erase_commands = [
            (['erase_region', '0x9000', '0x6000'], "Erase NVS partition (0x9000-0xF000)"),
            (['erase_flash'], "Erase entire flash (DESTRUCTIVE!)"),
            (['erase_region', '0x10000', '0x100000'], "Erase application partition")
        ]
        
        for cmd_args, description in erase_commands:
            full_cmd = ['esptool.py', '-p', self.port] + cmd_args
            print(f"🔸 {description}")
            print(f"   Command: {' '.join(full_cmd)}")
            print(f"   💡 Execute manually if needed (BE CAREFUL!)")
    
    def create_backup_script(self):
        """Create automated backup script"""
        print("\n💾 === CREATING BACKUP SCRIPT ===")
        
        script_content = f'''#!/bin/bash
# ESP32-C6 Flash Backup Script
# Generated by esptool_advanced_suite.py
# Based on ESP-IDF research document

set -e

PORT="{self.port}"
BAUD="{self.baud}"
BACKUP_DIR="flash_backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

echo "🔄 ESP32-C6 Flash Backup - $TIMESTAMP"
echo "=================================="

mkdir -p $BACKUP_DIR

# Backup critical regions
echo "📦 Backing up bootloader..."
esptool.py -p $PORT -b $BAUD read_flash 0x0 0x8000 "$BACKUP_DIR/bootloader_$TIMESTAMP.bin"

echo "📦 Backing up partition table..."
esptool.py -p $PORT -b $BAUD read_flash 0x8000 0x1000 "$BACKUP_DIR/partition_table_$TIMESTAMP.bin"

echo "📦 Backing up NVS..."
esptool.py -p $PORT -b $BAUD read_flash 0x9000 0x6000 "$BACKUP_DIR/nvs_$TIMESTAMP.bin"

echo "📦 Backing up application (first 1MB)..."
esptool.py -p $PORT -b $BAUD read_flash 0x10000 0x100000 "$BACKUP_DIR/application_$TIMESTAMP.bin"

echo "✅ Backup complete! Files saved in $BACKUP_DIR/"
ls -la $BACKUP_DIR/*$TIMESTAMP*

echo ""
echo "💡 Restore commands:"
echo "   Bootloader:      esptool.py -p $PORT write_flash 0x0 $BACKUP_DIR/bootloader_$TIMESTAMP.bin"
echo "   Partition Table: esptool.py -p $PORT write_flash 0x8000 $BACKUP_DIR/partition_table_$TIMESTAMP.bin"
echo "   NVS:            esptool.py -p $PORT write_flash 0x9000 $BACKUP_DIR/nvs_$TIMESTAMP.bin"
echo "   Application:     esptool.py -p $PORT write_flash 0x10000 $BACKUP_DIR/application_$TIMESTAMP.bin"
'''
        
        script_file = Path("backup_flash.sh")
        with open(script_file, 'w') as f:
            f.write(script_content)
        
        script_file.chmod(0o755)
        print(f"✅ Backup script created: {script_file}")
        print(f"💡 Usage: ./{script_file}")
    
    def run_comprehensive_demo(self):
        """Run complete esptool.py demonstration"""
        print("🎯 Advanced esptool.py Usage Suite")
        print("=" * 40)
        print("Based on ESP-IDF research document")
        print(f"Port: {self.port}, Baud: {self.baud}")
        print()
        
        # Check device connection
        result = self.run_esptool_command(['chip_id'], "Verify device connection")
        if result is None:
            print("❌ Cannot connect to device. Check connection and port.")
            return False
        
        # Run all demonstrations
        self.demonstrate_chip_info()
        self.demonstrate_flash_operations()
        self.demonstrate_flash_analysis()
        self.demonstrate_advanced_flashing()
        self.demonstrate_merge_bin()
        self.demonstrate_erase_operations()
        self.create_backup_script()
        
        # Summary
        print("\n📋 DEMONSTRATION COMPLETE")
        print("=" * 30)
        print("✅ Chip identification")
        print("✅ Flash operations")
        print("✅ Flash analysis")
        print("✅ Advanced flashing techniques")
        print("✅ Binary merging")
        print("✅ Erase operations (demo)")
        print("✅ Backup script generation")
        
        if self.backup_dir.exists():
            backups = list(self.backup_dir.glob('*'))
            if backups:
                print(f"\n📁 Backup files created: {len(backups)}")
                for backup in sorted(backups)[-5:]:  # Show last 5
                    size = backup.stat().st_size
                    print(f"   📄 {backup.name} ({size} bytes)")
        
        print("\n🎉 All esptool.py demonstrations complete!")
        print("📚 Based on ESP-IDF research document recommendations")
        return True

def main():
    """Main demonstration function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Advanced esptool.py Usage Suite')
    parser.add_argument('--port', default='/dev/ttyACM0', help='Serial port')
    parser.add_argument('--baud', type=int, default=115200, help='Baud rate')
    parser.add_argument('--info-only', action='store_true', help='Show chip info only')
    parser.add_argument('--backup-only', action='store_true', help='Create backup script only')
    parser.add_argument('--safe-mode', action='store_true', help='Skip potentially destructive operations')
    
    args = parser.parse_args()
    
    tool = AdvancedESPTool(args.port, args.baud)
    
    if args.info_only:
        tool.demonstrate_chip_info()
    elif args.backup_only:
        tool.create_backup_script()
    elif args.safe_mode:
        tool.demonstrate_chip_info()
        tool.demonstrate_flash_analysis()
        tool.create_backup_script()
    else:
        tool.run_comprehensive_demo()

if __name__ == "__main__":
    main()