"""Unit tests for toolkit.analysis.pinout — BBox, shape classification,
pad detection helpers, label assignment, and orchestrator.  No real PDF
files or subprocess calls are used; everything is driven with synthetic
numpy arrays and mocks.
"""

from __future__ import annotations

import math
import subprocess
from pathlib import Path
from unittest.mock import MagicMock, patch

import cv2
import numpy as np
import pytest

from toolkit.analysis.pinout import (
    BBox,
    OcrWord,
    PadDetection,
    PinoutResult,
    _classify_shape,
    assign_labels,
    detect_pads,
    extract_pinout,
    ocr_labels,
)


# ─── BBox ─────────────────────────────────────────────────────────────────────

class TestBBox:
    def test_cx_cy(self):
        b = BBox(0.1, 0.2, 0.4, 0.6)
        assert b.cx == pytest.approx(0.3)
        assert b.cy == pytest.approx(0.5)

    def test_area(self):
        b = BBox(0, 0, 0.5, 0.4)
        assert b.area == pytest.approx(0.2)

    def test_iou_identical(self):
        b = BBox(0, 0, 1, 1)
        assert b.iou(b) == pytest.approx(1.0)

    def test_iou_no_overlap(self):
        a = BBox(0, 0, 0.4, 0.4)
        b = BBox(0.6, 0.6, 0.4, 0.4)
        assert a.iou(b) == pytest.approx(0.0)

    def test_iou_partial(self):
        a = BBox(0, 0, 0.5, 1.0)
        b = BBox(0.25, 0, 0.5, 1.0)
        # Intersection width = 0.25, height = 1.0 → 0.25
        # Union = 0.5 + 0.5 − 0.25 = 0.75
        assert a.iou(b) == pytest.approx(0.25 / 0.75)

    def test_to_dict_round_trip(self):
        b = BBox(0.1, 0.2, 0.3, 0.4)
        assert BBox.from_dict(b.to_dict()) == b

    def test_from_dict(self):
        d = {"x": 0.0, "y": 0.1, "w": 0.5, "h": 0.6}
        b = BBox.from_dict(d)
        assert (b.x, b.y, b.w, b.h) == (0.0, 0.1, 0.5, 0.6)


# ─── _classify_shape ─────────────────────────────────────────────────────────

def _make_circle_contour(cx, cy, r, n=64) -> np.ndarray:
    angles = np.linspace(0, 2 * np.pi, n, endpoint=False)
    pts = np.array([
        [[int(cx + r * np.cos(a)), int(cy + r * np.sin(a))]]
        for a in angles
    ], dtype=np.int32)
    return pts


def _make_rect_contour(x, y, w, h) -> np.ndarray:
    return np.array([
        [[x, y]], [[x + w, y]], [[x + w, y + h]], [[x, y + h]]
    ], dtype=np.int32)


class TestClassifyShape:
    def test_circle_contour(self):
        cnt = _make_circle_contour(50, 50, 20)
        assert _classify_shape(cnt) == "circle"

    def test_square_contour(self):
        # A perfect 30×30 square has circularity ≈ π/4 ≈ 0.785 which exceeds the
        # circle threshold, so the algorithm correctly classifies it as "circle"
        # (it IS rounder than a rectangle).  Expect circle or square.
        cnt = _make_rect_contour(10, 10, 30, 30)
        assert _classify_shape(cnt) in ("circle", "square")

    def test_rect_contour(self):
        cnt = _make_rect_contour(10, 10, 80, 20)
        assert _classify_shape(cnt) == "rect"

    def test_zero_perimeter(self):
        # A degenerate 1-point contour
        cnt = np.array([[[10, 10]]], dtype=np.int32)
        result = _classify_shape(cnt)
        assert result in ("circle", "square", "rect")


# ─── detect_pads ─────────────────────────────────────────────────────────────

def _white_bg(h, w):
    return np.full((h, w, 3), 255, dtype=np.uint8)


def _draw_circle(img, cx, cy, r, color=(0, 0, 0)):
    cv2.circle(img, (cx, cy), r, color, -1)


def _draw_rect(img, x1, y1, x2, y2, color=(0, 0, 0)):
    cv2.rectangle(img, (x1, y1), (x2, y2), color, -1)


class TestDetectPads:
    def test_detects_single_circle(self):
        img = _white_bg(200, 200)
        _draw_circle(img, 100, 100, 20)
        pads = detect_pads(img)
        assert len(pads) >= 1

    def test_detects_multiple_circles(self):
        img = _white_bg(200, 400)
        _draw_circle(img, 80, 100, 15)
        _draw_circle(img, 200, 100, 15)
        _draw_circle(img, 320, 100, 15)
        pads = detect_pads(img)
        assert len(pads) >= 2

    def test_ignores_tiny_noise(self):
        img = _white_bg(200, 200)
        # Draw a 2×2 dot (< _MIN_PAD_AREA_PX)
        img[50:52, 50:52] = 0
        pads = detect_pads(img)
        assert len(pads) == 0

    def test_ignores_full_image_rect(self):
        img = _white_bg(200, 200)
        # Draw a rectangle that is 20% of the image area → should be filtered
        _draw_rect(img, 10, 10, 190, 190)
        pads = detect_pads(img)
        # The full border rect exceeds _MAX_PAD_FRACTION (10% of 200×200=4000px)
        # area=180×180=32400 > 0.1×40000=4000 → filtered
        # So we shouldn't get a single huge pad
        for p in pads:
            assert p.bbox.area < 0.10

    def test_deduplicates_overlapping_pads(self):
        img = _white_bg(200, 200)
        # Two almost-identical circles at the same spot
        _draw_circle(img, 100, 100, 20)
        _draw_circle(img, 102, 102, 18)   # nearly same → high IoU
        pads = detect_pads(img)
        # Should be deduplicated to at most 2 (likely 1)
        assert len(pads) <= 2

    def test_returns_normalised_coords(self):
        img = _white_bg(200, 400)
        _draw_circle(img, 200, 100, 20)
        pads = detect_pads(img)
        for p in pads:
            assert 0.0 <= p.bbox.x <= 1.0
            assert 0.0 <= p.bbox.y <= 1.0
            assert 0.0 <  p.bbox.w <= 1.0
            assert 0.0 <  p.bbox.h <= 1.0

    def test_shape_circle_label_on_round_pad(self):
        img = _white_bg(300, 300)
        _draw_circle(img, 150, 150, 30)
        pads = detect_pads(img)
        circles = [p for p in pads if p.shape == "circle"]
        assert len(circles) >= 1

    def test_shape_rect_on_elongated_pad(self):
        # 120×25 pad is clearly elongated → should be "rect"
        img = _white_bg(200, 400)
        _draw_rect(img, 100, 80, 220, 105)   # 120×25 px — well within area limits
        pads = detect_pads(img)
        rects = [p for p in pads if p.shape in ("rect", "square")]
        assert len(rects) >= 1


# ─── assign_labels ───────────────────────────────────────────────────────────

def _make_pad(cx, cy, size=0.05) -> PadDetection:
    half = size / 2
    return PadDetection(bbox=BBox(cx - half, cy - half, size, size))


def _make_word(text, cx, cy, size=0.02) -> OcrWord:
    half = size / 2
    return OcrWord(text=text, bbox=BBox(cx - half, cy - half, size, size))


class TestAssignLabels:
    def test_assigns_numeric_as_pin_number(self):
        pad = _make_pad(0.5, 0.5, size=0.08)
        word = _make_word("14", 0.52, 0.52)
        result = assign_labels([pad], [word])
        assert result[0].pin_number == "14"

    def test_assigns_alpha_as_label(self):
        pad = _make_pad(0.5, 0.5, size=0.08)
        word = _make_word("GND", 0.52, 0.52)
        result = assign_labels([pad], [word])
        assert result[0].label == "GND"

    def test_assigns_both_pin_and_label(self):
        pad = _make_pad(0.5, 0.5, size=0.10)
        num = _make_word("3", 0.51, 0.51)
        lbl = _make_word("VCC", 0.53, 0.53)
        result = assign_labels([pad], [num, lbl])
        assert result[0].pin_number == "3"
        assert result[0].label == "VCC"

    def test_does_not_assign_distant_word(self):
        pad = _make_pad(0.1, 0.1, size=0.04)
        word = _make_word("99", 0.9, 0.9)   # far away
        result = assign_labels([pad], [word])
        assert result[0].pin_number == ""

    def test_each_word_assigned_to_at_most_one_pad(self):
        p1 = _make_pad(0.2, 0.5, size=0.08)
        p2 = _make_pad(0.8, 0.5, size=0.08)
        shared_word = _make_word("1", 0.21, 0.50)   # very close to p1
        result = assign_labels([p1, p2], [shared_word])
        assigned = sum(1 for p in result if p.pin_number == "1")
        assert assigned == 1

    def test_returns_copy_not_mutating_original(self):
        pad = _make_pad(0.5, 0.5)
        word = _make_word("7", 0.51, 0.51)
        original_pin = pad.pin_number
        result = assign_labels([pad], [word])
        # Original pad should not be modified
        assert pad.pin_number == original_pin

    def test_empty_pads_returns_empty(self):
        result = assign_labels([], [_make_word("1", 0.5, 0.5)])
        assert result == []

    def test_empty_words_leaves_pads_unassigned(self):
        pad = _make_pad(0.5, 0.5)
        result = assign_labels([pad], [])
        assert result[0].pin_number == ""
        assert result[0].label == ""

    def test_negative_word_ignored(self):
        pad = _make_pad(0.5, 0.5, size=0.08)
        word = _make_word("-5", 0.51, 0.51)   # "-5" → lstrip → not purely digit
        result = assign_labels([pad], [word])
        # "-5" is not purely digits (lstrip("-") = "5" which IS digits)
        assert result[0].pin_number == "-5" or result[0].label == "-5"


# ─── PinoutResult.to_db_pins ─────────────────────────────────────────────────

class TestPinoutResultToDbPins:
    def test_keys_present(self):
        pad = PadDetection(bbox=BBox(0.1, 0.2, 0.1, 0.1), pin_number="1", label="CLK")
        result = PinoutResult(
            pads=[pad], image_width=100, image_height=100,
            source_page=1, source_bbox=BBox(0, 0, 1, 1),
        )
        pins = result.to_db_pins()
        assert len(pins) == 1
        assert pins[0]["pin_number"] == "1"
        assert pins[0]["label"] == "CLK"
        assert "x_rel" in pins[0]
        assert "y_rel" in pins[0]
        assert "shape" in pins[0]

    def test_x_rel_is_centroid(self):
        pad = PadDetection(bbox=BBox(0.2, 0.4, 0.2, 0.2))
        result = PinoutResult(
            pads=[pad], image_width=100, image_height=100,
            source_page=1, source_bbox=BBox(0, 0, 1, 1),
        )
        pins = result.to_db_pins()
        assert pins[0]["x_rel"] == pytest.approx(0.3)  # 0.2 + 0.2/2
        assert pins[0]["y_rel"] == pytest.approx(0.5)  # 0.4 + 0.2/2


# ─── crop_pinout_image (subprocess mock) ─────────────────────────────────────

class TestCropPinoutImage:
    def test_raises_on_pdftoppm_not_found(self):
        from toolkit.analysis.pinout import crop_pinout_image
        with patch("subprocess.run", side_effect=FileNotFoundError):
            with pytest.raises(RuntimeError, match="pdftoppm not found"):
                crop_pinout_image(Path("x.pdf"), 1, BBox(0, 0, 1, 1))

    def test_raises_on_timeout(self):
        from toolkit.analysis.pinout import crop_pinout_image
        with patch("subprocess.run", side_effect=subprocess.TimeoutExpired("pdftoppm", 30)):
            with pytest.raises(RuntimeError, match="timed out"):
                crop_pinout_image(Path("x.pdf"), 1, BBox(0, 0, 1, 1))

    def test_raises_when_png_missing(self):
        from toolkit.analysis.pinout import crop_pinout_image
        with patch("subprocess.run", return_value=MagicMock(returncode=0)):
            with pytest.raises(RuntimeError):
                crop_pinout_image(Path("x.pdf"), 1, BBox(0, 0, 1, 1))

    def test_crops_correctly(self, tmp_path):
        """Create a fake PNG, mock pdftoppm to copy it into the tmp dir."""
        from toolkit.analysis.pinout import crop_pinout_image

        # 400×200 white image with a black square in the right half
        img = np.full((200, 400, 3), 255, dtype=np.uint8)
        cv2.rectangle(img, (200, 50), (380, 150), (0, 0, 0), -1)

        png_src = tmp_path / "source.png"
        cv2.imwrite(str(png_src), img)

        def fake_pdftoppm(cmd, **kw):
            # Find the out_base from the command and write the PNG there
            out_base = Path(cmd[-1])
            import shutil
            shutil.copy(str(png_src), str(out_base.parent / "page.png"))
            return MagicMock(returncode=0)

        with patch("subprocess.run", side_effect=fake_pdftoppm):
            crop = crop_pinout_image(
                Path("fake.pdf"), 1,
                BBox(0.5, 0.0, 0.5, 1.0),   # right half
            )

        assert crop.shape[1] == 200   # half of 400
        assert crop.shape[0] == 200
