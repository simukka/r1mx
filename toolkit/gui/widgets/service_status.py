"""
service_status.py — Status-bar indicator dots for background services.

Shows three colored bullet characters in the toolbar / status bar:

    ● Indexer   ● ChromaDB   ● Ollama

Each dot is:
    ●  green  (#4caf50)  — service is up and healthy
    ●  yellow (#e6b400)  — service is starting / unknown
    ●  red    (#f44336)  — service is down or unreachable

Usage
-----
    bar = ServiceStatusBar(parent=self)
    self._status.addPermanentWidget(bar)

    # Slot receives dict[str, str] emitted by ServiceMonitor
    monitor.statusChanged.connect(bar.update_services)

    # IndexerWorker signals
    indexer.statusChanged.connect(bar.update_indexer)
"""

from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QWidget

# ---------------------------------------------------------------------------
# Colour constants
# ---------------------------------------------------------------------------

_GREEN  = "#4caf50"
_YELLOW = "#e6b400"
_RED    = "#f44336"
_GREY   = "#888888"

_COLOR_FOR_STATUS = {
    "up":       _GREEN,
    "starting": _YELLOW,
    "down":     _RED,
    "running":  _GREEN,
    "idle":     _GREY,
    "error":    _RED,
}


# ---------------------------------------------------------------------------
# ServiceDot — a single colored ● label
# ---------------------------------------------------------------------------

class ServiceDot(QLabel):
    """A colored bullet ``●`` that indicates one service's health."""

    def __init__(self, label: str, parent=None):
        super().__init__(parent)
        self._label = label
        self._status = "starting"
        self._refresh()

    def set_status(self, status: str) -> None:
        """Update the dot. *status* must be one of the keys in ``_COLOR_FOR_STATUS``."""
        if status == self._status:
            return
        self._status = status
        self._refresh()

    def _refresh(self) -> None:
        color = _COLOR_FOR_STATUS.get(self._status, _GREY)
        self.setText(f"● {self._label}")
        self.setStyleSheet(
            f"color: {color}; margin-left: 6px; margin-right: 2px;"
        )
        self.setToolTip(f"{self._label}: {self._status}")


# ---------------------------------------------------------------------------
# ServiceStatusBar — composite widget with all dots
# ---------------------------------------------------------------------------

class ServiceStatusBar(QWidget):
    """Compact status indicator strip for the main window status bar.

    Contains dots for: Indexer, ChromaDB, Ollama.
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 8, 0)
        layout.setSpacing(0)

        self._indexer  = ServiceDot("Indexer",  self)
        self._chromadb = ServiceDot("ChromaDB", self)
        self._ollama   = ServiceDot("Ollama",   self)

        layout.addWidget(self._indexer)
        layout.addWidget(self._chromadb)
        layout.addWidget(self._ollama)

    # ── Slots ────────────────────────────────────────────────────────────────

    def update_services(self, status: dict) -> None:
        """Slot for ``ServiceMonitor.statusChanged(dict)``.

        *status* keys: ``"chromadb"``, ``"ollama"`` — values: ``"up" | "starting" | "down"``
        """
        if "chromadb" in status:
            self._chromadb.set_status(status["chromadb"])
        if "ollama" in status:
            self._ollama.set_status(status["ollama"])

    def update_indexer(self, status: str) -> None:
        """Slot for ``DatasheetIndexWorker.statusChanged(str)``.

        *status*: ``"idle" | "running" | "error"``
        """
        self._indexer.set_status(status)

    # ── Read-only properties (for testing) ───────────────────────────────────

    @property
    def chromadb_status(self) -> str:
        return self._chromadb._status

    @property
    def ollama_status(self) -> str:
        return self._ollama._status

    @property
    def indexer_status(self) -> str:
        return self._indexer._status
