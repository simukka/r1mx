"""
pinout_wizard.py — DatasheetPinoutWizard

Two-step modal dialog for extracting a component pinout from a linked datasheet.

Step 0 – Region Select
    • Page through the PDF with prev/next buttons.
    • Hover over the page image → crosshair cursor.
    • Drag to draw a rubber-band bounding box around the pinout diagram.
    • The selection is shown as a semi-transparent yellow overlay.
    • "Next →" is enabled once a region has been drawn.

Step 1 – Review & Fix
    • Shows the cropped image with detected pads overlaid as coloured circles.
    • Click a pad to select it; edit its pin_number and label in the side panel.
    • "Re-detect" re-runs the OpenCV + OCR pipeline on the same crop.
    • "← Back" returns to Step 0 to redraw the region.
    • "Confirm" closes the dialog with ``result`` populated.

Result
------
``wizard.result`` is a ``PinoutResult`` (or None if cancelled).
``wizard.datasheet_id`` is the DB datasheet id (passed in by the caller).
"""

from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path

import cv2
import numpy as np

from PyQt6.QtCore import (
    QPoint, QRect, QRectF, QSize, Qt,
    pyqtSignal,
)
from PyQt6.QtGui import (
    QColor, QCursor, QFont, QImage, QMouseEvent, QPainter,
    QPen, QPixmap,
)
from PyQt6.QtWidgets import (
    QComboBox,
    QDialog,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QSplitter,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from toolkit.analysis.pinout import (
    BBox,
    PadDetection,
    PinoutResult,
    extract_pinout,
)


# ─── PDF page rendering helper ────────────────────────────────────────────────

def _render_page_to_pixmap(pdf_path: Path, page: int, dpi: int = 130) -> QPixmap | None:
    with tempfile.TemporaryDirectory() as tmpdir:
        out = Path(tmpdir) / "p"
        try:
            subprocess.run(
                ["pdftoppm", "-r", str(dpi), "-png", "-singlefile",
                 "-f", str(page), "-l", str(page), str(pdf_path), str(out)],
                capture_output=True, timeout=20,
            )
        except Exception:
            return None
        png = Path(tmpdir) / "p.png"
        if not png.exists():
            return None
        px = QPixmap(str(png))
        return px if not px.isNull() else None


def _count_pages(pdf_path: Path) -> int:
    try:
        r = subprocess.run(["pdfinfo", str(pdf_path)], capture_output=True,
                           text=True, timeout=10)
        for line in r.stdout.splitlines():
            if line.startswith("Pages:"):
                return int(line.split(":", 1)[1].strip())
    except Exception:
        pass
    return 1


# ─── Step 0 widget: PDF page with rubber-band selection ──────────────────────

class _PageWidget(QLabel):
    """QLabel that shows a rendered PDF page and lets the user draw a bbox."""

    regionSelected = pyqtSignal(QRect)   # pixel-space rect in the *displayed* image

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self.setCursor(QCursor(Qt.CursorShape.CrossCursor))
        self.setMouseTracking(True)

        self._origin:    QPoint | None = None
        self._selection: QRect | None  = None   # current rubber-band rect
        self._confirmed: QRect | None  = None   # last confirmed selection

    def clear_selection(self) -> None:
        self._confirmed = None
        self._selection = None
        self.update()

    @property
    def confirmed_selection(self) -> QRect | None:
        return self._confirmed

    # ── Mouse events ─────────────────────────────────────────────────────────

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self._origin    = event.pos()
            self._selection = QRect(self._origin, self._origin)
            self.update()

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if self._origin is not None:
            self._selection = QRect(self._origin, event.pos()).normalized()
            self.update()

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if self._origin is not None and self._selection is not None:
            rect = QRect(self._origin, event.pos()).normalized()
            if rect.width() > 5 and rect.height() > 5:
                self._confirmed = rect
                self.regionSelected.emit(rect)
            self._origin    = None
            self._selection = None
            self.update()

    # ── Paint ─────────────────────────────────────────────────────────────────

    def paintEvent(self, event) -> None:
        super().paintEvent(event)
        painter = QPainter(self)

        # Draw confirmed selection (semi-transparent yellow fill)
        if self._confirmed:
            painter.setPen(QPen(QColor(255, 200, 0), 2))
            painter.setBrush(QColor(255, 200, 0, 60))
            painter.drawRect(self._confirmed)

        # Draw active rubber-band
        if self._selection:
            painter.setPen(QPen(QColor(255, 255, 0, 200), 1, Qt.PenStyle.DashLine))
            painter.setBrush(QColor(255, 255, 0, 30))
            painter.drawRect(self._selection)

        painter.end()


class _RegionSelectPage(QWidget):
    """Wizard page 0: navigate PDF pages and draw a selection region."""

    regionConfirmed = pyqtSignal()   # selection drawn; "Next" now enabled

    def __init__(self, pdf_path: Path, parent=None):
        super().__init__(parent)
        self._pdf_path    = pdf_path
        self._current_page = 1
        self._total_pages  = _count_pages(pdf_path)
        self._pixmap:      QPixmap | None = None

        layout = QVBoxLayout(self)

        # Instruction bar
        info = QLabel(
            "Draw a bounding box around the pinout / pin table in the datasheet.\n"
            "Use the Prev / Next buttons to navigate pages."
        )
        info.setWordWrap(True)
        info.setStyleSheet("color: #aaa; font-size: 11px;")
        layout.addWidget(info)

        # Page image in scroll area
        self._page_widget = _PageWidget()
        self._page_widget.regionSelected.connect(self._on_region_selected)
        scroll = QScrollArea()
        scroll.setWidget(self._page_widget)
        scroll.setWidgetResizable(False)
        layout.addWidget(scroll, stretch=1)

        # Navigation
        nav_row = QHBoxLayout()
        self._prev_btn = QPushButton("← Prev page")
        self._prev_btn.clicked.connect(self._prev_page)
        nav_row.addWidget(self._prev_btn)

        self._page_lbl = QLabel()
        self._page_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        nav_row.addWidget(self._page_lbl, stretch=1)

        self._next_btn = QPushButton("Next page →")
        self._next_btn.clicked.connect(self._next_page)
        nav_row.addWidget(self._next_btn)

        self._clear_btn = QPushButton("Clear selection")
        self._clear_btn.clicked.connect(self._clear)
        nav_row.addWidget(self._clear_btn)

        layout.addLayout(nav_row)

        self._load_page()

    # ── Navigation ────────────────────────────────────────────────────────────

    def _prev_page(self) -> None:
        if self._current_page > 1:
            self._current_page -= 1
            self._page_widget.clear_selection()
            self._load_page()

    def _next_page(self) -> None:
        if self._current_page < self._total_pages:
            self._current_page += 1
            self._page_widget.clear_selection()
            self._load_page()

    def _clear(self) -> None:
        self._page_widget.clear_selection()

    def _load_page(self) -> None:
        self._page_lbl.setText(f"Page {self._current_page} of {self._total_pages}")
        self._prev_btn.setEnabled(self._current_page > 1)
        self._next_btn.setEnabled(self._current_page < self._total_pages)
        px = _render_page_to_pixmap(self._pdf_path, self._current_page)
        if px:
            self._pixmap = px
            self._page_widget.setPixmap(px)
            self._page_widget.resize(px.size())
        else:
            self._page_widget.setText(f"(Could not render page {self._current_page})")

    def _on_region_selected(self, rect: QRect) -> None:
        self.regionConfirmed.emit()

    # ── Result ────────────────────────────────────────────────────────────────

    def get_rel_bbox(self) -> BBox | None:
        """Return the confirmed selection as a normalised BBox (0–1 relative to page)."""
        sel = self._page_widget.confirmed_selection
        if sel is None or not self._pixmap:
            return None
        pw = self._pixmap.width()
        ph = self._pixmap.height()
        if pw == 0 or ph == 0:
            return None
        return BBox(
            x=max(0.0, sel.x() / pw),
            y=max(0.0, sel.y() / ph),
            w=min(1.0, sel.width() / pw),
            h=min(1.0, sel.height() / ph),
        )

    @property
    def current_page(self) -> int:
        return self._current_page


# ─── Step 1 widget: pad review ───────────────────────────────────────────────

def _ndarray_to_qpixmap(img: np.ndarray) -> QPixmap:
    """Convert a BGR numpy array to QPixmap."""
    h, w = img.shape[:2]
    rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    qimg = QImage(rgb.data, w, h, w * 3, QImage.Format.Format_RGB888)
    return QPixmap.fromImage(qimg.copy())


class _ReviewLabel(QLabel):
    """Pad overlay image.

    Interactions
    ------------
    * Click on a pad      → select it (padClicked)
    * Drag a pad          → move it in real time (padMoved on release)
    * Click on empty area → create a new pad at that position (newPadRequested)
    """

    padClicked      = pyqtSignal(int)          # index of pad that was clicked
    padMoved        = pyqtSignal(int)          # index of pad that was dragged
    newPadRequested = pyqtSignal(float, float) # normalised cx, cy for new pad

    _DRAG_THRESHOLD = 4  # px before a press becomes a drag

    def __init__(self, parent=None):
        super().__init__(parent)
        self._pads:    list[PadDetection] = []
        self._selected: int | None = None
        self.setMouseTracking(True)

        self._press_pos:      QPoint | None = None
        self._drag_pad_idx:   int | None    = None
        self._click_pad_idx:  int | None    = None
        self._dragging:       bool          = False

    def set_result(self, result: PinoutResult, pixmap: QPixmap) -> None:
        self._pads      = result.pads
        self._selected  = None
        self._dragging  = False
        self._drag_pad_idx = None
        self.setPixmap(pixmap)
        self.resize(pixmap.size())
        self.update()

    def select_pad(self, idx: int | None) -> None:
        self._selected = idx
        self.update()

    # ── Mouse ─────────────────────────────────────────────────────────────────

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() != Qt.MouseButton.LeftButton or not self.pixmap():
            return
        self._press_pos      = event.pos()
        self._dragging       = False
        self._click_pad_idx  = self._find_pad_at(event.pos())
        self._drag_pad_idx   = self._click_pad_idx

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        # Update cursor based on hover
        if not self._dragging and self._press_pos is None:
            hover = self._find_pad_at(event.pos())
            self.setCursor(QCursor(
                Qt.CursorShape.SizeAllCursor if hover is not None
                else Qt.CursorShape.CrossCursor
            ))

        if self._press_pos is None or self._drag_pad_idx is None:
            return
        delta = event.pos() - self._press_pos
        if not self._dragging and (
            abs(delta.x()) > self._DRAG_THRESHOLD
            or abs(delta.y()) > self._DRAG_THRESHOLD
        ):
            self._dragging = True

        if self._dragging and self.pixmap():
            pw = self.pixmap().width()
            ph = self.pixmap().height()
            pad = self._pads[self._drag_pad_idx]
            nx = max(0.0, min(1.0, event.pos().x() / pw))
            ny = max(0.0, min(1.0, event.pos().y() / ph))
            pad.bbox = BBox(
                x=nx - pad.bbox.w / 2,
                y=ny - pad.bbox.h / 2,
                w=pad.bbox.w,
                h=pad.bbox.h,
            )
            self.update()

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if event.button() != Qt.MouseButton.LeftButton:
            return
        if self._dragging and self._drag_pad_idx is not None:
            self.padMoved.emit(self._drag_pad_idx)
        elif not self._dragging:
            if self._click_pad_idx is not None:
                self.padClicked.emit(self._click_pad_idx)
            elif self.pixmap():
                pw = self.pixmap().width()
                ph = self.pixmap().height()
                nx = max(0.0, min(1.0, event.pos().x() / pw))
                ny = max(0.0, min(1.0, event.pos().y() / ph))
                self.newPadRequested.emit(nx, ny)
        self._press_pos     = None
        self._drag_pad_idx  = None
        self._click_pad_idx = None
        self._dragging      = False

    # ── Paint ─────────────────────────────────────────────────────────────────

    def paintEvent(self, event) -> None:
        super().paintEvent(event)
        if not self._pads or not self.pixmap():
            return
        pw = self.pixmap().width()
        ph = self.pixmap().height()
        painter = QPainter(self)
        for i, pad in enumerate(self._pads):
            cx = int(pad.cx * pw)
            cy = int(pad.cy * ph)
            r  = max(int(max(pad.bbox.w * pw, pad.bbox.h * ph) / 2), 5)
            if i == self._selected:
                painter.setPen(QPen(QColor(255, 80, 80), 3))
                painter.setBrush(QColor(255, 80, 80, 120))
            elif i == self._drag_pad_idx and self._dragging:
                painter.setPen(QPen(QColor(100, 200, 255), 3))
                painter.setBrush(QColor(100, 200, 255, 120))
            else:
                painter.setPen(QPen(QColor(255, 200, 0), 2))
                painter.setBrush(QColor(255, 200, 0, 80))
            if pad.shape == "circle":
                painter.drawEllipse(QPoint(cx, cy), r, r)
            else:
                painter.drawRect(cx - r, cy - r, r * 2, r * 2)
            lbl = pad.pin_number or pad.label
            if lbl:
                painter.setPen(QPen(QColor(255, 255, 255)))
                painter.drawText(QPoint(cx + r + 2, cy + 4), lbl)
        painter.end()

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _find_pad_at(self, pos: QPoint) -> int | None:
        if not self._pads or not self.pixmap():
            return None
        pw = self.pixmap().width()
        ph = self.pixmap().height()
        best_idx  = None
        best_dist = float("inf")
        for i, pad in enumerate(self._pads):
            cx   = pad.cx * pw
            cy   = pad.cy * ph
            r    = max(pad.bbox.w * pw, pad.bbox.h * ph) / 2 + 8
            dist = ((pos.x() - cx) ** 2 + (pos.y() - cy) ** 2) ** 0.5
            if dist < r and dist < best_dist:
                best_dist = dist
                best_idx  = i
        return best_idx


class _ReviewPage(QWidget):
    """Wizard page 1: review and manually fix detected pads.

    Supported edits
    ---------------
    * Click pad image or list row  → select
    * Drag pad on image            → move
    * Click empty area on image    → add new pad
    * Delete button / Delete key   → remove selected pad
    * Pin #, Label, Shape fields   → edit metadata of selected pad
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._result:       PinoutResult | None = None
        self._crop_px:      QPixmap | None      = None
        self._selected_idx: int | None          = None

        splitter = QSplitter(Qt.Orientation.Horizontal, self)
        layout   = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(splitter)

        # ── Left: image ──────────────────────────────────────────────────────
        left = QWidget()
        lv   = QVBoxLayout(left)
        self._review_lbl = _ReviewLabel()
        self._review_lbl.padClicked.connect(self._on_pad_clicked)
        self._review_lbl.padMoved.connect(self._on_pad_moved)
        self._review_lbl.newPadRequested.connect(self._add_pad)
        scroll = QScrollArea()
        scroll.setWidget(self._review_lbl)
        scroll.setWidgetResizable(False)
        lv.addWidget(scroll)

        self._detect_lbl = QLabel("No result yet")
        self._detect_lbl.setStyleSheet("color: #aaa; font-size: 10px;")
        lv.addWidget(self._detect_lbl)
        splitter.addWidget(left)

        # ── Right: editor ────────────────────────────────────────────────────
        right = QWidget()
        rv    = QVBoxLayout(right)
        rv.setContentsMargins(4, 4, 4, 4)

        box = QGroupBox("Selected pad")
        bv  = QVBoxLayout(box)
        from PyQt6.QtWidgets import QFormLayout
        form = QFormLayout()

        self._pin_num_edit = QLineEdit()
        self._pin_num_edit.setPlaceholderText("e.g. 14")
        self._pin_num_edit.editingFinished.connect(self._save_pad_edits)
        form.addRow("Pin #:", self._pin_num_edit)

        self._pin_lbl_edit = QLineEdit()
        self._pin_lbl_edit.setPlaceholderText("e.g. GND")
        self._pin_lbl_edit.editingFinished.connect(self._save_pad_edits)
        form.addRow("Label:", self._pin_lbl_edit)

        self._shape_combo = QComboBox()
        self._shape_combo.addItems(["circle", "rect", "square"])
        self._shape_combo.currentTextChanged.connect(self._save_pad_edits)
        form.addRow("Shape:", self._shape_combo)

        bv.addLayout(form)

        del_btn = QPushButton("🗑  Delete selected pad")
        del_btn.setToolTip("Delete (or press the Delete key)")
        del_btn.clicked.connect(self._delete_selected)
        bv.addWidget(del_btn)

        rv.addWidget(box)

        hint = QLabel(
            "<small><i>Click image to select/move pads.<br>"
            "Click empty area to add a new pad.</i></small>"
        )
        hint.setTextFormat(Qt.TextFormat.RichText)
        hint.setWordWrap(True)
        rv.addWidget(hint)

        self._pad_list = QListWidget()
        self._pad_list.currentRowChanged.connect(self._on_list_row_changed)
        rv.addWidget(self._pad_list, stretch=1)

        splitter.addWidget(right)
        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 1)

        self._set_editor_enabled(False)

    # ── Public API ────────────────────────────────────────────────────────────

    def load_result(self, result: PinoutResult, crop_img: np.ndarray) -> None:
        self._result   = result
        self._crop_px  = _ndarray_to_qpixmap(crop_img)
        self._refresh()

    @property
    def result(self) -> PinoutResult | None:
        return self._result

    # ── Keyboard ──────────────────────────────────────────────────────────────

    def keyPressEvent(self, event) -> None:
        if event.key() == Qt.Key.Key_Delete:
            self._delete_selected()
        else:
            super().keyPressEvent(event)

    # ── Slots ─────────────────────────────────────────────────────────────────

    def _on_pad_clicked(self, idx: int) -> None:
        self._select(idx)

    def _on_list_row_changed(self, row: int) -> None:
        if row >= 0:
            self._select(row)

    def _on_pad_moved(self, idx: int) -> None:
        """Pad was dragged — just refresh the list item text."""
        self._refresh_list_item(idx)

    def _add_pad(self, cx: float, cy: float) -> None:
        if not self._result:
            return
        default_size = 0.025
        new_pad = PadDetection(
            bbox=BBox(
                x=cx - default_size / 2,
                y=cy - default_size / 2,
                w=default_size,
                h=default_size,
            ),
            shape="circle",
        )
        self._result.pads.append(new_pad)
        new_idx = len(self._result.pads) - 1
        self._pad_list.addItem(self._pad_item_text(new_idx))
        self._review_lbl.update()
        self._update_detect_label()
        self._select(new_idx)

    def _delete_selected(self) -> None:
        if self._selected_idx is None or not self._result:
            return
        idx = self._selected_idx
        self._result.pads.pop(idx)
        self._selected_idx = None
        self._review_lbl.select_pad(None)
        self._set_editor_enabled(False)
        self._refresh()

    def _save_pad_edits(self) -> None:
        if self._selected_idx is None or not self._result:
            return
        pad            = self._result.pads[self._selected_idx]
        pad.pin_number = self._pin_num_edit.text().strip()
        pad.label      = self._pin_lbl_edit.text().strip()
        pad.shape      = self._shape_combo.currentText()
        self._refresh_list_item(self._selected_idx)
        self._review_lbl.update()

    # ── Private helpers ───────────────────────────────────────────────────────

    def _select(self, idx: int) -> None:
        if not self._result or idx >= len(self._result.pads):
            return
        self._selected_idx = idx
        self._review_lbl.select_pad(idx)
        # Block list signals while we set the row to avoid recursion
        self._pad_list.blockSignals(True)
        self._pad_list.setCurrentRow(idx)
        self._pad_list.blockSignals(False)
        pad = self._result.pads[idx]
        self._set_editor_enabled(True)
        self._pin_num_edit.setText(pad.pin_number)
        self._pin_lbl_edit.setText(pad.label)
        self._shape_combo.setCurrentText(pad.shape)

    def _refresh(self) -> None:
        if not self._result or not self._crop_px:
            return
        self._review_lbl.set_result(self._result, self._crop_px)
        self._pad_list.clear()
        for i in range(len(self._result.pads)):
            self._pad_list.addItem(self._pad_item_text(i))
        self._update_detect_label()
        self._selected_idx = None
        self._set_editor_enabled(False)

    def _refresh_list_item(self, idx: int) -> None:
        if item := self._pad_list.item(idx):
            item.setText(self._pad_item_text(idx))

    def _update_detect_label(self) -> None:
        n = len(self._result.pads) if self._result else 0
        self._detect_lbl.setText(
            f"{n} pad(s). Click to select/move. Click empty area to add."
        )

    def _pad_item_text(self, idx: int) -> str:
        pad = self._result.pads[idx]
        return f"[{idx+1}] #{pad.pin_number or '—'}  {pad.label or ''}  ({pad.shape})"

    def _set_editor_enabled(self, enabled: bool) -> None:
        self._pin_num_edit.setEnabled(enabled)
        self._pin_lbl_edit.setEnabled(enabled)
        self._shape_combo.setEnabled(enabled)
        if not enabled:
            self._pin_num_edit.clear()
            self._pin_lbl_edit.clear()



# ─── Main wizard dialog ───────────────────────────────────────────────────────

class DatasheetPinoutWizard(QDialog):
    """Two-step wizard for extracting a pinout from a linked datasheet PDF.

    Usage::

        wiz = DatasheetPinoutWizard(
            pdf_path=Path("/boards/cpu/datasheets/SII3512.pdf"),
            datasheet_id=42,
            component_id=7,
            parent=self,
        )
        if wiz.exec() == QDialog.DialogCode.Accepted:
            result     = wiz.result          # PinoutResult
            ds_id      = wiz.datasheet_id
            comp_id    = wiz.component_id
    """

    def __init__(
        self,
        pdf_path: Path,
        datasheet_id: int | None,
        component_id: int,
        parent: QWidget | None = None,
    ):
        super().__init__(parent)
        self.setWindowTitle(f"Select pinout — {pdf_path.name}")
        self.resize(1100, 700)
        self.setModal(True)
        self.setSizeGripEnabled(True)

        self._pdf_path     = pdf_path
        self.datasheet_id  = datasheet_id
        self.component_id  = component_id
        self.result:       PinoutResult | None = None

        self._build_ui()

    # ── UI ────────────────────────────────────────────────────────────────────

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(8, 8, 8, 8)

        # Step indicator
        self._step_lbl = QLabel()
        self._step_lbl.setFont(QFont("sans-serif", 10, QFont.Weight.Bold))
        root.addWidget(self._step_lbl)

        # Stacked pages
        self._stack = QStackedWidget()
        self._page0 = _RegionSelectPage(self._pdf_path)
        self._page0.regionConfirmed.connect(self._on_region_confirmed)
        self._stack.addWidget(self._page0)

        self._page1 = _ReviewPage()
        self._stack.addWidget(self._page1)

        root.addWidget(self._stack, stretch=1)

        # Error / status label
        self._error_lbl = QLabel("")
        self._error_lbl.setStyleSheet("color: #f44336; font-style: italic;")
        root.addWidget(self._error_lbl)

        # Navigation buttons
        btn_row = QHBoxLayout()

        self._back_btn = QPushButton("← Back")
        self._back_btn.setEnabled(False)
        self._back_btn.clicked.connect(self._go_back)
        btn_row.addWidget(self._back_btn)

        self._redetect_btn = QPushButton("🔍 Re-detect")
        self._redetect_btn.setVisible(False)
        self._redetect_btn.clicked.connect(self._redetect)
        btn_row.addWidget(self._redetect_btn)

        btn_row.addStretch()

        self._next_btn = QPushButton("Next →")
        self._next_btn.setEnabled(False)
        self._next_btn.clicked.connect(self._go_next)
        btn_row.addWidget(self._next_btn)

        self._confirm_btn = QPushButton("✓ Confirm pinout — align on canvas")
        self._confirm_btn.setVisible(False)
        self._confirm_btn.setStyleSheet(
            "font-weight: bold; background: #1b5e20; color: white;"
        )
        self._confirm_btn.clicked.connect(self._confirm)
        btn_row.addWidget(self._confirm_btn)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        btn_row.addWidget(cancel_btn)

        root.addLayout(btn_row)
        self._show_step(0)

    # ── Step navigation ───────────────────────────────────────────────────────

    def _show_step(self, idx: int) -> None:
        self._stack.setCurrentIndex(idx)
        if idx == 0:
            self._step_lbl.setText("Step 1 of 2: Draw a bounding box around the pinout diagram")
            self._back_btn.setEnabled(False)
            self._next_btn.setVisible(True)
            self._redetect_btn.setVisible(False)
            self._confirm_btn.setVisible(False)
        else:
            self._step_lbl.setText("Step 2 of 2: Review and fix detected pads, then confirm")
            self._back_btn.setEnabled(True)
            self._next_btn.setVisible(False)
            self._redetect_btn.setVisible(True)
            self._confirm_btn.setVisible(True)

    def _on_region_confirmed(self) -> None:
        self._next_btn.setEnabled(True)
        self._error_lbl.setText("")

    def _go_next(self) -> None:
        rel_bbox = self._page0.get_rel_bbox()
        if rel_bbox is None:
            self._error_lbl.setText("⚠ Please draw a selection box first.")
            return
        self._run_extraction(rel_bbox)

    def _go_back(self) -> None:
        self._show_step(0)

    def _redetect(self) -> None:
        rel_bbox = self._page0.get_rel_bbox()
        if rel_bbox is None:
            self._error_lbl.setText("⚠ Return to step 1 and re-draw the selection.")
            return
        self._run_extraction(rel_bbox)

    def _run_extraction(self, rel_bbox: BBox) -> None:
        self._error_lbl.setText("Processing…")
        self.setCursor(Qt.CursorShape.WaitCursor)
        try:
            page   = self._page0.current_page
            result = extract_pinout(self._pdf_path, page, rel_bbox, dpi=200)
            # Keep the crop image around for display
            from toolkit.analysis.pinout import crop_pinout_image
            crop_img = crop_pinout_image(self._pdf_path, page, rel_bbox, dpi=200)
            self._page1.load_result(result, crop_img)
            self._error_lbl.setText(
                f"Detected {len(result.pads)} pad(s).  "
                "Edit pin numbers/labels if needed, then confirm."
            )
            self._show_step(1)
        except Exception as exc:
            self._error_lbl.setText(f"⚠ Extraction failed: {exc}")
        finally:
            self.unsetCursor()

    def _confirm(self) -> None:
        result = self._page1.result
        if not result:
            return
        self.result = result
        self.accept()
