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
# PyQt6 — imported at module level; only QApplication creation needs display
# ---------------------------------------------------------------------------
try:
    from PyQt6.QtCore import QEventLoop, QPointF, Qt
    from PyQt6.QtGui import QColor, QPen
    from PyQt6.QtWidgets import (
        QApplication, QGraphicsRectItem, QGraphicsTextItem,
        QMainWindow, QStatusBar,
    )
    _PYQT6 = True
except ImportError:
    _PYQT6 = False

# r1mx_gui lives in the same directory as this script
sys.path.insert(0, str(Path(__file__).parent))

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
    return (warp_matrix as 3x3 nested list, [out_width, out_height]).
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


_TERMINAL_PHASES = {_Phase.DONE, _Phase.SKIP, _Phase.QUIT}


class CalibrationGUI(QMainWindow):
    """
    PyQt6 calibration window for a single board image.

    Coordinate conversion is handled by QGraphicsView.mapToScene() — no manual
    scale factors or device-pixel-ratio math required.

    Usage::

        app = QApplication.instance() or QApplication(sys.argv)
        gui = CalibrationGUI(image_path, ref_mm=2.54, index=0, total=3)
        layer, layer_cal = gui.run()   # blocks via nested QEventLoop
        if gui.quit_all: break         # user pressed Q or closed the window
    """

    TITLE      = "r1mx Board Calibration"
    CORNER_SEQ = ["TL", "TR", "BR", "BL"]

    def __init__(
        self,
        image_path: Path,
        ref_mm: float,
        index: int,
        total: int,
        preset_layer: str | None = None,
    ) -> None:
        """
        Parameters
        ----------
        image_path    : path to the board photograph
        ref_mm        : known distance between the two reference points
        index / total : used for the window title (e.g. "1 / 3")
        preset_layer  : when set, the ACCEPT and LAYER phases are skipped —
                        the window goes straight to corner selection.  Use
                        this when the caller already knows which layer the
                        image belongs to (e.g. via right-click in the tree).
        """
        if not _PYQT6:
            log.error("PyQt6 is required for the GUI.  Run: pip install PyQt6")
            sys.exit(1)
        super().__init__()

        self.image_path   = image_path
        self.ref_mm       = ref_mm
        self.index        = index
        self.total        = total
        self._preset_layer = preset_layer   # None → normal ACCEPT→LAYER flow

        # ── Load image ──────────────────────────────────────────────────────
        try:
            import cv2
            import numpy as np
        except ImportError:
            log.error("opencv-python is required: pip install opencv-python")
            sys.exit(1)
        self._cv2 = cv2
        self._np  = np

        bgr = cv2.imread(str(image_path))
        if bgr is None:
            raise ValueError(f"Cannot read image: {image_path}")
        self.original = bgr
        h, w = bgr.shape[:2]

        # ── State ───────────────────────────────────────────────────────────
        self.phase        = _Phase.ACCEPT
        self._layer_buf   = ""
        self.result_layer = preset_layer    # pre-fill if given
        self.result_cal   = None
        self.quit_all     = False

        # Corner coords (original image pixels)
        self._corners: list[list[int]] = []
        # Ref-point coords (warped image pixels)
        self._refs: list[list[int]]    = []
        # Tracked QGraphicsItems for annotations (cleared between phases)
        self._overlay_items: list      = []

        # Warp
        self._warped    = None
        self._warp_M    = None
        self._warp_size = None
        self._px_per_mm = 0.0

        # Event loop handle (set in run())
        self._loop: QEventLoop | None = None

        # ── Import shared gui helpers ────────────────────────────────────────
        from r1mx_gui import (
            ImageViewer, draw_corner, draw_ref_point, draw_polyline,
        )
        self._draw_corner     = draw_corner
        self._draw_ref_point  = draw_ref_point
        self._draw_polyline   = draw_polyline

        # ── Build UI ─────────────────────────────────────────────────────────
        self._viewer = ImageViewer(self)
        self.setCentralWidget(self._viewer)
        self._status = QStatusBar(self)
        self.setStatusBar(self._status)

        # Size window to ~85 % of available screen, preserving aspect ratio
        screen = QApplication.primaryScreen().availableGeometry()
        max_w  = int(screen.width()  * 0.85)
        max_h  = int(screen.height() * 0.85)
        scale  = min(1.0, max_w / w, max_h / h)
        self.resize(int(w * scale), int(h * scale))

        layer_tag = f"  [layer: {preset_layer}]" if preset_layer else ""
        self.setWindowTitle(
            f"{self.TITLE}  [{index + 1}/{total}]  {image_path.name}{layer_tag}"
        )

        self._viewer.set_image(self.original)
        self._viewer.set_crosshair_visible(False)
        self._viewer.imageClicked.connect(self._on_click)
        self._update_ui()

    # ------------------------------------------------------------------
    # Run — blocking via nested QEventLoop
    # ------------------------------------------------------------------

    def run(self) -> tuple:
        """Show window and block until the user finishes, skips, or quits."""
        self._loop = QEventLoop()
        self.show()
        # When the layer is already known, skip straight to corner selection.
        if self._preset_layer:
            self._set_phase(_Phase.CORNERS)
        self._loop.exec()
        self.hide()
        return self.result_layer, self.result_cal

    # ------------------------------------------------------------------
    # Phase transitions
    # ------------------------------------------------------------------

    def _set_phase(self, phase: _Phase) -> None:
        self.phase = phase
        if phase in (_Phase.REFPTS, _Phase.SUMMARY) and self._warped is not None:
            self._viewer.set_image(self._warped)
        elif phase in (_Phase.ACCEPT, _Phase.LAYER, _Phase.CORNERS):
            self._viewer.set_image(self.original)
        self._update_ui()
        if phase in _TERMINAL_PHASES and self._loop is not None:
            self._loop.quit()

    def _update_ui(self) -> None:
        """Refresh status bar and crosshair visibility for the current phase."""
        p = self.phase
        if p == _Phase.ACCEPT:
            self._status.showMessage(
                f"Image {self.index + 1}/{self.total}: {self.image_path.name}"
                "  |  [Y] Use   [N] Skip   [Q] Quit all"
            )
            self._viewer.set_crosshair_visible(False)

        elif p == _Phase.LAYER:
            self._status.showMessage(
                f"Layer: {self._layer_buf}_"
                "  |  [T] top   [B] bottom   or type a label + [Enter]"
            )
            self._viewer.set_crosshair_visible(False)

        elif p == _Phase.CORNERS:
            n   = len(self._corners)
            nxt = self.CORNER_SEQ[n] if n < 4 else "—"
            self._status.showMessage(
                f"Click board corners  TL → TR → BR → BL  |  next: {nxt}  ({n}/4)"
                "  |  [Backspace] undo   [R] redo all   [Enter] confirm (after 4)"
            )
            self._viewer.set_crosshair_visible(True)

        elif p == _Phase.REFPTS:
            n = len(self._refs)
            self._status.showMessage(
                f"Click 2 reference points {self.ref_mm} mm apart  ({n}/2)"
                "  |  [Backspace] undo   [Enter] confirm (after 2)"
            )
            self._viewer.set_crosshair_visible(True)

        elif p == _Phase.SUMMARY:
            self._status.showMessage(
                f"Layer: {self.result_layer}   "
                f"px/mm: {self._px_per_mm:.2f}   "
                f"Warp: {self._warp_size[0]}×{self._warp_size[1]} px"
                "  |  [S] Save   [R] Redo corners   [N] Discard"
            )
            self._viewer.set_crosshair_visible(False)

    # ------------------------------------------------------------------
    # Overlay management
    # ------------------------------------------------------------------

    def _add_items(self, items: list) -> None:
        self._overlay_items.extend(items)

    def _clear_overlays(self) -> None:
        scene = self._viewer.scene()
        for item in self._overlay_items:
            scene.removeItem(item)
        self._overlay_items.clear()

    def _redraw_corners(self) -> None:
        """Redraw all placed corners and the connecting polyline."""
        self._clear_overlays()
        scene = self._viewer.scene()
        for i, c in enumerate(self._corners):
            self._add_items(self._draw_corner(scene, c[0], c[1], self.CORNER_SEQ[i]))
        pts = [(c[0], c[1]) for c in self._corners]
        if len(pts) == 4:
            self._add_items(self._draw_polyline(scene, pts, closed=True))
        elif len(pts) >= 2:
            self._add_items(self._draw_polyline(scene, pts, closed=False))

    def _redraw_refs(self) -> None:
        """Redraw all placed ref points and the connecting line."""
        self._clear_overlays()
        scene = self._viewer.scene()
        for i, r in enumerate(self._refs):
            self._add_items(self._draw_ref_point(scene, r[0], r[1], f"P{i + 1}"))
        if len(self._refs) == 2:
            r0, r1 = self._refs[0], self._refs[1]
            self._add_items(
                self._draw_polyline(scene, [(r0[0], r0[1]), (r1[0], r1[1])])
            )

    # ------------------------------------------------------------------
    # Click handler (QPointF already in image-pixel coords via mapToScene)
    # ------------------------------------------------------------------

    def _on_click(self, pt: QPointF) -> None:
        x, y = int(pt.x()), int(pt.y())
        if self.phase == _Phase.CORNERS and len(self._corners) < 4:
            self._corners.append([x, y])
            self._redraw_corners()
            self._update_ui()

        elif self.phase == _Phase.REFPTS and len(self._refs) < 2:
            self._refs.append([x, y])
            self._redraw_refs()
            if len(self._refs) == 2:
                ppm = compute_px_per_mm(self._refs[0], self._refs[1], self.ref_mm)
                self._status.showMessage(
                    f"2 points placed — {ppm:.2f} px/mm"
                    "  |  [Enter] confirm   [Backspace] undo"
                )
            else:
                self._update_ui()

    # ------------------------------------------------------------------
    # Key handler
    # ------------------------------------------------------------------

    def keyPressEvent(self, event) -> None:  # type: ignore[override]
        key = event.key()
        p   = self.phase

        if p == _Phase.ACCEPT:
            if key == Qt.Key.Key_Y:
                self._set_phase(_Phase.LAYER)
            elif key == Qt.Key.Key_N:
                self._set_phase(_Phase.SKIP)
            elif key == Qt.Key.Key_Q:
                self.quit_all = True
                self._set_phase(_Phase.QUIT)

        elif p == _Phase.LAYER:
            if key == Qt.Key.Key_T and not self._layer_buf:
                self.result_layer = "top"
                self._set_phase(_Phase.CORNERS)
            elif key == Qt.Key.Key_B and not self._layer_buf:
                self.result_layer = "bottom"
                self._set_phase(_Phase.CORNERS)
            elif key in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
                self.result_layer = self._layer_buf.strip() or "top"
                self._layer_buf   = ""
                self._set_phase(_Phase.CORNERS)
            elif key == Qt.Key.Key_Backspace:
                self._layer_buf = self._layer_buf[:-1]
                self._update_ui()
            else:
                ch = event.text()
                if ch.isprintable() and ch:
                    self._layer_buf += ch
                    self._update_ui()

        elif p == _Phase.CORNERS:
            if key == Qt.Key.Key_Backspace and self._corners:
                self._corners.pop()
                self._redraw_corners()
                self._update_ui()
            elif key == Qt.Key.Key_R:
                self._corners.clear()
                self._clear_overlays()
                self._update_ui()
            elif key in (Qt.Key.Key_Return, Qt.Key.Key_Enter) and len(self._corners) == 4:
                self._build_warp()
                self._clear_overlays()
                self._set_phase(_Phase.REFPTS)

        elif p == _Phase.REFPTS:
            if key == Qt.Key.Key_Backspace and self._refs:
                self._refs.pop()
                self._redraw_refs()
                self._update_ui()
            elif key in (Qt.Key.Key_Return, Qt.Key.Key_Enter) and len(self._refs) == 2:
                self._px_per_mm = compute_px_per_mm(
                    self._refs[0], self._refs[1], self.ref_mm
                )
                self._set_phase(_Phase.SUMMARY)

        elif p == _Phase.SUMMARY:
            if key == Qt.Key.Key_S:
                self.result_cal = make_layer_calibration(
                    source_image=self.image_path.name,
                    corners_px=self._corners,
                    warp_matrix=self._warp_M,
                    warped_size=self._warp_size,
                    px_per_mm=self._px_per_mm,
                    ref_points_warped_px=self._refs,
                    ref_distance_mm=self.ref_mm,
                )
                self._set_phase(_Phase.DONE)
            elif key == Qt.Key.Key_R:
                self._corners.clear()
                self._refs.clear()
                self._clear_overlays()
                self._set_phase(_Phase.CORNERS)
            elif key == Qt.Key.Key_N:
                self._set_phase(_Phase.SKIP)

        else:
            super().keyPressEvent(event)

    # ------------------------------------------------------------------
    # Perspective warp
    # ------------------------------------------------------------------

    def _build_warp(self) -> None:
        np  = self._np
        cv2 = self._cv2
        M_list, size    = compute_homography(self._corners)
        M_np            = np.array(M_list, dtype=np.float64)
        self._warped    = cv2.warpPerspective(self.original, M_np, tuple(size))
        self._warp_M    = M_list
        self._warp_size = size

    # ------------------------------------------------------------------
    # Window close
    # ------------------------------------------------------------------

    def closeEvent(self, event) -> None:
        if self._loop and self._loop.isRunning():
            self.quit_all = True
            self._loop.quit()
        super().closeEvent(event)



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
# Coordinate calibration diagnostic (PyQt6)
# ---------------------------------------------------------------------------

def run_coord_calibration(img_w: int = 1600, img_h: int = 900) -> None:
    """
    Diagnostic tool for verifying that QGraphicsView.mapToScene() correctly maps
    window mouse coordinates to image-pixel coordinates on this platform.

    The test image has two sets of targets:

      CYAN ⊕ (click targets)   — click the centre; stdout prints image coords
                                 and pixel error vs the known position.
                                 ~0 px error means mapToScene() is correct.

      ORANGE □ (hover targets) — hover over each; the crosshair should land on
                                 the square.  If not, report the platform issue.

    Close the window to print a summary.
    """
    if not _PYQT6:
        print("PyQt6 required: pip install PyQt6")
        return
    try:
        import cv2
        import numpy as np
    except ImportError:
        print("opencv-python required: pip install opencv-python")
        return

    from r1mx_gui import ImageViewer, draw_crosshair as _static_xhair

    click_targets = [
        (0,               0),
        (img_w - 1,       0),
        (img_w - 1,       img_h - 1),
        (0,               img_h - 1),
        (img_w // 2,      img_h // 2),
        (img_w // 4,      img_h // 4),
        (3 * img_w // 4,  img_h // 4),
        (img_w // 4,      3 * img_h // 4),
        (3 * img_w // 4,  3 * img_h // 4),
    ]
    xhair_targets = [
        (img_w // 2,      0),
        (img_w - 1,       img_h // 2),
        (img_w // 2,      img_h - 1),
        (0,               img_h // 2),
        (img_w // 3,      img_h // 3),
        (2 * img_w // 3,  img_h // 3),
        (img_w // 3,      2 * img_h // 3),
        (2 * img_w // 3,  2 * img_h // 3),
    ]

    # ── Instructions ─────────────────────────────────────────────────────────
    print()
    print("════════════════════════════════════════════════════════════════════")
    print("  COORDINATE CALIBRATION DIAGNOSTIC  (PyQt6)")
    print("════════════════════════════════════════════════════════════════════")
    print()
    print("  Coordinate mapping: QGraphicsView.mapToScene(event.pos())")
    print()
    print(f"  Image: {img_w}×{img_h}")
    print(f"  Click targets (cyan ⊕):       {click_targets}")
    print(f"  Crosshair targets (orange □):  {xhair_targets}")
    print()
    print("  ── STEP 1: Hover over ORANGE □ targets ─────────────────────────")
    print("  The crosshair should visually land on the orange square.")
    print("  If it does not, mapToScene() has a platform-specific issue.")
    print()
    print("  ── STEP 2: Click CYAN ⊕ targets ────────────────────────────────")
    print("  Click the exact centre of each cyan crosshair marker.")
    print("  stdout prints the image-pixel result and error vs the known position.")
    print("    • ~0 px error → mapToScene() is correct")
    print("    • Large error → report this; a workaround will be needed")
    print()
    print("  Close the window to print a summary.")
    print("════════════════════════════════════════════════════════════════════")
    print()

    # ── Build synthetic test image (numpy BGR) ────────────────────────────────
    img = np.full((img_h, img_w, 3), 40, dtype=np.uint8)
    for x in range(0, img_w, img_w // 8):
        cv2.line(img, (x, 0), (x, img_h - 1), (70, 70, 70), 1)
    for y in range(0, img_h, img_h // 6):
        cv2.line(img, (0, y), (img_w - 1, y), (70, 70, 70), 1)

    # ── Qt window ────────────────────────────────────────────────────────────
    app    = QApplication.instance() or QApplication(sys.argv)
    viewer = ImageViewer()
    viewer.setWindowTitle("r1mx Coord Calibration")
    viewer.resize(min(img_w, 1400), min(img_h, 800))
    viewer.set_image(img)
    viewer.set_crosshair_visible(True)

    scene    = viewer.scene()
    sq_half  = max(8, img_w // 80)

    # Draw orange □ hover targets
    for tx, ty in xhair_targets:
        rect = QGraphicsRectItem(tx - sq_half, ty - sq_half, sq_half * 2, sq_half * 2)
        rect.setPen(QPen(QColor(255, 140, 0), 3))
        rect.setZValue(3)
        scene.addItem(rect)
        lbl = QGraphicsTextItem(f"({tx},{ty})")
        lbl.setDefaultTextColor(QColor(255, 180, 0))
        lbl.setPos(tx + sq_half + 4, ty - 10)
        lbl.setZValue(3)
        scene.addItem(lbl)

    # Draw cyan ⊕ click targets (static crosshairs)
    arm = max(12, img_w // 100)
    for tx, ty in click_targets:
        _static_xhair(scene, tx, ty, color=QColor(0, 255, 255), arm=arm)
        lbl = QGraphicsTextItem(f"({tx},{ty})")
        lbl.setDefaultTextColor(QColor(0, 220, 220))
        lbl.setPos(tx + arm + 4, ty - 10)
        lbl.setZValue(3)
        scene.addItem(lbl)

    click_errors: list[float] = []

    def on_click(pt: QPointF) -> None:
        x, y    = pt.x(), pt.y()
        nearest = min(click_targets, key=lambda t: (t[0] - x) ** 2 + (t[1] - y) ** 2)
        tx_exp, ty_exp = nearest
        err = math.sqrt((x - tx_exp) ** 2 + (y - ty_exp) ** 2)
        click_errors.append(err)
        print(
            f"[CLICK]  image=({x:7.1f},{y:7.1f})"
            f"  expected=({tx_exp:5d},{ty_exp:5d})"
            f"  err={err:6.2f} px",
            flush=True,
        )

    viewer.imageClicked.connect(on_click)

    loop = QEventLoop()

    class _Win(QMainWindow):
        def closeEvent(self, event):          # type: ignore[override]
            loop.quit()
            super().closeEvent(event)

    win = _Win()
    win.setCentralWidget(viewer)
    win.setWindowTitle("r1mx Coord Calibration")
    win.resize(min(img_w, 1400), min(img_h, 800))
    win.show()
    loop.exec()

    # ── Summary ──────────────────────────────────────────────────────────────
    print()
    print("════════════════════════════════════════════════════════════════════")
    print("  RESULTS SUMMARY")
    print("════════════════════════════════════════════════════════════════════")
    if click_errors:
        avg = sum(click_errors) / len(click_errors)
        worst = max(click_errors)
        print(f"  Clicks: {len(click_errors)}   avg error: {avg:.2f} px   worst: {worst:.2f} px")
        if avg < 2.0:
            print("  ✓ mapToScene() is correct on this platform.")
        else:
            print("  ✗ Large error — mapToScene() may have a platform-specific issue.")
            print("    Please report: avg error, OS, display scale factor.")
    else:
        print("  No clicks recorded.  Click the cyan ⊕ targets to measure error.")
    print("════════════════════════════════════════════════════════════════════")
    print()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Interactive per-layer PCB photo calibration with perspective correction."
    )
    parser.add_argument("--board", default="", metavar="NAME",
                        help="Board folder name under components/ (required unless --calibrate)")
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
    parser.add_argument("--calibrate", action="store_true",
                        help="Coordinate calibration diagnostic: show a synthetic test image "
                             "with targets at known pixel positions; click each target and "
                             "read the stdout coordinate report to verify/fix the math.")
    parser.add_argument("--calibrate-size", default="1600x900", metavar="WxH",
                        help="Size of synthetic test image for --calibrate (default: 1600x900)")
    args = parser.parse_args()

    # --calibrate runs standalone, no --board required
    if args.calibrate:
        try:
            cw, ch = (int(v) for v in args.calibrate_size.lower().split("x"))
        except ValueError:
            print("--calibrate-size must be WxH, e.g. 1600x900")
            sys.exit(1)
        run_coord_calibration(cw, ch)
        return

    board_dir = COMPONENTS_DIR / args.board
    if not args.board:
        log.error("--board is required (or use --calibrate for the coordinate diagnostic)")
        sys.exit(1)
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

