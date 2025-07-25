# A Custom BLDC Motor Controller (ESC)

**Date**: January 2014  
**Author**: Benjamin Vedder  
**Source**: http://vedder.se/2014/01/a-custom-bldc-motor-controller/

## Overview
Benjamin created an open-source brushless DC motor controller with the following key features:

### Hardware Specifications
- Microcontroller: STM32F4
- MOSFET Driver: DRV8302
- Voltage Range: 8V - 60V
- Current: Up to 240A (peak), ~50A continuous
- PCB Size: < 40mm x 60mm
- 4-layer PCB design

### Key Features
- Sensorless or sensored commutation
- Regenerative braking
- Multiple control interfaces:
  - Servo signal
  - Analog
  - UART
  - I2C
  - USB
  - CAN

### Advanced Capabilities
- Adaptive PWM frequency
- RPM-based phase advance
- Duty cycle/speed/current control
- Comprehensive motor protection
- Soft back-off strategies for current/RPM limits

## Software
- Uses ChibiOS for STM32F4
- Includes Qt debugging tool
- Open-source firmware available on GitHub

## Development Notes
Benjamin emphasizes this is an ongoing project with continuous improvements, recommending users refer to the latest hardware versions on GitHub.

## Recommended Use
Suitable for various applications including:
- RC vehicles
- Electric bikes
- Robotics
- Multicopters

## Licensing
Fully open-source hardware and software