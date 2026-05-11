"""FootprintPickerDialog — Browse KiCad footprint libraries and pick a footprint.

The dialog shows:
  • A search QLineEdit (queries name / library / tags)
  • An optional pin-count QSpinBox
  • A QListWidget results list ("Library / Name  [N pads]")
  • A QPainter preview canvas (draws pads to scale in mm)
  • "Use this footprint" accept button

On accept, ``selected_footprint`` holds the ``KicadFootprint`` with pads loaded.
"""

from __future__ import annotations

from typing import Optional

from PyQt6.QtCore import QSize, Qt, QTimer
from PyQt6.QtGui import QBrush, QColor, QPainter, QPen
from PyQt6.QtWidgets import (
    QCheckBox,
    QDialog,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QSizePolicy,
    QSpinBox,
    QSplitter,
    QVBoxLayout,
    QWidget,
    QLineEdit,
)

from toolkit.analysis.kicad_footprint import (
    KicadFootprint,
    build_index,
    load_pads,
    search_index,
)


# ─── Preview canvas ───────────────────────────────────────────────────────────

class _FootprintPreview(QWidget):
    """QPainter canvas that draws KiCad pads to scale."""

    _MARGIN_PX = 20

    def __init__(self, parent=None):
        super().__init__(parent)
        self._fp: Optional[KicadFootprint] = None
        self.setMinimumSize(200, 200)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setStyleSheet("background: #1e1e1e;")

    def set_footprint(self, fp: Optional[KicadFootprint]) -> None:
        self._fp = fp
        self.update()

    def sizeHint(self) -> QSize:
        return QSize(300, 300)

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        bg = QColor("#1e1e1e")
        painter.fillRect(self.rect(), bg)

        if not self._fp or not self._fp.pads:
            painter.setPen(QColor("#555"))
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, "No footprint selected")
            return

        pads = self._fp.pads
        w, h = self.width(), self.height()
        m = self._MARGIN_PX

        # Bounding box in mm
        xs = [p.x_mm - p.w_mm / 2 for p in pads] + [p.x_mm + p.w_mm / 2 for p in pads]
        ys = [p.y_mm - p.h_mm / 2 for p in pads] + [p.y_mm + p.h_mm / 2 for p in pads]
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)
        span_x = max(max_x - min_x, 0.5)
        span_y = max(max_y - min_y, 0.5)

        # Scale to fit canvas with margins
        scale_x = (w - 2 * m) / span_x
        scale_y = (h - 2 * m) / span_y
        scale = min(scale_x, scale_y)

        def to_px(mm_x: float, mm_y: float):
            px = m + (mm_x - min_x) * scale
            py = m + (mm_y - min_y) * scale
            return px, py

        pad_fill   = QColor("#f5a623")
        pad_stroke = QColor("#c07d18")
        text_col   = QColor("#1e1e1e")

        for pad in pads:
            cx, cy = to_px(pad.x_mm, pad.y_mm)
            pw = max(pad.w_mm * scale, 4)
            ph = max(pad.h_mm * scale, 4)

            painter.setPen(QPen(pad_stroke, 1))
            painter.setBrush(QBrush(pad_fill))

            if pad.shape in ("circle", "oval"):
                painter.drawEllipse(
                    int(cx - pw / 2), int(cy - ph / 2), int(pw), int(ph)
                )
            else:
                painter.drawRect(
                    int(cx - pw / 2), int(cy - ph / 2), int(pw), int(ph)
                )

            # Draw pad number
            if pw > 10 and pad.number:
                painter.setPen(QPen(text_col))
                painter.setFont(self.font())
                painter.drawText(
                    int(cx - pw / 2), int(cy - ph / 2), int(pw), int(ph),
                    Qt.AlignmentFlag.AlignCenter,
                    str(pad.number),
                )

        painter.end()


# ─── Dialog ───────────────────────────────────────────────────────────────────

class FootprintPickerDialog(QDialog):
    """Browse KiCad footprint libraries and select a footprint.

    Usage::

        dlg = FootprintPickerDialog(initial_query="SOIC-8", parent=self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            fp = dlg.selected_footprint  # KicadFootprint with pads loaded
    """

    def __init__(
        self,
        initial_query: str = "",
        initial_pin_count: int = 0,
        parent=None,
    ):
        super().__init__(parent)
        self.setWindowTitle("KiCad Footprint Library Picker")
        self.setMinimumSize(700, 500)
        self.setSizeGripEnabled(True)
        self.resize(900, 600)

        self.selected_footprint: Optional[KicadFootprint] = None

        self._index: list[KicadFootprint] = []
        self._debounce = QTimer(self)
        self._debounce.setSingleShot(True)
        self._debounce.timeout.connect(self._run_search)

        self._build_ui(initial_query, initial_pin_count)
        self._load_index()

    # ── UI construction ───────────────────────────────────────────────────────

    def _build_ui(self, initial_query: str, initial_pin_count: int) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(8, 8, 8, 8)
        root.setSpacing(6)

        # ── Search bar ──────────────────────────────────────────────────────
        search_row = QHBoxLayout()
        search_row.addWidget(QLabel("Search:"))

        self._search = QLineEdit()
        self._search.setPlaceholderText("e.g. SOIC-8, QFP-32, BGA …")
        self._search.setText(initial_query)
        self._search.textChanged.connect(self._on_query_changed)
        search_row.addWidget(self._search, stretch=1)

        self._pin_check = QCheckBox("Pin count:")
        self._pin_check.setChecked(initial_pin_count > 0)
        self._pin_check.toggled.connect(self._on_query_changed)
        search_row.addWidget(self._pin_check)

        self._pin_spin = QSpinBox()
        self._pin_spin.setRange(1, 1024)
        self._pin_spin.setValue(max(initial_pin_count, 1))
        self._pin_spin.setEnabled(initial_pin_count > 0)
        self._pin_spin.valueChanged.connect(self._on_query_changed)
        self._pin_check.toggled.connect(self._pin_spin.setEnabled)
        search_row.addWidget(self._pin_spin)

        root.addLayout(search_row)

        # ── Status label ────────────────────────────────────────────────────
        self._status = QLabel("Loading index…")
        self._status.setStyleSheet("color: #888; font-size: 11px;")
        root.addWidget(self._status)

        # ── Main split: list ↔ preview ────────────────────────────────────
        splitter = QSplitter(Qt.Orientation.Horizontal)

        self._results = QListWidget()
        self._results.currentItemChanged.connect(self._on_selection_changed)
        self._results.itemDoubleClicked.connect(self._accept_selected)
        splitter.addWidget(self._results)

        self._preview = _FootprintPreview()
        splitter.addWidget(self._preview)
        splitter.setSizes([380, 320])

        root.addWidget(splitter, stretch=1)

        # ── Buttons ──────────────────────────────────────────────────────────
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        self._use_btn = QPushButton("📦 Use this footprint")
        self._use_btn.setEnabled(False)
        self._use_btn.setDefault(True)
        self._use_btn.clicked.connect(self._accept_selected)
        btn_row.addWidget(self._use_btn)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        btn_row.addWidget(cancel_btn)
        root.addLayout(btn_row)

    # ── Index loading ─────────────────────────────────────────────────────────

    def _load_index(self) -> None:
        """Build index (runs synchronously; ~0.3 s on a typical install)."""
        self._index = build_index()
        count = len(self._index)
        self._status.setText(f"{count:,} footprints in {self._unique_library_count()} libraries")
        # Trigger initial search with the pre-filled query
        self._run_search()

    def _unique_library_count(self) -> int:
        return len({fp.library for fp in self._index})

    # ── Search ────────────────────────────────────────────────────────────────

    def _on_query_changed(self) -> None:
        self._debounce.start(150)

    def _run_search(self) -> None:
        query = self._search.text().strip()
        pin = self._pin_spin.value() if self._pin_check.isChecked() else None

        results = search_index(self._index, query, pin_count=pin, max_results=300)

        self._results.clear()
        for fp in results:
            text = f"{fp.library} / {fp.name}"
            item = QListWidgetItem(text)
            item.setData(Qt.ItemDataRole.UserRole, fp)
            item.setToolTip(fp.description or fp.name)
            self._results.addItem(item)

        count = len(results)
        total = len(self._index)
        self._status.setText(
            f"Showing {count} of {total:,} footprints"
            + (f' matching "{query}"' if query else "")
        )
        self._use_btn.setEnabled(False)
        self._preview.set_footprint(None)

    # ── Selection ─────────────────────────────────────────────────────────────

    def _on_selection_changed(
        self, current: QListWidgetItem | None, _previous
    ) -> None:
        if current is None:
            self._preview.set_footprint(None)
            self._use_btn.setEnabled(False)
            return

        stub: KicadFootprint = current.data(Qt.ItemDataRole.UserRole)
        fp = load_pads(stub)
        # Update item label with pad count now that pads are loaded
        current.setText(f"{fp.library} / {fp.name}  [{len(fp.pads)} pads]")
        current.setData(Qt.ItemDataRole.UserRole, fp)
        self._preview.set_footprint(fp)
        self._use_btn.setEnabled(True)

    # ── Accept ────────────────────────────────────────────────────────────────

    def _accept_selected(self, *_) -> None:
        item = self._results.currentItem()
        if item is None:
            return
        fp: KicadFootprint = item.data(Qt.ItemDataRole.UserRole)
        if not fp.pads:
            fp = load_pads(fp)
        self.selected_footprint = fp
        self.accept()
