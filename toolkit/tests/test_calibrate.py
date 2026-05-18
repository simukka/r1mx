"""Unit tests for toolkit.analysis.calibrate."""
from __future__ import annotations

import pytest

from toolkit.analysis.calibrate import compute_px_per_mm


def test_compute_px_per_mm_horizontal():
    pt1 = [0.0, 0.0]
    pt2 = [100.0, 0.0]
    ppm = compute_px_per_mm(pt1, pt2, 25.4)
    assert ppm == pytest.approx(100.0 / 25.4, rel=1e-4)


def test_compute_px_per_mm_diagonal():
    pt1 = [0.0, 0.0]
    pt2 = [3.0, 4.0]
    ppm = compute_px_per_mm(pt1, pt2, 1.0)
    assert ppm == pytest.approx(5.0)
