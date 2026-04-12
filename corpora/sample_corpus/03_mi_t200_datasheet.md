# MI-T200 Advanced Multi-Point Temperature Sensor — Datasheet

## Overview

The MI-T200 is Meridian Instruments' advanced temperature monitoring solution, supporting up to 8 measurement points on a single device. Launched in 2016, it is designed for applications requiring spatial temperature profiling, such as cold chain logistics, pharmaceutical storage, and data center hot/cold aisle monitoring.

## Specifications

| Parameter | Value |
|-----------|-------|
| Measurement range | -55°C to +150°C |
| Accuracy | ±0.2°C (at 25°C), ±0.4°C (full range) |
| Resolution | 0.01°C |
| Measurement points | 1 to 8 (configurable) |
| Response time | 5 seconds (in still air) per channel |
| Sensing element | Platinum RTD (PT1000), one per channel |
| Operating voltage | 5V to 24V DC |
| Power consumption | 120 mW (all channels active), 15 µW (sleep) |
| Communication | MeridianLink (RS-485), Modbus RTU, 4-20mA analog output |
| Sampling rate | Configurable: 10 samples/sec to 1 sample/hour per channel |
| Data logging | Internal 4 MB flash (up to 500,000 readings per channel) |
| Dimensions | 142mm × 85mm × 38mm (base unit) |
| Weight | 310g (base unit, without probes) |
| Ingress protection | IP65 (base unit), IP67 (probes) |
| Housing material | Anodized aluminum (base), 316L stainless steel (probes) |
| Probe cable length | 3m standard per channel |
| Operating humidity | 0–95% RH (non-condensing) |
| MTBF | 200,000 hours |

## Multi-Point Configuration

Each MI-T200 supports 1 to 8 independently addressable temperature probes. Probes connect to the base unit via M12 connectors. Each channel can be individually named, configured with its own sampling rate, and assigned alarm thresholds.

### Channel Alarm Modes

- **Absolute**: triggers when temperature exceeds a fixed threshold
- **Rate-of-change**: triggers when temperature changes faster than X°C per minute
- **Differential**: triggers when the difference between two channels exceeds a threshold

## Pricing

- MI-T200 Base Unit (1 probe included): $649 USD
- Additional probes: $89 USD each
- 8-probe bundle: $1,199 USD (base + 8 probes)

## Data Output Formats

The MI-T200 outputs data in three formats:
1. **MeridianLink native**: binary protocol, highest throughput (100 readings/sec)
2. **Modbus RTU**: standard industrial protocol, compatible with most SCADA systems
3. **4-20mA analog**: one output per channel, requires MI-T200-AO expansion module ($129 USD)

## Firmware

Current firmware version: 3.8.2 (released October 2024). Firmware updates are delivered via MeridianLink over RS-485 or via USB using the MeridianLink Desktop application.
