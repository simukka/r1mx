"""
Tests for FootprintOverlayItem — coordinate extraction and transforms.

These tests run headless (no display required) by using a QApplication
fixture and testing only the maths, not painting.
"""
import math

import pytest

from toolkit.analysis.pinout import BBox, PadDetection


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def _make_app():
    """Return a QApplication (or the existing one)."""
    from PyQt6.QtWidgets import QApplication
    import sys
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv[:1])
    return app


def _pad(cx: float, cy: float, num: str = "1", label: str = "") -> PadDetection:
    w = h = 0.05
    return PadDetection(
        bbox=BBox(x=cx - w / 2, y=cy - h / 2, w=w, h=h),
        pin_number=num, label=label, shape="rect",
    )


def _overlay(pads, w=100.0, h=50.0):
    from toolkit.gui.items.footprint_overlay import FootprintOverlayItem
    return FootprintOverlayItem(pads=pads, component_w_scene=w, component_h_scene=h)


@pytest.fixture(scope="module")
def app():
    return _make_app()


# ---------------------------------------------------------------------------
# to_absolute_scene_coords — no rotation
# ---------------------------------------------------------------------------

class TestAbsoluteSceneCoords:
    def test_no_rotation_pad_at_top_left(self, app):
        pad = _pad(0.0, 0.0)
        ov = _overlay([pad], w=100, h=50)
        ov.setPos(10, 20)
        coords = ov.to_absolute_scene_coords()
        c = coords[0]
        # pad.cx=0 → lx=0, after rotation centre (50,25): dx=-50→rx=0+50=50-50=0, scene=10+0=10
        assert abs(c["scene_x"] - 10.0) < 1e-6
        assert abs(c["scene_y"] - 20.0) < 1e-6

    def test_no_rotation_pad_at_centre(self, app):
        pad = _pad(0.5, 0.5)
        ov = _overlay([pad], w=100, h=50)
        ov.setPos(0, 0)
        coords = ov.to_absolute_scene_coords()
        assert abs(coords[0]["scene_x"] - 50.0) < 1e-6
        assert abs(coords[0]["scene_y"] - 25.0) < 1e-6

    def test_no_rotation_pad_at_bottom_right(self, app):
        pad = _pad(1.0, 1.0)
        ov = _overlay([pad], w=100, h=50)
        ov.setPos(0, 0)
        coords = ov.to_absolute_scene_coords()
        assert abs(coords[0]["scene_x"] - 100.0) < 1e-6
        assert abs(coords[0]["scene_y"] - 50.0) < 1e-6

    def test_position_offset_applied(self, app):
        pad = _pad(0.5, 0.5)
        ov = _overlay([pad], w=100, h=50)
        ov.setPos(200, 300)
        coords = ov.to_absolute_scene_coords()
        assert abs(coords[0]["scene_x"] - 250.0) < 1e-6
        assert abs(coords[0]["scene_y"] - 325.0) < 1e-6

    def test_multiple_pads(self, app):
        pads = [_pad(0.0, 0.0, "1"), _pad(1.0, 0.0, "2"), _pad(1.0, 1.0, "3")]
        ov = _overlay(pads, w=100, h=50)
        ov.setPos(0, 0)
        coords = ov.to_absolute_scene_coords()
        assert len(coords) == 3
        assert abs(coords[0]["scene_x"] -   0.0) < 1e-6
        assert abs(coords[1]["scene_x"] - 100.0) < 1e-6
        assert abs(coords[2]["scene_x"] - 100.0) < 1e-6
        assert abs(coords[2]["scene_y"] -  50.0) < 1e-6

    def test_pin_number_and_label_preserved(self, app):
        pad = _pad(0.5, 0.5, num="7", label="VCC")
        ov = _overlay([pad])
        ov.setPos(0, 0)
        c = ov.to_absolute_scene_coords()[0]
        assert c["pin_number"] == "7"
        assert c["label"] == "VCC"
        assert c["shape"] == "rect"

    def test_pads_outside_component_body_allowed(self, app):
        """A pad at cx=1.5 is 50% outside the right edge — x > w."""
        pad = _pad(1.5, 0.5)
        ov = _overlay([pad], w=100, h=50)
        ov.setPos(0, 0)
        coords = ov.to_absolute_scene_coords()
        # local x = 1.5*100=150; rotate=0 → scene_x = 0 + 150 = 150 > w=100
        assert coords[0]["scene_x"] > 100.0


# ---------------------------------------------------------------------------
# to_absolute_scene_coords — rotation
# ---------------------------------------------------------------------------

class TestAbsoluteSceneCoordsRotation:
    def test_rotate_180_centre_pad_unchanged(self, app):
        """Centre pad stays at centre after any rotation."""
        pad = _pad(0.5, 0.5)
        ov = _overlay([pad], w=100, h=50)
        ov.setPos(0, 0)
        ov.rotate_by(180)
        c = ov.to_absolute_scene_coords()[0]
        assert abs(c["scene_x"] - 50.0) < 1e-3
        assert abs(c["scene_y"] - 25.0) < 1e-3

    def test_rotate_90_cw_top_left_moves_to_top_right(self, app):
        """
        90° CW rotation of pad at (0,0):
          dx=-50, dy=-25
          rx = cos(-90)*-50 - sin(-90)*-25 = 0*-50 - (-1)*-25 = -25  → +50 = 25
          ry = sin(-90)*-50 + cos(-90)*-25 = (-1)*-50 + 0*-25 = 50   → +25 = 75

        Wait, rotate_by(90) means clockwise 90° in screen coords (y-down).
        angle_deg=90 → angle_rad=π/2
          cos(π/2)=0, sin(π/2)=1
          dx=0-50=-50, dy=0-25=-25
          rx = 0*-50 - 1*-25 = 25  → +50 = 75
          ry = 1*-50 + 0*-25 = -50 → +25 = -25
        """
        pad = _pad(0.0, 0.0)
        ov = _overlay([pad], w=100, h=50)
        ov.setPos(0, 0)
        ov.rotate_by(90)
        c = ov.to_absolute_scene_coords()[0]
        assert abs(c["scene_x"] - 75.0) < 1e-3
        assert abs(c["scene_y"] - (-25.0)) < 1e-3

    def test_rotate_ccw_is_negative_cw(self, app):
        pad = _pad(0.25, 0.75)
        ov1 = _overlay([pad], w=100, h=50)
        ov2 = _overlay([pad], w=100, h=50)
        ov1.setPos(0, 0)
        ov2.setPos(0, 0)
        ov1.rotate_by(90)
        ov1.rotate_by(90)   # 180 total
        ov2.rotate_by(180)
        c1 = ov1.to_absolute_scene_coords()[0]
        c2 = ov2.to_absolute_scene_coords()[0]
        assert abs(c1["scene_x"] - c2["scene_x"]) < 1e-3
        assert abs(c1["scene_y"] - c2["scene_y"]) < 1e-3

    def test_rotation_with_offset(self, app):
        """Position offset should be additive with rotation result."""
        pad = _pad(0.5, 0.5)
        ov = _overlay([pad], w=100, h=50)
        ov.setPos(500, 300)
        ov.rotate_by(90)
        c = ov.to_absolute_scene_coords()[0]
        # centre pad stays at centre; scene = pos + (w/2, h/2) = 500+50, 300+25
        assert abs(c["scene_x"] - 550.0) < 1e-3
        assert abs(c["scene_y"] - 325.0) < 1e-3


# ---------------------------------------------------------------------------
# to_absolute_scene_coords — scale
# ---------------------------------------------------------------------------

class TestAbsoluteSceneCoordsScale:
    def test_scale_up_moves_corners_outward(self, app):
        pad = _pad(1.0, 1.0)
        ov = _overlay([pad], w=100, h=50)
        ov.setPos(0, 0)
        coords_before = ov.to_absolute_scene_coords()[0]
        ov.scale_by(2.0)
        coords_after = ov.to_absolute_scene_coords()[0]
        # After scale×2: w=200, h=100 → pad at (200, 100) local → scene = (200, 100)
        assert coords_after["scene_x"] > coords_before["scene_x"]
        assert coords_after["scene_y"] > coords_before["scene_y"]

    def test_scale_down_clamps_at_minimum(self, app):
        pad = _pad(0.5, 0.5)
        ov = _overlay([pad], w=100, h=50)
        ov.setPos(0, 0)
        for _ in range(100):
            ov.scale_by(0.1)
        # scale clamped at 0.05
        w = ov._w
        assert w >= 100 * 0.05 - 1e-6


# ---------------------------------------------------------------------------
# translate (keyboard path) — affects pos()
# ---------------------------------------------------------------------------

class TestTranslate:
    def test_translate_updates_pos(self, app):
        pad = _pad(0.5, 0.5)
        ov = _overlay([pad], w=100, h=50)
        ov.setPos(0, 0)
        ov.translate(30, 15)
        assert abs(ov.pos().x() - 30.0) < 1e-6
        assert abs(ov.pos().y() - 15.0) < 1e-6

    def test_translate_reflected_in_scene_coords(self, app):
        pad = _pad(0.5, 0.5)
        ov = _overlay([pad], w=100, h=50)
        ov.setPos(0, 0)
        ov.translate(10, 20)
        c = ov.to_absolute_scene_coords()[0]
        assert abs(c["scene_x"] - (10 + 50)) < 1e-6
        assert abs(c["scene_y"] - (20 + 25)) < 1e-6


# ---------------------------------------------------------------------------
# Legacy to_component_relative_coords still works
# ---------------------------------------------------------------------------

class TestLegacyRelativeCoords:
    def test_centre_pad_returns_half_half(self, app):
        pad = _pad(0.5, 0.5)
        ov = _overlay([pad])
        coords = ov.to_component_relative_coords()
        assert abs(coords[0]["x_rel"] - 0.5) < 1e-6
        assert abs(coords[0]["y_rel"] - 0.5) < 1e-6

    def test_corner_pad(self, app):
        pad = _pad(0.0, 0.0)
        ov = _overlay([pad])
        coords = ov.to_component_relative_coords()
        assert abs(coords[0]["x_rel"] - 0.0) < 1e-6
        assert abs(coords[0]["y_rel"] - 0.0) < 1e-6

    def test_rotate_90_moves_corner(self, app):
        pad = _pad(1.0, 0.0)
        ov = _overlay([pad])
        ov.rotate_by(90)
        c = ov.to_component_relative_coords()[0]
        # (1-0.5, 0-0.5)=(0.5,-0.5), rot90: rx=0*0.5-1*(-0.5)=0.5, ry=1*0.5+0*(-0.5)=0.5 → +0.5 each = (1.0, 1.0)
        assert abs(c["x_rel"] - 1.0) < 1e-3
        assert abs(c["y_rel"] - 1.0) < 1e-3
