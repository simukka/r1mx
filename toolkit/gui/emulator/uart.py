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
    QComboBox,
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

from toolkit.gui.emulator.consts import DEV_UART
from toolkit.gui.emulator.broker import ActivityPacket

class UartMonitor(QWidget):
    """Shows TX (writes to TX_FIFO) and RX (reads from RX_FIFO) byte streams."""

    UART_TX_ADDR    = 0xE060_0004
    UART_RX_ADDR    = 0xE060_0000
    _MAX_UART_BYTES = 65536        # cap per direction; ~64 KB

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setSpacing(4)
        layout.setContentsMargins(4, 4, 4, 4)

        hdr = QLabel("UART MONITOR")
        hdr.setStyleSheet("font-weight: bold; font-size: 10px; color: #888;")
        layout.addWidget(hdr)

        tx_ctrl = QHBoxLayout()
        tx_ctrl.setSpacing(6)
        tx_hdr = QLabel("TX (firmware → serial)")
        tx_hdr.setStyleSheet("font-size: 10px; color: #f77f3a;")
        tx_ctrl.addWidget(tx_hdr)
        tx_ctrl.addStretch()
        self._tx_mode_combo = QComboBox()
        self._tx_mode_combo.addItems(["Hex+ASCII", "ASCII"])
        self._tx_mode_combo.setFixedWidth(90)
        self._tx_mode_combo.setStyleSheet("font-size: 10px;")
        self._tx_mode_combo.currentTextChanged.connect(self._on_tx_mode_changed)
        tx_ctrl.addWidget(self._tx_mode_combo)
        layout.addLayout(tx_ctrl)

        self._tx_view = QTextEdit()
        self._tx_view.setReadOnly(True)
        self._tx_view.setFont(self._mono_font())
        self._tx_view.setStyleSheet(
            "background:#0d1117; color:#e6edf3; font-size:11px;")
        self._tx_view.setMaximumHeight(500)
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
        self._tx_mode:  str  = "hex"
        self._tx_dirty: bool = False
        self._rx_dirty: bool = False

        # Batch display refreshes at 100 ms to avoid an O(n) setPlainText
        # call on every single byte at high UART baud rates.
        self._uart_timer = QTimer(self)
        self._uart_timer.setInterval(100)
        self._uart_timer.timeout.connect(self._flush_uart)
        self._uart_timer.start()

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
            if len(self._tx_bytes) > self._MAX_UART_BYTES:
                del self._tx_bytes[:-self._MAX_UART_BYTES]
            self._tx_dirty = True
        elif pkt.addr == self.UART_RX_ADDR and pkt.is_read:
            self._rx_bytes.append(byte_val)
            if len(self._rx_bytes) > self._MAX_UART_BYTES:
                del self._rx_bytes[:-self._MAX_UART_BYTES]
            self._rx_dirty = True

    def _flush_uart(self) -> None:
        """Timer-driven display refresh; batches updates to avoid O(n) work per byte."""
        if self._tx_dirty:
            self._refresh(self._tx_view, self._tx_bytes, self._tx_mode)
            self._tx_dirty = False
        if self._rx_dirty:
            self._refresh(self._rx_view, self._rx_bytes)
            self._rx_dirty = False

    def _refresh(self, view: QTextEdit, buf: bytearray, mode: str = "hex") -> None:
        if mode == "ascii":
            text = self._format_ascii(buf)
        else:
            text = self._format_hex(buf)
        view.setPlainText(text)
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

    @staticmethod
    def _format_ascii(buf: bytearray) -> str:
        """Render the byte stream as plain text.

        CR (0x0D) is dropped; LF (0x0A) becomes a newline so that the usual
        CR+LF pairs from VxWorks/UART output show as single newlines.  All
        other non-printable bytes are replaced with a period.
        """
        result: List[str] = []
        for b in buf:
            if b == 0x0A:
                result.append("\n")
            elif b == 0x0D:
                pass
            elif 0x20 <= b < 0x7F:
                result.append(chr(b))
            else:
                result.append(".")
        return "".join(result)

    def _on_tx_mode_changed(self, text: str) -> None:
        self._tx_mode = "ascii" if text == "ASCII" else "hex"
        self._refresh(self._tx_view, self._tx_bytes, self._tx_mode)

    def _clear(self) -> None:
        self._tx_bytes.clear()
        self._rx_bytes.clear()
        self._tx_dirty = False
        self._rx_dirty = False
        self._tx_view.clear()
        self._rx_view.clear()
