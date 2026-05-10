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
    QLabel, QLineEdit, QMainWindow, QMenu, QMessageBox, QProgressBar,
    QPushButton, QSizePolicy, QSplitter, QStatusBar, QTextEdit, QToolBar,
    QTreeWidget, QTreeWidgetItem, QVBoxLayout, QWidget,
)

# ── locate repo root and add scripts/ to path ─────────────────────────────
_SCRIPTS = Path(__file__).resolve().parent
_REPO    = _SCRIPTS.parent
sys.path.insert(0, str(_SCRIPTS))

from r1mx_gui import ImageViewer, bgr_to_pixmap, draw_corner, draw_polyline
from r1mx_db  import DB

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
# Worker (run blocking tasks in a thread, stream log lines to the GUI)
# ═══════════════════════════════════════════════════════════════════════════

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
    boardSelected   = pyqtSignal(str)                    # board name
    layerSelected   = pyqtSignal(str, str)               # board, layer
    visibilityChanged = pyqtSignal(str, str, str, bool)  # board, layer, objtype, visible

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
                l_item = QTreeWidgetItem([layer["name"]])
                l_item.setData(0, _ROLE_KIND,  "layer")
                l_item.setData(0, _ROLE_BOARD, board["name"])
                l_item.setData(0, _ROLE_LAYER, layer["name"])
                l_item.setCheckState(0, Qt.CheckState.Checked)
                color = LAYER_COLORS.get(layer["name"], QColor(150, 150, 150))
                l_item.setForeground(0, QBrush(color))

                if layer["calibrated"]:
                    l_item.setText(0, layer["name"] + "  ✓")

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
        self._scene.addItem(item)
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

        # View
        view_menu = mb.addMenu("&View")
        view_menu.addAction("Fit image", self._viewer.fit_image)

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
        if key not in self._layer_scenes:
            self._load_layer_into_scene(board_name, layer_name)
        else:
            # Just make it visible
            self._layer_scenes[key].set_all_visible(True)

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
            return
        key = (board, layer)
        ls = self._layer_scenes.get(key)
        if ls is None:
            return
        if not objtype:
            ls.set_all_visible(visible)
        else:
            ls.set_visible(objtype, visible)

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
        board = self._require_board()
        if not board:
            return
        self._log.clear()
        self._log.append(f"Starting calibration for {board} …")
        self._log.set_busy(True)

        cmd = [sys.executable, str(_SCRIPTS / "calibrate_board.py"), "--board", board]
        w = SubprocessWorker(cmd, self)
        w.signals.line.connect(self._log.append)
        w.signals.finished.connect(self._on_calibrate_done)
        self._workers.append(w)
        w.start()

    def _on_calibrate_done(self, ok: bool, msg: str):
        self._log.set_busy(False)
        self._log.append(f"Calibration {'complete' if ok else 'failed'}: {msg}")
        if ok:
            # Migrate JSON → DB for the active board
            self._db.migrate_calibration_json(self._active_board)
            self._tree.refresh()
            # Reload scene
            if self._active_board and self._active_layer:
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
