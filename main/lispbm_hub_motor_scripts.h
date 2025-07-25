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

#ifndef LISPBM_HUB_MOTOR_SCRIPTS_H_
#define LISPBM_HUB_MOTOR_SCRIPTS_H_

// Hub Motor LispBM Script Types
typedef enum {
    HUB_MOTOR_SCRIPT_BASIC_CONTROL = 0,     // Basic hub motor control
    HUB_MOTOR_SCRIPT_ADAPTIVE_PID,          // Adaptive PID controller
    HUB_MOTOR_SCRIPT_SAFETY_MONITOR,        // Safety monitoring
    HUB_MOTOR_SCRIPT_COGGING_COMPENSATION,  // Cogging torque compensation
    HUB_MOTOR_SCRIPT_REGEN_OPTIMIZER,       // Regenerative braking optimization
    HUB_MOTOR_SCRIPT_MULTI_MOTOR_COORD,     // Multi-motor coordination
    HUB_MOTOR_SCRIPT_THERMAL_MANAGEMENT,    // Thermal management
    HUB_MOTOR_SCRIPT_COUNT                  // Total number of scripts
} hub_motor_script_type_t;

// Function declarations
void lispbm_hub_motor_init_scripts(void);
const char* lispbm_get_hub_motor_script(hub_motor_script_type_t script_type);
void lispbm_hub_motor_print_script_info(void);

#endif /* LISPBM_HUB_MOTOR_SCRIPTS_H_ */