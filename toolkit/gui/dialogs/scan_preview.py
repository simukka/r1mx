"""ScanPreviewDialog — review and confirm scan results before saving.

Displays the warped board image with detected items overlaid as
QGraphicsItems.  Supports three interaction modes:

  Review     — default; shows summary + action buttons
  Annotate   — crosshair cursor; left-click adds a new item at that position
  Done       — returned to Review with annotated items merged in

The dialog returns Accepted when the user clicks "Confirm & Save".
It sets needs_retry=True when the user clicks "Adjust Parameters".

Usage::

    dlg = ScanPreviewDialog(scan_result, parent=self)
    code = dlg.exec()
    if code == QDialog.DialogCode.Accepted:
        save_to_db(dlg.confirmed_items())
    elif dlg.needs_retry():
        reopen_wizard_with(dlg.retry_opts())
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any

import numpy as np
from PyQt6.QtCore import Qt, QPointF, QRectF
from PyQt6.QtGui import (
    QBrush, QColor, QFont, QPen, QPolygonF, QCursor,
)
from PyQt6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QGraphicsEllipseItem,
    QGraphicsLineItem,
    QGraphicsPolygonItem,
    QGraphicsRectItem,
    QGraphicsScene,
    QGraphicsSimpleTextItem,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
)

from toolkit.gui.dialogs.scan_layer import ScanLayerResult
from toolkit.gui.viewer import ImageViewer, bgr_to_pixmap

# ---------------------------------------------------------------------------
# Overlay colours per scan type
# ---------------------------------------------------------------------------

_COLOURS = {
    "vias":    QColor(255,  80,  80),   # red
    "pads":    QColor(255, 200,   0),   # amber
    "traces":  QColor(  0, 140, 255),   # blue
    "text":    QColor(255, 160,  50),   # orange
    "outline": QColor(  0, 220, 255),   # cyan
}
_MANUAL_COLOUR = QColor(255, 255, 255)  # white for manually added items


# ---------------------------------------------------------------------------
# Helpers to build QGraphicsItems for each type
# ---------------------------------------------------------------------------

def _pen(colour: QColor, width: float = 1.5, cosmetic: bool = True) -> QPen:
    p = QPen(colour, width)
    p.setCosmetic(cosmetic)
    return p


def _draw_via(
    scene: QGraphicsScene,
    x_px: float,
    y_px: float,
    drill_px: float,
    annular_px: float,
    colour: QColor,
) -> list:
    r_drill  = drill_px / 2
    r_outer  = r_drill + annular_px
    items = []
    # Annular ring
    ring = QGraphicsEllipseItem(x_px - r_outer, y_px - r_outer, 2*r_outer, 2*r_outer)
    ring.setPen(_pen(colour, 1.5))
    ring.setBrush(QBrush(Qt.BrushStyle.NoBrush))
    ring.setZValue(5)
    scene.addItem(ring)
    items.append(ring)
    # Drill hole fill
    hole = QGraphicsEllipseItem(x_px - r_drill, y_px - r_drill, 2*r_drill, 2*r_drill)
    hole.setPen(QPen(Qt.PenStyle.NoPen))
    hole.setBrush(QBrush(colour.darker(180)))
    hole.setZValue(5)
    scene.addItem(hole)
    items.append(hole)
    return items


def _draw_pad(
    scene: QGraphicsScene,
    x_px: float,
    y_px: float,
    w_px: float,
    h_px: float,
    angle: float,
    colour: QColor,
    label: str = "",
) -> list:
    items = []
    rect = QGraphicsRectItem(-w_px / 2, -h_px / 2, w_px, h_px)
    rect.setPen(_pen(colour, 1.5))
    c = QColor(colour)
    c.setAlpha(60)
    rect.setBrush(QBrush(c))
    rect.setRotation(angle)
    rect.setPos(x_px, y_px)
    rect.setZValue(5)
    scene.addItem(rect)
    items.append(rect)
    if label:
        txt = QGraphicsSimpleTextItem(label)
        txt.setBrush(QBrush(colour))
        txt.setFont(QFont("monospace", 6))
        txt.setPos(x_px + 2, y_px + 2)
        txt.setZValue(6)
        scene.addItem(txt)
        items.append(txt)
    return items


def _draw_trace(
    scene: QGraphicsScene,
    sx: float, sy: float,
    ex: float, ey: float,
    colour: QColor,
) -> list:
    line = QGraphicsLineItem(sx, sy, ex, ey)
    line.setPen(_pen(colour, 1.2))
    line.setZValue(4)
    scene.addItem(line)
    return [line]


def _draw_text_box(
    scene: QGraphicsScene,
    x_px: float,
    y_px: float,
    label: str,
    colour: QColor,
) -> list:
    items = []
    txt = QGraphicsSimpleTextItem(label)
    txt.setBrush(QBrush(colour))
    txt.setFont(QFont("monospace", 7))
    txt.setPos(x_px, y_px)
    txt.setZValue(6)
    scene.addItem(txt)
    items.append(txt)
    br = txt.boundingRect()
    box = QGraphicsRectItem(x_px - 1, y_px - 1, br.width() + 2, br.height() + 2)
    box.setPen(_pen(colour, 1.0))
    box.setBrush(QBrush(Qt.BrushStyle.NoBrush))
    box.setZValue(5)
    scene.addItem(box)
    items.append(box)
    return items


def _draw_outline(
    scene: QGraphicsScene,
    pts_px: list[tuple[float, float]],
    colour: QColor,
) -> list:
    poly = QPolygonF([QPointF(x, y) for x, y in pts_px] + [QPointF(pts_px[0][0], pts_px[0][1])])
    item = QGraphicsPolygonItem(poly)
    item.setPen(_pen(colour, 2.0))
    item.setBrush(QBrush(Qt.BrushStyle.NoBrush))
    item.setZValue(3)
    scene.addItem(item)
    return [item]


# ---------------------------------------------------------------------------
# Overlay renderer
# ---------------------------------------------------------------------------

def _render_overlays(
    scene: QGraphicsScene,
    scan_type: str,
    items: list,
    px_per_mm: float,
    colour: QColor,
) -> list:
    """Draw all items on *scene*, return list of added QGraphicsItems."""
    added = []
    t = scan_type

    if t == "vias":
        for via in items:
            x_px  = via["x_mm"]  * px_per_mm
            y_px  = via["y_mm"]  * px_per_mm
            drill = via.get("drill_mm", 0.3) * px_per_mm
            ann   = via.get("annular_mm", 0.15) * px_per_mm
            added += _draw_via(scene, x_px, y_px, drill, ann, colour)

    elif t == "pads":
        for pad in items:
            x_px = pad["x_mm"] * px_per_mm
            y_px = pad["y_mm"] * px_per_mm
            w_px = pad["w_mm"] * px_per_mm
            h_px = pad["h_mm"] * px_per_mm
            added += _draw_pad(scene, x_px, y_px, w_px, h_px,
                               pad.get("rotation_deg", 0), colour,
                               label=pad.get("ref", ""))

    elif t == "traces":
        for tr in items:
            sx, sy = tr["start"][0] * px_per_mm, tr["start"][1] * px_per_mm
            ex, ey = tr["end"][0]   * px_per_mm, tr["end"][1]   * px_per_mm
            added += _draw_trace(scene, sx, sy, ex, ey, colour)

    elif t == "text":
        for entry in items:
            x_px = getattr(entry, "x_mm", -1.0) * px_per_mm
            y_px = getattr(entry, "y_mm", -1.0) * px_per_mm
            if x_px < 0 or y_px < 0:
                continue
            added += _draw_text_box(scene, x_px, y_px,
                                    getattr(entry, "label", str(entry)), colour)

    elif t == "outline":
        if items:
            pts = [(p[0] * px_per_mm, p[1] * px_per_mm) for p in items]
            added += _draw_outline(scene, pts, colour)

    return added


# ---------------------------------------------------------------------------
# Main Dialog
# ---------------------------------------------------------------------------

class ScanPreviewDialog(QDialog):
    """Show scan results overlaid on the board image; let user confirm or annotate.

    After exec():
        .confirmed_items()  — final (auto + manually-added) item list
        .needs_retry()      — True if user wants to re-tune parameters
        .retry_opts()       — original opts dict for re-opening the wizard
    """

    _MODE_REVIEW   = "review"
    _MODE_ANNOTATE = "annotate"

    def __init__(self, scan_result: ScanLayerResult, parent=None):
        super().__init__(parent)
        self._result     = scan_result
        self._scan_type  = scan_result.scan_type
        self._items      = list(scan_result.items)
        self._manual     = []          # items added by hand
        self._overlay_gfx: list = []   # QGraphicsItems for auto-detected
        self._manual_gfx: list = []    # QGraphicsItems for manual additions
        self._mode       = self._MODE_REVIEW
        self._retry      = False

        bgr       = scan_result.opts.get("_bgr")
        self._px  = float(scan_result.opts.get("_px_per_mm") or 20.0)
        self._bgr = bgr

        self.setWindowTitle(f"Scan Preview — {self._scan_type}")
        self.setMinimumSize(1000, 680)
        self.setSizeGripEnabled(True)

        # ── Viewer ────────────────────────────────────────────────────
        self._viewer = ImageViewer(self)
        self._scene  = self._viewer.scene()

        if bgr is not None:
            self._viewer.set_image(bgr)

        # ── Summary banner ────────────────────────────────────────────
        self._summary = QLabel()
        self._summary.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._summary.setStyleSheet(
            "background: #1e3a1e; color: #90ee90; "
            "padding: 6px; font-weight: bold; border-radius: 4px;"
        )
        self._update_summary()

        # ── Annotation hint ───────────────────────────────────────────
        self._hint = QLabel(
            "Click on the board image to mark a missed item.  "
            "Right-click or press Esc to finish."
        )
        self._hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._hint.setStyleSheet("color: #ffcc00; font-style: italic;")
        self._hint.setVisible(False)

        # ── Action buttons ────────────────────────────────────────────
        self._btn_confirm = QPushButton("✓  Confirm && Save")
        self._btn_confirm.setDefault(True)
        self._btn_confirm.clicked.connect(self._on_confirm)

        self._btn_add = QPushButton("+ Add Missed Item")
        self._btn_add.setCheckable(True)
        self._btn_add.clicked.connect(self._on_add_missed)

        self._btn_done_add = QPushButton("✓ Done Adding")
        self._btn_done_add.setVisible(False)
        self._btn_done_add.clicked.connect(self._on_done_adding)

        self._btn_retry = QPushButton("⟳  Adjust Parameters")
        self._btn_retry.clicked.connect(self._on_retry)

        self._btn_cancel = QPushButton("Cancel")
        self._btn_cancel.clicked.connect(self.reject)

        btn_row = QHBoxLayout()
        btn_row.addWidget(self._btn_confirm)
        btn_row.addWidget(self._btn_add)
        btn_row.addWidget(self._btn_done_add)
        btn_row.addStretch()
        btn_row.addWidget(self._btn_retry)
        btn_row.addWidget(self._btn_cancel)

        # ── Root layout ───────────────────────────────────────────────
        root = QVBoxLayout(self)
        root.addWidget(self._summary)
        root.addWidget(self._hint)
        root.addWidget(self._viewer, stretch=1)
        root.addLayout(btn_row)

        # Connect viewer click for annotation mode
        self._viewer.imageClicked.connect(self._on_image_click)

        # Draw initial overlays
        self._draw_all_overlays()

    # ------------------------------------------------------------------
    # Public
    # ------------------------------------------------------------------

    def confirmed_items(self) -> list:
        """All items (auto-detected + manually annotated)."""
        return self._items + self._manual

    def needs_retry(self) -> bool:
        return self._retry

    def retry_opts(self) -> dict:
        opts = dict(self._result.opts)
        opts.pop("_bgr", None)
        opts.pop("_px_per_mm", None)
        return opts

    # ------------------------------------------------------------------
    # Button handlers
    # ------------------------------------------------------------------

    def _on_confirm(self):
        self.accept()

    def _on_retry(self):
        self._retry = True
        self.reject()

    def _on_add_missed(self, checked: bool):
        if checked:
            self._set_mode(self._MODE_ANNOTATE)
        else:
            self._set_mode(self._MODE_REVIEW)

    def _on_done_adding(self):
        self._set_mode(self._MODE_REVIEW)
        self._btn_add.setChecked(False)

    # ------------------------------------------------------------------
    # Annotation
    # ------------------------------------------------------------------

    def _set_mode(self, mode: str):
        self._mode = mode
        is_ann = (mode == self._MODE_ANNOTATE)
        self._hint.setVisible(is_ann)
        self._btn_done_add.setVisible(is_ann)
        self._btn_confirm.setEnabled(not is_ann)
        self._btn_retry.setEnabled(not is_ann)
        if is_ann:
            self._viewer.setCursor(QCursor(Qt.CursorShape.CrossCursor))
            self._viewer.set_crosshair_visible(True)
        else:
            self._viewer.setCursor(QCursor(Qt.CursorShape.ArrowCursor))
            self._viewer.set_crosshair_visible(False)

    def _on_image_click(self, pos: QPointF):
        if self._mode != self._MODE_ANNOTATE:
            return
        x_px, y_px = pos.x(), pos.y()
        x_mm = round(x_px / self._px, 4)
        y_mm = round(y_px / self._px, 4)
        item = self._make_manual_item(x_mm, y_mm, x_px, y_px)
        if item is not None:
            self._manual.append(item)
            self._draw_manual_item(item)
            self._update_summary()

    def _make_manual_item(
        self,
        x_mm: float, y_mm: float,
        x_px: float, y_px: float,
    ) -> Any | None:
        """Prompt the user for any extra info and return a new item dict."""
        t = self._scan_type
        if t == "vias":
            drill, ok = QInputDialog.getDouble(
                self, "Via Drill Size",
                "Drill diameter (mm):", 0.3, 0.05, 3.0, 3
            )
            if not ok:
                return None
            return {
                "x_mm": x_mm, "y_mm": y_mm,
                "drill_mm": drill, "annular_mm": 0.15,
                "_manual": True,
            }
        if t == "pads":
            ref, ok = QInputDialog.getText(
                self, "Pad Reference", "Ref designator (leave blank if unknown):"
            )
            return {
                "x_mm": x_mm, "y_mm": y_mm,
                "w_mm": 1.0, "h_mm": 0.6,
                "rotation_deg": 0,
                "layer": "F_Cu",
                "ref": ref.strip() if ok else "",
                "_manual": True,
            }
        if t == "text":
            label, ok = QInputDialog.getText(
                self, "Text Label", "Reference designator or part number:"
            )
            if not ok or not label.strip():
                return None
            # Return a simple dict (not BomEntry) — app.py handles both
            return {
                "label": label.strip(),
                "ref_type": "RefDes",
                "x_mm": x_mm, "y_mm": y_mm,
                "confidence": 1.0,
                "_manual": True,
            }
        if t == "outline":
            return [x_mm, y_mm]
        if t == "traces":
            QMessageBox.information(
                self, "Trace Annotation",
                "Click a second point to define the trace end.\n"
                "(Trace annotation requires two clicks — feature coming soon.)"
            )
            return None
        return None

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape and self._mode == self._MODE_ANNOTATE:
            self._on_done_adding()
        else:
            super().keyPressEvent(event)

    # ------------------------------------------------------------------
    # Overlay drawing
    # ------------------------------------------------------------------

    def _draw_all_overlays(self):
        colour = _COLOURS.get(self._scan_type, QColor(0, 255, 120))
        self._overlay_gfx = _render_overlays(
            self._scene, self._scan_type, self._items, self._px, colour
        )

    def _draw_manual_item(self, item):
        """Draw a single manually-added item in white."""
        t = self._scan_type
        if t == "vias":
            self._manual_gfx += _draw_via(
                self._scene,
                item["x_mm"] * self._px, item["y_mm"] * self._px,
                item["drill_mm"] * self._px, item["annular_mm"] * self._px,
                _MANUAL_COLOUR,
            )
        elif t == "pads":
            self._manual_gfx += _draw_pad(
                self._scene,
                item["x_mm"] * self._px, item["y_mm"] * self._px,
                item["w_mm"] * self._px, item["h_mm"] * self._px,
                item["rotation_deg"], _MANUAL_COLOUR, label=item.get("ref", ""),
            )
        elif t == "text":
            self._manual_gfx += _draw_text_box(
                self._scene,
                item["x_mm"] * self._px, item["y_mm"] * self._px,
                item.get("label", "?"), _MANUAL_COLOUR,
            )
        elif t == "outline" and isinstance(item, list):
            # Single point marker
            x_px, y_px = item[0] * self._px, item[1] * self._px
            dot = QGraphicsEllipseItem(x_px - 4, y_px - 4, 8, 8)
            dot.setPen(_pen(_MANUAL_COLOUR, 1.5))
            dot.setBrush(QBrush(_MANUAL_COLOUR))
            dot.setZValue(7)
            self._scene.addItem(dot)
            self._manual_gfx.append(dot)

    # ------------------------------------------------------------------
    # Summary
    # ------------------------------------------------------------------

    def _update_summary(self):
        n_auto   = len(self._items)
        n_manual = len(self._manual)
        t        = self._scan_type
        labels   = {
            "text":    "text items",
            "vias":    "vias",
            "pads":    "pads",
            "traces":  "trace segments",
            "outline": "outline points",
        }
        label = labels.get(t, "items")
        parts = [f"<b>{n_auto}</b> {label} detected automatically"]
        if n_manual:
            parts.append(f"<b>{n_manual}</b> added manually")
        self._summary.setText("  ·  ".join(parts))
