# Startup Torque on Sensorless BLDC Motors

**Date**: August 2014  
**Author**: Benjamin Vedder  
**Source**: http://vedder.se/2014/08/startup-torque-on-sensorless-bldc-motors/

## Key Techniques for Smooth Startup

Benjamin describes several innovative techniques for achieving smooth startup and low-speed performance with sensorless BLDC motors:

1. **No Hardware Low-Pass Filters**
   - ADC samples synchronized to PWM timer
   - Dynamically adjusted for changing duty cycle and switching frequency

2. **Back-EMF Integration**
   - Integrate area under voltage after zero crossing
   - Use motor-specific threshold for commutation
   - Robust against acceleration
   - Provides good signal-to-noise ratio

3. **Voltage Coupling Compensation**
   - Parameter defines voltage coupling between windings
   - Critical for low-speed, low duty cycle performance
   - Compensates for RPM-dependent variations

4. **Adaptive Switching Frequency**
   - Proportional to duty cycle
   - Allows better back-EMF sampling at low speeds
   - Reduces switching losses

5. **Motor State Tracking**
   - Analyze back-EMF on all phases when motor is un-driven
   - Determine motor position, direction, and speed
   - Enable closed-loop operation from first commutation

## Performance Demonstrations

The author demonstrated these techniques on:
- Electric longboard
- 700W hub motor on electric bicycle
- Scorpion outrunner motor

### Key Observations
- Smooth startup even at 5% duty cycle
- Clean voltage and current waveforms
- Robust handling of unusual startup conditions
- Ability to restart after power interruption

## Practical Insights

The implementation shows that with careful algorithmic design, sensorless BLDC motors can achieve excellent startup performance without requiring Hall effect sensors.