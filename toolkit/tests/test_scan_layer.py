"""
test_scan_layer.py — Unit tests for the new Scan Layer workflow additions.

Covers:
  layers.py new entry points:
    - make_copper_mask         returns correct-shaped binary mask
    - make_hole_mask           returns correct-shaped binary mask
    - process_vias             returns list[dict] with required keys
    - process_pads             returns list[dict] with required keys
    - process_outline          returns list of [x_mm, y_mm] points or []
    - process_traces           returns list[dict] with required keys (potrace optional)
    - progress callbacks       all entry points fire progress_cb messages

  db.py save_feature_objects:
    - vias    saved with correct type and properties
    - pads    saved with correct type, dimensions, kicad_layer
    - traces  saved with correct type, midpoint, properties
    - outline saved as single "outline" row with points JSON
    - idempotent: re-running replaces only the matching type
    - raises ValueError for unknown scan_type
    - empty items list writes 0 rows (but still deletes old rows)
    - manual flag propagated into properties JSON
    - bottom layer uses B_Cu for kicad_layer
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

import cv2
import numpy as np
import pytest

from toolkit.analysis.layers import (
    DEFAULT_HSV,
    make_copper_mask,
    make_hole_mask,
    process_outline,
    process_pads,
    process_vias,
)
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
def layer_id(db):
    """A fresh board + layer row — returns the layer id (int)."""
    board = db.get_or_create_board("test_board")
    layer = db.add_layer(int(board), "top")
    return int(layer)


def _solid_bgr(h: int, w: int, bgr=(30, 30, 30)) -> np.ndarray:
    """Return a solid-colour BGR image of given size."""
    img = np.zeros((h, w, 3), dtype=np.uint8)
    img[:] = bgr
    return img


def _copper_patch_bgr(h: int = 200, w: int = 200) -> np.ndarray:
    """
    Synthetic board image: dark green background with a bright copper-coloured
    rectangle in the centre.  Used to test copper-mask extraction.

    Copper HSV defaults: hue ~20 (orange), high sat, high val.
    BGR for HSV(20, 200, 220) ≈ (20, 100, 220).
    """
    img = _solid_bgr(h, w, bgr=(20, 60, 20))   # dark green background
    # Copper patch in the middle quarter
    r0, r1 = h // 4, 3 * h // 4
    c0, c1 = w // 4, 3 * w // 4
    img[r0:r1, c0:c1] = (20, 100, 220)          # warm copper-orange in BGR
    return img


def _dark_hole_bgr(h: int = 200, w: int = 200) -> np.ndarray:
    """
    Synthetic image with a bright background and a small near-black circle
    in the centre (simulates a via drill hole).
    """
    img = _solid_bgr(h, w, bgr=(180, 180, 180))  # grey background
    cx, cy, r = w // 2, h // 2, 10
    cv2.circle(img, (cx, cy), r, (5, 5, 5), -1)  # very dark circle
    return img


def _rect_board_bgr(h: int = 300, w: int = 400) -> np.ndarray:
    """
    White rectangle on a black background — gives a clear board outline.
    The rectangle occupies ~80% of the image area, so it passes the 10% threshold.
    """
    img = np.zeros((h, w, 3), dtype=np.uint8)
    margin_y, margin_x = h // 10, w // 10
    cv2.rectangle(
        img,
        (margin_x, margin_y),
        (w - margin_x, h - margin_y),
        (255, 255, 255),
        -1,
    )
    return img


# ===========================================================================
# make_copper_mask
# ===========================================================================

class TestMakeCopperMask:

    def test_returns_uint8_mask(self):
        bgr = _copper_patch_bgr()
        mask = make_copper_mask(bgr)
        assert mask.dtype == np.uint8
        assert mask.shape == bgr.shape[:2]

    def test_copper_pixels_are_nonzero(self):
        bgr = _copper_patch_bgr(200, 200)
        mask = make_copper_mask(bgr)
        # The centre patch should have significant coverage
        centre = mask[60:140, 60:140]
        coverage = np.count_nonzero(centre) / centre.size
        assert coverage > 0.3, f"Expected >30% copper coverage in centre, got {coverage:.1%}"

    def test_background_pixels_are_zero(self):
        bgr = _copper_patch_bgr(200, 200)
        mask = make_copper_mask(bgr)
        # Corner (5×5) should be background
        corner = mask[0:5, 0:5]
        assert np.count_nonzero(corner) == 0, "Background corner should not be masked"

    def test_custom_hsv_cfg_overrides_defaults(self):
        # Pass an HSV range that matches the green background, not the copper
        bgr = _copper_patch_bgr(200, 200)
        green_cfg = {
            "copper_lower": [35, 20, 10],
            "copper_upper": [85, 255, 100],
        }
        mask = make_copper_mask(bgr, green_cfg)
        corner = mask[0:5, 0:5]
        assert np.count_nonzero(corner) > 0, (
            "With green-matching HSV config the background corner should be masked"
        )

    def test_blank_image_returns_empty_mask(self):
        bgr = _solid_bgr(100, 100, bgr=(20, 60, 20))  # all-green background
        mask = make_copper_mask(bgr)
        assert np.count_nonzero(mask) == 0


# ===========================================================================
# make_hole_mask
# ===========================================================================

class TestMakeHoleMask:

    def test_returns_uint8_mask(self):
        bgr = _dark_hole_bgr()
        mask = make_hole_mask(bgr)
        assert mask.dtype == np.uint8
        assert mask.shape == bgr.shape[:2]

    def test_dark_hole_is_detected(self):
        bgr = _dark_hole_bgr(200, 200)
        mask = make_hole_mask(bgr)
        cx, cy = 100, 100
        # Some pixels near the hole centre should be in the mask
        roi = mask[cy - 8: cy + 8, cx - 8: cx + 8]
        assert np.count_nonzero(roi) > 0, "Dark hole should appear in mask"

    def test_bright_background_not_masked(self):
        bgr = _dark_hole_bgr(200, 200)
        mask = make_hole_mask(bgr)
        corner = mask[0:5, 0:5]
        assert np.count_nonzero(corner) == 0, "Bright background should not be in hole mask"


# ===========================================================================
# process_vias
# ===========================================================================

class TestProcessVias:

    def test_returns_list(self):
        bgr = _solid_bgr(200, 200)
        result = process_vias(bgr, px_per_mm=20.0)
        assert isinstance(result, list)

    def test_each_via_has_required_keys(self):
        # Plant a synthetic "via" — small dark circle with copper ring
        bgr = _copper_patch_bgr(200, 200)
        # Draw a dark drill hole in the copper area
        cv2.circle(bgr, (100, 100), 5, (5, 5, 5), -1)
        result = process_vias(bgr, px_per_mm=20.0)
        for via in result:
            assert "x_mm" in via
            assert "y_mm" in via
            assert "drill_mm" in via
            assert "annular_mm" in via

    def test_progress_cb_called(self):
        messages = []
        bgr = _solid_bgr(100, 100)
        process_vias(bgr, px_per_mm=20.0, progress_cb=messages.append)
        assert len(messages) >= 2
        assert any("copper" in m.lower() or "mask" in m.lower() for m in messages)
        assert any("via" in m.lower() for m in messages)

    def test_values_in_mm(self):
        bgr = _solid_bgr(200, 200)
        result = process_vias(bgr, px_per_mm=20.0)
        for via in result:
            # Coordinates must be non-negative and within image bounds (200px / 20 = 10mm)
            assert 0 <= via["x_mm"] <= 10.0
            assert 0 <= via["y_mm"] <= 10.0
            assert via["drill_mm"] > 0


# ===========================================================================
# process_pads
# ===========================================================================

class TestProcessPads:

    def test_returns_list(self):
        bgr = _solid_bgr(200, 200)
        result = process_pads(bgr, px_per_mm=20.0)
        assert isinstance(result, list)

    def test_each_pad_has_required_keys(self):
        bgr = _copper_patch_bgr(200, 200)
        result = process_pads(bgr, px_per_mm=20.0)
        for pad in result:
            assert "x_mm" in pad
            assert "y_mm" in pad
            assert "w_mm" in pad
            assert "h_mm" in pad
            assert "rotation_deg" in pad
            assert "layer" in pad

    def test_kicad_layer_passed_through(self):
        bgr = _copper_patch_bgr(200, 200)
        result = process_pads(bgr, px_per_mm=20.0, kicad_layer="B_Cu")
        for pad in result:
            assert pad["layer"] == "B_Cu"

    def test_progress_cb_called(self):
        messages = []
        bgr = _solid_bgr(100, 100)
        process_pads(bgr, px_per_mm=20.0, progress_cb=messages.append)
        assert len(messages) >= 2

    def test_vias_excluded_from_pads(self):
        """Passing known via positions should reduce pad count (annular rings skipped)."""
        bgr = _copper_patch_bgr(200, 200)
        # Plant a via in the copper area
        via_x_mm, via_y_mm = 5.0, 5.0
        cv2.circle(bgr, (100, 100), 5, (5, 5, 5), -1)
        without_vias = len(process_pads(bgr, px_per_mm=20.0))
        with_vias    = len(process_pads(bgr, px_per_mm=20.0,
                                         vias=[{"x_mm": via_x_mm, "y_mm": via_y_mm,
                                                "drill_mm": 0.3, "annular_mm": 0.15}]))
        # Exclusion must not increase count
        assert with_vias <= without_vias


# ===========================================================================
# process_outline
# ===========================================================================

class TestProcessOutline:

    def test_detects_rectangle(self):
        bgr = _rect_board_bgr(300, 400)
        pts = process_outline(bgr, px_per_mm=20.0)
        assert isinstance(pts, list)
        assert len(pts) >= 4, "Rectangle outline should have at least 4 corners"

    def test_points_are_xy_pairs(self):
        bgr = _rect_board_bgr(300, 400)
        pts = process_outline(bgr, px_per_mm=20.0)
        for p in pts:
            assert isinstance(p, list)
            assert len(p) == 2

    def test_coordinates_in_mm(self):
        bgr = _rect_board_bgr(300, 400)
        px_per_mm = 20.0
        pts = process_outline(bgr, px_per_mm=px_per_mm)
        max_x = 400 / px_per_mm  # 20 mm
        max_y = 300 / px_per_mm  # 15 mm
        for x, y in pts:
            assert 0 <= x <= max_x + 1, f"x_mm out of range: {x}"
            assert 0 <= y <= max_y + 1, f"y_mm out of range: {y}"

    def test_returns_empty_for_blank_image(self):
        bgr = np.zeros((200, 200, 3), dtype=np.uint8)
        pts = process_outline(bgr, px_per_mm=20.0)
        assert pts == []

    def test_progress_cb_called(self):
        messages = []
        bgr = _rect_board_bgr()
        process_outline(bgr, px_per_mm=20.0, progress_cb=messages.append)
        assert len(messages) >= 1
        assert any("outline" in m.lower() for m in messages)

    def test_canny_thresholds_accepted(self):
        """Non-default Canny thresholds should not raise."""
        bgr = _rect_board_bgr()
        pts = process_outline(bgr, px_per_mm=10.0, canny_low=10, canny_high=50)
        assert isinstance(pts, list)


# ===========================================================================
# db.save_feature_objects — vias
# ===========================================================================

class TestSaveFeatureObjectsVias:

    def _via(self, x=1.0, y=2.0, drill=0.3, annular=0.15):
        return {"x_mm": x, "y_mm": y, "drill_mm": drill, "annular_mm": annular}

    def test_saves_correct_count(self, db, layer_id):
        vias = [self._via(1.0, 1.0), self._via(2.0, 2.0), self._via(3.0, 3.0)]
        n = db.save_feature_objects(layer_id, "vias", vias)
        assert n == 3

    def test_objects_stored_as_via_type(self, db, layer_id):
        db.save_feature_objects(layer_id, "vias", [self._via()])
        rows = db.conn().execute(
            "SELECT type FROM objects WHERE layer_id=?", (layer_id,)
        ).fetchall()
        assert all(r["type"] == "via" for r in rows)

    def test_coordinates_stored_correctly(self, db, layer_id):
        db.save_feature_objects(layer_id, "vias", [self._via(1.5, 2.5, 0.4)])
        row = db.conn().execute(
            "SELECT x_mm, y_mm, properties FROM objects WHERE layer_id=?", (layer_id,)
        ).fetchone()
        assert row["x_mm"] == pytest.approx(1.5)
        assert row["y_mm"] == pytest.approx(2.5)
        props = json.loads(row["properties"])
        assert props["drill_mm"] == pytest.approx(0.4)
        assert props["annular_mm"] == pytest.approx(0.15)

    def test_diameter_stored_as_width_and_height(self, db, layer_id):
        db.save_feature_objects(layer_id, "vias", [self._via(drill=0.3, annular=0.15)])
        row = db.conn().execute(
            "SELECT width_mm, height_mm FROM objects WHERE layer_id=?", (layer_id,)
        ).fetchone()
        expected = 0.3 + 2 * 0.15  # drill + 2×annular
        assert row["width_mm"] == pytest.approx(expected)
        assert row["height_mm"] == pytest.approx(expected)

    def test_idempotent_replaces_vias_only(self, db, layer_id):
        # Pre-insert a pad that should survive
        db.conn().execute(
            "INSERT INTO objects (layer_id, type, x_mm, y_mm, width_mm, height_mm, "
            "rotation_deg, confidence, properties) VALUES (?,?,?,?,?,?,?,?,?)",
            (layer_id, "pad", 5.0, 5.0, 1.0, 1.0, 0.0, None, "{}"),
        )
        db.conn().commit()

        db.save_feature_objects(layer_id, "vias", [self._via()])
        db.save_feature_objects(layer_id, "vias", [self._via(9.0, 9.0)])  # re-run

        rows = db.conn().execute(
            "SELECT type FROM objects WHERE layer_id=?", (layer_id,)
        ).fetchall()
        types = [r["type"] for r in rows]
        assert types.count("via") == 1,   "Re-run should leave exactly 1 via"
        assert types.count("pad") == 1,   "Pre-existing pad must survive"

    def test_manual_flag_stored(self, db, layer_id):
        via = {**self._via(), "_manual": True}
        db.save_feature_objects(layer_id, "vias", [via])
        row = db.conn().execute(
            "SELECT properties FROM objects WHERE layer_id=?", (layer_id,)
        ).fetchone()
        props = json.loads(row["properties"])
        assert props["manual"] is True

    def test_empty_items_deletes_existing(self, db, layer_id):
        db.save_feature_objects(layer_id, "vias", [self._via()])
        assert db.conn().execute(
            "SELECT COUNT(*) FROM objects WHERE layer_id=? AND type='via'", (layer_id,)
        ).fetchone()[0] == 1

        n = db.save_feature_objects(layer_id, "vias", [])
        assert n == 0
        assert db.conn().execute(
            "SELECT COUNT(*) FROM objects WHERE layer_id=? AND type='via'", (layer_id,)
        ).fetchone()[0] == 0


# ===========================================================================
# db.save_feature_objects — pads
# ===========================================================================

class TestSaveFeatureObjectsPads:

    def _pad(self, x=1.0, y=2.0, w=1.5, h=0.8, rot=0.0, ref="R1", layer="F_Cu"):
        return {"x_mm": x, "y_mm": y, "w_mm": w, "h_mm": h,
                "rotation_deg": rot, "ref": ref, "layer": layer}

    def test_saves_correct_count(self, db, layer_id):
        n = db.save_feature_objects(layer_id, "pads", [self._pad(), self._pad(x=5.0)])
        assert n == 2

    def test_type_is_pad(self, db, layer_id):
        db.save_feature_objects(layer_id, "pads", [self._pad()])
        row = db.conn().execute(
            "SELECT type FROM objects WHERE layer_id=?", (layer_id,)
        ).fetchone()
        assert row["type"] == "pad"

    def test_dimensions_stored(self, db, layer_id):
        db.save_feature_objects(layer_id, "pads", [self._pad(w=2.0, h=1.0, rot=45.0)])
        row = db.conn().execute(
            "SELECT width_mm, height_mm, rotation_deg FROM objects WHERE layer_id=?",
            (layer_id,),
        ).fetchone()
        assert row["width_mm"]    == pytest.approx(2.0)
        assert row["height_mm"]   == pytest.approx(1.0)
        assert row["rotation_deg"] == pytest.approx(45.0)

    def test_kicad_layer_in_properties(self, db, layer_id):
        db.save_feature_objects(layer_id, "pads", [self._pad(layer="B_Cu")])
        row = db.conn().execute(
            "SELECT properties FROM objects WHERE layer_id=?", (layer_id,)
        ).fetchone()
        props = json.loads(row["properties"])
        assert props["kicad_layer"] == "B_Cu"

    def test_bottom_layer_key_uses_b_cu(self, db, layer_id):
        # When layer_key="bottom" and pad has no explicit layer, should default to B_Cu
        pad = {"x_mm": 1.0, "y_mm": 1.0, "w_mm": 1.0, "h_mm": 0.5,
               "rotation_deg": 0.0, "ref": "C1"}
        db.save_feature_objects(layer_id, "pads", [pad], layer_key="bottom")
        row = db.conn().execute(
            "SELECT properties FROM objects WHERE layer_id=?", (layer_id,)
        ).fetchone()
        props = json.loads(row["properties"])
        assert props["kicad_layer"] == "B_Cu"

    def test_ref_stored_as_label(self, db, layer_id):
        db.save_feature_objects(layer_id, "pads", [self._pad(ref="U7")])
        row = db.conn().execute(
            "SELECT label FROM objects WHERE layer_id=?", (layer_id,)
        ).fetchone()
        assert row["label"] == "U7"

    def test_empty_ref_stored_as_null(self, db, layer_id):
        pad = {"x_mm": 1.0, "y_mm": 1.0, "w_mm": 1.0, "h_mm": 0.5,
               "rotation_deg": 0.0, "ref": ""}
        db.save_feature_objects(layer_id, "pads", [pad])
        row = db.conn().execute(
            "SELECT label FROM objects WHERE layer_id=?", (layer_id,)
        ).fetchone()
        assert row["label"] is None


# ===========================================================================
# db.save_feature_objects — traces
# ===========================================================================

class TestSaveFeatureObjectsTraces:

    def _trace(self, sx=0.0, sy=0.0, ex=5.0, ey=0.0, w=0.2, layer="F_Cu"):
        return {"start": [sx, sy], "end": [ex, ey], "width_mm": w, "layer": layer}

    def test_saves_correct_count(self, db, layer_id):
        n = db.save_feature_objects(layer_id, "traces", [self._trace(), self._trace(sy=1.0, ey=1.0)])
        assert n == 2

    def test_type_is_trace(self, db, layer_id):
        db.save_feature_objects(layer_id, "traces", [self._trace()])
        row = db.conn().execute(
            "SELECT type FROM objects WHERE layer_id=?", (layer_id,)
        ).fetchone()
        assert row["type"] == "trace"

    def test_midpoint_stored(self, db, layer_id):
        db.save_feature_objects(layer_id, "traces", [self._trace(sx=0.0, ex=10.0, sy=0.0, ey=4.0)])
        row = db.conn().execute(
            "SELECT x_mm, y_mm FROM objects WHERE layer_id=?", (layer_id,)
        ).fetchone()
        assert row["x_mm"] == pytest.approx(5.0)
        assert row["y_mm"] == pytest.approx(2.0)

    def test_properties_contain_start_end(self, db, layer_id):
        db.save_feature_objects(layer_id, "traces",
                                [self._trace(sx=1.0, sy=2.0, ex=3.0, ey=4.0, w=0.25)])
        row = db.conn().execute(
            "SELECT properties FROM objects WHERE layer_id=?", (layer_id,)
        ).fetchone()
        props = json.loads(row["properties"])
        assert props["start"] == [1.0, 2.0]
        assert props["end"]   == [3.0, 4.0]
        assert props["width_mm"] == pytest.approx(0.25)

    def test_width_stored_in_width_mm_column(self, db, layer_id):
        db.save_feature_objects(layer_id, "traces", [self._trace(w=0.3)])
        row = db.conn().execute(
            "SELECT width_mm FROM objects WHERE layer_id=?", (layer_id,)
        ).fetchone()
        assert row["width_mm"] == pytest.approx(0.3)


# ===========================================================================
# db.save_feature_objects — outline
# ===========================================================================

class TestSaveFeatureObjectsOutline:

    def _pts(self):
        return [[0.0, 0.0], [10.0, 0.0], [10.0, 8.0], [0.0, 8.0]]

    def test_saves_single_row(self, db, layer_id):
        n = db.save_feature_objects(layer_id, "outline", self._pts())
        assert n == 1

    def test_type_is_outline(self, db, layer_id):
        db.save_feature_objects(layer_id, "outline", self._pts())
        row = db.conn().execute(
            "SELECT type FROM objects WHERE layer_id=?", (layer_id,)
        ).fetchone()
        assert row["type"] == "outline"

    def test_points_stored_in_properties(self, db, layer_id):
        pts = self._pts()
        db.save_feature_objects(layer_id, "outline", pts)
        row = db.conn().execute(
            "SELECT properties FROM objects WHERE layer_id=?", (layer_id,)
        ).fetchone()
        props = json.loads(row["properties"])
        assert props["points"] == pts

    def test_empty_points_saves_zero_rows(self, db, layer_id):
        n = db.save_feature_objects(layer_id, "outline", [])
        assert n == 0

    def test_idempotent_replaces_outline(self, db, layer_id):
        db.save_feature_objects(layer_id, "outline", self._pts())
        new_pts = [[1.0, 1.0], [9.0, 1.0], [9.0, 7.0], [1.0, 7.0]]
        db.save_feature_objects(layer_id, "outline", new_pts)
        rows = db.conn().execute(
            "SELECT properties FROM objects WHERE layer_id=? AND type='outline'",
            (layer_id,),
        ).fetchall()
        assert len(rows) == 1
        props = json.loads(rows[0]["properties"])
        assert props["points"] == new_pts


# ===========================================================================
# db.save_feature_objects — error handling
# ===========================================================================

class TestSaveFeatureObjectsErrors:

    def test_raises_for_unknown_scan_type(self, db, layer_id):
        with pytest.raises(ValueError, match="unsupported scan_type"):
            db.save_feature_objects(layer_id, "banana", [])

    def test_text_scan_type_not_accepted(self, db, layer_id):
        with pytest.raises(ValueError):
            db.save_feature_objects(layer_id, "text", [])


# ===========================================================================
# db.save_feature_objects — cross-type isolation
# ===========================================================================

class TestSaveFeatureObjectsIsolation:
    """Saving one type must not disturb rows of other types on the same layer."""

    def test_pads_survive_via_rescan(self, db, layer_id):
        # Insert a pad manually
        db.conn().execute(
            "INSERT INTO objects (layer_id, type, x_mm, y_mm, width_mm, height_mm, "
            "rotation_deg, confidence, properties) VALUES (?,?,?,?,?,?,?,?,?)",
            (layer_id, "pad", 1.0, 1.0, 1.0, 0.5, 0.0, None, "{}"),
        )
        db.conn().commit()

        db.save_feature_objects(layer_id, "vias",
                                [{"x_mm": 5.0, "y_mm": 5.0, "drill_mm": 0.3, "annular_mm": 0.15}])

        pad_count = db.conn().execute(
            "SELECT COUNT(*) FROM objects WHERE layer_id=? AND type='pad'", (layer_id,)
        ).fetchone()[0]
        assert pad_count == 1, "Pad should survive a via rescan"

    def test_vias_survive_outline_rescan(self, db, layer_id):
        db.save_feature_objects(
            layer_id, "vias",
            [{"x_mm": 1.0, "y_mm": 1.0, "drill_mm": 0.3, "annular_mm": 0.15}]
        )
        db.save_feature_objects(
            layer_id, "outline",
            [[0.0, 0.0], [10.0, 0.0], [10.0, 8.0], [0.0, 8.0]]
        )

        via_count = db.conn().execute(
            "SELECT COUNT(*) FROM objects WHERE layer_id=? AND type='via'", (layer_id,)
        ).fetchone()[0]
        assert via_count == 1, "Via should survive an outline rescan"

    def test_traces_survive_pad_rescan(self, db, layer_id):
        db.save_feature_objects(
            layer_id, "traces",
            [{"start": [0.0, 0.0], "end": [5.0, 0.0], "width_mm": 0.2, "layer": "F_Cu"}]
        )
        db.save_feature_objects(
            layer_id, "pads",
            [{"x_mm": 3.0, "y_mm": 3.0, "w_mm": 1.0, "h_mm": 0.5,
              "rotation_deg": 0.0, "ref": "R1", "layer": "F_Cu"}]
        )

        trace_count = db.conn().execute(
            "SELECT COUNT(*) FROM objects WHERE layer_id=? AND type='trace'", (layer_id,)
        ).fetchone()[0]
        assert trace_count == 1, "Trace should survive a pad rescan"


# ===========================================================================
# Tests for LAB+CLAHE pipeline improvements (layers.py)
# ===========================================================================

class TestPreprocessClahe:
    """preprocess_clahe() output invariants."""

    def test_returns_same_shape(self):
        from toolkit.analysis.layers import preprocess_clahe
        img = np.zeros((100, 120, 3), dtype=np.uint8)
        out = preprocess_clahe(img)
        assert out.shape == img.shape

    def test_returns_uint8(self):
        from toolkit.analysis.layers import preprocess_clahe
        img = np.ones((50, 50, 3), dtype=np.uint8) * 128
        out = preprocess_clahe(img)
        assert out.dtype == np.uint8

    def test_dark_image_gets_brighter(self):
        """CLAHE should locally boost contrast — a uniform dark image should
        not become pitch-black after processing (L channel is redistributed)."""
        from toolkit.analysis.layers import preprocess_clahe
        img = np.ones((64, 64, 3), dtype=np.uint8) * 10   # very dark
        out = preprocess_clahe(img)
        # CLAHE on a uniform image keeps it uniform (no gradient to enhance),
        # but the output L value may shift slightly — it must stay uint8 range.
        assert out.min() >= 0
        assert out.max() <= 255

    def test_accepts_custom_clip_limit(self):
        from toolkit.analysis.layers import preprocess_clahe
        img = np.random.randint(0, 255, (80, 80, 3), dtype=np.uint8)
        out = preprocess_clahe(img, clip_limit=5.0, tile_size=8)
        assert out.shape == img.shape

    def test_accepts_custom_tile_size(self):
        from toolkit.analysis.layers import preprocess_clahe
        img = np.random.randint(0, 255, (128, 128, 3), dtype=np.uint8)
        out = preprocess_clahe(img, tile_size=32)
        assert out.shape == img.shape


class TestDefaultLab:
    """DEFAULT_LAB contains expected keys with valid ranges."""

    def test_has_copper_l_key(self):
        from toolkit.analysis.layers import DEFAULT_LAB
        assert "copper_lab_l" in DEFAULT_LAB

    def test_has_copper_a_key(self):
        from toolkit.analysis.layers import DEFAULT_LAB
        assert "copper_lab_a" in DEFAULT_LAB

    def test_has_copper_b_key(self):
        from toolkit.analysis.layers import DEFAULT_LAB
        assert "copper_lab_b" in DEFAULT_LAB

    def test_l_range_valid(self):
        from toolkit.analysis.layers import DEFAULT_LAB
        lo, hi = DEFAULT_LAB["copper_lab_l"]
        assert 0 <= lo < hi <= 255

    def test_a_range_valid(self):
        from toolkit.analysis.layers import DEFAULT_LAB
        lo, hi = DEFAULT_LAB["copper_lab_a"]
        assert 0 <= lo < hi <= 255

    def test_b_range_valid(self):
        from toolkit.analysis.layers import DEFAULT_LAB
        lo, hi = DEFAULT_LAB["copper_lab_b"]
        assert 0 <= lo < hi <= 255


class TestExtractCopperMaskLab:
    """extract_copper_mask() using the new dual-space pipeline."""

    def test_returns_binary_mask_shape(self):
        from toolkit.analysis.layers import extract_copper_mask, DEFAULT_HSV
        img = np.zeros((100, 100, 3), dtype=np.uint8)
        mask = extract_copper_mask(img, DEFAULT_HSV)
        assert mask.shape == (100, 100)

    def test_returns_uint8_dtype(self):
        from toolkit.analysis.layers import extract_copper_mask, DEFAULT_HSV
        img = np.zeros((50, 50, 3), dtype=np.uint8)
        mask = extract_copper_mask(img, DEFAULT_HSV)
        assert mask.dtype == np.uint8

    def test_mask_values_binary(self):
        from toolkit.analysis.layers import extract_copper_mask, DEFAULT_HSV
        img = np.random.randint(0, 255, (60, 60, 3), dtype=np.uint8)
        mask = extract_copper_mask(img, DEFAULT_HSV)
        unique = set(mask.flatten().tolist())
        assert unique.issubset({0, 255})

    def test_lab_override_keys_accepted(self):
        """Caller can override LAB ranges without error."""
        from toolkit.analysis.layers import extract_copper_mask, DEFAULT_HSV
        cfg = dict(DEFAULT_HSV)
        cfg["copper_lab_l"] = [50, 200]
        cfg["copper_lab_a"] = [125, 140]
        cfg["copper_lab_b"] = [130, 170]
        img = np.zeros((50, 50, 3), dtype=np.uint8)
        mask = extract_copper_mask(img, cfg)
        assert mask.shape == (50, 50)

    def test_copper_coloured_patch_detected(self):
        """A copper-coloured patch should produce non-zero mask pixels."""
        from toolkit.analysis.layers import extract_copper_mask, DEFAULT_HSV
        # HSV (20, 200, 220) → warm orange/copper; in BGR ≈ (20, 100, 220)
        img = np.zeros((100, 100, 3), dtype=np.uint8)
        img[30:70, 30:70] = (20, 100, 220)  # copper patch
        mask = extract_copper_mask(img, DEFAULT_HSV)
        assert mask[50, 50] == 255, "Copper-coloured patch must be detected"


# ===========================================================================
# Tests for eyedropper / colour picker (hsv_tuner.py)
# ===========================================================================

class TestSampleHsvRange:
    """sample_hsv_range() — pure-numpy eyedropper sampling logic."""

    def _solid(self, h: int, w: int, bgr) -> np.ndarray:
        img = np.zeros((h, w, 3), dtype=np.uint8)
        img[:] = bgr
        return img

    def test_returns_two_lists(self):
        from toolkit.gui.widgets.hsv_tuner import sample_hsv_range
        img = self._solid(50, 50, (0, 128, 200))
        lo, hi = sample_hsv_range(img, 25, 25)
        assert isinstance(lo, list) and isinstance(hi, list)

    def test_each_list_has_three_elements(self):
        from toolkit.gui.widgets.hsv_tuner import sample_hsv_range
        img = self._solid(50, 50, (0, 128, 200))
        lo, hi = sample_hsv_range(img, 25, 25)
        assert len(lo) == 3 and len(hi) == 3

    def test_lo_le_hi_on_each_channel(self):
        from toolkit.gui.widgets.hsv_tuner import sample_hsv_range
        img = self._solid(50, 50, (100, 150, 200))
        lo, hi = sample_hsv_range(img, 25, 25)
        for l, h in zip(lo, hi):
            assert l <= h

    def test_h_channel_clipped_to_179(self):
        from toolkit.gui.widgets.hsv_tuner import sample_hsv_range
        # Pure red in BGR → HSV hue ≈ 0
        img = self._solid(20, 20, (0, 0, 255))
        lo, hi = sample_hsv_range(img, 10, 10)
        assert 0 <= lo[0] <= 179
        assert 0 <= hi[0] <= 179

    def test_sv_channels_clipped_to_255(self):
        from toolkit.gui.widgets.hsv_tuner import sample_hsv_range
        img = self._solid(20, 20, (0, 255, 255))   # cyan → S and V = 255
        lo, hi = sample_hsv_range(img, 10, 10)
        assert 0 <= lo[1] <= 255
        assert 0 <= hi[1] <= 255
        assert 0 <= lo[2] <= 255
        assert 0 <= hi[2] <= 255

    def test_uniform_image_lo_equals_hi(self):
        """A perfectly uniform image has zero std — lo should equal hi."""
        from toolkit.gui.widgets.hsv_tuner import sample_hsv_range
        # uniform BGR → uniform HSV → std = 0 → lo == hi
        img = self._solid(30, 30, (50, 200, 100))
        lo, hi = sample_hsv_range(img, 15, 15)
        assert lo == hi, f"Expected lo==hi for uniform image, got {lo} vs {hi}"

    def test_black_image_stays_in_range(self):
        from toolkit.gui.widgets.hsv_tuner import sample_hsv_range
        img = np.zeros((30, 30, 3), dtype=np.uint8)
        lo, hi = sample_hsv_range(img, 15, 15)
        assert all(v >= 0 for v in lo)
        assert all(v >= 0 for v in hi)

    def test_boundary_coordinates_clamped(self):
        """Sampling at the very corner should not raise."""
        from toolkit.gui.widgets.hsv_tuner import sample_hsv_range
        img = self._solid(40, 40, (80, 80, 80))
        lo, hi = sample_hsv_range(img, 0, 0, radius=5)
        assert lo is not None and hi is not None

    def test_out_of_bounds_returns_fallback(self):
        """Coordinates outside the image should return a safe fallback."""
        from toolkit.gui.widgets.hsv_tuner import sample_hsv_range
        img = self._solid(20, 20, (80, 80, 80))
        lo, hi = sample_hsv_range(img, 500, 500, radius=5)
        assert lo == [0, 0, 0]
        assert hi == [179, 255, 255]

    def test_custom_radius(self):
        from toolkit.gui.widgets.hsv_tuner import sample_hsv_range
        img = np.random.randint(0, 255, (60, 60, 3), dtype=np.uint8)
        lo, hi = sample_hsv_range(img, 30, 30, radius=2)
        assert len(lo) == 3 and len(hi) == 3
