"""
footprint_overlay.py — FootprintOverlayItem

A QGraphicsItem that renders an extracted pinout footprint as an overlay on
the main canvas.  Used during the alignment step after the pinout wizard.

The item is positioned at the component's top-left corner (in scene coords,
i.e. mm × px_per_mm) and draws each pad at its relative position within
the component's bounding box.

Keyboard-driven transforms (handled by the parent MainWindow):

    R               Rotate 90° clockwise
    Shift+R         Rotate 90° counter-clockwise
    +               Scale up by 10%
    -               Scale down by 10%
    Arrow keys      Translate by 0.5 mm (× px_per_mm for scene units)
    Enter           Accept — caller calls ``to_component_relative_coords()``
    Escape          Cancel
"""

from __future__ import annotations

import math
from typing import Sequence

from PyQt6.QtCore import QPointF, QRectF, Qt
from PyQt6.QtGui import QBrush, QColor, QFont, QPainter, QPen
from PyQt6.QtWidgets import QGraphicsItem

from toolkit.analysis.pinout import PadDetection, PinoutResult


# Visual styling
_PAD_RADIUS_FRAC   = 0.025   # pad radius as fraction of overlay width (fallback)
_PAD_COLOR         = QColor(255, 200, 0, 220)     # gold
_PAD_OUTLINE       = QColor(200, 100, 0, 255)
_PIN_LABEL_COLOR   = QColor(255, 255, 255, 230)
_OUTLINE_COLOR     = QColor(0, 255, 120, 160)
_OUTLINE_WIDTH_PX  = 2


class FootprintOverlayItem(QGraphicsItem):
    """Overlay that renders detected pads on the canvas for alignment.

    Parameters
    ----------
    pads : list[PadDetection]
        Pads with normalised (0–1) coordinates relative to the pinout crop.
    component_w_scene : float
        Component bounding-box width in scene units (mm × px_per_mm).
    component_h_scene : float
        Component bounding-box height in scene units.

    After alignment is confirmed, call ``to_component_relative_coords()`` to
    get the final per-pad (x_rel, y_rel) values in component bbox space.
    """

    def __init__(
        self,
        pads: list[PadDetection],
        component_w_scene: float,
        component_h_scene: float,
        parent: QGraphicsItem | None = None,
    ):
        super().__init__(parent)
        self._pads = pads
        self._base_w = component_w_scene
        self._base_h = component_h_scene

        # Cumulative transforms applied by the user
        self._angle_deg: float = 0.0
        self._scale:     float = 1.0
        self._offset_x:  float = 0.0   # scene units
        self._offset_y:  float = 0.0

        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, False)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, False)
        self.setZValue(1000)   # always on top

    # ── Geometry ────────────────────────────────────────────────────────────

    @property
    def _w(self) -> float:
        return self._base_w * self._scale

    @property
    def _h(self) -> float:
        return self._base_h * self._scale

    def boundingRect(self) -> QRectF:
        margin = max(self._w, self._h) * 0.5 + 20
        return QRectF(
            -self._w / 2 - margin,
            -self._h / 2 - margin,
            self._w + margin * 2,
            self._h + margin * 2,
        )

    # ── Public transform API ────────────────────────────────────────────────

    def rotate_by(self, degrees: float) -> None:
        """Rotate the overlay by *degrees* (positive = clockwise)."""
        self._angle_deg = (self._angle_deg + degrees) % 360
        self.prepareGeometryChange()
        self.update()

    def scale_by(self, factor: float) -> None:
        """Multiply the current scale by *factor*."""
        self._scale = max(0.05, min(20.0, self._scale * factor))
        self.prepareGeometryChange()
        self.update()

    def translate(self, dx: float, dy: float) -> None:
        """Translate the overlay in scene units."""
        self._offset_x += dx
        self._offset_y += dy
        self.setPos(self.pos() + QPointF(dx, dy))

    # ── Result extraction ───────────────────────────────────────────────────

    def to_component_relative_coords(self) -> list[dict]:
        """Return per-pad positions in component-bbox-relative (0–1) coords.

        Applies the current rotation and scale to the original pad positions.
        The returned list has the same order as the input *pads*.
        """
        angle_rad = math.radians(self._angle_deg)
        cos_a = math.cos(angle_rad)
        sin_a = math.sin(angle_rad)
        results = []
        for pad in self._pads:
            # Pad centre in [−0.5, +0.5] space (centred on overlay origin)
            px = (pad.cx - 0.5)
            py = (pad.cy - 0.5)
            # Rotate
            rx = cos_a * px - sin_a * py
            ry = sin_a * px + cos_a * py
            # Back to [0, 1]
            results.append({
                "pin_number": pad.pin_number,
                "label":      pad.label,
                "x_rel":      rx + 0.5,
                "y_rel":      ry + 0.5,
                "shape":      pad.shape,
                "shape_json": pad.bbox.to_dict(),
            })
        return results

    # ── Painting ─────────────────────────────────────────────────────────────

    def paint(
        self,
        painter: QPainter,
        option,
        widget=None,
    ) -> None:
        painter.save()

        # Apply rotation around overlay centre
        painter.translate(self._w / 2, self._h / 2)
        painter.rotate(self._angle_deg)
        painter.translate(-self._w / 2, -self._h / 2)

        # Outer bounding box
        pen = QPen(_OUTLINE_COLOR, _OUTLINE_WIDTH_PX, Qt.PenStyle.DashLine)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRect(QRectF(0, 0, self._w, self._h))

        # Pads
        pad_r = self._w * _PAD_RADIUS_FRAC
        font = QFont("monospace", max(6, int(pad_r * 0.8)))
        painter.setFont(font)

        for pad in self._pads:
            cx = pad.cx * self._w
            cy = pad.cy * self._h

            if pad.shape == "circle":
                r_x = max(pad.bbox.w * self._w / 2, pad_r)
                r_y = max(pad.bbox.h * self._h / 2, pad_r)
                painter.setPen(QPen(_PAD_OUTLINE, 1))
                painter.setBrush(QBrush(_PAD_COLOR))
                painter.drawEllipse(QPointF(cx, cy), r_x, r_y)
            else:
                bw = max(pad.bbox.w * self._w, pad_r * 2)
                bh = max(pad.bbox.h * self._h, pad_r * 2)
                painter.setPen(QPen(_PAD_OUTLINE, 1))
                painter.setBrush(QBrush(_PAD_COLOR))
                painter.drawRect(QRectF(cx - bw / 2, cy - bh / 2, bw, bh))

            # Pin label
            lbl = pad.pin_number or pad.label
            if lbl:
                painter.setPen(QPen(_PIN_LABEL_COLOR))
                painter.drawText(QPointF(cx + pad_r + 1, cy + pad_r), lbl)

        painter.restore()
