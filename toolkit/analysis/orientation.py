"""orientation.py — Component orientation helpers.

Pure functions with no Qt dependency so they can be unit-tested directly.
"""
from __future__ import annotations

_EDGES = ("top", "bottom", "left", "right")


def nearest_edge(
    cx: float,
    cy: float,
    rect_x: float,
    rect_y: float,
    rect_w: float,
    rect_h: float,
) -> str:
    """Return which edge of *rect* is closest (perpendicular distance) to *(cx, cy)*.

    Parameters
    ----------
    cx, cy       : click / query point in the same coordinate space as the rect
    rect_x, rect_y : top-left corner of the rect
    rect_w, rect_h : width and height of the rect

    Returns
    -------
    One of ``"top"``, ``"bottom"``, ``"left"``, ``"right"``.

    When two edges are exactly equidistant the first in the priority order
    ``top > bottom > left > right`` is returned (deterministic).
    """
    d_top    = abs(cy - rect_y)
    d_bottom = abs(cy - (rect_y + rect_h))
    d_left   = abs(cx - rect_x)
    d_right  = abs(cx - (rect_x + rect_w))

    distances = {
        "top":    d_top,
        "bottom": d_bottom,
        "left":   d_left,
        "right":  d_right,
    }
    # min() on dict items is stable for equal values (insertion order in Python 3.7+)
    return min(distances, key=lambda k: distances[k])


def edge_midpoint(
    edge: str,
    rect_x: float,
    rect_y: float,
    rect_w: float,
    rect_h: float,
) -> tuple[float, float]:
    """Return the midpoint of *edge* on a rect defined by top-left + size."""
    cx = rect_x + rect_w / 2
    cy = rect_y + rect_h / 2
    if edge == "top":
        return cx, rect_y
    if edge == "bottom":
        return cx, rect_y + rect_h
    if edge == "left":
        return rect_x, cy
    if edge == "right":
        return rect_x + rect_w, cy
    raise ValueError(f"Unknown edge: {edge!r}")


def inward_triangle_points(
    edge: str,
    rect_x: float,
    rect_y: float,
    rect_w: float,
    rect_h: float,
    size: float,
) -> list[tuple[float, float]]:
    """Return the 3 vertices of a filled triangle on *edge* pointing inward.

    The triangle base is centred at the edge midpoint with length *size*,
    and the apex is *size* inside the rect.
    """
    mx, my = edge_midpoint(edge, rect_x, rect_y, rect_w, rect_h)
    half = size / 2

    if edge == "top":
        return [(mx - half, my), (mx + half, my), (mx, my + size)]
    if edge == "bottom":
        return [(mx - half, my), (mx + half, my), (mx, my - size)]
    if edge == "left":
        return [(mx, my - half), (mx, my + half), (mx + size, my)]
    # right
    return [(mx, my - half), (mx, my + half), (mx - size, my)]
