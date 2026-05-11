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
    Qt, QPoint, QPointF, QRectF, pyqtSignal,
)
from PyQt6.QtGui import (
    QColor, QCursor, QFont, QImage, QPainter, QPen, QPixmap, QBrush,
)
from PyQt6.QtWidgets import (
    QGraphicsEllipseItem, QGraphicsItem, QGraphicsLineItem,
    QGraphicsPixmapItem, QGraphicsRectItem, QGraphicsScene, QGraphicsTextItem,
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

    imageClicked  = pyqtSignal(QPointF)   # image-pixel coords (press)
    imageReleased = pyqtSignal(QPointF)   # image-pixel coords (release)
    imageMoved    = pyqtSignal(QPointF)   # image-pixel coords (move)

    # Fires on every left press regardless of bounds — carries full diagnostic state:
    # (scene_pos, in_bounds, img_w, img_h, capture_mode, rb_anchor_set, zoom_level)
    debugClicked  = pyqtSignal(QPointF, bool, int, int, bool, bool, float)

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

        # Crosshair overlay (four line segments) — cosmetic pens so they're
        # always readable at any zoom level.
        pen = QPen(QColor(0, 255, 255), 1.5)
        pen.setCosmetic(True)
        outline_pen = QPen(QColor(0, 0, 0), 3.5)
        outline_pen.setCosmetic(True)

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

        # Capture mode: when True, left-button is used for entity placement
        # (NoDrag forced), crosshair always shown, middle-button pans.
        self._capture_mode: bool = False

        # Middle-mouse pan state
        self._mid_pan_active: bool = False
        self._mid_pan_last: QPoint = QPoint()

        # Rubber-band ghost rectangle for ADD_COMPONENT mode
        self._rb_anchor: QPointF | None = None
        self._rb_item: QGraphicsRectItem | None = None
        self._rb_shadow: QGraphicsRectItem | None = None

    # ------------------------------------------------------------------
    # Capture mode — used by ADD_VIA / ADD_COMPONENT / ADD_TEXT modes
    # ------------------------------------------------------------------

    def set_capture_mode(self, on: bool) -> None:
        """Enable or disable entity-placement capture mode.

        When *on*:
          - Left-button drag no longer pans (NoDrag forced)
          - Crosshair cursor is shown
          - Crosshair overlay is always visible
          - Middle-button still pans

        When *off*:
          - Returns to normal scroll/pan behaviour
          - Crosshair overlay hidden unless explicitly re-enabled
          - Restores default arrow cursor
        """
        self._capture_mode = on
        self.set_crosshair_visible(on)
        if on:
            self.setDragMode(QGraphicsView.DragMode.NoDrag)
            self.setCursor(QCursor(Qt.CursorShape.CrossCursor))
        else:
            self.cancel_rubber_band()
            self.unsetCursor()
            self._update_drag_mode()

    # ------------------------------------------------------------------
    # Rubber-band rect API (used by canvas ADD_COMPONENT mode)
    # ------------------------------------------------------------------

    def start_rubber_band(self, scene_pt: QPointF) -> None:
        """Begin a rubber-band rect anchored at *scene_pt* (scene coords)."""
        self._rb_anchor = scene_pt
        # Remove any previous rubber-band items
        if self._rb_item is not None:
            self._scene.removeItem(self._rb_item)
            self._rb_item = None
        if self._rb_shadow is not None:
            self._scene.removeItem(self._rb_shadow)
            self._rb_shadow = None
        # Two-layer rubber-band: hot-pink dashes on a black shadow for contrast
        shadow_pen = QPen(QColor(0, 0, 0), 3.5)
        shadow_pen.setCosmetic(True)
        shadow_pen.setStyle(Qt.PenStyle.DashLine)
        self._rb_shadow = self._scene.addRect(
            scene_pt.x(), scene_pt.y(), 0, 0, shadow_pen
        )
        self._rb_shadow.setZValue(19)
        pen = QPen(QColor(255, 20, 147), 1.5)   # hot pink / deep pink
        pen.setCosmetic(True)
        pen.setStyle(Qt.PenStyle.DashLine)
        self._rb_item = self._scene.addRect(
            scene_pt.x(), scene_pt.y(), 0, 0, pen
        )
        self._rb_item.setZValue(20)

    def update_rubber_band(self, scene_pt: QPointF) -> None:
        """Stretch the rubber-band to *scene_pt* while the mouse moves."""
        if self._rb_anchor is None or self._rb_item is None:
            return
        ax, ay = self._rb_anchor.x(), self._rb_anchor.y()
        bx, by = scene_pt.x(), scene_pt.y()
        rect = QRectF(min(ax, bx), min(ay, by), abs(bx - ax), abs(by - ay))
        self._rb_item.setRect(rect)
        if self._rb_shadow is not None:
            self._rb_shadow.setRect(rect)

    def finish_rubber_band(self) -> QRectF | None:
        """Complete the rubber-band; remove the ghost rect and return the scene rect."""
        if self._rb_item is None:
            return None
        rect = self._rb_item.rect()
        self._scene.removeItem(self._rb_item)
        self._rb_item = None
        if self._rb_shadow is not None:
            self._scene.removeItem(self._rb_shadow)
            self._rb_shadow = None
        self._rb_anchor = None
        return rect if rect.width() > 1 and rect.height() > 1 else None

    def cancel_rubber_band(self) -> None:
        """Discard any in-progress rubber-band without returning a rect."""
        if self._rb_item is not None:
            self._scene.removeItem(self._rb_item)
            self._rb_item = None
        if self._rb_shadow is not None:
            self._scene.removeItem(self._rb_shadow)
            self._rb_shadow = None
        self._rb_anchor = None

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
        """Enable ScrollHandDrag when zoomed in — but never in capture mode."""
        if self._capture_mode:
            self.setDragMode(QGraphicsView.DragMode.NoDrag)
            return
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
        if not visible:
            for item in self._xhair_lines + self._xhair_outlines:
                item.setVisible(False)

    def set_crosshair_color(self, color: QColor) -> None:
        pen = QPen(color, 1.5)
        pen.setCosmetic(True)
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
        if self._rb_anchor is not None:
            self.update_rubber_band(sp)
        # Middle-mouse pan
        if self._mid_pan_active:
            delta = event.pos() - self._mid_pan_last
            self._mid_pan_last = event.pos()
            self.horizontalScrollBar().setValue(
                self.horizontalScrollBar().value() - delta.x()
            )
            self.verticalScrollBar().setValue(
                self.verticalScrollBar().value() - delta.y()
            )
            event.accept()
            return
        eff_w, eff_h = self._effective_bounds()
        if 0 <= sp.x() < eff_w and 0 <= sp.y() < eff_h:
            self.imageMoved.emit(sp)
        super().mouseMoveEvent(event)

    def _effective_bounds(self) -> tuple[int, int]:
        """Return (img_w, img_h) for bounds checks.

        Falls back to the scene rect when set_image() was never called
        (e.g. layer loaded via LayerScene.load_photo()).
        """
        if self._img_w > 0 and self._img_h > 0:
            return self._img_w, self._img_h
        sr = self._scene.sceneRect()
        return int(sr.width()), int(sr.height())

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.MiddleButton:
            # Middle mouse always pans, regardless of capture mode
            self._mid_pan_active = True
            self._mid_pan_last = event.pos()
            self.setCursor(QCursor(Qt.CursorShape.ClosedHandCursor))
            event.accept()
            return
        if event.button() == Qt.MouseButton.LeftButton:
            sp = self._scene_pos(event)
            eff_w, eff_h = self._effective_bounds()
            in_bounds = 0 <= sp.x() < eff_w and 0 <= sp.y() < eff_h
            self.debugClicked.emit(
                sp, in_bounds,
                eff_w, eff_h,
                self._capture_mode,
                self._rb_anchor is not None,
                self._zoom_level,
            )
            if in_bounds:
                self.imageClicked.emit(sp)
            if self._capture_mode:
                # Don't pass to super — prevents ScrollHandDrag from activating
                event.accept()
                return
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.MiddleButton:
            self._mid_pan_active = False
            if self._capture_mode:
                self.setCursor(QCursor(Qt.CursorShape.CrossCursor))
            else:
                self.unsetCursor()
            event.accept()
            return
        if event.button() == Qt.MouseButton.LeftButton:
            sp = self._scene_pos(event)
            eff_w, eff_h = self._effective_bounds()
            if 0 <= sp.x() < eff_w and 0 <= sp.y() < eff_h:
                self.imageReleased.emit(sp)
            if self._capture_mode:
                event.accept()
                return
        super().mouseReleaseEvent(event)

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
