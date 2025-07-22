/*
	Copyright 2025 Benjamin Vedder	benjamin@vedder.se

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

#ifndef TEST_ANDROID_COMPAT_H_
#define TEST_ANDROID_COMPAT_H_

#include <stdbool.h>

// Test results structure
typedef struct {
	bool ble_adv_intervals_ok;
	bool ble_mtu_support_ok;
	bool ble_power_mgmt_ok;
	bool wifi_security_ok;
	bool wifi_pmf_ok;
	bool wifi_power_mgmt_ok;
} android_compat_test_results_t;

/**
 * Run comprehensive Android compatibility tests
 * @return true if all tests pass, false otherwise
 */
bool run_android_compatibility_tests(void);

/**
 * Get the last test results
 * @return Structure containing individual test results
 */
android_compat_test_results_t get_android_compat_test_results(void);

/**
 * Start Android compatibility tests as a background task
 */
void start_android_compatibility_tests(void);

/**
 * Validate Android device compatibility at runtime
 * @return true if Android device compatibility is validated
 */
bool validate_android_device_compatibility(void);

#endif /* TEST_ANDROID_COMPAT_H_ */