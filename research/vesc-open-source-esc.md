# VESC – Open Source ESC

**Date**: January 7, 2015  
**Author**: Benjamin Vedder  
**Source**: https://vedder.se/2015/01/vesc-open-source-esc/

## Overview

Benjamin Vedder created an open-source Electronic Speed Controller (ESC) with the following key features:

### Hardware Specifications
- Microcontroller: STM32F4
- MOSFET Driver: DRV8302
- Voltage Range: 8V – 60V (3S to 12S LiPo)
- Current: Up to 240A (short burst), ~50A continuous
- PCB Size: Slightly less than 40mm x 60mm

### Software Features
- Open-source firmware and hardware
- Sensored and sensorless Field-Oriented Control (FOC)
- Multiple control modes:
  - Current control
  - Duty cycle control
  - Speed control
- Interfaces: PPM, analog, UART, I2C, USB, CAN-bus
- Regenerative braking
- Comprehensive motor parameter configuration

## Key Resources
- [Hardware Design on GitHub](https://github.com/vedderb/bldc-hardware)
- [Firmware on GitHub](https://github.com/vedderb/bldc)
- [Configuration GUI on GitHub](https://github.com/vedderb/bldc-tool)

## Installation Tutorial
The blog post includes a detailed Ubuntu Linux installation guide covering:
- Toolchain setup
- Firmware compilation
- Bootloader installation
- BLDC Tool configuration

## Licensing
"VESC Hardware by Benjamin Vedder is licensed under a Creative Commons Attribution-ShareAlike 4.0 International License."