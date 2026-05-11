"""
test_entity_mgmt.py — Unit tests for DB entity CRUD methods.

Covers:
  DB.create_object      — inserts object, returns valid id
  DB.delete_object      — deletes object and cascades to components
  DB.update_object      — updates arbitrary allowed fields; ignores disallowed
  DB.get_objects_by_type — filters by layer_id + type
  DB.merge_to_component  — creates component object + components row, deletes sources
                           handles mixed positions (centroid), NULL positions, single item
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
    """Returns (board_id, layer_id) for a fresh in-memory board."""
    board = db.get_or_create_board("test_board")
    layer = db.add_layer(int(board), "top")
    return int(board), int(layer)


# ---------------------------------------------------------------------------
# DB.create_object
# ---------------------------------------------------------------------------

class TestCreateObject:

    def test_returns_positive_integer(self, db, board_layer):
        _, layer_id = board_layer
        obj_id = db.create_object(layer_id, "via", x_mm=10.0, y_mm=5.0)
        assert isinstance(obj_id, int)
        assert obj_id > 0

    def test_row_exists_with_correct_type(self, db, board_layer):
        _, layer_id = board_layer
        obj_id = db.create_object(layer_id, "pad", x_mm=1.0, y_mm=2.0,
                                   width_mm=0.5, height_mm=0.3)
        row = db.conn().execute("SELECT * FROM objects WHERE id=?", (obj_id,)).fetchone()
        assert row is not None
        assert row["type"] == "pad"
        assert row["layer_id"] == layer_id

    def test_position_stored(self, db, board_layer):
        _, layer_id = board_layer
        obj_id = db.create_object(layer_id, "trace", x_mm=3.5, y_mm=7.25)
        row = db.conn().execute("SELECT x_mm, y_mm FROM objects WHERE id=?", (obj_id,)).fetchone()
        assert abs(row["x_mm"] - 3.5) < 1e-6
        assert abs(row["y_mm"] - 7.25) < 1e-6

    def test_label_stored(self, db, board_layer):
        _, layer_id = board_layer
        obj_id = db.create_object(layer_id, "text_label", label="SiI3512")
        row = db.conn().execute("SELECT label FROM objects WHERE id=?", (obj_id,)).fetchone()
        assert row["label"] == "SiI3512"

    def test_properties_dict_serialised(self, db, board_layer):
        _, layer_id = board_layer
        props = {"drill_mm": 0.4, "manual": True}
        obj_id = db.create_object(layer_id, "via", properties=props)
        row = db.conn().execute("SELECT properties FROM objects WHERE id=?", (obj_id,)).fetchone()
        stored = json.loads(row["properties"])
        assert stored["drill_mm"] == pytest.approx(0.4)
        assert stored["manual"] is True

    def test_null_position_allowed(self, db, board_layer):
        _, layer_id = board_layer
        obj_id = db.create_object(layer_id, "outline")
        row = db.conn().execute("SELECT x_mm, y_mm FROM objects WHERE id=?", (obj_id,)).fetchone()
        assert row["x_mm"] is None
        assert row["y_mm"] is None

    def test_verified_default_zero(self, db, board_layer):
        _, layer_id = board_layer
        obj_id = db.create_object(layer_id, "via")
        row = db.conn().execute("SELECT verified FROM objects WHERE id=?", (obj_id,)).fetchone()
        assert row["verified"] == 0

    def test_verified_can_be_set(self, db, board_layer):
        _, layer_id = board_layer
        obj_id = db.create_object(layer_id, "via", verified=1)
        row = db.conn().execute("SELECT verified FROM objects WHERE id=?", (obj_id,)).fetchone()
        assert row["verified"] == 1

    def test_multiple_objects_unique_ids(self, db, board_layer):
        _, layer_id = board_layer
        ids = [db.create_object(layer_id, "via", x_mm=float(i)) for i in range(5)]
        assert len(set(ids)) == 5


# ---------------------------------------------------------------------------
# DB.get_object
# ---------------------------------------------------------------------------

class TestGetObject:

    def test_returns_row_for_existing_object(self, db, board_layer):
        _, layer_id = board_layer
        obj_id = db.create_object(layer_id, "via")
        row = db.get_object(obj_id)
        assert row is not None

    def test_returns_none_for_missing_id(self, db, board_layer):
        row = db.get_object(99999)
        assert row is None

    def test_id_matches(self, db, board_layer):
        _, layer_id = board_layer
        obj_id = db.create_object(layer_id, "component")
        row = db.get_object(obj_id)
        assert row["id"] == obj_id

    def test_type_field_correct(self, db, board_layer):
        _, layer_id = board_layer
        obj_id = db.create_object(layer_id, "pad")
        assert db.get_object(obj_id)["type"] == "pad"

    def test_label_field_returned(self, db, board_layer):
        _, layer_id = board_layer
        obj_id = db.create_object(layer_id, "text_label", label="R10")
        assert db.get_object(obj_id)["label"] == "R10"

    def test_position_fields_returned(self, db, board_layer):
        _, layer_id = board_layer
        obj_id = db.create_object(layer_id, "via", x_mm=1.5, y_mm=2.5,
                                  width_mm=0.3, height_mm=0.3)
        row = db.get_object(obj_id)
        assert row["x_mm"] == pytest.approx(1.5)
        assert row["y_mm"] == pytest.approx(2.5)

    def test_properties_json_returned(self, db, board_layer):
        _, layer_id = board_layer
        obj_id = db.create_object(layer_id, "component",
                                  properties={"drawn_px": [0, 0, 100, 50]})
        import json
        props = json.loads(db.get_object(obj_id)["properties"])
        assert props["drawn_px"] == [0, 0, 100, 50]

    def test_returns_none_after_delete(self, db, board_layer):
        _, layer_id = board_layer
        obj_id = db.create_object(layer_id, "via")
        db.delete_object(obj_id)
        assert db.get_object(obj_id) is None

    def test_two_objects_independent(self, db, board_layer):
        _, layer_id = board_layer
        id_a = db.create_object(layer_id, "via",   label="A")
        id_b = db.create_object(layer_id, "trace", label="B")
        assert db.get_object(id_a)["label"] == "A"
        assert db.get_object(id_b)["label"] == "B"


# ---------------------------------------------------------------------------
# DB.delete_object
# ---------------------------------------------------------------------------

class TestDeleteObject:

    def test_object_gone_after_delete(self, db, board_layer):
        _, layer_id = board_layer
        obj_id = db.create_object(layer_id, "via")
        db.delete_object(obj_id)
        row = db.conn().execute("SELECT id FROM objects WHERE id=?", (obj_id,)).fetchone()
        assert row is None

    def test_cascades_to_components(self, db, board_layer):
        board_id, layer_id = board_layer
        obj_id = db.create_object(layer_id, "component", label="U1")
        # Manually insert a components row linked to this object
        db.conn().execute(
            "INSERT INTO components(object_id, board_id, ref_designator) VALUES (?,?,?)",
            (obj_id, board_id, "U1")
        )
        db.conn().commit()
        # Verify component exists
        comp = db.conn().execute(
            "SELECT id FROM components WHERE object_id=?", (obj_id,)
        ).fetchone()
        assert comp is not None
        # Delete object → component should cascade
        db.delete_object(obj_id)
        comp_after = db.conn().execute(
            "SELECT id FROM components WHERE object_id=?", (obj_id,)
        ).fetchone()
        assert comp_after is None

    def test_delete_nonexistent_is_noop(self, db, board_layer):
        """Deleting an object that doesn't exist should not raise."""
        db.delete_object(99999)  # no exception


# ---------------------------------------------------------------------------
# DB.update_object
# ---------------------------------------------------------------------------

class TestUpdateObject:

    def test_update_label(self, db, board_layer):
        _, layer_id = board_layer
        obj_id = db.create_object(layer_id, "text_label", label="old")
        db.update_object(obj_id, label="new")
        row = db.conn().execute("SELECT label FROM objects WHERE id=?", (obj_id,)).fetchone()
        assert row["label"] == "new"

    def test_update_position(self, db, board_layer):
        _, layer_id = board_layer
        obj_id = db.create_object(layer_id, "via", x_mm=0.0, y_mm=0.0)
        db.update_object(obj_id, x_mm=12.5, y_mm=7.0)
        row = db.conn().execute("SELECT x_mm, y_mm FROM objects WHERE id=?", (obj_id,)).fetchone()
        assert abs(row["x_mm"] - 12.5) < 1e-6
        assert abs(row["y_mm"] - 7.0) < 1e-6

    def test_update_dimensions(self, db, board_layer):
        _, layer_id = board_layer
        obj_id = db.create_object(layer_id, "component", width_mm=1.0, height_mm=1.0)
        db.update_object(obj_id, width_mm=5.0, height_mm=3.0)
        row = db.conn().execute(
            "SELECT width_mm, height_mm FROM objects WHERE id=?", (obj_id,)
        ).fetchone()
        assert abs(row["width_mm"] - 5.0) < 1e-6
        assert abs(row["height_mm"] - 3.0) < 1e-6

    def test_update_verified(self, db, board_layer):
        _, layer_id = board_layer
        obj_id = db.create_object(layer_id, "via")
        assert db.conn().execute(
            "SELECT verified FROM objects WHERE id=?", (obj_id,)
        ).fetchone()["verified"] == 0
        db.update_object(obj_id, verified=1)
        assert db.conn().execute(
            "SELECT verified FROM objects WHERE id=?", (obj_id,)
        ).fetchone()["verified"] == 1

    def test_update_properties_dict(self, db, board_layer):
        _, layer_id = board_layer
        obj_id = db.create_object(layer_id, "via")
        db.update_object(obj_id, properties={"drill_mm": 0.6})
        raw = db.conn().execute(
            "SELECT properties FROM objects WHERE id=?", (obj_id,)
        ).fetchone()["properties"]
        assert json.loads(raw)["drill_mm"] == pytest.approx(0.6)

    def test_disallowed_fields_ignored(self, db, board_layer):
        _, layer_id = board_layer
        obj_id = db.create_object(layer_id, "via")
        # "type" is not in _allowed — should not error, and type should be unchanged
        db.update_object(obj_id, type="pad", label="ok")
        row = db.conn().execute("SELECT type, label FROM objects WHERE id=?", (obj_id,)).fetchone()
        assert row["type"] == "via"    # unchanged
        assert row["label"] == "ok"   # label was allowed

    def test_empty_fields_noop(self, db, board_layer):
        _, layer_id = board_layer
        obj_id = db.create_object(layer_id, "via", label="original")
        db.update_object(obj_id)  # no fields — should not raise or change anything
        row = db.conn().execute("SELECT label FROM objects WHERE id=?", (obj_id,)).fetchone()
        assert row["label"] == "original"


# ---------------------------------------------------------------------------
# DB.get_objects_by_type
# ---------------------------------------------------------------------------

class TestGetObjectsByType:

    def test_returns_only_matching_type(self, db, board_layer):
        _, layer_id = board_layer
        db.create_object(layer_id, "via")
        db.create_object(layer_id, "via")
        db.create_object(layer_id, "pad")
        rows = db.get_objects_by_type(layer_id, "via")
        assert len(rows) == 2
        assert all(r["type"] == "via" for r in rows)

    def test_empty_when_no_match(self, db, board_layer):
        _, layer_id = board_layer
        db.create_object(layer_id, "pad")
        rows = db.get_objects_by_type(layer_id, "trace")
        assert rows == []

    def test_different_layers_isolated(self, db, board_layer):
        board_id, layer_id = board_layer
        other_layer = int(db.add_layer(board_id, "bottom"))
        db.create_object(layer_id, "via")
        db.create_object(other_layer, "via")
        rows = db.get_objects_by_type(layer_id, "via")
        assert len(rows) == 1

    def test_ordered_by_label_then_id(self, db, board_layer):
        _, layer_id = board_layer
        db.create_object(layer_id, "text_label", label="Z")
        db.create_object(layer_id, "text_label", label="A")
        db.create_object(layer_id, "text_label", label="M")
        labels = [r["label"] for r in db.get_objects_by_type(layer_id, "text_label")]
        assert labels == ["A", "M", "Z"]


# ---------------------------------------------------------------------------
# DB.merge_to_component
# ---------------------------------------------------------------------------

class TestMergeToComponent:

    def test_returns_new_component_object_id(self, db, board_layer):
        board_id, layer_id = board_layer
        a = db.create_object(layer_id, "text_label", x_mm=1.0, y_mm=1.0, label="SiI3512")
        b = db.create_object(layer_id, "text_label", x_mm=3.0, y_mm=1.0, label="SiI3512")
        new_id = db.merge_to_component([a, b], "U1", "SiI3512", layer_id, board_id)
        assert isinstance(new_id, int)
        assert new_id > 0

    def test_creates_component_type_object(self, db, board_layer):
        board_id, layer_id = board_layer
        a = db.create_object(layer_id, "text_label", x_mm=0.0, y_mm=0.0, label="P1")
        new_id = db.merge_to_component([a], "U2", "P1", layer_id, board_id)
        row = db.conn().execute("SELECT type FROM objects WHERE id=?", (new_id,)).fetchone()
        assert row["type"] == "component"

    def test_creates_components_row(self, db, board_layer):
        board_id, layer_id = board_layer
        a = db.create_object(layer_id, "text_label", label="ATMEGA328")
        new_id = db.merge_to_component([a], "U3", "ATMEGA328", layer_id, board_id)
        comp = db.conn().execute(
            "SELECT * FROM components WHERE object_id=?", (new_id,)
        ).fetchone()
        assert comp is not None
        assert comp["ref_designator"] == "U3"
        assert comp["part_number"] == "ATMEGA328"

    def test_source_objects_deleted(self, db, board_layer):
        board_id, layer_id = board_layer
        a = db.create_object(layer_id, "text_label", x_mm=0.0, y_mm=0.0)
        b = db.create_object(layer_id, "text_label", x_mm=2.0, y_mm=0.0)
        db.merge_to_component([a, b], "U4", "PART", layer_id, board_id)
        for oid in (a, b):
            row = db.conn().execute("SELECT id FROM objects WHERE id=?", (oid,)).fetchone()
            assert row is None, f"Source object {oid} should have been deleted"

    def test_centroid_computed(self, db, board_layer):
        board_id, layer_id = board_layer
        a = db.create_object(layer_id, "text_label", x_mm=0.0, y_mm=0.0)
        b = db.create_object(layer_id, "text_label", x_mm=4.0, y_mm=2.0)
        new_id = db.merge_to_component([a, b], "U5", "PART", layer_id, board_id)
        row = db.conn().execute("SELECT x_mm, y_mm FROM objects WHERE id=?", (new_id,)).fetchone()
        assert abs(row["x_mm"] - 2.0) < 1e-6
        assert abs(row["y_mm"] - 1.0) < 1e-6

    def test_null_positions_excluded_from_centroid(self, db, board_layer):
        board_id, layer_id = board_layer
        a = db.create_object(layer_id, "text_label", x_mm=None, y_mm=None)
        b = db.create_object(layer_id, "text_label", x_mm=6.0, y_mm=4.0)
        new_id = db.merge_to_component([a, b], "U6", "PART", layer_id, board_id)
        row = db.conn().execute("SELECT x_mm, y_mm FROM objects WHERE id=?", (new_id,)).fetchone()
        assert abs(row["x_mm"] - 6.0) < 1e-6
        assert abs(row["y_mm"] - 4.0) < 1e-6

    def test_all_null_positions_gives_null_centroid(self, db, board_layer):
        board_id, layer_id = board_layer
        a = db.create_object(layer_id, "text_label", x_mm=None, y_mm=None)
        new_id = db.merge_to_component([a], "U7", "PART", layer_id, board_id)
        row = db.conn().execute("SELECT x_mm, y_mm FROM objects WHERE id=?", (new_id,)).fetchone()
        assert row["x_mm"] is None
        assert row["y_mm"] is None

    def test_optional_fields_stored(self, db, board_layer):
        board_id, layer_id = board_layer
        a = db.create_object(layer_id, "text_label")
        db.merge_to_component(
            [a], "U8", "LM317",
            layer_id, board_id,
            manufacturer="TI",
            value="3.3V",
            package="TO-92",
            notes="power reg",
        )
        new_id = db.conn().execute(
            "SELECT id FROM objects WHERE layer_id=? AND type='component' AND label='U8'",
            (layer_id,)
        ).fetchone()["id"]
        comp = db.conn().execute(
            "SELECT * FROM components WHERE object_id=?", (new_id,)
        ).fetchone()
        assert comp["manufacturer"] == "TI"
        assert comp["value"] == "3.3V"
        assert comp["package"] == "TO-92"
        assert comp["notes"] == "power reg"

    def test_single_source_object(self, db, board_layer):
        board_id, layer_id = board_layer
        a = db.create_object(layer_id, "text_label", x_mm=5.0, y_mm=5.0, label="SPI_FLASH")
        new_id = db.merge_to_component([a], "U9", "SPI_FLASH", layer_id, board_id)
        row = db.conn().execute("SELECT x_mm, y_mm FROM objects WHERE id=?", (new_id,)).fetchone()
        assert abs(row["x_mm"] - 5.0) < 1e-6

    def test_component_is_verified(self, db, board_layer):
        board_id, layer_id = board_layer
        a = db.create_object(layer_id, "text_label")
        new_id = db.merge_to_component([a], "U10", "PART", layer_id, board_id)
        row = db.conn().execute("SELECT verified FROM objects WHERE id=?", (new_id,)).fetchone()
        assert row["verified"] == 1


# ---------------------------------------------------------------------------
# DB.refine_calibration_from_component
# ---------------------------------------------------------------------------

def _calibrated_layer(db, board_id, layer_name="top", px_per_mm=20.0):
    """Helper: create a layer with a minimal calibration JSON."""
    layer_id = int(db.add_layer(board_id, layer_name))
    cal = {"px_per_mm": px_per_mm, "warp_matrix": None, "warped_size": None}
    db.conn().execute(
        "UPDATE layers SET calibrated=1, calibration=? WHERE id=?",
        (__import__("json").dumps(cal), layer_id),
    )
    db.conn().commit()
    return layer_id


class TestRefineCalibrationFromComponent:

    def test_width_only_refinement(self, db, board_layer):
        board_id, _ = board_layer
        layer_id = _calibrated_layer(db, board_id, "top2", px_per_mm=20.0)
        # Object drawn at 200×100 px; known width = 10 mm → expected px_per_mm = 20
        obj_id = db.create_object(
            layer_id, "component",
            x_mm=0.0, y_mm=0.0, width_mm=10.0, height_mm=5.0,
            properties={"drawn_px": [0.0, 0.0, 200.0, 100.0], "manual": True},
        )
        new_ppm = db.refine_calibration_from_component(obj_id, known_width_mm=10.0)
        assert abs(new_ppm - 20.0) < 1e-6

    def test_width_and_height_averaged(self, db, board_layer):
        board_id, _ = board_layer
        layer_id = _calibrated_layer(db, board_id, "top3", px_per_mm=10.0)
        # drawn 300×200 px; known 15×8 mm → ppm_w=20, ppm_h=25, avg=22.5
        obj_id = db.create_object(
            layer_id, "component",
            x_mm=0.0, y_mm=0.0, width_mm=30.0, height_mm=20.0,
            properties={"drawn_px": [0.0, 0.0, 300.0, 200.0], "manual": True},
        )
        new_ppm = db.refine_calibration_from_component(obj_id, 15.0, 8.0)
        assert abs(new_ppm - 22.5) < 1e-6

    def test_updates_layer_calibration(self, db, board_layer):
        import json
        board_id, _ = board_layer
        layer_id = _calibrated_layer(db, board_id, "top4", px_per_mm=10.0)
        obj_id = db.create_object(
            layer_id, "component",
            x_mm=5.0, y_mm=3.0, width_mm=20.0, height_mm=10.0,
            properties={"drawn_px": [100.0, 60.0, 200.0, 100.0], "manual": True},
        )
        db.refine_calibration_from_component(obj_id, known_width_mm=10.0)  # → 20 px/mm
        row = db.conn().execute("SELECT calibration FROM layers WHERE id=?", (layer_id,)).fetchone()
        cal = json.loads(row["calibration"])
        assert abs(cal["px_per_mm"] - 20.0) < 1e-6

    def test_rescales_all_drawn_objects(self, db, board_layer):
        board_id, _ = board_layer
        layer_id = _calibrated_layer(db, board_id, "top5", px_per_mm=10.0)
        # Reference object: 200px wide, known 10mm → new ppm=20
        ref_id = db.create_object(
            layer_id, "component",
            x_mm=0.0, y_mm=0.0, width_mm=20.0, height_mm=10.0,
            properties={"drawn_px": [0.0, 0.0, 200.0, 100.0], "manual": True},
        )
        # Second manually drawn object at 400×50 px
        other_id = db.create_object(
            layer_id, "component",
            x_mm=0.0, y_mm=0.0, width_mm=40.0, height_mm=5.0,
            properties={"drawn_px": [0.0, 0.0, 400.0, 50.0], "manual": True},
        )
        db.refine_calibration_from_component(ref_id, known_width_mm=10.0)  # → ppm=20
        row = db.conn().execute(
            "SELECT width_mm, height_mm FROM objects WHERE id=?", (other_id,)
        ).fetchone()
        assert abs(row["width_mm"] - 20.0) < 1e-6   # 400/20=20
        assert abs(row["height_mm"] - 2.5) < 1e-6   # 50/20=2.5

    def test_non_drawn_objects_unchanged(self, db, board_layer):
        board_id, _ = board_layer
        layer_id = _calibrated_layer(db, board_id, "top6", px_per_mm=10.0)
        ref_id = db.create_object(
            layer_id, "component",
            x_mm=0.0, y_mm=0.0, width_mm=20.0, height_mm=10.0,
            properties={"drawn_px": [0.0, 0.0, 200.0, 100.0], "manual": True},
        )
        # OCR-extracted object — no drawn_px
        ocr_id = db.create_object(
            layer_id, "text_label",
            x_mm=5.0, y_mm=3.0, width_mm=2.0, height_mm=1.0,
        )
        db.refine_calibration_from_component(ref_id, known_width_mm=10.0)
        row = db.conn().execute(
            "SELECT x_mm, y_mm, width_mm, height_mm FROM objects WHERE id=?", (ocr_id,)
        ).fetchone()
        assert abs(row["x_mm"] - 5.0) < 1e-6
        assert abs(row["width_mm"] - 2.0) < 1e-6

    def test_raises_if_no_drawn_px(self, db, board_layer):
        board_id, _ = board_layer
        layer_id = _calibrated_layer(db, board_id, "top7", px_per_mm=20.0)
        obj_id = db.create_object(layer_id, "component", x_mm=1.0, y_mm=1.0)
        with pytest.raises(ValueError, match="drawn_px"):
            db.refine_calibration_from_component(obj_id, known_width_mm=10.0)

    def test_raises_if_object_not_found(self, db, board_layer):
        with pytest.raises(ValueError, match="not found"):
            db.refine_calibration_from_component(99999, known_width_mm=10.0)
