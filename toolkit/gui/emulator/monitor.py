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

from toolkit.gui.widgets.status_lcd import StatusLCDWidget
from toolkit.gui.emulator.device import DeviceListPanel
from toolkit.gui.emulator.uart import UartMonitor
from toolkit.gui.emulator.broker import BrokerThread, ActivityPacket
from toolkit.gui.emulator.eventlog import EventLogModel

@dataclass
class DeviceState:
    dev_id:      int
    read_count:  int = 0
    write_count: int = 0
    last_read:   float = 0.0   # host monotonic time of last read
    last_write:  float = 0.0   # host monotonic time of last write


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("R1MX Activity Monitor")
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

        # Right: UART monitor + Status LCD (vertical split)
        self._uart_monitor = UartMonitor()
        self._lcd_widget = StatusLCDWidget(parent=self)

        right_splitter = QSplitter(Qt.Orientation.Vertical)
        right_splitter.addWidget(self._uart_monitor)
        right_splitter.addWidget(self._lcd_widget)
        right_splitter.setStretchFactor(0, 2)
        right_splitter.setStretchFactor(1, 1)
        right_splitter.setSizes([400, 200])
        right_splitter.setMinimumWidth(200)
        splitter.addWidget(right_splitter)

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

        self._recv_count = 0
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
        self._recv_count = 0
        self._events_label.setText("RECV: 0")

    def _on_packet(self, pkt: ActivityPacket) -> None:
        # TODO: this is too slow. we need to buffer incoming packets
        # self._log_model.append(pkt)
        self._dev_panel.update_device(pkt)
        self._uart_monitor.handle_packet(pkt)
        self._recv_count += pkt.size
        self._events_label.setText(f"RECV: {self._recv_count}")

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
        self._lcd_widget._receiver.stop()
        self._lcd_widget._receiver.wait(2000)
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
