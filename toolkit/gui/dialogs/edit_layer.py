"""Layer editor dialog."""
from __future__ import annotations

import json
from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from toolkit.db import DB
from toolkit.gui.dialogs.image_picker import ImagePickerDialog

_REPO = Path(__file__).resolve().parents[3]

class EditLayerDialog(QDialog):
    """
    Edit all user-modifiable properties of a layer in one place:
      • Layer name
      • Source image (with thumbnail picker)
      • Notes / description

    Changes are saved to r1mx.db on accept.
    """

    def __init__(self, db: DB, board_name: str, layer_name: str, parent=None):
        super().__init__(parent)
        self._db         = db
        self._board_name = board_name
        self._layer_name = layer_name

        self.setWindowTitle(f"Edit layer — {board_name} / {layer_name}")
        self.setMinimumWidth(500)

        board_id  = db.get_or_create_board(board_name)
        layer_row = db.get_layer(board_id, layer_name)

        self._board_id  = board_id
        self._layer_id  = layer_row["id"] if layer_row else None
        self._board_dir = _REPO / "components" / board_name

        cal_data = {}
        if layer_row and layer_row["calibration"]:
            try:
                cal_data = json.loads(layer_row["calibration"])
            except Exception:
                pass

        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        layout.addLayout(form)

        # ── Layer name ─────────────────────────────────────────────────────
        self._name_edit = QLineEdit(layer_name)
        form.addRow("Layer name:", self._name_edit)

        # ── Source image ───────────────────────────────────────────────────
        src = (layer_row["source_image"] or "") if layer_row else ""
        img_row = QWidget()
        img_hl = QHBoxLayout(img_row)
        img_hl.setContentsMargins(0, 0, 0, 0)
        self._image_edit = QLineEdit(src)
        self._image_edit.setReadOnly(True)
        pick_btn = QPushButton("Browse…")
        pick_btn.setFixedWidth(80)
        pick_btn.clicked.connect(self._pick_image)
        img_hl.addWidget(self._image_edit, stretch=1)
        img_hl.addWidget(pick_btn)
        form.addRow("Source image:", img_row)

        # ── Calibration info (read-only summary) ───────────────────────────
        px_mm = cal_data.get("px_per_mm")
        cal_text = (f"{px_mm:.2f} px/mm" if px_mm else "Not calibrated")
        cal_lbl = QLabel(cal_text)
        cal_lbl.setStyleSheet("color: #888;")
        form.addRow("Calibration:", cal_lbl)

        # ── Notes ──────────────────────────────────────────────────────────
        notes_val = (layer_row["notes"] if layer_row and "notes" in layer_row.keys() else "") or ""
        self._notes_edit = QTextEdit()
        self._notes_edit.setPlainText(notes_val)
        self._notes_edit.setFixedHeight(80)
        form.addRow("Notes:", self._notes_edit)

        # ── Buttons ────────────────────────────────────────────────────────
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save |
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self._save)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _pick_image(self):
        dlg = ImagePickerDialog(self._board_dir, self._image_edit.text(), parent=self)
        if dlg.exec() == QDialog.DialogCode.Accepted and dlg.selected_file:
            self._image_edit.setText(dlg.selected_file)

    def _save(self):
        new_name  = self._name_edit.text().strip()
        new_image = self._image_edit.text().strip()
        new_notes = self._notes_edit.toPlainText().strip()

        if not new_name:
            QMessageBox.warning(self, "Validation", "Layer name cannot be empty.")
            return

        conn = self._db.conn()

        if self._layer_id is None:
            # Layer doesn't exist yet in DB — create it
            self._layer_id = self._db.get_or_create_layer(self._board_id, new_name)

        # Update name + source_image
        try:
            conn.execute(
                "UPDATE layers SET name=?, source_image=? WHERE id=?",
                (new_name, new_image or None, self._layer_id),
            )
        except Exception:
            # 'notes' column may not exist yet in older DBs — ignore gracefully
            pass

        # Update notes if column exists
        try:
            conn.execute(
                "UPDATE layers SET notes=? WHERE id=?",
                (new_notes or None, self._layer_id),
            )
        except Exception:
            pass

        conn.commit()
        self.accept()

