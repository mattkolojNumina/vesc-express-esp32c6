#!/usr/bin/env python3
"""
ESP32-C6 Static Analysis Integration Suite
Implementation of research document recommendations for code quality analysis
"""

import subprocess
import os
import sys
import json
import time
from pathlib import Path
from datetime import datetime

class ESP32StaticAnalyzer:
    """
    Comprehensive static analysis for ESP32-C6 VESC Express
    Based on ESP-IDF research document recommendations
    """
    
    def __init__(self, project_path=None):
        self.project_path = project_path or os.getcwd()
        self.build_path = Path(self.project_path) / 'build'
        self.reports_path = Path(self.project_path) / 'analysis_reports'
        self.reports_path.mkdir(exist_ok=True)
        
    def setup_environment(self):
        """Ensure ESP-IDF environment is loaded"""
        esp_idf_path = os.environ.get('IDF_PATH', '/home/rds/esp/esp-idf')
        if not os.path.exists(esp_idf_path):
            print(f"❌ ESP-IDF not found at {esp_idf_path}")
            return False
            
        # Source ESP-IDF environment
        try:
            result = subprocess.run(
                f'cd {esp_idf_path} && source export.sh && env',
                shell=True, capture_output=True, text=True, executable='/bin/bash'
            )
            
            # Update environment with ESP-IDF variables
            for line in result.stdout.split('\n'):
                if '=' in line and ('IDF_' in line or 'ESP_' in line or 'PATH=' in line):
                    key, value = line.split('=', 1)
                    os.environ[key] = value
                    
            print("✅ ESP-IDF environment loaded")
            return True
            
        except Exception as e:
            print(f"❌ Failed to load ESP-IDF environment: {e}")
            return False
    
    def run_clang_tidy_analysis(self):
        """Run clang-tidy static analysis as per research document"""
        print("\n🔍 === CLANG-TIDY STATIC ANALYSIS ===")
        print("Based on ESP-IDF research document recommendations")
        
        try:
            # Ensure clang toolchain is available
            print("📋 Setting up clang toolchain...")
            subprocess.run(['idf_tools.py', 'install', 'esp-clang'], check=True)
            
            # Set clang environment
            os.environ['IDF_TOOLCHAIN'] = 'clang'
            
            print("🔨 Configuring project with clang...")
            result = subprocess.run(
                ['idf.py', 'reconfigure'],
                cwd=self.project_path,
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                print(f"⚠️  Reconfigure warning: {result.stderr}")
            
            print("🔍 Running clang-tidy analysis...")
            result = subprocess.run(
                ['idf.py', 'clang-check'],
                cwd=self.project_path,
                capture_output=True,
                text=True
            )
            
            # Check for warnings.txt file
            warnings_file = Path(self.project_path) / 'warnings.txt'
            if warnings_file.exists():
                print(f"✅ Clang-tidy analysis complete")
                print(f"📄 Report saved to: {warnings_file}")
                
                # Copy to reports directory with timestamp
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                report_copy = self.reports_path / f'clang_tidy_{timestamp}.txt'
                subprocess.run(['cp', str(warnings_file), str(report_copy)])
                
                # Show summary
                with open(warnings_file, 'r') as f:
                    content = f.read()
                    lines = content.split('\n')
                    warning_count = len([l for l in lines if 'warning:' in l])
                    error_count = len([l for l in lines if 'error:' in l])
                    
                print(f"📊 Analysis Summary: {warning_count} warnings, {error_count} errors")
                
                # Show first few warnings
                if warning_count > 0:
                    print("\n🔸 Sample warnings:")
                    warning_lines = [l for l in lines if 'warning:' in l][:3]
                    for warning in warning_lines:
                        print(f"   {warning}")
                        
                return True
            else:
                print("⚠️  No warnings.txt generated - clang-tidy may have failed")
                print(f"Output: {result.stdout}")
                print(f"Errors: {result.stderr}")
                return False
                
        except subprocess.CalledProcessError as e:
            print(f"❌ Clang-tidy analysis failed: {e}")
            return False
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            return False
    
    def generate_html_report(self):
        """Generate HTML report as per research document"""
        print("\n📊 === GENERATING HTML REPORT ===")
        
        try:
            # Install codereport if not available
            result = subprocess.run(
                [sys.executable, '-m', 'pip', 'show', 'codereport'],
                capture_output=True
            )
            
            if result.returncode != 0:
                print("📦 Installing codereport...")
                subprocess.run([
                    sys.executable, '-m', 'pip', 'install', 'codereport'
                ], check=True)
            
            print("🔨 Generating HTML report...")
            result = subprocess.run(
                ['idf.py', 'clang-html-report'],
                cwd=self.project_path,
                capture_output=True,
                text=True
            )
            
            html_report_dir = Path(self.project_path) / 'html_report'
            if html_report_dir.exists():
                print(f"✅ HTML report generated in: {html_report_dir}")
                
                # Copy to timestamped reports directory
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                report_dir = self.reports_path / f'html_report_{timestamp}'
                subprocess.run(['cp', '-r', str(html_report_dir), str(report_dir)])
                
                print(f"📁 Report archived to: {report_dir}")
                print(f"🌐 Open: {report_dir}/index.html")
                return True
            else:
                print("⚠️  HTML report directory not found")
                return False
                
        except Exception as e:
            print(f"❌ HTML report generation failed: {e}")
            return False
    
    def run_gcc_static_analyzer(self):
        """Run GCC static analyzer as per research document"""
        print("\n🔍 === GCC STATIC ANALYZER ===")
        
        try:
            print("⚙️  Enabling GCC static analyzer in menuconfig...")
            
            # Create a temporary sdkconfig change
            config_change = """
# Enable GCC Static Analyzer
CONFIG_COMPILER_STATIC_ANALYZER=y
CONFIG_COMPILER_STATIC_ANALYZER_MODE_LOG=y
"""
            
            config_file = Path(self.project_path) / 'sdkconfig'
            backup_file = Path(self.project_path) / 'sdkconfig.backup'
            
            # Backup current config
            if config_file.exists():
                subprocess.run(['cp', str(config_file), str(backup_file)])
            
            # Add static analyzer config
            with open(config_file, 'a') as f:
                f.write(config_change)
                
            print("🔨 Building with GCC static analyzer...")
            result = subprocess.run(
                ['idf.py', 'build'],
                cwd=self.project_path,
                capture_output=True,
                text=True
            )
            
            # Look for analyzer output in build log
            analyzer_warnings = []
            if result.stdout:
                lines = result.stdout.split('\n')
                for line in lines:
                    if 'warning:' in line and ('analyzer' in line.lower() or 'static' in line.lower()):
                        analyzer_warnings.append(line)
            
            if result.stderr:
                lines = result.stderr.split('\n')
                for line in lines:
                    if 'warning:' in line and ('analyzer' in line.lower() or 'static' in line.lower()):
                        analyzer_warnings.append(line)
            
            # Save analyzer report
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            analyzer_report = self.reports_path / f'gcc_analyzer_{timestamp}.txt'
            
            with open(analyzer_report, 'w') as f:
                f.write("GCC Static Analyzer Report\n")
                f.write("=" * 30 + "\n\n")
                f.write(f"Generated: {datetime.now().isoformat()}\n")
                f.write(f"Project: {self.project_path}\n\n")
                
                if analyzer_warnings:
                    f.write("Analyzer Warnings:\n")
                    f.write("-" * 20 + "\n")
                    for warning in analyzer_warnings:
                        f.write(f"{warning}\n")
                else:
                    f.write("No analyzer warnings found.\n")
                
                f.write("\nFull Build Output:\n")
                f.write("-" * 20 + "\n")
                f.write(result.stdout)
                if result.stderr:
                    f.write("\nBuild Errors:\n")
                    f.write(result.stderr)
            
            print(f"✅ GCC analyzer report saved: {analyzer_report}")
            print(f"📊 Found {len(analyzer_warnings)} analyzer warnings")
            
            # Restore original config
            if backup_file.exists():
                subprocess.run(['mv', str(backup_file), str(config_file)])
            
            return True
            
        except Exception as e:
            print(f"❌ GCC static analyzer failed: {e}")
            return False
    
    def run_comprehensive_analysis(self):
        """Run complete static analysis suite"""
        print("🎯 ESP32-C6 Comprehensive Static Analysis")
        print("=" * 50)
        print("Based on ESP-IDF research document")
        print()
        
        if not self.setup_environment():
            return False
        
        results = {
            'clang_tidy': False,
            'html_report': False,
            'gcc_analyzer': False
        }
        
        # Run all analysis tools
        results['clang_tidy'] = self.run_clang_tidy_analysis()
        
        if results['clang_tidy']:
            results['html_report'] = self.generate_html_report()
        
        results['gcc_analyzer'] = self.run_gcc_static_analyzer()
        
        # Summary
        print("\n📋 ANALYSIS SUMMARY")
        print("=" * 20)
        for tool, success in results.items():
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"{tool.replace('_', ' ').title()}: {status}")
        
        total_success = sum(results.values())
        print(f"\n🎯 Overall Success: {total_success}/{len(results)} tools")
        
        # Show reports directory
        if self.reports_path.exists():
            reports = list(self.reports_path.glob('*'))
            if reports:
                print(f"\n📁 Analysis reports saved in: {self.reports_path}")
                for report in sorted(reports)[-3:]:  # Show last 3 reports
                    print(f"   📄 {report.name}")
        
        return total_success > 0

def main():
    """Main analysis function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='ESP32-C6 Static Analysis Suite')
    parser.add_argument('--project', default='.', help='Project directory')
    parser.add_argument('--clang-only', action='store_true', help='Run only clang-tidy')
    parser.add_argument('--gcc-only', action='store_true', help='Run only GCC analyzer')
    parser.add_argument('--html-only', action='store_true', help='Generate HTML report only')
    
    args = parser.parse_args()
    
    analyzer = ESP32StaticAnalyzer(args.project)
    
    if args.clang_only:
        analyzer.setup_environment()
        analyzer.run_clang_tidy_analysis()
    elif args.gcc_only:
        analyzer.setup_environment()
        analyzer.run_gcc_static_analyzer()
    elif args.html_only:
        analyzer.setup_environment()
        analyzer.generate_html_report()
    else:
        analyzer.run_comprehensive_analysis()

if __name__ == "__main__":
    main()