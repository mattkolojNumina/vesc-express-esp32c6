# TI DRV8302 MOSFET Driver Specifications

**Source**: http://www.ti.com/product/drv8302  
**Component**: Three-Phase Gate Driver IC used in VESC

## Key Features
- 8-V to 60-V Operating Supply Voltage Range
- 1.7-A Source and 2.3-A Sink Gate Drive Current
- Bootstrap Gate Driver with 100% Duty Cycle Support
- 6 or 3 PWM Input Modes
- Dual Integrated Current Shunt Amplifiers
- 3.3-V and 5-V Interface Support

## Technical Specifications
- Maximum Voltage: 65V
- Operating Temperature: -40°C to 125°C
- Integrated Buck Converter: Up to 1.5A output
- Protection Features:
  - Programmable Dead Time Control
  - Overcurrent Protection
  - Undervoltage/Overvoltage Lockout
  - Overtemperature Warning/Shutdown

## Unique Capabilities
- Supports three-phase motor drive applications
- Automatic handshaking to prevent current shoot-through
- Integrated VDS sensing for power stage protection
- Configurable via hardware interface
- Error reporting through nFAULT and nOCTW pins

## Application in VESC
The DRV8302 serves as the critical interface between the STM32F4 microcontroller and the power MOSFETs in the VESC design:

- **Gate Driving**: Provides high-current gate drive for six MOSFETs
- **Current Sensing**: Built-in amplifiers for motor current measurement
- **Protection**: Hardware-level protection against faults
- **Power Supply**: Integrated buck converter for system power
- **Interface**: SPI communication for configuration and status

## Pin Configuration
- **High-side drivers**: GPHA, GPHB, GPHC
- **Low-side drivers**: GPLA, GPLB, GPLC
- **Current sense**: SO1, SO2 outputs
- **Control interface**: SPI (SCLK, SDI, SDO, nSCS)
- **Protection**: nFAULT, nOCTW status pins