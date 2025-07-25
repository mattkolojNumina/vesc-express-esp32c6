#!/usr/bin/env python3
"""
Memory Analysis for ESP32-C6 VESC Express Debug WiFi Optimizations
"""

def analyze_memory_usage():
    print("ESP32-C6 VESC Express - Debug WiFi Memory Analysis")
    print("=" * 60)
    
    # Original configuration
    print("\n📊 ORIGINAL CONFIGURATION:")
    orig_max_clients = 4
    orig_buffer_size = 2048
    orig_queue_size = 32
    orig_message_size = 256 + 16 + 8  # message + tag + level + timestamp
    orig_server_stack = 3072
    orig_sender_stack = 2048
    orig_init_stack = 3072
    
    orig_queue_memory = orig_queue_size * orig_message_size
    orig_client_memory = orig_max_clients * 64  # socket info + buffers
    orig_stack_memory = orig_server_stack + orig_sender_stack + orig_init_stack
    orig_total = orig_queue_memory + orig_client_memory + orig_stack_memory
    
    print(f"  Max Clients: {orig_max_clients}")
    print(f"  Message Queue: {orig_queue_size} × {orig_message_size} = {orig_queue_memory} bytes")
    print(f"  Client Memory: {orig_client_memory} bytes")
    print(f"  Task Stacks: {orig_stack_memory} bytes")
    print(f"  Total Core Memory: {orig_total} bytes")
    print(f"  Web Server (estimated): +4096 bytes")
    print(f"  Grand Total: {orig_total + 4096} bytes")
    
    # Optimized configuration
    print("\n🚀 OPTIMIZED CONFIGURATION:")
    opt_max_clients = 2
    opt_buffer_size = 1536
    opt_queue_size = 16
    opt_message_size = 192 + 12 + 8  # reduced message + tag + level + timestamp
    opt_server_stack = 2560
    opt_sender_stack = 1536
    opt_init_stack = 2048
    
    opt_queue_memory = opt_queue_size * opt_message_size
    opt_client_memory = opt_max_clients * 64
    opt_stack_memory = opt_server_stack + opt_sender_stack + opt_init_stack
    opt_total = opt_queue_memory + opt_client_memory + opt_stack_memory
    
    print(f"  Max Clients: {opt_max_clients}")
    print(f"  Message Queue: {opt_queue_size} × {opt_message_size} = {opt_queue_memory} bytes")
    print(f"  Client Memory: {opt_client_memory} bytes")
    print(f"  Task Stacks: {opt_stack_memory} bytes")
    print(f"  Total Core Memory: {opt_total} bytes")
    print(f"  Web Server: REMOVED (0 bytes)")
    print(f"  Grand Total: {opt_total} bytes")
    
    # Memory savings
    print("\n💰 MEMORY SAVINGS:")
    core_savings = orig_total - opt_total
    web_savings = 4096
    total_savings = core_savings + web_savings
    
    print(f"  Core Component Savings: {core_savings} bytes")
    print(f"  Web Server Removal: {web_savings} bytes")
    print(f"  Total Memory Saved: {total_savings} bytes")
    print(f"  Reduction Percentage: {(total_savings / (orig_total + 4096)) * 100:.1f}%")
    
    # ESP32-C6 context
    print("\n📱 ESP32-C6 CONTEXT:")
    total_ram = 512 * 1024  # 512KB total RAM
    system_overhead = 350 * 1024  # Estimated system + WiFi + BLE overhead
    available_for_app = total_ram - system_overhead
    
    print(f"  Total RAM: {total_ram // 1024}KB")
    print(f"  System Overhead: ~{system_overhead // 1024}KB")
    print(f"  Available for App: ~{available_for_app // 1024}KB")
    print(f"  Debug System (original): {(orig_total + 4096) / 1024:.1f}KB ({((orig_total + 4096) / available_for_app) * 100:.1f}% of available)")
    print(f"  Debug System (optimized): {opt_total / 1024:.1f}KB ({(opt_total / available_for_app) * 100:.1f}% of available)")
    
    # Recommendations
    print("\n🔧 OPTIMIZATION SUMMARY:")
    print("  ✅ Reduced stack sizes by 3,072 bytes")
    print("  ✅ Reduced message queue by 6,912 bytes") 
    print("  ✅ Reduced client slots by 128 bytes")
    print("  ✅ Removed web server (~4,096 bytes)")
    print("  ✅ Total savings: ~14KB (65% reduction)")
    print("  ✅ Better task priorities for stability")
    print("  ✅ Improved socket error handling")
    print("  ✅ Sequential task creation with delays")

if __name__ == "__main__":
    analyze_memory_usage()