# Troubleshooting Guide

## Sensor Not Detected by MeridianLink

### Symptoms
MeridianLink's "Discover Sensors" scan completes but the sensor does not appear.

### Checklist

1. **Verify power**: Check that the sensor's power LED is lit (green = OK, red = fault, off = no power).
2. **Check wiring**: Verify A-to-A, B-to-B, and GND-to-GND connections. Reversed A/B is the most common wiring mistake.
3. **Address conflict**: Two sensors sharing the same RS-485 address will cause bus contention. Disconnect all sensors except the missing one and retry. Use DIP switches to assign a unique address.
4. **Baud rate mismatch**: Ensure MeridianLink's configured baud rate matches the sensor's DIP switch setting. The factory default is 9600 baud.
5. **Termination**: If the sensor is at the end of the bus, ensure the TERM DIP switch is ON. If it's in the middle, ensure TERM is OFF.
6. **Cable length**: RS-485 bus length must not exceed 1200m at 9600 baud or 300m at 115200 baud.
7. **USB adapter**: Try a different RS-485 USB adapter. Some adapters have insufficient drive strength for buses with more than 8 sensors. The Meridian-recommended adapter is the MI-USB-485 ($49 USD).

## Inaccurate Temperature Readings (MI-T100 / MI-T200)

### Symptoms
Temperature readings are consistently offset from a known reference.

### Solutions

1. **Self-heating**: The sensor's internal electronics generate heat. At very low airflow, self-heating can add 0.1–0.3°C. Increase airflow or reduce sampling rate.
2. **Calibration drift**: Check the calibration date in MeridianLink (Sensor > Info > Last Calibration). If more than 12 months old, recalibrate.
3. **Thermal bridging**: If the probe is not inserted deep enough, heat conducts along the probe stem. Ensure minimum 50mm insertion depth past the measurement point.
4. **Electrical noise**: High-current equipment nearby can induce noise. Use shielded cable and verify shield grounding.

## Humidity Drift (MI-H300)

### Symptoms
Humidity readings slowly drift upward over weeks/months.

### Solutions

1. **Sensor saturation**: Prolonged exposure to >95% RH causes temporary upward drift. Move the sensor to a 50% RH environment for 48 hours to recover.
2. **Contaminated filter cap**: The PTFE filter cap can clog with dust or chemical residue. Replace the filter cap ($12 for a 5-pack).
3. **Chemical damage**: If exposed to solvents, ammonia, or chlorine, the sensing element may be permanently damaged. Replace the sensor or return for factory refurbishment ($89 service fee).
4. **Recalibration**: Use the MI-CAL-H kit to perform a 2-point humidity calibration.

## MI-AQ500 Wi-Fi Connectivity Issues

### Symptoms
The MI-AQ500 disconnects from Wi-Fi frequently, or fails to connect after provisioning.

### Solutions

1. **Signal strength**: Check the Wi-Fi signal strength on the sensor's LCD (Settings > Network > Wi-Fi Status). Signal must be above -70 dBm for reliable operation. Below -80 dBm, the sensor falls back to RS-485.
2. **2.4 GHz only**: The MI-AQ500 does not support 5 GHz Wi-Fi. Ensure the target network operates on 2.4 GHz.
3. **Captive portal**: Enterprise networks with captive portals are not supported. Use WPA2-PSK or WPA2-Enterprise (EAP-TLS).
4. **Channel congestion**: In dense Wi-Fi environments, try setting the router to a fixed channel (1, 6, or 11) rather than auto.
5. **Firmware update**: Wi-Fi stability was improved significantly in firmware 2.4.0. Check the current version (Settings > About) and update if older.

## CO2 Readings Stuck at 400 ppm (MI-AQ500)

### Symptoms
The CO2 reading permanently shows ~400 ppm regardless of actual levels.

### Cause
This typically indicates the ABC (Automatic Baseline Correction) has incorrectly calibrated to an indoor baseline. This happens when the sensor is in a space that never reaches outdoor ambient levels.

### Solution
1. Disable ABC in MeridianLink (Sensor > Configuration > CO2 > Automatic Baseline Correction = OFF).
2. Perform a manual CO2 calibration using a known reference gas (e.g., outdoor air at ~420 ppm or a 1000 ppm span gas).
3. If the sensor has been running with incorrect ABC for more than 30 days, a factory reset is recommended (Sensor > Advanced > Factory Reset).

## Data Gaps in MeridianLink

### Symptoms
Gaps appear in the sensor data timeline.

### Common Causes

1. **Sensor in sleep mode**: If the sampling rate is set to a long interval (e.g., 1 sample/hour), gaps between readings are expected.
2. **Communication loss**: Check the RS-485 bus for loose connections, damaged cable, or electromagnetic interference.
3. **MeridianLink server restart**: Data is not collected during server downtime. The sensor's internal data log continues recording. After reconnection, MeridianLink syncs the backlog (up to the sensor's flash capacity).
4. **Full data log**: If the sensor's internal flash is full, old data is overwritten in a circular buffer. Increase the sync frequency or upgrade to a sensor with more flash (MI-T200 has 4 MB vs. MI-T100's 512 KB).
5. **PostgreSQL disk full**: Check disk usage on the MeridianLink server. When the database disk is full, new readings are dropped. MeridianLink shows a warning banner in this state.

## Firmware Update Failures

### Symptoms
Firmware update via MeridianLink fails partway through.

### Solutions

1. **Do not power off** the sensor during a firmware update. If interrupted, the sensor enters recovery mode (all LEDs blink rapidly). In recovery mode, retry the update.
2. **Bus traffic**: Other sensors on the same RS-485 bus can interfere with firmware updates. Pause monitoring of other sensors during the update, or update via USB (MI-T200 and MI-AQ500 only).
3. **Firmware file corrupt**: Re-download the firmware from meridianinstruments.com/firmware. Verify the SHA-256 checksum.
4. **Recovery mode stuck**: If the sensor remains in recovery mode after 3 failed update attempts, contact Meridian support. A JTAG recovery may be required (covered under warranty).
