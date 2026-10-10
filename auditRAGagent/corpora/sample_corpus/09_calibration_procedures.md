# Calibration Procedures

## Overview

All Meridian sensors are factory calibrated with NIST-traceable reference standards before shipment. Field recalibration is recommended at regular intervals to maintain accuracy within published specifications.

## Recalibration Intervals

| Sensor | Interval | Method |
|--------|----------|--------|
| MI-T100 | 12 months | 2-point (ice + boiling) |
| MI-T200 | 12 months | 2-point per channel |
| MI-H300 | 24 months | 2-point (33% + 75% RH salt solutions) |
| MI-P400 | 18 months | 1-point barometric (reference barometer) |
| MI-AQ500 CO2 | 12 months | 2-point (ambient + 1000 ppm span gas) |
| MI-AQ500 VOC | 12 months | 1-point (clean air zero) |
| MI-AQ500 PM | Not field-calibrable | Return to factory or replace module |

## Temperature Sensor Calibration (MI-T100 / MI-T200)

### Equipment Needed

- Ice bath (0°C reference): crushed ice made from distilled water, packed in a Dewar flask
- Boiling water bath (100°C reference at sea level — adjust for altitude)
- MeridianLink Desktop or Server (v2.0+)
- RS-485 connection to sensor

### Procedure

1. Connect the sensor to MeridianLink and navigate to **Sensor > Calibration**.
2. Click **Start Calibration** — the sensor enters calibration mode (sampling rate increases to 1/sec).
3. **Low point**: Immerse the probe in the ice bath. Wait for the reading to stabilize (±0.1°C for 60 seconds). Click **Capture Low Point**. MeridianLink records the raw ADC value and reference temperature (0.0°C).
4. **High point**: Transfer the probe to the boiling water bath. Wait for stabilization. Click **Capture High Point**. Enter the actual boiling point for your altitude (e.g., 95.0°C at 1650m elevation in Boulder, CO).
5. Click **Apply Calibration**. MeridianLink computes the linear correction coefficients and writes them to the sensor's EEPROM.
6. Verify: return the probe to the ice bath and confirm the reading is 0.0°C ± 0.2°C.

### For MI-T200 Multi-Point

Repeat the above procedure for each channel. Channels can be calibrated independently — you do not need to calibrate all 8 at once.

## Humidity Sensor Calibration (MI-H300)

### Equipment Needed

- MI-CAL-H calibration kit (includes two sealed chambers with saturated salt solutions: MgCl₂ at 33.0% RH and NaCl at 75.3% RH)
- MeridianLink Desktop or Server
- Stable environment: 22–28°C, no drafts

### Procedure

1. Allow the MI-CAL-H chambers to equilibrate at room temperature for at least 2 hours before use.
2. Connect the sensor to MeridianLink and navigate to **Sensor > Calibration**.
3. **Low point (33% RH)**: Place the sensor in the MgCl₂ chamber. Seal. Wait 30 minutes for equilibrium. Click **Capture Low Point**. Reference: 33.0% RH.
4. **High point (75% RH)**: Move the sensor to the NaCl chamber. Wait 30 minutes. Click **Capture High Point**. Reference: 75.3% RH.
5. Click **Apply Calibration**.
6. The salt solutions in the MI-CAL-H kit last approximately 50 calibration cycles. Replace the kit when the indicator strip turns from blue to white.

## Pressure Sensor Calibration (MI-P400)

### Equipment Needed

- Reference barometer with accuracy ±0.1 hPa (e.g., Vaisala PTB330)
- MeridianLink Desktop or Server

### Procedure

1. Place the MI-P400 and reference barometer side by side at the same elevation. Wait 10 minutes.
2. In MeridianLink, navigate to **Sensor > Calibration > Barometric Offset**.
3. Enter the reference barometer reading. MeridianLink computes and applies the offset.
4. For differential pressure: both ports must be open to the same ambient pressure. Click **Zero Differential**. The sensor stores the zero offset.

## Calibration Certificates

After each calibration (factory or field), MeridianLink generates a calibration certificate in PDF format containing:
- Sensor serial number and model
- Calibration date and technician name
- Reference standards used
- Pre-calibration and post-calibration readings
- Pass/fail status (based on ±2× published accuracy)
- Next recommended calibration date
