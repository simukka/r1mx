#!/usr/bin/env python3
"""
r1mx_app.py — r1mx Toolkit: unified GUI for RED ONE MX camera PCB reverse engineering.

Workflow:
  Process → Calibrate Board
  Analyze → Extract Layers | Extract BOM
  Generate → KiCad PCB

Panels:
  Left    — Board/Layer/Object tree with visibility toggles
  Center  — ImageViewer canvas (calibrated photo + extraction overlays)
  Right   — Inspector: component info + MCP query + datasheet badge
  Bottom  — Workflow log + progress bar

All data is persisted in r1mx.db (SQLite) at the repo root.

Usage:
    python scripts/r1mx_app.py
    python scripts/r1mx_app.py --board cpu_io_board
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

import numpy as np

from PyQt6.QtCore import (
    Qt, QPointF, QRectF, QThread, pyqtSignal, QObject,
)
from PyQt6.QtGui import (
    QAction, QBrush, QColor, QFont, QPen, QPixmap,
)
from PyQt6.QtWidgets import (
    QApplication, QCheckBox, QDialog, QDialogButtonBox, QDockWidget,
    QFormLayout, QGraphicsEllipseItem, QGraphicsItemGroup, QGraphicsPixmapItem,
    QGraphicsRectItem, QGraphicsScene, QHBoxLayout, QHeaderView,
    QLabel, QLineEdit, QListWidget, QListWidgetItem, QMainWindow, QMenu,
    QMessageBox, QProgressBar, QPushButton, QScrollArea, QSizePolicy,
    QSplitter, QStatusBar, QTextEdit, QToolBar,
    QTreeWidget, QTreeWidgetItem, QVBoxLayout, QWidget,
)

# ── locate repo root and add scripts/ to path ─────────────────────────────
_SCRIPTS = Path(__file__).resolve().parent
_REPO    = _SCRIPTS.parent
sys.path.insert(0, str(_SCRIPTS))

from r1mx_gui import ImageViewer, bgr_to_pixmap, draw_corner, draw_polyline
from r1mx_db  import DB

# ── image file extensions we look for ────────────────────────────────────
_IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".tif", ".tiff", ".bmp", ".JPG", ".JPEG", ".PNG"}

# ── object-type display config ────────────────────────────────────────────
OBJECT_TYPES = [
    ("photo",        "Photo",          QColor(200, 200, 200)),
    ("copper_area",  "Copper",         QColor(180, 120,   0)),
    ("outline",      "Outline",        QColor(  0, 180, 255)),
    ("via",          "Vias",           QColor(255,  80,  80)),
    ("pad",          "Pads",           QColor(255, 200,   0)),
    ("component",    "Components",     QColor(  0, 255, 120)),
    ("trace",        "Traces",         QColor(  0, 120, 255)),
]

LAYER_COLORS = {
    "top":    QColor(  0, 200, 100),
    "bottom": QColor(200, 100,   0),
}


# ═══════════════════════════════════════════════════════════════════════════
# Image picker dialog
# ═══════════════════════════════════════════════════════════════════════════

class ImagePickerDialog(QDialog):
    """
    Shows thumbnail previews of every image file in a board directory.
    The user selects one; the chosen filename is returned via `selected_file`.

    Usage::

        dlg = ImagePickerDialog(board_dir, current_image, parent=self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            chosen = dlg.selected_file   # relative filename, e.g. "P1003481.JPG"
    """

    _THUMB_W = 200
    _THUMB_H = 150

    def __init__(self, board_dir: Path, current_image: str = "", parent=None):
        super().__init__(parent)
        self.selected_file: str = current_image
        self._board_dir = board_dir

        self.setWindowTitle(f"Select image — {board_dir.name}")
        self.resize(900, 600)

        layout = QVBoxLayout(self)
        layout.setSpacing(8)

        info = QLabel(f"Board directory: <code>{board_dir}</code><br>"
                      "Double-click an image to select it.")
        info.setTextFormat(Qt.TextFormat.RichText)
        layout.addWidget(info)

        # Scroll area containing a grid of thumbnail buttons
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        grid_widget = QWidget()
        self._grid = QHBoxLayout(grid_widget)   # wrapping done via flow — simpler: use list
        scroll.setWidget(grid_widget)
        layout.addWidget(scroll, stretch=1)

        # Use QListWidget in icon mode — handles wrapping and selection automatically
        self._list = QListWidget()
        self._list.setViewMode(QListWidget.ViewMode.IconMode)
        self._list.setIconSize(
            __import__("PyQt6.QtCore", fromlist=["QSize"]).QSize(self._THUMB_W, self._THUMB_H)
        )
        self._list.setResizeMode(QListWidget.ResizeMode.Adjust)
        self._list.setSpacing(8)
        self._list.setWordWrap(True)
        self._list.itemDoubleClicked.connect(self._accept_item)
        layout.addWidget(self._list, stretch=1)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self._on_ok)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self._populate()

    def _populate(self):
        """Scan board dir and add thumbnails to the list."""
        import cv2
        from PyQt6.QtCore import QSize
        from PyQt6.QtGui import QIcon

        files = sorted(
            f for f in self._board_dir.iterdir()
            if f.suffix in _IMAGE_EXTS
        )
        if not files:
            item = QListWidgetItem("No image files found")
            self._list.addItem(item)
            return

        for fpath in files:
            img = cv2.imread(str(fpath))
            if img is None:
                continue
            # Scale thumbnail preserving aspect ratio
            h, w = img.shape[:2]
            scale = min(self._THUMB_W / w, self._THUMB_H / h)
            tw, th = int(w * scale), int(h * scale)
            thumb = cv2.resize(img, (tw, th), interpolation=cv2.INTER_AREA)
            pixmap = bgr_to_pixmap(thumb)

            item = QListWidgetItem(QIcon(pixmap), fpath.name)
            item.setData(Qt.ItemDataRole.UserRole, fpath.name)
            item.setToolTip(f"{fpath.name}\n{w}×{h} px")
            self._list.addItem(item)

            # Pre-select the current image
            if fpath.name == self.selected_file:
                self._list.setCurrentItem(item)

    def _accept_item(self, item: QListWidgetItem):
        self.selected_file = item.data(Qt.ItemDataRole.UserRole) or item.text()
        self.accept()

    def _on_ok(self):
        item = self._list.currentItem()
        if item:
            self.selected_file = item.data(Qt.ItemDataRole.UserRole) or item.text()
        self.accept()


# ═══════════════════════════════════════════════════════════════════════════
# Layer editor dialog
# ═══════════════════════════════════════════════════════════════════════════

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

class WorkerSignals(QObject):
    line       = pyqtSignal(str)
    finished   = pyqtSignal(bool, str)   # success, message


class SubprocessWorker(QThread):
    """Run an external command in a thread and stream its output."""

    def __init__(self, cmd: list[str], parent=None):
        super().__init__(parent)
        self._cmd = cmd
        self.signals = WorkerSignals()

    def run(self):
        try:
            proc = subprocess.Popen(
                self._cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
            )
            for line in proc.stdout:
                self.signals.line.emit(line.rstrip())
            proc.wait()
            ok = proc.returncode == 0
            self.signals.finished.emit(ok, "Done" if ok else f"Exit {proc.returncode}")
        except Exception as exc:
            self.signals.finished.emit(False, str(exc))


# ═══════════════════════════════════════════════════════════════════════════
# BoardTreePanel
# ═══════════════════════════════════════════════════════════════════════════

_ROLE_KIND   = Qt.ItemDataRole.UserRole          # "board" | "layer" | "objtype"
_ROLE_BOARD  = Qt.ItemDataRole.UserRole + 1      # board name
_ROLE_LAYER  = Qt.ItemDataRole.UserRole + 2      # layer name
_ROLE_OBJT   = Qt.ItemDataRole.UserRole + 3      # object type key


class BoardTreePanel(QWidget):
    """Left dock: tree of boards → layers → object types with visibility checkboxes."""

    # Emitted when a node is selected (board/layer) or visibility toggled
    boardSelected        = pyqtSignal(str)                    # board name
    layerSelected        = pyqtSignal(str, str)               # board, layer
    visibilityChanged    = pyqtSignal(str, str, str, bool)    # board, layer, objtype, visible
    imageSelectRequested = pyqtSignal(str, str)               # board, layer
    calibrateRequested   = pyqtSignal(str, str)               # board, layer
    editLayerRequested   = pyqtSignal(str, str)               # board, layer

    def __init__(self, db: DB, parent=None):
        super().__init__(parent)
        self._db = db
        self._ignore_check = False

        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)

        self._tree = QTreeWidget()
        self._tree.setHeaderHidden(True)
        self._tree.setColumnCount(1)
        self._tree.itemClicked.connect(self._on_click)
        self._tree.itemChanged.connect(self._on_check)
        self._tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self._tree.customContextMenuRequested.connect(self._on_context_menu)
        layout.addWidget(self._tree)

        self.refresh()

    def refresh(self):
        """Rebuild tree from DB."""
        self._ignore_check = True
        self._tree.clear()

        for board in self._db.list_boards():
            b_item = QTreeWidgetItem([board["name"]])
            b_item.setData(0, _ROLE_KIND,  "board")
            b_item.setData(0, _ROLE_BOARD, board["name"])
            b_item.setCheckState(0, Qt.CheckState.Checked)
            b_item.setFont(0, QFont("sans-serif", 9, QFont.Weight.Bold))

            for layer in self._db.list_layers(board["id"]):
                src = layer["source_image"] or ""
                cal_mark = "  ✓" if layer["calibrated"] else ""
                label = f"{layer['name']}{cal_mark}"
                if src:
                    label += f"  [{src}]"

                l_item = QTreeWidgetItem([label])
                l_item.setData(0, _ROLE_KIND,  "layer")
                l_item.setData(0, _ROLE_BOARD, board["name"])
                l_item.setData(0, _ROLE_LAYER, layer["name"])
                l_item.setCheckState(0, Qt.CheckState.Checked)
                color = LAYER_COLORS.get(layer["name"], QColor(150, 150, 150))
                l_item.setForeground(0, QBrush(color))
                l_item.setToolTip(0, f"Source image: {src or '(none)'}\n"
                                     "Right-click → Select image…")

                for key, label, color in OBJECT_TYPES:
                    ot_item = QTreeWidgetItem([label])
                    ot_item.setData(0, _ROLE_KIND,  "objtype")
                    ot_item.setData(0, _ROLE_BOARD, board["name"])
                    ot_item.setData(0, _ROLE_LAYER, layer["name"])
                    ot_item.setData(0, _ROLE_OBJT,  key)
                    ot_item.setCheckState(0, Qt.CheckState.Checked)
                    ot_item.setForeground(0, QBrush(color))
                    l_item.addChild(ot_item)

                b_item.addChild(l_item)

            self._tree.addTopLevelItem(b_item)
            b_item.setExpanded(True)
            for i in range(b_item.childCount()):
                b_item.child(i).setExpanded(False)

        self._ignore_check = False

    def _on_click(self, item: QTreeWidgetItem, col: int):
        kind = item.data(0, _ROLE_KIND)
        if kind == "board":
            self.boardSelected.emit(item.data(0, _ROLE_BOARD))
        elif kind in ("layer", "objtype"):
            self.layerSelected.emit(
                item.data(0, _ROLE_BOARD), item.data(0, _ROLE_LAYER)
            )

    def _on_check(self, item: QTreeWidgetItem, col: int):
        if self._ignore_check:
            return
        kind    = item.data(0, _ROLE_KIND)
        board   = item.data(0, _ROLE_BOARD) or ""
        layer   = item.data(0, _ROLE_LAYER) or ""
        objtype = item.data(0, _ROLE_OBJT)  or ""
        visible = item.checkState(0) == Qt.CheckState.Checked

        if kind == "board":
            # Cascade to all children
            self._ignore_check = True
            state = Qt.CheckState.Checked if visible else Qt.CheckState.Unchecked
            for i in range(item.childCount()):
                l_item = item.child(i)
                l_item.setCheckState(0, state)
                for j in range(l_item.childCount()):
                    l_item.child(j).setCheckState(0, state)
            self._ignore_check = False
            self.visibilityChanged.emit(board, "", "", visible)
        elif kind == "layer":
            self._ignore_check = True
            state = Qt.CheckState.Checked if visible else Qt.CheckState.Unchecked
            for i in range(item.childCount()):
                item.child(i).setCheckState(0, state)
            self._ignore_check = False
            self.visibilityChanged.emit(board, layer, "", visible)
        else:
            self.visibilityChanged.emit(board, layer, objtype, visible)

    def _on_context_menu(self, pos):
        item = self._tree.itemAt(pos)
        if item is None:
            return
        kind  = item.data(0, _ROLE_KIND)
        board = item.data(0, _ROLE_BOARD) or ""
        layer = item.data(0, _ROLE_LAYER) or ""

        menu = QMenu(self)
        if kind == "layer":
            sel_act = menu.addAction("Select image…")
            sel_act.triggered.connect(lambda: self.imageSelectRequested.emit(board, layer))
            cal_act = menu.addAction("Calibrate…")
            cal_act.triggered.connect(lambda: self.calibrateRequested.emit(board, layer))
            menu.addSeparator()
            edit_act = menu.addAction("Edit layer…")
            edit_act.triggered.connect(lambda: self.editLayerRequested.emit(board, layer))
        elif kind == "board":
            act = menu.addAction("Refresh")
            act.triggered.connect(self.refresh)
        menu.exec(self._tree.viewport().mapToGlobal(pos))

    def is_layer_visible(self, board: str, layer: str) -> bool:
        """Return the current checkbox state for a layer node."""
        root = self._tree.invisibleRootItem()
        for bi in range(root.childCount()):
            b_item = root.child(bi)
            if b_item.data(0, _ROLE_BOARD) != board:
                continue
            if b_item.checkState(0) != Qt.CheckState.Checked:
                return False
            for li in range(b_item.childCount()):
                l_item = b_item.child(li)
                if l_item.data(0, _ROLE_LAYER) == layer:
                    return l_item.checkState(0) == Qt.CheckState.Checked
        return True  # default visible if not found


# ═══════════════════════════════════════════════════════════════════════════
# InspectorPanel
# ═══════════════════════════════════════════════════════════════════════════

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
                    str(_SCRIPTS / "datasheet_mcp_server.py"),
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


# ═══════════════════════════════════════════════════════════════════════════
# WorkflowLog
# ═══════════════════════════════════════════════════════════════════════════

class WorkflowLog(QWidget):
    """Bottom dock: output log + progress bar."""

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 2, 4, 2)

        self._log = QTextEdit()
        self._log.setReadOnly(True)
        self._log.setFont(QFont("monospace", 9))
        self._log.setMaximumHeight(160)
        layout.addWidget(self._log)

        self._bar = QProgressBar()
        self._bar.setRange(0, 0)   # indeterminate by default
        self._bar.setVisible(False)
        layout.addWidget(self._bar)

    def append(self, line: str):
        self._log.append(line)
        self._log.verticalScrollBar().setValue(
            self._log.verticalScrollBar().maximum()
        )

    def clear(self):
        self._log.clear()

    def set_busy(self, busy: bool):
        self._bar.setVisible(busy)

    def set_progress(self, val: int, total: int):
        self._bar.setRange(0, total)
        self._bar.setValue(val)
        self._bar.setVisible(True)


# ═══════════════════════════════════════════════════════════════════════════
# Canvas scene groups
# ═══════════════════════════════════════════════════════════════════════════

class LayerScene:
    """Manages QGraphicsScene groups for a single board layer."""

    def __init__(self, scene: QGraphicsScene, board: str, layer: str):
        self.board  = board
        self.layer  = layer
        self._scene = scene
        self._groups: dict[str, QGraphicsItemGroup] = {}

        # Create a group per object type (+ "photo")
        for key, _, _ in [("photo", "", None)] + list(OBJECT_TYPES):
            g = QGraphicsItemGroup()
            scene.addItem(g)
            self._groups[key] = g

    def group(self, key: str) -> QGraphicsItemGroup | None:
        return self._groups.get(key)

    def set_visible(self, key: str, visible: bool):
        if key in self._groups:
            self._groups[key].setVisible(visible)

    def set_all_visible(self, visible: bool):
        for g in self._groups.values():
            g.setVisible(visible)

    def clear_group(self, key: str):
        g = self._groups.get(key)
        if g:
            for item in g.childItems():
                self._scene.removeItem(item)

    def load_photo(self, board_name: str, layer_name: str, source_image: str, warp_matrix, warped_size):
        """Load and display the calibrated (warped) board photo."""
        import cv2
        board_dir = _REPO / "components" / board_name
        img_path = board_dir / source_image
        if not img_path.exists():
            return
        img = cv2.imread(str(img_path))
        if img is None:
            return

        if warp_matrix and warped_size:
            M = np.array(warp_matrix, dtype=np.float64)
            w, h = warped_size
            img = cv2.warpPerspective(img, M, (w, h))

        pixmap = bgr_to_pixmap(img)
        item = QGraphicsPixmapItem(pixmap)
        item.setZValue(0)
        g = self._groups["photo"]
        g.addToGroup(item)

    def load_objects(self, db: DB, layer_id: int):
        """Load extracted objects from DB and create scene items."""
        for key, _, color in OBJECT_TYPES:
            if key == "photo":
                continue
            g = self._groups[key]
            # Remove old items
            for child in list(g.childItems()):
                self._scene.removeItem(child)
                g.removeFromGroup(child)

            objects = db.list_objects(layer_id, type_filter=key)
            for obj in objects:
                item = self._make_item(obj, color)
                if item:
                    g.addToGroup(item)

    def _make_item(self, obj, color: QColor):
        """Convert a DB object row into a QGraphicsItem."""
        # For now we need px_per_mm to convert mm → px. Use 20 px/mm as fallback.
        px = 20.0
        x  = (obj["x_mm"]  or 0) * px
        y  = (obj["y_mm"]  or 0) * px
        w  = (obj["width_mm"]  or 1) * px
        h  = (obj["height_mm"] or 1) * px
        t  = obj["type"]

        if t == "via":
            r = w / 2
            item = QGraphicsEllipseItem(x - r, y - r, w, h)
            pen = QPen(color, 1)
            pen.setCosmetic(True)
            item.setPen(pen)
            item.setBrush(QBrush(Qt.GlobalColor.transparent))
            item.setZValue(3)
            return item

        if t in ("pad", "component"):
            item = QGraphicsRectItem(x - w / 2, y - h / 2, w, h)
            pen = QPen(color, 1)
            pen.setCosmetic(True)
            item.setPen(pen)
            item.setBrush(QBrush(Qt.GlobalColor.transparent))
            item.setZValue(4)
            item.setFlag(item.GraphicsItemFlag.ItemIsSelectable)
            item.setData(0, obj["id"])       # store object id
            return item

        # outline / copper_area / trace: skip for now (need polygon data)
        return None


# ═══════════════════════════════════════════════════════════════════════════
# MainWindow
# ═══════════════════════════════════════════════════════════════════════════

class MainWindow(QMainWindow):

    def __init__(self, db: DB, initial_board: str | None = None):
        super().__init__()
        self._db = db
        self._workers: list[QThread] = []
        self._layer_scenes: dict[tuple[str, str], LayerScene] = {}  # (board,layer) → LayerScene
        self._active_board: str | None = None
        self._active_layer: str | None = None

        self.setWindowTitle("r1mx Toolkit")
        self.resize(1400, 900)

        self._build_ui()
        self._build_menus()
        self._build_toolbar()

        self._tree.refresh()
        self._load_db_state()

        if initial_board:
            self._open_board(initial_board)

    # ── UI construction ────────────────────────────────────────────────────

    def _build_ui(self):
        # Central widget: ImageViewer canvas
        self._viewer = ImageViewer(self)
        self._viewer.imageClicked.connect(self._on_canvas_click)
        self._viewer.imageMoved.connect(self._on_canvas_move)
        self._viewer.scene().selectionChanged.connect(self._on_selection_changed)
        self.setCentralWidget(self._viewer)

        # Left dock: board tree
        self._tree = BoardTreePanel(self._db, self)
        self._tree.boardSelected.connect(self._open_board)
        self._tree.layerSelected.connect(self._open_layer)
        self._tree.visibilityChanged.connect(self._on_visibility_changed)
        self._tree.imageSelectRequested.connect(self._pick_layer_image)
        self._tree.calibrateRequested.connect(self._calibrate_layer)
        self._tree.editLayerRequested.connect(self._edit_layer)
        left_dock = QDockWidget("Boards & Layers", self)
        left_dock.setWidget(self._tree)
        left_dock.setMinimumWidth(200)
        left_dock.setFeatures(
            QDockWidget.DockWidgetFeature.DockWidgetMovable |
            QDockWidget.DockWidgetFeature.DockWidgetFloatable
        )
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, left_dock)

        # Right dock: inspector
        self._inspector = InspectorPanel(self._db, self)
        right_dock = QDockWidget("Inspector", self)
        right_dock.setWidget(self._inspector)
        right_dock.setMinimumWidth(240)
        right_dock.setFeatures(
            QDockWidget.DockWidgetFeature.DockWidgetMovable |
            QDockWidget.DockWidgetFeature.DockWidgetFloatable
        )
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, right_dock)

        # Bottom dock: workflow log
        self._log = WorkflowLog(self)
        bottom_dock = QDockWidget("Workflow Log", self)
        bottom_dock.setWidget(self._log)
        bottom_dock.setFeatures(
            QDockWidget.DockWidgetFeature.DockWidgetMovable |
            QDockWidget.DockWidgetFeature.DockWidgetFloatable
        )
        self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, bottom_dock)

        self._status = QStatusBar()
        self.setStatusBar(self._status)

    def _build_menus(self):
        mb = self.menuBar()

        # File
        file_menu = mb.addMenu("&File")
        file_menu.addAction("&Refresh boards", self._tree.refresh)
        file_menu.addAction("&Import calibration JSONs", self._import_all_calibrations)
        file_menu.addAction("&Index datasheets", self._index_datasheets)
        file_menu.addSeparator()
        file_menu.addAction("&Quit", self.close)

        # Board
        board_menu = mb.addMenu("&Board")
        board_menu.addAction("Show in filesystem…", self._open_board_dir)
        board_menu.addAction("Select layer image…", self._pick_active_layer_image)
        board_menu.addAction("Calibrate layer…", self._calibrate_active_layer)

        # View
        view_menu = mb.addMenu("&View")

        zoom_in_act = QAction("Zoom In", self)
        zoom_in_act.setShortcut("Ctrl++")
        zoom_in_act.triggered.connect(self._viewer.zoom_in)
        view_menu.addAction(zoom_in_act)

        zoom_out_act = QAction("Zoom Out", self)
        zoom_out_act.setShortcut("Ctrl+-")
        zoom_out_act.triggered.connect(self._viewer.zoom_out)
        view_menu.addAction(zoom_out_act)

        zoom_fit_act = QAction("Fit Image", self)
        zoom_fit_act.setShortcut("Ctrl+0")
        zoom_fit_act.triggered.connect(self._viewer.fit_image)
        view_menu.addAction(zoom_fit_act)

        zoom_100_act = QAction("Zoom 100%", self)
        zoom_100_act.setShortcut("Ctrl+1")
        zoom_100_act.triggered.connect(self._viewer.zoom_reset)
        view_menu.addAction(zoom_100_act)

        # Help
        help_menu = mb.addMenu("&Help")
        help_menu.addAction("About r1mx Toolkit", self._show_about)

    def _build_toolbar(self):
        tb = QToolBar("Workflow", self)
        tb.setMovable(False)
        self.addToolBar(tb)

        # Process
        proc_label = QLabel("  Process: ")
        proc_label.setFont(QFont("sans-serif", 9, QFont.Weight.Bold))
        tb.addWidget(proc_label)

        cal_act = QAction("Calibrate Board", self)
        cal_act.setToolTip("Guided perspective calibration of PCB photos")
        cal_act.triggered.connect(self._run_calibrate)
        tb.addAction(cal_act)

        tb.addSeparator()

        # Analyze
        ana_label = QLabel("  Analyze: ")
        ana_label.setFont(QFont("sans-serif", 9, QFont.Weight.Bold))
        tb.addWidget(ana_label)

        ext_act = QAction("Extract Layers", self)
        ext_act.setToolTip("Extract copper, vias, outline from calibrated photo")
        ext_act.triggered.connect(self._run_extract_layers)
        tb.addAction(ext_act)

        bom_act = QAction("Extract BOM", self)
        bom_act.setToolTip("OCR reference designators and part numbers")
        bom_act.triggered.connect(self._run_extract_bom)
        tb.addAction(bom_act)

        tb.addSeparator()

        # Generate
        gen_label = QLabel("  Generate: ")
        gen_label.setFont(QFont("sans-serif", 9, QFont.Weight.Bold))
        tb.addWidget(gen_label)

        kicad_act = QAction("KiCad PCB", self)
        kicad_act.setToolTip("Generate .kicad_pcb from extracted data")
        kicad_act.triggered.connect(self._run_generate_kicad)
        tb.addAction(kicad_act)

        tb.addSeparator()

        # Calibrate diagnostic
        coord_act = QAction("--calibrate", self)
        coord_act.setToolTip("Coordinate calibration diagnostic")
        coord_act.triggered.connect(self._run_coord_calibrate)
        tb.addAction(coord_act)

    # ── State persistence ─────────────────────────────────────────────────

    def _load_db_state(self):
        board = self._db.get_state("active_board")
        if board:
            self._open_board(board)

    def _save_db_state(self):
        if self._active_board:
            self._db.set_state("active_board", self._active_board)
        if self._active_layer:
            self._db.set_state("active_layer", self._active_layer)

    # ── Board / layer opening ─────────────────────────────────────────────

    def _open_board(self, board_name: str):
        self._active_board = board_name
        self.setWindowTitle(f"r1mx Toolkit — {board_name}")
        self._status.showMessage(f"Board: {board_name}")
        self._save_db_state()

        # Auto-open the first calibrated layer
        board_id = self._db.get_or_create_board(board_name)
        layers = self._db.list_layers(board_id)
        cal_layers = [l for l in layers if l["calibrated"]]
        if cal_layers:
            self._open_layer(board_name, cal_layers[0]["name"])

    def _open_layer(self, board_name: str, layer_name: str):
        self._active_board = board_name
        self._active_layer = layer_name
        self._save_db_state()
        self._status.showMessage(f"Board: {board_name}  Layer: {layer_name}")

        key = (board_name, layer_name)
        should_show = self._tree.is_layer_visible(board_name, layer_name)

        if key not in self._layer_scenes:
            self._load_layer_into_scene(board_name, layer_name)
            if not should_show:
                # Loaded but tree says it's hidden — respect the checkbox
                ls = self._layer_scenes.get(key)
                if ls:
                    ls.set_all_visible(False)
        else:
            # Only change visibility if the tree agrees it should be shown
            self._layer_scenes[key].set_all_visible(should_show)
            self._viewer.scene().update()

        if should_show:
            self._viewer.fit_image()

    def _load_layer_into_scene(self, board_name: str, layer_name: str):
        board_id = self._db.get_or_create_board(board_name)
        layer_row = self._db.get_layer(board_id, layer_name)
        if not layer_row or not layer_row["calibrated"]:
            self._log.append(f"Layer {board_name}/{layer_name} not calibrated yet.")
            return

        cal = json.loads(layer_row["calibration"]) if layer_row["calibration"] else {}
        warp_matrix  = cal.get("warp_matrix")
        warped_size  = cal.get("warped_size")
        source_image = layer_row["source_image"] or ""

        scene = LayerScene(self._viewer.scene(), board_name, layer_name)
        self._layer_scenes[(board_name, layer_name)] = scene

        # Load the warped photo
        self._log.append(f"Loading {board_name}/{layer_name} …")
        scene.load_photo(board_name, layer_name, source_image, warp_matrix, warped_size)

        # Load extracted objects (may be empty)
        if layer_row["id"]:
            scene.load_objects(self._db, layer_row["id"])

        # Update viewer image size from the scene bounding rect
        rect = self._viewer.scene().itemsBoundingRect()
        self._viewer.scene().setSceneRect(rect)
        self._viewer.fit_image()
        self._log.append(f"  Loaded  {board_name}/{layer_name}")

    # ── Visibility toggles ────────────────────────────────────────────────

    def _on_visibility_changed(self, board: str, layer: str, objtype: str, visible: bool):
        if not board:
            return
        if not layer:
            # Toggle all layers for this board
            for (b, l), ls in self._layer_scenes.items():
                if b == board:
                    ls.set_all_visible(visible)
            self._viewer.scene().update()
            return
        key = (board, layer)
        ls = self._layer_scenes.get(key)
        if ls is None:
            return
        if not objtype:
            ls.set_all_visible(visible)
        else:
            ls.set_visible(objtype, visible)
        self._viewer.scene().update()

    # ── Canvas events ─────────────────────────────────────────────────────

    def _on_canvas_click(self, pt: QPointF):
        self._status.showMessage(
            f"Clicked: ({pt.x():.1f}, {pt.y():.1f}) px  "
            f"Board: {self._active_board}  Layer: {self._active_layer}"
        )

    def _on_canvas_move(self, pt: QPointF):
        self._status.showMessage(
            f"({pt.x():.0f}, {pt.y():.0f}) px   "
            f"{self._active_board or ''}  {self._active_layer or ''}"
        )

    def _on_selection_changed(self):
        items = self._viewer.scene().selectedItems()
        if not items:
            self._inspector.clear()
            return
        item = items[0]
        obj_id = item.data(0)   # stored in _make_item
        if obj_id is None:
            return
        # Find the component linked to this object
        row = self._db.conn().execute(
            "SELECT id FROM components WHERE object_id=?", (obj_id,)
        ).fetchone()
        if row:
            self._inspector.show_component(row["id"])
        else:
            self._inspector.clear()

    # ── Workflow actions ──────────────────────────────────────────────────

    def _require_board(self) -> str | None:
        if self._active_board:
            return self._active_board
        QMessageBox.warning(self, "No board selected", "Select a board first.")
        return None

    def _run_calibrate(self):
        """
        Toolbar 'Calibrate Board' button.

        Runs the full interactive calibration over all images in the board
        directory (normal ACCEPT → LAYER → CORNERS → REFPTS flow).
        If a specific layer is active, that layer's source image is offered first.
        """
        board = self._require_board()
        if not board:
            return

        sys.path.insert(0, str(_SCRIPTS))
        try:
            from calibrate_board import CalibrationGUI, save_calibration, find_all_images
        except ImportError as exc:
            QMessageBox.critical(self, "Import error",
                                 f"Cannot import calibrate_board:\n{exc}")
            return

        board_dir = _REPO / "components" / board
        images = find_all_images(board_dir)
        if not images:
            QMessageBox.warning(self, "No images",
                                f"No image files found in:\n{board_dir}")
            return

        self._log.clear()
        self._log.append(f"Calibrating {board}  ({len(images)} image(s)) …")
        board_id = self._db.get_or_create_board(board)
        saved = 0

        for i, img_path in enumerate(images):
            try:
                # No preset_layer — let the GUI ask [Y/N] and [T/B]
                gui = CalibrationGUI(img_path, 2.54, index=i, total=len(images))
            except ValueError as exc:
                self._log.append(f"  Skipping {img_path.name}: {exc}")
                continue

            layer_result, layer_cal = gui.run()

            if gui.quit_all:
                self._log.append("  Calibration cancelled.")
                break

            if layer_result is not None and layer_cal is not None:
                save_calibration(board, layer_result, layer_cal, board_dir)
                self._db.save_layer_calibration(
                    board_id, layer_result, layer_cal["source_image"], layer_cal
                )
                saved += 1
                self._log.append(
                    f"  Saved: {board}/{layer_result}  "
                    f"{layer_cal['px_per_mm']:.2f} px/mm"
                )
            else:
                self._log.append(f"  Skipped: {img_path.name}")

        self._log.append(
            f"Done — {saved} layer(s) calibrated." if saved else "No layers calibrated."
        )
        self._tree.refresh()
        if saved and self._active_board and self._active_layer:
            key = (self._active_board, self._active_layer)
            if key in self._layer_scenes:
                del self._layer_scenes[key]
            self._open_layer(self._active_board, self._active_layer)

    def _run_extract_layers(self):
        board = self._require_board()
        if not board:
            return
        self._log.clear()
        self._log.append(f"Extracting layers for {board} …")
        self._log.set_busy(True)

        cmd = [sys.executable, str(_SCRIPTS / "extract_pcb_layers.py"), "--board", board]
        w = SubprocessWorker(cmd, self)
        w.signals.line.connect(self._log.append)
        w.signals.finished.connect(lambda ok, m: self._on_step_done("extract_layers", ok, m))
        self._workers.append(w)
        w.start()

    def _run_extract_bom(self):
        board = self._require_board()
        if not board:
            return
        self._log.clear()
        self._log.append(f"Extracting BOM for {board} …")
        self._log.set_busy(True)

        cmd = [sys.executable, str(_SCRIPTS / "extract_bom.py"), "--board", board]
        w = SubprocessWorker(cmd, self)
        w.signals.line.connect(self._log.append)
        w.signals.finished.connect(lambda ok, m: self._on_step_done("extract_bom", ok, m))
        self._workers.append(w)
        w.start()

    def _run_generate_kicad(self):
        board = self._require_board()
        if not board:
            return
        self._log.clear()
        self._log.append(f"Generating KiCad PCB for {board} …")
        self._log.set_busy(True)

        output = _REPO / "components" / board / f"{board}.kicad_pcb"
        cmd = [
            "/usr/bin/python3",   # pcbnew requires system python
            str(_SCRIPTS / "generate_kicad_pcb.py"),
            "--board", board,
            "--output", str(output),
        ]
        w = SubprocessWorker(cmd, self)
        w.signals.line.connect(self._log.append)
        w.signals.finished.connect(
            lambda ok, m: self._on_kicad_done(ok, m, str(output))
        )
        self._workers.append(w)
        w.start()

    def _on_kicad_done(self, ok: bool, msg: str, output_path: str):
        self._log.set_busy(False)
        self._log.append(f"KiCad PCB {'written to ' + output_path if ok else 'failed: ' + msg}")
        if ok:
            btn = QMessageBox.question(
                self, "Open in KiCad?",
                f"KiCad PCB written to:\n{output_path}\n\nOpen in KiCad?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            if btn == QMessageBox.StandardButton.Yes:
                subprocess.Popen(["kicad", output_path])

    def _on_step_done(self, step: str, ok: bool, msg: str):
        self._log.set_busy(False)
        self._log.append(f"{step} {'complete' if ok else 'failed'}: {msg}")
        if ok and self._active_board and self._active_layer:
            # Refresh scene overlays
            key = (self._active_board, self._active_layer)
            if key in self._layer_scenes:
                board_id = self._db.get_or_create_board(self._active_board)
                layer_row = self._db.get_layer(board_id, self._active_layer)
                if layer_row:
                    self._layer_scenes[key].load_objects(self._db, layer_row["id"])

    def _run_coord_calibrate(self):
        self._log.clear()
        self._log.append("Starting coordinate calibration diagnostic …")
        self._log.set_busy(True)

        cmd = [sys.executable, str(_SCRIPTS / "calibrate_board.py"), "--calibrate"]
        w = SubprocessWorker(cmd, self)
        w.signals.line.connect(self._log.append)
        w.signals.finished.connect(lambda ok, m: (
            self._log.set_busy(False),
            self._log.append(f"Calibration diagnostic done: {m}"),
        ))
        self._workers.append(w)
        w.start()

    # ── Utility actions ───────────────────────────────────────────────────

    def _import_all_calibrations(self):
        self._db.migrate_all_calibration_jsons()
        self._tree.refresh()
        self._log.append("Imported all calibration.json files into r1mx.db")

    def _index_datasheets(self):
        self._db.index_datasheets()
        self._log.append("Datasheet index updated.")

    def _open_board_dir(self):
        if not self._active_board:
            return
        path = _REPO / "components" / self._active_board
        subprocess.Popen(["xdg-open", str(path)])

    def _pick_active_layer_image(self):
        """Board menu shortcut: pick image for the currently active layer."""
        if self._active_board and self._active_layer:
            self._pick_layer_image(self._active_board, self._active_layer)
        else:
            QMessageBox.information(self, "No layer active",
                                    "Select a board and layer first.")

    def _pick_layer_image(self, board_name: str, layer_name: str):
        """Open the image picker for a specific board/layer."""
        board_dir = _REPO / "components" / board_name
        if not board_dir.is_dir():
            QMessageBox.warning(self, "Board not found",
                                f"Directory not found:\n{board_dir}")
            return

        board_id  = self._db.get_or_create_board(board_name)
        layer_row = self._db.get_layer(board_id, layer_name)
        current   = layer_row["source_image"] if layer_row else ""

        dlg = ImagePickerDialog(board_dir, current or "", parent=self)
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return

        chosen = dlg.selected_file
        if not chosen:
            return

        # Persist to DB
        if layer_row:
            self._db.conn().execute(
                "UPDATE layers SET source_image=? WHERE id=?",
                (chosen, layer_row["id"]),
            )
            self._db.conn().commit()
        else:
            layer_id = self._db.get_or_create_layer(board_id, layer_name)
            self._db.conn().execute(
                "UPDATE layers SET source_image=? WHERE id=?",
                (chosen, layer_id),
            )
            self._db.conn().commit()

        self._log.append(f"Layer {board_name}/{layer_name}: image set to {chosen}")
        self._tree.refresh()

        # If this is the active layer, reload the canvas
        if board_name == self._active_board and layer_name == self._active_layer:
            key = (board_name, layer_name)
            if key in self._layer_scenes:
                del self._layer_scenes[key]
            self._open_layer(board_name, layer_name)

    def _calibrate_active_layer(self):
        """Board menu shortcut: calibrate the currently active layer."""
        if self._active_board and self._active_layer:
            self._calibrate_layer(self._active_board, self._active_layer)
        else:
            QMessageBox.information(self, "No layer active",
                                    "Select a board and layer first.")

    def _edit_layer(self, board_name: str, layer_name: str):
        """Open the layer editor dialog and refresh state on save."""
        dlg = EditLayerDialog(self._db, board_name, layer_name, parent=self)
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return

        # If the layer was renamed, the old scene key is stale — drop it
        old_key = (board_name, layer_name)
        if old_key in self._layer_scenes:
            del self._layer_scenes[old_key]

        self._tree.refresh()
        self._log.append(f"Layer {board_name}/{layer_name}: properties saved.")

        # If this was the active layer, reload canvas with new settings
        if board_name == self._active_board and layer_name == self._active_layer:
            new_name = dlg._name_edit.text().strip()
            self._active_layer = new_name
            self._open_layer(board_name, new_name)

    def _calibrate_layer(self, board_name: str, layer_name: str):
        """
        Run CalibrationGUI for the source image of the given layer.

        If no source image is set yet, the image picker opens first so the
        user can choose one.  The calibration runs in-process via a nested
        QEventLoop — no subprocess needed.

        On completion, results are written to:
          • components/<board>/calibration.json  (for CLI tool compatibility)
          • r1mx.db  layers table                (single source of truth)
        """
        # Import calibration helpers from calibrate_board.py
        sys.path.insert(0, str(_SCRIPTS))
        try:
            from calibrate_board import (
                CalibrationGUI, save_calibration, find_all_images,
            )
        except ImportError as exc:
            QMessageBox.critical(self, "Import error",
                                 f"Cannot import calibrate_board:\n{exc}")
            return

        board_dir = _REPO / "components" / board_name
        if not board_dir.is_dir():
            QMessageBox.warning(self, "Board not found",
                                f"Directory not found:\n{board_dir}")
            return

        board_id  = self._db.get_or_create_board(board_name)
        layer_row = self._db.get_layer(board_id, layer_name)
        source_image = layer_row["source_image"] if layer_row else ""

        # If no image is assigned, open the picker first
        if not source_image:
            dlg = ImagePickerDialog(board_dir, "", parent=self)
            if dlg.exec() != QDialog.DialogCode.Accepted or not dlg.selected_file:
                return
            source_image = dlg.selected_file
            # Save choice immediately
            layer_id = self._db.get_or_create_layer(board_id, layer_name)
            self._db.conn().execute(
                "UPDATE layers SET source_image=? WHERE id=?",
                (source_image, layer_id),
            )
            self._db.conn().commit()

        image_path = board_dir / source_image
        if not image_path.exists():
            QMessageBox.warning(self, "Image not found",
                                f"Image file not found:\n{image_path}\n\n"
                                "Use right-click → Select image… to reassign.")
            return

        images = [image_path]

        self._log.append(
            f"Calibrating {board_name}/{layer_name}  ({source_image}) …"
        )

        saved = 0
        ref_mm = 2.54   # standard 0.1″ header pitch — could be a dialog option later

        for i, img_path in enumerate(images):
            try:
                gui = CalibrationGUI(
                    img_path, ref_mm,
                    index=i, total=len(images),
                    preset_layer=layer_name,
                )
            except ValueError as exc:
                self._log.append(f"  Skipping {img_path.name}: {exc}")
                continue

            layer_result, layer_cal = gui.run()

            if gui.quit_all:
                self._log.append("  Calibration cancelled.")
                break

            if layer_result is not None and layer_cal is not None:
                # Write calibration.json (keeps CLI scripts working)
                save_calibration(board_name, layer_result, layer_cal, board_dir)
                # Write to DB
                self._db.save_layer_calibration(
                    board_id, layer_result, layer_cal["source_image"], layer_cal
                )
                saved += 1
                self._log.append(
                    f"  Saved: {board_name}/{layer_result}  "
                    f"{layer_cal['px_per_mm']:.2f} px/mm"
                )
            else:
                self._log.append(f"  Skipped: {img_path.name}")

        if saved:
            self._log.append(f"Calibration complete — {saved} layer(s) saved.")
            self._tree.refresh()
            # Reload canvas for the calibrated layer
            key = (board_name, layer_name)
            if key in self._layer_scenes:
                del self._layer_scenes[key]
            self._open_layer(board_name, layer_name)

    def _show_about(self):
        QMessageBox.about(
            self,
            "r1mx Toolkit",
            "<b>r1mx Toolkit</b><br><br>"
            "Reverse engineering assistant for the RED ONE MX digital cinema camera.<br><br>"
            "Workflow: Calibrate → Extract Layers → Extract BOM → Generate KiCad PCB<br><br>"
            "All data stored in <code>r1mx.db</code> (SQLite) at the repo root.",
        )

    def closeEvent(self, event):
        self._save_db_state()
        super().closeEvent(event)


# ═══════════════════════════════════════════════════════════════════════════
# Entry point
# ═══════════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(description="r1mx Toolkit")
    parser.add_argument("--board", metavar="BOARD", help="Open this board on startup")
    args = parser.parse_args()

    app = QApplication(sys.argv)
    app.setApplicationName("r1mx Toolkit")
    app.setStyle("Fusion")

    db = DB()
    # Auto-migrate calibration JSONs on first run if DB is empty
    if not db.list_boards():
        print("First run — importing calibration.json files …")
        db.migrate_all_calibration_jsons()
        db.index_datasheets()

    win = MainWindow(db, initial_board=args.board)
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
