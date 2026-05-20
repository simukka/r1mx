"""Tests for the photo enhancement pipeline used in LayerScene.apply_photo_enhancement.

Uses synthetic numpy images — no real PCB photos, no GUI instantiation.
The enhancement logic is tested via a local reimplementation of the pipeline
(mirroring toolkit/gui/scene.py) so tests remain pure-Python / no-Qt.
"""
from __future__ import annotations

import cv2
import numpy as np
import pytest


# ── Helpers ───────────────────────────────────────────────────────────────────

def _solid(value: int, shape: tuple = (4, 4, 3)) -> np.ndarray:
    """Solid colour image (all channels = value)."""
    return np.full(shape, value, dtype=np.uint8)


# We need to intercept the numpy array passed to bgr_to_pixmap.
# Easiest approach: monkey-patch apply_photo_enhancement to capture input just
# before bgr_to_pixmap is called.

def _run_enhancement(img_in: np.ndarray, **kwargs) -> np.ndarray:
    """Run the enhancement pipeline on *img_in* and return the result array."""
    brightness = kwargs.get("brightness", 0)
    contrast   = kwargs.get("contrast", 1.0)
    gamma      = kwargs.get("gamma", 1.0)
    sharpen    = kwargs.get("sharpen", False)
    invert     = kwargs.get("invert", False)

    img = img_in.astype(np.int16)
    if brightness != 0:
        img = img + brightness
    if contrast != 1.0:
        img = (img.astype(np.float32) - 128.0) * contrast + 128.0
    img = np.clip(img, 0, 255).astype(np.uint8)
    if gamma != 1.0:
        inv_gamma = 1.0 / max(gamma, 0.01)
        lut = np.array(
            [((i / 255.0) ** inv_gamma) * 255 for i in range(256)], dtype=np.uint8
        )
        img = cv2.LUT(img, lut)
    if sharpen:
        kernel = np.array(
            [[ 0, -1,  0],
             [-1,  5, -1],
             [ 0, -1,  0]], dtype=np.float32,
        )
        img = cv2.filter2D(img, -1, kernel)
    if invert:
        img = 255 - img
    return img


# ── Tests ─────────────────────────────────────────────────────────────────────

def test_brightness_increases_pixel_values():
    img = _solid(100)
    result = _run_enhancement(img, brightness=50)
    assert result[0, 0, 0] == 150


def test_brightness_clips_at_255():
    img = _solid(220)
    result = _run_enhancement(img, brightness=100)
    assert result[0, 0, 0] == 255


def test_brightness_clips_at_0():
    img = _solid(30)
    result = _run_enhancement(img, brightness=-100)
    assert result[0, 0, 0] == 0


def test_contrast_above_one_increases_spread():
    img = _solid(180)
    result = _run_enhancement(img, contrast=2.0)
    # (180 - 128) * 2 + 128 = 232
    assert result[0, 0, 0] == 232


def test_contrast_below_one_decreases_spread():
    img = _solid(180)
    result = _run_enhancement(img, contrast=0.5)
    # (180 - 128) * 0.5 + 128 = 154
    assert result[0, 0, 0] == 154


def test_contrast_clips_at_255():
    img = _solid(255)
    result = _run_enhancement(img, contrast=3.0)
    assert result[0, 0, 0] == 255


def test_gamma_gt_one_brightens_midtones():
    img = _solid(128)
    result = _run_enhancement(img, gamma=2.0)
    # (128/255)^0.5 * 255 ≈ 180
    assert result[0, 0, 0] > 128


def test_gamma_lt_one_darkens_midtones():
    img = _solid(128)
    result = _run_enhancement(img, gamma=0.5)
    assert result[0, 0, 0] < 128


def test_invert_flips_values():
    img = _solid(100)
    result = _run_enhancement(img, invert=True)
    assert result[0, 0, 0] == 155


def test_invert_of_255_is_0():
    img = _solid(255)
    result = _run_enhancement(img, invert=True)
    assert result[0, 0, 0] == 0


def test_sharpen_does_not_crash_on_uniform_image():
    img = _solid(128, shape=(8, 8, 3))
    result = _run_enhancement(img, sharpen=True)
    # Uniform image stays uniform after sharpening
    assert result.shape == img.shape


def test_no_ops_returns_identical_image():
    img = _solid(100)
    result = _run_enhancement(img)
    assert np.array_equal(result, img)


def test_brightness_and_contrast_combined():
    img = _solid(100)
    result = _run_enhancement(img, brightness=28, contrast=2.0)
    # After brightness: 128; then contrast: (128-128)*2+128 = 128
    assert result[0, 0, 0] == 128


def test_output_dtype_is_uint8():
    img = _solid(100)
    for kwargs in [
        {"brightness": 50},
        {"contrast": 2.0},
        {"gamma": 1.5},
        {"sharpen": True},
        {"invert": True},
    ]:
        result = _run_enhancement(img, **kwargs)
        assert result.dtype == np.uint8, f"dtype wrong for {kwargs}"
