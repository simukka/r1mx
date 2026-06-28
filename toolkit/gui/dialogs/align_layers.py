"""align_layers.py — manual cross-layer alignment via through-feature point-pairs.

The user clicks the same physical vias / mounting-holes on two layers
(reference + target).  We fit a 2x3 affine transform (which naturally recovers
the back side's X-mirror, plus scale and rotation) mapping the **target**
layer's warped-pixel coordinates into the **reference** layer's frame, and
store it on the target layer via :meth:`DB.save_layer_alignment`.

Once stored, ``LayerScene.set_board_transform`` registers the layers so they
share a coordinate frame — vias and holes line up across layers, layer switches
preserve the view, and one layer can ghost over another as an overlay.
"""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

import cv2
import numpy as np
from PyQt6.QtCore import QPointF, Qt
from PyQt6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from toolkit.db import DB
from toolkit.gui.viewer import ImageViewer, draw_ref_point

# A click within this many mm of a via centre snaps to that via.
_SNAP_TOL_MM = 1.0
# Minimum point-pairs needed to fit a 2x3 affine.
_MIN_PAIRS = 3


def load_layer_warped(db: DB, board: str, layer_name: str) -> tuple[np.ndarray | None, float]:
    """Return ``(warped_bgr, px_per_mm)`` for a calibrated layer.

    Mirrors the warp path in ``LayerScene.load_photo`` so the picked pixel
    coordinates match the scene coordinates used for rendering.  Returns
    ``(None, 0.0)`` when the layer has no usable image.
    """
    board_id = db.get_or_create_board(board)
    row = db.get_layer(board_id, layer_name)
    if not row or not row["source_image"]:
        return None, 0.0
    cal = json.loads(row["calibration"]) if row["calibration"] else {}
    img_path = Path(db.get_board_abs_dir(board)) / row["source_image"]
    if not img_path.exists():
        return None, 0.0
    img = cv2.imread(str(img_path))
    if img is None:
        return None, 0.0
    warp_matrix = cal.get("warp_matrix") if row["calibrated"] else None
    warped_size = cal.get("warped_size")
    if warp_matrix and warped_size:
        M = np.array(warp_matrix, dtype=np.float64)
        w, h = warped_size
        img = cv2.warpPerspective(img, M, (w, h))
    return img, float(cal.get("px_per_mm", 20.0))


class _PickPane(QWidget):
    """One labelled ImageViewer that snaps clicks to nearby via objects."""

    def __init__(self, db: DB, board: str, layer: str, parent=None):
        super().__init__(parent)
        self.db = db
        self.board = board
        self.layer = layer
        self.px_per_mm = 0.0
        self.layer_id: int | None = None
        self._markers: list = []

        v = QVBoxLayout(self)
        v.setContentsMargins(0, 0, 0, 0)
        self._title = QLabel(layer)
        self._title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        v.addWidget(self._title)
        self.viewer = ImageViewer(self)
        v.addWidget(self.viewer, 1)

        row = db.get_layer(db.get_or_create_board(board), layer)
        self.layer_id = int(row["id"]) if row else None
        self.set_layer(layer)

    def set_layer(self, layer: str) -> None:
        self.layer = layer
        self._title.setText(f"{self.board} / {layer}")
        row = self.db.get_layer(self.db.get_or_create_board(self.board), layer)
        self.layer_id = int(row["id"]) if row else None
        img, ppm = load_layer_warped(self.db, self.board, layer)
        self.px_per_mm = ppm
        self.clear_markers()
        if img is not None:
            self.viewer.set_image(img)

    def snap(self, sp: QPointF) -> QPointF:
        """Snap a clicked scene point to the nearest via centre, if close."""
        if not self.layer_id or self.px_per_mm <= 0:
            return sp
        x_mm = sp.x() / self.px_per_mm
        y_mm = sp.y() / self.px_per_mm
        hits = self.db.objects_at_mm(self.layer_id, x_mm, y_mm, _SNAP_TOL_MM)
        vias = [o for o in hits if o["type"] == "via"]
        if vias:
            v = vias[0]
            return QPointF(v["x_mm"] * self.px_per_mm, v["y_mm"] * self.px_per_mm)
        return sp

    def add_marker(self, sp: QPointF, label: str) -> None:
        self._markers.extend(
            draw_ref_point(self.viewer.scene(), sp.x(), sp.y(), label)
        )

    def pop_marker(self) -> None:
        # draw_ref_point adds 2 items (dot + label) per call
        for _ in range(2):
            if self._markers:
                self.viewer.scene().removeItem(self._markers.pop())

    def clear_markers(self) -> None:
        for it in self._markers:
            self.viewer.scene().removeItem(it)
        self._markers = []


class AlignLayersDialog(QDialog):
    """Pick corresponding vias/holes on two layers and store the affine fit."""

    def __init__(self, db: DB, board: str, target_layer: str, parent=None):
        super().__init__(parent)
        self.db = db
        self.board = board
        self.setWindowTitle(f"Align layers — {board}")
        self.resize(1100, 720)

        board_id = db.get_or_create_board(board)
        layers = [l["name"] for l in db.list_layers(board_id) if l["calibrated"]]
        # Default reference = first calibrated layer that isn't the target.
        ref_default = next((l for l in layers if l != target_layer), None)

        # Collected (ref_px, tgt_px) pairs and which side we expect next.
        self._pairs: list[tuple[tuple[float, float], tuple[float, float]]] = []
        self._pending_ref: tuple[float, float] | None = None

        outer = QVBoxLayout(self)

        # Reference-layer selector
        top = QHBoxLayout()
        top.addWidget(QLabel("Reference layer:"))
        self._ref_combo = QComboBox()
        self._ref_combo.addItems([l for l in layers if l != target_layer])
        if ref_default:
            self._ref_combo.setCurrentText(ref_default)
        self._ref_combo.currentTextChanged.connect(self._on_ref_changed)
        top.addWidget(self._ref_combo)
        top.addStretch(1)
        outer.addLayout(top)

        self._instr = QLabel()
        outer.addWidget(self._instr)

        panes = QHBoxLayout()
        self._ref_pane = _PickPane(db, board, ref_default or target_layer)
        self._tgt_pane = _PickPane(db, board, target_layer)
        panes.addWidget(self._ref_pane, 1)
        panes.addWidget(self._tgt_pane, 1)
        outer.addLayout(panes, 1)

        self._ref_pane.viewer.imageClicked.connect(self._on_ref_click)
        self._tgt_pane.viewer.imageClicked.connect(self._on_tgt_click)

        # Controls
        ctl = QHBoxLayout()
        self._undo_btn = QPushButton("Undo last pair")
        self._undo_btn.clicked.connect(self._undo)
        self._clear_btn = QPushButton("Clear all")
        self._clear_btn.clicked.connect(self._clear)
        ctl.addWidget(self._undo_btn)
        ctl.addWidget(self._clear_btn)
        ctl.addStretch(1)
        outer.addLayout(ctl)

        self._buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save
            | QDialogButtonBox.StandardButton.Cancel
        )
        self._buttons.accepted.connect(self._save)
        self._buttons.rejected.connect(self.reject)
        outer.addWidget(self._buttons)

        self._update_state()

    # ── Reference selection ──────────────────────────────────────────────────

    def _on_ref_changed(self, name: str) -> None:
        if not name:
            return
        self._ref_pane.set_layer(name)
        self._clear()

    # ── Click handling ───────────────────────────────────────────────────────

    def _on_ref_click(self, sp: QPointF) -> None:
        if self._pending_ref is not None:
            return  # already have a ref click; expecting the target click
        sp = self._ref_pane.snap(sp)
        self._pending_ref = (sp.x(), sp.y())
        self._ref_pane.add_marker(sp, str(len(self._pairs) + 1))
        self._update_state()

    def _on_tgt_click(self, sp: QPointF) -> None:
        if self._pending_ref is None:
            return  # click the reference point first
        sp = self._tgt_pane.snap(sp)
        self._tgt_pane.add_marker(sp, str(len(self._pairs) + 1))
        self._pairs.append((self._pending_ref, (sp.x(), sp.y())))
        self._pending_ref = None
        self._update_state()

    def _undo(self) -> None:
        if self._pending_ref is not None:
            self._pending_ref = None
            self._ref_pane.pop_marker()
        elif self._pairs:
            self._pairs.pop()
            self._ref_pane.pop_marker()
            self._tgt_pane.pop_marker()
        self._update_state()

    def _clear(self) -> None:
        self._pairs = []
        self._pending_ref = None
        self._ref_pane.clear_markers()
        self._tgt_pane.clear_markers()
        self._update_state()

    # ── State / fit ──────────────────────────────────────────────────────────

    def _fit(self):
        """Return ``(M_2x3, rms)`` for the current pairs, or ``(None, None)``."""
        if len(self._pairs) < _MIN_PAIRS:
            return None, None
        ref = np.array([p[0] for p in self._pairs], dtype=np.float64)
        tgt = np.array([p[1] for p in self._pairs], dtype=np.float64)
        M, _ = cv2.estimateAffine2D(tgt, ref)
        if M is None:
            return None, None
        proj = (M[:, :2] @ tgt.T).T + M[:, 2]
        rms = float(np.sqrt(np.mean(np.sum((proj - ref) ** 2, axis=1))))
        return M, rms

    def _update_state(self) -> None:
        n = len(self._pairs)
        if self._pending_ref is None:
            step = f"click via #{n + 1} on the REFERENCE (left) layer"
        else:
            step = f"now click the SAME via on the TARGET (right) layer"
        M, rms = self._fit()
        rms_txt = f"   residual RMS = {rms:.2f} px" if rms is not None else ""
        self._instr.setText(
            f"Pairs: {n} (need ≥{_MIN_PAIRS}) — {step}.{rms_txt}"
        )
        self._buttons.button(
            QDialogButtonBox.StandardButton.Save
        ).setEnabled(M is not None)

    def _save(self) -> None:
        M, rms = self._fit()
        if M is None:
            QMessageBox.warning(
                self, "Not enough pairs",
                f"Pick at least {_MIN_PAIRS} via/hole correspondences first.",
            )
            return
        if self._tgt_pane.layer_id is None or self._ref_pane.layer_id is None:
            QMessageBox.warning(self, "Missing layer", "Layer not found.")
            return
        alignment = {
            "ref_layer": self._ref_pane.layer,
            "matrix": M.tolist(),
            "pairs": {
                "ref": [list(p[0]) for p in self._pairs],
                "tgt": [list(p[1]) for p in self._pairs],
            },
            "rms_px": rms,
            "created_at": datetime.now().isoformat(),
        }
        self.db.save_layer_alignment(self._tgt_pane.layer_id, alignment)
        # The reference layer defines the board frame → identity.
        self.db.save_layer_alignment(self._ref_pane.layer_id, None)
        self.accept()
