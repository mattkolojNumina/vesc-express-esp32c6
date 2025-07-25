#!/usr/bin/env python3
"""
ESP32-C6 Memory Debugging Utilities (Refactored)
Advanced memory analysis and debugging tools for ESP-IDF projects
"""

import re
import struct
import json
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass

from esp32_debug_base import (
    ESP32DebugToolBase, ESP32Constants, ESP32ToolException,
    ESP32BuildError
)

@dataclass
class MemorySection:
    """Represents a memory section from ELF analysis"""
    name: str
    size: int
    vma: int
    lma: int
    region: str
    
    @property
    def size_kb(self) -> float:
        """Size in kilobytes"""
        return self.size / 1024
    
    @property
    def size_mb(self) -> float:
        """Size in megabytes"""
        return self.size / (1024 * 1024)

@dataclass
class MemoryRegionInfo:
    """Information about a memory region"""
    name: str
    start_addr: int
    size: int
    region_type: str
    used_size: int = 0
    
    @property
    def end_addr(self) -> int:
        """End address of region"""
        return self.start_addr + self.size
    
    @property
    def usage_percent(self) -> float:
        """Usage percentage"""
        return (self.used_size / self.size) * 100 if self.size > 0 else 0
    
    @property
    def free_size(self) -> int:
        """Free size in region"""
        return self.size - self.used_size

class MemoryAnalyzer:
    """Handles memory analysis operations"""
    
    def __init__(self, elf_file: Path):
        self.elf_file = elf_file
        self.memory_regions = ESP32Constants.MEMORY_REGIONS
    
    def analyze_elf_sections(self) -> Dict[str, MemorySection]:
        """
        Analyze memory sections from ELF file
        
        Returns:
            Dictionary of memory sections
            
        Raises:
            ESP32ToolException: If analysis fails
        """
        if not self.elf_file.exists():
            raise ESP32BuildError(f"ELF file not found: {self.elf_file}")
        
        try:
            from esp32_debug_base import ProcessManager
            
            # Get memory sections from ELF
            result = ProcessManager.run_command([
                'riscv32-esp-elf-objdump', '-h', str(self.elf_file)
            ])
            
            sections = {}
            for line in result.stdout.split('\\n'):
                if re.match(r'^\\s*\\d+\\s+\\.\\w+', line):
                    parts = line.split()
                    if len(parts) >= 6:
                        section_name = parts[1]
                        size = int(parts[2], 16)
                        vma = int(parts[3], 16)
                        lma = int(parts[4], 16)
                        
                        sections[section_name] = MemorySection(
                            name=section_name,
                            size=size,
                            vma=vma,
                            lma=lma,
                            region=self._get_memory_region(vma)
                        )
            
            return sections
            
        except Exception as e:
            raise ESP32ToolException(f"ELF analysis failed: {e}") from e
    
    def _get_memory_region(self, address: int) -> str:
        """Get memory region for given address"""
        for region, info in self.memory_regions.items():
            if info['start'] <= address < info['start'] + info['size']:
                return region
        return 'Unknown'
    
    def analyze_symbol_sizes(self) -> Dict[str, int]:
        """
        Analyze symbol sizes from ELF file
        
        Returns:
            Dictionary mapping symbol names to sizes
        """
        try:
            from esp32_debug_base import ProcessManager
            
            result = ProcessManager.run_command([
                'riscv32-esp-elf-nm', '--print-size', '--size-sort', str(self.elf_file)
            ])
            
            symbols = {}
            for line in result.stdout.split('\\n'):
                parts = line.split()
                if len(parts) >= 4:
                    try:
                        size = int(parts[1], 16)
                        symbol_name = parts[3]
                        symbols[symbol_name] = size
                    except ValueError:
                        continue
            
            return symbols
            
        except Exception as e:
            raise ESP32ToolException(f"Symbol analysis failed: {e}") from e

class ESP32C6MemoryDebugger(ESP32DebugToolBase):
    """
    ESP32-C6 Memory Analysis and Debugging Tool
    
    Comprehensive memory debugging capabilities including:
    - Memory layout analysis from ELF files
    - Stack usage monitoring and analysis
    - Heap fragmentation detection and reporting
    - Memory leak detection and tracking
    """
    
    @property
    def config_filename(self) -> str:
        return "memory_debug_config.json"
    
    @property
    def default_config(self) -> Dict[str, Any]:
        return {
            'memory_threshold_warning': 80,  # Percentage
            'memory_threshold_critical': 95,  # Percentage
            'analyze_symbols': True,
            'generate_reports': True,
            'session_history': []
        }
    
    def __init__(self, project_path: Optional[str] = None):
        super().__init__(project_path)
        self.analyzer = MemoryAnalyzer(self.config.elf_file)
    
    def analyze_memory_layout(self) -> Dict[str, MemorySection]:
        """
        Analyze memory layout from ELF file
        
        Returns:
            Dictionary of memory sections
        """
        self.logger.info("Analyzing memory layout...")
        
        sections = self.analyzer.analyze_elf_sections()
        self._print_memory_layout(sections)
        
        self.log_session('memory_layout_analyzed', {
            'sections_count': len(sections),
            'total_size': sum(s.size for s in sections.values())
        })
        
        return sections
    
    def _print_memory_layout(self, sections: Dict[str, MemorySection]) -> None:
        """Print formatted memory layout"""
        self.logger.info("Memory Layout Analysis:")
        self.logger.info("=" * 60)
        
        header = f"{'Section':<15} {'Size':<10} {'VMA':<12} {'LMA':<12} {'Region':<12}"
        self.logger.info(header)
        self.logger.info("-" * 60)
        
        total_size = 0
        for section in sorted(sections.values(), key=lambda x: x.vma):
            size_str = f"{section.size} ({section.size_kb:.1f}KB)"
            row = f"{section.name:<15} {size_str:<10} 0x{section.vma:08x}   0x{section.lma:08x}   {section.region:<12}"
            self.logger.info(row)
            total_size += section.size
        
        self.logger.info("-" * 60)
        self.logger.info(f"{'Total':<15} {total_size} ({total_size/1024:.1f}KB)")
    
    def analyze_stack_usage(self) -> Dict[str, Any]:
        """
        Analyze stack usage from ELF file
        
        Returns:
            Stack usage analysis results
        """
        self.logger.info("Analyzing stack usage...")
        
        try:
            # Use ESP-IDF stack analysis tool if available
            result = self.run_command([
                'riscv32-esp-elf-objdump', '-t', str(self.config.elf_file)
            ])
            
            stack_symbols = {}
            for line in result.stdout.split('\\n'):
                if 'stack' in line.lower():
                    parts = line.split()
                    if len(parts) >= 6:
                        try:
                            addr = int(parts[0], 16)
                            size = int(parts[4], 16) if len(parts) > 4 else 0
                            symbol = parts[-1]
                            stack_symbols[symbol] = {'address': addr, 'size': size}
                        except ValueError:
                            continue
            
            analysis = {
                'stack_symbols': stack_symbols,
                'total_stack_size': sum(s['size'] for s in stack_symbols.values()),
                'stack_count': len(stack_symbols)
            }
            
            self._print_stack_analysis(analysis)
            self.log_session('stack_analysis_complete', analysis)
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Stack analysis failed: {e}")
            return {}
    
    def _print_stack_analysis(self, analysis: Dict[str, Any]) -> None:
        """Print stack analysis results"""
        self.logger.info("Stack Usage Analysis:")
        self.logger.info("=" * 50)
        
        for symbol, info in analysis['stack_symbols'].items():
            size_kb = info['size'] / 1024
            self.logger.info(f"{symbol}: {info['size']} bytes ({size_kb:.1f}KB) @ 0x{info['address']:08x}")
        
        total_kb = analysis['total_stack_size'] / 1024
        self.logger.info(f"\\nTotal stack usage: {analysis['total_stack_size']} bytes ({total_kb:.1f}KB)")
        self.logger.info(f"Stack count: {analysis['stack_count']}")
    
    def analyze_memory_fragmentation(self) -> Dict[str, Any]:
        """
        Analyze memory fragmentation
        
        Returns:
            Fragmentation analysis results
        """
        self.logger.info("Analyzing memory fragmentation...")
        
        # Get memory layout
        sections = self.analyze_memory_layout()
        
        # Analyze fragmentation by region
        region_usage = {}
        for section in sections.values():
            if section.region not in region_usage:
                region_usage[section.region] = {
                    'total_size': 0,
                    'sections': [],
                    'fragmentation_score': 0
                }
            
            region_usage[section.region]['total_size'] += section.size
            region_usage[section.region]['sections'].append(section)
        
        # Calculate fragmentation scores
        for region, info in region_usage.items():
            sections_count = len(info['sections'])
            avg_section_size = info['total_size'] / sections_count if sections_count > 0 else 0
            
            # Simple fragmentation score based on section count and size distribution
            if sections_count > 10:
                info['fragmentation_score'] = min(sections_count / 10, 1.0)
            else:
                info['fragmentation_score'] = 0.1
        
        analysis = {
            'region_usage': region_usage,
            'total_regions': len(region_usage),
            'most_fragmented': max(region_usage.items(), 
                                 key=lambda x: x[1]['fragmentation_score'])[0] if region_usage else None
        }
        
        self._print_fragmentation_analysis(analysis)
        self.log_session('fragmentation_analysis_complete', analysis)
        
        return analysis
    
    def _print_fragmentation_analysis(self, analysis: Dict[str, Any]) -> None:
        """Print fragmentation analysis results"""
        self.logger.info("Memory Fragmentation Analysis:")
        self.logger.info("=" * 50)
        
        for region, info in analysis['region_usage'].items():
            size_kb = info['total_size'] / 1024
            score_percent = info['fragmentation_score'] * 100
            
            self.logger.info(f"Region {region}:")
            self.logger.info(f"  Total size: {info['total_size']} bytes ({size_kb:.1f}KB)")
            self.logger.info(f"  Sections: {len(info['sections'])}")
            self.logger.info(f"  Fragmentation score: {score_percent:.1f}%")
            
            if info['fragmentation_score'] > 0.7:
                self.logger.warning(f"  ⚠️  High fragmentation detected in {region}")
    
    def generate_memory_report(self) -> Path:
        """
        Generate comprehensive memory report
        
        Returns:
            Path to generated report file
        """
        self.logger.info("Generating memory report...")
        
        # Gather all analysis data
        sections = self.analyze_memory_layout()
        stack_analysis = self.analyze_stack_usage()
        fragmentation_analysis = self.analyze_memory_fragmentation()
        
        # Optional symbol analysis
        symbol_analysis = {}
        if self.tool_config.get('analyze_symbols', True):
            try:
                symbol_analysis = self.analyzer.analyze_symbol_sizes()
            except Exception as e:
                self.logger.warning(f"Symbol analysis failed: {e}")
        
        # Create comprehensive report
        report = {
            'timestamp': self._get_timestamp(),
            'project_path': str(self.config.project_path),
            'elf_file': str(self.config.elf_file),
            'memory_layout': {
                name: {
                    'size': section.size,
                    'vma': section.vma,
                    'lma': section.lma,
                    'region': section.region
                } for name, section in sections.items()
            },
            'stack_analysis': stack_analysis,
            'fragmentation_analysis': fragmentation_analysis,
            'symbol_analysis': dict(list(symbol_analysis.items())[:50]) if symbol_analysis else {},  # Top 50 symbols
            'summary': self._create_memory_summary(sections, stack_analysis, fragmentation_analysis)
        }
        
        # Save report
        report_path = self.config.project_path / f'memory_report_{int(self._get_timestamp().timestamp())}.json'
        
        try:
            with open(report_path, 'w') as f:
                json.dump(report, f, indent=2)
            
            self.logger.info(f"Memory report saved: {report_path}")
            self.log_session('memory_report_generated', {'report_path': str(report_path)})
            
            return report_path
            
        except IOError as e:
            raise ESP32ToolException(f"Failed to save memory report: {e}") from e
    
    def _create_memory_summary(self, sections: Dict[str, MemorySection], 
                              stack_analysis: Dict[str, Any],
                              fragmentation_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Create memory summary"""
        total_size = sum(s.size for s in sections.values())
        total_stack = stack_analysis.get('total_stack_size', 0)
        
        # Find regions with high usage
        warning_regions = []
        critical_regions = []
        
        for region, info in fragmentation_analysis.get('region_usage', {}).items():
            if info['fragmentation_score'] > 0.8:
                critical_regions.append(region)
            elif info['fragmentation_score'] > 0.6:
                warning_regions.append(region)
        
        return {
            'total_memory_used': total_size,
            'total_stack_memory': total_stack,
            'section_count': len(sections),
            'warning_regions': warning_regions,
            'critical_regions': critical_regions,
            'recommendations': self._generate_recommendations(warning_regions, critical_regions)
        }
    
    def _generate_recommendations(self, warning_regions: List[str], 
                                 critical_regions: List[str]) -> List[str]:
        """Generate memory optimization recommendations"""
        recommendations = []
        
        if critical_regions:
            recommendations.append(f"Critical fragmentation in {', '.join(critical_regions)}. Consider memory layout optimization.")
        
        if warning_regions:
            recommendations.append(f"High fragmentation in {', '.join(warning_regions)}. Monitor memory usage.")
        
        if not warning_regions and not critical_regions:
            recommendations.append("Memory layout appears optimal.")
        
        return recommendations
    
    def _get_timestamp(self):
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now()
    
    def create_memory_debugging_tools(self) -> None:
        """Create additional memory debugging tools and scripts"""
        tools_dir = self.config.project_path / 'memory_tools'
        tools_dir.mkdir(exist_ok=True)
        
        # Create memory monitoring script
        monitor_script = tools_dir / 'monitor_memory.py'
        with open(monitor_script, 'w') as f:
            f.write('''#!/usr/bin/env python3
"""
Memory monitoring script - Auto-generated
Monitors memory usage during runtime
"""

import time
import json
from pathlib import Path

def monitor_memory():
    """Monitor memory usage continuously"""
    from esp32c6_memory_debug import ESP32C6MemoryDebugger
    
    debugger = ESP32C6MemoryDebugger()
    
    while True:
        try:
            report = debugger.generate_memory_report()
            print(f"Memory report generated: {report}")
            time.sleep(60)  # Monitor every minute
        except KeyboardInterrupt:
            print("Memory monitoring stopped")
            break
        except Exception as e:
            print(f"Monitoring error: {e}")
            time.sleep(5)

if __name__ == '__main__':
    monitor_memory()
''')
        monitor_script.chmod(0o755)
        
        self.logger.info(f"Created memory debugging tools in {tools_dir}")
    
    def main(self, args: Optional[List[str]] = None) -> bool:
        """
        Main entry point for memory debugging tool
        
        Args:
            args: Command line arguments
            
        Returns:
            True if successful
        """
        import argparse
        
        parser = argparse.ArgumentParser(description='ESP32-C6 Memory Debugging Tool')
        parser.add_argument('--layout', action='store_true',
                          help='Analyze memory layout')
        parser.add_argument('--stack', action='store_true',
                          help='Analyze stack usage')
        parser.add_argument('--fragmentation', action='store_true',
                          help='Analyze memory fragmentation')
        parser.add_argument('--report', action='store_true',
                          help='Generate comprehensive memory report')
        parser.add_argument('--create-tools', action='store_true',
                          help='Create memory debugging tools')
        
        parsed_args = parser.parse_args(args)
        
        try:
            self.validate_environment()
            
            if parsed_args.create_tools:
                self.create_memory_debugging_tools()
                return True
            
            if parsed_args.layout:
                self.analyze_memory_layout()
                return True
            
            if parsed_args.stack:
                self.analyze_stack_usage()
                return True
            
            if parsed_args.fragmentation:
                self.analyze_memory_fragmentation()
                return True
            
            if parsed_args.report:
                self.generate_memory_report()
                return True
            
            # Default: run all analyses
            self.analyze_memory_layout()
            self.analyze_stack_usage()
            self.analyze_memory_fragmentation()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Memory debugging failed: {e}")
            return False

# MCP integration functions
def cli_main():
    """CLI wrapper for entry point compatibility"""
    return ESP32C6MemoryDebugger()

def analyze_memory_mcp(project_path: Optional[str] = None) -> Dict[str, Any]:
    """MCP wrapper for memory analysis"""
    tool = ESP32C6MemoryDebugger(project_path)
    
    try:
        sections = tool.analyze_memory_layout()
        stack_analysis = tool.analyze_stack_usage()
        fragmentation_analysis = tool.analyze_memory_fragmentation()
        
        return {
            'success': True,
            'project_path': str(tool.config.project_path),
            'total_sections': len(sections),
            'total_memory': sum(s.size for s in sections.values()),
            'stack_memory': stack_analysis.get('total_stack_size', 0),
            'fragmentation_regions': len(fragmentation_analysis.get('region_usage', {}))
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'project_path': str(tool.config.project_path)
        }

if __name__ == '__main__':
    tool = ESP32C6MemoryDebugger()
    success = tool.main()
    exit(0 if success else 1)