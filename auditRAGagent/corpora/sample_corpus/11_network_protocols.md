# Network and Communication Protocols

## MeridianLink Protocol

The MeridianLink protocol is Meridian Instruments' proprietary communication protocol, built on top of RS-485 (physical layer) and inspired by Modbus RTU (framing).

### Frame Format

```
| Address (1 byte) | Function (1 byte) | Data Length (2 bytes) | Data (N bytes) | CRC-16 (2 bytes) |
```

### Function Codes

| Code | Name | Description |
|------|------|-------------|
| 0x01 | READ_REGISTER | Read one or more holding registers |
| 0x02 | WRITE_REGISTER | Write to one or more holding registers |
| 0x03 | READ_MEASUREMENT | Read current measurement value(s) |
| 0x04 | READ_LOG | Read stored data log entries |
| 0x05 | START_CALIBRATION | Enter calibration mode |
| 0x06 | APPLY_CALIBRATION | Apply calibration coefficients |
| 0x07 | FIRMWARE_UPDATE | Initiate firmware update sequence |
| 0x08 | DEVICE_INFO | Read device model, serial number, firmware version |
| 0x0F | RESET | Soft reset the sensor |

### Register Map (Common to All Sensors)

| Register | Address | Type | Description |
|----------|---------|------|-------------|
| SERIAL_NUMBER | 0x0000 | uint32 | Sensor serial number |
| MODEL_ID | 0x0004 | uint16 | Model identifier |
| FIRMWARE_VERSION | 0x0006 | uint16[3] | Major.Minor.Patch |
| SAMPLING_RATE | 0x000C | uint16 | Sampling interval in milliseconds |
| RS485_ADDRESS | 0x000E | uint8 | RS-485 bus address |
| RS485_BAUD | 0x000F | uint8 | Baud rate selector (0=9600, 1=19200, 2=38400, 3=57600, 4=115200) |
| STATUS | 0x0010 | uint16 | Bit field: 0=OK, bit 0=cal expired, bit 1=memory full, bit 2=sensor fault |
| TEMPERATURE | 0x0100 | float32 | Current temperature reading (°C) |
| UPTIME | 0x0200 | uint32 | Sensor uptime in seconds |

### Error Responses

If a command fails, the sensor responds with the function code OR'd with 0x80, followed by an error code:

| Error Code | Meaning |
|------------|---------|
| 0x01 | Invalid function code |
| 0x02 | Invalid register address |
| 0x03 | Invalid data value |
| 0x04 | Sensor busy (e.g., during calibration or firmware update) |
| 0x05 | Calibration failure |

## Modbus RTU Compatibility

The MI-T200 and MI-P400 support standard Modbus RTU in addition to the MeridianLink protocol. Modbus mode is enabled by setting register 0x0300 to 1 (default: 0 = MeridianLink mode).

In Modbus mode, the sensors respond to standard Modbus function codes:
- FC03 (Read Holding Registers)
- FC06 (Write Single Register)
- FC16 (Write Multiple Registers)

The Modbus register map is documented separately in each sensor's Modbus appendix.

**Important**: Modbus mode and MeridianLink mode cannot be active simultaneously. Switching modes requires a sensor reboot (power cycle or soft reset via register 0x0300).

## Wi-Fi (MI-AQ500 Only)

The MI-AQ500 includes an ESP32-based Wi-Fi module supporting 802.11 b/g/n on the 2.4 GHz band.

### Wi-Fi Provisioning

1. Press and hold the **CONFIG** button on the MI-AQ500 for 5 seconds. The Wi-Fi LED blinks blue.
2. Connect to the sensor's provisioning network: SSID `Meridian-AQ500-XXXX` (where XXXX = last 4 digits of serial number). No password.
3. Open a browser and navigate to `http://192.168.4.1`. The provisioning page allows you to select the target Wi-Fi network and enter credentials.
4. After successful connection, the Wi-Fi LED turns solid green.

### MQTT Configuration

The MI-AQ500 can publish readings to an MQTT broker. Configuration fields:
- Broker address: hostname or IP
- Port: 1883 (default) or 8883 (TLS)
- Topic prefix: default `meridian/{serial_number}/`
- QoS: 0, 1, or 2 (default: 1)
- Publish interval: 10 seconds to 3600 seconds (default: 60 seconds)
- TLS: optional, supports client certificate authentication

### Message Format (MQTT)

```json
{
  "sensor_id": "MI-AQ500-12345",
  "timestamp": "2024-10-15T14:30:00Z",
  "readings": {
    "co2_ppm": 623,
    "voc_ppb": 45,
    "pm25_ugm3": 12.3,
    "pm10_ugm3": 28.7,
    "temperature_c": 22.1,
    "humidity_rh": 48.5,
    "aqi": 52
  }
}
```
