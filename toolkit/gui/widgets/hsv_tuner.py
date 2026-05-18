"""HsvTuner — HSV threshold slider widget with live mask preview.

Embeds two HSV triplet groups (Lower / Upper) and a thumbnail of the board
image with the current mask overlaid.  Designed to be embedded inside the
ScanLayerWizard parameter-tuning page.

Usage::

    tuner = HsvTuner(bgr_image, mask_fn=make_copper_mask, parent=self)
    tuner.params_changed.connect(self._on_params)   # emits dict
    layout.addWidget(tuner)
    current = tuner.hsv_cfg()   # read current values at any time

Eyedropper / colour picker::

    Click the "🎯 Pick" button (toggle), then click anywhere on the preview
    image.  The widget samples an 11×11 neighbourhood around the clicked pixel,
    computes mean ± 2σ in HSV space, and pushes those values to the Lower /
    Upper sliders automatically.  Click "🎯 Pick" again to cancel.
"""
from __future__ import annotations

from typing import Callable

import cv2
import numpy as np
from PyQt6.QtCore import QPoint, QTimer, Qt, pyqtSignal
from PyQt6.QtGui import QCursor, QImage, QPixmap
from PyQt6.QtWidgets import (
    QButtonGroup,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QSlider,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

# Keys that exist in DEFAULT_HSV / hsv_cfg for each feature group
_HOLE_KEYS   = ("hole_lower",   "hole_upper")
_COPPER_KEYS = ("copper_lower", "copper_upper")
_SILK_KEYS   = ("silk_lower_white", "silk_upper_white")

# Max thumbnail width (px) — scaled to fit
_THUMB_W = 640
_THUMB_H = 400

# Debounce delay for live preview refresh (ms)
_DEBOUNCE_MS = 150


# ---------------------------------------------------------------------------
# Pure-numpy helper — no Qt dependency, fully unit-testable
# ---------------------------------------------------------------------------

def sample_hsv_range(
    bgr: np.ndarray,
    cx: int,
    cy: int,
    radius: int = 5,
) -> tuple[list[int], list[int]]:
    """Sample a neighbourhood of *bgr* at *(cx, cy)* and return HSV lo/hi.

    Computes the per-channel mean and standard deviation of the HSV values
    inside a ``(2*radius+1) × (2*radius+1)`` window centred on *(cx, cy)*.
    Returns ``(lo, hi)`` where::

        lo[c] = clip(mean[c] - 2*std[c], channel_min)
        hi[c] = clip(mean[c] + 2*std[c], channel_max)

    Channel limits: H ∈ [0, 179], S ∈ [0, 255], V ∈ [0, 255].

    Parameters
    ----------
    bgr:
        Source BGR image (uint8).
    cx, cy:
        Centre pixel coordinates (clamped to image bounds).
    radius:
        Half-width of the sampling window in pixels.

    Returns
    -------
    (lo, hi) as lists of three integers [H, S, V].
    """
    h_img, w_img = bgr.shape[:2]
    x0 = max(0, cx - radius)
    x1 = min(w_img, cx + radius + 1)
    y0 = max(0, cy - radius)
    y1 = min(h_img, cy + radius + 1)

    roi_bgr = bgr[y0:y1, x0:x1]
    if roi_bgr.size == 0:
        return [0, 0, 0], [179, 255, 255]

    roi_hsv = cv2.cvtColor(roi_bgr, cv2.COLOR_BGR2HSV)
    pixels  = roi_hsv.reshape(-1, 3).astype(np.float32)

    mean = pixels.mean(axis=0)
    std  = pixels.std(axis=0)

    limits = [(0, 179), (0, 255), (0, 255)]
    lo = [int(np.clip(mean[i] - 2 * std[i], limits[i][0], limits[i][1])) for i in range(3)]
    hi = [int(np.clip(mean[i] + 2 * std[i], limits[i][0], limits[i][1])) for i in range(3)]

    # Ensure lo <= hi on each channel
    for i in range(3):
        if lo[i] > hi[i]:
            lo[i], hi[i] = hi[i], lo[i]

    return lo, hi


# ---------------------------------------------------------------------------
# Clickable QLabel — emits a signal when the user clicks
# ---------------------------------------------------------------------------

class _ClickableLabel(QLabel):
    """QLabel subclass that emits ``clicked(QPoint)`` on left-mouse-press."""

    clicked = pyqtSignal(QPoint)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(event.pos())
        super().mousePressEvent(event)


def _bgr_to_pixmap(bgr: np.ndarray) -> QPixmap:
    h, w = bgr.shape[:2]
    rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
    img = QImage(rgb.data, w, h, 3 * w, QImage.Format.Format_RGB888)
    return QPixmap.fromImage(img.copy())


def _mask_to_pixmap(mask: np.ndarray) -> QPixmap:
    h, w = mask.shape[:2]
    img = QImage(mask.data, w, h, w, QImage.Format.Format_Grayscale8)
    return QPixmap.fromImage(img.copy())


def _blend_mask_on_bgr(bgr: np.ndarray, mask: np.ndarray, colour=(0, 255, 80)) -> np.ndarray:
    """Overlay *mask* (binary) on *bgr* with a semi-transparent tint."""
    overlay = bgr.copy()
    overlay[mask > 0] = [int(c * 0.6) + int(b * 0.4)
                         for c, b in zip(colour, bgr[mask > 0].mean(axis=0)
                                         if mask.any() else [0, 0, 0])]
    # Simpler: just tint the masked pixels directly
    tint = np.zeros_like(bgr)
    tint[:] = colour
    blended = bgr.copy().astype(np.float32)
    mask3 = cv2.merge([mask, mask, mask]).astype(np.float32) / 255.0
    blended = (blended * (1 - 0.5 * mask3) + tint.astype(np.float32) * 0.5 * mask3)
    return np.clip(blended, 0, 255).astype(np.uint8)


class _HsvGroup(QWidget):
    """Three H/S/V sliders with spinboxes for a single (lower or upper) HSV bound."""

    changed = pyqtSignal()

    def __init__(self, label: str, defaults: list[int], parent=None):
        super().__init__(parent)
        self._sliders: list[QSlider] = []
        self._spins: list[QSpinBox] = []

        box = QGroupBox(label)
        form = QFormLayout(box)
        form.setVerticalSpacing(4)
        form.setContentsMargins(8, 4, 8, 4)

        ranges = [(0, 180), (0, 255), (0, 255)]
        labels = ["H", "S", "V"]
        for i, (lo, hi) in enumerate(ranges):
            row = QHBoxLayout()
            sld = QSlider(Qt.Orientation.Horizontal)
            sld.setRange(lo, hi)
            sld.setValue(defaults[i])
            sld.setFixedWidth(160)

            spin = QSpinBox()
            spin.setRange(lo, hi)
            spin.setValue(defaults[i])
            spin.setFixedWidth(52)

            # Keep slider ↔ spinbox in sync
            sld.valueChanged.connect(spin.setValue)
            spin.valueChanged.connect(sld.setValue)
            sld.valueChanged.connect(lambda _: self.changed.emit())

            row.addWidget(sld)
            row.addWidget(spin)
            form.addRow(labels[i] + ":", row)

            self._sliders.append(sld)
            self._spins.append(spin)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(box)

    def values(self) -> list[int]:
        return [s.value() for s in self._sliders]

    def set_values(self, vals: list[int]):
        for s, sp, v in zip(self._sliders, self._spins, vals):
            s.blockSignals(True)
            sp.blockSignals(True)
            s.setValue(v)
            sp.setValue(v)
            s.blockSignals(False)
            sp.blockSignals(False)
        self.changed.emit()


class HsvTuner(QWidget):
    """HSV threshold tuner with live mask preview thumbnail.

    Parameters
    ----------
    bgr_image:
        The (warped) board image as a BGR numpy array.
    mask_fn:
        ``callable(bgr: np.ndarray, hsv_cfg: dict) -> np.ndarray`` — returns a
        binary uint8 mask.  Called on a down-scaled thumbnail for speed.
    lower_key / upper_key:
        Keys in ``hsv_cfg`` for the lower and upper HSV bounds.
    lower_defaults / upper_defaults:
        Initial [H, S, V] values for the two bounds.
    overlay_colour:
        BGR colour used to tint the masked region in blend mode.
    """

    params_changed = pyqtSignal(dict)

    def __init__(
        self,
        bgr_image: np.ndarray,
        mask_fn: Callable[[np.ndarray, dict], np.ndarray],
        lower_key: str = "copper_lower",
        upper_key: str = "copper_upper",
        lower_defaults: list[int] | None = None,
        upper_defaults: list[int] | None = None,
        overlay_colour: tuple[int, int, int] = (0, 255, 80),
        extra_keys: dict | None = None,
        parent=None,
    ):
        super().__init__(parent)

        self._mask_fn = mask_fn
        self._lower_key = lower_key
        self._upper_key = upper_key
        self._overlay_colour = overlay_colour
        self._extra_keys = extra_keys or {}

        # Build a scaled-down working thumbnail for fast preview
        h, w = bgr_image.shape[:2]
        scale = min(_THUMB_W / w, _THUMB_H / h, 1.0)
        tw = max(1, int(w * scale))
        th = max(1, int(h * scale))
        self._thumb_bgr = cv2.resize(bgr_image, (tw, th), interpolation=cv2.INTER_AREA)

        ld = lower_defaults or [0, 0, 0]
        ud = upper_defaults or [180, 255, 255]

        # ── HSV groups ────────────────────────────────────────────────────
        self._lower_group = _HsvGroup("Lower bound", ld)
        self._upper_group = _HsvGroup("Upper bound", ud)
        self._lower_group.changed.connect(self._schedule_refresh)
        self._upper_group.changed.connect(self._schedule_refresh)

        # ── Display mode toggle + eyedropper ─────────────────────────────
        mode_row = QHBoxLayout()
        self._mode_btns: list[QPushButton] = []
        mode_bg = QButtonGroup(self)
        for i, label in enumerate(["Blend", "Mask", "Original"]):
            btn = QPushButton(label)
            btn.setCheckable(True)
            btn.setFlat(True)
            mode_bg.addButton(btn, i)
            mode_row.addWidget(btn)
            self._mode_btns.append(btn)
        self._mode_btns[0].setChecked(True)
        mode_bg.idClicked.connect(self._on_mode)

        # Eyedropper / colour-picker button
        self._btn_pick = QPushButton("🎯 Pick")
        self._btn_pick.setCheckable(True)
        self._btn_pick.setFlat(True)
        self._btn_pick.setToolTip(
            "Click this, then click a pixel on the preview image to\n"
            "auto-fill the HSV sliders from that colour's neighbourhood."
        )
        self._btn_pick.toggled.connect(self._on_pick_toggled)
        mode_row.addStretch()
        mode_row.addWidget(self._btn_pick)

        # ── Preview label (clickable for eyedropper) ──────────────────────
        self._preview = _ClickableLabel()
        self._preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._preview.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self._preview.setMinimumSize(480, 300)
        self._preview.setStyleSheet("background: #1a1a1a; border: 1px solid #444;")
        self._preview.clicked.connect(self._on_preview_clicked)

        self._mode = 0  # 0=blend, 1=mask, 2=original
        self._pick_mode = False  # True while eyedropper is active

        # ── Layout ────────────────────────────────────────────────────────
        ctrl = QVBoxLayout()
        ctrl.addWidget(self._lower_group)
        ctrl.addWidget(self._upper_group)
        ctrl.addStretch()

        right = QVBoxLayout()
        right.addLayout(mode_row)
        right.addWidget(self._preview, stretch=1)

        root = QHBoxLayout(self)
        root.setSpacing(12)
        root.addLayout(ctrl)
        root.addLayout(right, stretch=1)

        # Debounce timer
        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(self._refresh_preview)

        # Initial render
        self._schedule_refresh()

    # ── Public API ────────────────────────────────────────────────────────

    def hsv_cfg(self) -> dict:
        """Return the current HSV config dict."""
        cfg = dict(self._extra_keys)
        cfg[self._lower_key] = self._lower_group.values()
        cfg[self._upper_key] = self._upper_group.values()
        return cfg

    def set_hsv_cfg(self, cfg: dict):
        """Restore slider values from a previously-saved config dict."""
        if self._lower_key in cfg:
            self._lower_group.set_values(cfg[self._lower_key])
        if self._upper_key in cfg:
            self._upper_group.set_values(cfg[self._upper_key])

    # ── Internal ─────────────────────────────────────────────────────────

    def _schedule_refresh(self):
        self._timer.start(_DEBOUNCE_MS)

    def _on_mode(self, idx: int):
        self._mode = idx
        self._schedule_refresh()

    def _refresh_preview(self):
        cfg = self.hsv_cfg()
        try:
            mask = self._mask_fn(self._thumb_bgr, cfg)
        except Exception:
            return

        if self._mode == 1:
            pix = _mask_to_pixmap(mask)
        elif self._mode == 2:
            pix = _bgr_to_pixmap(self._thumb_bgr)
        else:
            blended = _blend_mask_on_bgr(self._thumb_bgr, mask, self._overlay_colour)
            pix = _bgr_to_pixmap(blended)

        self._preview.setPixmap(
            pix.scaled(
                self._preview.width(),
                self._preview.height(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
        )
        self.params_changed.emit(cfg)

    # ── Eyedropper ────────────────────────────────────────────────────────

    def _on_pick_toggled(self, checked: bool):
        self._pick_mode = checked
        cursor = Qt.CursorShape.CrossCursor if checked else Qt.CursorShape.ArrowCursor
        self._preview.setCursor(QCursor(cursor))

    def _on_preview_clicked(self, pos: QPoint):
        """Map a click on the displayed (letterboxed) preview to a thumbnail
        pixel, sample the HSV neighbourhood, and push to the sliders."""
        if not self._pick_mode:
            return

        # The pixmap is centred inside the label with KeepAspectRatio letterboxing.
        # Compute the rendered pixmap rect inside the label.
        pix = self._preview.pixmap()
        if pix is None or pix.isNull():
            return

        label_w = self._preview.width()
        label_h = self._preview.height()
        pix_w   = pix.width()
        pix_h   = pix.height()

        # Top-left offset of the pixmap within the label (centred)
        offset_x = (label_w - pix_w) // 2
        offset_y = (label_h - pix_h) // 2

        # Click relative to the pixmap
        rel_x = pos.x() - offset_x
        rel_y = pos.y() - offset_y

        if not (0 <= rel_x < pix_w and 0 <= rel_y < pix_h):
            return  # Click was in the letterbox border

        # Scale from displayed pixmap coords → thumbnail coords
        thumb_h, thumb_w = self._thumb_bgr.shape[:2]
        tx = int(rel_x * thumb_w / pix_w)
        ty = int(rel_y * thumb_h / pix_h)

        lo, hi = sample_hsv_range(self._thumb_bgr, tx, ty, radius=5)

        # Block slider signals while setting both groups to avoid double refresh
        self._lower_group.set_values(lo)
        self._upper_group.set_values(hi)

        # Deactivate pick mode (one-shot)
        self._btn_pick.setChecked(False)
