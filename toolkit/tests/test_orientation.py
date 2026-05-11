"""test_orientation.py — Unit tests for toolkit.analysis.orientation."""
from __future__ import annotations

import pytest
from toolkit.analysis.orientation import (
    edge_midpoint,
    inward_triangle_points,
    nearest_edge,
)

# Rect used across most tests: top-left (10, 20), 100 wide, 60 tall
_X, _Y, _W, _H = 10.0, 20.0, 100.0, 60.0


class TestNearestEdge:

    def test_click_above_rect_returns_top(self):
        assert nearest_edge(60, 15, _X, _Y, _W, _H) == "top"

    def test_click_below_rect_returns_bottom(self):
        assert nearest_edge(60, 90, _X, _Y, _W, _H) == "bottom"

    def test_click_left_of_rect_returns_left(self):
        assert nearest_edge(5, 50, _X, _Y, _W, _H) == "left"

    def test_click_right_of_rect_returns_right(self):
        assert nearest_edge(115, 50, _X, _Y, _W, _H) == "right"

    def test_click_near_top_inside_rect(self):
        # Inside, but much closer to top than any other edge
        assert nearest_edge(60, 22, _X, _Y, _W, _H) == "top"

    def test_click_near_bottom_inside_rect(self):
        assert nearest_edge(60, 78, _X, _Y, _W, _H) == "bottom"

    def test_click_near_left_inside_rect(self):
        assert nearest_edge(12, 50, _X, _Y, _W, _H) == "left"

    def test_click_near_right_inside_rect(self):
        assert nearest_edge(108, 50, _X, _Y, _W, _H) == "right"

    def test_click_exactly_on_top_edge(self):
        assert nearest_edge(60, _Y, _X, _Y, _W, _H) == "top"

    def test_click_exactly_on_bottom_edge(self):
        assert nearest_edge(60, _Y + _H, _X, _Y, _W, _H) == "bottom"

    def test_click_exactly_on_left_edge(self):
        assert nearest_edge(_X, 50, _X, _Y, _W, _H) == "left"

    def test_click_exactly_on_right_edge(self):
        assert nearest_edge(_X + _W, 50, _X, _Y, _W, _H) == "right"

    def test_equidistant_top_bottom_prefers_top(self):
        # Click at vertical centre, horizontal centre → top and bottom equally close
        cy = _Y + _H / 2   # 50 — equidistant from top(20) and bottom(80)
        # Make left/right further away by using a wide rect
        result = nearest_edge(60, cy, _X, _Y, _W, _H)
        # top has priority over bottom per docstring; left/right are 50px away, v is 30
        assert result == "top"

    def test_square_rect_top_left_corner(self):
        # Click at top-left corner: equidistant from top and left → "top" wins
        result = nearest_edge(0, 0, 0, 0, 100, 100)
        assert result == "top"

    def test_zero_size_rect_returns_top(self):
        # Degenerate case: all distances are equal (d_top = d_bottom = d_left = d_right = 0)
        result = nearest_edge(5, 5, 5, 5, 0, 0)
        assert result == "top"


class TestEdgeMidpoint:

    def test_top_midpoint(self):
        mx, my = edge_midpoint("top", _X, _Y, _W, _H)
        assert mx == _X + _W / 2
        assert my == _Y

    def test_bottom_midpoint(self):
        mx, my = edge_midpoint("bottom", _X, _Y, _W, _H)
        assert mx == _X + _W / 2
        assert my == _Y + _H

    def test_left_midpoint(self):
        mx, my = edge_midpoint("left", _X, _Y, _W, _H)
        assert mx == _X
        assert my == _Y + _H / 2

    def test_right_midpoint(self):
        mx, my = edge_midpoint("right", _X, _Y, _W, _H)
        assert mx == _X + _W
        assert my == _Y + _H / 2

    def test_invalid_edge_raises(self):
        with pytest.raises(ValueError, match="Unknown edge"):
            edge_midpoint("diagonal", _X, _Y, _W, _H)


class TestInwardTrianglePoints:

    def _assert_triangle(self, pts, expected_count=3):
        assert len(pts) == expected_count

    def test_top_triangle_apex_points_inward(self):
        pts = inward_triangle_points("top", 0, 0, 100, 60, 10)
        # Apex (3rd point) should have y > 0 (inside the rect)
        apex_y = pts[2][1]
        assert apex_y > 0

    def test_bottom_triangle_apex_points_inward(self):
        pts = inward_triangle_points("bottom", 0, 0, 100, 60, 10)
        apex_y = pts[2][1]
        assert apex_y < 60  # inward = above bottom edge

    def test_left_triangle_apex_points_inward(self):
        pts = inward_triangle_points("left", 0, 0, 100, 60, 10)
        apex_x = pts[2][0]
        assert apex_x > 0

    def test_right_triangle_apex_points_inward(self):
        pts = inward_triangle_points("right", 0, 0, 100, 60, 10)
        apex_x = pts[2][0]
        assert apex_x < 100

    def test_top_base_centred_on_midpoint(self):
        pts = inward_triangle_points("top", 0, 0, 100, 60, 10)
        base_x = (pts[0][0] + pts[1][0]) / 2
        assert abs(base_x - 50) < 1e-9  # midpoint of top edge


# ---------------------------------------------------------------------------
# Additional nearest_edge edge cases
# ---------------------------------------------------------------------------

class TestNearestEdgeAdditional:
    """Corner and off-rect cases not covered by the main test class."""

    def test_top_right_corner_equidistant_prefers_top(self):
        # Click exactly at the top-right corner: d_top=0, d_right=0, d_bottom=H, d_left=W
        result = nearest_edge(100, 0, 0, 0, 100, 60)
        assert result == "top"   # top priority over right

    def test_bottom_right_corner_prefers_bottom(self):
        # d_bottom=0, d_right=0 → bottom has priority over right
        result = nearest_edge(100, 60, 0, 0, 100, 60)
        assert result == "bottom"

    def test_bottom_left_corner_prefers_bottom(self):
        # d_bottom=0, d_left=0 → bottom has priority over left
        result = nearest_edge(0, 60, 0, 0, 100, 60)
        assert result == "bottom"

    def test_top_left_corner_prefers_top(self):
        # d_top=0, d_left=0 → top has priority over left
        result = nearest_edge(0, 0, 0, 0, 100, 60)
        assert result == "top"

    def test_click_far_outside_rect_top_side(self):
        # Point above the rect, close to top edge horizontally centred
        # d_top=5, d_bottom=65, d_left=50, d_right=50 → "top"
        result = nearest_edge(50, -5, 0, 0, 100, 60)
        assert result == "top"

    def test_click_far_outside_rect_right_side(self):
        # Point right of rect, very close to its right edge, centred vertically
        # d_right=2, d_top=30, d_bottom=30, d_left=202 → "right"
        result = nearest_edge(102, 30, 0, 0, 100, 60)
        assert result == "right"

    def test_negative_rect_origin(self):
        # Rect at (-200, -100), 400 wide, 200 tall — click near top edge
        result = nearest_edge(0, -95, -200, -100, 400, 200)
        assert result == "top"

    def test_float_coords_exact(self):
        result = nearest_edge(10.5, 0.1, 0.0, 0.0, 100.0, 60.0)
        assert result == "top"

    def test_tall_narrow_rect_click_near_left(self):
        # 10 wide, 500 tall — click near left edge
        result = nearest_edge(1, 250, 0, 0, 10, 500)
        assert result == "left"

    def test_wide_flat_rect_click_near_top(self):
        # 500 wide, 10 tall — click near top edge
        result = nearest_edge(250, 1, 0, 0, 500, 10)
        assert result == "top"


# ---------------------------------------------------------------------------
# Additional inward_triangle_points edge cases
# ---------------------------------------------------------------------------

class TestInwardTriangleAdditional:

    def test_returns_exactly_three_vertices_for_all_edges(self):
        for edge in ("top", "bottom", "left", "right"):
            pts = inward_triangle_points(edge, 0, 0, 100, 60, 10)
            assert len(pts) == 3, f"Expected 3 vertices for edge={edge}"

    def test_base_span_equals_size_top(self):
        """Base length must equal *size* (not 2*size)."""
        pts = inward_triangle_points("top", 0, 0, 100, 60, 20)
        base_len = abs(pts[1][0] - pts[0][0])
        assert abs(base_len - 20) < 1e-9

    def test_base_span_equals_size_left(self):
        pts = inward_triangle_points("left", 0, 0, 100, 60, 20)
        base_len = abs(pts[1][1] - pts[0][1])
        assert abs(base_len - 20) < 1e-9

    def test_apex_depth_equals_size_top(self):
        """Apex must be exactly *size* inside the rect from the edge."""
        pts = inward_triangle_points("top", 0, 0, 100, 60, 15)
        # Base y == 0 (top edge), apex y == 15 (size inside)
        assert pts[2][1] == 15

    def test_apex_depth_equals_size_bottom(self):
        pts = inward_triangle_points("bottom", 0, 0, 100, 60, 15)
        assert pts[2][1] == 60 - 15   # 45

    def test_apex_depth_equals_size_left(self):
        pts = inward_triangle_points("left", 0, 0, 100, 60, 15)
        assert pts[2][0] == 15

    def test_apex_depth_equals_size_right(self):
        pts = inward_triangle_points("right", 0, 0, 100, 60, 15)
        assert pts[2][0] == 100 - 15   # 85

    def test_translated_rect_triangle_moves_with_it(self):
        """Triangle coordinates must be relative to rect_x, rect_y."""
        pts_origin = inward_triangle_points("top", 0, 0, 100, 60, 10)
        pts_offset = inward_triangle_points("top", 50, 30, 100, 60, 10)
        for (ox, oy), (px, py) in zip(pts_origin, pts_offset):
            assert abs(px - (ox + 50)) < 1e-9
            assert abs(py - (oy + 30)) < 1e-9

    def test_size_zero_triangle_is_degenerate_point(self):
        """size=0: all three vertices collapse to the edge midpoint."""
        pts = inward_triangle_points("top", 0, 0, 100, 60, 0)
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        assert all(abs(x - 50) < 1e-9 for x in xs)
        assert all(y == 0 for y in ys)

    def test_all_vertices_are_2_tuples(self):
        for edge in ("top", "bottom", "left", "right"):
            pts = inward_triangle_points(edge, 0, 0, 100, 60, 12)
            for v in pts:
                assert len(v) == 2, f"Vertex {v!r} is not a 2-tuple"

