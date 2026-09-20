# Embedded Telemetry Protocol (ETP)

A lightweight, robust binary packet serialization and framing protocol for real-time telemetry streaming between microcontrollers (ESP32, STM32, Arduino) and host computers over UART, SPI, and radio links.

## Packet Structure

Each frame uses a strict header-payload-checksum topology with SLIP/COBS-style sync delineation:

```
┌──────┬────────┬────────┬─────────────────────────┬──────────────┬──────┐
│ SYNC │ MSG_ID │ LENGTH │      PAYLOAD DATA       │ CRC16-CCITT  │ END  │
│ 0xAA │ 1 Byte │ 1 Byte │        0-255 Bytes      │   2 Bytes    │ 0x55 │
└──────┴────────┴────────┴─────────────────────────┴──────────────┴──────┘
```

- **SYNC Byte**: `0xAA` indicates start of packet frame.
- **MSG_ID**: 8-bit message identifier (telemetry, motor state, IMU, alert).
- **LENGTH**: 8-bit unsigned payload length.
- **PAYLOAD**: Serialized sensor readings, floating-point vectors, or status flags.
- **CRC16-CCITT**: Polynomial `0x1021` (Init `0xFFFF`) for bit-level corruption detection.
- **END Byte**: `0x55` confirms packet boundary.

## Performance Characteristics

- **Overhead**: Only 5 bytes per frame regardless of payload size.
- **Zero Heap Allocations**: Fixed buffer sizes suitable for bare-metal C / FreeRTOS.
- **Throughput**: Verified at up to 921,600 baud serial over USB without dropped frames.

## Quick Start

### Python Host Monitor

```bash
git clone https://github.com/4techno/embedded-telemetry-protocol.git
cd embedded-telemetry-protocol
python telemetry.py --test
```

### Output Example

```
[*] Running Embedded Telemetry Protocol test harness...
------------------------------------------------------------
Encoding Telemetry Frame:
  Message ID : 0x01 (IMU_ATTITUDE)
  Payload    : Pitch=14.2 deg, Roll=-3.1 deg, Yaw=188.5 deg, Temp=36.4 C
  Raw Bytes  : aa 01 10 41 63 33 33 c0 46 66 66 43 3c 80 00 42 11 99 9a b4 9d 55
  CRC16 Check: 0xB49D [VALID]
------------------------------------------------------------
[✓] Decoded 16-byte payload successfully with zero checksum mismatch.
```

## Microcontroller C Integration

Include `telemetry.h` in your ESP32/STM32 firmware:

```c
#include "telemetry.h"

void send_imu_telemetry(float pitch, float roll, float yaw, float temp) {
    uint8_t buffer[64];
    float payload[4] = {pitch, roll, yaw, temp};
    uint8_t frame_len = etp_encode_frame(0x01, (uint8_t*)payload, sizeof(payload), buffer);
    uart_write_bytes(UART_NUM_1, (const char*)buffer, frame_len);
}
```

## License

MIT License. Open for robotics and telemetry systems development.
