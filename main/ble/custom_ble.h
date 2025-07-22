/*
	Copyright 2023 Rasmus Söderhielm    rasmus.soderhielm@gmail.com

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

#ifndef MAIN_BLE_CUSTOM_BLE_H_
#define MAIN_BLE_CUSTOM_BLE_H_

#include <stdint.h>
#include <stdlib.h>
#include <stdbool.h>

#ifdef CONFIG_BT_ENABLED
#include "esp_bt_defs.h"
#ifdef CONFIG_BT_ENABLED
#include "esp_gatt_defs.h"
#endif
#ifdef CONFIG_BT_ENABLED
#include "esp_gap_ble_api.h"
#endif
#else
// Stub definitions when Bluetooth is disabled
typedef struct { uint8_t dummy; } esp_bt_uuid_t;
typedef uint8_t esp_gatt_perm_t;
typedef uint8_t esp_gatt_char_prop_t;
typedef struct { uint8_t dummy; } esp_ble_adv_params_t;
#endif

#define CUSTOM_BLE_MAX_NAME_LEN 30

typedef enum {
	CUSTOM_BLE_OK                     = 0,
	/** Generic error. (Don't think this is ever returned to an external
	   caller...) */
	CUSTOM_BLE_ERROR                  = 1,
	/** Internal error caused by some ESP function. */
	CUSTOM_BLE_ESP_ERROR              = 2,
	/** Represents some internal error. Should hopefully never be returned. */
	CUSTOM_BLE_INTERNAL_ERROR         = 3,
	/** Failed due to the BLE server beeing started. */
	CUSTOM_BLE_ALREADY_STARTED        = 4,
	/** Failed due to the BLE server having not yet been started. */
	CUSTOM_BLE_NOT_STARTED            = 5,
	/** The name given to custom_ble_set_name was too long. */
	CUSTOM_BLE_NAME_TOO_LONG          = 6,
	/** Tried to create more than the configured amount of services. */
	CUSTOM_BLE_TOO_MANY_SERVICES      = 7,
	/** Tried to create more characteristics and/or descriptors than the
	   configured capacity. */
	CUSTOM_BLE_TOO_MANY_CHR_AND_DESCR = 8,
	/** The previously ran init function failed, causing this function to fail.
	 */
	CUSTOM_BLE_INIT_FAILED            = 9,
	/** Waiting for the BLE server to process action timed out. */
	CUSTOM_BLE_TIMEOUT                = 10,
	/** The specified server, characteristic, or descriptor handle didn't exist.
	 */
	CUSTOM_BLE_INVALID_HANDLE         = 11,
	/** Tried to remove a service which was not the most recent (not aldready
	 * removed) one. */
	CUSTOM_BLE_SERVICE_NOT_LAST       = 12,
	/** The given array was too long. */
	CUSTOM_BLE_TOO_LONG               = 13,
} custom_ble_result_t;

typedef struct {
	esp_bt_uuid_t uuid;
	esp_gatt_perm_t perm;

	uint16_t value_max_len;
	uint16_t value_len;
	/**
	 * The initial value. A copy of this value is created during
	 * initialization. May be null.
	 */
	uint8_t *value;
} ble_desc_definition_t;

typedef struct {
	esp_bt_uuid_t uuid;
	esp_gatt_perm_t perm;
	esp_gatt_char_prop_t property;

	uint16_t value_max_len;
	uint16_t value_len;
	/**
	 * The initial value. A copy of this value is created during
	 * initialization. May be null.
	 */
	uint8_t *value;

	uint16_t descr_count;
	/**
	 * List of descriptors to add to this characteristic. May be null.
	 */
	ble_desc_definition_t *descriptors;
} ble_chr_definition_t;

typedef void (*service_handles_cb_t)(
	uint16_t count, const uint16_t handles[count]
);

typedef void (*attr_write_cb_t)(
	uint16_t attr_handle, uint16_t len, uint8_t value[len]
);

/**
 * Set the device name to use for the ble service.
 * Must be called before starting the ble service.
 *
 * @param name The device name to use. May not be more than 30 characters long
 * (excluding the terminating null byte).
 * @return Returns CUSTOM_BLE_OK if successfull, otherwise
 * - CUSTOM_BLE_ALREADY_STARTED: The ble service has already been started
 *   using custom_ble_start.
 * - CUSTOM_BLE_NAME_TOO_LONG: The provided name was too long.
 */
custom_ble_result_t custom_ble_set_name(const char *name);

/**
 * Configure if custom raw advertising and scan response packets should be used,
 * and which should be set if that is the case.
 * 
 * The change will go into effect shortly after calling this, as an
 * event listener has to be called before the packets are updated.
 * If the BLE server has not been started yet the changes will take effect when
 * started.
 * 
 * This function should not be called by multiple threads simultaneously.
 * 
 * @param use_raw If custom raw packets should be used. All other
 * parameters are ignored if this is false.
 * @param adv_len The length of adv_data_raw in bytes. Must not be larger than
 * 31 bytes. Is ignored if adv_data_raw is NULL.
 * @param adv_data_raw Buffer containing the data for advertising packets.
 * Ownership is not transferred as a copy is made internally. The raw
 * advertising data is left unchanged if NULL is passed.
 * @param scan_rsp_len The length of adv_data_raw in bytes. Must not be larger than
 * 31 bytes. Is ignored if scan_rsp_data_raw is NULL.
 * @param scan_rsp_data_raw The buffer containing the data for scan response
 * packets. Ownership is not transferred as a copy is made internally.
 * The current raw scan response data is left unchanged if NULL is passed.
 * @return Returns CUSTOM_BLE_OK if successfull, otherwise
 * - CUSTOM_BLE_TOO_LONG:  adv_data_raw or scan_rsp_data_raw was longer than 31
 *   bytes.
 * - CUSTOM_BLE_ESP_ERROR: The internal call to esp_ble_gap_stop_advertising
 *   failed.
*/
custom_ble_result_t custom_ble_update_adv(
	bool use_raw, size_t adv_len, const uint8_t adv_data_raw[adv_len],
	size_t scan_rsp_len, const uint8_t scan_rsp_data_raw[scan_rsp_len]
);

/**
 * Configure a function that will be called whenever the value of a
 * characteristic or descriptor is written to by a client.
 *
 * @param callback The function that will be called once a client write event
 * occurs. The attribute handle together with the new value is
 * provided to the callback. Provide the value NULL will unset the callback.
 */
void custom_ble_set_attr_write_handler(attr_write_cb_t callback);

// TODO: If this fails, you're kinda screwed, since the internal attribute count
// is Still incremented, with no way to decrement it from the outside. Yeah...
// ._. Blocks until handles_cb has been called with the resulting handles.
/**
 * Add a service with the specified list of characteristics and descriptors.
 *
 * The created handles are returned to a callback function. This function will
 * always be called before this function returns. In other words this function
 * blocks until the service has been created.
 *
 * Note: You should only call this function from a single thread.
 *
 *
 * @param service_uuid The uuid of the created service.
 * @param chr_count The length of chr.
 * @param chr A list of characteristic definitions, that specifies the
 * characteristics and their descriptors that should be added. All sub pointers
 * in this struct only need to live for the duration of this function call.
 * @param handles_cb This function will be called with a list of the created
 * service, characteristic, and descriptor handles. The service handle is always
 * the first in this list, followed by the characteristic and descriptor
 * handles. These appear in the order that they were given in the characteristic
 * list, with each characteristic handle appearing before the handles of its
 * descriptors.
 * @return
 * - CUSTOM_BLE_OK
 * - CUSTOM_BLE_INIT_FAILED
 * - CUSTOM_BLE_NOT_STARTED
 * - CUSTOM_BLE_TOO_MANY_SERVICES:      The number of allocated services went
 *   above the configured capacity.
 * - CUSTOM_BLE_TOO_MANY_CHR_AND_DESCR: The number of allocated characteristics
 *   or descriptors went above the configured capacity.
 * - CUSTOM_BLE_ESP_ERROR
 * - CUSTOM_BLE_TIMEOUT
 * - CUSTOM_BLE_INTERNAL_ERROR:         Something wen't wrong internally
 */
custom_ble_result_t custom_ble_add_service(
	esp_bt_uuid_t service_uuid, uint16_t chr_count,
	const ble_chr_definition_t chr[chr_count], service_handles_cb_t handles_cb
);

/**
 * Remove a service created with custom_ble_add_service.
 *
 * The specified service needs to be the last added service. This means that you
 * need to remove several services in the reverse order that how they were
 * added.
 *
 * Note: You should only call this function from a single thread.
 *
 * @param service_handle The service to remove. This should be a service handle
 * acquired through the handles callback function given to
 * custom_ble_add_service.
 * @return
 * - CUSTOM_BLE_OK:               The operation was successfull.
 * - CUSTOM_BLE_INVALID_HANDLE:   The given handle did not represent any
 *   existing service.
 * - CUSTOM_BLE_SERVICE_NOT_LAST: The given service was not most recently added
 *   service in the list of currently active services.
 * - CUSTOM_BLE_NOT_STARTED:      The ble service has not been started yet.
 * - CUSTOM_BLE_ESP_ERROR:        An error was generated when trying to remove
 *   the service using the ESP BLE APIs for an unknown reason. The server
 *   might be left in an invalid state as a result of this.
 * - CUSTOM_BLE_INTERNAL_ERROR:   The internal list of attributes was out of
 *   order for an unknown reason. This shouldn't ever happen and the server
 *   is most likely in an invalid state.
 */
custom_ble_result_t custom_ble_remove_service(uint16_t service_handle);

/**
 * Get the current value of a characteristic or descriptor.
 *
 * Note: unsure if this works with descriptors...
 *
 *
 * @param attr_handle The characteristic or descriptor handle. This should be a
 * handle acquired through the handles callback function given to
 * custom_ble_add_service.
 * @param length Will be set to the length in bytes of the current value.
 * @param value Will be set to a pointer to the current value. TODO: Unsure how
 * long this pointer will live...
 * @return
 * - CUSTOM_BLE_OK:             The operation was successfull.
 * - CUSTOM_BLE_INVALID_HANDLE: The given characteristic or descriptor did not
 *      exist.
 * - CUSTOM_BLE_ESP_ERROR:      Some error was generated for an unknown reason
 *      by a call to the underlying ESP APIs.
 */
custom_ble_result_t custom_ble_get_attr_value(
	uint16_t attr_handle, uint16_t *length, const uint8_t **value
);

/**
 * Set the value of a characteristic or descriptor.
 *
 *
 * Calling this function automatically sends notifications and/or
 * indications if required.
 *
 * Note: unsure if this works with descriptors...
 * Note: You should only call this function from a single thread.
 *
 * @param attr_handle The characteristic or descriptor handle. This should be a
 * handle acquired through the handles callback function given to
 * custom_ble_add_service.
 * @param length The length of the value.
 * @param value The value that will be set as the current value. Does not need
 * to live longer than this function call (I think).
 * @return Sorry, this one won't tell you if the handle wasn't valid... ._.
 * - CUSTOM_BLE_OK:             The operation was successfull.
 * - CUSTOM_BLE_INVALID_HANDLE: The provided handle didn't exist.
 * - CUSTOM_BLE_ESP_ERROR:      Some error was generated for an unknown reason
 *   sohent by a call to the underlying ESP APIs.
 */
custom_ble_result_t custom_ble_set_attr_value(
	uint16_t attr_handle, uint16_t length, const uint8_t value[length]
);

/**
 * Get the amount of active services.
 *
 * If an error occurs, 0 is returned.
 */
uint16_t custom_ble_service_count();

/**
 * Get a list of currently active services.
 *
 * The handles are ordered in the order they were created in, starting with the
 * earliest added one. So the last element (granted that all handles fit in your
 * buffer) is the one which you're allowed to remove.
 *
 * This will return an empty list when querying the service handles would be
 * invalid (such as before starting the BLE server).
 *
 * @param capacity How many handles can fit in your buffer. At most this many
 * handles will be read. The current amount of handles can be queried with
 * custom_ble_service_count.
 * @param service_handles The list of handles.
 * @return The amount of handles written.
 */
uint16_t custom_ble_get_services(
	uint16_t capacity, uint16_t service_handles[capacity]
);

/**
 * Get the amount of characteristic and descriptors for a given service.
 *
 * @return The amount of characteristic and descriptors that belong to the given
 * service, or -1 if an error occurs.
 */
int16_t custom_ble_attr_count(uint16_t service_handle);

/**
 * Get a list of a service's characteristic and descriptor handles.
 *
 * The handles are ordered in the order they were created, starting with the
 * earliest added one.
 *
 * This will return an empty list when querying the service handles would be
 * invalid (such as before starting the BLE server).
 *
 * @param service_handle The service whose handles to query.
 * @param capacity How many handles can fit in your buffer. At most this many
 * handles will be read. The actual amount of handles can be queried with
 * custom_ble_attr_count.
 * @param service_handles The list of handles.
 * @param written_count Will be set to the amount of handles written on success.
 * @return
 * - CUSTOM_BLE_OK: The handles were successfully written to service_handles.
 * - CUSTOM_BLE_NOT_STARTED
 * - CUSTOM_BLE_INVALID_HANDLE: The specified service did not exist.
 *
 */
custom_ble_result_t custom_ble_get_attrs(
	uint16_t service_handle, uint16_t capacity,
	uint16_t service_handles[capacity], uint16_t *written_count
);

/**
 * Start the BLE server.
 *
 * Note: custom_ble_init has to have been called at some point before this.
 * Note: You should only call this function from a single thread.
 *
 * @return
 * - CUSTOM_BLE_OK:              on success
 * - CUSTOM_BLE_ALREADY_STARTED: The BLE server has already been started
 *   previously.
 * - CUSTOM_BLE_INIT_FAILED:     This is returned if custom_ble_init failed.
 *   This is typically due to memory allocation failing.
 */
custom_ble_result_t custom_ble_start();

bool custom_ble_started();

void custom_ble_init();

extern esp_ble_adv_params_t ble_adv_params;

#endif /* MAIN_BLE_CUSTOM_BLE_H_ */