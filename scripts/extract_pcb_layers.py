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

Usage:
    # Requires calibration.json first (see calibrate_board.py):
    python scripts/extract_pcb_layers.py --board cpu_io_board
    python scripts/extract_pcb_layers.py --board cpu_io_board --debug
    python scripts/extract_pcb_layers.py --board cpu_io_board --tune-hsv
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
) -> dict:
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

    for layer_name, image_name, flip, kicad_layer in [
        ("front", "top.JPG",    False, "F_Cu"),
        ("back",  "bottom.JPG", True,  "B_Cu"),
    ]:
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
                continue

        log.info("  Layer: %s (%s)", layer_name, img_path.name)
        bgr = load_and_crop(img_path)

        if flip:
            bgr = cv2.flip(bgr, 1)  # horizontal flip for bottom layer alignment

        # Board outline (front layer only)
        if layer_name == "front":
            outline = detect_board_outline(bgr)
            if outline is not None:
                pts = [[round(float(p[0][0]) / px_per_mm, 3),
                        round(float(p[0][1]) / px_per_mm, 3)]
                       for p in outline]
                layout["board_outline"] = pts
                log.info("  Board outline: %d points", len(pts))

        copper_mask = extract_copper_mask(bgr, hsv_cfg)
        if debug_dir:
            cv2.imwrite(str(debug_dir / f"{layer_name}_copper_mask.png"), copper_mask)

        vias = detect_vias(bgr, copper_mask, px_per_mm, hsv_cfg)
        if layer_name == "front":
            layout["vias"] = vias

        # Build pad exclusion mask for trace extraction
        pad_mask = np.zeros(copper_mask.shape, np.uint8)

        pads = detect_pads(copper_mask, px_per_mm, vias, layer=kicad_layer)

        # Mark pads on exclusion mask
        for pad in pads:
            cx = int(pad["x_mm"] * px_per_mm)
            cy = int(pad["y_mm"] * px_per_mm)
            rw = int(pad["w_mm"] * px_per_mm / 2 + 2)
            rh = int(pad["h_mm"] * px_per_mm / 2 + 2)
            cv2.ellipse(pad_mask, (cx, cy), (rw, rh), pad["rotation_deg"], 0, 360, 255, -1)

        # Also exclude via rings from pad mask
        for via in vias:
            cx = int(via["x_mm"] * px_per_mm)
            cy = int(via["y_mm"] * px_per_mm)
            r = int((via["drill_mm"] / 2 + via["annular_mm"]) * px_per_mm + 2)
            cv2.circle(pad_mask, (cx, cy), r, 255, -1)

        # Assign refs from bom.csv
        bom_path = board_dir / "bom.csv"
        pads = assign_refs_to_pads(pads, bom_path, px_per_mm)

        tracks = vectorise_traces(copper_mask, pad_mask, px_per_mm, layer=kicad_layer)

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
    parser.add_argument("--px-per-mm", type=float, default=0.0, metavar="FLOAT",
                        help="Pixels per mm (overrides calibration.json)")
    parser.add_argument("--debug", action="store_true",
                        help="Save intermediate mask images to <board>/_layer_debug/")
    parser.add_argument("--tune-hsv", action="store_true",
                        help="Launch interactive HSV tuning window (requires display)")
    args = parser.parse_args()

    board_dir = COMPONENTS_DIR / args.board
    if not board_dir.is_dir():
        log.error("Board not found: %s", board_dir)
        sys.exit(1)

    # Resolve px_per_mm
    px_per_mm = args.px_per_mm
    if px_per_mm <= 0:
        cal = load_calibration(board_dir)
        px_per_mm = cal.get("px_per_mm", 0.0)
    if px_per_mm <= 0:
        log.error(
            "px_per_mm not set. Run calibrate_board.py first, or pass --px-per-mm VALUE.\n"
            "Tip: measure the pitch between two header pins (2.54 mm) in pixels in any\n"
            "image editor and divide: px_per_mm = measured_px / 2.54"
        )
        sys.exit(1)

    # Load HSV overrides from calibration if available
    cal = load_calibration(board_dir)
    hsv_overrides = cal.get("hsv_overrides", {})

    if args.tune_hsv:
        _interactive_hsv_tune(board_dir, hsv_overrides)
        return

    layout = process_board(board_dir, px_per_mm, args.debug, hsv_overrides)
    save_layout(layout, board_dir)


def _interactive_hsv_tune(board_dir: Path, hsv_overrides: dict) -> None:
    """Interactive trackbar window to tune HSV copper thresholds."""
    img_path = board_dir / "top.JPG"
    if not img_path.exists():
        for alt in ["board-top.png"]:
            if (board_dir / alt).exists():
                img_path = board_dir / alt
                break
        else:
            log.error("No top image found in %s", board_dir)
            return

    bgr = load_and_crop(img_path)
    hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)

    cfg = {**DEFAULT_HSV, **hsv_overrides}
    lo = cfg["copper_lower"][:]
    hi = cfg["copper_upper"][:]

    cv2.namedWindow("HSV Tune", cv2.WINDOW_NORMAL)

    def nothing(_): pass

    cv2.createTrackbar("H lo", "HSV Tune", lo[0], 179, nothing)
    cv2.createTrackbar("S lo", "HSV Tune", lo[1], 255, nothing)
    cv2.createTrackbar("V lo", "HSV Tune", lo[2], 255, nothing)
    cv2.createTrackbar("H hi", "HSV Tune", hi[0], 179, nothing)
    cv2.createTrackbar("S hi", "HSV Tune", hi[1], 255, nothing)
    cv2.createTrackbar("V hi", "HSV Tune", hi[2], 255, nothing)

    display = cv2.resize(bgr, (1280, 720))
    hsv_disp = cv2.resize(hsv, (1280, 720))

    print("Adjust trackbars. Press 's' to save to calibration.json, 'q' to quit.")
    while True:
        lo = [cv2.getTrackbarPos("H lo", "HSV Tune"),
              cv2.getTrackbarPos("S lo", "HSV Tune"),
              cv2.getTrackbarPos("V lo", "HSV Tune")]
        hi = [cv2.getTrackbarPos("H hi", "HSV Tune"),
              cv2.getTrackbarPos("S hi", "HSV Tune"),
              cv2.getTrackbarPos("V hi", "HSV Tune")]

        mask = cv2.inRange(hsv_disp, np.array(lo, np.uint8), np.array(hi, np.uint8))
        overlay = display.copy()
        overlay[mask > 0] = [0, 255, 0]
        cv2.imshow("HSV Tune", overlay)

        key = cv2.waitKey(30) & 0xFF
        if key == ord("q"):
            break
        if key == ord("s"):
            cal_path = board_dir / "calibration.json"
            cal = json.loads(cal_path.read_text()) if cal_path.exists() else {}
            cal.setdefault("hsv_overrides", {})["copper_lower"] = lo
            cal.setdefault("hsv_overrides", {})["copper_upper"] = hi
            cal_path.write_text(json.dumps(cal, indent=2))
            print(f"Saved to {cal_path}")

    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
