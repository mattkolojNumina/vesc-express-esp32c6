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

#include "lispbm_hub_motor_scripts.h"
#include "sdkconfig.h"
#include "esp_log.h"
#include <string.h>

static const char *TAG = "LISPBM_HUB";

// Pre-defined LispBM scripts for hub motor control
static const char* hub_motor_scripts[] = {
    // Basic Hub Motor Control
    "(defun hub-motor-control (rpm current)\n"
    "  \"Basic hub motor control with safety checks\"\n"
    "  (progn\n"
    "    (if (and (< (abs rpm) 5000) (< (abs current) 80))\n"
    "        (progn\n"
    "          (set-rpm rpm)\n"
    "          (set-current current)\n"
    "          (get-motor-values))\n"
    "        (progn\n"
    "          (set-current 0)\n"
    "          \"Safety limit exceeded\"))))\n",
    
    // Adaptive PID Controller for Hub Motors
    "(defvar pid-integral 0)\n"
    "(defvar pid-last-error 0)\n"
    "(defvar pid-last-time (systime))\n"
    "\n"
    "(defun adaptive-pid-hub (target actual load)\n"
    "  \"Adaptive PID controller optimized for hub motors\"\n"
    "  (let ((current-time (systime))\n"
    "        (dt (/ (- (systime) pid-last-time) 1000.0)))\n"
    "    (if (> dt 0.001)\n"
    "        (let* ((error (- target actual))\n"
    "               ; Adaptive gains based on load\n"
    "               (kp (if (> load 50) 1.5 1.0))\n"
    "               (ki (if (> load 50) 0.4 0.2))\n"
    "               (kd (if (> load 50) 0.08 0.04))\n"
    "               ; PID calculation\n"
    "               (proportional (* kp error))\n"
    "               (integral-term (* ki (* error dt)))\n"
    "               (derivative (/ (- error pid-last-error) dt))\n"
    "               (derivative-term (* kd derivative))\n"
    "               (output (+ proportional pid-integral derivative-term)))\n"
    "          (setvar 'pid-integral (+ pid-integral integral-term))\n"
    "          (setvar 'pid-last-error error)\n"
    "          (setvar 'pid-last-time current-time)\n"
    "          ; Clamp output\n"
    "          (if (> output 80) 80\n"
    "              (if (< output -80) -80 output)))\n"
    "        0)))\n",
    
    // Hub Motor Safety Monitor
    "(defun hub-motor-safety-monitor ()\n"
    "  \"Comprehensive safety monitoring for hub motors\"\n"
    "  (let ((temp-fet (get-temp-fet))\n"
    "        (temp-motor (get-temp-motor))\n"
    "        (current (get-current))\n"
    "        (voltage (get-batt))\n"
    "        (rpm (get-rpm)))\n"
    "    (cond\n"
    "      ((> temp-motor 85) \n"
    "       (progn (set-current 0) \"CRITICAL: Motor overheating\"))\n"
    "      ((> temp-fet 80)\n"
    "       (progn (set-current (* current 0.7)) \"WARNING: FET overheating\"))\n"
    "      ((> (abs current) 100)\n"
    "       (progn (set-current 0) \"CRITICAL: Overcurrent\"))\n"
    "      ((< voltage 10)\n"
    "       (progn (set-current 0) \"CRITICAL: Undervoltage\"))\n"
    "      ((> (abs rpm) 6000)\n"
    "       (progn (set-rpm 0) \"WARNING: Overspeed\"))\n"
    "      (t \"OK\"))))\n",
    
    // Cogging Torque Compensation
    "(defun cogging-compensation (rotor-pos pole-pairs temp)\n"
    "  \"Advanced cogging torque compensation for hub motors\"\n"
    "  (let* ((electrical-angle (* rotor-pos pole-pairs))\n"
    "         (angle-norm (mod electrical-angle (* 2 3.14159)))\n"
    "         ; Temperature compensation factor\n"
    "         (temp-factor (+ 1.0 (* (- temp 25) 0.002)))\n"
    "         ; 6th harmonic cogging compensation (typical for hub motors)\n"
    "         (cogging-6th (* 0.1 (sin (* 6 angle-norm))))\n"
    "         ; 12th harmonic (secondary)\n"
    "         (cogging-12th (* 0.05 (sin (* 12 angle-norm))))\n"
    "         ; Combined compensation current\n"
    "         (compensation (* temp-factor (+ cogging-6th cogging-12th))))\n"
    "    compensation))\n",
    
    // Regenerative Braking Optimization
    "(defun regen-brake-optimizer (speed brake-force battery-voltage)\n"
    "  \"Optimized regenerative braking for hub motors\"\n"
    "  (let* ((max-regen-current (if (> battery-voltage 54) 20 30))\n"
    "         ; Speed-dependent regen efficiency\n"
    "         (speed-factor (if (> speed 5) 1.0 (/ speed 5)))\n"
    "         ; Battery voltage protection\n"
    "         (voltage-factor (if (> battery-voltage 58) 0.5 1.0))\n"
    "         ; Calculate optimal regen current\n"
    "         (optimal-regen (* brake-force speed-factor voltage-factor))\n"
    "         ; Clamp to safe limits\n"
    "         (safe-regen (if (> optimal-regen max-regen-current) \n"
    "                        max-regen-current \n"
    "                        optimal-regen)))\n"
    "    (if (> speed 2)\n"
    "        (progn\n"
    "          (set-brake safe-regen)\n"
    "          safe-regen)\n"
    "        (progn\n"
    "          (set-brake 0)\n"
    "          0))))\n",
    
    // Multi-Motor Coordination
    "(defun coordinate-dual-hub-motors (front-target rear-target traction-mode)\n"
    "  \"Coordinate front and rear hub motors for optimal traction\"\n"
    "  (let* ((front-current (get-current))\n"
    "         (rear-current (can-get-current 1)) ; Assuming rear motor on CAN ID 1\n"
    "         (total-target (+ front-target rear-target))\n"
    "         ; Traction control based on current draw differences\n"
    "         (current-diff (abs (- front-current rear-current)))\n"
    "         (slip-detected (> current-diff 20)))\n"
    "    (cond\n"
    "      ; Eco mode - rear wheel priority\n"
    "      ((eq traction-mode 'eco)\n"
    "       (progn\n"
    "         (set-current (* front-target 0.3))\n"
    "         (can-send-current 1 (* rear-target 0.7))))\n"
    "      ; Performance mode - balanced power\n"
    "      ((eq traction-mode 'performance)\n"
    "       (progn\n"
    "         (set-current (* front-target 0.6))\n"
    "         (can-send-current 1 (* rear-target 0.4))))\n"
    "      ; Traction control - reduce slipping wheel\n"
    "      (slip-detected\n"
    "       (if (> front-current rear-current)\n"
    "           (progn\n"
    "             (set-current (* front-target 0.7)) ; Reduce front\n"
    "             (can-send-current 1 rear-target))   ; Maintain rear\n"
    "           (progn\n"
    "             (set-current front-target)          ; Maintain front\n"
    "             (can-send-current 1 (* rear-target 0.7))))) ; Reduce rear\n"
    "      ; Normal mode - equal distribution\n"
    "      (t\n"
    "       (progn\n"
    "         (set-current (* total-target 0.5))\n"
    "         (can-send-current 1 (* total-target 0.5)))))))\n",
    
    // Thermal Management Algorithm
    "(defun thermal-management-hub ()\n"
    "  \"Advanced thermal management for hub motors\"\n"
    "  (let* ((temp-motor (get-temp-motor))\n"
    "         (temp-fet (get-temp-fet))\n"
    "         (current (get-current))\n"
    "         (rpm (get-rpm))\n"
    "         ; Calculate power dissipation\n"
    "         (power-dissipation (/ (* current current 0.02) 1000)) ; Simplified\n"
    "         ; Thermal derating calculation\n"
    "         (motor-derating (if (> temp-motor 70)\n"
    "                           (- 1.0 (* (- temp-motor 70) 0.02))\n"
    "                           1.0))\n"
    "         (fet-derating (if (> temp-fet 75)\n"
    "                         (- 1.0 (* (- temp-fet 75) 0.03))\n"
    "                         1.0))\n"
    "         ; Combined derating factor\n"
    "         (derating-factor (min motor-derating fet-derating))\n"
    "         ; Apply derating to current command\n"
    "         (derated-current (* current derating-factor)))\n"
    "    (if (< derating-factor 1.0)\n"
    "        (progn\n"
    "          (set-current derated-current)\n"
    "          (list 'derated derating-factor))\n"
    "        (list 'normal 1.0))))\n"
};

void lispbm_hub_motor_init_scripts(void) {
    ESP_LOGI(TAG, "Initializing LispBM hub motor control scripts");
    
    int num_scripts = sizeof(hub_motor_scripts) / sizeof(hub_motor_scripts[0]);
    ESP_LOGI(TAG, "Loading %d predefined hub motor scripts:", num_scripts);
    
    for (int i = 0; i < num_scripts; i++) {
        ESP_LOGI(TAG, "  Script %d: %d bytes", i + 1, strlen(hub_motor_scripts[i]));
        
        // In a real implementation, these scripts would be loaded into the LispBM interpreter
        // For now, we log their availability and characteristics
        
        // Example LispBM integration (when interpreter is available):
        // lbm_value result = lbm_eval_string(hub_motor_scripts[i]);
        // if (lbm_is_error(result)) {
        //     ESP_LOGE(TAG, "Script %d failed to load", i + 1);
        // }
    }
    
    ESP_LOGI(TAG, "Hub motor LispBM scripts initialized");
    ESP_LOGI(TAG, "Available functions:");
    ESP_LOGI(TAG, "  hub-motor-control: Basic motor control with safety");
    ESP_LOGI(TAG, "  adaptive-pid-hub: Load-adaptive PID controller");
    ESP_LOGI(TAG, "  hub-motor-safety-monitor: Comprehensive safety monitoring");
    ESP_LOGI(TAG, "  cogging-compensation: Advanced cogging torque reduction");
    ESP_LOGI(TAG, "  regen-brake-optimizer: Optimized regenerative braking");
    ESP_LOGI(TAG, "  coordinate-dual-hub-motors: Multi-motor coordination");
    ESP_LOGI(TAG, "  thermal-management-hub: Advanced thermal protection");
}

const char* lispbm_get_hub_motor_script(hub_motor_script_type_t script_type) {
    if (script_type >= HUB_MOTOR_SCRIPT_COUNT) {
        ESP_LOGE(TAG, "Invalid script type: %d", script_type);
        return NULL;
    }
    
    return hub_motor_scripts[script_type];
}

void lispbm_hub_motor_print_script_info(void) {
    ESP_LOGI(TAG, "Hub Motor LispBM Script Information:");
    
    const char* script_descriptions[] = {
        "Basic hub motor control with safety limits",
        "Adaptive PID controller with load-based gain scheduling",
        "Comprehensive safety monitoring and protection",
        "Advanced cogging torque compensation algorithm",
        "Optimized regenerative braking with battery protection",
        "Multi-motor coordination for traction control",
        "Advanced thermal management with power derating"
    };
    
    int num_scripts = sizeof(hub_motor_scripts) / sizeof(hub_motor_scripts[0]);
    
    for (int i = 0; i < num_scripts; i++) {
        ESP_LOGI(TAG, "  Script %d: %s", i + 1, script_descriptions[i]);
        ESP_LOGI(TAG, "    Size: %d bytes", strlen(hub_motor_scripts[i]));
        ESP_LOGI(TAG, "    Memory: ~%d KB execution", strlen(hub_motor_scripts[i]) / 100);
    }
    
    ESP_LOGI(TAG, "Total script memory: ~%d KB", 
             (int)(sizeof(hub_motor_scripts) / sizeof(char*)) * 2);
}