"""
viewer.py — shared PyQt6 GUI primitives for the r1mx reverse-engineering toolkit.

Provides:
  ImageViewer       QGraphicsView subclass that displays a numpy BGR image and
                    translates mouse events into image-pixel coordinates via
                    mapToScene().  Emits imageClicked(QPointF) and
                    imageMoved(QPointF) signals.

  bgr_to_pixmap()   Convert a numpy BGR array to QPixmap.
  mask_to_pixmap()  Convert a binary/grey mask to a semi-transparent QPixmap.

  Annotation helpers that add QGraphicsItems to a QGraphicsScene:
    draw_crosshair()    thin cross with gap at centre (follows mouse)
    draw_corner()       filled circle + label
    draw_ref_point()    filled circle + label
    draw_polyline()     connected line segments

All coordinates accepted and emitted by this module are in **image pixels**
(i.e. scene coordinates when the pixmap is placed at (0, 0) in the scene).
HiDPI is handled transparently by Qt — no manual scale factors needed.
"""

from __future__ import annotations

from typing import Sequence

import numpy as np

from PyQt6.QtCore import (
    Qt, QPointF, QRectF, pyqtSignal,
)
from PyQt6.QtGui import (
    QColor, QFont, QImage, QPainter, QPen, QPixmap, QBrush,
)
from PyQt6.QtWidgets import (
    QGraphicsEllipseItem, QGraphicsItem, QGraphicsLineItem,
    QGraphicsPixmapItem, QGraphicsScene, QGraphicsTextItem,
    QGraphicsView,
)


# ---------------------------------------------------------------------------
# Image conversion helpers
# ---------------------------------------------------------------------------

def bgr_to_pixmap(arr: np.ndarray) -> QPixmap:
    """Convert an OpenCV BGR uint8 array to QPixmap."""
    h, w = arr.shape[:2]
    rgb = arr[..., ::-1].copy()          # BGR → RGB, contiguous
    img = QImage(rgb.data, w, h, w * 3, QImage.Format.Format_RGB888)
    return QPixmap.fromImage(img)


def mask_to_pixmap(
    mask: np.ndarray,
    color: tuple[int, int, int] = (0, 255, 0),
    alpha: int = 120,
) -> QPixmap:
    """
    Convert a binary (0/255) or grey mask to a coloured semi-transparent QPixmap.

    Parameters
    ----------
    mask  : H×W uint8 array
    color : (R, G, B) overlay colour
    alpha : 0–255 opacity of the coloured region
    """
    h, w = mask.shape[:2]
    rgba = np.zeros((h, w, 4), dtype=np.uint8)
    m = mask > 0
    rgba[m, 0] = color[0]
    rgba[m, 1] = color[1]
    rgba[m, 2] = color[2]
    rgba[m, 3] = alpha
    img = QImage(rgba.data, w, h, w * 4, QImage.Format.Format_RGBA8888)
    return QPixmap.fromImage(img.copy())   # .copy() pins memory


# ---------------------------------------------------------------------------
# ImageViewer
# ---------------------------------------------------------------------------

class ImageViewer(QGraphicsView):
    """
    A QGraphicsView that:
      - Displays a numpy BGR image as a QPixmap scene item at (0, 0)
      - Fits the image to the window on first show (preserving aspect ratio)
      - Emits imageClicked(QPointF) with image-pixel coords on left click
      - Emits imageMoved(QPointF) with image-pixel coords on mouse move
      - Optionally tracks a crosshair overlay that follows the cursor

    Usage::

        viewer = ImageViewer()
        viewer.set_image(bgr_array)
        viewer.imageClicked.connect(on_click)
        viewer.imageMoved.connect(on_move)
        viewer.set_crosshair_visible(True)
    """

    imageClicked = pyqtSignal(QPointF)   # image-pixel coords
    imageMoved   = pyqtSignal(QPointF)   # image-pixel coords

    _XHAIR_ARM   = 20    # crosshair arm length in image pixels
    _XHAIR_GAP   = 4     # gap radius around the centre
    _ZOOM_STEP   = 1.25  # scale factor per zoom step
    _ZOOM_MIN    = 0.02  # lower bound (don't zoom out to nothing)
    _ZOOM_MAX    = 64.0  # upper bound

    def __init__(self, parent=None):
        super().__init__(parent)
        self._scene = QGraphicsScene(self)
        self.setScene(self._scene)

        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        self.setDragMode(QGraphicsView.DragMode.NoDrag)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorViewCenter)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setMouseTracking(True)

        self._pixmap_item: QGraphicsPixmapItem | None = None
        self._img_w = 0
        self._img_h = 0
        self._zoom_level: float = 1.0   # current cumulative scale factor

        # Crosshair overlay (four line segments)
        pen = QPen(QColor(0, 255, 255), 1.5)
        pen.setCosmetic(False)
        outline_pen = QPen(QColor(0, 0, 0), 3.5)
        outline_pen.setCosmetic(False)

        self._xhair_lines: list[QGraphicsLineItem] = []
        self._xhair_outlines: list[QGraphicsLineItem] = []
        for _ in range(4):     # left, right, top, bottom arm
            ol = QGraphicsLineItem()
            ol.setPen(outline_pen)
            ol.setZValue(9)
            ol.setVisible(False)
            self._scene.addItem(ol)
            self._xhair_outlines.append(ol)

            li = QGraphicsLineItem()
            li.setPen(pen)
            li.setZValue(10)
            li.setVisible(False)
            self._scene.addItem(li)
            self._xhair_lines.append(li)

        self._xhair_visible = False

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def set_image(self, arr: np.ndarray) -> None:
        """Replace the displayed image. Existing overlay items are kept."""
        pixmap = bgr_to_pixmap(arr)
        self._img_h, self._img_w = arr.shape[:2]

        if self._pixmap_item is None:
            self._pixmap_item = self._scene.addPixmap(pixmap)
            self._pixmap_item.setZValue(0)
        else:
            self._pixmap_item.setPixmap(pixmap)

        self._scene.setSceneRect(QRectF(0, 0, self._img_w, self._img_h))
        self.fit_image()

    def fit_image(self) -> None:
        """Fit the scene contents into the viewport, preserving aspect ratio.

        Works whether the image was loaded via set_image() or added directly
        to the scene (e.g. via LayerScene.load_photo()).
        """
        rect = self._scene.sceneRect()
        if not rect.isEmpty():
            self.fitInView(rect, Qt.AspectRatioMode.KeepAspectRatio)
            self._zoom_level = self.transform().m11()
            self._update_drag_mode()

    def zoom_in(self) -> None:
        """Zoom in one step, anchored to the mouse cursor."""
        self._apply_zoom(self._ZOOM_STEP)

    def zoom_out(self) -> None:
        """Zoom out one step, anchored to the mouse cursor."""
        self._apply_zoom(1.0 / self._ZOOM_STEP)

    def zoom_reset(self) -> None:
        """Return to 100 % (1 image pixel = 1 screen pixel)."""
        self.resetTransform()
        self._zoom_level = 1.0
        self._update_drag_mode()

    def _apply_zoom(self, factor: float) -> None:
        new_level = self._zoom_level * factor
        new_level = max(self._ZOOM_MIN, min(self._ZOOM_MAX, new_level))
        actual_factor = new_level / self._zoom_level
        self.scale(actual_factor, actual_factor)
        self._zoom_level = new_level
        self._update_drag_mode()

    def _update_drag_mode(self) -> None:
        """Enable ScrollHandDrag when zoomed in so the user can pan."""
        scene_rect = self._scene.sceneRect()
        if scene_rect.isEmpty():
            return
        vr = self.viewport().rect()
        sr = self.mapToScene(vr).boundingRect()
        zoomed_in = sr.width() < scene_rect.width() or sr.height() < scene_rect.height()
        mode = (QGraphicsView.DragMode.ScrollHandDrag if zoomed_in
                else QGraphicsView.DragMode.NoDrag)
        if self.dragMode() != mode:
            self.setDragMode(mode)

    def scene(self) -> QGraphicsScene:  # type: ignore[override]
        return self._scene

    def set_crosshair_visible(self, visible: bool) -> None:
        self._xhair_visible = visible
        for item in self._xhair_lines + self._xhair_outlines:
            item.setVisible(False)   # hidden until first mouse move

    def set_crosshair_color(self, color: QColor) -> None:
        pen = QPen(color, 1.5)
        pen.setCosmetic(False)
        for li in self._xhair_lines:
            li.setPen(pen)

    @property
    def image_width(self) -> int:
        return self._img_w

    @property
    def image_height(self) -> int:
        return self._img_h

    # ------------------------------------------------------------------
    # Internal event handling
    # ------------------------------------------------------------------

    def _scene_pos(self, event) -> QPointF:
        return self.mapToScene(event.pos())

    def _update_crosshair(self, sp: QPointF) -> None:
        if not self._xhair_visible:
            return
        cx, cy = sp.x(), sp.y()
        arm, gap = self._XHAIR_ARM, self._XHAIR_GAP
        segments = [
            (cx - arm, cy, cx - gap, cy),   # left
            (cx + gap, cy, cx + arm, cy),   # right
            (cx, cy - arm, cx, cy - gap),   # top
            (cx, cy + gap, cx, cy + arm),   # bottom
        ]
        for i, (x0, y0, x1, y1) in enumerate(segments):
            for item in (self._xhair_outlines[i], self._xhair_lines[i]):
                item.setLine(x0, y0, x1, y1)
                item.setVisible(True)

    def mouseMoveEvent(self, event) -> None:
        sp = self._scene_pos(event)
        self._update_crosshair(sp)
        if 0 <= sp.x() < self._img_w and 0 <= sp.y() < self._img_h:
            self.imageMoved.emit(sp)
        super().mouseMoveEvent(event)

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            sp = self._scene_pos(event)
            if 0 <= sp.x() < self._img_w and 0 <= sp.y() < self._img_h:
                self.imageClicked.emit(sp)
        super().mousePressEvent(event)

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        # Re-fit only when close to the "fit" zoom level (not manually zoomed).
        scene_rect = self._scene.sceneRect()
        if scene_rect.isEmpty():
            return
        vr = self.viewport().rect()
        if vr.width() > 0 and vr.height() > 0:
            fit_sx = vr.width()  / max(scene_rect.width(),  1)
            fit_sy = vr.height() / max(scene_rect.height(), 1)
            fit_scale = min(fit_sx, fit_sy)
            if abs(self._zoom_level - fit_scale) / max(fit_scale, 1e-6) < 0.15:
                self.fit_image()

    def showEvent(self, event) -> None:
        super().showEvent(event)
        self.fit_image()

    def wheelEvent(self, event) -> None:
        """Scroll wheel zooms; anchor is the cursor position."""
        delta = event.angleDelta().y()
        if delta > 0:
            self._apply_zoom(self._ZOOM_STEP)
        elif delta < 0:
            self._apply_zoom(1.0 / self._ZOOM_STEP)
        event.accept()


# ---------------------------------------------------------------------------
# Annotation helpers
# ---------------------------------------------------------------------------

_CORNER_COLOR    = QColor(0, 255, 0)
_REF_COLOR       = QColor(255, 100, 0)
_POLYLINE_COLOR  = QColor(0, 200, 255)
_LABEL_FONT      = QFont("monospace", 10, QFont.Weight.Bold)


def draw_crosshair(
    scene: QGraphicsScene,
    x: float,
    y: float,
    color: QColor = QColor(0, 255, 255),
    arm: float = 20,
    gap: float = 4,
    z: float = 10,
) -> list[QGraphicsLineItem]:
    """
    Add a static crosshair at (x, y) in scene/image coords.
    Returns the list of line items so the caller can remove them later.
    """
    pen = QPen(color, 1.5)
    pen.setCosmetic(False)
    outline = QPen(QColor(0, 0, 0), 3.5)
    outline.setCosmetic(False)

    segments = [
        (x - arm, y, x - gap, y),
        (x + gap, y, x + arm, y),
        (x, y - arm, x, y - gap),
        (x, y + gap, x, y + arm),
    ]
    items: list[QGraphicsLineItem] = []
    for x0, y0, x1, y1 in segments:
        for pen_, zv in ((outline, z - 1), (pen, z)):
            li = QGraphicsLineItem(x0, y0, x1, y1)
            li.setPen(pen_)
            li.setZValue(zv)
            scene.addItem(li)
            items.append(li)
    return items


def draw_corner(
    scene: QGraphicsScene,
    x: float,
    y: float,
    label: str,
    color: QColor = _CORNER_COLOR,
    radius: float = 7,
    z: float = 5,
) -> list[QGraphicsItem]:
    """Add a filled circle + label at (x, y). Returns the added items."""
    items: list[QGraphicsItem] = []

    dot = QGraphicsEllipseItem(x - radius, y - radius, radius * 2, radius * 2)
    dot.setBrush(QBrush(color))
    dot.setPen(QPen(Qt.GlobalColor.transparent))
    dot.setZValue(z)
    scene.addItem(dot)
    items.append(dot)

    txt = QGraphicsTextItem(label)
    txt.setFont(_LABEL_FONT)
    txt.setDefaultTextColor(color)
    txt.setPos(x + radius + 2, y - radius - 2)
    txt.setZValue(z)
    scene.addItem(txt)
    items.append(txt)

    return items


def draw_ref_point(
    scene: QGraphicsScene,
    x: float,
    y: float,
    label: str,
    color: QColor = _REF_COLOR,
    radius: float = 7,
    z: float = 5,
) -> list[QGraphicsItem]:
    """Add a ref-point circle + label. Returns added items."""
    return draw_corner(scene, x, y, label, color=color, radius=radius, z=z)


def draw_polyline(
    scene: QGraphicsScene,
    pts: Sequence[tuple[float, float]],
    color: QColor = _POLYLINE_COLOR,
    width: float = 1.5,
    z: float = 4,
    closed: bool = False,
) -> list[QGraphicsLineItem]:
    """Draw connected line segments through pts. Returns the line items."""
    if len(pts) < 2:
        return []
    pen = QPen(color, width)
    pen.setCosmetic(False)
    items: list[QGraphicsLineItem] = []
    seq = list(pts)
    if closed:
        seq = seq + [seq[0]]
    for (x0, y0), (x1, y1) in zip(seq, seq[1:]):
        li = QGraphicsLineItem(x0, y0, x1, y1)
        li.setPen(pen)
        li.setZValue(z)
        scene.addItem(li)
        items.append(li)
    return items
