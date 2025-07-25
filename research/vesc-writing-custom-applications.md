# VESC - Writing Custom Applications

**Date**: August 2015  
**Author**: Benjamin Vedder  
**Source**: http://vedder.se/2015/08/vesc-writing-custom-applications/

## Overview
This tutorial explains how to write custom applications for the VESC (Vedder Electronic Speed Controller) using C programming. The custom application allows running additional user code alongside motor control.

## Preparation
1. Clone the VESC firmware repository
2. Ensure you can build and upload firmware

## Example Custom Application

### Code Structure
```c
#include "ch.h" // ChibiOS
#include "hal.h" // ChibiOS HAL
#include "mc_interface.h" // Motor control functions
#include "hw.h" // Pin mapping
#include "timeout.h" // Timeout reset

// Example thread function
static THD_FUNCTION(example_thread, arg);
static THD_WORKING_AREA(example_thread_wa, 2048);

void app_example_init(void) {
    // Initialize application
    palSetPadMode(HW_UART_TX_PORT, HW_UART_TX_PIN, PAL_MODE_INPUT_PULLDOWN);
    
    // Start thread
    chThdCreateStatic(example_thread_wa, sizeof(example_thread_wa),
        NORMALPRIO, example_thread, NULL);
}

static THD_FUNCTION(example_thread, arg) {
    for(;;) {
        // Read potentiometer value
        float pot = (float)ADC_Value[ADC_IND_EXT] / 4095.0;

        if (palReadPad(HW_UART_TX_PORT, HW_UART_TX_PIN)) {
            // Run motor with speed control
            mc_interface_set_pid_speed(pot * 10000.0);
        } else {
            // Release motor
            mc_interface_release_motor();
        }

        // Run loop at 500Hz
        chThdSleepMilliseconds(2);
        timeout_reset();
    }
}
```

## Integration Steps
1. Add application to `applications.mk`
2. Update `app.h` with application initialization
3. Modify `app.c` to include custom application
4. Build and flash firmware

## Key APIs Available
- **Motor Control**: `mc_interface_*` functions
- **Hardware Access**: `hw.h` pin definitions
- **ADC Reading**: Access to sensor inputs
- **ChibiOS**: Full RTOS functionality
- **Timeout Management**: Prevent watchdog resets

## Application Thread Management
- Use ChibiOS threading system
- Allocate working area for thread stack
- Call `timeout_reset()` regularly to prevent system reset
- Run main loop at appropriate frequency (typically 500Hz)

## Hardware Interface
- Direct GPIO control via ChibiOS HAL
- ADC access for analog sensors
- Timer and PWM functionality
- I2C, UART, and other peripheral access