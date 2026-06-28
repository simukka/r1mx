from __future__ import annotations

from typing import Dict, Optional

from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QVBoxLayout,
    QWidget,
)

from toolkit.gui.emulator.consts import DEVICE_INFO
from toolkit.gui.emulator.led import LedWidget, _LED_READ, _LED_WRITE
from toolkit.gui.emulator.broker import ActivityPacket

class DeviceListPanel(QWidget):
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._leds:     Dict[int, LedWidget] = {}
        self._r_lbls:   Dict[int, QLabel]    = {}
        self._w_lbls:   Dict[int, QLabel]    = {}
        self._r_counts: Dict[int, int]       = {}
        self._w_counts: Dict[int, int]       = {}

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

            self._r_counts[dev_id] = 0
            self._w_counts[dev_id] = 0
            row.addStretch()
            layout.addLayout(row)

        layout.addStretch()

    def update_device(self, pkt: ActivityPacket) -> None:
        led = self._leds.get(pkt.dev_id)
        if led is None:
            return
        if pkt.is_read:
            led.flash(_LED_READ)
            self._r_counts[pkt.dev_id] += 1
            self._r_lbls[pkt.dev_id].setText(f"R:{self._r_counts[pkt.dev_id]}")
        else:
            led.flash(_LED_WRITE)
            self._w_counts[pkt.dev_id] += 1
            self._w_lbls[pkt.dev_id].setText(f"W:{self._w_counts[pkt.dev_id]}")

    def reset_counters(self) -> None:
        for dev_id in DEVICE_INFO:
            self._r_counts[dev_id] = 0
            self._w_counts[dev_id] = 0
            if dev_id in self._r_lbls:
                self._r_lbls[dev_id].setText("R:0")
                self._w_lbls[dev_id].setText("W:0")
