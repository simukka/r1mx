"""FootprintPickerDialog — Browse KiCad footprint libraries and pick a footprint.

The dialog shows:
  • An optional "📄 Datasheet suggests:" banner with clickable hint chips
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
    QFrame,
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
from toolkit.analysis.datasheet_package import PackageHint
from toolkit.analysis.footprint_match import (
    DatasheetDimensions,
    extract_datasheet_dimensions,
    extract_kicad_dimensions,
    score_match,
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

        hints = extract_package_hints(pdf_path)
        dlg = FootprintPickerDialog(initial_query="SOIC-8", hints=hints, parent=self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            fp = dlg.selected_footprint  # KicadFootprint with pads loaded
    """

    def __init__(
        self,
        initial_query: str = "",
        initial_pin_count: int = 0,
        hints: list[PackageHint] | None = None,
        datasheet_pdf: Optional["Path"] = None,
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

        # Pre-extract datasheet dimensions once (if a PDF is available)
        self._ds_dims: Optional[DatasheetDimensions] = None
        if datasheet_pdf is not None:
            self._ds_dims = self._load_datasheet_dims(datasheet_pdf)

        # If no query is pre-filled, auto-apply the top hint
        if not initial_query.strip() and hints:
            top = hints[0]
            initial_query = top.kicad_query
            if top.pin_count and not initial_pin_count:
                initial_pin_count = top.pin_count

        self._build_ui(initial_query, initial_pin_count, hints or [])
        self._load_index()

    # ── UI construction ───────────────────────────────────────────────────────

    def _build_ui(
        self,
        initial_query: str,
        initial_pin_count: int,
        hints: list[PackageHint],
    ) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(8, 8, 8, 8)
        root.setSpacing(6)

        # ── Datasheet hints banner ──────────────────────────────────────────
        if hints:
            self._hints_frame = QFrame()
            self._hints_frame.setFrameShape(QFrame.Shape.StyledPanel)
            self._hints_frame.setStyleSheet(
                "QFrame { background: #1e3a2a; border: 1px solid #2e6a4a; border-radius: 4px; }"
            )
            hints_layout = QHBoxLayout(self._hints_frame)
            hints_layout.setContentsMargins(6, 4, 6, 4)
            hints_layout.setSpacing(6)

            lbl = QLabel("📄 Datasheet suggests:")
            lbl.setStyleSheet("color: #7fd6a8; font-size: 11px; font-weight: bold; background: none; border: none;")
            hints_layout.addWidget(lbl)

            for hint in hints[:3]:
                pin_str = f"  {hint.pin_count}p" if hint.pin_count else ""
                chip_text = f"{hint.name}{pin_str}"
                chip = QPushButton(chip_text)
                chip.setToolTip(
                    f'Apply: search="{hint.kicad_query}", pin_count={hint.pin_count or "any"}'
                    f"  (confidence {hint.confidence:.0%})"
                )
                chip.setStyleSheet(
                    "QPushButton { background: #2e6a4a; color: #d4f5e4; border: 1px solid #4caf80; "
                    "border-radius: 3px; padding: 2px 8px; font-size: 11px; }"
                    "QPushButton:hover { background: #3d8a62; }"
                )
                chip.setCheckable(False)
                chip.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
                # Capture hint in closure
                chip.clicked.connect(lambda _checked, h=hint: self._apply_hint(h))
                hints_layout.addWidget(chip)

            hints_layout.addStretch()
            root.addWidget(self._hints_frame)
        else:
            self._hints_frame = None

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

        # ── Match score bar (shown when datasheet PDF provided) ───────────────
        self._match_label = QLabel("")
        self._match_label.setWordWrap(True)
        self._match_label.setStyleSheet("font-size: 11px; padding: 2px 0;")
        self._match_label.setVisible(self._ds_dims is not None)
        root.addWidget(self._match_label)

        # ── Buttons ────────────────────────────────────────────────────────────
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

    @staticmethod
    def _load_datasheet_dims(pdf_path) -> Optional[DatasheetDimensions]:
        """Extract DatasheetDimensions from *pdf_path* (up to 30 pages).

        Returns ``None`` on any error so the dialog still opens.
        """
        try:
            from toolkit.analysis.datasheet_package import _pdf_to_text
            text = _pdf_to_text(pdf_path, max_pages=30)
            if text.strip():
                return extract_datasheet_dimensions(text)
        except Exception:
            pass
        return None

    # ── Hint chips ────────────────────────────────────────────────────────────

    def _apply_hint(self, hint: PackageHint) -> None:
        """Apply a datasheet hint chip: set search text and optional pin count."""
        self._search.setText(hint.kicad_query)
        if hint.pin_count:
            self._pin_check.setChecked(True)
            self._pin_spin.setValue(hint.pin_count)
        else:
            self._pin_check.setChecked(False)

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
            self._update_match_label(None)
            return

        stub: KicadFootprint = current.data(Qt.ItemDataRole.UserRole)
        fp = load_pads(stub)
        # Update item label with pad count now that pads are loaded
        current.setText(f"{fp.library} / {fp.name}  [{len(fp.pads)} pads]")
        current.setData(Qt.ItemDataRole.UserRole, fp)
        self._preview.set_footprint(fp)
        self._use_btn.setEnabled(True)
        self._update_match_label(fp)

    def _update_match_label(self, fp: Optional[KicadFootprint]) -> None:
        """Compute and display the datasheet cross-reference score."""
        if self._ds_dims is None or fp is None:
            if self._ds_dims is None:
                self._match_label.setVisible(False)
            return

        fp_dims = extract_kicad_dimensions(fp)
        result  = score_match(fp_dims, self._ds_dims)

        if not result.has_data:
            self._match_label.setText("📐 Datasheet match: no dimension data found in PDF")
            self._match_label.setStyleSheet("font-size: 11px; color: #888; padding: 2px 0;")
            self._match_label.setVisible(True)
            return

        pct = int(result.total * 100)
        if pct >= 80:
            colour = "#4caf50"
            icon   = "✅"
        elif pct >= 50:
            colour = "#ff9800"
            icon   = "⚠️"
        else:
            colour = "#f44336"
            icon   = "❌"

        summary = f"{icon} Datasheet match: {pct}%"
        breakdown = "  |  ".join(result.details)
        self._match_label.setText(f"{summary}  —  {breakdown}")
        self._match_label.setStyleSheet(
            f"font-size: 11px; color: {colour}; padding: 2px 0;"
        )
        self._match_label.setVisible(True)

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
