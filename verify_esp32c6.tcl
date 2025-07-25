#!/usr/bin/expect -f

# ESP32-C6 verification script via OpenOCD
spawn telnet localhost 4444

expect ">"

# Check if ESP32-C6 is halted or running
send "halt\r"
expect ">"

# Read program counter to verify it's running
send "reg pc\r"
expect ">"

# Check if we can read memory (indicates successful connection)
send "mdw 0x40000000 1\r"
expect ">"

# Resume execution
send "resume\r"
expect ">"

# Read some system registers to verify functionality
send "halt\r"
expect ">"

send "reg\r"
expect ">"

send "resume\r"
expect ">"

send "exit\r"
expect eof