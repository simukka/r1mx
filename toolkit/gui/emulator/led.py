from __future__ import annotations

import time
from typing import Optional

from PyQt6.QtCore import (
    Qt,
    QTimer,
)
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import (
    QWidget
)

from toolkit.gui.widgets.status_lcd import StatusLCDWidget

_LED_OFF   = QColor("#2a2a2a")
_LED_READ  = QColor("#3a82f7")   # blue
_LED_WRITE = QColor("#f77f3a")   # orange
_LED_FADE  = 0.20                # seconds until LED fades


class LedWidget(QWidget):
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setFixedSize(14, 14)
        self._color    = _LED_OFF
        self._deadline: float = 0.0
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
