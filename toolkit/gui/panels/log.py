"""Workflow log panel."""
from __future__ import annotations

from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QProgressBar, QTextEdit, QVBoxLayout, QWidget

class WorkflowLog(QWidget):
    """Bottom dock: output log + progress bar."""

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 2, 4, 2)

        self._log = QTextEdit()
        self._log.setReadOnly(True)
        self._log.setFont(QFont("monospace", 9))
        self._log.setMaximumHeight(160)
        layout.addWidget(self._log)

        self._bar = QProgressBar()
        self._bar.setRange(0, 0)   # indeterminate by default
        self._bar.setVisible(False)
        layout.addWidget(self._bar)

    def append(self, line: str):
        self._log.append(line)
        self._log.verticalScrollBar().setValue(
            self._log.verticalScrollBar().maximum()
        )

    def clear(self):
        self._log.clear()

    def set_busy(self, busy: bool):
        self._bar.setVisible(busy)

    def set_progress(self, val: int, total: int):
        self._bar.setRange(0, total)
        self._bar.setValue(val)
        self._bar.setVisible(True)


