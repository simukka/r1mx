"""ScanLayerWorker — unified QThread for all single-feature PCB layer scans.

Dispatches to the appropriate analysis function based on *scan_type*:

    "text"    → scan.process_warped_image()      (OCR)
    "vias"    → layers.process_vias()
    "pads"    → layers.process_pads()
    "traces"  → layers.process_traces()
    "outline" → layers.process_outline()

Emits
-----
signals.line(str)            — progress messages for the log panel
scan_layer_done(list)        — result items (type-dependent, see below)
signals.finished(bool, str)  — success flag + summary message

Result item format per scan_type
---------------------------------
"text"    : list of BomEntry (from scan.py)
"vias"    : list of {x_mm, y_mm, drill_mm, annular_mm}
"pads"    : list of {x_mm, y_mm, w_mm, h_mm, rotation_deg, layer, ref}
"traces"  : list of {start, end, width_mm, layer}
"outline" : list of [x_mm, y_mm] (corner points)
"""
from __future__ import annotations

import json

import cv2
import numpy as np
from PyQt6.QtCore import QThread, pyqtSignal

from toolkit.analysis import layers as _layers
from toolkit.analysis import scan as _scan
from toolkit.db import DB
from toolkit.paths import REPO_ROOT
from toolkit.workers.base import WorkerSignals

SCAN_TYPES = ("text", "vias", "pads", "traces", "outline")


class ScanLayerWorker(QThread):
    """Run a single-feature PCB scan in a background thread.

    Parameters
    ----------
    board_name : str
    layer_name : str
    scan_type  : one of SCAN_TYPES
    opts       : dict — scan-type-specific options (see module docstring)
    """

    scan_layer_done = pyqtSignal(list)

    def __init__(
        self,
        board_name: str,
        layer_name: str,
        scan_type: str,
        opts: dict,
        parent=None,
    ):
        super().__init__(parent)
        self._board_name = board_name
        self._layer_name = layer_name
        self._scan_type  = scan_type
        self._opts       = opts
        self.signals     = WorkerSignals()

    # ------------------------------------------------------------------
    def run(self):
        try:
            bgr, px_per_mm, kicad_layer = self._load_warped_image()
        except Exception as exc:
            self.signals.finished.emit(False, str(exc))
            return

        try:
            items = self._dispatch(bgr, px_per_mm, kicad_layer)
        except Exception as exc:
            import traceback
            self.signals.line.emit(traceback.format_exc())
            self.signals.finished.emit(False, str(exc))
            return

        self.scan_layer_done.emit(items)
        self.signals.finished.emit(True, self._summary(items))

    # ------------------------------------------------------------------
    def _load_warped_image(self) -> tuple[np.ndarray, float, str]:
        """Load the calibrated, perspective-corrected board image."""
        db = DB()
        board_id  = db.get_or_create_board(self._board_name)
        layer_row = db.get_layer(board_id, self._layer_name)
        if not layer_row or not layer_row["calibrated"]:
            raise RuntimeError(
                f"Layer {self._board_name}/{self._layer_name} is not calibrated. "
                "Calibrate it first before scanning."
            )

        cal         = json.loads(layer_row["calibration"] or "{}")
        warp_matrix = cal.get("warp_matrix")
        warped_size = cal.get("warped_size")
        px_per_mm   = cal.get("px_per_mm", 20.0)
        source_img  = layer_row["source_image"] or ""

        img_path = REPO_ROOT / "components" / self._board_name / source_img
        if not img_path.exists():
            raise FileNotFoundError(f"Source image not found: {img_path}")

        bgr = cv2.imread(str(img_path))
        if bgr is None:
            raise RuntimeError(f"Cannot read image: {img_path}")

        if warp_matrix and warped_size:
            M      = np.array(warp_matrix, dtype=np.float64)
            width, height = warped_size
            bgr    = cv2.warpPerspective(bgr, M, (width, height))

        # Bottom layer is stored flipped so KiCad coords are front-relative
        kicad_layer = "F_Cu" if self._layer_name == "top" else "B_Cu"
        if self._layer_name == "bottom":
            bgr = cv2.flip(bgr, 1)

        return bgr, px_per_mm, kicad_layer

    # ------------------------------------------------------------------
    def _dispatch(
        self,
        bgr: np.ndarray,
        px_per_mm: float,
        kicad_layer: str,
    ) -> list:
        t    = self._scan_type
        opts = self._opts
        prog = self.signals.line.emit

        if t == "text":
            prog("Starting OCR scan …")
            return _scan.process_warped_image(
                bgr,
                board_name=self._board_name,
                layer_name=self._layer_name,
                px_per_mm=px_per_mm,
                engine=opts.get("engine", "easyocr"),
                min_confidence=opts.get("min_confidence", 0.35),
                tile_size=opts.get("tile_size", 512),
                tile_overlap=opts.get("tile_overlap", 100),
                gpu=opts.get("gpu", False),
                progress_cb=prog,
            )

        hsv_cfg = opts.get("hsv_cfg") or {}

        if t == "vias":
            prog("Scanning for vias …")
            return _layers.process_vias(bgr, px_per_mm, hsv_cfg, progress_cb=prog)

        if t == "pads":
            prog("Scanning for pads …")
            vias = opts.get("vias") or []
            return _layers.process_pads(bgr, px_per_mm, hsv_cfg,
                                        kicad_layer=kicad_layer,
                                        vias=vias, progress_cb=prog)

        if t == "traces":
            prog("Scanning for traces …")
            vias = opts.get("vias") or []
            return _layers.process_traces(bgr, px_per_mm, hsv_cfg,
                                          kicad_layer=kicad_layer,
                                          vias=vias, progress_cb=prog)

        if t == "outline":
            prog("Scanning for board outline …")
            return _layers.process_outline(
                bgr, px_per_mm,
                canny_low=opts.get("canny_low", 30),
                canny_high=opts.get("canny_high", 100),
                progress_cb=prog,
            )

        raise ValueError(f"Unknown scan_type: {t!r}")

    # ------------------------------------------------------------------
    def _summary(self, items: list) -> str:
        n = len(items)
        labels = {
            "text":    f"{n} text items",
            "vias":    f"{n} vias",
            "pads":    f"{n} pads",
            "traces":  f"{n} trace segments",
            "outline": f"outline with {n} corner points",
        }
        return labels.get(self._scan_type, f"{n} items")
