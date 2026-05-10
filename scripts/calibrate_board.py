#!/usr/bin/env python3
"""
calibrate_board.py — Interactive scale and board-outline calibration for r1mx PCB photos.

Iterates over every image found in the board directory.  For each image the user
is guided through a single OpenCV GUI window:

  Phase 0 — Accept/skip the image
  Phase 1 — Label the layer (top / bottom / custom)
  Phase 2 — Click 4 board corners (TL → TR → BR → BL) for perspective correction
  Phase 3 — Click 2 reference pins on the dewarped image to set the px/mm scale
  Phase 4 — Review summary and save

The perspective-correction homography is computed from the 4 corners; the output
rectangle size is inferred from the corner pixel distances so no physical board
dimensions are required.

Usage:
    python scripts/calibrate_board.py --board cpu_io_board
    python scripts/calibrate_board.py --board cpu_io_board --ref-mm 2.54

    # Single-image override (still prompts for layer via GUI):
    python scripts/calibrate_board.py --board cpu_io_board --image top.JPG

    # Non-interactive (headless) mode:
    python scripts/calibrate_board.py --board cpu_io_board --headless \\
        --image top.JPG --ref-px 320 --ref-mm 2.54 --layer top \\
        --corners 120,95,1820,90,1825,1210,118,1215

Output (components/<board>/calibration.json):
    {
      "board_name": "cpu_io_board",
      "hsv_overrides": {},
      "layers": {
        "top": {
          "source_image": "top.JPG",
          "corners_px": [[tl_x,tl_y],[tr_x,tr_y],[br_x,br_y],[bl_x,bl_y]],
          "warp_matrix": [[3x3 homography as nested list]],
          "warped_size": [width_px, height_px],
          "px_per_mm": 142.5,
          "ref_points_warped_px": [[x1,y1],[x2,y2]],
          "ref_distance_mm": 2.54
        },
        "bottom": { "..." }
      }
    }
"""

import argparse
import json
import logging
import math
import sys
from enum import Enum, auto
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)

REPO_ROOT = Path(__file__).resolve().parent.parent
COMPONENTS_DIR = REPO_ROOT / "components"
IMAGE_EXTS = {".jpg", ".jpeg", ".png"}

# ---------------------------------------------------------------------------
# Image discovery
# ---------------------------------------------------------------------------

def find_all_images(board_dir: Path) -> list[Path]:
    """Return sorted list of all image files in board_dir."""
    return sorted(
        p for p in board_dir.iterdir()
        if p.is_file() and p.suffix.lower() in IMAGE_EXTS
    )


# ---------------------------------------------------------------------------
# Calibration data helpers
# ---------------------------------------------------------------------------

def make_layer_calibration(
    source_image: str,
    corners_px: list,
    warp_matrix: list,
    warped_size: list,
    px_per_mm: float,
    ref_points_warped_px: list,
    ref_distance_mm: float,
) -> dict:
    return {
        "source_image": source_image,
        "corners_px": corners_px,
        "warp_matrix": warp_matrix,
        "warped_size": warped_size,
        "px_per_mm": round(px_per_mm, 4),
        "ref_points_warped_px": ref_points_warped_px,
        "ref_distance_mm": ref_distance_mm,
    }


def save_calibration(board_name: str, layer: str, layer_cal: dict, board_dir: Path) -> None:
    out = board_dir / "calibration.json"
    if out.exists():
        cal = json.loads(out.read_text())
        # Migrate old flat-schema files (no "layers" key)
        if "layers" not in cal and "px_per_mm" in cal:
            log.info("Migrating old flat calibration.json to layered schema")
            old_layer = {
                "source_image": cal.get("source_image", ""),
                "corners_px": [],
                "warp_matrix": [],
                "warped_size": [],
                "px_per_mm": cal.get("px_per_mm", 0.0),
                "ref_points_warped_px": cal.get("ref_points_px", []),
                "ref_distance_mm": cal.get("ref_distance_mm", 2.54),
            }
            cal = {
                "board_name": cal.get("board_name", board_name),
                "hsv_overrides": cal.get("hsv_overrides", {}),
                "layers": {"top": old_layer},
            }
    else:
        cal = {"board_name": board_name, "hsv_overrides": {}, "layers": {}}

    cal.setdefault("board_name", board_name)
    cal.setdefault("hsv_overrides", {})
    cal.setdefault("layers", {})[layer] = layer_cal
    out.write_text(json.dumps(cal, indent=2) + "\n")
    log.info("Saved layer '%s' → %s  (%.2f px/mm)", layer, out, layer_cal["px_per_mm"])


# ---------------------------------------------------------------------------
# Geometry
# ---------------------------------------------------------------------------

def compute_homography(corners_px: list) -> tuple[list, list]:
    """
    Given 4 corners [[TL],[TR],[BR],[BL]] in original image pixel coords,
    return (warp_matrix as 3×3 nested list, [out_width, out_height]).
    Output size is inferred from the corner distances.
    """
    try:
        import cv2
        import numpy as np
    except ImportError:
        log.error("opencv-python is required. Run: pip install opencv-python")
        sys.exit(1)

    pts = np.array(corners_px, dtype=np.float32)
    tl, tr, br, bl = pts

    w = int(max(
        math.hypot(*(tr - tl)),
        math.hypot(*(br - bl)),
    ))
    h = int(max(
        math.hypot(*(bl - tl)),
        math.hypot(*(br - tr)),
    ))

    dst = np.array([[0, 0], [w - 1, 0], [w - 1, h - 1], [0, h - 1]], dtype=np.float32)
    M = cv2.getPerspectiveTransform(pts, dst)
    return M.tolist(), [w, h]


def compute_px_per_mm(pt1: list, pt2: list, ref_mm: float) -> float:
    dist = math.hypot(pt2[0] - pt1[0], pt2[1] - pt1[1])
    return dist / ref_mm


# ---------------------------------------------------------------------------
# GUI state machine
# ---------------------------------------------------------------------------

class _Phase(Enum):
    ACCEPT   = auto()
    LAYER    = auto()
    CORNERS  = auto()
    REFPTS   = auto()
    SUMMARY  = auto()
    DONE     = auto()
    SKIP     = auto()
    QUIT     = auto()


class CalibrationGUI:
    """
    Single-window OpenCV GUI that guides the user through calibrating one image.

    Usage::

        gui = CalibrationGUI(image_path, ref_mm=2.54, index=0, total=3)
        layer, layer_cal = gui.run()  # returns (None, None) if skipped
        if gui.quit_all: break        # user pressed Q
    """

    WINDOW     = "r1mx Board Calibration"
    MAX_W      = 1600
    MAX_H      = 900
    FONT       = None          # set in __init__ after cv2 import
    CORNER_SEQ = ["TL", "TR", "BR", "BL"]

    def __init__(self, image_path: Path, ref_mm: float, index: int, total: int):
        try:
            import cv2
            import numpy as np
        except ImportError:
            log.error("opencv-python is required. Run: pip install opencv-python")
            sys.exit(1)

        self.cv2 = cv2
        self.np  = np
        self.FONT = cv2.FONT_HERSHEY_SIMPLEX

        self.image_path = image_path
        self.ref_mm     = ref_mm
        self.index      = index
        self.total      = total

        bgr = cv2.imread(str(image_path))
        if bgr is None:
            raise ValueError(f"Cannot read image: {image_path}")
        self.original = bgr
        h, w = bgr.shape[:2]

        self._orig_scale = min(1.0, self.MAX_W / w, self.MAX_H / h)
        dw = int(w * self._orig_scale)
        dh = int(h * self._orig_scale)
        # Annotation sizes are scaled up so they look the same physical size in the
        # window when drawn on the full-resolution image.
        self._ann_s = 1.0 / self._orig_scale

        # State
        self.phase           = _Phase.ACCEPT
        self._layer_buf      = ""          # typed label characters
        self.result_layer    = None
        self.result_cal      = None
        self.quit_all        = False

        # Corner click state — only original-scale coords; display-scale kept for mouse→image conversion
        self._corners_d: list[tuple[int, int]] = []
        self._corners_o: list[list[int]]       = []

        # Warped image state (populated after corners confirmed)
        self._warped_o       = None
        self._warp_scale     = 1.0
        self._warp_ann_s     = 1.0
        self._warp_M         = None
        self._warp_size      = None
        self._warp_dw        = dw       # display size; updated in _build_warp
        self._warp_dh        = dh

        # Ref-point state — only original-scale coords
        self._refs_d: list[tuple[int, int]] = []
        self._refs_o: list[list[int]]       = []

        self._px_per_mm      = 0.0

        # Live mouse position in window coords (updated on MOUSEMOVE)
        self._mouse_win: tuple[int, int] | None = None

        # Store display dimensions for window sizing
        self._dw = dw
        self._dh = dh

    # ------------------------------------------------------------------
    # Coordinate helpers
    # ------------------------------------------------------------------

    def _win_to_image(self, wx: int, wy: int) -> list[int]:
        """Convert window pixel coords → original image pixel coords.
        Uses cv2.getWindowImageRect so it stays correct if the window is resized."""
        rect = self.cv2.getWindowImageRect(self.WINDOW)  # (x, y, w, h) of image area
        ww, wh = max(1, rect[2]), max(1, rect[3])
        ih, iw = self.original.shape[:2]
        return [int(wx * iw / ww), int(wy * ih / wh)]

    def _win_to_warp(self, wx: int, wy: int) -> list[int]:
        """Convert window pixel coords → warped image pixel coords."""
        rect = self.cv2.getWindowImageRect(self.WINDOW)
        ww, wh = max(1, rect[2]), max(1, rect[3])
        sw, sh = self._warp_size
        return [int(wx * sw / ww), int(wy * sh / wh)]

    # Keep old names as aliases (used in _handle_key / _on_mouse)
    def _to_orig(self, dx: int, dy: int) -> list[int]:
        return self._win_to_image(dx, dy)

    def _to_warp_orig(self, dx: int, dy: int) -> list[int]:
        return self._win_to_warp(dx, dy)

    # ------------------------------------------------------------------
    # Drawing helpers
    # ------------------------------------------------------------------

    def _draw_crosshair(self, img, cx: int, cy: int, ann_s: float = 1.0) -> None:
        """Draw a crosshair centered on (cx, cy) in image coords."""
        cv2 = self.cv2
        arm   = int(20 * ann_s)   # half-length of each arm
        gap   = int(4 * ann_s)    # gap around the centre point
        thick = max(1, round(ann_s))
        h, w  = img.shape[:2]

        # Horizontal and vertical arms with a small gap at centre
        for (x0, x1), (y0, y1) in [
            ((max(0, cx - arm), max(0, cx - gap)), (cy, cy)),  # left arm
            ((min(w, cx + gap), min(w, cx + arm)), (cy, cy)),  # right arm
            ((cx, cx), (max(0, cy - arm), max(0, cy - gap))),  # top arm
            ((cx, cx), (min(h, cy + gap), min(h, cy + arm))),  # bottom arm
        ]:
            cv2.line(img, (x0, y0), (x1, y1), (0, 0, 0),       thick + 2, cv2.LINE_AA)
            cv2.line(img, (x0, y0), (x1, y1), (0, 255, 255), thick,     cv2.LINE_AA)

    def _overlay_text(self, img, lines: list[str], ann_s: float = 1.0) -> None:
        """Draw semi-transparent text box in the top-left corner."""
        cv2 = self.cv2
        s = ann_s
        fscale = 0.55 * s
        thick  = max(1, round(s))
        lh     = int(22 * s)
        pad    = int(8 * s)
        box_w = max(
            cv2.getTextSize(l, self.FONT, fscale, thick)[0][0]
            for l in lines
        ) + pad * 2
        box_h = len(lines) * lh + pad * 2

        overlay = img.copy()
        cv2.rectangle(overlay, (0, 0), (box_w, box_h), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.65, img, 0.35, 0, img)

        for i, line in enumerate(lines):
            y = (i + 1) * lh + pad // 2
            cv2.putText(img, line, (pad, y), self.FONT, fscale,
                        (255, 255, 255), thick, cv2.LINE_AA)

    def _draw_corners(self, img, ann_s: float = 1.0) -> None:
        cv2, np = self.cv2, self.np
        s = ann_s
        r  = max(4, round(7 * s))
        lw = max(1, round(2 * s))
        fs = 0.6 * s
        for i, co in enumerate(self._corners_o):
            cx, cy = co[0], co[1]
            cv2.circle(img, (cx, cy), r, (0, 255, 0), -1)
            cv2.putText(img, self.CORNER_SEQ[i], (cx + round(10 * s), cy - round(6 * s)),
                        self.FONT, fs, (0, 255, 0), lw, cv2.LINE_AA)
        n = len(self._corners_o)
        if n >= 2:
            for i in range(n - 1):
                p1 = tuple(self._corners_o[i])
                p2 = tuple(self._corners_o[i + 1])
                cv2.line(img, p1, p2, (0, 200, 255), max(1, round(s)))
        if n == 4:
            pts = np.array(self._corners_o, dtype=np.int32)
            cv2.polylines(img, [pts[[0, 1, 2, 3]]], isClosed=True,
                          color=(0, 200, 255), thickness=lw)

    def _draw_refs(self, img, ann_s: float = 1.0) -> None:
        cv2 = self.cv2
        s = ann_s
        r  = max(4, round(7 * s))
        lw = max(1, round(2 * s))
        fs = 0.6 * s
        for i, ro in enumerate(self._refs_o):
            rx, ry = ro[0], ro[1]
            cv2.circle(img, (rx, ry), r, (0, 80, 255), -1)
            cv2.putText(img, f"P{i + 1}", (rx + round(10 * s), ry - round(6 * s)),
                        self.FONT, fs, (0, 80, 255), lw, cv2.LINE_AA)
        if len(self._refs_o) == 2:
            p1 = tuple(self._refs_o[0])
            p2 = tuple(self._refs_o[1])
            cv2.line(img, p1, p2, (255, 100, 0), lw)
            ppm = compute_px_per_mm(self._refs_o[0], self._refs_o[1], self.ref_mm)
            mid = (int((p1[0] + p2[0]) / 2 + 5 * s), int((p1[1] + p2[1]) / 2 - 8 * s))
            cv2.putText(img, f"{ppm:.1f} px/mm", mid,
                        self.FONT, 0.55 * s, (255, 100, 0), lw, cv2.LINE_AA)

    # ------------------------------------------------------------------
    # Per-phase frame renderers
    # ------------------------------------------------------------------

    def _frame_accept(self):
        img = self.original.copy()
        self._overlay_text(img, [
            f"Image {self.index + 1}/{self.total}: {self.image_path.name}",
            "[Y] Use this image   [N] Skip   [Q] Quit all",
        ], ann_s=self._ann_s)
        return img

    def _frame_layer(self):
        img = self.original.copy()
        typed = self._layer_buf
        self._overlay_text(img, [
            "[T] top   [B] bottom   or type a label + [Enter]",
            f"Layer: {typed}_",
        ], ann_s=self._ann_s)
        return img

    def _frame_corners(self):
        img = self.original.copy()
        n = len(self._corners_o)
        next_lbl = self.CORNER_SEQ[n] if n < 4 else "—"
        hints = "[Enter] confirm (after 4)  [Backspace] undo  [R] redo all"
        self._overlay_text(img, [
            f"Click corners: TL \u2192 TR \u2192 BR \u2192 BL  |  next: {next_lbl}  ({n}/4)",
            hints,
        ], ann_s=self._ann_s)
        self._draw_corners(img, ann_s=self._ann_s)
        if self._mouse_win and n < 4:
            mx, my = self._to_orig(*self._mouse_win)
            self._draw_crosshair(img, mx, my, ann_s=self._ann_s)
        return img

    def _frame_refpts(self):
        img = self._warped_o.copy()
        n = len(self._refs_o)
        self._overlay_text(img, [
            f"Perspective corrected. Click 2 reference points {self.ref_mm} mm apart  ({n}/2)",
            "[Enter] confirm (after 2)  [Backspace] undo",
        ], ann_s=self._warp_ann_s)
        self._draw_refs(img, ann_s=self._warp_ann_s)
        if self._mouse_win and n < 2:
            mx, my = self._to_warp_orig(*self._mouse_win)
            self._draw_crosshair(img, mx, my, ann_s=self._warp_ann_s)
        return img

    def _frame_summary(self):
        img = self._warped_o.copy()
        self._overlay_text(img, [
            f"Layer: {self.result_layer}   Source: {self.image_path.name}",
            f"px/mm: {self._px_per_mm:.2f}   Warp: {self._warp_size[0]}x{self._warp_size[1]} px",
            "[S] Save   [R] Redo corners   [N] Discard",
        ], ann_s=self._warp_ann_s)
        return img

    # ------------------------------------------------------------------
    # Perspective warp
    # ------------------------------------------------------------------

    def _build_warp(self) -> None:
        M_list, size = compute_homography(self._corners_o)
        M_np = self.np.array(M_list, dtype=self.np.float64)
        self._warp_M    = M_list
        self._warp_size = size
        warped = self.cv2.warpPerspective(self.original, M_np, tuple(size))
        self._warped_o  = warped
        self._warp_scale = min(1.0, self.MAX_W / size[0], self.MAX_H / size[1])
        self._warp_ann_s = 1.0 / self._warp_scale
        self._warp_dw = int(size[0] * self._warp_scale)
        self._warp_dh = int(size[1] * self._warp_scale)

    # ------------------------------------------------------------------
    # Mouse callback
    # ------------------------------------------------------------------

    def _on_mouse(self, event, x, y, flags, param):
        cv2 = self.cv2
        if event == cv2.EVENT_MOUSEMOVE:
            self._mouse_win = (x, y)
        elif event == cv2.EVENT_LBUTTONDOWN:
            if self.phase == _Phase.CORNERS and len(self._corners_d) < 4:
                self._corners_d.append((x, y))
                self._corners_o.append(self._to_orig(x, y))
            elif self.phase == _Phase.REFPTS and len(self._refs_d) < 2:
                self._refs_d.append((x, y))
                self._refs_o.append(self._to_warp_orig(x, y))
    # ------------------------------------------------------------------
    # Main loop
    # ------------------------------------------------------------------

    def run(self) -> tuple:
        """
        Block until the user finishes or skips.
        Returns (layer_label, layer_cal_dict) on save, or (None, None) on skip.
        Sets self.quit_all = True if the user pressed Q.
        """
        cv2 = self.cv2
        cv2.namedWindow(self.WINDOW, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(self.WINDOW, self._dw, self._dh)
        cv2.setMouseCallback(self.WINDOW, self._on_mouse)

        terminal_phases = {_Phase.DONE, _Phase.SKIP, _Phase.QUIT}
        prev_phase = None

        while self.phase not in terminal_phases:
            # When switching to the warp-based phases, resize the window
            if self.phase != prev_phase:
                if self.phase in (_Phase.REFPTS, _Phase.SUMMARY):
                    cv2.resizeWindow(self.WINDOW, self._warp_dw, self._warp_dh)
                elif self.phase in (_Phase.ACCEPT, _Phase.LAYER, _Phase.CORNERS):
                    cv2.resizeWindow(self.WINDOW, self._dw, self._dh)
                prev_phase = self.phase

            # Render current phase
            if self.phase == _Phase.ACCEPT:
                frame = self._frame_accept()
            elif self.phase == _Phase.LAYER:
                frame = self._frame_layer()
            elif self.phase == _Phase.CORNERS:
                frame = self._frame_corners()
            elif self.phase == _Phase.REFPTS:
                frame = self._frame_refpts()
            elif self.phase == _Phase.SUMMARY:
                frame = self._frame_summary()
            else:
                break

            cv2.imshow(self.WINDOW, frame)
            key = cv2.waitKey(30) & 0xFF

            if key == 255:   # no key pressed
                continue

            self._handle_key(key)

        cv2.destroyWindow(self.WINDOW)
        return self.result_layer, self.result_cal

    def _handle_key(self, key: int) -> None:
        """Dispatch key presses for the current phase."""
        p = self.phase

        if p == _Phase.ACCEPT:
            if key in (ord('y'), ord('Y')):
                self.phase = _Phase.LAYER
            elif key in (ord('n'), ord('N')):
                self.phase = _Phase.SKIP
            elif key in (ord('q'), ord('Q')):
                self.quit_all = True
                self.phase = _Phase.QUIT

        elif p == _Phase.LAYER:
            if key in (ord('t'), ord('T')) and not self._layer_buf:
                self.result_layer = "top"
                self.phase = _Phase.CORNERS
            elif key in (ord('b'), ord('B')) and not self._layer_buf:
                self.result_layer = "bottom"
                self.phase = _Phase.CORNERS
            elif key == 13:   # Enter
                self.result_layer = self._layer_buf.strip() or "top"
                self._layer_buf = ""
                self.phase = _Phase.CORNERS
            elif key == 8:    # Backspace
                self._layer_buf = self._layer_buf[:-1]
            elif 32 <= key < 127:
                self._layer_buf += chr(key)

        elif p == _Phase.CORNERS:
            if key == 8 and self._corners_d:      # Backspace — undo last
                self._corners_d.pop()
                self._corners_o.pop()
            elif key in (ord('r'), ord('R')):     # Redo all corners
                self._corners_d.clear()
                self._corners_o.clear()
            elif key == 13 and len(self._corners_d) == 4:   # Enter — confirm
                self._build_warp()
                self.phase = _Phase.REFPTS

        elif p == _Phase.REFPTS:
            if key == 8 and self._refs_d:         # Backspace — undo last
                self._refs_d.pop()
                self._refs_o.pop()
            elif key == 13 and len(self._refs_d) == 2:      # Enter — confirm
                self._px_per_mm = compute_px_per_mm(
                    self._refs_o[0], self._refs_o[1], self.ref_mm
                )
                self.phase = _Phase.SUMMARY

        elif p == _Phase.SUMMARY:
            if key in (ord('s'), ord('S')):
                self.result_cal = make_layer_calibration(
                    source_image=self.image_path.name,
                    corners_px=self._corners_o,
                    warp_matrix=self._warp_M,
                    warped_size=self._warp_size,
                    px_per_mm=self._px_per_mm,
                    ref_points_warped_px=self._refs_o,
                    ref_distance_mm=self.ref_mm,
                )
                self.phase = _Phase.DONE
            elif key in (ord('r'), ord('R')):     # Redo from corners
                self._corners_d.clear()
                self._corners_o.clear()
                self._refs_d.clear()
                self._refs_o.clear()
                self.phase = _Phase.CORNERS
            elif key in (ord('n'), ord('N')):
                self.phase = _Phase.SKIP


# ---------------------------------------------------------------------------
# Headless calibration (non-interactive)
# ---------------------------------------------------------------------------

def headless_calibrate(
    board_dir: Path,
    image_path: Path,
    layer: str,
    ref_px: float,
    ref_mm: float,
    corners_raw: str,
) -> dict:
    """Non-interactive calibration for scripting."""
    corners: list = []
    warp_matrix: list = []
    warped_size: list = []

    if corners_raw:
        vals = [float(v) for v in corners_raw.split(",")]
        if len(vals) != 8:
            log.error("--corners requires exactly 8 comma-separated values (TL TR BR BL)")
            sys.exit(1)
        corners = [[int(vals[i * 2]), int(vals[i * 2 + 1])] for i in range(4)]
        warp_matrix, warped_size = compute_homography(corners)

    px_per_mm = ref_px / ref_mm
    return make_layer_calibration(
        source_image=image_path.name,
        corners_px=corners,
        warp_matrix=warp_matrix,
        warped_size=warped_size,
        px_per_mm=px_per_mm,
        ref_points_warped_px=[],
        ref_distance_mm=ref_mm,
    )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Interactive per-layer PCB photo calibration with perspective correction."
    )
    parser.add_argument("--board", required=True, metavar="NAME",
                        help="Board folder name under components/")
    parser.add_argument("--ref-mm", type=float, default=2.54, metavar="FLOAT",
                        help="Known distance between the two reference points in mm "
                             "(default: 2.54 — standard 0.1\" header pitch)")
    parser.add_argument("--image", metavar="FILENAME",
                        help="Process only this image file (default: all images in board dir)")
    parser.add_argument("--headless", action="store_true",
                        help="Non-interactive mode (requires --ref-px, --layer; "
                             "optionally --corners for perspective correction)")
    parser.add_argument("--ref-px", type=float, default=0.0, metavar="FLOAT",
                        help="Measured pixel distance between reference points (--headless only)")
    parser.add_argument("--layer", default="", metavar="LABEL",
                        help="Layer label, e.g. top or bottom (--headless required; "
                             "interactive mode prompts in GUI)")
    parser.add_argument("--corners", default="", metavar="x1,y1,...,x4,y4",
                        help="8 comma-separated corner coords TL TR BR BL (--headless only)")
    args = parser.parse_args()

    board_dir = COMPONENTS_DIR / args.board
    if not board_dir.is_dir():
        log.error("Board directory not found: %s", board_dir)
        sys.exit(1)

    # ------------------------------------------------------------------
    # Headless path
    # ------------------------------------------------------------------
    if args.headless:
        if args.ref_px <= 0:
            log.error("--headless requires --ref-px VALUE")
            sys.exit(1)
        if not args.layer:
            log.error("--headless requires --layer VALUE (e.g. --layer top)")
            sys.exit(1)

        if args.image:
            image_path = board_dir / args.image
        else:
            images = find_all_images(board_dir)
            if not images:
                log.error("No images found in %s", board_dir)
                sys.exit(1)
            image_path = images[0]

        if not image_path.exists():
            log.error("Image not found: %s", image_path)
            sys.exit(1)

        cal = headless_calibrate(
            board_dir, image_path, args.layer,
            args.ref_px, args.ref_mm, args.corners,
        )
        save_calibration(args.board, args.layer, cal, board_dir)
        print(f"Headless calibration: {cal['px_per_mm']:.2f} px/mm  (layer: {args.layer})")
        print(f"Now run: python scripts/extract_pcb_layers.py --board {args.board} --layer {args.layer}")
        return

    # ------------------------------------------------------------------
    # Interactive GUI path
    # ------------------------------------------------------------------
    images = [board_dir / args.image] if args.image else find_all_images(board_dir)
    if not images:
        log.error("No images found in %s. Use --image to specify one.", board_dir)
        sys.exit(1)

    saved = 0
    for i, image_path in enumerate(images):
        if not image_path.exists():
            log.warning("Image not found, skipping: %s", image_path)
            continue

        try:
            gui = CalibrationGUI(image_path, args.ref_mm, i, len(images))
        except ValueError as exc:
            log.warning("Skipping %s: %s", image_path.name, exc)
            continue

        layer, layer_cal = gui.run()

        if gui.quit_all:
            print("Quit.")
            break

        if layer is not None and layer_cal is not None:
            save_calibration(args.board, layer, layer_cal, board_dir)
            saved += 1
            log.info("Saved: layer '%s' from %s  (%.2f px/mm)",
                     layer, image_path.name, layer_cal["px_per_mm"])

    if saved:
        print(f"\n{saved} layer(s) calibrated.")
        print(f"Now run: python scripts/extract_pcb_layers.py --board {args.board}")
    else:
        print("No layers calibrated.")


if __name__ == "__main__":
    main()

