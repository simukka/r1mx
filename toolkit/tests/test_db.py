"""Unit tests for toolkit.db."""
from __future__ import annotations

import pytest

from toolkit.analysis.scan import BomEntry
from toolkit.db import DB


@pytest.fixture
def db(tmp_path):
    database = DB(db_path=tmp_path / "test.db")
    try:
        yield database
    finally:
        database.close()


def test_get_or_create_board(db):
    board = db.get_or_create_board("test_board")
    assert board["name"] == "test_board"
    board2 = db.get_or_create_board("test_board")
    assert board2["id"] == board["id"]


def test_add_layer(db):
    board = db.get_or_create_board("board1")
    layer = db.add_layer(board["id"], "top", "/fake/path.jpg")
    assert layer["name"] == "top"
    assert layer["board_id"] == board["id"]


def test_delete_objects_cleans_components(db):
    board = db.get_or_create_board("board1")
    layer = db.add_layer(board["id"], "top", "/fake/path.jpg")
    oid = db.conn().execute(
        "INSERT INTO objects (layer_id, type, label, x_mm, y_mm, width_mm, height_mm, confidence, properties) VALUES (?,?,?,?,?,?,?,?,?)",
        (layer["id"], "component", "R1", 1.0, 2.0, 3.0, 4.0, 0.9, "{}"),
    ).lastrowid
    db.conn().execute(
        "INSERT INTO components (object_id, board_id, ref_designator) VALUES (?,?,?)",
        (oid, board["id"], "R1"),
    )
    db.conn().commit()
    db.delete_objects(layer["id"], obj_type=None)
    rows = db.conn().execute("SELECT * FROM components WHERE object_id=?", (oid,)).fetchall()
    assert len(rows) == 0


def test_set_get_state(db):
    db.set_state("test_key", "test_value")
    assert db.get_state("test_key") == "test_value"


def test_save_scan_results(db):
    board = db.get_or_create_board("board1")
    layer = db.add_layer(board["id"], "top", "/fake/path.jpg")
    db.save_calibration(board["id"], layer["id"], {"px_per_mm": 10.0, "corners_px": []})
    entries = [
        BomEntry(label="R1", ref_type="R", x_mm=1.0, y_mm=2.0, confidence=0.9, source="easyocr"),
        BomEntry(label="ABC123", ref_type="", x_mm=3.0, y_mm=4.0, confidence=0.75, source="easyocr"),
    ]
    count = db.save_scan_results(layer["id"], entries)
    assert count == 2
