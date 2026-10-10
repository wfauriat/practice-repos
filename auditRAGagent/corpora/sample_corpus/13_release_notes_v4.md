# MeridianLink v4.0 Release Notes

**Release date**: August 15, 2023

## Overview

MeridianLink v4.0 is a major release introducing cloud analytics, a REST API, webhook integrations, and a redesigned report builder. This release also includes critical security patches and performance improvements.

## New Features

### Cloud Analytics (Cloud Edition)

- **Anomaly detection**: ML-based detection of unusual sensor behavior. Uses an isolation forest model trained on 30 days of historical data per sensor. Alerts are surfaced as "anomaly" type in the alerts panel.
- **Trend forecasting**: Linear and seasonal trend projections for up to 7 days. Available for temperature, humidity, and CO2 channels. Forecasts are displayed as a shaded band on the real-time chart.
- **Correlation analysis**: Cross-sensor correlation matrix showing relationships between measurements. Helps identify environmental dependencies (e.g., HVAC cycling affecting both temperature and humidity).

### REST API (Server and Cloud Editions)

- Full CRUD access to sensors, readings, alerts, and reports. See the API Reference documentation for details.
- SDKs for Python, JavaScript/TypeScript, and C#/.NET.
- API keys managed under Settings > API Keys. Each key has configurable scope (read, write, admin).

### Webhook Integrations

- Send real-time events (alerts, sensor status changes, data quality warnings) to external systems.
- Supported formats: JSON, Slack-compatible, PagerDuty-compatible.
- Retry policy: 3 attempts with exponential backoff (1s, 5s, 25s). Failed webhooks are logged and can be replayed from the webhook history page.

### Report Builder

- Drag-and-drop report builder replacing the previous fixed-format reports.
- Custom date ranges, sensor groups, and metric selections.
- Export to PDF, HTML, or CSV.
- Scheduled reports: daily, weekly, or monthly delivery via email.

## Improvements

- **Dashboard performance**: 3× faster rendering for dashboards with more than 50 sensors. Achieved by switching from SVG to Canvas-based charts.
- **Data export**: CSV export now supports up to 10M rows (previously 100K). Large exports run asynchronously with a download link sent via email.
- **Alert deduplication**: Repeated alerts for the same condition are now grouped. A single notification is sent with a "repeat count" instead of separate alerts.
- **User roles**: Added "Technician" role with calibration and configuration access but no data deletion rights. Role hierarchy: Admin > Technician > Operator > Viewer.
- **PostgreSQL 16 support**: Tested and certified for PostgreSQL 16. PostgreSQL 13 is no longer supported.

## Bug Fixes

- Fixed: MI-T200 channels 5–8 sometimes returned stale readings when channels 1–4 were in high-speed mode (10 samples/sec). Root cause: shared SPI bus contention. Fix: sequential read with per-channel locking.
- Fixed: MeridianLink Desktop crashed on macOS Ventura when opening the calibration wizard. Root cause: deprecated CoreGraphics API. Fix: migrated to Metal rendering.
- Fixed: Alert emails contained UTC timestamps regardless of user timezone setting. Now respects the user's configured timezone.
- Fixed: Data import from CSV failed silently if the timestamp column used comma as decimal separator (common in European locales). Now auto-detects the decimal separator.

## Breaking Changes

- **Minimum PostgreSQL version**: 14 (previously 13). Users on PostgreSQL 13 must upgrade before installing MeridianLink v4.0.
- **API authentication**: The legacy API key format (plain text in query parameter) is removed. All API access now requires Bearer tokens.
- **Report templates**: Custom report templates from v3.x are not compatible with the new report builder. A migration wizard is provided to convert existing templates.

## Known Issues

- The REST API `GET /sensors/{id}/readings` endpoint returns HTTP 500 when `resolution=raw` is used with a date range exceeding 7 days. Workaround: use aggregated resolution or split the query into 7-day chunks. Fix planned for v4.0.1.
- Webhook delivery to endpoints behind Cloudflare may fail with a 403 error if the Meridian IP range is not allowlisted. Meridian's outbound IP range: 52.14.128.0/24.
- Dark mode: some chart tooltips are unreadable (dark text on dark background). Fix planned for v4.0.1.

## Upgrade Instructions

1. **Backup**: Take a full PostgreSQL backup before upgrading.
2. **Server**: Stop the MeridianLink service. Run `meridianlink-upgrade --from 3.5 --to 4.0`. The migration takes approximately 5 minutes per GB of data.
3. **Desktop**: Download the v4.0 installer from meridianinstruments.com/download. Uninstall v3.x first.
4. **Cloud**: No action required — cloud instances are upgraded automatically.
