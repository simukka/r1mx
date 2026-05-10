"""
Tests for image display via LayerScene.load_photo() + ImageViewer.fit_image().

Regression coverage for:
1. fit_image() silently doing nothing when images were added via
   LayerScene.load_photo() (inserts into a scene group, not set_image()).
2. _REPO path computed with wrong parents[] depth in scene.py — pointed to
   toolkit/ instead of the repo root, so load_photo() couldn't find images.
3. _load_layer_into_scene() returning early for uncalibrated layers even when
   an image was selected — now shows the raw image without calibration.
"""

from __future__ import annotations

import sys
import pytest

# Require a QApplication for every test in this module.
pytest.importorskip("PyQt6.QtWidgets", reason="PyQt6 not available")

from PyQt6.QtCore import QRectF
from PyQt6.QtGui import QColor, QPixmap
from PyQt6.QtWidgets import QApplication, QGraphicsPixmapItem

from toolkit.gui.viewer import ImageViewer


@pytest.fixture(scope="module")
def qapp():
    """Return (or create) a QApplication for the test session."""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv[:1])
    return app


def test_fit_image_noop_when_pixmap_item_none(qapp):
    """
    Reproduces the root cause: fit_image() returned early when _pixmap_item is None,
    even though the scene contained visible content added via a group item.

    Verifies that fitInView IS called (i.e. no early-return guard), regardless of
    whether a real display is available.
    """
    from unittest.mock import patch

    viewer = ImageViewer()

    # Simulate what LayerScene.load_photo() does: add content to the scene
    # directly (via a group), NOT via ImageViewer.set_image().
    pixmap = QPixmap(2000, 1000)
    pixmap.fill(QColor(80, 80, 80))
    item = QGraphicsPixmapItem(pixmap)
    scene = viewer.scene()
    scene.addItem(item)
    scene.setSceneRect(QRectF(0, 0, 2000, 1000))

    assert viewer._pixmap_item is None, (
        "_pixmap_item should be None when set_image() was never called"
    )

    with patch.object(viewer, "fitInView") as mock_fit:
        viewer.fit_image()

    mock_fit.assert_called_once(), (
        "fit_image() did not call fitInView — likely blocked by "
        "'if _pixmap_item is not None' guard that has been removed"
    )


def test_fit_image_works_via_set_image(qapp):
    """Baseline: fit_image() calls fitInView when set_image() is used."""
    import numpy as np
    from unittest.mock import patch

    viewer = ImageViewer()
    img = np.full((1000, 2000, 3), 80, dtype="uint8")
    viewer.set_image(img)

    assert viewer._pixmap_item is not None

    with patch.object(viewer, "fitInView") as mock_fit:
        viewer.fit_image()

    mock_fit.assert_called_once(), (
        "fit_image() did not call fitInView even when set_image() was used."
    )


def test_scene_repo_root_is_correct():
    """
    Regression: _REPO in toolkit/gui/scene.py must point to the repo root,
    not to toolkit/.  Wrong depth (parents[1] instead of parents[2]) caused
    load_photo() to look for images in toolkit/components/ which doesn't exist.
    """
    from pathlib import Path
    import toolkit.gui.scene as scene_mod

    # test file is at toolkit/tests/test_image_display.py
    # parents[0]=tests/, parents[1]=toolkit/, parents[2]=repo root
    repo_root = Path(__file__).resolve().parents[2]

    assert (repo_root / "components").exists(), (
        f"Sanity: repo root should contain components/, got {repo_root}"
    )
    assert scene_mod._REPO == repo_root, (
        f"scene._REPO={scene_mod._REPO!r} != repo root {repo_root!r}. "
        "Wrong parents[] depth — images will never be found."
    )


def test_load_photo_without_calibration(qapp, tmp_path):
    """
    Regression: LayerScene.load_photo() must display a raw image even when
    warp_matrix/warped_size are None (uncalibrated layer).
    """
    import cv2
    import numpy as np
    from pathlib import Path
    import toolkit.gui.scene as scene_mod

    # Write a small test image into a temp board dir
    board_dir = tmp_path / "components" / "test_board"
    board_dir.mkdir(parents=True)
    img = np.full((100, 200, 3), 128, dtype="uint8")
    cv2.imwrite(str(board_dir / "test.jpg"), img)

    # Patch _REPO to point at tmp_path so load_photo can find the image
    original_repo = scene_mod._REPO
    scene_mod._REPO = tmp_path
    try:
        from PyQt6.QtWidgets import QGraphicsScene
        from toolkit.gui.scene import LayerScene

        qt_scene = QGraphicsScene()
        layer = LayerScene(qt_scene, "test_board", "top")

        # Load without calibration (warp_matrix=None, warped_size=None)
        layer.load_photo("test_board", "top", "test.jpg", None, None)

        photo_group = layer.group("photo")
        assert photo_group is not None
        assert len(photo_group.childItems()) > 0, (
            "load_photo() added no items for an uncalibrated layer. "
            "Raw image should be shown even without calibration."
        )
    finally:
        scene_mod._REPO = original_repo
