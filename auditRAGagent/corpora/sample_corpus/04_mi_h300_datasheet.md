# MI-H300 Precision Humidity Sensor — Datasheet

## Overview

The MI-H300 is Meridian Instruments' precision humidity sensor, launched in 2017. It measures both relative humidity and temperature, making it ideal for cleanrooms, museums, archives, pharmaceutical manufacturing, and agricultural environments. The sensor uses a proprietary capacitive polymer element developed in partnership with ETH Zurich.

## Specifications

| Parameter | Value |
|-----------|-------|
| Humidity range | 0% to 100% RH |
| Humidity accuracy | ±1.5% RH (20–80% range), ±2.5% RH (full range) |
| Humidity resolution | 0.05% RH |
| Temperature range | -20°C to +80°C |
| Temperature accuracy | ±0.3°C |
| Response time (humidity) | 15 seconds (T63, at 25°C, 1 m/s airflow) |
| Sensing element | Capacitive polymer (humidity), NTC thermistor (temperature) |
| Operating voltage | 3.3V to 5.5V DC |
| Power consumption | 55 mW (active), 12 µW (sleep) |
| Communication | MeridianLink (RS-485) |
| Sampling rate | Configurable: 1 sample/sec to 1 sample/10 min |
| Data logging | Internal 1 MB flash (up to 130,000 readings) |
| Dimensions | 92mm × 38mm × 28mm |
| Weight | 67g |
| Ingress protection | IP54 (sensor must be exposed to ambient air) |
| Housing material | ABS plastic with sintered PTFE filter cap |
| Cable length | 2m standard |
| Operating temperature | -20°C to +60°C |
| Dew point calculation | Built-in, accuracy ±0.5°C |
| MTBF | 120,000 hours |

## Dew Point Monitoring

The MI-H300 calculates dew point in real time using the Magnus formula. Dew point alarms can be configured to trigger when ambient temperature approaches the calculated dew point within a configurable margin (default: 3°C).

## Calibration

Factory calibrated at 25°C against saturated salt solutions (11.3% RH, 33.0% RH, 75.3% RH, 97.3% RH). Recalibration recommended every 24 months. Field calibration is supported using Meridian's MI-CAL-H humidity calibration kit ($349 USD), which provides two reference points (33% and 75% RH).

## Known Limitations

- Prolonged exposure to humidity above 95% RH may cause temporary drift of up to ±3% RH. The sensor recovers within 48 hours at 50% RH.
- Chemical vapors (especially solvents, ammonia, and chlorine) can permanently damage the sensing element. Use the MI-H300-CF (chemical filter) variant in environments with chemical exposure risk. The chemical filter adds $45 to the unit price and must be replaced every 6 months.
- The sensor should not be mounted directly above heat sources, as rising thermal currents create measurement artifacts.

## Pricing

- MI-H300: $279 USD
- MI-H300-CF (chemical filter variant): $324 USD
- MI-CAL-H calibration kit: $349 USD
- Replacement PTFE filter cap: $12 USD (pack of 5)
