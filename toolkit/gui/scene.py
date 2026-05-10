"""Scene primitives for calibrated layers."""
from __future__ import annotations

import json
from pathlib import Path

import cv2
import numpy as np
from PyQt6.QtCore import QPointF, Qt
from PyQt6.QtGui import QBrush, QColor, QFont, QPainterPath, QPen, QPolygonF
from PyQt6.QtWidgets import (
    QGraphicsEllipseItem,
    QGraphicsItemGroup,
    QGraphicsPathItem,
    QGraphicsPixmapItem,
    QGraphicsPolygonItem,
    QGraphicsRectItem,
    QGraphicsScene,
    QGraphicsSimpleTextItem,
)

from toolkit.db import DB
from toolkit.gui.viewer import bgr_to_pixmap

_REPO = Path(__file__).resolve().parents[2]

_IMAGE_EXTS = {'.jpg', '.jpeg', '.png', '.tif', '.tiff', '.bmp', '.JPG', '.JPEG', '.PNG'}

OBJECT_TYPES = [
    ("photo",        "Photo",          QColor(200, 200, 200)),
    ("copper_area",  "Copper",         QColor(180, 120,   0)),
    ("outline",      "Outline",        QColor(  0, 180, 255)),
    ("via",          "Vias",           QColor(255,  80,  80)),
    ("pad",          "Pads",           QColor(255, 200,   0)),
    ("component",    "Components",     QColor(  0, 255, 120)),
    ("text_label",   "Part Numbers",   QColor(255, 160,  50)),
    ("trace",        "Traces",         QColor(  0, 120, 255)),
]

LAYER_COLORS = {
    "top":    QColor(  0, 200, 100),
    "bottom": QColor(200, 100,   0),
}

class LayerScene:
    """Manages QGraphicsScene groups for a single board layer."""

    def __init__(self, scene: QGraphicsScene, board: str, layer: str):
        self.board  = board
        self.layer  = layer
        self._scene = scene
        self._groups: dict[str, QGraphicsItemGroup] = {}

        # Create a group per object type (+ "photo")
        for key, _, _ in [("photo", "", None)] + list(OBJECT_TYPES):
            g = QGraphicsItemGroup()
            scene.addItem(g)
            self._groups[key] = g

    def group(self, key: str) -> QGraphicsItemGroup | None:
        return self._groups.get(key)

    def set_visible(self, key: str, visible: bool):
        if key in self._groups:
            self._groups[key].setVisible(visible)

    def set_all_visible(self, visible: bool):
        for g in self._groups.values():
            g.setVisible(visible)

    def clear_group(self, key: str):
        g = self._groups.get(key)
        if g:
            for item in g.childItems():
                self._scene.removeItem(item)

    def load_photo(self, board_name: str, layer_name: str, source_image: str, warp_matrix, warped_size):
        """Load and display the calibrated (warped) board photo."""
        import cv2
        board_dir = _REPO / "components" / board_name
        img_path = board_dir / source_image
        if not img_path.exists():
            return
        img = cv2.imread(str(img_path))
        if img is None:
            return

        if warp_matrix and warped_size:
            M = np.array(warp_matrix, dtype=np.float64)
            w, h = warped_size
            img = cv2.warpPerspective(img, M, (w, h))

        pixmap = bgr_to_pixmap(img)
        item = QGraphicsPixmapItem(pixmap)
        item.setZValue(0)
        g = self._groups["photo"]
        g.addToGroup(item)

    def load_objects(self, db: DB, layer_id: int, px_per_mm: float = 20.0):
        """Load extracted objects from DB and create scene items.

        Traces are batched into a single QGraphicsPathItem per group for
        performance — rendering 250k line items individually is too slow.
        """
        # colour map by type
        _color = {key: col for key, _, col in OBJECT_TYPES}

        for key, _, color in OBJECT_TYPES:
            if key == "photo":
                continue
            g = self._groups[key]
            # Clear old children
            for child in list(g.childItems()):
                g.removeFromGroup(child)
                self._scene.removeItem(child)

            objects = db.list_objects(layer_id, type_filter=key)
            if not objects:
                continue

            if key == "trace":
                # Batch all segments into one QPainterPath per layer group
                path = QPainterPath()
                for obj in objects:
                    props = json.loads(obj["properties"] or "{}")
                    s = props.get("start")
                    e = props.get("end")
                    if s and e:
                        path.moveTo(s[0] * px_per_mm, s[1] * px_per_mm)
                        path.lineTo(e[0] * px_per_mm, e[1] * px_per_mm)
                pen = QPen(color, 0)        # width=0 → cosmetic hairline
                pen.setCosmetic(True)
                path_item = QGraphicsPathItem(path)
                path_item.setPen(pen)
                path_item.setZValue(2)
                g.addToGroup(path_item)

            elif key == "outline":
                for obj in objects:
                    props = json.loads(obj["properties"] or "{}")
                    pts = props.get("points", [])
                    if len(pts) >= 2:
                        poly = QPolygonF([
                            QPointF(p[0] * px_per_mm, p[1] * px_per_mm)
                            for p in pts
                        ])
                        item = QGraphicsPolygonItem(poly)
                        pen = QPen(color, 2)
                        pen.setCosmetic(True)
                        item.setPen(pen)
                        item.setBrush(QBrush(Qt.GlobalColor.transparent))
                        item.setZValue(5)
                        g.addToGroup(item)

            else:
                for obj in objects:
                    item = self._make_item(obj, color, px_per_mm)
                    if item:
                        g.addToGroup(item)

    def _make_item(self, obj, color: QColor, px_per_mm: float = 20.0):
        """Convert a DB object row into a QGraphicsItem."""
        x  = (obj["x_mm"]      or 0) * px_per_mm
        y  = (obj["y_mm"]      or 0) * px_per_mm
        w  = (obj["width_mm"]  or 1) * px_per_mm
        h  = (obj["height_mm"] or 1) * px_per_mm
        t  = obj["type"]

        if t == "via":
            r = w / 2
            item = QGraphicsEllipseItem(x - r, y - r, w, h)
            pen = QPen(color, 1)
            pen.setCosmetic(True)
            item.setPen(pen)
            item.setBrush(QBrush(Qt.GlobalColor.transparent))
            item.setZValue(3)
            return item

        if t in ("pad", "component"):
            rot = obj["rotation_deg"] or 0.0
            item = QGraphicsRectItem(-w / 2, -h / 2, w, h)
            pen = QPen(color, 1)
            pen.setCosmetic(True)
            item.setPen(pen)
            item.setBrush(QBrush(Qt.GlobalColor.transparent))
            item.setZValue(4)
            item.setFlag(item.GraphicsItemFlag.ItemIsSelectable)
            item.setData(0, obj["id"])
            item.setPos(x, y)
            if rot:
                item.setRotation(rot)

            # Add a text label for component items
            if t == "component" and obj["label"]:
                label_item = QGraphicsSimpleTextItem(obj["label"])
                font = QFont("monospace", 5)
                label_item.setFont(font)
                label_item.setBrush(QBrush(color))
                label_item.setZValue(6)
                label_item.setParentItem(item)
                label_item.setPos(w / 2 + 2, -4)

            return item

        if t == "text_label" and obj["label"]:
            item = QGraphicsSimpleTextItem(obj["label"])
            font = QFont("monospace", 5)
            item.setFont(font)
            item.setBrush(QBrush(color))
            item.setZValue(5)
            item.setFlag(item.GraphicsItemFlag.ItemIsSelectable)
            item.setData(0, obj["id"])
            item.setPos(x, y)
            return item

        return None


# ═══════════════════════════════════════════════════════════════════════════
# MainWindow
# ═══════════════════════════════════════════════════════════════════════════
