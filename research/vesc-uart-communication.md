# Communicating with VESC using UART

**Date**: October 2015  
**Author**: Benjamin Vedder  
**Source**: http://vedder.se/2015/10/communicating-with-the-vesc-using-uart/

## Protocol Overview

The VESC communicates over UART using packets with the following format:
- Start byte (2 for short packets, 3 for long packets)
- Packet length (1-2 bytes)
- Payload 
- 2-byte CRC checksum
- Stop byte (value 3)

## Key Implementation Files

Important files for UART communication:
- `bldc_interface.c/.h`: Assembles and interprets command payloads
- `datatypes.h`: VESC data structures
- `packet.c/.h`: Packet assembly and state machine
- `bldc_interface_uart.c/.h`: UART interface connection

## Initialization Example

```c
// Send packet function
static void send_packet(unsigned char *data, unsigned int len) {
    // Platform-specific UART send implementation
}

// UART initialization 
void comm_uart_init(void) {
    // Initialize UART
    bldc_interface_uart_init(send_packet);
}
```

## Reading Data Example

```c
// Callback for received values
void bldc_val_received(mc_values *val) {
    printf("Input voltage: %.2f V\n", val->v_in);
    printf("RPM: %.1f RPM\n", val->rpm);
    // Print other values
}

// Set callback and request data
bldc_interface_set_rx_value_func(bldc_val_received);
bldc_interface_get_values();
```

## Sending Commands

```c
// Set motor current
bldc_interface_set_current(10.0);

// Send periodic alive signal
bldc_interface_send_alive();
```

## Packet Format Details

### Short Packet (< 256 bytes)
- Start byte: `0x02`
- Length: 1 byte (payload length)
- Payload: Variable length
- CRC: 2 bytes
- Stop byte: `0x03`

### Long Packet (≥ 256 bytes)
- Start byte: `0x03`
- Length: 2 bytes (payload length)
- Payload: Variable length
- CRC: 2 bytes
- Stop byte: `0x03`

## Key Considerations

- Call setter functions regularly to prevent motor timeout
- Implement platform-specific UART send and receive functions
- Use callback functions for asynchronous data reception
- Handle packet framing and CRC validation properly

## Platforms

- Original implementation: STM32F4 Discovery Board
- Community implementations: Arduino, iOS
- ESP32 implementations for wireless connectivity

## Data Structures

Key data types from `datatypes.h`:
- `mc_values`: Motor controller values (voltage, current, RPM, etc.)
- `mc_configuration`: Motor configuration parameters
- `app_configuration`: Application-specific settings