"""Scene primitives for calibrated layers."""
from __future__ import annotations

import json
from pathlib import Path

import cv2
import numpy as np
from PyQt6.QtCore import QPointF, QRectF, Qt
from PyQt6.QtGui import (
    QBrush,
    QColor,
    QFont,
    QPainterPath,
    QPen,
    QPolygonF,
    QRadialGradient,
    QTransform,
)
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

from toolkit.analysis.orientation import inward_triangle_points
from toolkit.db import DB
from toolkit.gui.theme import THEME
from toolkit.gui.viewer import bgr_to_pixmap
from toolkit.paths import COMPONENTS_DIR

_IMAGE_EXTS = {'.jpg', '.jpeg', '.png', '.tif', '.tiff', '.bmp', '.JPG', '.JPEG', '.PNG'}

# Object-type registry — (db_key, display_label, colour).
# Colours come from the active THEME so swapping the theme changes the palette.
OBJECT_TYPES = [
    ("photo",        "Photo",        THEME.photo_color),
    ("copper_area",  "Copper",       THEME.copper_color),
    ("outline",      "Outline",      THEME.outline_color),
    ("via",          "Vias",         THEME.via_color),
    ("pad",          "Pads",         THEME.pad_color),
    ("component",    "Components",   THEME.component_color),
    ("text_label",   "Part Numbers", THEME.text_label_color),
    ("trace",        "Traces",       THEME.trace_color),
    ("pin",          "Pins",         THEME.pin_color),
]

LAYER_COLORS: dict[str, QColor] = {
    "top":    THEME.layer_top_color,
    "bottom": THEME.layer_bottom_color,
}

class LayerScene:
    """Manages QGraphicsScene groups for a single board layer."""

    # Z of the layer root group: the active layer sits at the base, overlays
    # render above it (semi-transparent ghost) but below the viewer's own
    # crosshair / rubber-band items (Z >= 9).
    _Z_ACTIVE  = 0.0
    _Z_OVERLAY = 2.0

    def __init__(self, scene: QGraphicsScene, board: str, layer: str):
        self.board  = board
        self.layer  = layer
        self._scene = scene
        self._groups: dict[str, QGraphicsItemGroup] = {}
        self._vignette_item: QGraphicsPathItem | None = None  # spotlight overlay
        self._original_img: np.ndarray | None = None          # stored for live enhancement

        # Root group carries the cross-layer alignment transform so the whole
        # layer can be registered into the shared board frame at once.
        self._root = QGraphicsItemGroup()
        scene.addItem(self._root)

        # Create a group per object type (+ "photo"), parented to the root so
        # the alignment transform / opacity applies to all of them together.
        for key, _, _ in [("photo", "", None)] + list(OBJECT_TYPES):
            g = QGraphicsItemGroup()
            g.setParentItem(self._root)
            self._groups[key] = g

    def group(self, key: str) -> QGraphicsItemGroup | None:
        return self._groups.get(key)

    def set_visible(self, key: str, visible: bool):
        if key in self._groups:
            self._groups[key].setVisible(visible)

    def set_all_visible(self, visible: bool):
        for g in self._groups.values():
            g.setVisible(visible)

    # ── Cross-layer alignment & overlay ──────────────────────────────────────

    def set_board_transform(self, matrix_2x3) -> None:
        """Register this layer into the shared board frame.

        *matrix_2x3* is a 2x3 affine ``[[a, b, tx], [c, d, ty]]`` mapping this
        layer's warped-pixel (scene) coords into the reference layer's frame.
        Passing a falsy value resets to identity (the reference layer).
        """
        if not matrix_2x3:
            self._root.setTransform(QTransform())
            return
        (a, b, tx), (c, d, ty) = matrix_2x3
        # Qt's QTransform takes column-major args: (m11, m12, m21, m22, dx, dy)
        self._root.setTransform(QTransform(a, c, b, d, tx, ty))

    def set_overlay(self, opacity: float | None) -> None:
        """Mark this layer active (``opacity is None``) or an overlay.

        Active  → fully opaque, base Z, items selectable/interactive.
        Overlay → semi-transparent at *opacity*, raised Z so it ghosts over the
                  active layer, and non-interactive (its items can't be
                  clicked/selected, so it never interferes with the active layer).
        """
        if opacity is None:
            self._root.setOpacity(1.0)
            self._root.setZValue(self._Z_ACTIVE)
            self._set_items_selectable(True)
        else:
            self._root.setOpacity(max(0.0, min(1.0, opacity)))
            self._root.setZValue(self._Z_OVERLAY)
            self._set_items_selectable(False)

    def _set_items_selectable(self, selectable: bool) -> None:
        for key, g in self._groups.items():
            if key == "photo":
                continue
            for child in g.childItems():
                child.setFlag(
                    child.GraphicsItemFlag.ItemIsSelectable, selectable
                )

    def clear_group(self, key: str):
        g = self._groups.get(key)
        if g:
            for item in g.childItems():
                self._scene.removeItem(item)

    # ── Vignette spotlight ───────────────────────────────────────────────────

    def highlight_object(self, object_id: int) -> bool:
        """Draw a radial vignette spotlight centred on the object with *object_id*.

        The scene is darkened everywhere except around the selected item.
        Returns True if the object was found and highlighted.
        """
        self.clear_highlight()

        # Find the graphics item tagged with this object_id
        target = None
        for key, group in self._groups.items():
            if key == "photo":
                continue
            for child in group.childItems():
                if child.data(0) == object_id:
                    target = child
                    break
            if target is not None:
                break

        if target is None:
            return False

        # Scene rect — cover the entire board image
        scene_rect = self._scene.sceneRect()

        # Spotlight centre & radius from the item's scene bounding rect
        item_scene_rect = target.mapToScene(target.boundingRect()).boundingRect()
        cx = item_scene_rect.center().x()
        cy = item_scene_rect.center().y()
        # Spotlight radius: generous so nearby neighbours are visible
        spot_r = max(item_scene_rect.width(), item_scene_rect.height()) * 3 + 40

        # Radial gradient: transparent centre → dark edges
        grad = QRadialGradient(cx, cy, spot_r)
        vc = THEME.vignette_color
        grad.setColorAt(0.0, QColor(vc.red(), vc.green(), vc.blue(),   0))
        grad.setColorAt(0.4, QColor(vc.red(), vc.green(), vc.blue(),   0))
        grad.setColorAt(1.0, QColor(vc.red(), vc.green(), vc.blue(), THEME.vignette_alpha))

        # Extend gradient coverage so the corners of the scene are fully dark
        grad.setSpread(QRadialGradient.Spread.PadSpread)

        # The path is just the full scene rect — the gradient does all the work
        path = QPainterPath()
        # Use a rect large enough to cover the whole scene even during zoom/pan
        margin = max(scene_rect.width(), scene_rect.height())
        big = scene_rect.adjusted(-margin, -margin, margin, margin)
        path.addRect(big)

        self._vignette_item = QGraphicsPathItem(path)
        self._vignette_item.setPen(QPen(Qt.PenStyle.NoPen))
        self._vignette_item.setBrush(QBrush(grad))
        self._vignette_item.setZValue(50)   # above objects, below nothing
        self._vignette_item.setAcceptedMouseButtons(Qt.MouseButton.NoButton)
        self._scene.addItem(self._vignette_item)
        return True

    def clear_highlight(self) -> None:
        """Remove the vignette spotlight overlay if present."""
        if self._vignette_item is not None:
            self._scene.removeItem(self._vignette_item)
            self._vignette_item = None

    def load_photo(
        self,
        board_name: str,
        layer_name: str,
        source_image: str,
        warp_matrix,
        warped_size,
        board_dir: Path | None = None,
    ):
        """Load and display the calibrated (warped) board photo.

        Parameters
        ----------
        board_dir : resolved absolute path to the board directory.
                    Falls back to ``COMPONENTS_DIR / board_name`` when not given.
        """
        import cv2
        if board_dir is None:
            board_dir = COMPONENTS_DIR / board_name
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

        self._original_img = img.copy()
        pixmap = bgr_to_pixmap(img)
        item = QGraphicsPixmapItem(pixmap)
        item.setZValue(0)
        g = self._groups["photo"]
        g.addToGroup(item)

    def apply_photo_enhancement(
        self,
        brightness: int = 0,
        contrast: float = 1.0,
        gamma: float = 1.0,
        sharpen: bool = False,
        invert: bool = False,
    ) -> None:
        """Apply temporary visual adjustments to the layer photo.

        Operates on a copy of ``_original_img`` — the source file is never
        modified.  Call with all defaults to restore the original display.

        Parameters
        ----------
        brightness : integer offset added to every channel (−100 … +100)
        contrast   : multiplicative factor centred on mid-grey (0.1 … 3.0)
        gamma      : gamma correction  (0.2 … 3.0; >1 brightens shadows)
        sharpen    : apply unsharp-mask sharpening kernel
        invert     : invert all channels (255 − value)
        """
        if self._original_img is None:
            return

        img = self._original_img.astype(np.int16)

        # 1. Brightness
        if brightness != 0:
            img = img + brightness

        # 2. Contrast  (centred on mid-grey = 128)
        if contrast != 1.0:
            img = (img.astype(np.float32) - 128.0) * contrast + 128.0

        img = np.clip(img, 0, 255).astype(np.uint8)

        # 3. Gamma via LUT
        if gamma != 1.0:
            inv_gamma = 1.0 / max(gamma, 0.01)
            lut = np.array(
                [((i / 255.0) ** inv_gamma) * 255 for i in range(256)],
                dtype=np.uint8,
            )
            img = cv2.LUT(img, lut)

        # 4. Sharpen (unsharp mask)
        if sharpen:
            kernel = np.array(
                [[ 0, -1,  0],
                 [-1,  5, -1],
                 [ 0, -1,  0]], dtype=np.float32,
            )
            img = cv2.filter2D(img, -1, kernel)

        # 5. Invert
        if invert:
            img = 255 - img

        pixmap = bgr_to_pixmap(img)

        # Replace the photo group's pixmap item in-place
        g = self._groups["photo"]
        for child in list(g.childItems()):
            if isinstance(child, QGraphicsPixmapItem):
                child.setPixmap(pixmap)
                return
        # No existing item — add a new one
        item = QGraphicsPixmapItem(pixmap)
        item.setZValue(0)
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
                    wpts = props.get("waypoints")
                    if wpts and len(wpts) >= 2:
                        # New format: multi-point routed trace
                        path.moveTo(wpts[0][0] * px_per_mm, wpts[0][1] * px_per_mm)
                        for p in wpts[1:]:
                            path.lineTo(p[0] * px_per_mm, p[1] * px_per_mm)
                    else:
                        # Legacy format: single start/end segment
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
            pen = QPen(THEME.via_outline_color, 1.5)
            pen.setCosmetic(True)
            item.setPen(pen)
            vc = THEME.via_color
            item.setBrush(QBrush(QColor(vc.red(), vc.green(), vc.blue(), THEME.via_fill_alpha)))
            item.setZValue(3)
            return item

        if t in ("pad", "component"):
            rot = obj["rotation_deg"] or 0.0
            item = QGraphicsRectItem(0, 0, w, h)
            pen = QPen(color, 1)
            pen.setCosmetic(True)
            item.setPen(pen)
            item.setBrush(QBrush(Qt.GlobalColor.transparent))
            item.setZValue(4)
            item.setFlag(item.GraphicsItemFlag.ItemIsSelectable)
            item.setData(0, obj["id"])
            item.setPos(x, y)
            if rot:
                item.setTransformOriginPoint(w / 2, h / 2)
                item.setRotation(rot)

            # Add a text label for component items
            if t == "component" and obj["label"]:
                label_item = QGraphicsSimpleTextItem(obj["label"])
                font = QFont("monospace", 5)
                label_item.setFont(font)
                label_item.setBrush(QBrush(color))
                label_item.setZValue(6)
                label_item.setParentItem(item)
                label_item.setPos(w + 2, 0)

            # Draw pin-1 orientation triangle if set
            props = json.loads(obj["properties"] or "{}")
            pin1_edge = props.get("pin1_edge")
            if pin1_edge:
                tri_size = max(4.0, min(w, h) / 6.0)
                pts = inward_triangle_points(pin1_edge, 0, 0, w, h, tri_size)
                poly = QPolygonF([QPointF(px, py) for px, py in pts])
                tri = QGraphicsPolygonItem(poly)
                tri.setPen(QPen(Qt.PenStyle.NoPen))
                tri.setBrush(QBrush(color))
                tri.setZValue(5)
                tri.setParentItem(item)

            return item

        if t == "pin":
            # Small filled circle — 6 px cosmetic diameter
            r = 3.0
            item = QGraphicsEllipseItem(-r, -r, r * 2, r * 2)
            pen = QPen(color, 1)
            pen.setCosmetic(True)
            item.setPen(pen)
            item.setBrush(QBrush(color))
            item.setZValue(7)
            item.setFlag(item.GraphicsItemFlag.ItemIsSelectable)
            item.setData(0, obj["id"])
            item.setPos(x, y)

            # Small label: pin_number if set, else label
            lbl = obj["label"] or ""
            if lbl:
                lbl_item = QGraphicsSimpleTextItem(lbl)
                font = QFont("monospace", 4)
                lbl_item.setFont(font)
                lbl_item.setBrush(QBrush(color))
                lbl_item.setZValue(8)
                lbl_item.setParentItem(item)
                lbl_item.setPos(r + 1, -r)

            return item

        return None


# ═══════════════════════════════════════════════════════════════════════════
# MainWindow
# ═══════════════════════════════════════════════════════════════════════════
