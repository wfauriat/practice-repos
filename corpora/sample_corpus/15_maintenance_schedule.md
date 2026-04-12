# Maintenance Schedule and Procedures

## Overview

Regular maintenance ensures Meridian sensors continue to operate within published specifications. This document provides recommended maintenance intervals and procedures for each sensor model.

## Maintenance Matrix

| Task | MI-T100 | MI-T200 | MI-H300 | MI-P400 | MI-AQ500 | Interval |
|------|---------|---------|---------|---------|----------|----------|
| Visual inspection | Yes | Yes | Yes | Yes | Yes | 3 months |
| Cable/connector check | Yes | Yes | Yes | Yes | Yes | 6 months |
| Calibration | Yes | Yes | Yes | Yes | Yes (CO2/VOC) | See below |
| Filter replacement | — | — | Yes (PTFE cap) | — | Yes (PM intake) | 12 months |
| Firmware update check | Yes | Yes | Yes | Yes | Yes | 6 months |
| PM sensor replacement | — | — | — | — | Yes | 24 months |
| VOC element replacement | — | — | — | — | Yes | 36 months |
| Battery replacement (if applicable) | — | — | — | — | Yes (RTC battery) | 60 months |

## Calibration Intervals

| Sensor | Parameter | Interval | Method |
|--------|-----------|----------|--------|
| MI-T100 | Temperature | 12 months | 2-point field calibration |
| MI-T200 | Temperature (per channel) | 12 months | 2-point field calibration |
| MI-H300 | Humidity | 24 months | 2-point salt solution |
| MI-P400 | Barometric pressure | 18 months | 1-point reference comparison |
| MI-P400 | Differential pressure | 18 months | Zero-point check |
| MI-AQ500 | CO2 | 12 months | 2-point (ambient + span gas) |
| MI-AQ500 | VOC | 12 months | 1-point (clean air zero) |
| MI-AQ500 | PM | Not field-calibrable | Factory or module replacement |
| MI-AQ500 | Temperature | 24 months | 2-point field calibration |
| MI-AQ500 | Humidity | 24 months | 2-point salt solution |

## Visual Inspection Procedure (All Sensors)

Perform every 3 months:

1. Check the sensor housing for cracks, corrosion, or physical damage.
2. Inspect cable entry points for fraying, moisture ingress, or rodent damage.
3. Verify that mounting hardware is secure and vibration has not loosened fasteners.
4. Check the power LED: green = normal, red = fault, off = no power.
5. For MI-H300: inspect the PTFE filter cap for discoloration or blockage.
6. For MI-AQ500: inspect the air intake vents for dust buildup. Clean with compressed air if needed.
7. Record findings in the maintenance log.

## Filter and Consumable Replacement

### MI-H300 PTFE Filter Cap

- **Interval**: 12 months, or sooner if visibly discolored or clogged
- **Part number**: MI-H300-FC-5 (pack of 5, $12 USD)
- **Procedure**: Unscrew the old cap counterclockwise. Screw on the new cap finger-tight. Do not overtighten.

### MI-AQ500 PM Sensor Module

- **Interval**: 24 months (the laser diode degrades over time, reducing accuracy)
- **Part number**: MI-AQ500-PM (single module, $89 USD)
- **Procedure**:
  1. Power off the MI-AQ500.
  2. Remove the 4× Phillips screws on the bottom panel.
  3. Disconnect the PM module ribbon cable (ZIF connector — lift the latch, do not pull the cable).
  4. Slide out the old module and insert the new one.
  5. Reconnect the ribbon cable and secure the latch.
  6. Replace the bottom panel and power on. The sensor auto-detects the new module.

### MI-AQ500 VOC Sensor Element

- **Interval**: 36 months
- **Part number**: MI-AQ500-VOC ($49 USD)
- **Procedure**: Same as PM module replacement but located in the upper sensor bay. After replacement, a 48-hour burn-in period is required (the sensor displays "VOC BURN-IN" during this period and readings are unreliable).

### MI-AQ500 RTC Battery

- **Interval**: 60 months
- **Battery type**: CR2032 3V lithium coin cell
- **Procedure**: The battery holder is accessible by removing the bottom panel. Replace and verify the clock is set correctly in MeridianLink.

## Spare Parts Inventory Recommendation

For installations with more than 20 sensors, Meridian recommends maintaining the following spare parts inventory:

| Part | Quantity |
|------|----------|
| MI-T100 complete sensor | 2 |
| MI-T200 probe (spare) | 4 |
| MI-H300 PTFE filter cap pack | 2 |
| MI-AQ500 PM module | 2 |
| MI-AQ500 VOC element | 1 |
| RS-485 cable (50m spool) | 1 |
| 120Ω termination resistor (pack of 10) | 1 |
| MI-USB-485 adapter | 1 |

## Maintenance Log

All maintenance activities should be recorded in MeridianLink under **Assets > Maintenance Log**. Each entry should include:
- Date and time
- Sensor serial number
- Activity performed
- Technician name
- Next scheduled maintenance date
- Notes (any anomalies observed)

MeridianLink can send automated maintenance reminders via email based on the configured intervals.
