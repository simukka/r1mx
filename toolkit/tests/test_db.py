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


# ---------------------------------------------------------------------------
# objects_at_mm hit-test tests
# ---------------------------------------------------------------------------

def _insert_object(db, layer_id, obj_type, x, y, w, h, label=""):
    return db.conn().execute(
        "INSERT INTO objects (layer_id, type, label, x_mm, y_mm, width_mm, height_mm, confidence, properties)"
        " VALUES (?,?,?,?,?,?,?,?,?)",
        (layer_id, obj_type, label, x, y, w, h, 1.0, "{}"),
    ).lastrowid


@pytest.fixture
def layer_with_objects(db):
    board = db.get_or_create_board("hit_board")
    layer = db.add_layer(board["id"], "top", "/fake/top.jpg")
    db.conn().commit()
    return layer


def test_objects_at_mm_via_hit(db, layer_with_objects):
    layer = layer_with_objects
    _insert_object(db, layer["id"], "via", 10.0, 10.0, 2.0, 2.0, "V1")
    db.conn().commit()
    results = db.objects_at_mm(layer["id"], 10.0, 10.0)
    assert len(results) == 1
    assert results[0]["type"] == "via"


def test_objects_at_mm_via_edge_hit(db, layer_with_objects):
    layer = layer_with_objects
    _insert_object(db, layer["id"], "via", 10.0, 10.0, 2.0, 2.0)
    db.conn().commit()
    # exactly on the circumference (radius = 1.0 mm)
    results = db.objects_at_mm(layer["id"], 11.0, 10.0)
    assert len(results) == 1


def test_objects_at_mm_via_miss(db, layer_with_objects):
    layer = layer_with_objects
    _insert_object(db, layer["id"], "via", 10.0, 10.0, 2.0, 2.0)
    db.conn().commit()
    # just outside radius
    results = db.objects_at_mm(layer["id"], 11.1, 10.0)
    assert len(results) == 0


def test_objects_at_mm_component_hit(db, layer_with_objects):
    layer = layer_with_objects
    # top-left at (5, 5), size 10x6
    _insert_object(db, layer["id"], "component", 5.0, 5.0, 10.0, 6.0, "U1")
    db.conn().commit()
    results = db.objects_at_mm(layer["id"], 10.0, 8.0)
    assert len(results) == 1
    assert results[0]["label"] == "U1"


def test_objects_at_mm_component_miss(db, layer_with_objects):
    layer = layer_with_objects
    _insert_object(db, layer["id"], "component", 5.0, 5.0, 10.0, 6.0, "U1")
    db.conn().commit()
    results = db.objects_at_mm(layer["id"], 4.9, 8.0)
    assert len(results) == 0


def test_objects_at_mm_pad_hit(db, layer_with_objects):
    layer = layer_with_objects
    _insert_object(db, layer["id"], "pad", 0.0, 0.0, 3.0, 2.0)
    db.conn().commit()
    results = db.objects_at_mm(layer["id"], 1.5, 1.0)
    assert len(results) == 1
    assert results[0]["type"] == "pad"


def test_objects_at_mm_pin_hit_within_tolerance(db, layer_with_objects):
    layer = layer_with_objects
    _insert_object(db, layer["id"], "pin", 20.0, 20.0, 0.5, 0.5, "1")
    db.conn().commit()
    results = db.objects_at_mm(layer["id"], 20.4, 20.4, tolerance_mm=0.5)
    assert len(results) == 1
    assert results[0]["type"] == "pin"


def test_objects_at_mm_pin_miss_beyond_tolerance(db, layer_with_objects):
    layer = layer_with_objects
    _insert_object(db, layer["id"], "pin", 20.0, 20.0, 0.5, 0.5)
    db.conn().commit()
    results = db.objects_at_mm(layer["id"], 20.6, 20.0, tolerance_mm=0.5)
    assert len(results) == 0


def test_objects_at_mm_no_trace(db, layer_with_objects):
    layer = layer_with_objects
    db.conn().execute(
        "INSERT INTO objects (layer_id, type, label, x_mm, y_mm, width_mm, height_mm, confidence, properties)"
        " VALUES (?,?,?,?,?,?,?,?,?)",
        (layer["id"], "trace", "", 0.0, 0.0, 100.0, 100.0, 1.0, "{}"),
    )
    db.conn().commit()
    results = db.objects_at_mm(layer["id"], 1.0, 1.0)
    assert all(r["type"] != "trace" for r in results)


def test_objects_at_mm_empty_layer(db, layer_with_objects):
    layer = layer_with_objects
    results = db.objects_at_mm(layer["id"], 0.0, 0.0)
    assert results == []


def test_objects_at_mm_multiple_overlapping(db, layer_with_objects):
    layer = layer_with_objects
    _insert_object(db, layer["id"], "via",       5.0, 5.0, 2.0, 2.0, "V1")
    _insert_object(db, layer["id"], "component", 4.0, 4.0, 4.0, 4.0, "U1")
    db.conn().commit()
    results = db.objects_at_mm(layer["id"], 5.0, 5.0)
    types = {r["type"] for r in results}
    assert "via" in types
    assert "component" in types

