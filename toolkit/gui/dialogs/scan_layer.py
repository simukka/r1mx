"""ScanLayerWizard — multi-step dialog for unified PCB layer scanning.

Four-page QStackedWidget flow
──────────────────────────────
Page 0 — Photography Guidance  (skippable via "Don't show again")
    Tips for capturing PCB images that give the best analysis results.

Page 1 — Type Picker
    Radio buttons: Text/Components | Vias | Pads | Traces | Board Outline

Page 2 — Parameter Tuning
    Left: scan-type-specific controls
    Right: HsvTuner live preview (for visual scans) or OCR settings panel

Page 3 — Progress
    Log text area + indeterminate progress bar, Cancel available

On completion (accepted) the dialog exposes:
    .result()       → ScanLayerResult or None
    .needs_retry()  → True when "Adjust Parameters" was clicked in the
                      preview dialog — caller should re-open with same opts
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import cv2
import numpy as np
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QPushButton,
    QRadioButton,
    QScrollArea,
    QSizePolicy,
    QSpinBox,
    QStackedWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from toolkit.analysis.layers import (
    DEFAULT_HSV,
    DEFAULT_LAB,
    make_copper_mask,
    make_hole_mask,
)
from toolkit.db import DB
from toolkit.gui.widgets.hsv_tuner import HsvTuner
from toolkit.workers.scan_layer import ScanLayerWorker

_REPO = Path(__file__).resolve().parents[3]

# ---------------------------------------------------------------------------
# Wizard page indices — use these constants everywhere, never magic numbers
# ---------------------------------------------------------------------------

_PAGE_GUIDANCE  = 0
_PAGE_TYPE      = 1
_PAGE_PARAM     = 2
_PAGE_PROGRESS  = 3

# DB state key that controls whether the guidance page is shown
_STATE_SHOW_GUIDANCE = "scan_wizard_show_guidance"

# ---------------------------------------------------------------------------
# Result container
# ---------------------------------------------------------------------------

@dataclass
class ScanLayerResult:
    scan_type: str
    items: list = field(default_factory=list)
    opts: dict  = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Descriptions shown below each radio button
# ---------------------------------------------------------------------------

_DESCRIPTIONS = {
    "text": (
        "Extract reference designators (R1, U7, C12…) and part numbers from the "
        "board silkscreen using OCR (EasyOCR or Tesseract)."
    ),
    "vias": (
        "Detect via drill holes using circle detection on the dark-hole mask. "
        "Tune the Hole HSV thresholds so all via holes appear white in the preview."
    ),
    "pads": (
        "Detect SMD and through-hole pads from the copper mask. "
        "Tune the Copper HSV thresholds so all pads appear highlighted."
    ),
    "traces": (
        "Vectorise copper traces using potrace. "
        "Tune the Copper HSV thresholds for best trace coverage. "
        "Note: this step can take several minutes on high-resolution images."
    ),
    "outline": (
        "Detect the board outline by finding the largest contour. "
        "Adjust Canny edge thresholds if the outline is not found correctly."
    ),
}

_LABELS = {
    "text":    "Text / Components  (OCR)",
    "vias":    "Vias  (circle detection)",
    "pads":    "Pads  (copper blob detection)",
    "traces":  "Traces  (copper vectorisation)",
    "outline": "Board Outline  (edge detection)",
}


# ---------------------------------------------------------------------------
# Page 0 — Photography Guidance
# ---------------------------------------------------------------------------

_PHOTO_TIPS = [
    (
        "🥇",
        "White background",
        "Place a sheet of white paper or white foam board directly behind/under the PCB. "
        "This creates a crisp light/dark edge so the board outline is automatically detectable. "
        "A black-background photo makes the board edge nearly invisible to the detector.",
    ),
    (
        "🥈",
        "365 nm UV (black-light) illumination",
        "Standard solder mask — including dark green and black — fluoresces yellow-green "
        "under 365 nm UV light. Copper and the background do not fluoresce. "
        "This gives colour separation that is impossible in visible light, and is the "
        "single most effective fix for dark-PCB images. A cheap UV LED panel ($15–30) "
        "is sufficient. Photograph in a darkened room.",
    ),
    (
        "🥉",
        "Diffuse / ring lighting",
        "Direct, angled, or single-point lighting creates specular hotspots on copper "
        "and tin finishes that saturate HSV channels and break colour thresholds. "
        "Use a ring-flash, LED light tent, or a large diffuser panel to wrap the light "
        "evenly around the board. No hotspots = consistent HSV across the whole image.",
    ),
    (
        "✳",
        "Flatbed scanner (bare boards)",
        "A flatbed scanner (e.g. Epson V39 / ES-400) at 1200–2400 DPI eliminates all "
        "lighting problems: built-in diffuse illumination, zero perspective distortion, "
        "and fixed geometry. Place a white card on top of the board so the platen "
        "light back-illuminates the FR4, making copper appear as dark silhouettes. "
        "Recommended for any bare (unpopulated) board.",
    ),
    (
        "ℹ",
        "Raking / grazing light (optional)",
        "A low-angle (15–30°) LED panel skimming across the board surface exaggerates "
        "trace relief via shadows. Useful for detecting trace topology on flat boards "
        "where colour-based approaches still struggle after the above steps.",
    ),
]


class _PhotoGuidancePage(QWidget):
    """Photography tips page shown before the scan type picker."""

    #: Emitted when the "Don't show again" checkbox is toggled.
    show_changed = pyqtSignal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)

        scroll_content = QWidget()
        v = QVBoxLayout(scroll_content)
        v.setSpacing(14)
        v.setContentsMargins(8, 8, 8, 8)

        header = QLabel(
            "<b>Before You Scan — Photography Tips</b><br>"
            "<span style='font-size:12px;'>"
            "The quality of your board photograph is the single biggest factor in "
            "scan accuracy. These tips are ranked by impact.</span>"
        )
        header.setWordWrap(True)
        header.setTextFormat(Qt.TextFormat.RichText)
        v.addWidget(header)

        for icon, title, body in _PHOTO_TIPS:
            group = QGroupBox(f"{icon}  {title}")
            group.setStyleSheet("QGroupBox { font-weight: bold; }")
            gl = QVBoxLayout(group)
            gl.setContentsMargins(8, 4, 8, 6)
            lbl = QLabel(body)
            lbl.setWordWrap(True)
            lbl.setStyleSheet("font-weight: normal;")
            gl.addWidget(lbl)
            v.addWidget(group)

        v.addStretch()

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(scroll_content)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)

        self._chk_skip = QCheckBox("Don't show this again")
        self._chk_skip.toggled.connect(lambda checked: self.show_changed.emit(not checked))

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll, stretch=1)
        outer.addWidget(self._chk_skip)

    def skip_next_time(self) -> bool:
        return self._chk_skip.isChecked()

    def set_skip(self, skip: bool):
        self._chk_skip.setChecked(skip)


# ---------------------------------------------------------------------------
# Page 1 — Type Picker
# ---------------------------------------------------------------------------

class _TypePickerPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        layout.addWidget(QLabel("<b>Choose what to scan for:</b>"))

        self._radios: dict[str, QRadioButton] = {}
        self._desc = QLabel()
        self._desc.setWordWrap(True)
        self._desc.setStyleSheet("color: #aaa; font-style: italic;")

        for key in ("text", "vias", "pads", "traces", "outline"):
            rb = QRadioButton(_LABELS[key])
            rb.toggled.connect(lambda checked, k=key: self._on_toggle(k, checked))
            layout.addWidget(rb)
            self._radios[key] = rb

        self._radios["text"].setChecked(True)

        layout.addSpacing(8)
        layout.addWidget(self._desc)
        layout.addStretch()

    def _on_toggle(self, key: str, checked: bool):
        if checked:
            self._desc.setText(_DESCRIPTIONS[key])

    def scan_type(self) -> str:
        for key, rb in self._radios.items():
            if rb.isChecked():
                return key
        return "text"

    def set_scan_type(self, t: str):
        if t in self._radios:
            self._radios[t].setChecked(True)


# ---------------------------------------------------------------------------
# Page 1 — Parameter Tuning
# ---------------------------------------------------------------------------

class _ParamPage(QWidget):
    """Shows scan-type-specific parameter controls + optional HsvTuner."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._scan_type = "text"
        self._hsv_tuner: HsvTuner | None = None
        self._bgr: np.ndarray | None = None
        self._px_per_mm: float = 20.0

        # Left: parameter controls (in a scroll area for future expansion)
        self._ctrl_stack = QStackedWidget()
        self._pages: dict[str, QWidget] = {}
        for t in ("text", "vias", "pads", "traces", "outline"):
            w = self._build_ctrl_page(t)
            self._pages[t] = w
            self._ctrl_stack.addWidget(w)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(self._ctrl_stack)
        scroll.setMinimumWidth(260)
        scroll.setMaximumWidth(360)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)

        # Right: tuner placeholder (filled when board image is available)
        self._tuner_placeholder = QLabel(
            "Load a calibrated layer to enable live preview."
        )
        self._tuner_placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._tuner_placeholder.setStyleSheet("color: #666;")
        self._tuner_placeholder.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )

        self._right_layout = QVBoxLayout()
        self._right_layout.addWidget(self._tuner_placeholder)

        root = QHBoxLayout(self)
        root.setSpacing(12)
        root.addWidget(scroll)
        right_widget = QWidget()
        right_widget.setLayout(self._right_layout)
        root.addWidget(right_widget, stretch=1)

    # ── Control pages ─────────────────────────────────────────────────

    def _build_ctrl_page(self, scan_type: str) -> QWidget:
        if scan_type == "text":
            return self._build_text_ctrl()
        if scan_type in ("vias", "pads", "traces"):
            return self._build_hsv_note(scan_type)
        if scan_type == "outline":
            return self._build_outline_ctrl()
        return QWidget()

    def _build_text_ctrl(self) -> QWidget:
        w = QWidget()
        f = QFormLayout(w)
        f.setVerticalSpacing(8)
        f.setContentsMargins(0, 0, 0, 0)

        self._engine = QComboBox()
        self._engine.addItems(["EasyOCR", "Tesseract"])
        f.addRow("Engine:", self._engine)

        self._confidence = QDoubleSpinBox()
        self._confidence.setRange(0.0, 1.0)
        self._confidence.setSingleStep(0.05)
        self._confidence.setDecimals(2)
        self._confidence.setValue(0.35)
        self._confidence.setToolTip(
            "Minimum OCR confidence (0 = accept all, 1 = perfect only).\n"
            "Lower values find more text but with more noise."
        )
        f.addRow("Min confidence:", self._confidence)

        self._tile_size = QSpinBox()
        self._tile_size.setRange(128, 4096)
        self._tile_size.setSingleStep(128)
        self._tile_size.setValue(512)
        self._tile_size.setSuffix(" px")
        f.addRow("Tile size:", self._tile_size)

        self._tile_overlap = QSpinBox()
        self._tile_overlap.setRange(0, 512)
        self._tile_overlap.setSingleStep(16)
        self._tile_overlap.setValue(100)
        self._tile_overlap.setSuffix(" px")
        f.addRow("Tile overlap:", self._tile_overlap)

        self._gpu = QCheckBox("Use GPU (CUDA)")
        f.addRow("", self._gpu)

        note = QLabel(
            "Tip: for best results, ensure the board image is in focus and "
            "well-lit with no glare on the silkscreen."
        )
        note.setWordWrap(True)
        note.setStyleSheet("color: #888; font-size: 11px;")
        f.addRow(note)

        return w

    def _build_hsv_note(self, scan_type: str) -> QWidget:
        w = QWidget()
        v = QVBoxLayout(w)
        v.setContentsMargins(0, 0, 0, 0)
        note = QLabel(
            "Use the sliders on the right to tune the HSV colour thresholds. "
            "The preview shows which pixels are captured by the current settings.\n\n"
            "• Set the threshold so the target features are clearly highlighted\n"
            "• Minimise false positives (background noise)\n"
            "• Click 'Mask' to see the raw binary mask"
        )
        note.setWordWrap(True)
        note.setStyleSheet("color: #aaa;")
        v.addWidget(note)
        v.addStretch()
        return w

    def _build_outline_ctrl(self) -> QWidget:
        w = QWidget()
        f = QFormLayout(w)
        f.setVerticalSpacing(8)
        f.setContentsMargins(0, 0, 0, 0)

        self._canny_low = QSpinBox()
        self._canny_low.setRange(1, 500)
        self._canny_low.setValue(30)
        self._canny_low.setToolTip("Lower Canny edge detection threshold.")
        f.addRow("Canny low:", self._canny_low)

        self._canny_high = QSpinBox()
        self._canny_high.setRange(1, 500)
        self._canny_high.setValue(100)
        self._canny_high.setToolTip("Upper Canny edge detection threshold.")
        f.addRow("Canny high:", self._canny_high)

        note = QLabel(
            "The board outline is detected as the largest closed contour. "
            "Increase the thresholds if small features are mistaken for the outline; "
            "decrease if the outline edge is faint."
        )
        note.setWordWrap(True)
        note.setStyleSheet("color: #888; font-size: 11px;")
        f.addRow(note)

        return w

    # ── Public API ────────────────────────────────────────────────────

    def set_scan_type(self, scan_type: str):
        self._scan_type = scan_type
        self._ctrl_stack.setCurrentWidget(self._pages[scan_type])
        self._rebuild_tuner()

    def load_board_image(self, bgr: np.ndarray, px_per_mm: float):
        """Provide the warped board image so the HsvTuner can show a preview."""
        self._bgr = bgr
        self._px_per_mm = px_per_mm
        self._rebuild_tuner()

    def opts(self) -> dict:
        """Return the current parameter dict for the active scan type."""
        t = self._scan_type
        if t == "text":
            return {
                "engine":         self._engine.currentText().lower(),
                "min_confidence": self._confidence.value(),
                "tile_size":      self._tile_size.value(),
                "tile_overlap":   self._tile_overlap.value(),
                "gpu":            self._gpu.isChecked(),
            }
        if t == "outline":
            return {
                "canny_low":  self._canny_low.value(),
                "canny_high": self._canny_high.value(),
            }
        # vias / pads / traces — HSV cfg from tuner
        if self._hsv_tuner:
            return {"hsv_cfg": self._hsv_tuner.hsv_cfg()}
        return {"hsv_cfg": dict(DEFAULT_HSV)}

    def set_opts(self, opts: dict):
        """Restore previously-used options (for retry flow)."""
        t = self._scan_type
        if t == "text":
            if "engine" in opts:
                idx = self._engine.findText(opts["engine"], Qt.MatchFlag.MatchFixedString)
                if idx >= 0:
                    self._engine.setCurrentIndex(idx)
            if "min_confidence" in opts:
                self._confidence.setValue(opts["min_confidence"])
            if "tile_size" in opts:
                self._tile_size.setValue(opts["tile_size"])
            if "tile_overlap" in opts:
                self._tile_overlap.setValue(opts["tile_overlap"])
            if "gpu" in opts:
                self._gpu.setChecked(opts["gpu"])
        elif t == "outline":
            if "canny_low" in opts:
                self._canny_low.setValue(opts["canny_low"])
            if "canny_high" in opts:
                self._canny_high.setValue(opts["canny_high"])
        elif self._hsv_tuner and "hsv_cfg" in opts:
            self._hsv_tuner.set_hsv_cfg(opts["hsv_cfg"])

    # ── Internal ─────────────────────────────────────────────────────

    def _rebuild_tuner(self):
        """Swap the right-side widget: HsvTuner for visual scans, note otherwise."""
        # Clear previous tuner
        if self._hsv_tuner is not None:
            self._right_layout.removeWidget(self._hsv_tuner)
            self._hsv_tuner.deleteLater()
            self._hsv_tuner = None

        t = self._scan_type
        if self._bgr is None or t not in ("vias", "pads", "traces"):
            self._tuner_placeholder.setVisible(True)
            return

        self._tuner_placeholder.setVisible(False)

        if t == "vias":
            mask_fn = make_hole_mask
            lower_key, upper_key = "hole_lower", "hole_upper"
            lo = DEFAULT_HSV["hole_lower"]
            hi = DEFAULT_HSV["hole_upper"]
            colour = (80, 80, 255)   # red circles for vias
        else:
            # pads and traces both use copper mask
            mask_fn = make_copper_mask
            lower_key, upper_key = "copper_lower", "copper_upper"
            lo = DEFAULT_HSV["copper_lower"]
            hi = DEFAULT_HSV["copper_upper"]
            colour = (0, 200, 255)  # gold/orange for copper

        self._hsv_tuner = HsvTuner(
            bgr_image=self._bgr,
            mask_fn=mask_fn,
            lower_key=lower_key,
            upper_key=upper_key,
            lower_defaults=list(lo),
            upper_defaults=list(hi),
            overlay_colour=colour,
            parent=self,
        )
        self._right_layout.addWidget(self._hsv_tuner)


# ---------------------------------------------------------------------------
# Page 3 — Progress  (was Page 2 before guidance page was added)
# ---------------------------------------------------------------------------

class _ProgressPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        v = QVBoxLayout(self)
        v.setSpacing(6)

        self._log = QTextEdit()
        self._log.setReadOnly(True)
        self._log.setMinimumHeight(220)
        v.addWidget(self._log)

        self._bar = QProgressBar()
        self._bar.setRange(0, 0)   # indeterminate
        v.addWidget(self._bar)

    def clear(self):
        self._log.clear()

    def append(self, line: str):
        self._log.append(line)
        self._log.verticalScrollBar().setValue(self._log.verticalScrollBar().maximum())

    def set_done(self):
        self._bar.setRange(0, 1)
        self._bar.setValue(1)


# ---------------------------------------------------------------------------
# The Wizard
# ---------------------------------------------------------------------------

class ScanLayerWizard(QDialog):
    """Four-page wizard for unified PCB layer scanning.

    After exec() returns Accepted, access .result() for the scan result.
    If .needs_retry() is True the caller should reopen with pre-filled opts.
    """

    def __init__(self, board_name: str, layer_name: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Scan Layer — {board_name} / {layer_name}")
        self.setMinimumSize(960, 620)
        self.resize(1200, 700)
        self.setSizeGripEnabled(True)

        self._board_name  = board_name
        self._layer_name  = layer_name
        self._worker: ScanLayerWorker | None = None
        self._scan_result: ScanLayerResult | None = None
        self._retry       = False
        self._bgr: np.ndarray | None = None
        self._px_per_mm   = 20.0

        # ── Pages ──────────────────────────────────────────────────────
        self._guid_page  = _PhotoGuidancePage()
        self._type_page  = _TypePickerPage()
        self._param_page = _ParamPage()
        self._prog_page  = _ProgressPage()

        self._stack = QStackedWidget()
        self._stack.addWidget(self._guid_page)   # _PAGE_GUIDANCE = 0
        self._stack.addWidget(self._type_page)   # _PAGE_TYPE     = 1
        self._stack.addWidget(self._param_page)  # _PAGE_PARAM    = 2
        self._stack.addWidget(self._prog_page)   # _PAGE_PROGRESS = 3

        # Persist "don't show again" choice immediately when toggled
        self._guid_page.show_changed.connect(self._on_guidance_show_changed)

        # ── Navigation buttons ─────────────────────────────────────────
        self._btn_back   = QPushButton("← Back")
        self._btn_next   = QPushButton("Next →")
        self._btn_run    = QPushButton("▶  Run Scan")
        self._btn_cancel = QPushButton("Cancel")

        self._btn_back.clicked.connect(self._go_back)
        self._btn_next.clicked.connect(self._go_next)
        self._btn_run.clicked.connect(self._start_scan)
        self._btn_cancel.clicked.connect(self._cancel)

        nav = QHBoxLayout()
        nav.addWidget(self._btn_back)
        nav.addStretch()
        nav.addWidget(self._btn_cancel)
        nav.addWidget(self._btn_next)
        nav.addWidget(self._btn_run)

        # ── Root layout ────────────────────────────────────────────────
        root = QVBoxLayout(self)
        root.addWidget(self._stack, stretch=1)
        root.addLayout(nav)

        # Determine whether to show the guidance page
        start_page = _PAGE_GUIDANCE
        try:
            db = DB()
            if db.get_state(_STATE_SHOW_GUIDANCE) == "0":
                start_page = _PAGE_TYPE
                self._guid_page.set_skip(True)
        except Exception:
            pass

        self._set_page(start_page)

        # Pre-load the board image for the param tuner
        self._try_load_board_image()

    # ------------------------------------------------------------------
    # Public
    # ------------------------------------------------------------------

    def result(self) -> ScanLayerResult | None:
        return self._scan_result

    def needs_retry(self) -> bool:
        return self._retry

    def set_scan_type(self, t: str):
        self._type_page.set_scan_type(t)

    def set_opts(self, opts: dict):
        self._param_page.set_opts(opts)

    # ------------------------------------------------------------------
    # Navigation
    # ------------------------------------------------------------------

    def _set_page(self, idx: int):
        self._stack.setCurrentIndex(idx)
        self._btn_back.setVisible(idx > _PAGE_GUIDANCE)
        self._btn_next.setVisible(idx < _PAGE_PARAM)
        self._btn_run.setVisible(idx == _PAGE_PARAM)
        self._btn_cancel.setEnabled(True)

        if idx == _PAGE_PARAM:
            self._param_page.set_scan_type(self._type_page.scan_type())

    def _go_next(self):
        self._set_page(self._stack.currentIndex() + 1)

    def _go_back(self):
        idx = self._stack.currentIndex()
        if idx == _PAGE_PROGRESS and self._worker and self._worker.isRunning():
            return  # can't go back while running
        self._set_page(max(_PAGE_GUIDANCE, idx - 1))

    # ------------------------------------------------------------------
    # Guidance page persistence
    # ------------------------------------------------------------------

    def _on_guidance_show_changed(self, show: bool):
        """Persist the 'don't show again' preference immediately."""
        try:
            DB().set_state(_STATE_SHOW_GUIDANCE, "1" if show else "0")
        except Exception:
            pass

    # ------------------------------------------------------------------
    # Scan execution
    # ------------------------------------------------------------------

    def _start_scan(self):
        scan_type = self._type_page.scan_type()
        opts      = self._param_page.opts()

        self._prog_page.clear()
        self._set_page(_PAGE_PROGRESS)
        self._btn_cancel.setEnabled(True)

        self._worker = ScanLayerWorker(
            self._board_name, self._layer_name, scan_type, opts, parent=self
        )
        self._worker.signals.line.connect(self._prog_page.append)
        self._worker.scan_layer_done.connect(
            lambda items: self._on_scan_done(items, scan_type, opts)
        )
        self._worker.signals.finished.connect(self._on_worker_finished)
        self._worker.start()

    def _on_scan_done(self, items: list, scan_type: str, opts: dict):
        self._scan_result = ScanLayerResult(
            scan_type=scan_type,
            items=items,
            opts=opts,
        )

    def _on_worker_finished(self, ok: bool, msg: str):
        self._prog_page.set_done()
        self._prog_page.append(("✓ " if ok else "✗ ") + msg)

        if ok and self._scan_result is not None:
            # Attach the warped image so the preview dialog can render overlays
            self._scan_result.opts["_bgr"] = self._bgr
            self._scan_result.opts["_px_per_mm"] = self._px_per_mm
            self.accept()
        elif not ok:
            self._btn_back.setVisible(True)

    def _cancel(self):
        if self._worker and self._worker.isRunning():
            self._worker.terminate()
            self._worker.wait(2000)
        self.reject()

    # ------------------------------------------------------------------
    # Image pre-loading
    # ------------------------------------------------------------------

    def _try_load_board_image(self):
        """Load + warp the board image so the HsvTuner can show a preview."""
        try:
            db        = DB()
            board_id  = db.get_or_create_board(self._board_name)
            layer_row = db.get_layer(board_id, self._layer_name)
            if not layer_row or not layer_row["calibrated"]:
                return

            cal         = json.loads(layer_row["calibration"] or "{}")
            warp_matrix = cal.get("warp_matrix")
            warped_size = cal.get("warped_size")
            px_per_mm   = cal.get("px_per_mm", 20.0)
            source_img  = layer_row["source_image"] or ""

            img_path = _REPO / "components" / self._board_name / source_img
            if not img_path.exists():
                return

            bgr = cv2.imread(str(img_path))
            if bgr is None:
                return

            if warp_matrix and warped_size:
                M = np.array(warp_matrix, dtype=np.float64)
                bgr = cv2.warpPerspective(bgr, M, tuple(warped_size))

            if self._layer_name == "bottom":
                bgr = cv2.flip(bgr, 1)

            self._bgr       = bgr
            self._px_per_mm = px_per_mm
            self._param_page.load_board_image(bgr, px_per_mm)

        except Exception:
            pass  # non-fatal — preview just won't show
