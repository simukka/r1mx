"""test_component_orientation_db.py — DB-level tests for the component
orientation and drawn-pixel workflows.

Recent features covered:
  drawn_px  — pixel-coordinate ground truth stored in object properties at
              placement time so calibration can be refined later without
              trusting OCR coordinates.

  pin1_edge — identifies which edge (top / bottom / left / right) is the
              pin-1 / notch side of a component.  Written by
              ``_place_orientation`` in app.py via a raw SQL UPDATE
              (preserving the rest of the properties dict) and rendered as
              an inward triangle in the scene.

Tests verify:
  1. drawn_px round-trip via DB.create_object + SELECT
  2. pin1_edge written via DB.update_object (properties dict path)
  3. pin1_edge written via raw SQL (as app.py does) — read back correctly
  4. pin1_edge does not overwrite other properties (manual, drawn_px)
  5. update_object replaces the full properties blob (caller must merge)
  6. Multiple pin1_edge updates are idempotent — last write wins
  7. pin1_edge set on an object whose properties column was NULL
  8. pin1_edge survives DB.refine_calibration_from_component
  9. drawn_px survives a pin1_edge update
 10. drawn_px is absent when object created without it
 11. manual flag stored and retrieved correctly
 12. refine_calibration_from_component: pin1_edge present on source object
     is preserved in the updated properties JSON
"""

from __future__ import annotations

import json
import pytest

from toolkit.db import DB


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def db(tmp_path):
    database = DB(db_path=tmp_path / "test.db")
    yield database
    database.close()


@pytest.fixture
def board_layer(db):
    """Returns (board_id, layer_id) for a fresh test board."""
    board_id = int(db.get_or_create_board("test_board"))
    layer_id  = int(db.add_layer(board_id, "top"))
    return board_id, layer_id


@pytest.fixture
def calibrated_layer(db, tmp_path):
    """Board + layer with a calibration JSON (px_per_mm=100)."""
    board_id  = int(db.get_or_create_board("cal_board"))
    layer_id  = int(db.add_layer(board_id, "top"))
    cal = json.dumps({"px_per_mm": 100.0, "warp_matrix": [], "warped_size": [1000, 1000]})
    db.conn().execute(
        "UPDATE layers SET calibrated=1, calibration=? WHERE id=?", (cal, layer_id)
    )
    db.conn().commit()
    return board_id, layer_id


def _get_props(db: DB, obj_id: int) -> dict:
    row = db.conn().execute(
        "SELECT properties FROM objects WHERE id=?", (obj_id,)
    ).fetchone()
    assert row is not None, f"Object {obj_id} not found"
    return json.loads(row["properties"] or "{}")


# ---------------------------------------------------------------------------
# 1. drawn_px round-trip via create_object
# ---------------------------------------------------------------------------

class TestDrawnPxStorage:

    def test_drawn_px_stored_in_create_object(self, db, board_layer):
        _, layer_id = board_layer
        obj_id = db.create_object(
            layer_id=layer_id,
            obj_type="component",
            x_mm=1.0, y_mm=2.0,
            width_mm=5.0, height_mm=3.0,
            properties={"drawn_px": [100, 200, 500, 300], "manual": True},
        )
        props = _get_props(db, obj_id)
        assert props["drawn_px"] == [100, 200, 500, 300]

    def test_manual_flag_stored_alongside_drawn_px(self, db, board_layer):
        _, layer_id = board_layer
        obj_id = db.create_object(
            layer_id=layer_id,
            obj_type="component",
            properties={"drawn_px": [0, 0, 50, 50], "manual": True},
        )
        props = _get_props(db, obj_id)
        assert props["manual"] is True

    def test_drawn_px_absent_when_not_provided(self, db, board_layer):
        _, layer_id = board_layer
        obj_id = db.create_object(
            layer_id=layer_id,
            obj_type="component",
            properties={"manual": True},
        )
        props = _get_props(db, obj_id)
        assert "drawn_px" not in props

    def test_drawn_px_absent_when_properties_is_none(self, db, board_layer):
        _, layer_id = board_layer
        obj_id = db.create_object(
            layer_id=layer_id,
            obj_type="component",
        )
        props = _get_props(db, obj_id)
        assert "drawn_px" not in props

    def test_drawn_px_values_are_list_not_tuple(self, db, board_layer):
        """JSON round-trip converts tuples to lists."""
        _, layer_id = board_layer
        obj_id = db.create_object(
            layer_id=layer_id,
            obj_type="component",
            properties={"drawn_px": (10, 20, 30, 40)},
        )
        props = _get_props(db, obj_id)
        assert isinstance(props["drawn_px"], list)

    def test_drawn_px_four_elements(self, db, board_layer):
        _, layer_id = board_layer
        obj_id = db.create_object(
            layer_id=layer_id,
            obj_type="component",
            properties={"drawn_px": [11.5, 22.5, 333.0, 200.0]},
        )
        props = _get_props(db, obj_id)
        assert len(props["drawn_px"]) == 4


# ---------------------------------------------------------------------------
# 2. pin1_edge via DB.update_object (properties dict)
# ---------------------------------------------------------------------------

class TestPin1EdgeViaUpdateObject:

    def test_pin1_edge_stored_via_update_object(self, db, board_layer):
        _, layer_id = board_layer
        obj_id = db.create_object(layer_id=layer_id, obj_type="component")
        db.update_object(obj_id, properties={"pin1_edge": "top"})
        assert _get_props(db, obj_id)["pin1_edge"] == "top"

    def test_all_four_edges_accepted(self, db, board_layer):
        _, layer_id = board_layer
        for edge in ("top", "bottom", "left", "right"):
            obj_id = db.create_object(layer_id=layer_id, obj_type="component")
            db.update_object(obj_id, properties={"pin1_edge": edge})
            assert _get_props(db, obj_id)["pin1_edge"] == edge

    def test_update_object_replaces_entire_properties(self, db, board_layer):
        """update_object(properties=…) replaces the whole blob — caller must merge."""
        _, layer_id = board_layer
        obj_id = db.create_object(
            layer_id=layer_id,
            obj_type="component",
            properties={"drawn_px": [0, 0, 100, 50], "manual": True},
        )
        # Caller passes full merged dict
        db.update_object(
            obj_id,
            properties={"drawn_px": [0, 0, 100, 50], "manual": True, "pin1_edge": "left"},
        )
        props = _get_props(db, obj_id)
        assert props["pin1_edge"] == "left"
        assert props["drawn_px"] == [0, 0, 100, 50]
        assert props["manual"] is True

    def test_multiple_updates_last_write_wins(self, db, board_layer):
        _, layer_id = board_layer
        obj_id = db.create_object(layer_id=layer_id, obj_type="component")
        for edge in ("top", "right", "bottom"):
            db.update_object(obj_id, properties={"pin1_edge": edge})
        assert _get_props(db, obj_id)["pin1_edge"] == "bottom"


# ---------------------------------------------------------------------------
# 3. pin1_edge via raw SQL (mirrors _place_orientation in app.py)
# ---------------------------------------------------------------------------

class TestPin1EdgeViaRawSQL:
    """_place_orientation uses raw SQL to merge pin1_edge into existing props.
    These tests verify the merge semantics that app.py relies on.
    """

    def _write_pin1_edge(self, db: DB, obj_id: int, edge: str) -> None:
        """Reproduce the exact code path from app.py._place_orientation."""
        row = db.conn().execute(
            "SELECT properties FROM objects WHERE id=?", (obj_id,)
        ).fetchone()
        props = json.loads(row["properties"] or "{}")
        props["pin1_edge"] = edge
        db.conn().execute(
            "UPDATE objects SET properties=? WHERE id=?",
            (json.dumps(props), obj_id),
        )
        db.conn().commit()

    def test_pin1_edge_written_when_props_null(self, db, board_layer):
        _, layer_id = board_layer
        obj_id = db.create_object(layer_id=layer_id, obj_type="component")
        # properties is NULL at this point
        self._write_pin1_edge(db, obj_id, "right")
        assert _get_props(db, obj_id)["pin1_edge"] == "right"

    def test_pin1_edge_does_not_overwrite_drawn_px(self, db, board_layer):
        _, layer_id = board_layer
        obj_id = db.create_object(
            layer_id=layer_id,
            obj_type="component",
            properties={"drawn_px": [5, 5, 100, 80], "manual": True},
        )
        self._write_pin1_edge(db, obj_id, "top")
        props = _get_props(db, obj_id)
        assert props["pin1_edge"] == "top"
        assert props["drawn_px"] == [5, 5, 100, 80]
        assert props["manual"] is True

    def test_pin1_edge_overwrite_changes_value(self, db, board_layer):
        _, layer_id = board_layer
        obj_id = db.create_object(
            layer_id=layer_id,
            obj_type="component",
            properties={"pin1_edge": "top"},
        )
        self._write_pin1_edge(db, obj_id, "bottom")
        assert _get_props(db, obj_id)["pin1_edge"] == "bottom"

    def test_drawn_px_survives_pin1_edge_update(self, db, board_layer):
        _, layer_id = board_layer
        obj_id = db.create_object(
            layer_id=layer_id,
            obj_type="component",
            properties={"drawn_px": [10, 20, 200, 100], "manual": True},
        )
        self._write_pin1_edge(db, obj_id, "left")
        props = _get_props(db, obj_id)
        # drawn_px must survive
        assert props["drawn_px"] == [10, 20, 200, 100]
        # pin1_edge written correctly
        assert props["pin1_edge"] == "left"


# ---------------------------------------------------------------------------
# 4. pin1_edge survives refine_calibration_from_component
# ---------------------------------------------------------------------------

class TestPin1EdgeSurvivesCalibration:
    """When refine_calibration_from_component recomputes mm coords it must
    not wipe the pin1_edge that was previously set."""

    def _make_calibrated_component(
        self, db: DB, layer_id: int, *, with_pin1: str | None = None
    ) -> int:
        """Create a component object with drawn_px and optional pin1_edge."""
        props: dict = {"drawn_px": [100, 200, 400, 200], "manual": True}
        if with_pin1:
            props["pin1_edge"] = with_pin1
        return db.create_object(
            layer_id=layer_id,
            obj_type="component",
            x_mm=1.0, y_mm=2.0,
            width_mm=4.0, height_mm=2.0,
            properties=props,
        )

    def test_pin1_edge_preserved_after_refinement(self, db, calibrated_layer):
        board_id, layer_id = calibrated_layer
        obj_id = self._make_calibrated_component(db, layer_id, with_pin1="left")
        db.refine_calibration_from_component(obj_id, known_width_mm=4.0)
        props = _get_props(db, obj_id)
        assert props["pin1_edge"] == "left"

    def test_drawn_px_preserved_after_refinement(self, db, calibrated_layer):
        board_id, layer_id = calibrated_layer
        obj_id = self._make_calibrated_component(db, layer_id)
        db.refine_calibration_from_component(obj_id, known_width_mm=4.0)
        props = _get_props(db, obj_id)
        assert props["drawn_px"] == [100, 200, 400, 200]

    def test_pin1_edge_preserved_without_pin1(self, db, calibrated_layer):
        """Objects without pin1_edge still work; property simply absent after."""
        _, layer_id = calibrated_layer
        obj_id = self._make_calibrated_component(db, layer_id, with_pin1=None)
        db.refine_calibration_from_component(obj_id, known_width_mm=4.0)
        props = _get_props(db, obj_id)
        assert "pin1_edge" not in props

    def test_mm_coords_updated_while_pin1_preserved(self, db, calibrated_layer):
        """mm coordinates are recomputed AND pin1_edge kept in same update."""
        _, layer_id = calibrated_layer
        # drawn_px width = 400, known_width_mm = 2.0 → new px_per_mm = 200
        obj_id = self._make_calibrated_component(db, layer_id, with_pin1="right")
        db.refine_calibration_from_component(obj_id, known_width_mm=2.0)
        props = _get_props(db, obj_id)
        assert props["pin1_edge"] == "right"
        # Confirm calibration was actually updated (px_per_mm changed)
        row = db.conn().execute(
            "SELECT l.calibration FROM objects o JOIN layers l ON o.layer_id=l.id WHERE o.id=?",
            (obj_id,)
        ).fetchone()
        cal = json.loads(row["calibration"])
        assert abs(cal["px_per_mm"] - 200.0) < 0.1
