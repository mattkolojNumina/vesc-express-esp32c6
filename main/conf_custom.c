/*
	Copyright 2022 Benjamin Vedder	benjamin@vedder.se
	Copyright 2025 VESC Express Compatibility Layer

	This file is part of the VESC Express firmware.

	The VESC Express firmware is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    The VESC Express firmware is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
 */

#include "conf_custom.h"
#include "datatypes.h"
#include "packet.h"
#include "mempools.h"
#include "buffer.h"
#include "main.h"
#include "confparser.h"
#include "comm_can.h"
#include "commands.h"

#include <string.h>

// Function pointers - VESC Controller compatible
static int (*m_get_cfg)(uint8_t *data, bool is_default) = 0;
static bool (*m_set_cfg)(uint8_t *data) = 0;
static int (*m_get_cfg_xml)(uint8_t **data) = 0;

// VESC Express compatibility functions
static int vesc_express_get_cfg(uint8_t *data, bool is_default);
static bool vesc_express_set_cfg(uint8_t *data);
static int vesc_express_get_cfg_xml(uint8_t **data);

// Simple function validation helper (replaces utils_is_func_valid)
static bool is_func_valid(void *func) {
	return func != NULL;
}

// Static XML configuration data
static const char* vesc_express_xml = 
"<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n"
"<config>\n"
"  <param name=\"controller_id\" type=\"int16\" min=\"0\" max=\"254\" default=\"0\" />\n"
"  <param name=\"can_baud_rate\" type=\"uint8\" min=\"0\" max=\"8\" default=\"3\" />\n"
"  <param name=\"can_status_rate_hz\" type=\"int16\" min=\"1\" max=\"1000\" default=\"50\" />\n"
"  <param name=\"wifi_mode\" type=\"uint8\" min=\"0\" max=\"3\" default=\"3\" />\n"
"  <param name=\"wifi_sta_ssid\" type=\"string\" maxlen=\"64\" default=\"\" />\n"
"  <param name=\"wifi_sta_key\" type=\"string\" maxlen=\"64\" default=\"\" />\n"
"  <param name=\"wifi_ap_ssid\" type=\"string\" maxlen=\"64\" default=\"VESC Express\" />\n"
"  <param name=\"wifi_ap_key\" type=\"string\" maxlen=\"64\" default=\"\" />\n"
"  <param name=\"use_tcp_local\" type=\"bool\" default=\"true\" />\n"
"  <param name=\"use_tcp_hub\" type=\"bool\" default=\"false\" />\n"
"  <param name=\"tcp_hub_url\" type=\"string\" maxlen=\"256\" default=\"\" />\n"
"  <param name=\"tcp_hub_port\" type=\"int16\" min=\"1\" max=\"65535\" default=\"65102\" />\n"
"  <param name=\"tcp_hub_id\" type=\"string\" maxlen=\"64\" default=\"\" />\n"
"  <param name=\"tcp_hub_pass\" type=\"string\" maxlen=\"64\" default=\"\" />\n"
"  <param name=\"ble_name\" type=\"string\" maxlen=\"32\" default=\"VESC Express\" />\n"
"  <param name=\"ble_pin\" type=\"int32\" min=\"0\" max=\"999999\" default=\"123456\" />\n"
"</config>\n";

void conf_custom_add_config(
		int (*get_cfg)(uint8_t *data, bool is_default),
		bool (*set_cfg)(uint8_t *data),
		int (*get_cfg_xml)(uint8_t **data)) {

	if (get_cfg && set_cfg && get_cfg_xml) {
		m_get_cfg = get_cfg;
		m_set_cfg = set_cfg;
		m_get_cfg_xml = get_cfg_xml;
	}
}

void conf_custom_clear_configs(void) {
	m_get_cfg = 0;
	m_set_cfg = 0;
	m_get_cfg_xml = 0;
}

int conf_custom_cfg_num(void) {
	int res = 0;

	if (m_get_cfg_xml) {
		uint8_t *xml_data = 0;
		m_get_cfg_xml(&xml_data);

		if (is_func_valid(xml_data)) {
			res = 1;
		}
	} else {
		// VESC Express always has config available
		res = 1;
	}

	return res;
}

int conf_custom_get_cfg_xml(int conf_ind, uint8_t **data) {
	if (conf_ind != 0) {
		return 0;
	}

	if (m_get_cfg_xml) {
		return m_get_cfg_xml(data);
	} else {
		// Use default VESC Express XML
		return vesc_express_get_cfg_xml(data);
	}
}

void conf_custom_process_cmd(unsigned char *data, unsigned int len,
		void(*reply_func)(unsigned char *data, unsigned int len)) {
	COMM_PACKET_ID packet_id;

	packet_id = data[0];
	data++;
	len--;

	switch (packet_id) {

	case COMM_GET_CUSTOM_CONFIG:
	case COMM_GET_CUSTOM_CONFIG_DEFAULT: {
		int conf_ind = data[0];
		if ((m_get_cfg && conf_ind == 0) || conf_ind == 0) {
			uint8_t *send_buffer = mempools_get_packet_buffer();
			int32_t ind = 0;
			send_buffer[ind++] = packet_id;
			send_buffer[ind++] = conf_ind;
			
			int32_t len_cfg;
			if (m_get_cfg) {
				len_cfg = m_get_cfg(send_buffer + ind, packet_id == COMM_GET_CUSTOM_CONFIG_DEFAULT);
			} else {
				len_cfg = vesc_express_get_cfg(send_buffer + ind, packet_id == COMM_GET_CUSTOM_CONFIG_DEFAULT);
			}
			
			ind += len_cfg;
			reply_func(send_buffer, ind);
			mempools_free_packet_buffer(send_buffer);
		}
	} break;

	case COMM_SET_CUSTOM_CONFIG: {
		int conf_ind = data[0];
		if (conf_ind == 0) {
			bool success = false;
			if (m_set_cfg) {
				success = m_set_cfg(data + 1);
			} else {
				success = vesc_express_set_cfg(data + 1);
			}
			
			if (success) {
				int32_t ind = 0;
				uint8_t send_buffer[50];
				send_buffer[ind++] = packet_id;
				reply_func(send_buffer, ind);
			}
		}
	} break;

	case COMM_GET_CUSTOM_CONFIG_XML: {
		int32_t ind = 0;

		int conf_ind = data[ind++];

		if (conf_ind != 0) {
			break;
		}

		int32_t len_conf = buffer_get_int32(data, &ind);
		int32_t ofs_conf = buffer_get_int32(data, &ind);

		uint8_t *xml_data = 0;
		int xml_len;
		
		if (m_get_cfg_xml) {
			xml_len = m_get_cfg_xml(&xml_data);
		} else {
			xml_len = vesc_express_get_cfg_xml(&xml_data);
		}

		if ((len_conf + ofs_conf) > xml_len || len_conf > (PACKET_MAX_PL_LEN - 10)) {
			break;
		}

		uint8_t *send_buffer = mempools_get_packet_buffer();
		int32_t send_ind = 0;
		send_buffer[send_ind++] = packet_id;
		send_buffer[send_ind++] = conf_ind;
		buffer_append_int32(send_buffer, xml_len, &send_ind);
		buffer_append_int32(send_buffer, ofs_conf, &send_ind);
		memcpy(send_buffer + send_ind, xml_data + ofs_conf, len_conf);
		send_ind += len_conf;

		reply_func(send_buffer, send_ind);
		mempools_free_packet_buffer(send_buffer);
	} break;

	default:
		break;
	}
}

// VESC Express compatibility implementations
static int vesc_express_get_cfg(uint8_t *data, bool is_default) {
	main_config_t *conf = calloc(1, sizeof(main_config_t));
	
	if (is_default) {
		confparser_set_defaults_main_config_t(conf);
	} else {
		*conf = backup.config;
	}
	
	int32_t len = confparser_serialize_main_config_t(data, conf);
	free(conf);
	return len;
}

static bool vesc_express_set_cfg(uint8_t *data) {
	main_config_t *conf = calloc(1, sizeof(main_config_t));
	*conf = backup.config;

	bool success = confparser_deserialize_main_config_t(data, conf);
	if (success) {
		// Check if CAN baud rate changed to update CAN bus
		bool baud_changed = backup.config.can_baud_rate != conf->can_baud_rate;
		
		backup.config = *conf;
		
		if (baud_changed) {
			comm_can_update_baudrate(0);
		}
		
		main_store_backup_data();
	}
	
	free(conf);
	return success;
}

static int vesc_express_get_cfg_xml(uint8_t **data) {
	*data = (uint8_t*)vesc_express_xml;
	return strlen(vesc_express_xml);
}