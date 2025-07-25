# VESC Research Documentation

This directory contains technical documentation and research materials related to VESC (Vedder Electronic Speed Controller) development and implementation.

## Benjamin Vedder's Original Articles

### Core VESC Documentation
- **[vesc-open-source-esc.md](vesc-open-source-esc.md)** - January 2015  
  Complete overview of the open-source VESC project including hardware specifications, software features, and installation guide.

- **[custom-bldc-motor-controller.md](custom-bldc-motor-controller.md)** - January 2014  
  Original blog post about creating a custom BLDC motor controller with advanced features.

### Technical Implementation Details
- **[startup-torque-sensorless-bldc.md](startup-torque-sensorless-bldc.md)** - August 2014  
  Advanced techniques for achieving smooth startup and low-speed performance with sensorless BLDC motors.

- **[vesc-uart-communication.md](vesc-uart-communication.md)** - October 2015  
  Complete guide to UART communication protocol, packet format, and programming examples.

- **[vesc-writing-custom-applications.md](vesc-writing-custom-applications.md)** - August 2015  
  Tutorial on writing custom C applications for VESC using ChibiOS.

### Development Tools
- **[debugging-stm32f4-openocd-gdb.md](debugging-stm32f4-openocd-gdb.md)** - December 2012  
  Setup guide for debugging STM32F4 using OpenOCD, GDB, and Eclipse.

## Component Specifications

### Hardware Components
- **[ti-drv8302-specifications.md](ti-drv8302-specifications.md)**  
  Technical specifications for the TI DRV8302 MOSFET driver chip used in VESC hardware.

### Software Platform
- **[chibios-rtos-overview.md](chibios-rtos-overview.md)**  
  Overview of ChibiOS real-time operating system used in VESC firmware.

## Relevance to ESP32-C6 VESC Express

These documents provide essential background for understanding:

1. **Protocol Compatibility**: UART communication protocols that must be maintained
2. **Motor Control Algorithms**: Startup techniques and sensorless control methods
3. **Real-Time Requirements**: Timing constraints and threading models
4. **Hardware Integration**: Component interfaces and protection mechanisms
5. **Application Development**: Custom code integration patterns

## Research Date
Collected: July 25, 2025  
For: ESP32-C6 VESC Express firmware development