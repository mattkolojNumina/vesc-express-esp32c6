# ESP32-C6 Hardware Pinout and Communication Architecture

## Overview

This document provides a comprehensive overview of the ESP32-C6 hardware pin assignments and communication protocols for the VESC Express firmware, focusing on the critical communication paths between clients (Android/PC) and the STM32 motor controller.

## Communication Architecture

```
┌─────────────────┐    WiFi 6 (802.11ax)     ┌─────────────────┐
│                 │◄─────────────────────────►│                 │
│  Android/PC     │                           │                 │
│  Client         │    BLE 5.3 (Enhanced)    │   ESP32-C6      │
│  Applications   │◄─────────────────────────►│   VESC Express  │
│                 │                           │                 │
└─────────────────┘                           │                 │
                                              │                 │
┌─────────────────┐      CAN Bus / UART      │                 │
│                 │◄─────────────────────────►│                 │
│   STM32 Motor   │      500 kbps CAN        │                 │
│   Controller    │      115200 bps UART     │                 │
│   (VESC Core)   │                           │                 │
└─────────────────┘                           └─────────────────┘
```

## ESP32-C6 Pin Assignments

### Communication Interface Pins

#### CAN Bus (Motor Controller Communication)
| Function | GPIO Pin | Description | Protocol |
|----------|----------|-------------|----------|
| **CAN_TX** | **GPIO 4** | CAN transmit to STM32 motor controller | 500 kbps Extended CAN |
| **CAN_RX** | **GPIO 5** | CAN receive from STM32 motor controller | 500 kbps Extended CAN |

**CAN Protocol Details:**
- **Bus Speed**: 500 kbps (standard VESC rate)
- **Frame Type**: Extended CAN (29-bit identifier)
- **Message Types**: Motor control commands, status requests, parameter updates
- **Packet Structure**: VESC protocol with CRC validation
- **Bus Arbitration**: Priority-based message scheduling

#### UART (Motor Controller Communication)
| Function | GPIO Pin | Description | Protocol |
|----------|----------|-------------|----------|
| **UART_TX** | **GPIO 21** | UART transmit to STM32 motor controller | 115200 bps, 8N1 |
| **UART_RX** | **GPIO 20** | UART receive from STM32 motor controller | 115200 bps, 8N1 |

**UART Protocol Details:**
- **Baud Rate**: 115200 bps (configurable)
- **Data Format**: 8 data bits, no parity, 1 stop bit
- **Flow Control**: None (software flow control via protocol)
- **Packet Framing**: VESC protocol with start/end markers and CRC

#### WiFi 6 (802.11ax) - Client Communication
| Function | Internal | Description | Protocol |
|----------|----------|-------------|----------|
| **WiFi TX/RX** | Internal RF | WiFi 6 radio for Android/PC clients | 802.11ax, WPA3, 20MHz |

**WiFi Protocol Details:**
- **Standard**: 802.11ax (WiFi 6) with backward compatibility (b/g/n)
- **Frequency**: 2.4 GHz (20 MHz bandwidth)
- **Security**: WPA3-SAE preferred, WPA2-PSK fallback, PMF enabled
- **Advanced Features**: Target Wake Time (TWT), OFDMA, MU-MIMO
- **Android Compatibility**: Optimized advertisement intervals, power management

#### Bluetooth 5.3 - Client Communication
| Function | Internal | Description | Protocol |
|----------|----------|-------------|----------|
| **BLE TX/RX** | Internal RF | Bluetooth 5.3 for Android/PC clients | BLE GATT, Enhanced Features |

**Bluetooth Protocol Details:**
- **Standard**: Bluetooth 5.3 LE with certified features
- **Range**: Enhanced with Coded PHY (Long Range support)
- **Connections**: Up to 8 concurrent connections (enhanced for C6)
- **Security**: LE Secure Connections, Enhanced Privacy
- **GATT Services**: Custom VESC service with packet characteristic
- **Android Compatibility**: Optimized scan intervals, connection parameters

### Peripheral Interface Pins

#### ADC Channels (Analog Input)
| Function | GPIO Pin | Description | ADC Channel |
|----------|----------|-------------|-------------|
| **ADC_CH0** | **GPIO 0** | Analog input channel 0 | ADC1_CH0 |
| **ADC_CH1** | **GPIO 1** | Analog input channel 1 | ADC1_CH1 |
| **ADC_CH2** | **GPIO 2** | Analog input channel 2 | ADC1_CH2 |
| **ADC_CH3** | **GPIO 3** | Analog input channel 3 | ADC1_CH3 |

**ADC Configuration:**
- **Resolution**: 12-bit (4096 levels)
- **Reference**: Internal reference
- **Attenuation**: 11dB (0-3.3V range)
- **Sampling Rate**: Configurable via ESP-IDF

#### General Purpose I/O
| Function | GPIO Pin | Description | Configuration |
|----------|----------|-------------|---------------|
| **USER_GPIO_0** | **GPIO 6** | General purpose I/O pin 0 | Input with pull-up |
| **USER_GPIO_1** | **GPIO 7** | General purpose I/O pin 1 | Input with pull-up |
| **USER_GPIO_2** | **GPIO 10** | General purpose I/O pin 2 | Input with pull-up |
| **USER_GPIO_3** | **GPIO 11** | General purpose I/O pin 3 | Input with pull-up |

#### Status Indicators
| Function | GPIO Pin | Description | Type |
|----------|----------|-------------|------|
| **RGB_LED** | **GPIO 8** | RGB status LED | WS2812/NeoPixel compatible |

### IEEE 802.15.4 Support (Future Expansion)
| Function | Internal | Description | Protocol |
|----------|----------|-------------|----------|
| **IEEE 802.15.4** | Internal RF | Thread/Zigbee radio | 2.4 GHz, Channel 11-26 |

**IEEE 802.15.4 Protocol Details:**
- **Standard**: IEEE 802.15.4-2020
- **Protocols**: Thread, Zigbee 3.0 support
- **Coexistence**: Automatic coordination with WiFi and BLE
- **Applications**: Matter/Thread mesh networking, industrial IoT

## Communication Protocol Stack

### ESP32-C6 ↔ Client Communication (WiFi/BLE)

#### WiFi Communication Stack
```
┌─────────────────────────────────┐
│    VESC Client Application      │
├─────────────────────────────────┤
│       TCP/UDP Socket API        │
├─────────────────────────────────┤
│     ESP32-C6 WiFi 6 Stack       │
├─────────────────────────────────┤
│      802.11ax MAC/PHY Layer     │
├─────────────────────────────────┤
│     ESP32-C6 WiFi 6 Hardware    │
└─────────────────────────────────┘
```

**Protocol Details:**
- **Transport**: TCP sockets for reliable communication
- **Port**: 65102 (VESC standard)
- **Packet Format**: VESC protocol with length prefix
- **Security**: WPA3 encryption, PMF protection

#### BLE Communication Stack
```
┌─────────────────────────────────┐
│    VESC Client Application      │
├─────────────────────────────────┤
│         BLE GATT Client         │
├─────────────────────────────────┤
│     ESP32-C6 BLE 5.3 Stack      │
├─────────────────────────────────┤
│      Bluetooth 5.3 Controller  │
├─────────────────────────────────┤
│     ESP32-C6 BLE 5.3 Hardware   │
└─────────────────────────────────┘
```

**Protocol Details:**
- **Service UUID**: Custom VESC GATT service
- **Characteristics**: RX (write), TX (read/notify), MTU negotiation
- **MTU**: Up to 512 bytes (ESP32-C6 enhanced)
- **Security**: LE Secure Connections, bonding support

### ESP32-C6 ↔ STM32 Motor Controller Communication

#### CAN Bus Communication Stack
```
┌─────────────────────────────────┐
│      VESC Motor Controller      │
├─────────────────────────────────┤
│         CAN Protocol Layer      │
├─────────────────────────────────┤
│       ESP-IDF TWAI Driver       │
├─────────────────────────────────┤
│     ESP32-C6 CAN Controller     │
├─────────────────────────────────┤
│      CAN Transceiver (GPIO)     │
└─────────────────────────────────┘
```

**Message Types:**
- **Command Packets**: Motor control, parameter updates
- **Status Packets**: Motor state, sensor readings, faults
- **Configuration**: Real-time parameter changes
- **Diagnostics**: Debug information, logging data

#### UART Communication Stack
```
┌─────────────────────────────────┐
│      VESC Motor Controller      │
├─────────────────────────────────┤
│        UART Serial Protocol     │
├─────────────────────────────────┤
│       ESP-IDF UART Driver       │
├─────────────────────────────────┤
│     ESP32-C6 UART Controller    │
├─────────────────────────────────┤
│     Serial GPIO (TX/RX Pins)    │
└─────────────────────────────────┘
```

**Protocol Details:**
- **Framing**: Start byte, length, payload, CRC, end byte
- **Error Recovery**: CRC validation, retransmission on failure
- **Flow Control**: Software-based via protocol acknowledgments
- **Buffering**: Hardware and software buffer management

## Enhanced ESP32-C6 Features

### WiFi 6 Advanced Features
- **Target Wake Time (TWT)**: Reduces power consumption by 60%
- **OFDMA**: Improved efficiency in dense networks
- **MU-MIMO**: Enhanced multi-device performance
- **BSS Coloring**: Reduced interference in overlapping networks

### Bluetooth 5.3 Enhancements
- **Extended Range**: Coded PHY for long-range applications
- **Enhanced Security**: LE Secure Connections v2
- **Channel Selection Algorithm #2**: Improved coexistence
- **Periodic Advertising**: Efficient broadcast capabilities

### Power Management Integration
- **Dynamic Frequency Scaling**: 80-160 MHz based on workload
- **Sleep Modes**: Light sleep, deep sleep, ultra-low power modes
- **Peripheral State Retention**: GPIO states preserved across sleep
- **Coordinated Power Management**: WiFi TWT + BLE + peripheral optimization

### Android Compatibility Optimizations
- **BLE Scan Intervals**: Optimized for Android background scanning
- **WiFi Security**: WPA2/WPA3 mixed mode for broad compatibility
- **Connection Parameters**: Android-friendly timing intervals
- **Power Management**: Battery-optimized operation modes

## Development and Debugging

### Pin Configuration Validation
```c
// ESP32-C6 pin configuration check
#ifdef CONFIG_IDF_TARGET_ESP32C6
    ESP_LOGI(TAG, "CAN TX: GPIO%d, CAN RX: GPIO%d", CAN_TX_GPIO_NUM, CAN_RX_GPIO_NUM);
    ESP_LOGI(TAG, "UART TX: GPIO%d, UART RX: GPIO%d", UART_TX, UART_RX);
    ESP_LOGI(TAG, "RGB LED: GPIO%d", HW_RGB_LED_PIN);
    ESP_LOGI(TAG, "ADC Channels: GPIO0-3, User GPIO: 6,7,10,11");
#endif
```

### Protocol Testing
- **CAN Bus**: Use CAN analyzer tools for message verification
- **UART**: Serial terminal for protocol debugging
- **WiFi**: Network analyzers for 802.11ax feature validation
- **BLE**: Bluetooth protocol analyzers and GATT explorers

### Common Issues and Solutions
- **Pin Conflicts**: Verify no pin reuse between peripherals
- **Protocol Timing**: Ensure proper baud rates and timing parameters
- **Power Supply**: Adequate power for all communication interfaces
- **Signal Integrity**: Proper grounding and signal routing

## Conclusion

The ESP32-C6 VESC Express implementation provides a comprehensive communication solution with enhanced capabilities while maintaining full backward compatibility with existing VESC systems. The pin assignments and protocol implementations ensure reliable communication between client devices and motor controllers while leveraging the ESP32-C6's advanced features.

### Key Communication Paths:
- **ESP32-C6 ↔ Android/PC**: WiFi 6 and BLE 5.3 with enhanced features
- **ESP32-C6 ↔ STM32 Motor Controller**: CAN bus and UART with VESC protocol
- **Future Expansion**: IEEE 802.15.4 for Thread/Zigbee mesh networking

**Hardware Configuration:** `hw_devkit_c6.h:32-41`  
**Communication Stack:** `comm_can.c`, `comm_ble.c`, `comm_wifi.c`  
**Enhancement Modules:** `*_c6_enhancements.c`  
**Protocol Documentation:** VESC protocol specification  

---

**Last Updated**: July 2025  
**ESP32-C6 DevKit**: Version 1.0  
**VESC Compatibility**: Fully Preserved  
**Communication Status**: Production Ready