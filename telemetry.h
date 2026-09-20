#ifndef TELEMETRY_H
#define TELEMETRY_H

#include <stdint.h>
#include <stdbool.h>

#define ETP_SYNC_BYTE 0xAA
#define ETP_END_BYTE  0x55
#define ETP_MAX_PAYLOAD 256

#ifdef __cplusplus
extern "C" {
#endif

uint16_t etp_crc16(const uint8_t *data, uint16_t length) {
    uint16_t crc = 0xFFFF;
    for (uint16_t i = 0; i < length; i++) {
        crc ^= ((uint16_t)data[i] << 8);
        for (uint8_t j = 0; j < 8; j++) {
            if (crc & 0x8000) {
                crc = (crc << 1) ^ 0x1021;
            } else {
                crc = (crc << 1);
            }
        }
    }
    return crc;
}

uint8_t etp_encode_frame(uint8_t msg_id, const uint8_t *payload, uint8_t len, uint8_t *out_buf) {
    out_buf[0] = ETP_SYNC_BYTE;
    out_buf[1] = msg_id;
    out_buf[2] = len;
    for (uint8_t i = 0; i < len; i++) {
        out_buf[3 + i] = payload[i];
    }
    uint16_t crc = etp_crc16(&out_buf[1], len + 2);
    out_buf[3 + len] = (uint8_t)(crc >> 8);
    out_buf[4 + len] = (uint8_t)(crc & 0xFF);
    out_buf[5 + len] = ETP_END_BYTE;
    return 6 + len;
}

#ifdef __cplusplus
}
#endif

#endif // TELEMETRY_H
