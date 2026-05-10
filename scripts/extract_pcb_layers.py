#!/usr/bin/env python3
"""
extract_pcb_layers.py — PCB copper layer feature extractor for the r1mx project.

Analyses high-resolution top/bottom PCB photographs to detect:
  - Vias (through-holes)
  - Copper traces (via potrace vectorisation of the copper mask)
  - SMD / THT pads
  - Board outline

Outputs an intermediate `layout.json` per board consumed by
`generate_kicad_pcb.py` to produce a .kicad_pcb file.

Reads calibration.json written by calibrate_board.py.  The calibration
file contains a per-layer perspective-correction homography; this script
applies the warp automatically before feature extraction so the analysis
always operates on a geometry-corrected image.

Usage:
    # Requires calibration.json first (see calibrate_board.py):
    python scripts/extract_pcb_layers.py --board cpu_io_board
    python scripts/extract_pcb_layers.py --board cpu_io_board --layer bottom
    python scripts/extract_pcb_layers.py --board cpu_io_board --debug
    python scripts/extract_pcb_layers.py --board cpu_io_board --tune-hsv
    python scripts/extract_pcb_layers.py --board cpu_io_board --tune-hsv --layer bottom

    # Interactive review — pause after each step for human verification:
    python scripts/extract_pcb_layers.py --board cpu_io_board --review
    python scripts/extract_pcb_layers.py --board cpu_io_board --review --layer bottom
"""

import argparse
import json
import logging
import math
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

import cv2
import numpy as np

# PyQt6 — only used by LayerReviewer (interactive --review mode) and
# _interactive_hsv_tune (--tune-hsv mode).  Imported lazily inside those
# classes so the rest of the script runs fine without a display.
sys.path.insert(0, str(Path(__file__).resolve().parent))  # for r1mx_gui

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)

REPO_ROOT = Path(__file__).resolve().parent.parent
COMPONENTS_DIR = REPO_ROOT / "components"

# ---------------------------------------------------------------------------
# Default HSV ranges for PCB feature segmentation
# These work for standard green FR4 with HASL or ENIG finish.
# Override per board in calibration.json under "hsv_overrides".
# ---------------------------------------------------------------------------

DEFAULT_HSV = {
    # Copper / HASL pads & traces: warm golden/orange
    "copper_lower": [10, 40, 120],
    "copper_upper": [35, 255, 255],
    # Silkscreen (white): low saturation, high value
    "silk_lower_white": [0, 0, 180],
    "silk_upper_white": [180, 60, 255],
    # Via holes: very dark (the drill hole itself)
    "hole_lower": [0, 0, 0],
    "hole_upper": [180, 255, 55],
}

# Estimated via drill sizes in mm (used to set HoughCircles radius range)
VIA_DRILL_MIN_MM = 0.15
VIA_DRILL_MAX_MM = 1.2

# Pad size thresholds
PAD_AREA_MIN_MM2 = 0.04   # 0.2 × 0.2 mm minimum
PAD_AREA_MAX_MM2 = 25.0   # 5 × 5 mm maximum
PAD_ASPECT_MAX = 8.0       # reject very elongated regions (those are traces)


# ---------------------------------------------------------------------------
# Calibration I/O
# ---------------------------------------------------------------------------

def load_calibration(board_dir: Path) -> dict:
    cal_path = board_dir / "calibration.json"
    if not cal_path.exists():
        log.warning(
            "No calibration.json found for %s. "
            "Run calibrate_board.py first, or use --px-per-mm to set scale manually.",
            board_dir.name,
        )
        return {}
    with cal_path.open() as f:
        return json.load(f)


def get_layer_cal(cal: dict, layer: str) -> dict:
    """Return the calibration sub-dict for *layer* (e.g. 'top' or 'bottom').

    Falls back gracefully to flat old-schema keys so existing calibration.json
    files continue to work until they are re-calibrated.
    """
    layers = cal.get("layers", {})
    if layer in layers:
        return layers[layer]
    # Old flat schema compatibility
    if "px_per_mm" in cal:
        log.debug("Falling back to flat calibration schema for layer '%s'", layer)
        return {
            "source_image": cal.get("source_image", ""),
            "corners_px": [],
            "warp_matrix": [],
            "warped_size": [],
            "px_per_mm": cal.get("px_per_mm", 0.0),
            "ref_points_warped_px": cal.get("ref_points_px", []),
            "ref_distance_mm": cal.get("ref_distance_mm", 2.54),
        }
    return {}


def px_to_mm(px: float, px_per_mm: float) -> float:
    return px / px_per_mm


def coord_px_to_mm(x: float, y: float, px_per_mm: float) -> tuple[float, float]:
    return round(x / px_per_mm, 4), round(y / px_per_mm, 4)


# ---------------------------------------------------------------------------
# Image loading & preprocessing
# ---------------------------------------------------------------------------

def load_and_crop(image_path: Path) -> np.ndarray:
    """Load a PCB image; apply basic CLAHE contrast enhancement."""
    bgr = cv2.imread(str(image_path))
    if bgr is None:
        raise FileNotFoundError(f"Cannot load {image_path}")

    # Light CLAHE to even out lighting without changing hue
    lab = cv2.cvtColor(bgr, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    lab = cv2.merge([clahe.apply(l), a, b])
    return cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)


def apply_perspective_warp(bgr: np.ndarray, layer_cal: dict) -> np.ndarray:
    """Apply the perspective-correction homography stored in *layer_cal*.

    If *layer_cal* contains no warp_matrix (e.g. calibrated with --headless
    without --corners, or old flat schema), the image is returned unchanged.
    """
    warp_M = layer_cal.get("warp_matrix")
    warp_size = layer_cal.get("warped_size")
    if not warp_M or not warp_size:
        return bgr
    M = np.array(warp_M, dtype=np.float64)
    return cv2.warpPerspective(bgr, M, tuple(warp_size))


def detect_board_outline(bgr: np.ndarray) -> np.ndarray | None:
    """
    Return the largest quadrilateral contour found — the PCB edge.
    Returns None if no suitable outline is found.
    """
    gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (7, 7), 0)
    edges = cv2.Canny(blurred, 30, 100)
    edges = cv2.dilate(edges, np.ones((3, 3), np.uint8), iterations=2)

    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return None

    # Largest contour by area
    largest = max(contours, key=cv2.contourArea)
    area = cv2.contourArea(largest)
    img_area = bgr.shape[0] * bgr.shape[1]

    if area < 0.1 * img_area:
        return None  # Too small — probably not the board outline

    peri = cv2.arcLength(largest, True)
    approx = cv2.approxPolyDP(largest, 0.02 * peri, True)
    return approx


# ---------------------------------------------------------------------------
# Copper layer segmentation
# ---------------------------------------------------------------------------

def extract_copper_mask(bgr: np.ndarray, hsv_cfg: dict) -> np.ndarray:
    """
    Return a binary mask of copper regions using HSV colour thresholding.
    Morphological operations clean up noise.
    """
    hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)

    lo = np.array(hsv_cfg.get("copper_lower", DEFAULT_HSV["copper_lower"]), np.uint8)
    hi = np.array(hsv_cfg.get("copper_upper", DEFAULT_HSV["copper_upper"]), np.uint8)
    mask = cv2.inRange(hsv, lo, hi)

    # Clean up
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=1)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=2)
    return mask


# ---------------------------------------------------------------------------
# Via detection
# ---------------------------------------------------------------------------

def detect_vias(
    bgr: np.ndarray,
    copper_mask: np.ndarray,
    px_per_mm: float,
    hsv_cfg: dict,
) -> list[dict[str, Any]]:
    """
    Detect via drill holes using HoughCircles on the dark-hole mask.
    Returns list of {x_mm, y_mm, drill_mm, annular_mm}.
    """
    # Via holes appear as very dark spots (the drill)
    gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
    # Blur lightly to merge nearby noise
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    min_r = max(2, int(VIA_DRILL_MIN_MM * px_per_mm / 2))
    max_r = int(VIA_DRILL_MAX_MM * px_per_mm / 2)
    min_dist = max_r * 2

    circles = cv2.HoughCircles(
        blurred,
        cv2.HOUGH_GRADIENT,
        dp=1,
        minDist=min_dist,
        param1=60,
        param2=20,
        minRadius=min_r,
        maxRadius=max_r,
    )

    vias = []
    if circles is None:
        return vias

    circles = np.round(circles[0]).astype(int)
    h, w = bgr.shape[:2]

    for cx, cy, r in circles:
        # Confirm the surrounding ring has copper
        ring_mask = np.zeros((h, w), np.uint8)
        cv2.circle(ring_mask, (cx, cy), r + max(2, int(0.15 * px_per_mm)), 255, -1)
        cv2.circle(ring_mask, (cx, cy), r, 0, -1)
        ring_copper = cv2.bitwise_and(copper_mask, ring_mask)
        if cv2.countNonZero(ring_copper) < 0.3 * cv2.countNonZero(ring_mask):
            continue  # No annular ring — skip

        drill_mm = round(2 * r / px_per_mm, 3)
        x_mm, y_mm = coord_px_to_mm(cx, cy, px_per_mm)
        vias.append({
            "x_mm": x_mm,
            "y_mm": y_mm,
            "drill_mm": drill_mm,
            "annular_mm": round(0.15, 3),  # conservative default
        })

    log.info("  Detected %d vias", len(vias))
    return vias


# ---------------------------------------------------------------------------
# Pad detection
# ---------------------------------------------------------------------------

def detect_pads(
    copper_mask: np.ndarray,
    px_per_mm: float,
    via_positions: list[dict],
    layer: str = "F_Cu",
) -> list[dict[str, Any]]:
    """
    Detect SMD/THT pads as compact copper blobs.
    Returns list of {x_mm, y_mm, w_mm, h_mm, rotation_deg, layer}.
    """
    # Label connected components
    n_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(
        copper_mask, connectivity=8
    )

    px2 = px_per_mm ** 2
    pads = []

    # Pre-compute via positions as pixel coords for filtering
    via_px = [(v["x_mm"] * px_per_mm, v["y_mm"] * px_per_mm) for v in via_positions]

    for i in range(1, n_labels):  # skip background label 0
        area_px = stats[i, cv2.CC_STAT_AREA]
        area_mm2 = area_px / px2

        if area_mm2 < PAD_AREA_MIN_MM2 or area_mm2 > PAD_AREA_MAX_MM2:
            continue

        bx = stats[i, cv2.CC_STAT_LEFT]
        by = stats[i, cv2.CC_STAT_TOP]
        bw = stats[i, cv2.CC_STAT_WIDTH]
        bh = stats[i, cv2.CC_STAT_HEIGHT]

        aspect = max(bw, bh) / max(1, min(bw, bh))
        if aspect > PAD_ASPECT_MAX:
            continue  # Elongated → trace, not pad

        cx, cy = centroids[i]

        # Skip if this is a via annular ring
        is_via = any(
            math.hypot(cx - vx, cy - vy) < 3 * px_per_mm
            for vx, vy in via_px
        )
        if is_via:
            continue

        # Fit a rotated bounding rectangle for rotation angle
        component_mask = (labels == i).astype(np.uint8) * 255
        contours, _ = cv2.findContours(component_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if not contours:
            continue
        rect = cv2.minAreaRect(contours[0])
        _, (rw, rh), angle = rect

        w_mm = round(max(rw, rh) / px_per_mm, 3)
        h_mm = round(min(rw, rh) / px_per_mm, 3)
        x_mm, y_mm = coord_px_to_mm(cx, cy, px_per_mm)

        pads.append({
            "x_mm": x_mm,
            "y_mm": y_mm,
            "w_mm": w_mm,
            "h_mm": h_mm,
            "rotation_deg": round(angle, 1),
            "layer": layer,
            "ref": "",  # filled in by component assignment
        })

    log.info("  Detected %d pads", len(pads))
    return pads


# ---------------------------------------------------------------------------
# Trace vectorisation via potrace
# ---------------------------------------------------------------------------

def vectorise_traces(
    copper_mask: np.ndarray,
    pad_mask: np.ndarray,
    px_per_mm: float,
    layer: str = "F_Cu",
) -> list[dict[str, Any]]:
    """
    Use potrace to convert the copper trace mask (pads/vias removed) to SVG,
    then parse the SVG paths into line segments for KiCad tracks.

    Returns list of {start: [x_mm, y_mm], end: [x_mm, y_mm], width_mm, layer}.
    """
    # Remove pads from copper mask so we get trace skeleton only
    trace_mask = cv2.bitwise_and(copper_mask, cv2.bitwise_not(pad_mask))

    # Light morphological thinning to remove blobs (keep only elongated traces)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    trace_mask = cv2.morphologyEx(trace_mask, cv2.MORPH_OPEN, kernel, iterations=1)

    # Estimate trace width (median half-width from distance transform)
    dist = cv2.distanceTransform(trace_mask, cv2.DIST_L2, 5)
    nonzero_dist = dist[dist > 0]
    if len(nonzero_dist) == 0:
        log.info("  No trace pixels found after masking")
        return []
    median_half_width = float(np.median(nonzero_dist))
    trace_width_mm = round(2 * median_half_width / px_per_mm, 3)
    log.info("  Estimated trace width: %.3f mm", trace_width_mm)

    # Write mask as PBM for potrace
    with tempfile.TemporaryDirectory() as tmpdir:
        pbm_path = Path(tmpdir) / "traces.pbm"
        svg_path = Path(tmpdir) / "traces.svg"

        # PBM: 0 = white (background), 255 = black (foreground for potrace)
        potrace_input = cv2.bitwise_not(trace_mask)
        cv2.imwrite(str(pbm_path), potrace_input)

        result = subprocess.run(
            ["potrace", "--svg", "--flat", "-o", str(svg_path), str(pbm_path)],
            capture_output=True, text=True,
        )
        if result.returncode != 0:
            log.warning("potrace failed: %s", result.stderr[:200])
            return []

        if not svg_path.exists():
            return []

        tracks = _parse_svg_to_tracks(svg_path, px_per_mm, trace_width_mm, layer)

    log.info("  Extracted %d track segments from potrace SVG", len(tracks))
    return tracks


def _parse_svg_to_tracks(
    svg_path: Path,
    px_per_mm: float,
    width_mm: float,
    layer: str,
) -> list[dict[str, Any]]:
    """
    Parse potrace SVG output into straight-line track segments.
    Bezier curves are approximated as polylines at 0.1mm resolution.
    """
    try:
        from svgpathtools import svg2paths
    except ImportError:
        log.warning("svgpathtools not installed — cannot parse SVG tracks")
        return []

    paths, _ = svg2paths(str(svg_path))
    tracks = []
    step_mm = 0.1  # approximate curves at this resolution

    for path in paths:
        for segment in path:
            seg_type = type(segment).__name__

            if seg_type == "Line":
                sx, sy = segment.start.real / px_per_mm, segment.start.imag / px_per_mm
                ex, ey = segment.end.real / px_per_mm, segment.end.imag / px_per_mm
                tracks.append({
                    "start": [round(sx, 4), round(sy, 4)],
                    "end":   [round(ex, 4), round(ey, 4)],
                    "width_mm": width_mm,
                    "layer": layer,
                })
            else:
                # Bezier or Arc — sample into polyline
                length = segment.length()
                n_steps = max(2, int(length / (step_mm * px_per_mm)))
                pts = [segment.point(t / n_steps) for t in range(n_steps + 1)]
                for i in range(len(pts) - 1):
                    sx, sy = pts[i].real / px_per_mm, pts[i].imag / px_per_mm
                    ex, ey = pts[i + 1].real / px_per_mm, pts[i + 1].imag / px_per_mm
                    tracks.append({
                        "start": [round(sx, 4), round(sy, 4)],
                        "end":   [round(ex, 4), round(ey, 4)],
                        "width_mm": width_mm,
                        "layer": layer,
                    })

    return tracks


# ---------------------------------------------------------------------------
# Component placement (assign refs to pads from BOM position data)
# ---------------------------------------------------------------------------

def assign_refs_to_pads(
    pads: list[dict],
    bom_path: Path,
    px_per_mm: float,
) -> list[dict]:
    """
    Load bom.csv (which now includes x_px, y_px) and assign ref designators
    to the nearest pad cluster within a search radius.
    Returns pads with 'ref' field populated.
    """
    import csv

    if not bom_path.exists():
        log.warning("  No bom.csv found — skipping component assignment")
        return pads

    ref_positions = []  # (ref, x_mm, y_mm)
    with bom_path.open() as f:
        for row in csv.DictReader(f):
            try:
                x_px = int(row["x_px"])
                y_px = int(row["y_px"])
                if x_px < 0 or y_px < 0:
                    continue
                x_mm = x_px / px_per_mm
                y_mm = y_px / px_per_mm
                ref_positions.append((row["reference"], x_mm, y_mm))
            except (KeyError, ValueError):
                continue

    if not ref_positions:
        log.info("  No position data in bom.csv (re-run extract_bom.py to populate x_px/y_px)")
        return pads

    # For each ref, find nearest pad (within 3mm search radius)
    search_radius_mm = 3.0
    for pad in pads:
        best_ref = ""
        best_dist = search_radius_mm
        for ref, rx, ry in ref_positions:
            d = math.hypot(pad["x_mm"] - rx, pad["y_mm"] - ry)
            if d < best_dist:
                best_dist = d
                best_ref = ref
        pad["ref"] = best_ref

    assigned = sum(1 for p in pads if p["ref"])
    log.info("  Assigned refs to %d/%d pads", assigned, len(pads))
    return pads


# ---------------------------------------------------------------------------
# Main processing pipeline
# ---------------------------------------------------------------------------

def process_board(
    board_dir: Path,
    px_per_mm: float,
    debug: bool,
    hsv_overrides: dict,
    cal: dict | None = None,
    review: bool = False,
    layer_filter: str | None = None,
    progress_cb=None,
) -> dict:
    """Extract PCB features from board images.

    Parameters
    ----------
    layer_filter : if set (e.g. "top" or "bottom"), only that layer is
                   processed.  Corresponds to the cal_key / DB layer name.
    progress_cb  : optional callable(message: str) for progress reporting.
    """
    board_name = board_dir.name
    log.info("Processing board: %s (%.1f px/mm)", board_name, px_per_mm)

    debug_dir = board_dir / "_layer_debug" if debug else None
    if debug_dir:
        debug_dir.mkdir(exist_ok=True)

    hsv_cfg = {**DEFAULT_HSV, **hsv_overrides}
    layout: dict[str, Any] = {
        "board": board_name,
        "px_per_mm": px_per_mm,
        "vias": [],
        "pads_front": [],
        "pads_back": [],
        "tracks_front": [],
        "tracks_back": [],
        "board_outline": [],
    }

    cal = cal or {}

    # Build the layer table, using source_image from calibration when available
    def _layer_image(cal_key: str, fallback: str) -> str:
        lc = get_layer_cal(cal, cal_key)
        return lc.get("source_image") or fallback

    all_layers = [
        ("front", "top",    "top.JPG",    False, "F_Cu"),
        ("back",  "bottom", "bottom.JPG", True,  "B_Cu"),
    ]
    # Honour layer_filter: "top" → front, "bottom" → back, or any cal_key match
    if layer_filter:
        all_layers = [(ln, ck, fi, fl, kl)
                      for ln, ck, fi, fl, kl in all_layers
                      if ck == layer_filter]

    for layer_name, cal_key, fallback_img, flip, kicad_layer in all_layers:
        def _prog(msg: str):
            log.info("  %s", msg)
            if progress_cb:
                progress_cb(msg)

        image_name = _layer_image(cal_key, fallback_img)
        img_path = board_dir / image_name
        if not img_path.exists():
            # Try alternative naming conventions
            for alt in ["board-top.png", "board-bottom.png"]:
                alt_path = board_dir / alt
                if alt_path.exists():
                    img_path = alt_path
                    break
            else:
                log.warning("  No %s image found for %s", image_name, board_name)
                _prog(f"No image found for {layer_name} layer — skipping")
                continue

        _prog(f"Loading {layer_name} layer ({img_path.name}) …")
        bgr = load_and_crop(img_path)
        bgr = apply_perspective_warp(bgr, get_layer_cal(cal, cal_key))

        if flip:
            bgr = cv2.flip(bgr, 1)  # horizontal flip for bottom layer alignment

        reviewer = LayerReviewer(bgr, layer_name, px_per_mm, board_dir) if review else None

        # Copper mask — reviewed first; drives all subsequent steps
        _prog("Extracting copper mask …")
        copper_mask = extract_copper_mask(bgr, hsv_cfg)
        if reviewer:
            copper_mask, hsv_cfg = reviewer.review_copper_mask(copper_mask, hsv_cfg)
        if debug_dir:
            cv2.imwrite(str(debug_dir / f"{layer_name}_copper_mask.png"), copper_mask)

        # Board outline (front layer only)
        if layer_name == "front":
            _prog("Detecting board outline …")
            outline = detect_board_outline(bgr)
            if reviewer:
                outline = reviewer.review_outline(outline)
            if outline is not None:
                pts = [[round(float(p[0][0]) / px_per_mm, 3),
                        round(float(p[0][1]) / px_per_mm, 3)]
                       for p in outline]
                layout["board_outline"] = pts
                _prog(f"Board outline: {len(pts)} points")

        _prog("Detecting vias …")
        vias = detect_vias(bgr, copper_mask, px_per_mm, hsv_cfg)
        if reviewer:
            vias = reviewer.review_vias(vias)
        if layer_name == "front":
            layout["vias"] = vias
        _prog(f"  → {len(vias)} vias")

        # Build pad exclusion mask (always from full detected set for trace quality)
        _prog("Detecting pads …")
        pads_raw = detect_pads(copper_mask, px_per_mm, vias, layer=kicad_layer)
        pad_mask = np.zeros(copper_mask.shape, np.uint8)
        for pad in pads_raw:
            cx = int(pad["x_mm"] * px_per_mm)
            cy = int(pad["y_mm"] * px_per_mm)
            rw = int(pad["w_mm"] * px_per_mm / 2 + 2)
            rh = int(pad["h_mm"] * px_per_mm / 2 + 2)
            cv2.ellipse(pad_mask, (cx, cy), (rw, rh), pad["rotation_deg"], 0, 360, 255, -1)
        for via in vias:
            cx = int(via["x_mm"] * px_per_mm)
            cy = int(via["y_mm"] * px_per_mm)
            r  = int((via["drill_mm"] / 2 + via["annular_mm"]) * px_per_mm + 2)
            cv2.circle(pad_mask, (cx, cy), r, 255, -1)

        # Assign refs then offer pad review
        bom_path = board_dir / "bom.csv"
        pads = assign_refs_to_pads(pads_raw, bom_path, px_per_mm)
        if reviewer:
            pads = reviewer.review_pads(pads)
        _prog(f"  → {len(pads)} pads")

        _prog("Vectorising traces (this may take a while) …")
        tracks = vectorise_traces(copper_mask, pad_mask, px_per_mm, layer=kicad_layer)
        if reviewer:
            tracks = reviewer.review_tracks(tracks)
        _prog(f"  → {len(tracks)} trace segments")

        if reviewer:
            reviewer.close()

        if layer_name == "front":
            layout["pads_front"] = pads
            layout["tracks_front"] = tracks
        else:
            layout["pads_back"] = pads
            layout["tracks_back"] = tracks

        log.info(
            "  %s: %d vias, %d pads, %d tracks",
            layer_name, len(vias), len(pads), len(tracks),
        )

    return layout


def save_layout(layout: dict, board_dir: Path) -> Path:
    out = board_dir / "layout.json"
    with out.open("w") as f:
        json.dump(layout, f, indent=2)
    log.info("Wrote %s", out)
    return out


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Extract PCB copper layer features from photographs."
    )
    parser.add_argument("--board", metavar="NAME", required=True,
                        help="Board folder name under components/")
    parser.add_argument("--layer", metavar="LABEL", default="top",
                        help="Layer to process: top, bottom, or custom label "
                             "(default: top; used to look up calibration data)")
    parser.add_argument("--px-per-mm", type=float, default=0.0, metavar="FLOAT",
                        help="Pixels per mm (overrides calibration.json)")
    parser.add_argument("--debug", action="store_true",
                        help="Save intermediate mask images to <board>/_layer_debug/")
    parser.add_argument("--tune-hsv", action="store_true",
                        help="Launch interactive HSV tuning window (requires display)")
    parser.add_argument("--review", action="store_true",
                        help="Pause after each extraction step to review results in the GUI; "
                             "press [Y/Enter] to accept, [S] to skip, [T] to tune HSV (copper mask only)")
    args = parser.parse_args()

    board_dir = COMPONENTS_DIR / args.board
    if not board_dir.is_dir():
        log.error("Board not found: %s", board_dir)
        sys.exit(1)

    cal = load_calibration(board_dir)
    hsv_overrides = cal.get("hsv_overrides", {})

    # Resolve px_per_mm: CLI flag → calibration layer → error
    px_per_mm = args.px_per_mm
    if px_per_mm <= 0:
        layer_cal = get_layer_cal(cal, args.layer)
        px_per_mm = layer_cal.get("px_per_mm", 0.0)
    if px_per_mm <= 0:
        log.error(
            "px_per_mm not set. Run calibrate_board.py first, or pass --px-per-mm VALUE.\n"
            "Tip: measure the pitch between two header pins (2.54 mm) in pixels in any\n"
            "image editor and divide: px_per_mm = measured_px / 2.54"
        )
        sys.exit(1)

    if args.tune_hsv:
        _interactive_hsv_tune(board_dir, hsv_overrides, cal, args.layer)
        return

    layout = process_board(board_dir, px_per_mm, args.debug, hsv_overrides, cal,
                           review=args.review)
    save_layout(layout, board_dir)


# ---------------------------------------------------------------------------
# Interactive layer extraction review
# ---------------------------------------------------------------------------

class LayerReviewer:
    """
    Shows each extraction result overlaid on the corrected PCB photo and lets
    the user accept, skip, or refine the result interactively.

    Uses PyQt6 + ImageViewer for display (HiDPI-correct coordinates).

    Review steps:
      review_copper_mask   — green tint overlay; Tune button opens HSV sliders
      review_outline       — cyan polygon; Tune button enters click-to-draw mode
      review_vias          — green circles (drill + annular ring)
      review_pads          — orange rotated rectangles with ref labels
      review_tracks        — blue line segments

    Buttons in every step:
      [Accept]  — use the result as-is
      [Skip]    — discard the result for this step
      [Tune]    — only shown where a manual correction is available
    """

    def __init__(
        self,
        bgr: np.ndarray,
        layer_name: str,
        px_per_mm: float,
        board_dir: Path,
    ) -> None:
        from PyQt6.QtWidgets import QApplication
        self._app = QApplication.instance() or QApplication(sys.argv)

        self.bgr        = bgr
        self.layer_name = layer_name.upper()
        self.px_per_mm  = px_per_mm
        self.board_dir  = board_dir
        self._win       = _ReviewWindow(bgr, layer_name.upper())

    def close(self) -> None:
        self._win.hide()

    # ------------------------------------------------------------------
    # Per-step review methods
    # ------------------------------------------------------------------

    def review_copper_mask(
        self, mask: np.ndarray, hsv_cfg: dict
    ) -> tuple[np.ndarray, dict]:
        """
        Show copper mask as a green overlay.
        'Tune HSV' button opens an HSV slider dialog.
        Returns (mask, hsv_cfg) — mask is zeroed if the user skips.
        """
        print(
            "\n── Copper Mask ─────────────────────────────────────────────────────\n"
            "  The green tint highlights every pixel the algorithm thinks is\n"
            "  exposed copper (pads, traces, via annular rings).\n"
            "\n"
            "  What to look for:\n"
            "    ✓ All copper-coloured areas on the board are tinted green\n"
            "    ✓ The green does NOT spill onto the solder-mask (dark green PCB)\n"
            "    ✓ Silkscreen, substrate, and holes are NOT tinted\n"
            "\n"
            "  'Tune HSV' opens sliders to adjust thresholds for this board.\n"
            "  Thresholds are saved to calibration.json for future runs.\n"
            "────────────────────────────────────────────────────────────────────"
        )
        while True:
            overlay = self._copper_overlay(mask)
            n_px = int(cv2.countNonZero(mask))
            result = self._win.run(
                overlay,
                f"Copper Mask — {n_px:,} px covered",
                tune_label="Tune HSV",
            )
            if result == "accept":
                return mask, hsv_cfg
            if result == "skip":
                log.info("  Copper mask skipped — all downstream steps will be empty")
                return np.zeros_like(mask), hsv_cfg
            # result == "tune"
            hsv_cfg = _HsvTuneDialog.run_dialog(self.bgr, hsv_cfg, self.board_dir)
            mask = extract_copper_mask(self.bgr, hsv_cfg)

    def review_outline(self, outline: np.ndarray | None) -> np.ndarray | None:
        """Show detected board outline as a cyan polygon. Returns outline or None."""
        print(
            "\n── Board Outline ───────────────────────────────────────────────────\n"
            "  The cyan polygon shows the detected PCB edge.\n"
            "\n"
            "  What to look for:\n"
            "    ✓ The polygon hugs the physical edge of the board\n"
            "    ✓ All four corners (or more) are roughly correct\n"
            "    'Draw' — click corners manually if detection is wrong\n"
            "    [Skip] — no outline exported\n"
            "────────────────────────────────────────────────────────────────────"
        )
        while True:
            overlay = self._outline_overlay(outline)
            n = len(outline) if outline is not None else 0
            result = self._win.run(
                overlay,
                f"Board Outline — {n} corner points",
                tune_label="Draw manually",
            )
            if result == "accept":
                return outline
            if result == "skip":
                return None
            # result == "tune" → manual click-to-draw
            drawn = self._win.outline_draw_mode(self.bgr)
            if drawn is not None:
                outline = drawn

    def review_vias(self, vias: list[dict]) -> list[dict]:
        """Show via drill holes (filled) + annular rings. Returns vias or []."""
        print(
            "\n── Vias ────────────────────────────────────────────────────────────\n"
            "  Filled green circles = drill holes.  Outer ring = annular copper.\n"
            "\n"
            "  What to look for:\n"
            "    ✓ Every through-hole via on the board has a marker\n"
            "    ✓ Circle size roughly matches the actual drill hole\n"
            "    ✗ False positives: small circles over screw holes, fiducials,\n"
            "      or dark silkscreen text — these can be skipped or tolerated\n"
            "    ✗ If most vias are missing, the copper mask may need tuning\n"
            "────────────────────────────────────────────────────────────────────"
        )
        overlay = self._via_overlay(vias)
        result = self._win.run(overlay, f"Vias — {len(vias)} detected")
        return vias if result == "accept" else []

    def review_pads(self, pads: list[dict]) -> list[dict]:
        """Show pads as orange rotated rectangles with ref labels. Returns pads or []."""
        print(
            "\n── Pads ────────────────────────────────────────────────────────────\n"
            "  Orange rectangles show detected SMD/THT pads.\n"
            "  Yellow labels show component reference designators (if bom.csv exists).\n"
            "\n"
            "  What to look for:\n"
            "    ✓ Each discrete copper pad (not a trace) has a rectangle\n"
            "    ✓ Rectangle size and rotation roughly match the physical pad\n"
            "    ✗ Very elongated rectangles are probably traces mis-classified\n"
            "      as pads — tolerable; they'll also appear in traces\n"
            "    ✗ If almost nothing is detected, the copper mask may be too\n"
            "      conservative — go back with [S] then re-run with --review\n"
            "────────────────────────────────────────────────────────────────────"
        )
        overlay = self._pad_overlay(pads)
        result = self._win.run(overlay, f"Pads — {len(pads)} detected")
        return pads if result == "accept" else []

    def review_tracks(self, tracks: list[dict]) -> list[dict]:
        """Show vectorised trace segments as blue lines. Returns tracks or []."""
        print(
            "\n── Traces ──────────────────────────────────────────────────────────\n"
            "  Blue lines are the vectorised copper trace segments (via potrace).\n"
            "  Pad areas are excluded so only routing traces remain.\n"
            "\n"
            "  What to look for:\n"
            "    ✓ Major routing traces are represented as connected blue lines\n"
            "    ✓ Lines follow the actual copper paths on the board\n"
            "    ✗ Over-segmented or noisy lines near pad areas are expected\n"
            "      — they can be cleaned up later in KiCad\n"
            "    ✗ If there are very few or no traces, potrace may not be\n"
            "      installed (run: sudo apt install potrace) or the copper\n"
            "      mask may be too sparse\n"
            "────────────────────────────────────────────────────────────────────"
        )
        overlay = self._track_overlay(tracks)
        result = self._win.run(overlay, f"Traces — {len(tracks)} segments")
        return tracks if result == "accept" else []

    # ------------------------------------------------------------------
    # Overlay builders (numpy → numpy, using cv2 drawing primitives)
    # ------------------------------------------------------------------

    def _copper_overlay(self, mask: np.ndarray) -> np.ndarray:
        overlay = self.bgr.copy()
        tint = np.zeros_like(overlay)
        tint[mask > 0] = [0, 200, 0]
        cv2.addWeighted(tint, 0.45, overlay, 0.55, 0, overlay)
        return overlay

    def _outline_overlay(self, outline: np.ndarray | None) -> np.ndarray:
        overlay = self.bgr.copy()
        if outline is not None:
            cv2.polylines(overlay, [outline], isClosed=True,
                          color=(0, 220, 255), thickness=3)
        return overlay

    def _via_overlay(self, vias: list[dict]) -> np.ndarray:
        overlay = self.bgr.copy()
        ppm = self.px_per_mm
        for v in vias:
            cx = int(v["x_mm"] * ppm)
            cy = int(v["y_mm"] * ppm)
            r  = max(2, int(v["drill_mm"] / 2 * ppm))
            ra = max(r + 2, int((v["drill_mm"] / 2 + v["annular_mm"]) * ppm))
            cv2.circle(overlay, (cx, cy), r,  (0, 255, 80), -1)
            cv2.circle(overlay, (cx, cy), ra, (0, 255, 80), 2)
        return overlay

    def _pad_overlay(self, pads: list[dict]) -> np.ndarray:
        overlay = self.bgr.copy()
        ppm = self.px_per_mm
        for pad in pads:
            cx = int(pad["x_mm"] * ppm)
            cy = int(pad["y_mm"] * ppm)
            w  = int(pad["w_mm"] * ppm)
            h  = int(pad["h_mm"] * ppm)
            box = cv2.boxPoints(((cx, cy), (w, h), pad["rotation_deg"]))
            cv2.drawContours(overlay, [np.int0(box)], 0, (0, 140, 255), 2)
            ref = pad.get("ref", "")
            if ref:
                cv2.putText(overlay, ref, (cx + 4, cy - 4),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.4,
                            (255, 255, 0), 1, cv2.LINE_AA)
        return overlay

    def _track_overlay(self, tracks: list[dict]) -> np.ndarray:
        overlay = self.bgr.copy()
        ppm = self.px_per_mm
        for t in tracks:
            sx = int(t["start"][0] * ppm)
            sy = int(t["start"][1] * ppm)
            ex = int(t["end"][0]   * ppm)
            ey = int(t["end"][1]   * ppm)
            cv2.line(overlay, (sx, sy), (ex, ey), (255, 80, 0), 1)
        return overlay


# ---------------------------------------------------------------------------
# Internal PyQt6 review window (used only by LayerReviewer)
# ---------------------------------------------------------------------------

class _ReviewWindow:
    """
    A persistent QMainWindow that shows extraction result overlays and
    blocks until the user clicks Accept / Skip / Tune.

    Not part of the public API — use LayerReviewer instead.
    """

    def __init__(self, bgr: np.ndarray, layer_name: str):
        from PyQt6.QtCore import QEventLoop, Qt
        from PyQt6.QtGui import QColor, QFont, QPen, QBrush
        from PyQt6.QtWidgets import (
            QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
            QPushButton, QLabel, QStatusBar,
        )
        from r1mx_gui import ImageViewer

        self._QEventLoop = QEventLoop
        self._Qt = Qt

        self._win = QMainWindow()
        self._win.setWindowTitle(f"r1mx — Layer Review [{layer_name}]")
        self._win.resize(1400, 900)

        central = QWidget()
        layout = QVBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self._viewer = ImageViewer()
        layout.addWidget(self._viewer)

        # Button bar
        btn_bar = QWidget()
        btn_layout = QHBoxLayout(btn_bar)
        btn_layout.setContentsMargins(8, 4, 8, 4)

        self._lbl = QLabel("")
        self._lbl.setFont(QFont("monospace", 10))
        btn_layout.addWidget(self._lbl)
        btn_layout.addStretch()

        self._accept_btn = QPushButton("Accept  [Y]")
        self._accept_btn.setDefault(True)
        self._skip_btn   = QPushButton("Skip  [S]")
        self._tune_btn   = QPushButton("")          # label set per step
        self._tune_btn.setVisible(False)

        for btn in (self._accept_btn, self._skip_btn, self._tune_btn):
            btn_layout.addWidget(btn)

        layout.addWidget(btn_bar)
        self._win.setCentralWidget(central)

        self._result: str = "skip"
        self._loop: QEventLoop | None = None   # type: ignore[name-defined]

        self._accept_btn.clicked.connect(self._on_accept)
        self._skip_btn.clicked.connect(self._on_skip)
        self._tune_btn.clicked.connect(self._on_tune)

        # Install key handler
        self._win.keyPressEvent = self._key_press   # type: ignore[method-assign]

    def run(
        self,
        overlay: np.ndarray,
        label: str,
        tune_label: str = "",
    ) -> str:
        """
        Display overlay, show label. Block until Accept/Skip/Tune clicked.
        Returns "accept" | "skip" | "tune".
        """
        from PyQt6.QtCore import QEventLoop
        self._viewer.set_image(overlay)
        self._lbl.setText(label)
        self._tune_btn.setVisible(bool(tune_label))
        self._tune_btn.setText(tune_label)
        self._result = "skip"
        self._win.show()
        self._win.raise_()
        self._loop = QEventLoop()
        self._loop.exec()
        return self._result

    def hide(self):
        self._win.hide()

    # ── outline draw mode ────────────────────────────────────────────────

    def outline_draw_mode(self, bgr: np.ndarray) -> "np.ndarray | None":
        """
        Interactive click-to-draw board outline mode.
        Returns contour array (N,1,2 int32) or None if cancelled.
        """
        from PyQt6.QtCore import QEventLoop, QPointF
        from PyQt6.QtGui import QColor, QPen, QBrush
        from PyQt6.QtWidgets import QGraphicsEllipseItem, QGraphicsLineItem

        print(
            "\n  [Manual Outline] Click corners on the image — clockwise from top-left\n"
            "  Backspace = undo last   Accept (≥3 pts) = confirm   Skip = cancel"
        )

        self._viewer.set_image(bgr)
        self._viewer.set_crosshair_visible(True)
        self._tune_btn.setVisible(False)
        self._accept_btn.setEnabled(False)
        self._result = "skip"

        pts: list[tuple[float, float]] = []
        scene = self._viewer.scene()
        dot_items: list = []
        line_items: list = []

        cyan = QColor(0, 220, 255)
        dot_pen = QPen(cyan)
        dot_brush = QBrush(cyan)
        line_pen = QPen(cyan, 2)
        line_pen.setCosmetic(False)

        def _redraw():
            for it in dot_items + line_items:
                scene.removeItem(it)
            dot_items.clear()
            line_items.clear()
            for i, (px, py) in enumerate(pts):
                dot = QGraphicsEllipseItem(px - 5, py - 5, 10, 10)
                dot.setPen(dot_pen)
                dot.setBrush(dot_brush)
                dot.setZValue(10)
                scene.addItem(dot)
                dot_items.append(dot)
            if len(pts) >= 2:
                for i in range(len(pts) - 1):
                    li = QGraphicsLineItem(pts[i][0], pts[i][1], pts[i+1][0], pts[i+1][1])
                    li.setPen(line_pen)
                    li.setZValue(9)
                    scene.addItem(li)
                    line_items.append(li)
                # Closing preview line
                li = QGraphicsLineItem(pts[-1][0], pts[-1][1], pts[0][0], pts[0][1])
                li.setPen(line_pen)
                li.setZValue(9)
                scene.addItem(li)
                line_items.append(li)
            n = len(pts)
            suffix = f"  —  {n} point(s)"
            if n < 3:
                suffix += f" (need {3 - n} more)"
            self._lbl.setText(f"Draw outline{suffix}")
            self._accept_btn.setEnabled(n >= 3)

        def _on_click(pt: QPointF):
            pts.append((pt.x(), pt.y()))
            _redraw()

        self._viewer.imageClicked.connect(_on_click)
        _redraw()

        loop = QEventLoop()
        self._loop = loop
        loop.exec()

        self._viewer.imageClicked.disconnect(_on_click)
        self._viewer.set_crosshair_visible(False)

        for it in dot_items + line_items:
            scene.removeItem(it)

        if self._result == "skip" or len(pts) < 3:
            print("  Manual outline cancelled — keeping previous result.")
            return None

        contour = np.array(
            [[int(round(x)), int(round(y))] for x, y in pts],
            dtype=np.int32,
        ).reshape(-1, 1, 2)
        log.info("  Manual board outline: %d points", len(pts))
        return contour

    # ── internal slots ────────────────────────────────────────────────────

    def _on_accept(self):
        self._result = "accept"
        if self._loop:
            self._loop.quit()

    def _on_skip(self):
        self._result = "skip"
        if self._loop:
            self._loop.quit()

    def _on_tune(self):
        self._result = "tune"
        if self._loop:
            self._loop.quit()

    def _key_press(self, event):
        from PyQt6.QtCore import Qt
        key = event.key()
        if key in (Qt.Key.Key_Y, Qt.Key.Key_Return, Qt.Key.Key_Enter):
            self._on_accept()
        elif key == Qt.Key.Key_S:
            self._on_skip()
        elif key == Qt.Key.Key_T and self._tune_btn.isVisible():
            self._on_tune()
        elif key == Qt.Key.Key_Backspace:
            # Handled by outline_draw_mode via key filter; emit signal would be cleaner,
            # but we handle it here by re-emitting via the active loop's thread.
            # For now, ignore in non-draw mode — outline_draw_mode installs its own handler.
            pass


# ---------------------------------------------------------------------------
# HSV tuning dialog (Qt replacement for the OpenCV trackbar window)
# ---------------------------------------------------------------------------

class _HsvTuneDialog:
    """
    Qt dialog with 6 QSliders (H/S/V lo and hi) and a live preview in an
    ImageViewer.  'Save & return' persists thresholds to calibration.json.
    """

    @staticmethod
    def run_dialog(bgr: np.ndarray, hsv_cfg: dict, board_dir: Path) -> dict:
        """
        Show dialog, block until user closes.
        Returns updated hsv_cfg (with 'copper_lower'/'copper_upper' keys).
        """
        from PyQt6.QtCore import QEventLoop, Qt
        from PyQt6.QtWidgets import (
            QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
            QPushButton, QLabel, QSlider, QGroupBox,
        )
        from PyQt6.QtGui import QFont
        from r1mx_gui import ImageViewer, bgr_to_pixmap

        cfg = {**DEFAULT_HSV, **hsv_cfg}
        lo  = cfg["copper_lower"][:]
        hi  = cfg["copper_upper"][:]

        dialog = QDialog()
        dialog.setWindowTitle("r1mx — Tune HSV Copper Thresholds")
        dialog.resize(1200, 800)

        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(8, 8, 8, 8)

        viewer = ImageViewer()
        layout.addWidget(viewer, stretch=1)

        # Instructions
        info = QLabel(
            "Adjust sliders until the GREEN tint covers all exposed copper "
            "without spilling onto the solder mask.\n"
            "  Save & return — persists thresholds to calibration.json\n"
            "  Return — uses current values for this run only"
        )
        info.setFont(QFont("monospace", 9))
        info.setWordWrap(True)
        layout.addWidget(info)

        # Sliders
        sliders: dict[str, QSlider] = {}
        slider_box = QGroupBox("HSV thresholds — Copper")
        slider_form = QFormLayout(slider_box)
        specs = [
            ("H lo",  lo[0],  0, 179),
            ("S lo",  lo[1],  0, 255),
            ("V lo",  lo[2],  0, 255),
            ("H hi",  hi[0],  0, 179),
            ("S hi",  hi[1],  0, 255),
            ("V hi",  hi[2],  0, 255),
        ]
        for name, val, mn, mx in specs:
            s = QSlider(Qt.Orientation.Horizontal)
            s.setRange(mn, mx)
            s.setValue(val)
            s.setMinimumWidth(300)
            slider_form.addRow(name, s)
            sliders[name] = s

        layout.addWidget(slider_box)

        # Buttons
        btn_row = QHBoxLayout()
        save_btn   = QPushButton("Save && return")
        return_btn = QPushButton("Return (no save)")
        btn_row.addStretch()
        btn_row.addWidget(save_btn)
        btn_row.addWidget(return_btn)
        layout.addLayout(btn_row)

        result_cfg: dict = dict(hsv_cfg)

        hsv_img = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)

        def _update(_=None):
            cur_lo = [sliders["H lo"].value(), sliders["S lo"].value(), sliders["V lo"].value()]
            cur_hi = [sliders["H hi"].value(), sliders["S hi"].value(), sliders["V hi"].value()]
            mask = cv2.inRange(hsv_img, np.array(cur_lo, np.uint8), np.array(cur_hi, np.uint8))
            overlay = bgr.copy()
            tint = np.zeros_like(overlay)
            tint[mask > 0] = [0, 200, 0]
            cv2.addWeighted(tint, 0.45, overlay, 0.55, 0, overlay)
            viewer.set_image(overlay)

        for s in sliders.values():
            s.valueChanged.connect(_update)

        _update()  # initial render

        def _get_values():
            return (
                [sliders["H lo"].value(), sliders["S lo"].value(), sliders["V lo"].value()],
                [sliders["H hi"].value(), sliders["S hi"].value(), sliders["V hi"].value()],
            )

        def _save():
            cur_lo, cur_hi = _get_values()
            cal_path = board_dir / "calibration.json"
            if cal_path.exists():
                cal_data = json.loads(cal_path.read_text())
                cal_data.setdefault("hsv_overrides", {})["copper_lower"] = cur_lo
                cal_data.setdefault("hsv_overrides", {})["copper_upper"] = cur_hi
                cal_path.write_text(json.dumps(cal_data, indent=2) + "\n")
                log.info("HSV overrides saved → %s", cal_path)
            nonlocal result_cfg
            result_cfg = {**hsv_cfg, "copper_lower": cur_lo, "copper_upper": cur_hi}
            dialog.accept()

        def _return_only():
            cur_lo, cur_hi = _get_values()
            nonlocal result_cfg
            result_cfg = {**hsv_cfg, "copper_lower": cur_lo, "copper_upper": cur_hi}
            dialog.accept()

        save_btn.clicked.connect(_save)
        return_btn.clicked.connect(_return_only)

        dialog.exec()   # blocks (Qt modal dialog)
        return result_cfg


def _interactive_hsv_tune(
    board_dir: Path,
    hsv_overrides: dict,
    cal: dict | None = None,
    layer: str = "top",
) -> None:
    """Standalone HSV tuning dialog (--tune-hsv flag).  Uses _HsvTuneDialog."""
    from PyQt6.QtWidgets import QApplication
    app = QApplication.instance() or QApplication(sys.argv)

    cal = cal or {}
    layer_cal = get_layer_cal(cal, layer)

    source_img = layer_cal.get("source_image", "")
    img_path = board_dir / source_img if source_img else None

    if img_path is None or not img_path.exists():
        for fallback in ["top.JPG", "board-top.png", "bottom.JPG", "board-bottom.png"]:
            candidate = board_dir / fallback
            if candidate.exists():
                img_path = candidate
                break
        else:
            log.error("No image found in %s for HSV tuning", board_dir)
            return

    bgr = load_and_crop(img_path)
    bgr = apply_perspective_warp(bgr, layer_cal)
    _HsvTuneDialog.run_dialog(bgr, hsv_overrides, board_dir)


if __name__ == "__main__":
    main()
