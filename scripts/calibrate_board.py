#!/usr/bin/env python3
"""
calibrate_board.py — Interactive scale and board-outline calibration for r1mx PCB photos.

Allows the user to click two reference points on a PCB photograph (e.g. the centres
of two adjacent header pins at 2.54 mm pitch, or two fiducial marks) and records
the pixels-per-mm scale factor plus board corners to calibration.json.

Usage:
    python scripts/calibrate_board.py --board cpu_io_board
    python scripts/calibrate_board.py --board cpu_io_board --ref-mm 2.54
    python scripts/calibrate_board.py --board cpu_io_board --headless \
        --ref-px 100 --ref-mm 2.54

Requires a display for interactive mode; --headless accepts px/mm directly.

Output (components/<board>/calibration.json):
    {
      "px_per_mm": 142.5,
      "ref_points_px": [[x1, y1], [x2, y2]],
      "ref_distance_mm": 2.54,
      "board_name": "cpu_io_board",
      "source_image": "top.JPG",
      "hsv_overrides": {}     # filled by extract_pcb_layers.py --tune-hsv
    }
"""

import argparse
import json
import logging
import math
import sys
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)

REPO_ROOT = Path(__file__).resolve().parent.parent
COMPONENTS_DIR = REPO_ROOT / "components"

# ---------------------------------------------------------------------------
# Calibration data model
# ---------------------------------------------------------------------------

def make_calibration(
    board_name: str,
    source_image: str,
    px_per_mm: float,
    ref_points_px: list,
    ref_distance_mm: float,
) -> dict:
    return {
        "board_name": board_name,
        "source_image": source_image,
        "px_per_mm": round(px_per_mm, 4),
        "ref_points_px": ref_points_px,
        "ref_distance_mm": ref_distance_mm,
        "hsv_overrides": {},
    }


def save_calibration(cal: dict, board_dir: Path) -> None:
    out = board_dir / "calibration.json"
    # Preserve existing hsv_overrides if any
    if out.exists():
        existing = json.loads(out.read_text())
        cal["hsv_overrides"] = existing.get("hsv_overrides", {})
    out.write_text(json.dumps(cal, indent=2) + "\n")
    log.info("Calibration saved: %s  (%.2f px/mm)", out, cal["px_per_mm"])


# ---------------------------------------------------------------------------
# Interactive click-to-calibrate (requires display)
# ---------------------------------------------------------------------------

def interactive_calibrate(
    board_dir: Path,
    image_path: Path,
    ref_distance_mm: float,
) -> dict | None:
    """
    Show the PCB photo; user clicks two reference points.
    Returns calibration dict or None on cancel.
    """
    try:
        import cv2
        import numpy as np
    except ImportError:
        log.error("opencv-python not installed. Run: pip install opencv-python")
        return None

    bgr = cv2.imread(str(image_path))
    if bgr is None:
        log.error("Cannot load %s", image_path)
        return None

    h, w = bgr.shape[:2]
    # Scale display to fit on screen without resampling the calibration
    max_display = 1600
    scale = min(1.0, max_display / max(h, w))
    display = cv2.resize(bgr, (int(w * scale), int(h * scale)))

    points_display = []   # clicks in display coords
    points_original = []  # clicks in full-resolution coords

    def on_click(event, x, y, flags, _param):
        if event == cv2.EVENT_LBUTTONDOWN and len(points_display) < 2:
            points_display.append((x, y))
            ox, oy = int(x / scale), int(y / scale)
            points_original.append((ox, oy))
            cv2.circle(display, (x, y), 8, (0, 255, 0), 2)
            cv2.circle(display, (x, y), 2, (0, 255, 0), -1)
            cv2.putText(display, f"P{len(points_display)}", (x + 10, y - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
            if len(points_display) == 2:
                cv2.line(display, points_display[0], points_display[1], (0, 255, 0), 2)
            cv2.imshow("PCB Calibration", display)

    cv2.namedWindow("PCB Calibration", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("PCB Calibration", int(w * scale), int(h * scale))
    cv2.setMouseCallback("PCB Calibration", on_click)

    print("\n=== PCB Calibration ===")
    print(f"Image: {image_path.name}  ({w}×{h} px)")
    print(f"Reference distance: {ref_distance_mm} mm")
    print("Click TWO reference points on the board (e.g. two adjacent header pins).")
    print("Press ENTER to confirm, ESC to cancel.\n")

    cv2.imshow("PCB Calibration", display)

    while True:
        key = cv2.waitKey(50) & 0xFF
        if key == 27:  # ESC
            cv2.destroyAllWindows()
            return None
        if key in (13, 10) and len(points_original) == 2:  # ENTER
            break

    cv2.destroyAllWindows()

    x1, y1 = points_original[0]
    x2, y2 = points_original[1]
    dist_px = math.hypot(x2 - x1, y2 - y1)
    px_per_mm = dist_px / ref_distance_mm

    print(f"  Distance: {dist_px:.1f} px = {ref_distance_mm} mm → {px_per_mm:.2f} px/mm")

    return make_calibration(
        board_name=board_dir.name,
        source_image=image_path.name,
        px_per_mm=px_per_mm,
        ref_points_px=[list(points_original[0]), list(points_original[1])],
        ref_distance_mm=ref_distance_mm,
    )


# ---------------------------------------------------------------------------
# Headless mode (non-interactive, for scripting)
# ---------------------------------------------------------------------------

def headless_calibrate(
    board_dir: Path,
    image_path: Path,
    ref_px: float,
    ref_distance_mm: float,
) -> dict:
    """
    Non-interactive calibration: supply measured pixel distance directly.
    """
    px_per_mm = ref_px / ref_distance_mm
    print(f"  {ref_px:.1f} px = {ref_distance_mm} mm → {px_per_mm:.2f} px/mm")
    return make_calibration(
        board_name=board_dir.name,
        source_image=image_path.name,
        px_per_mm=px_per_mm,
        ref_points_px=[],
        ref_distance_mm=ref_distance_mm,
    )


# ---------------------------------------------------------------------------
# Board image discovery
# ---------------------------------------------------------------------------

def find_top_image(board_dir: Path) -> Path | None:
    for name in ["top.JPG", "top.jpg", "top.png", "board-top.png",
                 "front.JPG", "front.jpg"]:
        p = board_dir / name
        if p.exists():
            return p
    # Fall back to first image in the directory
    for p in sorted(board_dir.iterdir()):
        if p.suffix.lower() in (".jpg", ".jpeg", ".png") and "bottom" not in p.name.lower():
            return p
    return None


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Interactive scale calibration for PCB photos."
    )
    parser.add_argument("--board", required=True, metavar="NAME",
                        help="Board folder name under components/")
    parser.add_argument("--ref-mm", type=float, default=2.54, metavar="FLOAT",
                        help="Known distance between the two reference points in mm "
                             "(default: 2.54 — standard 0.1\" header pitch)")
    parser.add_argument("--headless", action="store_true",
                        help="Non-interactive mode: provide --ref-px")
    parser.add_argument("--ref-px", type=float, default=0.0, metavar="FLOAT",
                        help="Measured pixel distance between reference points (--headless only)")
    parser.add_argument("--image", metavar="FILENAME",
                        help="Override image filename (default: auto-discover top image)")
    args = parser.parse_args()

    board_dir = COMPONENTS_DIR / args.board
    if not board_dir.is_dir():
        log.error("Board not found: %s", board_dir)
        sys.exit(1)

    if args.image:
        image_path = board_dir / args.image
    else:
        image_path = find_top_image(board_dir)

    if image_path is None or not image_path.exists():
        log.error("No suitable image found in %s. Use --image to specify one.", board_dir)
        sys.exit(1)

    log.info("Using image: %s", image_path)

    if args.headless:
        if args.ref_px <= 0:
            log.error("--headless requires --ref-px VALUE (measured pixels between reference points)")
            sys.exit(1)
        cal = headless_calibrate(board_dir, image_path, args.ref_px, args.ref_mm)
    else:
        cal = interactive_calibrate(board_dir, image_path, args.ref_mm)
        if cal is None:
            print("Calibration cancelled.")
            sys.exit(0)

    save_calibration(cal, board_dir)
    print(f"\nCalibration complete: {cal['px_per_mm']:.2f} px/mm")
    print(f"Now run: python scripts/extract_pcb_layers.py --board {args.board}")


if __name__ == "__main__":
    main()
