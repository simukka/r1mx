"""test_layer_alignment.py — cross-layer alignment: DB storage, affine fit,
and LayerScene board-transform / overlay rendering roles.
"""
from __future__ import annotations

import sys

import numpy as np
import pytest

from toolkit.db import DB


# ---------------------------------------------------------------------------
# DB: alignment column + round-trip
# ---------------------------------------------------------------------------

@pytest.fixture
def db(tmp_path):
    database = DB(db_path=tmp_path / "test.db")
    try:
        yield database
    finally:
        database.close()


def test_layers_has_alignment_column(db):
    cols = {row[1] for row in db.conn().execute("PRAGMA table_info(layers)")}
    assert "alignment" in cols


def test_alignment_round_trip(db):
    board = db.get_or_create_board("b")
    layer = db.add_layer(board["id"], "bottom", "/fake.jpg")
    assert db.get_layer_alignment(layer["id"]) is None

    alignment = {
        "ref_layer": "top",
        "matrix": [[-1.0, 0.0, 100.0], [0.0, 1.0, 5.0]],
        "pairs": {"ref": [[1, 2]], "tgt": [[3, 4]]},
    }
    db.save_layer_alignment(layer["id"], alignment)
    got = db.get_layer_alignment(layer["id"])
    assert got["ref_layer"] == "top"
    assert got["matrix"] == [[-1.0, 0.0, 100.0], [0.0, 1.0, 5.0]]


def test_alignment_clear_with_none(db):
    board = db.get_or_create_board("b")
    layer = db.add_layer(board["id"], "bottom", "/fake.jpg")
    db.save_layer_alignment(layer["id"], {"ref_layer": "top", "matrix": []})
    db.save_layer_alignment(layer["id"], None)
    assert db.get_layer_alignment(layer["id"]) is None


# ---------------------------------------------------------------------------
# Affine fit recovers a known transform, including the back-side X mirror
# ---------------------------------------------------------------------------

def test_estimate_affine_recovers_mirror():
    cv2 = pytest.importorskip("cv2")
    # Known transform: mirror X, scale 1.04, translate — like a back layer.
    M_true = np.array([[-1.04, 0.0, 500.0], [0.0, 1.04, 12.0]])
    tgt = np.array([[10, 20], [400, 30], [50, 600], [300, 450]], dtype=np.float64)
    ref = (M_true[:, :2] @ tgt.T).T + M_true[:, 2]

    M, _ = cv2.estimateAffine2D(tgt, ref)
    assert M is not None
    proj = (M[:, :2] @ tgt.T).T + M[:, 2]
    rms = float(np.sqrt(np.mean(np.sum((proj - ref) ** 2, axis=1))))
    assert rms < 1e-3
    # Mirror is reflected in a negative x-scale term.
    assert M[0, 0] < 0


# ---------------------------------------------------------------------------
# LayerScene: board transform + overlay roles
# ---------------------------------------------------------------------------

pytest.importorskip("PyQt6.QtWidgets", reason="PyQt6 not available")

from PyQt6.QtCore import QPointF  # noqa: E402
from PyQt6.QtWidgets import (  # noqa: E402
    QApplication,
    QGraphicsEllipseItem,
    QGraphicsScene,
)

from toolkit.gui.scene import LayerScene  # noqa: E402


@pytest.fixture(scope="module")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv[:1])
    return app


def _layer_with_item(qapp):
    scene = QGraphicsScene()
    ls = LayerScene(scene, "b", "bottom")
    item = QGraphicsEllipseItem(-5, -5, 10, 10)
    item.setData(0, 1)
    ls.group("via").addToGroup(item)
    return ls, item


def test_board_transform_maps_points(qapp):
    ls, item = _layer_with_item(qapp)
    # Mirror X (scale -2), scale-y 2, translate (100, 200)
    ls.set_board_transform([[-2, 0, 100], [0, 2, 200]])
    p0 = item.mapToScene(QPointF(0, 0))
    p1 = item.mapToScene(QPointF(1, 1))
    assert (round(p0.x()), round(p0.y())) == (100, 200)
    assert (round(p1.x()), round(p1.y())) == (98, 202)


def test_board_transform_none_is_identity(qapp):
    ls, item = _layer_with_item(qapp)
    ls.set_board_transform([[3, 0, 7], [0, 3, 9]])
    ls.set_board_transform(None)
    p = item.mapToScene(QPointF(2, 2))
    assert (round(p.x()), round(p.y())) == (2, 2)


def test_overlay_role_makes_items_inert(qapp):
    ls, item = _layer_with_item(qapp)
    flag = item.GraphicsItemFlag.ItemIsSelectable

    ls.set_overlay(0.4)
    assert ls._root.opacity() == pytest.approx(0.4)
    assert not bool(item.flags() & flag)

    ls.set_overlay(None)  # active
    assert ls._root.opacity() == pytest.approx(1.0)
    assert bool(item.flags() & flag)
    # Active sits below overlays so overlays ghost on top.
    assert ls._Z_ACTIVE < ls._Z_OVERLAY
