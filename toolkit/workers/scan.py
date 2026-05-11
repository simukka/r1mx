"""Board scan worker."""
from __future__ import annotations

import json

import cv2
import numpy as np
from PyQt6.QtCore import QThread, pyqtSignal

from toolkit.analysis.scan import process_warped_image
from toolkit.db import DB
from toolkit.paths import COMPONENTS_DIR
from toolkit.workers.base import WorkerSignals

class ScanBoardWorker(QThread):
    """Run extract_bom.process_warped_image() in-process for the active layer.

    The source image is perspective-warped using the layer calibration before
    OCR so that returned mm coordinates are in the calibrated coordinate space.

    Emits:
        signals.line(str)          — progress messages
        signals.scan_done(list)    — list of BomEntry namedtuples
        signals.finished(ok, msg)
    """

    scan_done = pyqtSignal(list)

    def __init__(self, board_name: str, layer_name: str, opts: dict, parent=None):
        super().__init__(parent)
        self._board_name = board_name
        self._layer_name = layer_name
        self._opts = opts          # keys: engine, min_confidence, tile_size, tile_overlap, gpu, scan_refs, scan_parts
        self.signals = WorkerSignals()

    def run(self):
        """Run OCR for the active calibrated board layer."""
        try:
            db = DB()
            board_id = db.get_or_create_board(self._board_name)
            layer_row = db.get_layer(board_id, self._layer_name)
            if not layer_row or not layer_row["calibrated"]:
                self.signals.finished.emit(False, "Layer not calibrated")
                return

            cal = json.loads(layer_row["calibration"] or "{}")
            warp_matrix = cal.get("warp_matrix")
            warped_size = cal.get("warped_size")
            px_per_mm = cal.get("px_per_mm", 20.0)
            source_image = layer_row["source_image"] or ""

            img_path = COMPONENTS_DIR / self._board_name / source_image
            if not img_path.exists():
                self.signals.finished.emit(False, f"Image not found: {img_path}")
                return

            bgr = cv2.imread(str(img_path))
            if bgr is None:
                self.signals.finished.emit(False, f"Cannot read image: {img_path}")
                return

            if warp_matrix and warped_size:
                matrix = np.array(warp_matrix, dtype=np.float64)
                width, height = warped_size
                bgr = cv2.warpPerspective(bgr, matrix, (width, height))

            entries = process_warped_image(
                bgr,
                board_name=self._board_name,
                layer_name=self._layer_name,
                px_per_mm=px_per_mm,
                engine=self._opts.get("engine", "easyocr"),
                min_confidence=self._opts.get("min_confidence", 0.35),
                tile_size=self._opts.get("tile_size", 512),
                tile_overlap=self._opts.get("tile_overlap", 100),
                gpu=self._opts.get("gpu", False),
                progress_cb=self.signals.line.emit,
            )
            scan_refs = self._opts.get("scan_refs", True)
            scan_parts = self._opts.get("scan_parts", True)
            entries = [
                entry for entry in entries
                if (entry.ref_type != "PartNumber" and scan_refs)
                or (entry.ref_type == "PartNumber" and scan_parts)
            ]
            self.scan_done.emit(entries)
            self.signals.finished.emit(
                True,
                f"{len(entries)} items found ({sum(1 for entry in entries if entry.ref_type != 'PartNumber')} refs)",
            )
        except Exception as exc:
            import traceback

            self.signals.line.emit(traceback.format_exc())
            self.signals.finished.emit(False, str(exc))


