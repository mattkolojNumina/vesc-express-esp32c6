/*
	Copyright 2023 Benjamin Vedder	benjamin@vedder.se

	This file is part of the VESC firmware.

	The VESC firmware is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    The VESC firmware is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
    */

#ifndef HW_DEVKIT_C6_H_
#define HW_DEVKIT_C6_H_

#define HW_NAME						"Devkit C3"

// BLE
#define HW_BLE_HAS_UART				1

// WiFi
#define HW_WIFI_6_SUPPORT			1
#define HW_WIFI_WPA3_SUPPORT		1

// CAN - ESP32-C6 DevKit CAN pins for VESC motor controller communication
#define HW_INIT_TWAI_NUM			0
#define CAN_TX_GPIO_NUM				4  // ESP32-C6 GPIO4 for CAN TX
#define CAN_RX_GPIO_NUM				5  // ESP32-C6 GPIO5 for CAN RX

// UART - ESP32-C6 DevKit UART pins for VESC motor controller communication
#define UART_NUM					0  // ESP32-C6 UART0
#define UART_TX						21 // ESP32-C6 GPIO21 for UART TX
#define UART_RX						20 // ESP32-C6 GPIO20 for UART RX
#define UART_BAUDRATE				115200

// HW properties
#define HW_DEAD_TIME_NSEC			600.0

// LEDs
#define HW_RGB_LED_PIN				8
#define HW_HAS_RGB_LED				1

// ADC Pins
#define HW_ADC_CH0					0
#define HW_ADC_CH1					1
#define HW_ADC_CH2					2
#define HW_ADC_CH3					3

// Digital I/O pins available for general use
#define HW_GPIO_USER_0				6
#define HW_GPIO_USER_1				7
#define HW_GPIO_USER_2				10
#define HW_GPIO_USER_3				11

// Hardware initialization hook - CRITICAL for hw_init() to be called
#define HW_INIT_HOOK()				hw_init()

// Functions
void hw_init(void);

#endif /* HW_DEVKIT_C6_H_ */