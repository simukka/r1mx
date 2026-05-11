"""Inspector panel — editable component details with verify + draw-outline actions."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QProgressBar,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from toolkit.db import DB


class InspectorPanel(QWidget):
    """Right dock: editable component/entity details.

    Signals
    -------
    drawOutlineRequested(int)
        Emitted when the user clicks "✎ Draw outline". The argument is the
        object_id whose bounding box should be (re)drawn on the canvas.
    """

    drawOutlineRequested      = pyqtSignal(int)   # object_id
    refineScaleRequested      = pyqtSignal(int)   # object_id
    datasheetSearchRequested  = pyqtSignal(int, str, str)
    """Emitted when the user clicks "Find on filesystem…" or "Find online…".

    Arguments: (object_id, part_number, mode)
    where mode is ``"filesystem"`` or ``"internet"``.
    """

    def __init__(self, db: DB, parent=None):
        super().__init__(parent)
        self._db = db
        self._component_id: int | None = None
        self._object_id: int | None = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(6)

        title = QLabel("Inspector")
        title.setFont(QFont("sans-serif", 10, QFont.Weight.Bold))
        layout.addWidget(title)

        # ── Confidence / verified row ────────────────────────────────────────
        conf_row = QHBoxLayout()
        conf_lbl = QLabel("Confidence:")
        conf_lbl.setStyleSheet("font-size: 11px;")
        conf_row.addWidget(conf_lbl)
        self._conf_bar = QProgressBar()
        self._conf_bar.setRange(0, 100)
        self._conf_bar.setValue(0)
        self._conf_bar.setMaximumHeight(14)
        self._conf_bar.setTextVisible(True)
        self._conf_bar.setFormat("%p%")
        conf_row.addWidget(self._conf_bar, stretch=1)
        layout.addLayout(conf_row)

        # ── Editable fields ──────────────────────────────────────────────────
        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        form.setVerticalSpacing(4)

        self._ref   = self._make_field("ref_designator",  form, "Ref:")
        self._part  = self._make_field("part_number",     form, "Part:")
        self._mfr   = self._make_field("manufacturer",    form, "Manufacturer:")
        self._value = self._make_field("value",           form, "Value:")
        self._pkg   = self._make_field("package",         form, "Package:")
        layout.addLayout(form)

        # ── Action buttons ───────────────────────────────────────────────────
        btn_row1 = QHBoxLayout()
        self._verify_btn = QPushButton("✓ Verify")
        self._verify_btn.setToolTip("Mark this entity as human-verified")
        self._verify_btn.clicked.connect(self._on_verify)
        btn_row1.addWidget(self._verify_btn)

        self._draw_outline_btn = QPushButton("✎ Draw outline")
        self._draw_outline_btn.setToolTip(
            "Enter canvas rect-draw mode to define/update the component bounding box"
        )
        self._draw_outline_btn.clicked.connect(self._on_draw_outline)
        btn_row1.addWidget(self._draw_outline_btn)
        layout.addLayout(btn_row1)

        btn_row1b = QHBoxLayout()
        self._refine_scale_btn = QPushButton("⇱ Refine scale")
        self._refine_scale_btn.setToolTip(
            "Use this component's known datasheet dimensions to refine the layer's px/mm calibration"
        )
        self._refine_scale_btn.setEnabled(False)
        self._refine_scale_btn.clicked.connect(self._on_refine_scale)
        btn_row1b.addWidget(self._refine_scale_btn)
        btn_row1b.addStretch()
        layout.addLayout(btn_row1b)

        # ── Linked datasheets ────────────────────────────────────────────────
        ds_label = QLabel("Datasheets:")
        ds_label.setFont(QFont("sans-serif", 9, QFont.Weight.Bold))
        layout.addWidget(ds_label)

        self._ds_list = QListWidget()
        self._ds_list.setMaximumHeight(90)
        self._ds_list.setToolTip("Double-click to open PDF")
        self._ds_list.itemDoubleClicked.connect(self._open_datasheet)
        layout.addWidget(self._ds_list)

        # ── Find-datasheet buttons ────────────────────────────────────────────
        ds_btn_row = QHBoxLayout()
        self._ds_fs_btn = QPushButton("📁 Find on filesystem…")
        self._ds_fs_btn.setToolTip("Scan a local folder for PDFs matching this part number")
        self._ds_fs_btn.clicked.connect(lambda: self._emit_datasheet_search("filesystem"))
        ds_btn_row.addWidget(self._ds_fs_btn)

        self._ds_web_btn = QPushButton("🌐 Find online…")
        self._ds_web_btn.setToolTip(
            "Search AllDatasheet, DuckDuckGo, Wayback Machine etc. and download candidates"
        )
        self._ds_web_btn.clicked.connect(lambda: self._emit_datasheet_search("internet"))
        ds_btn_row.addWidget(self._ds_web_btn)
        layout.addLayout(ds_btn_row)

        # ── Notes ────────────────────────────────────────────────────────────
        self._notes = QTextEdit()
        self._notes.setPlaceholderText("Notes…")
        self._notes.setMaximumHeight(70)
        layout.addWidget(self._notes)

        btn_row2 = QHBoxLayout()
        self._save_btn = QPushButton("Save notes")
        self._save_btn.clicked.connect(self._save_notes)
        self._mcp_btn  = QPushButton("Query MCP")
        self._mcp_btn.clicked.connect(self._query_mcp)
        btn_row2.addWidget(self._save_btn)
        btn_row2.addWidget(self._mcp_btn)
        layout.addLayout(btn_row2)

        self._mcp_result = QTextEdit()
        self._mcp_result.setReadOnly(True)
        self._mcp_result.setPlaceholderText("MCP result will appear here…")
        layout.addWidget(self._mcp_result)

        layout.addStretch()
        self._set_enabled(False)

    # ── Field helpers ────────────────────────────────────────────────────────

    def _make_field(self, db_key: str, form: QFormLayout, label: str) -> QLineEdit:
        """Create an editable QLineEdit and wire auto-save on Return key."""
        edit = QLineEdit()
        edit.setPlaceholderText("—")
        edit.setProperty("db_key", db_key)
        edit.returnPressed.connect(lambda _e=edit: self._save_field(_e))
        edit.editingFinished.connect(lambda _e=edit: self._save_field(_e))
        form.addRow(label, edit)
        return edit

    def _save_field(self, edit: QLineEdit) -> None:
        """Persist a changed component field to the DB."""
        if self._component_id is None:
            return
        key = edit.property("db_key")
        val = edit.text().strip() or None
        self._db.conn().execute(
            f"UPDATE components SET {key}=? WHERE id=?",
            (val, self._component_id),
        )
        self._db.conn().commit()
        # Keep label on the object in sync with ref_designator
        if key == "ref_designator" and self._object_id is not None and val:
            self._db.update_object(self._object_id, label=val)

    # ── Enable/disable ───────────────────────────────────────────────────────

    def _set_enabled(self, on: bool):
        for w in (self._notes, self._save_btn, self._mcp_btn,
                  self._verify_btn, self._draw_outline_btn,
                  self._ds_fs_btn, self._ds_web_btn):
            w.setEnabled(on)
        for edit in (self._ref, self._part, self._mfr, self._value, self._pkg):
            edit.setEnabled(on)
        if not on:
            self._refine_scale_btn.setEnabled(False)

    def _emit_datasheet_search(self, mode: str) -> None:
        """Emit datasheetSearchRequested with the current object and best part number."""
        if self._object_id is None:
            return
        # Prefer the part_number field; fall back to ref_designator label
        part_number = (self._part.text().strip() or self._ref.text().strip() or "")
        if not part_number:
            return
        self.datasheetSearchRequested.emit(self._object_id, part_number, mode)

    # ── Populate helpers ─────────────────────────────────────────────────────

    def _populate_datasheets(self, object_id: int | None) -> None:
        self._ds_list.clear()
        if object_id is None:
            item = QListWidgetItem("No datasheet linked")
            item.setForeground(Qt.GlobalColor.gray)
            self._ds_list.addItem(item)
            return

        rows = self._db.get_object_datasheets(object_id)
        if not rows:
            item = QListWidgetItem("No datasheet linked")
            item.setForeground(Qt.GlobalColor.gray)
            self._ds_list.addItem(item)
            return

        for ds in rows:
            path = Path(ds["file_path"])
            item = QListWidgetItem(f"✓  {path.name}")
            item.setData(Qt.ItemDataRole.UserRole, str(path))
            item.setToolTip(str(path))
            item.setForeground(Qt.GlobalColor.darkGreen)
            self._ds_list.addItem(item)

    def _open_datasheet(self, item: QListWidgetItem) -> None:
        path_str = item.data(Qt.ItemDataRole.UserRole)
        if not path_str:
            return
        path = Path(path_str)
        if not path.exists():
            return
        try:
            subprocess.Popen(["xdg-open", str(path)])
        except Exception:
            pass

    def _update_confidence(self, confidence: float | None) -> None:
        if confidence is None:
            self._conf_bar.setValue(0)
            self._conf_bar.setFormat("(manual)")
        else:
            pct = int(confidence * 100)
            self._conf_bar.setValue(pct)
            self._conf_bar.setFormat(f"{pct}%")
            if pct >= 80:
                self._conf_bar.setStyleSheet("QProgressBar::chunk { background-color: #4caf50; }")
            elif pct >= 50:
                self._conf_bar.setStyleSheet("QProgressBar::chunk { background-color: #ff9800; }")
            else:
                self._conf_bar.setStyleSheet("QProgressBar::chunk { background-color: #f44336; }")

    def _update_refine_scale_btn(self, object_id: int | None) -> None:
        """Enable 'Refine scale' only if the object was manually drawn (has drawn_px)."""
        if object_id is None:
            self._refine_scale_btn.setEnabled(False)
            return
        obj = self._db.conn().execute(
            "SELECT properties FROM objects WHERE id=?", (object_id,)
        ).fetchone()
        if obj:
            props = json.loads(obj["properties"] or "{}")
            self._refine_scale_btn.setEnabled(bool(props.get("drawn_px")))
        else:
            self._refine_scale_btn.setEnabled(False)

    # ── Public API ───────────────────────────────────────────────────────────

    def show_component(self, component_id: int):
        """Display and enable editing for a component (has a components row)."""
        self._component_id = component_id
        rows = self._db.conn().execute(
            "SELECT c.*, o.id AS object_id, o.confidence, o.verified "
            "FROM components c LEFT JOIN objects o ON o.id = c.object_id WHERE c.id=?",
            (component_id,),
        ).fetchall()
        if not rows:
            return
        c = rows[0]
        self._object_id = c["object_id"]

        self._ref.setText(c["ref_designator"] or "")
        self._part.setText(c["part_number"] or "")
        self._mfr.setText(c["manufacturer"] or "")
        self._value.setText(c["value"] or "")
        self._pkg.setText(c["package"] or "")
        self._notes.setPlainText(c["notes"] or "")
        self._update_confidence(c["confidence"])
        self._update_verify_button(bool(c["verified"]))

        self._populate_datasheets(self._object_id)
        self._update_refine_scale_btn(self._object_id)

        if c["mcp_data"]:
            try:
                self._mcp_result.setPlainText(
                    json.dumps(json.loads(c["mcp_data"]), indent=2)
                )
            except Exception:
                self._mcp_result.setPlainText(c["mcp_data"])

        self._set_enabled(True)

    def show_object(self, object_id: int) -> None:
        """Display minimal info for a non-component object (text_label, via, pad, etc.)."""
        self._object_id = object_id
        self._component_id = None

        obj_row = self._db.conn().execute(
            "SELECT * FROM objects WHERE id=?", (object_id,)
        ).fetchone()
        if not obj_row:
            return

        props = json.loads(obj_row["properties"] or "{}")
        self._ref.setText(obj_row["label"] or "")
        self._part.setText(props.get("part_number") or props.get("ref", "") or "")
        self._mfr.setText("")
        self._value.setText("")
        self._pkg.setText("")
        self._notes.clear()
        self._update_confidence(obj_row["confidence"])
        self._update_verify_button(bool(obj_row["verified"]))

        self._populate_datasheets(object_id)
        self._update_refine_scale_btn(object_id)
        # Only ref field editable for non-component objects; others grayed
        for edit in (self._part, self._mfr, self._value, self._pkg):
            edit.setEnabled(False)
        self._ref.setEnabled(True)
        self._notes.setEnabled(False)
        self._save_btn.setEnabled(False)
        self._mcp_btn.setEnabled(False)
        self._verify_btn.setEnabled(True)
        self._draw_outline_btn.setEnabled(True)

    def refresh_datasheets(self) -> None:
        self._populate_datasheets(self._object_id)

    def clear(self):
        self._component_id = None
        self._object_id = None
        for edit in (self._ref, self._part, self._mfr, self._value, self._pkg):
            edit.clear()
        self._ds_list.clear()
        self._notes.clear()
        self._mcp_result.clear()
        self._conf_bar.setValue(0)
        self._conf_bar.setFormat("")
        self._conf_bar.setStyleSheet("")
        self._set_enabled(False)

    # ── Button handlers ──────────────────────────────────────────────────────

    def _update_verify_button(self, verified: bool) -> None:
        if verified:
            self._verify_btn.setText("✓ Verified")
            self._verify_btn.setStyleSheet("color: #4caf50; font-weight: bold;")
        else:
            self._verify_btn.setText("✓ Verify")
            self._verify_btn.setStyleSheet("")

    def _on_verify(self) -> None:
        if self._object_id is None:
            return
        self._db.update_object(self._object_id, verified=1)
        if self._component_id is not None:
            self._db.conn().execute(
                "UPDATE components SET verified=1 WHERE id=?", (self._component_id,)
            )
            self._db.conn().commit()
        self._update_verify_button(True)

    def _on_draw_outline(self) -> None:
        if self._object_id is not None:
            self.drawOutlineRequested.emit(self._object_id)

    def _on_refine_scale(self) -> None:
        if self._object_id is not None:
            self.refineScaleRequested.emit(self._object_id)

    def _save_notes(self):
        if self._component_id is None:
            return
        notes = self._notes.toPlainText()
        self._db.conn().execute(
            "UPDATE components SET notes=? WHERE id=?",
            (notes, self._component_id),
        )
        self._db.conn().commit()

    def _query_mcp(self):
        if self._component_id is None:
            return
        row = self._db.conn().execute(
            "SELECT ref_designator, board_id FROM components WHERE id=?",
            (self._component_id,),
        ).fetchone()
        if not row:
            return
        board_row = self._db.conn().execute(
            "SELECT name FROM boards WHERE id=?", (row["board_id"],)
        ).fetchone()
        board_name = board_row["name"] if board_row else ""

        self._mcp_result.setPlainText("Querying MCP server…")
        try:
            result = subprocess.run(
                [
                    sys.executable, "-m", "toolkit.datasheets",
                    "--lookup", row["ref_designator"],
                    "--board", board_name,
                ],
                capture_output=True,
                text=True,
                timeout=30,
            )
            out = result.stdout or result.stderr
            self._mcp_result.setPlainText(out)
            self._db.save_mcp_data(self._component_id, {"raw": out})
        except subprocess.TimeoutExpired:
            self._mcp_result.setPlainText("MCP query timed out.")
        except Exception as exc:
            self._mcp_result.setPlainText(f"Error: {exc}")
