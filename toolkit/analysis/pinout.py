"""
pinout.py — Extract component pinout data from a datasheet PDF region.

Workflow
--------
1. ``crop_pinout_image(pdf_path, page, rel_bbox, dpi)``
   Renders the requested page at *dpi* via pdftoppm and crops to *rel_bbox*.

2. ``detect_pads(image)``
   Finds circular/square/rectangular pads using OpenCV adaptive thresholding
   and contour analysis.

3. ``ocr_labels(image)``
   Runs Tesseract (PSM 11 — sparse text) to find word-level text and their
   bounding boxes within *image*.

4. ``assign_labels(pads, ocr_results)``
   For each pad, finds the nearest OCR word within 3× the pad's equivalent
   radius.  Numeric tokens become *pin_number*; others become *label*.

5. ``extract_pinout(pdf_path, page, rel_bbox, dpi)``
   Convenience orchestrator that runs steps 1–4 and returns a ``PinoutResult``.

All coordinates returned by this module are **normalised 0–1** relative to the
crop image dimensions, except ``source_bbox`` which is relative to the full PDF
page.
"""

from __future__ import annotations

import math
import subprocess
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Sequence

import cv2
import numpy as np


# ─── Data structures ─────────────────────────────────────────────────────────

@dataclass
class BBox:
    """Axis-aligned bounding box with normalised 0–1 coordinates."""
    x: float   # left edge
    y: float   # top edge
    w: float   # width
    h: float   # height

    @property
    def cx(self) -> float:
        return self.x + self.w / 2

    @property
    def cy(self) -> float:
        return self.y + self.h / 2

    @property
    def area(self) -> float:
        return self.w * self.h

    def iou(self, other: "BBox") -> float:
        """Intersection-over-union with another BBox."""
        ix1 = max(self.x, other.x)
        iy1 = max(self.y, other.y)
        ix2 = min(self.x + self.w, other.x + other.w)
        iy2 = min(self.y + self.h, other.y + other.h)
        inter = max(0.0, ix2 - ix1) * max(0.0, iy2 - iy1)
        union = self.area + other.area - inter
        return inter / union if union > 0 else 0.0

    def to_dict(self) -> dict:
        return {"x": self.x, "y": self.y, "w": self.w, "h": self.h}

    @classmethod
    def from_dict(cls, d: dict) -> "BBox":
        return cls(d["x"], d["y"], d["w"], d["h"])


@dataclass
class PadDetection:
    """One detected pad within the crop image."""
    bbox: BBox                # normalised 0–1 within crop
    shape: str = "circle"     # "circle" | "square" | "rect"
    pin_number: str = ""
    label: str = ""

    @property
    def cx(self) -> float:
        return self.bbox.cx

    @property
    def cy(self) -> float:
        return self.bbox.cy


@dataclass
class OcrWord:
    """One word returned by Tesseract with its bounding box."""
    text: str
    bbox: BBox   # normalised 0–1 within image


@dataclass
class PinoutResult:
    """Result of a full pinout extraction run."""
    pads:          list[PadDetection]
    image_width:   int
    image_height:  int
    source_page:   int
    source_bbox:   BBox   # relative to the full PDF page

    def to_db_pins(self) -> list[dict]:
        """Convert pads to a format suitable for ``DB.save_component_pinout()``."""
        return [
            {
                "pin_number": p.pin_number,
                "label":      p.label,
                "x_rel":      p.cx,
                "y_rel":      p.cy,
                "shape":      p.shape,
                "shape_json": p.bbox.to_dict(),
            }
            for p in self.pads
        ]


# ─── Step 1: Crop ────────────────────────────────────────────────────────────

def crop_pinout_image(
    pdf_path: Path,
    page: int,
    rel_bbox: BBox,
    dpi: int = 200,
) -> np.ndarray:
    """Render *page* of *pdf_path* at *dpi* and crop to *rel_bbox*.

    *rel_bbox* coordinates are 0–1 relative to the full rendered page size.

    Returns a BGR ``numpy.ndarray``.  Raises ``RuntimeError`` on failure.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        out_base = Path(tmpdir) / "page"
        try:
            result = subprocess.run(
                [
                    "pdftoppm",
                    "-r", str(dpi),
                    "-png",
                    "-singlefile",
                    "-f", str(page),
                    "-l", str(page),
                    str(pdf_path),
                    str(out_base),
                ],
                capture_output=True,
                timeout=30,
            )
        except FileNotFoundError as exc:
            raise RuntimeError("pdftoppm not found — install poppler-utils") from exc
        except subprocess.TimeoutExpired as exc:
            raise RuntimeError(f"pdftoppm timed out rendering page {page}") from exc

        png_path = Path(tmpdir) / "page.png"
        if not png_path.exists():
            raise RuntimeError(
                f"pdftoppm produced no output for page {page} of {pdf_path}"
            )

        full_img = cv2.imread(str(png_path))
        if full_img is None:
            raise RuntimeError(f"Failed to read rendered page image: {png_path}")

    h, w = full_img.shape[:2]
    x1 = max(0, int(rel_bbox.x * w))
    y1 = max(0, int(rel_bbox.y * h))
    x2 = min(w, int((rel_bbox.x + rel_bbox.w) * w))
    y2 = min(h, int((rel_bbox.y + rel_bbox.h) * h))
    cropped = full_img[y1:y2, x1:x2]
    if cropped.size == 0:
        raise RuntimeError(
            f"Crop region {rel_bbox} produced an empty image on {w}×{h} page"
        )
    return cropped


# ─── Step 2: Detect pads ─────────────────────────────────────────────────────

_MIN_PAD_AREA_PX  = 20      # pixels²  — smaller blobs are noise
_MAX_PAD_FRACTION = 0.10    # fraction of image area — larger are board outlines
_IOU_DEDUP        = 0.50    # IoU threshold for duplicate suppression
_CIRC_THRESHOLD   = 0.72    # circularity ≥ this → "circle"
_SQUARE_ASPECT    = 0.20    # |aspect_ratio - 1| ≤ this → "square"


def _classify_shape(contour) -> str:
    """Classify a contour as 'circle', 'square', or 'rect'."""
    perimeter = cv2.arcLength(contour, True)
    if perimeter < 1e-6:
        return "rect"
    area = cv2.contourArea(contour)
    circularity = 4 * math.pi * area / (perimeter ** 2)
    if circularity >= _CIRC_THRESHOLD:
        return "circle"
    _, (bw, bh), _ = cv2.minAreaRect(contour)
    if bh < 1e-6:
        return "rect"
    aspect = min(bw, bh) / max(bw, bh)
    if abs(aspect - 1.0) <= _SQUARE_ASPECT:
        return "square"
    return "rect"


def detect_pads(image: np.ndarray) -> list[PadDetection]:
    """Detect pad-like shapes in *image* using adaptive thresholding + contours.

    Returns a list of ``PadDetection`` objects with normalised coordinates.
    """
    h, w = image.shape[:2]
    total_area = h * w
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Adaptive threshold works better than global for varied lighting
    block = max(11, (min(h, w) // 20) | 1)  # odd, at least 11
    thresh = cv2.adaptiveThreshold(
        gray, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV,
        block, 3,
    )

    # Clean up with morphological open (removes tiny noise dots)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    cleaned = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=1)

    contours, _ = cv2.findContours(cleaned, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    pads: list[PadDetection] = []
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area < _MIN_PAD_AREA_PX:
            continue
        if area > total_area * _MAX_PAD_FRACTION:
            continue

        bx, by, bw, bh = cv2.boundingRect(cnt)
        bbox = BBox(bx / w, by / h, bw / w, bh / h)
        shape = _classify_shape(cnt)
        pads.append(PadDetection(bbox=bbox, shape=shape))

    # Deduplicate overlapping detections (keep the one with larger area)
    pads.sort(key=lambda p: p.bbox.area, reverse=True)
    kept: list[PadDetection] = []
    for pad in pads:
        if not any(pad.bbox.iou(k.bbox) >= _IOU_DEDUP for k in kept):
            kept.append(pad)

    return kept


# ─── Step 3: OCR ─────────────────────────────────────────────────────────────

def ocr_labels(image: np.ndarray) -> list[OcrWord]:
    """Extract word-level text from *image* using Tesseract PSM 11.

    Returns a list of ``OcrWord`` with normalised coordinates.
    """
    try:
        import pytesseract  # type: ignore
    except ImportError:
        return []

    h, w = image.shape[:2]
    # Upscale small images so Tesseract has more pixels to work with
    scale = max(1.0, 300 / max(h, w, 1))
    if scale > 1.0:
        interp = cv2.INTER_CUBIC
        image = cv2.resize(image, None, fx=scale, fy=scale, interpolation=interp)
        h, w = image.shape[:2]

    # PSM 11: sparse text — works well for component datasheets
    data = pytesseract.image_to_data(
        image,
        config="--psm 11 --oem 3",
        output_type=pytesseract.Output.DICT,
    )

    words: list[OcrWord] = []
    for i, text in enumerate(data["text"]):
        text = text.strip()
        if not text:
            continue
        conf = int(data["conf"][i])
        if conf < 20:
            continue
        bx = data["left"][i]
        by = data["top"][i]
        bw_ = data["width"][i]
        bh_ = data["height"][i]
        if bw_ < 1 or bh_ < 1:
            continue
        bbox = BBox(bx / w, by / h, bw_ / w, bh_ / h)
        words.append(OcrWord(text=text, bbox=bbox))

    return words


# ─── Step 4: Assign labels ───────────────────────────────────────────────────

_LABEL_SEARCH_RADIUS = 3.0   # × pad equivalent radius


def assign_labels(
    pads: list[PadDetection],
    ocr_words: list[OcrWord],
    *,
    image_aspect: float = 1.0,  # w/h of the source image (for distance scaling)
) -> list[PadDetection]:
    """Associate OCR words with nearby pads.

    Numeric tokens → ``pin_number``.  Alphanumeric non-numeric tokens → ``label``.
    Each word can only be assigned to the nearest unmatched pad.

    Returns *pads* with ``pin_number`` and ``label`` fields populated in-place
    (a new list is returned for safety).
    """
    import copy
    pads = [copy.copy(p) for p in pads]
    used_words: set[int] = set()

    for pad in pads:
        # Equivalent radius in normalised coords
        r = math.sqrt(pad.bbox.area) / 2 * _LABEL_SEARCH_RADIUS

        candidates: list[tuple[float, int, OcrWord]] = []
        for idx, word in enumerate(ocr_words):
            if idx in used_words:
                continue
            # Distance from pad centre to word centre
            dx = pad.cx - word.bbox.cx
            dy = (pad.cy - word.bbox.cy) * image_aspect
            dist = math.hypot(dx, dy)
            if dist <= r:
                candidates.append((dist, idx, word))

        # Sort by distance; assign pin_number first (numeric), then label
        candidates.sort(key=lambda t: t[0])
        for _, idx, word in candidates:
            text = word.text
            if text.lstrip("-").isdigit() and not pad.pin_number:
                pad.pin_number = text
                used_words.add(idx)
            elif not pad.label:
                pad.label = text
                used_words.add(idx)
            if pad.pin_number and pad.label:
                break

    return pads


# ─── Step 5: Orchestrator ────────────────────────────────────────────────────

def extract_pinout(
    pdf_path: Path,
    page: int,
    rel_bbox: BBox,
    dpi: int = 200,
) -> PinoutResult:
    """Run the full pinout extraction pipeline.

    1. Render and crop the PDF page.
    2. Detect pad shapes.
    3. OCR text.
    4. Assign labels.
    5. Return a ``PinoutResult``.
    """
    image = crop_pinout_image(pdf_path, page, rel_bbox, dpi=dpi)
    h, w = image.shape[:2]
    pads       = detect_pads(image)
    words      = ocr_labels(image)
    aspect     = w / h if h > 0 else 1.0
    pads       = assign_labels(pads, words, image_aspect=aspect)
    return PinoutResult(
        pads=pads,
        image_width=w,
        image_height=h,
        source_page=page,
        source_bbox=rel_bbox,
    )
