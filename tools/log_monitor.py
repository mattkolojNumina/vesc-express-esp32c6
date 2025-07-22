#!/usr/bin/env python3
"""
ESP32-C6 VESC Express Log Monitor
Real-time log analysis and monitoring with intelligent parsing
"""

import serial
import threading
import queue
import time
import re
import json
from pathlib import Path
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Pattern
from collections import defaultdict, deque
import argparse

@dataclass
class LogEntry:
    """Structured log entry"""
    timestamp: datetime
    level: str
    tag: str
    message: str
    raw_line: str
    line_number: int

@dataclass
class SystemMetrics:
    """System performance metrics"""
    free_heap: Optional[int] = None
    stack_usage: Dict[str, int] = None
    cpu_usage: Optional[float] = None
    wifi_rssi: Optional[int] = None
    ble_connections: int = 0
    can_errors: int = 0
    packet_count: int = 0
    uptime: Optional[int] = None
    
    def __post_init__(self):
        if self.stack_usage is None:
            self.stack_usage = {}

class VESCLogMonitor:
    """Intelligent VESC Express log monitor"""
    
    # Log level patterns
    LOG_PATTERNS = {
        'esp_idf': re.compile(r'^([EWIVD])\s*\((\d+)\)\s*([^:]+):\s*(.+)$'),
        'vesc': re.compile(r'^\[(\w+)\]\s*(.+)$'),
        'timestamp': re.compile(r'^\[(\d{2}:\d{2}:\d{2}\.\d{3})\]'),
        'heap': re.compile(r'free heap:\s*(\d+)', re.IGNORECASE),
        'stack': re.compile(r'(\w+)\s+task\s+stack:\s*(\d+)', re.IGNORECASE),
        'wifi_rssi': re.compile(r'rssi:\s*(-?\d+)', re.IGNORECASE),
        'uptime': re.compile(r'uptime:\s*(\d+)', re.IGNORECASE)
    }
    
    # Critical error patterns
    ERROR_PATTERNS = {
        'panic': re.compile(r'panic|abort|exception|fatal', re.IGNORECASE),
        'malloc_fail': re.compile(r'malloc.*fail|out of memory', re.IGNORECASE),
        'stack_overflow': re.compile(r'stack overflow|stack smashing', re.IGNORECASE),
        'wifi_error': re.compile(r'wifi.*error|wifi.*fail', re.IGNORECASE),
        'ble_error': re.compile(r'ble.*error|bluetooth.*error', re.IGNORECASE),
        'can_error': re.compile(r'can.*error|twai.*error', re.IGNORECASE),
        'vesc_error': re.compile(r'vesc.*error|motor.*error', re.IGNORECASE)
    }
    
    # Performance warning patterns
    WARNING_PATTERNS = {
        'low_heap': re.compile(r'heap.*low|memory.*low', re.IGNORECASE),
        'high_cpu': re.compile(r'cpu.*high|load.*high', re.IGNORECASE),
        'slow_response': re.compile(r'timeout|slow.*response', re.IGNORECASE),
        'connection_drop': re.compile(r'disconnect|connection.*lost', re.IGNORECASE)
    }
    
    def __init__(self, port: str = "/dev/ttyACM0", baud: int = 115200):
        self.port = port
        self.baud = baud
        self.serial_conn: Optional[serial.Serial] = None
        self.running = False
        
        # Threading
        self.read_thread: Optional[threading.Thread] = None
        self.log_queue: queue.Queue = queue.Queue()
        self.analysis_thread: Optional[threading.Thread] = None
        
        # Data storage
        self.logs: deque = deque(maxlen=10000)  # Keep last 10k entries
        self.metrics_history: deque = deque(maxlen=1000)  # Keep metrics history
        self.current_metrics = SystemMetrics()
        
        # Statistics
        self.stats = {
            'total_lines': 0,
            'errors': 0,
            'warnings': 0,
            'start_time': None,
            'last_activity': None
        }
        
        # Error tracking
        self.error_counts = defaultdict(int)
        self.warning_counts = defaultdict(int)
        
        # Setup logging
        self.logs_dir = Path(__file__).parent.parent / "logs"
        self.logs_dir.mkdir(exist_ok=True)
        
        # Output files
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.raw_log_file = self.logs_dir / f"raw_monitor_{timestamp}.log"
        self.parsed_log_file = self.logs_dir / f"parsed_monitor_{timestamp}.json"
        self.metrics_file = self.logs_dir / f"metrics_{timestamp}.json"
        
    def parse_log_line(self, line: str, line_number: int) -> Optional[LogEntry]:
        """Parse a log line into structured format"""
        line = line.strip()
        if not line:
            return None
        
        # Try ESP-IDF format first
        match = self.LOG_PATTERNS['esp_idf'].match(line)
        if match:
            level_char, timestamp_ms, tag, message = match.groups()
            level_map = {'E': 'ERROR', 'W': 'WARN', 'I': 'INFO', 'D': 'DEBUG', 'V': 'VERBOSE'}
            level = level_map.get(level_char, 'UNKNOWN')
            
            return LogEntry(
                timestamp=datetime.now(),
                level=level,
                tag=tag.strip(),
                message=message.strip(),
                raw_line=line,
                line_number=line_number
            )
        
        # Try VESC format
        match = self.LOG_PATTERNS['vesc'].match(line)
        if match:
            level, message = match.groups()
            return LogEntry(
                timestamp=datetime.now(),
                level=level.upper(),
                tag="VESC",
                message=message.strip(),
                raw_line=line,
                line_number=line_number
            )
        
        # Default: treat as info message
        return LogEntry(
            timestamp=datetime.now(),
            level="INFO",
            tag="SYSTEM",
            message=line,
            raw_line=line,
            line_number=line_number
        )
    
    def extract_metrics(self, entry: LogEntry) -> None:
        """Extract system metrics from log entry"""
        message = entry.message.lower()
        
        # Free heap
        match = self.LOG_PATTERNS['heap'].search(message)
        if match:
            self.current_metrics.free_heap = int(match.group(1))
        
        # Stack usage
        match = self.LOG_PATTERNS['stack'].search(message)
        if match:
            task_name, stack_size = match.groups()
            self.current_metrics.stack_usage[task_name] = int(stack_size)
        
        # WiFi RSSI
        match = self.LOG_PATTERNS['wifi_rssi'].search(message)
        if match:
            self.current_metrics.wifi_rssi = int(match.group(1))
        
        # Uptime
        match = self.LOG_PATTERNS['uptime'].search(message)
        if match:
            self.current_metrics.uptime = int(match.group(1))
        
        # Count various events
        if 'ble' in message and 'connect' in message:
            self.current_metrics.ble_connections += 1
        elif 'can' in message and 'error' in message:
            self.current_metrics.can_errors += 1
        elif 'packet' in message:
            self.current_metrics.packet_count += 1
    
    def analyze_entry(self, entry: LogEntry) -> None:
        """Analyze log entry for issues and patterns"""
        message_lower = entry.message.lower()
        
        # Check for critical errors
        for error_type, pattern in self.ERROR_PATTERNS.items():
            if pattern.search(entry.message):
                self.error_counts[error_type] += 1
                print(f"🚨 CRITICAL ERROR [{error_type}]: {entry.message}")
        
        # Check for warnings
        for warning_type, pattern in self.WARNING_PATTERNS.items():
            if pattern.search(entry.message):
                self.warning_counts[warning_type] += 1
                print(f"⚠️  WARNING [{warning_type}]: {entry.message}")
        
        # Extract metrics
        self.extract_metrics(entry)
        
        # Update stats
        if entry.level in ['ERROR', 'FATAL']:
            self.stats['errors'] += 1
        elif entry.level in ['WARN', 'WARNING']:
            self.stats['warnings'] += 1
        
        self.stats['last_activity'] = datetime.now()
    
    def format_entry(self, entry: LogEntry) -> str:
        """Format log entry for display"""
        timestamp_str = entry.timestamp.strftime("%H:%M:%S.%f")[:-3]
        
        # Color coding
        color_map = {
            'ERROR': '\033[91m',    # Red
            'WARN': '\033[93m',     # Yellow
            'WARNING': '\033[93m',  # Yellow
            'INFO': '\033[94m',     # Blue
            'DEBUG': '\033[95m',    # Magenta
            'VERBOSE': '\033[90m'   # Gray
        }
        
        color = color_map.get(entry.level, '')
        reset = '\033[0m' if color else ''
        
        return f"[{timestamp_str}] {color}{entry.level:8s}{reset} {entry.tag:12s} {entry.message}"
    
    def serial_reader(self) -> None:
        """Read from serial port in separate thread"""
        line_number = 0
        
        try:
            while self.running:
                try:
                    if self.serial_conn and self.serial_conn.in_waiting:
                        line = self.serial_conn.readline().decode('utf-8', errors='ignore').strip()
                        if line:
                            line_number += 1
                            self.stats['total_lines'] = line_number
                            
                            # Write raw log
                            with open(self.raw_log_file, 'a') as f:
                                f.write(f"[{datetime.now().isoformat()}] {line}\n")
                            
                            # Queue for processing
                            self.log_queue.put((line, line_number))
                    else:
                        time.sleep(0.001)  # Small delay to prevent busy waiting
                        
                except serial.SerialException as e:
                    print(f"❌ Serial error: {e}")
                    break
                except Exception as e:
                    print(f"❌ Unexpected error in serial reader: {e}")
                    
        except Exception as e:
            print(f"💥 Fatal error in serial reader: {e}")
    
    def log_analyzer(self) -> None:
        """Analyze logs in separate thread"""
        try:
            while self.running:
                try:
                    # Process queued log lines
                    line, line_number = self.log_queue.get(timeout=1.0)
                    
                    # Parse and analyze
                    entry = self.parse_log_line(line, line_number)
                    if entry:
                        self.logs.append(entry)
                        self.analyze_entry(entry)
                        
                        # Display formatted entry
                        print(self.format_entry(entry))
                        
                        # Save parsed entry
                        with open(self.parsed_log_file, 'a') as f:
                            f.write(json.dumps(asdict(entry), default=str) + "\n")
                    
                    self.log_queue.task_done()
                    
                except queue.Empty:
                    continue
                except Exception as e:
                    print(f"❌ Error in log analyzer: {e}")
                    
        except Exception as e:
            print(f"💥 Fatal error in log analyzer: {e}")
    
    def metrics_reporter(self) -> None:
        """Periodically report system metrics"""
        while self.running:
            try:
                time.sleep(10)  # Report every 10 seconds
                
                if not self.running:
                    break
                
                # Save current metrics
                metrics_snapshot = asdict(self.current_metrics)
                metrics_snapshot['timestamp'] = datetime.now().isoformat()
                self.metrics_history.append(metrics_snapshot)
                
                # Write metrics to file
                with open(self.metrics_file, 'w') as f:
                    json.dump(list(self.metrics_history), f, indent=2, default=str)
                
                # Print summary
                print("\n" + "="*60)
                print(f"📊 SYSTEM METRICS - {datetime.now().strftime('%H:%M:%S')}")
                print("="*60)
                
                if self.current_metrics.free_heap:
                    heap_mb = self.current_metrics.free_heap / 1024
                    print(f"💾 Free Heap: {heap_mb:.1f} KB ({self.current_metrics.free_heap:,} bytes)")
                
                if self.current_metrics.stack_usage:
                    print("📚 Stack Usage:")
                    for task, usage in self.current_metrics.stack_usage.items():
                        print(f"   {task}: {usage:,} bytes")
                
                if self.current_metrics.wifi_rssi:
                    print(f"📡 WiFi RSSI: {self.current_metrics.wifi_rssi} dBm")
                
                if self.current_metrics.uptime:
                    uptime_min = self.current_metrics.uptime / 60
                    print(f"⏱️  Uptime: {uptime_min:.1f} minutes")
                
                print(f"🔌 BLE Connections: {self.current_metrics.ble_connections}")
                print(f"📦 Packets: {self.current_metrics.packet_count}")
                print(f"⚠️  CAN Errors: {self.current_metrics.can_errors}")
                
                print("\n📈 LOG STATISTICS")
                runtime = datetime.now() - self.stats['start_time'] if self.stats['start_time'] else timedelta(0)
                print(f"   Total Lines: {self.stats['total_lines']:,}")
                print(f"   Errors: {self.stats['errors']}")
                print(f"   Warnings: {self.stats['warnings']}")
                print(f"   Runtime: {str(runtime).split('.')[0]}")
                
                if self.error_counts:
                    print("\n🚨 ERROR BREAKDOWN")
                    for error_type, count in self.error_counts.items():
                        print(f"   {error_type}: {count}")
                
                if self.warning_counts:
                    print("\n⚠️  WARNING BREAKDOWN")
                    for warning_type, count in self.warning_counts.items():
                        print(f"   {warning_type}: {count}")
                
                print("="*60 + "\n")
                
            except Exception as e:
                print(f"❌ Error in metrics reporter: {e}")
    
    def start_monitoring(self) -> None:
        """Start log monitoring"""
        print(f"🚀 Starting VESC Express log monitor on {self.port}")
        print(f"📁 Logs will be saved to {self.logs_dir}")
        print("Press Ctrl+C to stop\n")
        
        try:
            # Open serial connection
            self.serial_conn = serial.Serial(
                port=self.port,
                baudrate=self.baud,
                timeout=1.0,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE
            )
            
            print(f"✅ Connected to {self.port} at {self.baud} baud")
            
        except serial.SerialException as e:
            print(f"❌ Failed to open {self.port}: {e}")
            return
        
        # Initialize stats
        self.stats['start_time'] = datetime.now()
        self.running = True
        
        # Start threads
        self.read_thread = threading.Thread(target=self.serial_reader, daemon=True)
        self.analysis_thread = threading.Thread(target=self.log_analyzer, daemon=True)
        self.metrics_thread = threading.Thread(target=self.metrics_reporter, daemon=True)
        
        self.read_thread.start()
        self.analysis_thread.start()
        self.metrics_thread.start()
        
        try:
            # Keep main thread alive
            while self.running:
                time.sleep(0.1)
                
        except KeyboardInterrupt:
            print("\n🛑 Stopping monitor...")
            self.stop_monitoring()
    
    def stop_monitoring(self) -> None:
        """Stop log monitoring"""
        self.running = False
        
        # Wait for threads to finish
        if self.read_thread and self.read_thread.is_alive():
            self.read_thread.join(timeout=2)
        
        if self.analysis_thread and self.analysis_thread.is_alive():
            self.analysis_thread.join(timeout=2)
            
        if hasattr(self, 'metrics_thread') and self.metrics_thread.is_alive():
            self.metrics_thread.join(timeout=2)
        
        # Close serial connection
        if self.serial_conn and self.serial_conn.is_open:
            self.serial_conn.close()
        
        # Final report
        self.generate_final_report()
        
        print(f"✅ Monitor stopped. Logs saved to {self.logs_dir}")
    
    def generate_final_report(self) -> None:
        """Generate final monitoring report"""
        report = {
            'session': {
                'start_time': self.stats['start_time'].isoformat() if self.stats['start_time'] else None,
                'end_time': datetime.now().isoformat(),
                'duration': str(datetime.now() - self.stats['start_time']).split('.')[0] if self.stats['start_time'] else None,
                'total_lines': self.stats['total_lines'],
                'port': self.port,
                'baud': self.baud
            },
            'statistics': {
                'errors': self.stats['errors'],
                'warnings': self.stats['warnings'],
                'error_breakdown': dict(self.error_counts),
                'warning_breakdown': dict(self.warning_counts)
            },
            'final_metrics': asdict(self.current_metrics),
            'metrics_history': list(self.metrics_history)
        }
        
        # Save report
        report_file = self.logs_dir / f"monitor_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        print(f"📄 Final report saved to {report_file}")

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="ESP32-C6 VESC Express Log Monitor")
    parser.add_argument("-p", "--port", default="/dev/ttyACM0", help="Serial port")
    parser.add_argument("-b", "--baud", type=int, default=115200, help="Baud rate")
    parser.add_argument("-t", "--timeout", type=int, help="Monitor timeout in seconds")
    
    args = parser.parse_args()
    
    monitor = VESCLogMonitor(args.port, args.baud)
    
    try:
        if args.timeout:
            # Start monitoring in background
            import signal
            
            def timeout_handler(signum, frame):
                print(f"\n⏰ Timeout reached ({args.timeout}s)")
                monitor.stop_monitoring()
            
            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(args.timeout)
        
        monitor.start_monitoring()
        
    except Exception as e:
        print(f"💥 Fatal error: {e}")
        exit(1)

if __name__ == "__main__":
    main()