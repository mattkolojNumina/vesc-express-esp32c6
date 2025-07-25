/*
	Copyright 2024 Benjamin Vedder	benjamin@vedder.se

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

#ifndef HUB_MOTOR_ENHANCEMENTS_H_
#define HUB_MOTOR_ENHANCEMENTS_H_

#include <stdbool.h>
#include <stdint.h>

// Hub Motor Configuration Structure (Research-Based 2024)
typedef struct {
    // FOC Low-Speed Torque Optimization (2024 Research)
    float foc_observer_gain_multiplier;  // Default: 0.5 (50% of wizard value)
    float foc_motor_resistance_multiplier; // Default: 1.05 (105% of wizard value)
    bool low_speed_torque_optimization;    // Enable/disable optimization
    
    // Cogging Torque Reduction
    bool cogging_compensation_enabled;     // Enable cogging compensation
    float cogging_compensation_gain;       // Compensation strength (0.0-1.0)
    uint16_t cogging_lut_size;            // Lookup table size (default: 360)
    
    // Thermal Management
    bool thermal_protection_enabled;       // Enable thermal protection
    float temp_motor_warning;             // Warning temperature (°C)
    float temp_motor_critical;            // Critical temperature (°C)
    float thermal_derating_rate;          // Power reduction rate (%/°C)
    
    // Hub Motor Specific Parameters
    uint8_t motor_pole_pairs;             // Number of pole pairs
    float hub_motor_inertia;              // Motor inertia (kg⋅m²)
    bool hall_sensor_enabled;             // Hall sensor availability
    
    // ESP32-C6 Enhanced Features
    bool wifi6_motor_control;             // WiFi 6 optimized control
    bool ble53_long_range;                // BLE 5.3 long range mode
    bool dual_core_optimization;          // Dual-core RISC-V optimization
} hub_motor_config_t;

// Default Configuration (Research-Based Optimal Settings)
#define HUB_MOTOR_CONFIG_DEFAULT() { \
    .foc_observer_gain_multiplier = 0.5f, \
    .foc_motor_resistance_multiplier = 1.05f, \
    .low_speed_torque_optimization = true, \
    .cogging_compensation_enabled = true, \
    .cogging_compensation_gain = 0.8f, \
    .cogging_lut_size = 360, \
    .thermal_protection_enabled = true, \
    .temp_motor_warning = 70.0f, \
    .temp_motor_critical = 85.0f, \
    .thermal_derating_rate = 0.02f, \
    .motor_pole_pairs = 15, \
    .hub_motor_inertia = 0.5f, \
    .hall_sensor_enabled = true, \
    .wifi6_motor_control = true, \
    .ble53_long_range = true, \
    .dual_core_optimization = true \
}

// Function Declarations
void hub_motor_foc_init_optimization(void);
bool hub_motor_configure_features(const hub_motor_config_t *config);
void hub_motor_init_cogging_lut(void);
float hub_motor_calculate_cogging_compensation(float rotor_position, float temperature);
float hub_motor_calculate_thermal_derating(float motor_temp, float controller_temp);
void hub_motor_apply_foc_optimization(void);
bool hub_motor_validate_configuration(const hub_motor_config_t *config);
void hub_motor_print_capabilities(void);

// Thermal Management Functions
typedef struct {
    float motor_temp;      // Hub motor internal temperature
    float controller_temp; // ESP32-C6 junction temperature
    float ambient_temp;    // Environmental temperature
    float battery_temp;    // Battery pack temperature
} thermal_state_t;

// Cogging Compensation Functions
typedef struct {
    float electrical_angle;
    float compensation_current;
    float temperature_factor;
} cogging_lut_t;

#endif /* HUB_MOTOR_ENHANCEMENTS_H_ */