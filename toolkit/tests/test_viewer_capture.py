"""test_viewer_capture.py — Qt unit tests for ImageViewer capture mode and
effective-bounds fallback.

Recent fixes covered:

  set_capture_mode(True/False)
    When True the viewer switches to NoDrag and shows the crosshair.
    When False the crosshair is hidden, the rubber-band is cancelled, and
    normal drag-mode logic is restored.

  _effective_bounds()
    The key fix for the "img_w=0 → all clicks fail" bug (see canvas click
    debug log: "in_bounds: False (img_w=0 img_h=0)").

    When a layer is loaded via LayerScene.load_photo() the viewer's
    set_image() is never called so _img_w / _img_h stay 0.
    _effective_bounds() must fall back to scene().sceneRect() dimensions in
    that case so click-position checks work correctly.
"""

from __future__ import annotations

import sys
import pytest

pytest.importorskip("PyQt6.QtWidgets", reason="PyQt6 not available")

from PyQt6.QtCore import QPointF, QRectF
from PyQt6.QtGui import QColor, QPixmap
from PyQt6.QtWidgets import QApplication, QGraphicsPixmapItem, QGraphicsView

from toolkit.gui.viewer import ImageViewer


# ---------------------------------------------------------------------------
# QApplication singleton
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv[:1])
    return app


# ---------------------------------------------------------------------------
# set_capture_mode
# ---------------------------------------------------------------------------

class TestSetCaptureMode:

    def test_capture_mode_false_by_default(self, qapp):
        v = ImageViewer()
        assert v._capture_mode is False

    def test_capture_mode_true_after_enable(self, qapp):
        v = ImageViewer()
        v.set_capture_mode(True)
        assert v._capture_mode is True

    def test_capture_mode_false_after_disable(self, qapp):
        v = ImageViewer()
        v.set_capture_mode(True)
        v.set_capture_mode(False)
        assert v._capture_mode is False

    def test_capture_mode_on_forces_no_drag(self, qapp):
        v = ImageViewer()
        v.set_capture_mode(True)
        assert v.dragMode() == QGraphicsView.DragMode.NoDrag

    def test_capture_mode_off_leaves_no_drag_when_not_zoomed(self, qapp):
        """With an empty scene (not zoomed in), NoDrag is the correct normal mode."""
        v = ImageViewer()
        v.set_capture_mode(True)
        v.set_capture_mode(False)
        assert v.dragMode() == QGraphicsView.DragMode.NoDrag

    def test_crosshair_visible_after_enable(self, qapp):
        v = ImageViewer()
        v.set_capture_mode(True)
        assert v._xhair_visible is True

    def test_crosshair_hidden_after_disable(self, qapp):
        v = ImageViewer()
        v.set_capture_mode(True)
        v.set_capture_mode(False)
        assert v._xhair_visible is False

    def test_rubber_band_cleared_on_disable(self, qapp):
        v = ImageViewer()
        v.set_capture_mode(True)
        # Simulate a rubber-band being started
        v.start_rubber_band(QPointF(10, 10))
        assert v._rb_anchor is not None
        v.set_capture_mode(False)
        # Anchor must be cleared
        assert v._rb_anchor is None

    def test_enable_twice_is_idempotent(self, qapp):
        v = ImageViewer()
        v.set_capture_mode(True)
        v.set_capture_mode(True)
        assert v._capture_mode is True
        assert v.dragMode() == QGraphicsView.DragMode.NoDrag

    def test_disable_twice_is_idempotent(self, qapp):
        v = ImageViewer()
        v.set_capture_mode(False)
        v.set_capture_mode(False)
        assert v._capture_mode is False

    def test_update_drag_mode_respects_capture(self, qapp):
        """_update_drag_mode() must not override NoDrag while capture is on."""
        v = ImageViewer()
        v.set_capture_mode(True)
        # Calling _update_drag_mode() directly must keep NoDrag
        v._update_drag_mode()
        assert v.dragMode() == QGraphicsView.DragMode.NoDrag


# ---------------------------------------------------------------------------
# _effective_bounds
# ---------------------------------------------------------------------------

class TestEffectiveBounds:

    def test_returns_img_size_after_set_image(self, qapp):
        """When set_image() is called _effective_bounds must use _img_w/_img_h."""
        import numpy as np
        v = ImageViewer()
        arr = np.zeros((600, 800, 3), dtype=np.uint8)
        v.set_image(arr)
        w, h = v._effective_bounds()
        assert w == 800
        assert h == 600

    def test_fallback_to_scene_rect_when_no_image(self, qapp):
        """LayerScene.load_photo() path: set_image() never called → _img_w/_img_h == 0.
        _effective_bounds must fall back to sceneRect().
        """
        v = ImageViewer()
        # Simulate what LayerScene.load_photo() does
        px = QPixmap(1920, 1080)
        px.fill(QColor(0, 0, 0))
        item = QGraphicsPixmapItem(px)
        v.scene().addItem(item)
        v.scene().setSceneRect(QRectF(0, 0, 1920, 1080))

        assert v._img_w == 0 and v._img_h == 0, "set_image() was never called"
        w, h = v._effective_bounds()
        assert w == 1920
        assert h == 1080

    def test_fallback_when_img_w_is_zero(self, qapp):
        v = ImageViewer()
        v._img_w = 0
        v._img_h = 0
        v.scene().setSceneRect(QRectF(0, 0, 500, 300))
        w, h = v._effective_bounds()
        assert w == 500
        assert h == 300

    def test_does_not_fallback_when_img_dims_nonzero(self, qapp):
        """Even if sceneRect is larger, should use _img_w/_img_h."""
        v = ImageViewer()
        v._img_w = 200
        v._img_h = 100
        v.scene().setSceneRect(QRectF(0, 0, 9999, 9999))
        w, h = v._effective_bounds()
        assert w == 200
        assert h == 100

    def test_fallback_empty_scene_returns_zero(self, qapp):
        v = ImageViewer()
        # No image, no scene content — sceneRect is empty
        assert v._img_w == 0 and v._img_h == 0
        w, h = v._effective_bounds()
        # Empty scene rect → (0, 0) — no crash
        assert w == 0
        assert h == 0

    def test_img_w_positive_but_img_h_zero_uses_scene(self, qapp):
        """Both must be positive; if either is 0, fall back to scene rect."""
        v = ImageViewer()
        v._img_w = 100
        v._img_h = 0   # degenerate — fall back
        v.scene().setSceneRect(QRectF(0, 0, 400, 300))
        w, h = v._effective_bounds()
        assert w == 400
        assert h == 300


# ---------------------------------------------------------------------------
# img_width / img_height properties
# ---------------------------------------------------------------------------

class TestImgProperties:

    def test_img_width_zero_before_set_image(self, qapp):
        v = ImageViewer()
        assert v.image_width == 0

    def test_img_height_zero_before_set_image(self, qapp):
        v = ImageViewer()
        assert v.image_height == 0

    def test_img_width_after_set_image(self, qapp):
        import numpy as np
        v = ImageViewer()
        v.set_image(np.zeros((480, 640, 3), dtype=np.uint8))
        assert v.image_width == 640

    def test_img_height_after_set_image(self, qapp):
        import numpy as np
        v = ImageViewer()
        v.set_image(np.zeros((480, 640, 3), dtype=np.uint8))
        assert v.image_height == 480
