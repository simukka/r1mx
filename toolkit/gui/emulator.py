#!/usr/bin/env python3
"""
R1MX Emulator Device Activity Monitor
======================================
A PyQt6 GUI that connects to the QEMU r1mx-virtex4 machine's activity broker
(TCP localhost:17187) and displays real-time MMIO access events for all
emulated devices.

Layout
------
  Left  — Device list: one row per device with a flashing LED, R/W counters
  Centre — Event log: scrolling table with decoded register names
  Right  — UART monitor: hex + ASCII dump of bytes written to / read from the
            XPS UARTLite TX/RX FIFOs

Packet format (32 bytes, all multi-byte fields big-endian):
  [0-3]   magic "RDEV"
  [4]     device_id  (R1MX_DEV_* constants)
  [5]     direction  'R' = 0x52 / 'W' = 0x57
  [6]     access size in bytes (1, 2, or 4)
  [7]     reserved
  [8-11]  guest physical address (uint32)
  [12-15] value lower 32 bits (uint32)
  [16-23] virtual-clock timestamp ns (uint64)
  [24-31] reserved

Run:
  python3 -m toolkit.gui.emulator
  python3 toolkit/gui/emulator.py        # also works

Requires:
  PyQt6 >= 6.4
"""

from __future__ import annotations

import socket
import struct
import sys
import time
from collections import deque
from dataclasses import dataclass, field
from typing import Deque, Dict, List, Optional, Tuple

from PyQt6.QtCore import (
    QAbstractTableModel,
    QModelIndex,
    QObject,
    Qt,
    QThread,
    QTimer,
    pyqtSignal,
)
from PyQt6.QtGui import QColor, QFont, QFontDatabase, QPalette
from PyQt6.QtWidgets import (
    QApplication,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMainWindow,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QSplitter,
    QStatusBar,
    QTableView,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

BROKER_HOST = "127.0.0.1"
BROKER_PORT = 17187
PACKET_SIZE = 32
PACKET_MAGIC = b"RDEV"

# Device IDs (must match r1mx_activity.h)
DEV_UART       = 0
DEV_ETHERNET   = 1
DEV_DMA        = 2
DEV_HIST_LUMA  = 3
DEV_HIST_RGB   = 4
DEV_HIST_RGBC  = 5
DEV_HIST_MONO  = 6
DEV_HIST_WAVE  = 7
DEV_FPGA       = 8

# Short name, long name, base address
DEVICE_INFO: Dict[int, Tuple[str, str, int]] = {
    DEV_UART:      ("UART",      "XPS UARTLite",         0xE060_0000),
    DEV_ETHERNET:  ("ETH",       "XPS EthernetLite",     0xE102_0000),
    DEV_DMA:       ("DMA",       "OPB DMA Channel",      0x6401_0000),
    DEV_HIST_LUMA: ("HIST-LUMA", "Luma Histogram",       0xE008_0000),
    DEV_HIST_RGB:  ("HIST-RGB",  "RGB Histogram",        0xE00A_0000),
    DEV_HIST_RGBC: ("HIST-RGBC", "RGB Comp Histogram",   0xE010_0000),
    DEV_HIST_MONO: ("HIST-MONO", "Mono Histogram",       0xE012_0000),
    DEV_HIST_WAVE: ("HIST-WAVE", "Luma Waveform",        0xE020_0000),
    DEV_FPGA:      ("FPGA",      "FPGA Catch-all",       0xE000_0000),
}

# ---------------------------------------------------------------------------
# Register map: guest physical address → (register name, notes)
# ---------------------------------------------------------------------------

REG_MAP: Dict[int, Tuple[str, str]] = {
    # XPS UARTLite (DS570)
    0xE060_0000: ("ULITE_RX_FIFO",  "RX data / status"),
    0xE060_0004: ("ULITE_TX_FIFO",  "TX data byte"),
    0xE060_0008: ("ULITE_STATUS",   "RX valid[0], TX full[3], parity err[4], frame err[5], overrun[6]"),
    0xE060_000C: ("ULITE_CONTROL",  "RST_TX[0] RST_RX[1] EN_INTR[4]"),

    # XPS EthernetLite (DS599) — key registers; buffer area is 0x7F40 bytes
    0xE102_7F40: ("ETHLITE_MDIOADDR",  "MDIO address"),
    0xE102_7F44: ("ETHLITE_MDIOWR",    "MDIO write data"),
    0xE102_7F48: ("ETHLITE_MDIORD",    "MDIO read data"),
    0xE102_7F4C: ("ETHLITE_MDIOCTRL",  "MDIO control"),
    0xE102_7F50: ("ETHLITE_TX0_LEN",   "TX buf-0 frame length"),
    0xE102_7F54: ("ETHLITE_GIE",       "Global interrupt enable"),
    0xE102_7F5C: ("ETHLITE_TX0_CTRL",  "TX buf-0 control: SND[0] PROG[1]"),
    0xE102_7F7C: ("ETHLITE_RX0_CTRL",  "RX buf-0 control: RDY[0] IE[3]"),
    0xE102_FF50: ("ETHLITE_TX1_LEN",   "TX buf-1 frame length"),
    0xE102_FF5C: ("ETHLITE_TX1_CTRL",  "TX buf-1 control"),
    0xE102_FF7C: ("ETHLITE_RX1_CTRL",  "RX buf-1 control"),

    # OPB DMA Channel (dma_v1_10_b)
    0x6401_0000: ("DMA_RST",   "Reset (write 0xA)"),
    0x6401_0004: ("DMA_DMAC",  "DMA Control (reset=0x98000000)"),
    0x6401_0008: ("DMA_SA",    "Source Address"),
    0x6401_000C: ("DMA_DA",    "Destination Address"),
    0x6401_0010: ("DMA_LEN",   "Byte count — write triggers transfer"),
    0x6401_0014: ("DMA_DMAS",  "DMA Status: BUSY[31]"),
    0x6401_0018: ("DMA_BDA",   "Buffer Descriptor Address"),
    0x6401_001C: ("DMA_SWCR",  "SW Control: SG_ENABLE[31]"),
    0x6401_0020: ("DMA_UPC",   "Unserviced Packet Count"),
    0x6401_0024: ("DMA_PCT",   "Packet Count Threshold"),
    0x6401_0028: ("DMA_PWB",   "Packet Wait Bound"),
    0x6401_002C: ("DMA_IS",    "Interrupt Status (W1C)"),
    0x6401_0030: ("DMA_IE",    "Interrupt Enable"),

    # RED Histogram IPs — inferred from firmware disassembly
    0xE008_0034: ("LUMA_HIST_STATUS0", ""),
    0xE008_0038: ("LUMA_HIST_CTRL",    "Enable[5]"),
    0xE008_003C: ("LUMA_HIST_STATUS1", "Done[5]"),
    0xE00A_0034: ("RGB_HIST_STATUS0",  ""),
    0xE00A_0038: ("RGB_HIST_CTRL",     "Enable[5]"),
    0xE00A_003C: ("RGB_HIST_STATUS1",  "Done[5]"),
    0xE010_0034: ("RGBC_HIST_STATUS0", ""),
    0xE010_0038: ("RGBC_HIST_CTRL",    "Enable[5]"),
    0xE010_003C: ("RGBC_HIST_STATUS1", "Done[5]"),
    0xE012_0034: ("MONO_HIST_STATUS0", ""),
    0xE012_0038: ("MONO_HIST_CTRL",    "Enable[5]"),
    0xE012_003C: ("MONO_HIST_STATUS1", "Done[5]"),
    0xE020_0034: ("LUMA_WAVE_STATUS0", ""),
    0xE020_0038: ("LUMA_WAVE_CTRL",    "Enable[5]"),
    0xE020_003C: ("LUMA_WAVE_STATUS1", "Done[5]"),
}


def decode_register(addr: int) -> str:
    """Return 'REGNAME' if address is in the map, or '+0xOFFSET' relative to device base."""
    if addr in REG_MAP:
        return REG_MAP[addr][0]
    # Find closest device base
    for dev_id, (_, _, base) in DEVICE_INFO.items():
        if base <= addr < base + 0x40000:
            return f"+0x{addr - base:04X}"
    return f"0x{addr:08X}"


def decode_register_note(addr: int) -> str:
    """Return field description if available."""
    if addr in REG_MAP:
        return REG_MAP[addr][1]
    return ""


# ---------------------------------------------------------------------------
# Packet dataclass
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# Background TCP reader thread
# ---------------------------------------------------------------------------

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
        buf = b""

        while not self._stop_flag:
            if sock is None:
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(2.0)
                    sock.connect((BROKER_HOST, BROKER_PORT))
                    sock.settimeout(0.5)
                    self.status_changed.emit(
                        f"Connected to {BROKER_HOST}:{BROKER_PORT}")
                    buf = b""
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
                buf += chunk
            except socket.timeout:
                continue
            except OSError as exc:
                self.status_changed.emit(f"Disconnected: {exc}")
                sock.close()
                sock = None
                self.msleep(1000)
                continue

            while len(buf) >= PACKET_SIZE:
                raw = buf[:PACKET_SIZE]
                buf = buf[PACKET_SIZE:]
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


# ---------------------------------------------------------------------------
# Device state — per-device counters and last-active timestamp
# ---------------------------------------------------------------------------

@dataclass
class DeviceState:
    dev_id:      int
    read_count:  int = 0
    write_count: int = 0
    last_read:   float = 0.0   # host monotonic time of last read
    last_write:  float = 0.0   # host monotonic time of last write


# ---------------------------------------------------------------------------
# LED widget — flashes on activity
# ---------------------------------------------------------------------------

_LED_OFF   = QColor("#2a2a2a")
_LED_READ  = QColor("#3a82f7")   # blue
_LED_WRITE = QColor("#f77f3a")   # orange
_LED_FADE  = 0.20                # seconds until LED fades


class LedWidget(QWidget):
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setFixedSize(14, 14)
        self._color = _LED_OFF
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._fade)
        self._timer.setInterval(50)

    def flash(self, color: QColor) -> None:
        self._color = color
        self.update()
        if not self._timer.isActive():
            self._timer.start()
        self._deadline = time.monotonic() + _LED_FADE

    def _fade(self) -> None:
        if time.monotonic() >= self._deadline:
            self._color = _LED_OFF
            self.update()
            self._timer.stop()

    def paintEvent(self, _event) -> None:  # type: ignore[override]
        from PyQt6.QtGui import QPainter
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(self._color)
        p.drawEllipse(1, 1, 12, 12)


# ---------------------------------------------------------------------------
# Device list panel
# ---------------------------------------------------------------------------

class DeviceListPanel(QWidget):
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._leds:   Dict[int, LedWidget] = {}
        self._r_lbls: Dict[int, QLabel]    = {}
        self._w_lbls: Dict[int, QLabel]    = {}

        layout = QVBoxLayout(self)
        layout.setSpacing(2)
        layout.setContentsMargins(6, 6, 6, 6)

        # Header
        hdr = QLabel("DEVICES")
        hdr.setStyleSheet("font-weight: bold; font-size: 10px; color: #888;")
        layout.addWidget(hdr)

        for dev_id in sorted(DEVICE_INFO):
            short, long_name, base = DEVICE_INFO[dev_id]
            row = QHBoxLayout()
            row.setSpacing(6)

            led = LedWidget()
            self._leds[dev_id] = led
            row.addWidget(led)

            name_lbl = QLabel(f"{short}")
            name_lbl.setToolTip(f"{long_name}\nBase: 0x{base:08X}")
            name_lbl.setFixedWidth(72)
            name_lbl.setStyleSheet("font-size: 11px;")
            row.addWidget(name_lbl)

            r_lbl = QLabel("R:0")
            r_lbl.setStyleSheet("font-size: 10px; color: #3a82f7;")
            r_lbl.setFixedWidth(40)
            self._r_lbls[dev_id] = r_lbl
            row.addWidget(r_lbl)

            w_lbl = QLabel("W:0")
            w_lbl.setStyleSheet("font-size: 10px; color: #f77f3a;")
            w_lbl.setFixedWidth(40)
            self._w_lbls[dev_id] = w_lbl
            row.addWidget(w_lbl)

            row.addStretch()
            layout.addLayout(row)

        layout.addStretch()

    def update_device(self, pkt: ActivityPacket) -> None:
        led = self._leds.get(pkt.dev_id)
        if led is None:
            return
        if pkt.is_read:
            led.flash(_LED_READ)
            lbl = self._r_lbls[pkt.dev_id]
            cur = int(lbl.text()[2:]) + 1
            lbl.setText(f"R:{cur}")
        else:
            led.flash(_LED_WRITE)
            lbl = self._w_lbls[pkt.dev_id]
            cur = int(lbl.text()[2:]) + 1
            lbl.setText(f"W:{cur}")

    def reset_counters(self) -> None:
        for dev_id in DEVICE_INFO:
            if dev_id in self._r_lbls:
                self._r_lbls[dev_id].setText("R:0")
                self._w_lbls[dev_id].setText("W:0")


# ---------------------------------------------------------------------------
# Event log table model
# ---------------------------------------------------------------------------

_LOG_COLUMNS = ["Time (ms)", "Device", "R/W", "Address", "Register", "Value", "sz"]
_LOG_MAX     = 4096          # keep last N events
_COL_TS   = 0
_COL_DEV  = 1
_COL_DIR  = 2
_COL_ADDR = 3
_COL_REG  = 4
_COL_VAL  = 5
_COL_SZ   = 6


class EventLogModel(QAbstractTableModel):
    def __init__(self, parent: Optional[QObject] = None) -> None:
        super().__init__(parent)
        self._rows: Deque[ActivityPacket] = deque(maxlen=_LOG_MAX)

    def append(self, pkt: ActivityPacket) -> None:
        insert_pos = len(self._rows)
        self.beginInsertRows(QModelIndex(), insert_pos, insert_pos)
        self._rows.append(pkt)
        self.endInsertRows()
        # If we hit the cap, the deque silently drops the oldest entry.
        # Signal a full reset so the view doesn't see stale row indices.
        if len(self._rows) == _LOG_MAX:
            self.beginResetModel()
            self.endResetModel()

    def clear(self) -> None:
        self.beginResetModel()
        self._rows.clear()
        self.endResetModel()

    # --- QAbstractTableModel interface ---

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return len(self._rows)

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return len(_LOG_COLUMNS)

    def headerData(self, section: int, orientation: Qt.Orientation,
                   role: int = Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole and \
                orientation == Qt.Orientation.Horizontal:
            return _LOG_COLUMNS[section]
        return None

    def data(self, index: QModelIndex,
             role: int = Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None
        pkt = self._rows[index.row()]
        col = index.column()

        if role == Qt.ItemDataRole.DisplayRole:
            if col == _COL_TS:   return pkt.ts_ms_str
            if col == _COL_DEV:  return pkt.dev_short
            if col == _COL_DIR:  return pkt.direction
            if col == _COL_ADDR: return f"0x{pkt.addr:08X}"
            if col == _COL_REG:  return pkt.reg_name
            if col == _COL_VAL:  return pkt.value_hex
            if col == _COL_SZ:   return str(pkt.size)

        if role == Qt.ItemDataRole.ForegroundRole:
            if col == _COL_DIR:
                return QColor("#3a82f7") if pkt.is_read else QColor("#f77f3a")

        if role == Qt.ItemDataRole.BackgroundRole:
            if pkt.is_read:
                return QColor("#1a2035")
            else:
                return QColor("#201a10")

        if role == Qt.ItemDataRole.ToolTipRole:
            note = decode_register_note(pkt.addr)
            return (
                f"Device: {pkt.dev_long}\n"
                f"Addr:   0x{pkt.addr:08X}\n"
                f"Reg:    {pkt.reg_name}\n"
                f"Value:  {pkt.value_hex}\n"
                f"Time:   {pkt.ts_ms_str} ms\n"
                + (f"Fields: {note}" if note else "")
            )

        return None


# ---------------------------------------------------------------------------
# UART monitor — hex + ASCII dump
# ---------------------------------------------------------------------------

class UartMonitor(QWidget):
    """Shows TX (writes to TX_FIFO) and RX (reads from RX_FIFO) byte streams."""

    UART_TX_ADDR = 0xE060_0004
    UART_RX_ADDR = 0xE060_0000

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setSpacing(4)
        layout.setContentsMargins(4, 4, 4, 4)

        hdr = QLabel("UART MONITOR")
        hdr.setStyleSheet("font-weight: bold; font-size: 10px; color: #888;")
        layout.addWidget(hdr)

        tx_hdr = QLabel("TX (firmware → serial)")
        tx_hdr.setStyleSheet("font-size: 10px; color: #f77f3a;")
        layout.addWidget(tx_hdr)

        self._tx_view = QTextEdit()
        self._tx_view.setReadOnly(True)
        self._tx_view.setFont(self._mono_font())
        self._tx_view.setStyleSheet(
            "background:#0d1117; color:#e6edf3; font-size:11px;")
        self._tx_view.setMaximumHeight(200)
        layout.addWidget(self._tx_view)

        rx_hdr = QLabel("RX (serial → firmware)")
        rx_hdr.setStyleSheet("font-size: 10px; color: #3a82f7;")
        layout.addWidget(rx_hdr)

        self._rx_view = QTextEdit()
        self._rx_view.setReadOnly(True)
        self._rx_view.setFont(self._mono_font())
        self._rx_view.setStyleSheet(
            "background:#0d1117; color:#e6edf3; font-size:11px;")
        self._rx_view.setMaximumHeight(200)
        layout.addWidget(self._rx_view)

        # Raw byte accumulator for the hex+ascii formatter
        self._tx_bytes: bytearray = bytearray()
        self._rx_bytes: bytearray = bytearray()

        btn_clear = QPushButton("Clear")
        btn_clear.setFixedWidth(60)
        btn_clear.clicked.connect(self._clear)
        layout.addWidget(btn_clear)
        layout.addStretch()

    @staticmethod
    def _mono_font() -> QFont:
        font = QFont("Monospace")
        font.setStyleHint(QFont.StyleHint.TypeWriter)
        font.setPointSize(9)
        return font

    def handle_packet(self, pkt: ActivityPacket) -> None:
        if pkt.dev_id != DEV_UART:
            return
        byte_val = pkt.value & 0xFF
        if pkt.addr == self.UART_TX_ADDR and not pkt.is_read:
            self._tx_bytes.append(byte_val)
            self._refresh(self._tx_view, self._tx_bytes)
        elif pkt.addr == self.UART_RX_ADDR and pkt.is_read:
            self._rx_bytes.append(byte_val)
            self._refresh(self._rx_view, self._rx_bytes)

    def _refresh(self, view: QTextEdit, buf: bytearray) -> None:
        view.setPlainText(self._format_hex(buf))
        # scroll to bottom
        sb = view.verticalScrollBar()
        if sb:
            sb.setValue(sb.maximum())

    @staticmethod
    def _format_hex(buf: bytearray, width: int = 16) -> str:
        """Format bytearray as a hex dump with ASCII annotation."""
        lines: List[str] = []
        for i in range(0, len(buf), width):
            chunk = buf[i:i + width]
            offset = f"{i:04X}"
            hex_part = " ".join(f"{b:02X}" for b in chunk)
            hex_part = hex_part.ljust(width * 3 - 1)
            ascii_part = "".join(chr(b) if 0x20 <= b < 0x7F else "." for b in chunk)
            lines.append(f"{offset}  {hex_part}  |{ascii_part}|")
        return "\n".join(lines)

    def _clear(self) -> None:
        self._tx_bytes.clear()
        self._rx_bytes.clear()
        self._tx_view.clear()
        self._rx_view.clear()


# ---------------------------------------------------------------------------
# Main window
# ---------------------------------------------------------------------------

class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("R1MX Emulator Activity Monitor")
        self.resize(1400, 720)
        self._apply_dark_theme()

        # Central widget & splitter
        central = QWidget()
        self.setCentralWidget(central)
        root_layout = QVBoxLayout(central)
        root_layout.setContentsMargins(4, 4, 4, 4)
        root_layout.setSpacing(4)

        # Top toolbar
        toolbar = self._build_toolbar()
        root_layout.addWidget(toolbar)

        # Main splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        root_layout.addWidget(splitter, 1)

        # Left: device list
        self._dev_panel = DeviceListPanel()
        self._dev_panel.setMinimumWidth(180)
        self._dev_panel.setMaximumWidth(260)
        left_scroll = QScrollArea()
        left_scroll.setWidgetResizable(True)
        left_scroll.setWidget(self._dev_panel)
        left_scroll.setStyleSheet("QScrollArea { border: none; }")
        splitter.addWidget(left_scroll)

        # Centre: event log
        log_container = QWidget()
        log_layout = QVBoxLayout(log_container)
        log_layout.setContentsMargins(0, 0, 0, 0)
        log_layout.setSpacing(2)

        log_hdr = QLabel("EVENT LOG")
        log_hdr.setStyleSheet(
            "font-weight: bold; font-size: 10px; color: #888; padding: 2px 4px;")
        log_layout.addWidget(log_hdr)

        self._log_model = EventLogModel()
        self._log_view = QTableView()
        self._log_view.setModel(self._log_model)
        self._log_view.setShowGrid(False)
        self._log_view.setAlternatingRowColors(False)
        self._log_view.verticalHeader().setVisible(False)
        self._log_view.verticalHeader().setDefaultSectionSize(18)
        self._log_view.setSelectionBehavior(
            QTableView.SelectionBehavior.SelectRows)
        self._log_view.setEditTriggers(
            QTableView.EditTrigger.NoEditTriggers)
        hh = self._log_view.horizontalHeader()
        hh.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        hh.setStretchLastSection(False)
        # Default column widths
        col_widths = [82, 70, 28, 90, 130, 80, 28]
        for i, w in enumerate(col_widths):
            self._log_view.setColumnWidth(i, w)
        hh.setStretchLastSection(True)
        self._log_view.setStyleSheet(
            "QTableView { background: #0d1117; color: #e6edf3;"
            " selection-background-color: #1f3a6e; }")

        log_layout.addWidget(self._log_view, 1)
        splitter.addWidget(log_container)

        # Right: UART monitor
        self._uart_monitor = UartMonitor()
        self._uart_monitor.setMinimumWidth(200)
        splitter.addWidget(self._uart_monitor)

        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 3)
        splitter.setStretchFactor(2, 1)
        splitter.setSizes([200, 900, 300])

        # Status bar
        self._status_bar = QStatusBar()
        self.setStatusBar(self._status_bar)
        self._conn_label = QLabel("Disconnected")
        self._conn_label.setStyleSheet("color: #f44; font-size: 11px;")
        self._status_bar.addPermanentWidget(self._conn_label)
        self._events_label = QLabel("Events: 0")
        self._status_bar.addWidget(self._events_label)

        # Scroll-to-bottom timer — avoid scrolling on every packet
        self._scroll_timer = QTimer(self)
        self._scroll_timer.setInterval(100)
        self._scroll_timer.timeout.connect(self._scroll_to_bottom)
        self._scroll_timer.start()

        self._event_count = 0
        self._auto_scroll = True

        # Start broker thread
        self._thread = BrokerThread(self)
        self._thread.packet_received.connect(self._on_packet)
        self._thread.status_changed.connect(self._on_status)
        self._thread.start()

    def _build_toolbar(self) -> QWidget:
        bar = QWidget()
        bar.setFixedHeight(32)
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        title = QLabel("R1MX Device Monitor")
        title.setStyleSheet("font-weight: bold; font-size: 13px;")
        layout.addWidget(title)

        layout.addStretch()

        self._scroll_btn = QPushButton("↓ Auto-scroll ON")
        self._scroll_btn.setCheckable(True)
        self._scroll_btn.setChecked(True)
        self._scroll_btn.setFixedWidth(130)
        self._scroll_btn.clicked.connect(self._toggle_scroll)
        layout.addWidget(self._scroll_btn)

        clear_btn = QPushButton("Clear log")
        clear_btn.setFixedWidth(80)
        clear_btn.clicked.connect(self._clear_log)
        layout.addWidget(clear_btn)

        return bar

    def _toggle_scroll(self) -> None:
        self._auto_scroll = self._scroll_btn.isChecked()
        self._scroll_btn.setText(
            "↓ Auto-scroll ON" if self._auto_scroll else "↓ Auto-scroll OFF")

    def _clear_log(self) -> None:
        self._log_model.clear()
        self._dev_panel.reset_counters()
        self._event_count = 0
        self._events_label.setText("Events: 0")

    def _on_packet(self, pkt: ActivityPacket) -> None:
        self._log_model.append(pkt)
        self._dev_panel.update_device(pkt)
        self._uart_monitor.handle_packet(pkt)
        self._event_count += 1
        self._events_label.setText(f"Events: {self._event_count}")

    def _on_status(self, msg: str) -> None:
        is_connected = msg.startswith("Connected")
        self._conn_label.setText(msg)
        self._conn_label.setStyleSheet(
            "color: #4f4; font-size: 11px;"
            if is_connected else
            "color: #f44; font-size: 11px;"
        )

    def _scroll_to_bottom(self) -> None:
        if self._auto_scroll and self._log_model.rowCount() > 0:
            last = self._log_model.index(self._log_model.rowCount() - 1, 0)
            self._log_view.scrollTo(last)

    def closeEvent(self, event) -> None:  # type: ignore[override]
        self._thread.stop()
        self._thread.wait(2000)
        super().closeEvent(event)

    @staticmethod
    def _apply_dark_theme() -> None:
        app = QApplication.instance()
        if app is None:
            return
        palette = QPalette()
        bg   = QColor("#0d1117")
        bg2  = QColor("#161b22")
        fg   = QColor("#e6edf3")
        sel  = QColor("#1f3a6e")
        bdr  = QColor("#30363d")
        palette.setColor(QPalette.ColorRole.Window,          bg)
        palette.setColor(QPalette.ColorRole.WindowText,      fg)
        palette.setColor(QPalette.ColorRole.Base,            bg2)
        palette.setColor(QPalette.ColorRole.AlternateBase,   bg)
        palette.setColor(QPalette.ColorRole.ToolTipBase,     bg2)
        palette.setColor(QPalette.ColorRole.ToolTipText,     fg)
        palette.setColor(QPalette.ColorRole.Text,            fg)
        palette.setColor(QPalette.ColorRole.Button,          bg2)
        palette.setColor(QPalette.ColorRole.ButtonText,      fg)
        palette.setColor(QPalette.ColorRole.Highlight,       sel)
        palette.setColor(QPalette.ColorRole.HighlightedText, fg)
        app.setPalette(palette)
        app.setStyleSheet(
            "QHeaderView::section {"
            "  background-color: #161b22; color: #8b949e;"
            "  border: none; border-bottom: 1px solid #30363d;"
            "  padding: 3px 6px; font-size: 11px; }"
            "QPushButton {"
            "  background-color: #21262d; color: #e6edf3;"
            "  border: 1px solid #30363d; border-radius: 4px;"
            "  padding: 3px 10px; }"
            "QPushButton:hover { background-color: #30363d; }"
            "QPushButton:checked { background-color: #1f3a6e;"
            "  border-color: #3a82f7; }"
            "QScrollArea { border: 1px solid #30363d; }"
            "QSplitter::handle { background: #30363d; }"
        )


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    app = QApplication(sys.argv)
    app.setApplicationName("R1MX Activity Monitor")
    win = MainWindow()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
