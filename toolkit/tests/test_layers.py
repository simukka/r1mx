"""Unit tests for toolkit.analysis.layers coordinate math."""
from __future__ import annotations

import pytest

from toolkit.analysis.layers import coord_px_to_mm, px_to_mm


def test_px_to_mm_basic():
    assert px_to_mm(254.0, 10.0) == pytest.approx(25.4)


def test_px_to_mm_zero():
    assert px_to_mm(0, 5.0) == pytest.approx(0.0)


def test_coord_px_to_mm():
    x_mm, y_mm = coord_px_to_mm(100.0, 200.0, 10.0)
    assert x_mm == pytest.approx(10.0)
    assert y_mm == pytest.approx(20.0)
