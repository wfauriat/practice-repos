# MeridianLink REST API Reference

## Overview

The MeridianLink REST API (available in Server v4.0+ and Cloud editions) provides programmatic access to sensor data, configuration, and alerts. The API uses JSON over HTTPS and follows RESTful conventions.

## Authentication

All API requests require a Bearer token. Tokens are obtained via the `/auth/token` endpoint:

```
POST /api/v1/auth/token
Content-Type: application/json

{
  "username": "api_user",
  "password": "secret",
  "scope": "read write"
}
```

Tokens expire after 24 hours. Refresh tokens are valid for 30 days.

## Rate Limits

- Server edition: no rate limits
- Cloud edition: 1000 requests/minute per API key, 100,000 requests/day

## Endpoints

### Sensors

**GET /api/v1/sensors**
List all sensors. Supports pagination (`?page=1&per_page=50`) and filtering (`?type=MI-T100&status=online`).

**GET /api/v1/sensors/{sensor_id}**
Get sensor details including model, firmware version, location, and current status.

**PATCH /api/v1/sensors/{sensor_id}**
Update sensor configuration (name, location, sampling rate, alarm thresholds).

### Readings

**GET /api/v1/sensors/{sensor_id}/readings**
Query historical readings. Parameters:
- `start`: ISO 8601 timestamp (required)
- `end`: ISO 8601 timestamp (default: now)
- `channel`: filter by channel name
- `resolution`: aggregation window — `raw`, `1min`, `5min`, `1hour`, `1day` (default: `raw`)
- `format`: `json` (default) or `csv`

Maximum query range: 7 days for `raw`, 90 days for aggregated, 365 days for `1day`.

**POST /api/v1/sensors/{sensor_id}/readings**
Submit manual readings (for integration with non-Meridian sensors). Requires `write` scope.

### Alerts

**GET /api/v1/alerts**
List active alerts. Supports filtering by severity (`critical`, `warning`, `info`) and sensor.

**GET /api/v1/alerts/rules**
List configured alert rules.

**POST /api/v1/alerts/rules**
Create a new alert rule. Example:

```json
{
  "name": "Freezer temp high",
  "sensor_id": "MI-T100-0042",
  "channel": "temperature",
  "condition": "above",
  "threshold": -15.0,
  "duration_seconds": 300,
  "severity": "critical",
  "actions": ["email:ops@example.com", "webhook:https://hooks.example.com/alert"]
}
```

### Reports

**POST /api/v1/reports/generate**
Generate a report. Supported types:
- `compliance`: regulatory compliance summary for a date range
- `summary`: daily/weekly/monthly sensor summary
- `excursion`: list of threshold violations

Reports are generated asynchronously. The response includes a `report_id` for polling status via `GET /api/v1/reports/{report_id}`.

## Error Codes

| Code | Meaning |
|------|---------|
| 400 | Bad request — invalid parameters |
| 401 | Unauthorized — missing or expired token |
| 403 | Forbidden — insufficient scope |
| 404 | Not found — sensor or resource does not exist |
| 429 | Rate limit exceeded |
| 500 | Internal server error |

## SDKs

Official SDKs are available for:
- Python: `pip install meridianlink` (v2.1.0, supports async)
- JavaScript/TypeScript: `npm install @meridian/link` (v1.4.0)
- C#/.NET: NuGet package `MeridianLink.Client` (v1.2.0)
