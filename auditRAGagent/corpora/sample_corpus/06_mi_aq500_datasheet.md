# MI-AQ500 Multi-Gas Air Quality Sensor — Datasheet

## Overview

The MI-AQ500, launched in 2021, is Meridian Instruments' most advanced sensor. It simultaneously measures CO2, volatile organic compounds (VOCs), particulate matter (PM2.5 and PM10), temperature, and humidity. Targeted at indoor air quality monitoring for offices, schools, hospitals, and industrial facilities.

## Specifications

| Parameter | Value |
|-----------|-------|
| **CO2** | |
| CO2 range | 400 ppm to 5000 ppm |
| CO2 accuracy | ±50 ppm + 3% of reading |
| CO2 technology | NDIR (non-dispersive infrared) |
| CO2 response time | 120 seconds (T90) |
| **VOC** | |
| VOC range | 0 to 500 ppb (isobutylene equivalent) |
| VOC accuracy | ±15 ppb (0–100 ppb), ±15% of reading (above 100 ppb) |
| VOC technology | Metal oxide semiconductor (MOX) |
| VOC response time | 30 seconds (T90) |
| **Particulate Matter** | |
| PM2.5 range | 0 to 1000 µg/m³ |
| PM10 range | 0 to 2000 µg/m³ |
| PM accuracy | ±10 µg/m³ (0–100), ±10% of reading (above 100) |
| PM technology | Laser scattering |
| **Temperature** | ±0.5°C accuracy |
| **Humidity** | ±3% RH accuracy |
| Operating voltage | 5V DC (USB-C) or 12–24V DC |
| Power consumption | 850 mW (active, all sensors), 50 µW (sleep) |
| Communication | MeridianLink (RS-485), Wi-Fi (802.11 b/g/n), BLE 5.0 |
| Sampling rate | 1 sample/10 sec (PM), 1 sample/5 sec (gas), 1 sample/sec (T/RH) |
| Data logging | Internal 8 MB flash + microSD slot (up to 32 GB) |
| Dimensions | 155mm × 95mm × 62mm |
| Weight | 420g |
| Ingress protection | IP42 (indoor use only) |
| Housing material | Recycled ABS plastic |
| Display | 2.4" color LCD (320×240), shows real-time readings and AQI |
| MTBF | 80,000 hours |

## Air Quality Index (AQI)

The MI-AQ500 computes a composite AQI on a 0–500 scale following the US EPA methodology. The LCD displays a color-coded indicator:

| AQI Range | Color | Category |
|-----------|-------|----------|
| 0–50 | Green | Good |
| 51–100 | Yellow | Moderate |
| 101–150 | Orange | Unhealthy for sensitive groups |
| 151–200 | Red | Unhealthy |
| 201–300 | Purple | Very unhealthy |
| 301–500 | Maroon | Hazardous |

## CO2 Automatic Baseline Correction

The NDIR CO2 sensor uses Automatic Baseline Correction (ABC), which assumes the lowest CO2 reading over a 7-day period represents outdoor ambient (~420 ppm). ABC should be disabled in environments that never reach outdoor ambient levels (e.g., underground facilities, submarines). ABC can be toggled via MeridianLink.

## Wi-Fi and Cloud

The MI-AQ500 is the first Meridian sensor with built-in Wi-Fi. It can push data to:
1. **MeridianLink Cloud**: Meridian's hosted dashboard (requires subscription: $9.99/month per sensor)
2. **Custom MQTT broker**: configurable endpoint, supports TLS
3. **HTTP webhook**: POST JSON payloads to a custom URL at configurable intervals

## Pricing

- MI-AQ500: $699 USD
- MI-AQ500 with 1-year cloud subscription: $799 USD
- Replacement PM sensor module: $89 USD (user-replaceable, recommended every 2 years)
- Replacement VOC sensor element: $49 USD (recommended every 3 years)
