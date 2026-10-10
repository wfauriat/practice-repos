# Installation Guide

## Overview

This guide covers the physical installation of Meridian sensors and their connection to the MeridianLink software platform. For software installation, see the MeridianLink Platform documentation.

## RS-485 Bus Wiring

All Meridian sensors (except the MI-AQ500 in Wi-Fi mode) communicate over an RS-485 multi-drop bus.

### Cable Specifications

- **Type**: Shielded twisted pair (STP), minimum 24 AWG
- **Recommended**: Belden 9841 or equivalent
- **Maximum bus length**: 1200 meters at 9600 baud, 300 meters at 115200 baud
- **Shield grounding**: ground the shield at one end only (typically at the MeridianLink host) to prevent ground loops

### Wiring Diagram

Each sensor has three RS-485 terminals:
- **A (−)**: Data negative (connect to A on all other devices)
- **B (+)**: Data positive (connect to B on all other devices)
- **GND**: Signal ground (connect to GND on all other devices)

Wire all sensors in a daisy-chain (bus) topology. **Do not use star topology** — it causes signal reflections.

### Bus Termination

Install a 120Ω termination resistor between A and B at **both ends** of the bus. Most Meridian sensors have a built-in switchable terminator — set the DIP switch labeled "TERM" to ON for the sensor at each end of the bus.

### Addressing

Each sensor must have a unique RS-485 address (1–247). The default address is 1. Change addresses using:
- The physical DIP switches on the sensor (addresses 1–15)
- MeridianLink software (addresses 1–247)

## Power Supply

### Voltage Requirements

| Sensor | Voltage Range | Typical Current |
|--------|--------------|-----------------|
| MI-T100 | 3.3V – 5.5V DC | 14 mA at 5V |
| MI-T200 | 5V – 24V DC | 25 mA at 12V |
| MI-H300 | 3.3V – 5.5V DC | 17 mA at 5V |
| MI-P400 | 5V – 24V DC | 18 mA at 12V |
| MI-AQ500 | 5V (USB-C) or 12–24V DC | 170 mA at 5V |

### Power Over Bus

For installations with fewer than 8 sensors and total cable length under 100 meters, sensors can be powered over the RS-485 bus using the Meridian MI-POB-8 power injector ($149 USD). The MI-POB-8 provides 5V at up to 2A across 8 ports.

## Sensor Mounting

### MI-T100 / MI-T200 Probes

- Use the provided stainless steel mounting bracket and M4 screws
- Insertion probes: drill a pilot hole, insert the probe, and secure with the compression fitting
- Minimum insertion depth: 50mm beyond the point of measurement
- For liquid immersion: use the MI-T100-W waterproof variant only
- Avoid mounting near heat sources, direct sunlight, or air conditioning vents (unless measuring those specifically)

### MI-H300

- Mount at 1.5m height on an interior wall for room-level measurements
- Keep at least 30cm from exterior walls, windows, and doors
- The PTFE filter cap must face downward to prevent moisture accumulation
- Do not mount in direct airflow from HVAC diffusers

### MI-P400

- Mount on a stable, vibration-free surface
- For differential measurements: route tubing from each pressure port to the respective measurement zone. Keep tubing lengths equal (±10%) to avoid lag differences.
- Avoid sharp bends in tubing (minimum bend radius: 25mm)

### MI-AQ500

- Mount at 1.2m to 1.5m height (breathing zone)
- Minimum 1m from walls, windows, and doors
- Do not mount in direct sunlight — LCD display may overheat above 45°C
- Ensure the air intake vents on the sides are unobstructed (minimum 5cm clearance)

## First-Time Setup

1. Wire all sensors to the RS-485 bus and apply power.
2. Connect the RS-485 USB adapter to the MeridianLink host computer.
3. Launch MeridianLink and click **Discover Sensors** on the dashboard.
4. MeridianLink scans addresses 1–247 at the configured baud rate. Discovered sensors appear in the sensor list.
5. For each sensor, set a descriptive name, location, and desired sampling rate.
6. Click **Start Monitoring** to begin data collection.
