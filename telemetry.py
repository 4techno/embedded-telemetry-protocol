import struct
import sys
from typing import Dict, Optional, Tuple

SYNC_BYTE = 0xAA
END_BYTE  = 0x55

def calculate_crc16(data: bytes) -> int:
    crc = 0xFFFF
    for byte in data:
        crc ^= (byte << 8)
        for _ in range(8):
            if crc & 0x8000:
                crc = ((crc << 1) ^ 0x1021) & 0xFFFF
            else:
                crc = (crc << 1) & 0xFFFF
    return crc

def encode_packet(msg_id: int, payload: bytes) -> bytes:
    length = len(payload)
    if length > 255:
        raise ValueError("Payload length cannot exceed 255 bytes.")
        
    header_and_body = bytes([msg_id, length]) + payload
    crc = calculate_crc16(header_and_body)
    packet = bytes([SYNC_BYTE]) + header_and_body + struct.pack(">H", crc) + bytes([END_BYTE])
    return packet

def decode_packet(raw_data: bytes) -> Optional[Tuple[int, bytes]]:
    if len(raw_data) < 6:
        return None
    if raw_data[0] != SYNC_BYTE or raw_data[-1] != END_BYTE:
        return None
        
    msg_id = raw_data[1]
    length = raw_data[2]
    
    if len(raw_data) != 6 + length:
        return None
        
    payload = raw_data[3:3 + length]
    received_crc = struct.unpack(">H", raw_data[3 + length:5 + length])[0]
    computed_crc = calculate_crc16(raw_data[1:3 + length])
    
    if received_crc != computed_crc:
        print(f"[!] CRC Mismatch: computed 0x{computed_crc:04X}, received 0x{received_crc:04X}")
        return None
        
    return msg_id, payload

def main():
    print("[*] Running Embedded Telemetry Protocol (ETP) Test Harness...")
    pitch, roll, yaw, temp = 14.2, -3.1, 188.5, 36.4
    payload = struct.pack("<4f", pitch, roll, yaw, temp)
    
    packet = encode_packet(msg_id=0x01, payload=payload)
    hex_str = " ".join(f"{b:02x}" for b in packet)
    
    print("-" * 60)
    print(f"  Encoded Packet   : {hex_str}")
    print(f"  Total Length     : {len(packet)} bytes (Overhead: 6 bytes)")
    
    decoded = decode_packet(packet)
    if decoded:
        d_id, d_payload = decoded
        dp, dr, dy, dt = struct.unpack("<4f", d_payload)
        print(f"  Decoded Msg ID   : 0x{d_id:02X}")
        print(f"  Decoded Telemetry: Pitch={dp:.1f} deg, Roll={dr:.1f} deg, Yaw={dy:.1f} deg, Temp={dt:.1f} C")
        print("-" * 60)
        print("[✓] Packet integrity verified with zero checksum errors.")
    else:
        print("[✗] Packet decoding failed.")

if __name__ == "__main__":
    main()
