# Debugging STM32F4 using OpenOCD, GDB, and Eclipse

**Date**: December 2012  
**Author**: Benjamin Vedder  
**Source**: http://vedder.se/2012/12/debugging-the-stm32f4-using-openocd-gdb-and-eclipse/

## Prerequisites
- STM32F4 discovery board
- Built-in SWD programmer/debugger
- Ubuntu Linux
- Toolchain from tutorial

## Setup Steps

### Install Toolchain
1. Follow the original tutorial to install:
   - Summon-arm toolchain
   - Eclipse
   - Zylin Eclipse plugin

### Configure Debug Configuration
1. In Eclipse, create a new "Zylin Embedded debug (Native)" configuration
2. Set project name and select .elf file
3. Configure GDB path (typically `/home/YOUR_USERNAME/sat/bin/arm-none-eabi-gdb`)
4. Add initialization commands:
   ```
   target remote localhost:3333
   monitor reset
   monitor halt
   load
   disconnect
   target remote localhost:3333
   monitor reset
   monitor halt
   ```

### Start OpenOCD Server
1. Create `stm32f4discovery.cfg`:
   ```
   source [find interface/stlink-v2.cfg]
   source [find target/stm32f4x_stlink.cfg]
   reset_config srst_only srst_nogate
   ```
2. Run OpenOCD: `openocd -f stm32f4discovery.cfg`

## Debugging Techniques
- Set hardware breakpoints
- Inspect variable values
- Modify variables during debugging
- View source code and assembly

## Troubleshooting
- Unplug/replug board if debugging fails
- Disable code optimizations for better debugging
- Ensure `-g` compiler flag is used for symbol information

## Key Tips
- Use `-O0` optimization for debugging
- Compile with `-g` flag
- Restart OpenOCD if connection issues occur