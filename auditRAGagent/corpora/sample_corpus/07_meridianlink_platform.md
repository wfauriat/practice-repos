# MeridianLink Software Platform

## Overview

MeridianLink is Meridian Instruments' unified software platform for sensor configuration, monitoring, data logging, alerting, and reporting. First released in 2014 alongside the MI-T100, it has evolved through four major versions.

## Version History

| Version | Release Date | Key Changes |
|---------|-------------|-------------|
| 1.0 | March 2014 | Initial release, MI-T100 support only |
| 2.0 | September 2019 | Added MI-P400 support, Modbus gateway, dashboard overhaul |
| 3.0 | June 2021 | MI-AQ500 support, Wi-Fi provisioning, alert rules engine |
| 3.5 | January 2023 | Multi-site management, user roles, audit logging |
| 4.0 | August 2023 | Cloud analytics, REST API, webhook integrations, report builder |

## Editions

MeridianLink is available in three editions:

### MeridianLink Desktop (Free)
- Connects to sensors via RS-485 USB adapter
- Supports up to 16 sensors
- Real-time dashboard with 7-day data retention
- CSV export
- Windows 10/11 and macOS 12+ (no Linux support)
- Download size: 245 MB

### MeridianLink Server (Licensed)
- On-premise installation on Linux (Ubuntu 20.04+, RHEL 8+) or Windows Server 2019+
- Unlimited sensors
- 5-year data retention (configurable)
- User roles: Admin, Operator, Viewer (up to 50 users)
- REST API access
- Email and SMS alerts
- Pricing: $2,499 USD per server license + $499/year maintenance

### MeridianLink Cloud (SaaS)
- Hosted by Meridian on AWS (us-east-1, eu-west-1, ap-southeast-1 regions)
- Unlimited data retention
- Unlimited users with SSO (SAML 2.0)
- Advanced analytics and ML-based anomaly detection
- Pricing: $9.99/month per sensor (minimum 10 sensors), volume discounts available

## System Requirements (Server Edition)

| Resource | Minimum | Recommended |
|----------|---------|-------------|
| CPU | 2 cores | 4 cores |
| RAM | 4 GB | 8 GB |
| Disk | 20 GB | 100 GB SSD |
| Database | PostgreSQL 14+ | PostgreSQL 16 |
| Network | 100 Mbps | 1 Gbps |

## RS-485 Network Topology

MeridianLink communicates with sensors over RS-485 in a multi-drop bus topology. Key parameters:
- Baud rate: 9600 (default), 19200, 38400, 57600, 115200
- Maximum bus length: 1200 meters (at 9600 baud)
- Maximum sensors per bus: 32 (with standard RS-485 transceivers), 128 (with high-drive transceivers)
- Termination: 120Ω resistor required at each end of the bus
- Recommended cable: shielded twisted pair, 24 AWG minimum

## Data Storage

All sensor data is stored in PostgreSQL (Server edition) or AWS TimeStream (Cloud edition). The data schema includes:
- `sensor_id`: unique identifier
- `timestamp`: UTC, millisecond precision
- `channel`: measurement channel (e.g., "temperature", "humidity")
- `value`: floating-point measurement
- `unit`: measurement unit
- `quality`: data quality flag (0 = good, 1 = uncertain, 2 = bad)
