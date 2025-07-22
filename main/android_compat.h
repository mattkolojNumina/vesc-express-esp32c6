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

#ifndef ANDROID_COMPAT_H_
#define ANDROID_COMPAT_H_

#include <stdbool.h>
#include <stdint.h>

// Android compatibility modes
typedef enum {
    ANDROID_COMPAT_DISABLED,    // No Android optimizations
    ANDROID_COMPAT_BASIC,       // Basic Android compatibility
    ANDROID_COMPAT_OPTIMIZED,   // Full Android optimizations
} android_compat_mode_t;

#ifdef CONFIG_IDF_TARGET_ESP32C6

// Function declarations for ESP32-C6
void android_compat_init(void);
void android_compat_set_mode(android_compat_mode_t mode);
android_compat_mode_t android_compat_get_mode(void);
bool android_compat_test_ble(void);
bool android_compat_test_wifi(void);
void android_compat_print_status(void);

#else
// Stub functions for non-C6 targets
static inline void android_compat_init(void) {}
static inline void android_compat_set_mode(android_compat_mode_t mode) { (void)mode; }
static inline android_compat_mode_t android_compat_get_mode(void) { return ANDROID_COMPAT_DISABLED; }
static inline bool android_compat_test_ble(void) { return true; }
static inline bool android_compat_test_wifi(void) { return true; }
static inline void android_compat_print_status(void) {}
#endif

#endif /* ANDROID_COMPAT_H_ */