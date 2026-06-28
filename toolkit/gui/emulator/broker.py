from __future__ import annotations

import socket
import struct
from dataclasses import dataclass, field
from typing import Optional

from PyQt6.QtCore import (
    QObject,
    QThread,
    pyqtSignal,
)

from toolkit.gui.emulator.consts import (
    decode_register, 
    DEVICE_INFO, 
    BROKER_HOST, 
    BROKER_PORT,
    PACKET_SIZE,
    PACKET_MAGIC
)

@dataclass
class ActivityPacket:
    dev_id:    int
    direction: str          # 'R' or 'W'
    size:      int          # bytes
    addr:      int          # guest physical address
    value:     int          # 32-bit value
    ts_ns:     int          # virtual clock nanoseconds
    # Decoded
    dev_short: str = field(init=False)
    dev_long:  str = field(init=False)
    reg_name:  str = field(init=False)

    def __post_init__(self) -> None:
        info = DEVICE_INFO.get(self.dev_id, ("?", "Unknown", 0))
        self.dev_short = info[0]
        self.dev_long  = info[1]
        self.reg_name  = decode_register(self.addr)

    @property
    def ts_ms_str(self) -> str:
        return f"{self.ts_ns / 1_000_000:.3f}"

    @property
    def value_hex(self) -> str:
        width = self.size * 2
        return f"0x{self.value:0{width}X}"

    @property
    def is_read(self) -> bool:
        return self.direction == 'R'

class BrokerThread(QThread):
    """Reads RDEV packets from the broker socket in a background thread."""

    packet_received = pyqtSignal(object)   # ActivityPacket
    status_changed  = pyqtSignal(str)      # status message

    _stop_flag: bool

    def __init__(self, parent: Optional[QObject] = None) -> None:
        super().__init__(parent)
        self._stop_flag = False

    def run(self) -> None:
        self._stop_flag = False
        self.status_changed.emit(f"Connecting to {BROKER_HOST}:{BROKER_PORT}…")
        sock: Optional[socket.socket] = None
        buf = bytearray()

        while not self._stop_flag:
            if sock is None:
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(2.0)
                    sock.connect((BROKER_HOST, BROKER_PORT))
                    sock.settimeout(0.5)
                    self.status_changed.emit(
                        f"Connected to {BROKER_HOST}:{BROKER_PORT}")
                    buf.clear()
                except OSError as exc:
                    sock = None
                    self.status_changed.emit(
                        f"Connection failed: {exc} — retrying in 3 s…")
                    self.msleep(3000)
                    continue

            try:
                chunk = sock.recv(256)
                if not chunk:
                    raise OSError("connection closed by QEMU")
                buf.extend(chunk)
            except socket.timeout:
                continue
            except OSError as exc:
                self.status_changed.emit(f"Disconnected: {exc}")
                sock.close()
                sock = None
                self.msleep(1000)
                continue

            while len(buf) >= PACKET_SIZE:
                raw = bytes(buf[:PACKET_SIZE])
                del buf[:PACKET_SIZE]
                pkt = self._parse(raw)
                if pkt is not None:
                    self.packet_received.emit(pkt)

        if sock is not None:
            sock.close()

    def stop(self) -> None:
        self._stop_flag = True

    @staticmethod
    def _parse(raw: bytes) -> Optional[ActivityPacket]:
        if raw[:4] != PACKET_MAGIC:
            return None
        dev_id    = raw[4]
        direction = chr(raw[5])
        size      = raw[6]
        addr,     = struct.unpack_from(">I", raw, 8)
        value,    = struct.unpack_from(">I", raw, 12)
        ts_ns,    = struct.unpack_from(">Q", raw, 16)
        if direction not in ('R', 'W'):
            return None
        return ActivityPacket(dev_id=dev_id, direction=direction, size=size,
                               addr=addr, value=value, ts_ns=ts_ns)