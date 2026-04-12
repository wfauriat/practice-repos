# MI-P400 Barometric and Differential Pressure Sensor — Datasheet

## Overview

The MI-P400, launched in 2019, measures both absolute barometric pressure and differential pressure between two points. It is designed for cleanroom pressure monitoring, HVAC system balancing, altitude compensation, and weather station applications.

## Specifications

| Parameter | Value |
|-----------|-------|
| Barometric pressure range | 300 hPa to 1100 hPa |
| Barometric accuracy | ±0.5 hPa (at 25°C) |
| Barometric resolution | 0.01 hPa |
| Differential pressure range | -500 Pa to +500 Pa |
| Differential pressure accuracy | ±1.0 Pa |
| Differential pressure resolution | 0.1 Pa |
| Temperature compensation range | -10°C to +50°C |
| Integrated temperature sensor | ±0.5°C accuracy |
| Sensing element | MEMS piezoresistive (barometric), capacitive diaphragm (differential) |
| Operating voltage | 5V to 24V DC |
| Power consumption | 85 mW (active), 20 µW (sleep) |
| Communication | MeridianLink (RS-485), Modbus RTU |
| Sampling rate | Configurable: 20 samples/sec to 1 sample/min |
| Data logging | Internal 2 MB flash |
| Dimensions | 110mm × 68mm × 42mm |
| Weight | 185g |
| Ingress protection | IP54 |
| Housing material | Polycarbonate with stainless steel fittings |
| Differential ports | 2× barbed fittings for 6mm OD tubing |
| Altitude calculation | Built-in, based on barometric pressure and ISA model |
| MTBF | 180,000 hours |

## Cleanroom Application

For cleanroom monitoring, the MI-P400 measures the pressure differential between the cleanroom and an adjacent reference space. The sensor supports ISO 14644-3 compliance monitoring with configurable alarm thresholds:

- **ISO Class 5–6**: minimum +12.5 Pa differential recommended
- **ISO Class 7–8**: minimum +5.0 Pa differential recommended

The sensor logs pressure excursions with timestamps and duration, producing compliance reports via MeridianLink.

## Altitude Mode

When operating in altitude mode, the MI-P400 converts barometric readings to altitude above sea level using the International Standard Atmosphere (ISA) model. Accuracy is ±5 meters at elevations below 2000m, degrading to ±15 meters at 5000m. A reference pressure (QNH) can be manually entered for improved accuracy.

## Pricing

- MI-P400: $399 USD
- MI-P400-D (differential-only variant, no barometric): $299 USD
- Tubing kit (2× 5m silicone tubing + fittings): $35 USD
