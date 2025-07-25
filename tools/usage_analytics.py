#!/usr/bin/env python3
"""
ESP32 Tool Usage Analytics
Track tool usage patterns and provide intelligent recommendations
"""

import json
import os
import time
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict, Counter

class ESP32ToolAnalytics:
    """
    Track and analyze ESP32 development tool usage patterns
    Provides intelligent recommendations based on usage history
    """
    
    def __init__(self, analytics_file=".vesc_analytics.json"):
        self.analytics_file = Path(analytics_file)
        self.data = self.load_analytics()
        
    def load_analytics(self):
        """Load existing analytics data"""
        if self.analytics_file.exists():
            try:
                with open(self.analytics_file, 'r') as f:
                    return json.load(f)
            except Exception:
                pass
        
        return {
            "tool_usage": {},
            "command_history": [],
            "session_data": {},
            "recommendations": {},
            "first_use": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat()
        }
    
    def save_analytics(self):
        """Save analytics data to file"""
        self.data["last_updated"] = datetime.now().isoformat()
        try:
            with open(self.analytics_file, 'w') as f:
                json.dump(self.data, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save analytics: {e}")
    
    def record_tool_usage(self, tool_name, success=True, duration=None):
        """Record tool usage event"""
        timestamp = datetime.now().isoformat()
        
        # Update tool usage counts
        if tool_name not in self.data["tool_usage"]:
            self.data["tool_usage"][tool_name] = {
                "count": 0,
                "success_count": 0,
                "failure_count": 0,
                "total_duration": 0,
                "first_used": timestamp,
                "last_used": timestamp
            }
        
        tool_data = self.data["tool_usage"][tool_name]
        tool_data["count"] += 1
        tool_data["last_used"] = timestamp
        
        if success:
            tool_data["success_count"] += 1
        else:
            tool_data["failure_count"] += 1
        
        if duration:
            tool_data["total_duration"] += duration
        
        # Add to command history
        self.data["command_history"].append({
            "tool": tool_name,
            "timestamp": timestamp,
            "success": success,
            "duration": duration
        })
        
        # Keep only last 100 commands
        if len(self.data["command_history"]) > 100:
            self.data["command_history"] = self.data["command_history"][-100:]
        
        self.save_analytics()
    
    def get_usage_stats(self):
        """Get comprehensive usage statistics"""
        stats = {
            "total_commands": len(self.data["command_history"]),
            "unique_tools": len(self.data["tool_usage"]),
            "most_used_tools": [],
            "recent_activity": [],
            "success_rate": 0,
            "session_info": {}
        }
        
        # Most used tools
        tool_counts = [(tool, data["count"]) for tool, data in self.data["tool_usage"].items()]
        stats["most_used_tools"] = sorted(tool_counts, key=lambda x: x[1], reverse=True)[:5]
        
        # Recent activity (last 24 hours)
        cutoff = datetime.now() - timedelta(hours=24)
        recent_commands = [
            cmd for cmd in self.data["command_history"]
            if datetime.fromisoformat(cmd["timestamp"]) > cutoff
        ]
        stats["recent_activity"] = recent_commands[-10:]  # Last 10 commands
        
        # Success rate
        if self.data["command_history"]:
            successes = sum(1 for cmd in self.data["command_history"] if cmd["success"])
            stats["success_rate"] = (successes / len(self.data["command_history"])) * 100
        
        return stats
    
    def get_intelligent_recommendations(self):
        """Generate intelligent tool recommendations based on usage patterns"""
        recommendations = []
        
        # Analyze current project state
        has_device = self._check_device_connected()
        has_build = self._check_build_exists()
        has_environment = self._check_environment_ready()
        
        # Analyze usage patterns
        stats = self.get_usage_stats()
        
        # Time-based recommendations
        now = datetime.now()
        hour = now.hour
        
        if 9 <= hour <= 17:  # Work hours
            if not has_device:
                recommendations.append({
                    "tool": "./vesc troubleshoot",
                    "reason": "Device connection issues during work hours",
                    "priority": "high",
                    "category": "troubleshooting"
                })
            elif not has_build:
                recommendations.append({
                    "tool": "./vesc build",
                    "reason": "No build detected - start development",
                    "priority": "high", 
                    "category": "development"
                })
        
        # Usage pattern based recommendations
        if stats["most_used_tools"]:
            most_used = stats["most_used_tools"][0][0]
            if "troubleshoot" in most_used.lower():
                recommendations.append({
                    "tool": "python tools/comprehensive_troubleshooting.py --auto-fix",
                    "reason": "Frequent troubleshooting - enable auto-fixes",
                    "priority": "medium",
                    "category": "optimization"
                })
        
        # Error pattern recommendations
        recent_failures = [
            cmd for cmd in stats["recent_activity"]
            if not cmd["success"]
        ]
        
        if len(recent_failures) >= 2:
            recommendations.append({
                "tool": "./vesc check",
                "reason": "Multiple recent failures detected",
                "priority": "high",
                "category": "diagnostics"
            })
        
        # Unused tool recommendations
        all_tools = [
            "comprehensive_troubleshooting.py",
            "esptool_advanced_suite.py", 
            "static_analysis_suite.py",
            "openocd_telnet_demo.py",
            "esp32c6_memory_debug.py"
        ]
        
        unused_tools = [
            tool for tool in all_tools
            if tool not in [used_tool for used_tool, _ in stats["most_used_tools"]]
        ]
        
        if unused_tools:
            recommendations.append({
                "tool": f"python tools/{unused_tools[0]}",
                "reason": "Explore unused analysis capabilities",
                "priority": "low",
                "category": "exploration"
            })
        
        return recommendations
    
    def _check_device_connected(self):
        """Check if ESP32 device is connected"""
        try:
            import subprocess
            result = subprocess.run(['lsusb'], capture_output=True, text=True)
            return '303a:1001' in result.stdout
        except:
            return False
    
    def _check_build_exists(self):
        """Check if build directory exists"""
        return Path("build").exists()
    
    def _check_environment_ready(self):
        """Check if ESP-IDF environment is ready"""
        return os.environ.get('IDF_PATH') is not None
    
    def generate_usage_report(self):
        """Generate comprehensive usage report"""
        stats = self.get_usage_stats()
        recommendations = self.get_intelligent_recommendations()
        
        report = f"""
ESP32 Tool Usage Analytics Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
=====================================

📊 USAGE STATISTICS
-------------------
Total Commands Executed: {stats['total_commands']}
Unique Tools Used: {stats['unique_tools']}
Overall Success Rate: {stats['success_rate']:.1f}%

🔥 MOST USED TOOLS
------------------"""
        
        for tool, count in stats["most_used_tools"]:
            report += f"\n{count:3d}x {tool}"
        
        report += f"""

🕒 RECENT ACTIVITY (Last 10 commands)
------------------------------------"""
        
        for cmd in stats["recent_activity"]:
            status = "✅" if cmd["success"] else "❌"
            timestamp = datetime.fromisoformat(cmd["timestamp"]).strftime('%H:%M')
            report += f"\n{status} {timestamp} {cmd['tool']}"
        
        report += f"""

💡 INTELLIGENT RECOMMENDATIONS
------------------------------"""
        
        for rec in recommendations:
            priority_icon = {"high": "🚨", "medium": "⚠️", "low": "💡"}[rec["priority"]]
            report += f"\n{priority_icon} {rec['tool']}"
            report += f"\n   Reason: {rec['reason']}"
            report += f"\n   Category: {rec['category']}\n"
        
        return report
    
    def show_dashboard(self):
        """Show usage analytics dashboard"""
        print("🎯 ESP32 Tool Usage Dashboard")
        print("=" * 35)
        print(self.generate_usage_report())

def track_command(tool_name, success=True, duration=None):
    """Convenience function to track command usage"""
    analytics = ESP32ToolAnalytics()
    analytics.record_tool_usage(tool_name, success, duration)

def show_recommendations():
    """Show intelligent recommendations"""
    analytics = ESP32ToolAnalytics()
    recommendations = analytics.get_intelligent_recommendations()
    
    if not recommendations:
        print("✅ No specific recommendations - all systems optimal!")
        return
    
    print("💡 Intelligent Tool Recommendations")
    print("=" * 40)
    
    for rec in recommendations:
        priority_icon = {"high": "🚨", "medium": "⚠️", "low": "💡"}[rec["priority"]]
        print(f"{priority_icon} {rec['priority'].upper()}: {rec['tool']}")
        print(f"   📝 {rec['reason']}")
        print(f"   🏷️  Category: {rec['category']}")
        print()

def main():
    """Main analytics interface"""
    import argparse
    
    parser = argparse.ArgumentParser(description='ESP32 Tool Usage Analytics')
    parser.add_argument('--dashboard', action='store_true', help='Show usage dashboard')
    parser.add_argument('--recommend', action='store_true', help='Show recommendations')
    parser.add_argument('--track', help='Track tool usage')
    parser.add_argument('--success', action='store_true', help='Mark tracked command as successful')
    parser.add_argument('--duration', type=float, help='Command duration in seconds')
    
    args = parser.parse_args()
    
    if args.dashboard:
        analytics = ESP32ToolAnalytics()
        analytics.show_dashboard()
    elif args.recommend:
        show_recommendations()
    elif args.track:
        track_command(args.track, args.success, args.duration)
        print(f"✅ Tracked usage of: {args.track}")
    else:
        print("ESP32 Tool Usage Analytics")
        print("Usage: python tools/usage_analytics.py --dashboard")
        print("       python tools/usage_analytics.py --recommend")
        print("       python tools/usage_analytics.py --track 'tool_name' --success")

if __name__ == "__main__":
    main()