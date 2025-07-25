#!/usr/bin/env python3
"""
ESP32-C6 Memory Debugging Utilities
Advanced memory analysis and debugging tools for ESP-IDF projects
"""

import os
import sys
import json
import subprocess
import re
import time
from pathlib import Path
import argparse
import struct

class ESP32C6MemoryDebugger:
    """
    ESP32-C6 Memory Analysis and Debugging Tool
    
    Comprehensive memory debugging capabilities including:
    - Memory layout analysis from ELF files
    - Stack usage monitoring and analysis
    - Heap fragmentation detection and reporting
    - Memory leak detection and tracking
    """
    def __init__(self, project_path=None):
        self.project_path = project_path or os.getcwd()
        self.build_path = Path(self.project_path) / 'build'
        self.elf_file = self.build_path / 'project.elf'
        
        # ESP32-C6 memory layout
        self.memory_regions = {
            'ROM': {'start': 0x40000000, 'size': 0x20000, 'type': 'code'},
            'SRAM': {'start': 0x40800000, 'size': 0x80000, 'type': 'data'},
            'DRAM': {'start': 0x40800000, 'size': 0x80000, 'type': 'data'},
            'IRAM': {'start': 0x40800000, 'size': 0x80000, 'type': 'code'},
            'Flash': {'start': 0x42000000, 'size': 0x400000, 'type': 'code'},
            'External_RAM': {'start': 0x3C000000, 'size': 0x800000, 'type': 'data'}
        }

    def analyze_memory_layout(self):
        """Analyze memory layout from ELF file"""
        if not self.elf_file.exists():
            print("❌ ELF file not found. Build project first.")
            return None
        
        print("🧠 Analyzing memory layout...")
        
        try:
            # Get memory sections from ELF
            result = subprocess.run([
                'riscv32-esp-elf-objdump', '-h', str(self.elf_file)
            ], capture_output=True, text=True)
            
            sections = {}
            for line in result.stdout.split('\n'):
                if re.match(r'^\s*\d+\s+\.\w+', line):
                    parts = line.split()
                    if len(parts) >= 6:
                        section_name = parts[1]
                        size = int(parts[2], 16)
                        vma = int(parts[3], 16)
                        lma = int(parts[4], 16)
                        
                        sections[section_name] = {
                            'size': size,
                            'vma': vma,
                            'lma': lma,
                            'region': self.get_memory_region(vma)
                        }
            
            self.print_memory_layout(sections)
            return sections
            
        except Exception as e:
            print(f"❌ Memory analysis failed: {e}")
            return None

    def get_memory_region(self, address):
        """Get memory region for given address"""
        for region, info in self.memory_regions.items():
            if info['start'] <= address < info['start'] + info['size']:
                return region
        return 'Unknown'

    def print_memory_layout(self, sections):
        """Print formatted memory layout"""
        print("\n📊 Memory Layout Analysis:")
        print("=" * 60)
        print(f"{'Section':<15} {'Size':<10} {'VMA':<12} {'LMA':<12} {'Region':<12}")
        print("-" * 60)
        
        total_size = 0
        for name, info in sorted(sections.items(), key=lambda x: x[1]['vma']):
            print(f"{name:<15} {info['size']:<10} 0x{info['vma']:08x}   0x{info['lma']:08x}   {info['region']:<12}")
            total_size += info['size']
        
        print("-" * 60)
        print(f"{'Total':<15} {total_size:<10}")
        print(f"Binary size: {total_size / 1024:.1f} KB")

    def analyze_stack_usage(self):
        """Analyze stack usage from ELF file"""
        print("📚 Analyzing stack usage...")
        
        try:
            # Get stack information
            result = subprocess.run([
                'riscv32-esp-elf-objdump', '-t', str(self.elf_file)
            ], capture_output=True, text=True)
            
            stack_symbols = []
            for line in result.stdout.split('\n'):
                if 'stack' in line.lower() or '_stack' in line:
                    parts = line.split()
                    if len(parts) >= 6:
                        addr = int(parts[0], 16)
                        size = parts[4] if len(parts) > 4 else '0'
                        name = parts[-1]
                        stack_symbols.append({'name': name, 'addr': addr, 'size': size})
            
            if stack_symbols:
                print("\n📚 Stack Symbols Found:")
                print("-" * 40)
                for sym in stack_symbols:
                    print(f"{sym['name']}: 0x{sym['addr']:08x} (size: {sym['size']})")
            else:
                print("ℹ️  No explicit stack symbols found")
                
        except Exception as e:
            print(f"❌ Stack analysis failed: {e}")

    def create_heap_monitor_script(self):
        """Create GDB script for heap monitoring"""
        script_path = Path(self.project_path) / 'heap_monitor.gdb'
        
        gdb_script = '''# ESP32-C6 Heap Monitoring Script

define heap_info
    echo \\n=== ESP32-C6 Heap Information ===\\n
    monitor esp heap_info
    echo \\n=== Heap Summary ===\\n
    info heap
end

define heap_trace_start
    echo Starting heap trace...\\n
    monitor esp heap_trace_start
end

define heap_trace_stop
    echo Stopping heap trace...\\n
    monitor esp heap_trace_stop
    monitor esp heap_trace_dump
end

define stack_info
    echo \\n=== Stack Information ===\\n
    info stack
    bt
    echo \\n=== Register State ===\\n
    info registers
end

define memory_map
    echo \\n=== Memory Mappings ===\\n
    info proc mappings
    echo \\n=== Memory Regions ===\\n
    info mem
end

define freertos_tasks
    echo \\n=== FreeRTOS Task Information ===\\n
    monitor esp freertos_info
    info threads
    thread apply all bt
end

define memory_corruption_check
    echo \\n=== Memory Corruption Check ===\\n
    # Check heap integrity
    monitor esp heap_info
    # Check stack canaries (if enabled)
    info stack
    # Check for buffer overruns in common areas
    x/32wx $sp-128
    x/32wx $sp+128
end

# Breakpoint on memory allocation functions
break malloc
break free
break heap_caps_malloc
break heap_caps_free

# Commands to run on heap allocation breakpoints
commands 1 2 3 4
    silent
    printf "Memory operation at %s\\n", $pc
    printf "Stack trace:\\n"
    bt 5
    continue
end

echo \\nESP32-C6 heap monitoring ready!\\n
echo Use: heap_info, heap_trace_start, heap_trace_stop\\n
echo Use: stack_info, memory_map, freertos_tasks\\n
echo Use: memory_corruption_check\\n
'''
        
        with open(script_path, 'w') as f:
            f.write(gdb_script)
        
        print(f"✅ Created heap monitor script: {script_path}")
        return script_path

    def analyze_memory_fragmentation(self, openocd_process=None):
        """Analyze memory fragmentation via OpenOCD"""
        if not openocd_process:
            print("🚀 Starting OpenOCD for memory analysis...")
            try:
                openocd_process = subprocess.Popen([
                    'openocd', '-f', 'esp32c6_optimized.cfg'
                ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                time.sleep(3)
            except (subprocess.SubprocessError, FileNotFoundError, OSError) as e:
                print(f"❌ Failed to start OpenOCD: {e}")
                return None
        
        try:
            import telnetlib
            
            print("🧠 Analyzing memory fragmentation...")
            
            tn = telnetlib.Telnet('localhost', 4444)
            
            # Halt target
            tn.write(b"halt\n")
            time.sleep(1)
            tn.read_very_eager()
            
            # Get heap info
            tn.write(b"esp heap_info\n")
            time.sleep(1)
            heap_info = tn.read_very_eager().decode()
            
            # Resume target
            tn.write(b"resume\n")
            time.sleep(1)
            
            tn.close()
            
            print("\n📊 Memory Fragmentation Analysis:")
            print("=" * 50)
            print(heap_info)
            
            # Parse heap information
            free_blocks = re.findall(r'free:\s*(\d+)', heap_info)
            total_free = sum(int(x) for x in free_blocks) if free_blocks else 0
            
            largest_block = re.search(r'largest free block:\s*(\d+)', heap_info)
            if largest_block:
                largest = int(largest_block.group(1))
                fragmentation = (1 - largest / total_free) * 100 if total_free > 0 else 0
                print(f"\n📈 Fragmentation Analysis:")
                print(f"   Total free memory: {total_free} bytes")
                print(f"   Largest free block: {largest} bytes") 
                print(f"   Fragmentation: {fragmentation:.1f}%")
            
        except Exception as e:
            print(f"❌ Memory fragmentation analysis failed: {e}")
        
        finally:
            if openocd_process:
                openocd_process.terminate()

    def generate_memory_report(self):
        """Generate comprehensive memory report"""
        report_path = Path(self.project_path) / 'memory_report.json'
        
        print("📋 Generating comprehensive memory report...")
        
        report = {
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'project_path': str(self.project_path),
            'elf_file': str(self.elf_file),
            'memory_regions': self.memory_regions
        }
        
        # Memory layout analysis
        sections = self.analyze_memory_layout()
        if sections:
            report['sections'] = sections
        
        # Binary size analysis
        if self.elf_file.exists():
            try:
                result = subprocess.run([
                    'riscv32-esp-elf-size', str(self.elf_file)
                ], capture_output=True, text=True)
                
                lines = result.stdout.strip().split('\n')
                if len(lines) >= 2:
                    headers = lines[0].split()
                    values = lines[1].split()
                    
                    size_info = {}
                    for i, header in enumerate(headers):
                        if i < len(values):
                            size_info[header] = int(values[i])
                    
                    report['size_info'] = size_info
                    
            except (subprocess.SubprocessError, ValueError, IndexError) as e:
                # Size analysis failed - not critical
                print(f"Warning: Could not parse size information: {e}")
        
        # Save report
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"✅ Memory report saved: {report_path}")
        return report_path

    def create_memory_debugging_tools(self):
        """Create complete memory debugging toolset"""
        tools_dir = Path(self.project_path) / 'memory_debug_tools'
        tools_dir.mkdir(exist_ok=True)
        
        # Create heap monitor script
        heap_script = self.create_heap_monitor_script()
        
        # Memory analyzer script
        analyzer_script = tools_dir / 'memory_analyzer.py'
        with open(analyzer_script, 'w') as f:
            f.write(f'''#!/usr/bin/env python3
# ESP32-C6 Memory Analyzer
import sys
sys.path.append('{Path(__file__).parent.parent / "tools"}')

from esp32c6_memory_debug import ESP32C6MemoryDebugger

def main():
    debugger = ESP32C6MemoryDebugger()
    debugger.analyze_memory_layout()
    debugger.analyze_stack_usage()
    debugger.generate_memory_report()

if __name__ == '__main__':
    main()
''')
        os.chmod(analyzer_script, 0o755)
        
        # Heap tracer script
        heap_tracer = tools_dir / 'heap_tracer.sh'
        with open(heap_tracer, 'w') as f:
            f.write('''#!/bin/bash
# ESP32-C6 Heap Tracer
echo "🧠 Starting ESP32-C6 heap tracing session..."

if [ ! -f "build/project.elf" ]; then
    echo "❌ Build project first: idf.py build"
    exit 1
fi

# Start OpenOCD in background
openocd -f esp32c6_optimized.cfg > openocd_heap.log 2>&1 &
OPENOCD_PID=$!

sleep 3

# Start GDB with heap monitoring
riscv32-esp-elf-gdb build/project.elf \
    -x heap_monitor.gdb \
    -ex "target remote localhost:3333" \
    -ex "monitor reset halt" \
    -ex "heap_trace_start" \
    -ex "continue"

# Cleanup
echo "Stopping OpenOCD..."
kill $OPENOCD_PID
''')
        os.chmod(heap_tracer, 0o755)
        
        print(f"✅ Created memory debugging tools: {tools_dir}")
        return tools_dir

def main():
    parser = argparse.ArgumentParser(description='ESP32-C6 Memory Debugging Tool')
    parser.add_argument('--analyze', action='store_true',
                       help='Analyze memory layout and usage')
    parser.add_argument('--fragmentation', action='store_true',
                       help='Analyze memory fragmentation')
    parser.add_argument('--report', action='store_true',
                       help='Generate memory report')
    parser.add_argument('--create-tools', action='store_true',
                       help='Create memory debugging toolset')
    parser.add_argument('--project-path', type=str,
                       help='Project path (default: current directory)')
    
    args = parser.parse_args()
    
    debugger = ESP32C6MemoryDebugger(args.project_path)
    
    if args.create_tools:
        debugger.create_memory_debugging_tools()
        return
    
    if args.analyze:
        debugger.analyze_memory_layout()
        debugger.analyze_stack_usage()
        return
    
    if args.fragmentation:
        debugger.analyze_memory_fragmentation()
        return
    
    if args.report:
        debugger.generate_memory_report()
        return
    
    # Default: Create tools and analyze
    debugger.create_memory_debugging_tools()
    debugger.analyze_memory_layout()
    debugger.analyze_stack_usage()
    debugger.generate_memory_report()

# CLI wrapper functions for entry points
def cli_main():
    """CLI wrapper for entry point compatibility - safe version that doesn't parse args"""
    # Don't call main() directly as it parses sys.argv
    debugger = ESP32C6MemoryDebugger()
    print("🧠 ESP32-C6 Memory Debugging Tool")
    print("💡 Use 'esp32-debug memory-analyze' for memory analysis")
    return debugger

def analyze_memory_mcp():
    """MCP wrapper for memory analysis"""
    debugger = ESP32C6MemoryDebugger()
    debugger.analyze_memory_layout()
    debugger.analyze_stack_usage()
    return debugger.generate_memory_report()

if __name__ == '__main__':
    main()