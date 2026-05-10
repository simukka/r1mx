"""Inspector panel."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from toolkit.db import DB

_TOOLKIT = Path(__file__).resolve().parents[2]

class InspectorPanel(QWidget):
    """Right dock: shows info about the selected component."""

    def __init__(self, db: DB, parent=None):
        super().__init__(parent)
        self._db = db
        self._component_id: int | None = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(6, 6, 6, 6)

        title = QLabel("Inspector")
        title.setFont(QFont("sans-serif", 10, QFont.Weight.Bold))
        layout.addWidget(title)

        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        self._ref   = QLabel("—")
        self._part  = QLabel("—")
        self._mfr   = QLabel("—")
        self._value = QLabel("—")
        self._pkg   = QLabel("—")
        self._ds_badge = QLabel("No datasheet")
        self._ds_badge.setStyleSheet("color: grey;")

        form.addRow("Ref:",          self._ref)
        form.addRow("Part:",         self._part)
        form.addRow("Manufacturer:", self._mfr)
        form.addRow("Value:",        self._value)
        form.addRow("Package:",      self._pkg)
        form.addRow("Datasheet:",    self._ds_badge)
        layout.addLayout(form)

        self._notes = QTextEdit()
        self._notes.setPlaceholderText("Notes…")
        self._notes.setMaximumHeight(80)
        layout.addWidget(self._notes)

        btn_row = QHBoxLayout()
        self._save_btn = QPushButton("Save notes")
        self._save_btn.clicked.connect(self._save_notes)
        self._mcp_btn  = QPushButton("Query MCP")
        self._mcp_btn.clicked.connect(self._query_mcp)
        btn_row.addWidget(self._save_btn)
        btn_row.addWidget(self._mcp_btn)
        layout.addLayout(btn_row)

        self._mcp_result = QTextEdit()
        self._mcp_result.setReadOnly(True)
        self._mcp_result.setPlaceholderText("MCP result will appear here…")
        layout.addWidget(self._mcp_result)

        layout.addStretch()
        self._set_enabled(False)

    def _set_enabled(self, on: bool):
        for w in (self._notes, self._save_btn, self._mcp_btn):
            w.setEnabled(on)

    def show_component(self, component_id: int):
        self._component_id = component_id
        rows = self._db.conn().execute(
            "SELECT c.*, d.file_path AS ds_path FROM components c "
            "LEFT JOIN datasheets d ON c.datasheet_id=d.id WHERE c.id=?",
            (component_id,),
        ).fetchall()
        if not rows:
            return
        c = rows[0]
        self._ref.setText(c["ref_designator"] or "—")
        self._part.setText(c["part_number"] or "—")
        self._mfr.setText(c["manufacturer"] or "—")
        self._value.setText(c["value"] or "—")
        self._pkg.setText(c["package"] or "—")
        self._notes.setPlainText(c["notes"] or "")

        if c["ds_path"]:
            self._ds_badge.setText(f"✓  {Path(c['ds_path']).name}")
            self._ds_badge.setStyleSheet("color: green;")
        else:
            # Try finding by part number
            part = c["part_number"] or ""
            ds = self._db.find_datasheet(part) if part else None
            if ds:
                self._ds_badge.setText(f"✓  {Path(ds['file_path']).name}")
                self._ds_badge.setStyleSheet("color: green;")
            else:
                self._ds_badge.setText("No datasheet")
                self._ds_badge.setStyleSheet("color: grey;")

        if c["mcp_data"]:
            try:
                self._mcp_result.setPlainText(
                    json.dumps(json.loads(c["mcp_data"]), indent=2)
                )
            except Exception:
                self._mcp_result.setPlainText(c["mcp_data"])

        self._set_enabled(True)

    def clear(self):
        self._component_id = None
        for lbl in (self._ref, self._part, self._mfr, self._value, self._pkg):
            lbl.setText("—")
        self._ds_badge.setText("No datasheet")
        self._ds_badge.setStyleSheet("color: grey;")
        self._notes.clear()
        self._mcp_result.clear()
        self._set_enabled(False)

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
                    sys.executable,
                    str(_TOOLKIT / "datasheets" / "mcp_server.py"),
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


