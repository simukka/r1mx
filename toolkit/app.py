"""Main application entry point."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

from PyQt6.QtCore import QPointF, Qt, QThread
from PyQt6.QtGui import QAction, QColor, QFont, QPen
from PyQt6.QtWidgets import (
    QApplication,
    QDialog,
    QDockWidget,
    QLabel,
    QMainWindow,
    QMessageBox,
    QStatusBar,
    QToolBar,
)

from toolkit.analysis.calibrate import CalibrationGUI, find_all_images, save_calibration, run_coord_calibration
from toolkit.db import DB
from toolkit.gui.dialogs.datasheet_find import DatasheetFindDialog
from toolkit.gui.dialogs.datasheet_scan import DatasheetScanDialog
from toolkit.gui.dialogs.edit_layer import EditLayerDialog
from toolkit.gui.dialogs.footprint_picker import FootprintPickerDialog
from toolkit.gui.dialogs.image_picker import ImagePickerDialog
from toolkit.gui.dialogs.merge_entities import MergeEntitiesDialog
from toolkit.gui.dialogs.pinout_wizard import DatasheetPinoutWizard
from toolkit.gui.dialogs.probe_wizard import ProbeWizardDialog
from toolkit.gui.dialogs.scan_layer import ScanLayerWizard, ScanLayerResult
from toolkit.gui.dialogs.scan_preview import ScanPreviewDialog
from toolkit.gui.items.footprint_overlay import FootprintOverlayItem
from toolkit.gui.panels.inspector import InspectorPanel
from toolkit.gui.panels.log import WorkflowLog
from toolkit.gui.panels.tree import BoardTreePanel
from toolkit.gui.scene import LayerScene, OBJECT_TYPES
from toolkit.gui.theme import THEME
from toolkit.gui.viewer import ImageViewer
from toolkit.gui.widgets.service_status import ServiceStatusBar
from toolkit.gui.widgets.status_lcd import StatusLCDWidget
from toolkit.paths import REPO_ROOT
from toolkit.services.manager import ServiceManager, ServiceMonitor
from toolkit.workers.base import SubprocessWorker
from toolkit.workers.indexer import DatasheetIndexWorker

from enum import Enum, auto

class CanvasMode(Enum):
    """Active interaction mode for the main canvas."""
    NORMAL          = auto()   # pan / zoom / select (default)
    ADD_VIA         = auto()   # next click places a via
    ADD_COMPONENT   = auto()   # click+drag defines a component bounding box
    ADD_TEXT        = auto()   # next click places a text_label
    ADD_TRACE       = auto()   # click via/pad or point → route trace segments; Enter breaks chain; Esc exits
    SET_ORIENTATION = auto()   # next edge-click sets pin-1 side for a component
    ALIGN_FOOTPRINT = auto()   # keyboard R/+/-/arrows adjust footprint overlay; Enter confirms
    ADD_PIN         = auto()   # each click places a pin marker; Enter confirms, Esc cancels


class MainWindow(QMainWindow):

    def __init__(self, db: DB, initial_board: str | None = None):
        super().__init__()
        self._db = db
        self._workers: list[QThread] = []
        self._layer_scenes: dict[tuple[str, str], LayerScene] = {}  # (board,layer) → LayerScene
        self._active_board: str | None = None
        self._active_layer: str | None = None
        self._probe_wizard: ProbeWizardDialog | None = None
        self._canvas_mode: CanvasMode = CanvasMode.NORMAL
        self._add_target_object_id: int | None = None  # object being outlined
        self._edge_preview_item = None                 # QGraphicsLineItem shown in SET_ORIENTATION mode
        # Footprint alignment state
        self._footprint_overlay = None                  # FootprintOverlayItem | None
        self._footprint_object_id: int | None = None   # component being aligned
        self._footprint_pinout_id: int | None = None   # pinout row id
        # Pin placement state
        self._pin_target_object_id: int | None = None  # component being pinned
        self._pending_pin_items: list = []             # temp QGraphicsEllipseItems
        # Continuous placement state (via / component / text modes)
        self._last_placed_object_id: int | None = None  # last item placed in current mode
        self._mode_place_count: int = 0                 # items placed since mode entered
        self._last_via_drill_mm: float = 0.3            # remembered default for drill dialog
        # Trace placement state (ADD_TRACE mode)
        self._trace_points: list[tuple[float, float]] = []  # (x,y) mm of each clicked point
        self._trace_start_obj_id: int | None = None         # DB id of snapped start via/pad
        self._trace_end_obj_id:   int | None = None         # DB id of snapped end via/pad (last snap)
        self._trace_preview_items: list = []                # QGraphicsLineItems for the live path
        self._trace_anchor_dot  = None                      # QGraphicsEllipseItem at start
        self._trace_snap_ring   = None                      # QGraphicsEllipseItem snap highlight
        self._trace_width_mm: float = 0.2                   # remembered trace width

        # Background services
        self._svc_manager: ServiceManager | None = None
        self._svc_monitor: ServiceMonitor | None = None
        self._indexer: DatasheetIndexWorker | None = None

        self.setWindowTitle("r1mx Toolkit")
        self.resize(1400, 900)

        self._build_ui()
        self._build_menus()
        self._build_toolbar()

        self._tree.refresh(self._tree.get_full_vis_state())
        self._load_db_state()

        if initial_board:
            self._open_board(initial_board)

        # Start background services after the window is fully built
        self._start_background_services()

    # ── UI construction ────────────────────────────────────────────────────

    def _build_ui(self):
        # Central widget: ImageViewer canvas
        self._viewer = ImageViewer(self)
        self._viewer.imageClicked.connect(self._on_canvas_click)
        self._viewer.imageReleased.connect(self._on_canvas_release)
        self._viewer.imageMoved.connect(self._on_canvas_move)
        self._viewer.debugClicked.connect(self._on_debug_click)
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
        self._tree.componentSelected.connect(self._on_component_selected)
        self._tree.removeDataRequested.connect(self._remove_layer_data)
        self._tree.scanDatasheetRequested.connect(self._scan_datasheet)
        # Entity CRUD
        self._tree.entityDeleteRequested.connect(self._on_entity_delete)
        self._tree.entityEditRequested.connect(self._on_entity_edit)
        self._tree.entityVerifyRequested.connect(self._on_entity_verify)
        self._tree.mergeRequested.connect(self._on_merge_requested)
        self._tree.removeDataRequested.connect(self._remove_layer_data)
        self._tree.scanDatasheetRequested.connect(self._scan_datasheet)
        # Layer CRUD
        self._tree.addLayerRequested.connect(self._on_layer_added)
        self._tree.deleteLayerRequested.connect(self._on_layer_deleted)
        self._tree.shiftObjectsRequested.connect(self._on_objects_shifted)
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
        self._inspector.drawOutlineRequested.connect(self._on_draw_outline_requested)
        self._inspector.refineScaleRequested.connect(self._on_refine_scale_requested)
        self._inspector.setOrientationRequested.connect(self._on_set_orientation_requested)
        self._inspector.datasheetSearchRequested.connect(self._find_datasheet)
        self._inspector.pinoutSelectionRequested.connect(self._open_pinout_wizard)
        self._inspector.kicadFootprintRequested.connect(self._open_footprint_picker)
        self._inspector.placePinsRequested.connect(self._enter_add_pin_mode)
        self._inspector.photoEnhancementChanged.connect(self._on_photo_enhancement)
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

        # Status LCD dock (hidden by default; show via View > Status LCD)
        self._lcd_widget = StatusLCDWidget(parent=self)
        lcd_dock = QDockWidget("Status LCD", self)
        lcd_dock.setWidget(self._lcd_widget)
        lcd_dock.setFeatures(
            QDockWidget.DockWidgetFeature.DockWidgetMovable |
            QDockWidget.DockWidgetFeature.DockWidgetFloatable |
            QDockWidget.DockWidgetFeature.DockWidgetClosable
        )
        lcd_dock.setMinimumWidth(200)
        lcd_dock.hide()
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, lcd_dock)
        self._lcd_dock = lcd_dock

        self._status = QStatusBar()
        self.setStatusBar(self._status)

        # Service status dots (right of status bar, leftmost of the permanent widgets)
        self._svc_status_bar = ServiceStatusBar(self)
        self._status.addPermanentWidget(self._svc_status_bar)

        # Persistent unresolved-component count label on the right of the status bar
        self._unresolved_label = QLabel("")
        self._unresolved_label.setStyleSheet("color: #e6b400; margin-right: 8px;")
        self._status.addPermanentWidget(self._unresolved_label)

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

        view_menu.addSeparator()
        lcd_act = QAction("Status LCD", self)
        lcd_act.setCheckable(True)
        lcd_act.setChecked(False)
        lcd_act.setShortcut("Ctrl+Shift+L")
        lcd_act.triggered.connect(self._toggle_lcd_dock)
        self._lcd_dock.visibilityChanged.connect(lcd_act.setChecked)
        view_menu.addAction(lcd_act)

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

        ext_act = QAction("Scan Layer", self)
        ext_act.setToolTip(
            "Unified PCB layer scan: choose vias, pads, traces, outline, or text/components.\n"
            "Results are previewed before saving — you can add missed items or re-tune parameters."
        )
        ext_act.triggered.connect(self._run_scan_layer)
        tb.addAction(ext_act)

        # "Add entity" dropdown
        from PyQt6.QtWidgets import QToolButton, QMenu as _QMenu
        add_btn = QToolButton(self)
        add_btn.setText("✚ Add")
        add_btn.setToolTip("Manually place a via, component, or text label on the canvas")
        add_btn.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        add_menu = _QMenu(add_btn)
        add_menu.addAction("📍 Via",       lambda: self._set_canvas_mode(CanvasMode.ADD_VIA))
        add_menu.addAction("□ Component",  lambda: self._set_canvas_mode(CanvasMode.ADD_COMPONENT))
        add_menu.addAction("T Text Label", lambda: self._set_canvas_mode(CanvasMode.ADD_TEXT))
        add_menu.addAction("∿ Trace",      lambda: self._enter_trace_mode())
        add_btn.setMenu(add_menu)
        tb.addWidget(add_btn)

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

        tb.addSeparator()

        # Identify
        ident_label = QLabel("  Identify: ")
        ident_label.setFont(QFont("sans-serif", 9, QFont.Weight.Bold))
        tb.addWidget(ident_label)

        probe_act = QAction("Probe Components", self)
        probe_act.setToolTip(
            "Open the probe wizard: step-by-step multimeter guidance\n"
            "to identify unknown resistors, capacitors, inductors, and more."
        )
        probe_act.triggered.connect(self._run_probe_wizard)
        tb.addAction(probe_act)

    # ── State persistence ─────────────────────────────────────────────────

    def _load_db_state(self):
        # Restore visibility first, then open the last active board/layer
        vis = self._db.load_visibility_state()
        if vis:
            self._tree.refresh(vis)
        board = self._db.get_state("active_board")
        if board:
            self._open_board(board)

    # ── Background services ────────────────────────────────────────────────

    def _start_background_services(self) -> None:
        """Start ChromaDB + Ollama, wire status dots, and launch the indexer."""
        try:
            self._svc_manager = ServiceManager()
            self._svc_manager.start_all()

            self._svc_monitor = ServiceMonitor(self._svc_manager, parent=self)
            self._svc_monitor.statusChanged.connect(self._svc_status_bar.update_services)
            self._svc_monitor.start()

            self._indexer = DatasheetIndexWorker(parent=self)
            self._indexer.statusChanged.connect(self._svc_status_bar.update_indexer)
            self._indexer.logLine.connect(self._log.append)
            self._indexer.newChunks.connect(self._on_indexer_new_chunks)
            self._indexer.start()

        except Exception as exc:
            self._log.append(f"<b>⚠ Services startup error:</b> {exc}")

    def _on_indexer_new_chunks(self, count: int) -> None:
        self._log.append(f"<b>Indexer:</b> {count} new chunk(s) added to ChromaDB")

    def closeEvent(self, event) -> None:  # type: ignore[override]
        """Stop background services and threads on window close."""
        if self._indexer:
            self._indexer.stop()
            self._indexer.wait(3000)

        if self._svc_monitor:
            self._svc_monitor.stop()
            self._svc_monitor.wait(3000)

        if self._svc_manager:
            self._svc_manager.stop_all()

        super().closeEvent(event)

    def _save_db_state(self):
        if self._active_board:
            self._db.set_state("active_board", self._active_board)
        if self._active_layer:
            self._db.set_state("active_layer", self._active_layer)

    def _save_visibility_state(self):
        """Persist current tree checkbox state to DB."""
        self._db.save_visibility_state(self._tree.get_full_vis_state())

    # ── Board / layer opening ─────────────────────────────────────────────

    def _open_board(self, board_name: str):
        self._active_board = board_name
        self.setWindowTitle(f"r1mx Toolkit — {board_name}")
        self._status.showMessage(f"Board: {board_name}")
        self._save_db_state()
        self._refresh_unresolved_count()

        # Auto-open the first calibrated layer
        board_id = self._db.get_or_create_board(board_name)
        layers = self._db.list_layers(board_id)
        cal_layers = [l for l in layers if l["calibrated"]]
        if cal_layers:
            self._open_layer(board_name, cal_layers[0]["name"])

    def _open_layer(self, board_name: str, layer_name: str):
        """
        Make (board_name, layer_name) the active layer.

        Solo behaviour: hide all other loaded layer scenes and uncheck them
        in the tree so only the selected layer is shown.  The user can then
        re-check other layers via the tree to overlay them.
        """
        self._active_board = board_name
        self._active_layer = layer_name
        self._save_db_state()
        self._status.showMessage(f"Board: {board_name}  Layer: {layer_name}")

        # Clear any vignette highlight from previously active layers
        for ls in self._layer_scenes.values():
            ls.clear_highlight()

        # Solo: uncheck everything except this layer, update scene visibility
        self._tree.set_solo_layer(board_name, layer_name)
        for (b, l), ls in self._layer_scenes.items():
            ls.set_all_visible(b == board_name and l == layer_name)

        key = (board_name, layer_name)
        if key not in self._layer_scenes:
            self._load_layer_into_scene(board_name, layer_name)
        else:
            self._viewer.scene().update()

        # Persist the new solo state
        self._save_visibility_state()
        self._viewer.fit_image()

    def _load_layer_into_scene(self, board_name: str, layer_name: str):
        board_id = self._db.get_or_create_board(board_name)
        layer_row = self._db.get_layer(board_id, layer_name)
        if not layer_row:
            return

        calibrated   = bool(layer_row["calibrated"])
        cal          = json.loads(layer_row["calibration"]) if layer_row["calibration"] else {}
        warp_matrix  = cal.get("warp_matrix") if calibrated else None
        warped_size  = cal.get("warped_size")  if calibrated else None
        px_per_mm    = cal.get("px_per_mm", 20.0)
        source_image = layer_row["source_image"] or ""

        if not source_image:
            self._log.append(f"Layer {board_name}/{layer_name}: no image selected yet.")
            return

        scene = LayerScene(self._viewer.scene(), board_name, layer_name)
        self._layer_scenes[(board_name, layer_name)] = scene

        # Load photo — shows raw image when not calibrated, warped when calibrated
        status = "calibrated" if calibrated else "raw (not calibrated)"
        self._log.append(f"Loading {board_name}/{layer_name} ({status}) …")
        scene.load_photo(
            board_name, layer_name, source_image, warp_matrix, warped_size,
            board_dir=self._db.get_board_abs_dir(board_name),
        )

        # Load extracted objects only if calibrated and objects exist
        if calibrated:
            n_objs = self._db.conn().execute(
                "SELECT COUNT(*) FROM objects WHERE layer_id=?", (layer_row["id"],)
            ).fetchone()[0]
            if n_objs > 0:
                self._log.append(f"  Rendering {n_objs} objects …")
                scene.load_objects(self._db, layer_row["id"], px_per_mm)

        # Apply per-objtype visibility saved in the tree (e.g. "hide traces")
        saved_vis = self._tree.get_full_vis_state()
        layer_vis = saved_vis.get(board_name, {}).get(layer_name, {})
        for obj_key, _, _ in OBJECT_TYPES:
            scene.set_visible(obj_key, layer_vis.get(obj_key, True))

        # Fit viewport to the scene contents
        rect = self._viewer.scene().itemsBoundingRect()
        self._viewer.scene().setSceneRect(rect)
        self._viewer.fit_image()
        self._log.append(f"  Loaded  {board_name}/{layer_name}")

    # ── Visibility toggles ────────────────────────────────────────────────

    def _on_visibility_changed(self, board: str, layer: str, objtype: str, visible: bool):
        if not board:
            return
        saved_vis = self._tree.get_full_vis_state()

        if not layer:
            # Board-level toggle: apply per-objtype state to all scenes for this board
            for (b, l), ls in self._layer_scenes.items():
                if b == board:
                    if not visible:
                        ls.set_all_visible(False)
                    else:
                        # Re-enable with per-objtype granularity
                        layer_vis = saved_vis.get(b, {}).get(l, {})
                        for key, _, _ in OBJECT_TYPES:
                            ls.set_visible(key, layer_vis.get(key, True))
        else:
            key = (board, layer)
            ls = self._layer_scenes.get(key)
            if ls is not None:
                if not objtype:
                    # Layer-level toggle: apply per-objtype state when enabling
                    if not visible:
                        ls.set_all_visible(False)
                    else:
                        layer_vis = saved_vis.get(board, {}).get(layer, {})
                        for otype, _, _ in OBJECT_TYPES:
                            ls.set_visible(otype, layer_vis.get(otype, True))
                else:
                    ls.set_visible(objtype, visible)

        self._viewer.scene().update()
        self._save_visibility_state()

    # ── Canvas events ─────────────────────────────────────────────────────

    _CONTINUOUS_MODES = frozenset({CanvasMode.ADD_VIA, CanvasMode.ADD_COMPONENT, CanvasMode.ADD_TEXT, CanvasMode.ADD_TRACE})

    def _set_canvas_mode(self, mode: CanvasMode, target_object_id: int | None = None) -> None:
        """Switch the canvas interaction mode and update the status bar hint."""
        prev_mode = self._canvas_mode
        # clean up edge preview from a previous SET_ORIENTATION session
        self._clear_edge_preview()
        # clean up trace preview items whenever leaving ADD_TRACE
        if prev_mode == CanvasMode.ADD_TRACE and mode != CanvasMode.ADD_TRACE:
            self._clear_trace_preview()
            self._trace_points = []
            self._trace_start_obj_id = None
            self._trace_end_obj_id   = None
        # cancel any uncommitted pin placement when leaving ADD_PIN mode
        if prev_mode == CanvasMode.ADD_PIN and mode != CanvasMode.ADD_PIN:
            self._cancel_pin_placement()

        # When exiting a continuous placement mode → select the last placed object
        if (prev_mode in self._CONTINUOUS_MODES
                and mode == CanvasMode.NORMAL
                and self._last_placed_object_id is not None):
            last_id = self._last_placed_object_id
            self._last_placed_object_id = None
            self._mode_place_count = 0
            self._canvas_mode = mode
            self._add_target_object_id = target_object_id
            self._viewer.set_capture_mode(False)
            self._status.clearMessage()
            self._on_component_selected(last_id)
            return

        # When entering a continuous placement mode, reset counters
        if mode in self._CONTINUOUS_MODES and prev_mode not in self._CONTINUOUS_MODES:
            self._last_placed_object_id = None
            self._mode_place_count = 0

        self._canvas_mode = mode
        self._add_target_object_id = target_object_id
        # ALIGN_FOOTPRINT uses item-level dragging, not viewer capture mode
        capture = mode not in (CanvasMode.NORMAL, CanvasMode.ALIGN_FOOTPRINT)
        self._viewer.set_capture_mode(capture)
        if mode == CanvasMode.ALIGN_FOOTPRINT:
            from PyQt6.QtWidgets import QGraphicsView
            self._viewer.setDragMode(QGraphicsView.DragMode.NoDrag)
        if mode == CanvasMode.ADD_VIA:
            n = self._mode_place_count
            hint = f" ({n} placed)" if n else ""
            self._status.showMessage(
                f"ADD VIA{hint} — click to place  |  Middle-mouse to pan  |  Esc to finish"
            )
        elif mode == CanvasMode.ADD_COMPONENT:
            if target_object_id is not None:
                self._status.showMessage("DRAW OUTLINE — click and drag  |  Middle-mouse to pan  |  Esc to cancel")
            else:
                n = self._mode_place_count
                hint = f" ({n} placed)" if n else ""
                self._status.showMessage(
                    f"ADD COMPONENT{hint} — click and drag to draw bounding box  |  Middle-mouse to pan  |  Esc to finish"
                )
        elif mode == CanvasMode.ADD_TEXT:
            n = self._mode_place_count
            hint = f" ({n} placed)" if n else ""
            self._status.showMessage(
                f"ADD TEXT{hint} — click to place  |  Middle-mouse to pan  |  Esc to finish"
            )
        elif mode == CanvasMode.SET_ORIENTATION:
            self._status.showMessage("ORIENTATION — click the edge that is the pin-1/notch side  |  Middle-mouse to pan  |  Esc to cancel")
        elif mode == CanvasMode.ADD_PIN:
            count = len(self._pending_pin_items)
            self._status.showMessage(
                f"ADD PINS — click to place ({count} pending)  |  Enter to confirm  |  Esc to cancel"
            )
        elif mode == CanvasMode.ADD_TRACE:
            n = self._mode_place_count
            placed_hint = f" ({n} placed)" if n else ""
            pts = len(self._trace_points)
            if pts == 0:
                self._status.showMessage(
                    f"ADD TRACE{placed_hint} — click a via or pad to start  |  Esc to finish"
                )
            else:
                self._status.showMessage(
                    f"ADD TRACE{placed_hint} — {pts} point(s) — click to extend  |  "
                    f"click via/pad then Enter to commit  |  Esc to cancel"
                )
        else:
            self._status.clearMessage()

    def keyPressEvent(self, event) -> None:
        if self._canvas_mode == CanvasMode.ALIGN_FOOTPRINT:
            self._handle_alignment_key(event)
            return
        if self._canvas_mode == CanvasMode.ADD_PIN:
            if event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
                self._confirm_pin_placement()
                return
            if event.key() == Qt.Key.Key_Escape:
                self._cancel_pin_placement()
                self._set_canvas_mode(CanvasMode.NORMAL)
                return
        if self._canvas_mode == CanvasMode.ADD_TRACE:
            if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
                self._commit_trace()
                return
            if event.key() == Qt.Key.Key_Escape:
                if self._trace_points:
                    # Cancel in-progress route, stay in ADD_TRACE
                    self._clear_trace_preview()
                    self._trace_points = []
                    self._trace_start_obj_id = None
                    self._trace_end_obj_id   = None
                    self._set_canvas_mode(CanvasMode.ADD_TRACE)
                else:
                    # Idle — exit mode (selects last committed trace via _CONTINUOUS_MODES exit logic)
                    self._set_canvas_mode(CanvasMode.NORMAL)
                return
        if event.key() == Qt.Key.Key_Escape and self._canvas_mode != CanvasMode.NORMAL:
            self._set_canvas_mode(CanvasMode.NORMAL)
        else:
            super().keyPressEvent(event)

    def _on_debug_click(
        self,
        sp: QPointF,
        in_bounds: bool,
        img_w: int,
        img_h: int,
        capture: bool,
        rb_set: bool,
        zoom: float,
    ) -> None:
        """Log a structured click event when crosshairs are active."""
        if not capture:
            return
        mode_name = self._canvas_mode.name
        scene_rect = self._viewer.scene().sceneRect()
        lines = [
            "<b>── canvas click ──</b>",
            f"  mode        : {mode_name}",
            f"  scene pos   : ({sp.x():.1f}, {sp.y():.1f}) px",
            f"  in_bounds   : {in_bounds}  (img_w={img_w} img_h={img_h})",
            f"  scene rect  : {scene_rect.width():.0f} × {scene_rect.height():.0f}",
            f"  zoom        : {zoom:.4f}×",
            f"  rb_anchor   : {'set' if rb_set else 'none'}",
            f"  board/layer : {self._active_board or '—'} / {self._active_layer or '—'}",
        ]
        self._log.append("<br>".join(lines))

    def _on_canvas_click(self, pt: QPointF):
        if self._canvas_mode == CanvasMode.NORMAL:
            self._status.showMessage(
                f"Clicked: ({pt.x():.1f}, {pt.y():.1f}) px  "
                f"Board: {self._active_board}  Layer: {self._active_layer}"
            )
            return

        board, layer = self._require_board_and_layer()
        if not board or not layer:
            self._set_canvas_mode(CanvasMode.NORMAL)
            return

        if self._canvas_mode == CanvasMode.ADD_VIA:
            self._place_via(pt, board, layer)
        elif self._canvas_mode == CanvasMode.ADD_COMPONENT:
            # First click: anchor for rubber-band
            self._viewer.start_rubber_band(pt)
        elif self._canvas_mode == CanvasMode.ADD_TEXT:
            self._place_text(pt, board, layer)
        elif self._canvas_mode == CanvasMode.ADD_TRACE:
            self._trace_click(pt, board, layer)
        elif self._canvas_mode == CanvasMode.SET_ORIENTATION:
            self._place_orientation(pt, board, layer)
        elif self._canvas_mode == CanvasMode.ADD_PIN:
            self._add_pending_pin(pt)

    def _on_canvas_release(self, pt: QPointF):
        if self._canvas_mode == CanvasMode.ADD_COMPONENT:
            board, layer = self._require_board_and_layer()
            if not board or not layer:
                self._set_canvas_mode(CanvasMode.NORMAL)
                return
            rect = self._viewer.finish_rubber_band()
            if rect is not None:
                self._place_component_rect(rect, board, layer)
            else:
                # Too small / cancelled — stay in ADD_COMPONENT mode
                self._set_canvas_mode(CanvasMode.ADD_COMPONENT)

    def _on_canvas_move(self, pt: QPointF):
        if self._canvas_mode == CanvasMode.NORMAL:
            self._status.showMessage(
                f"({pt.x():.0f}, {pt.y():.0f}) px   "
                f"{self._active_board or ''}  {self._active_layer or ''}"
            )
        elif self._canvas_mode == CanvasMode.SET_ORIENTATION:
            self._update_edge_preview(pt)
        elif self._canvas_mode == CanvasMode.ADD_TRACE:
            self._update_trace_preview(pt)

    def _px_to_mm(self, pt: QPointF) -> tuple[float, float]:
        """Convert scene-pixel coords to mm using the active layer's calibration."""
        board, layer = self._active_board, self._active_layer
        if not board or not layer:
            return float(pt.x()), float(pt.y())
        board_id  = self._db.get_or_create_board(board)
        layer_row = self._db.get_layer(board_id, layer)
        if not layer_row or not layer_row["calibration"]:
            return float(pt.x()), float(pt.y())
        cal = json.loads(layer_row["calibration"])
        px_per_mm = cal.get("px_per_mm", 20.0)
        return pt.x() / px_per_mm, pt.y() / px_per_mm

    def _place_via(self, pt: QPointF, board: str, layer: str) -> None:
        from PyQt6.QtWidgets import QInputDialog as _QID
        drill, ok = _QID.getDouble(
            self, "Via Drill Diameter", "Drill diameter (mm):",
            self._last_via_drill_mm, 0.05, 5.0, 2
        )
        if not ok:
            # Stay in ADD_VIA — just refresh status bar (no mode change)
            self._set_canvas_mode(CanvasMode.ADD_VIA)
            return

        x_mm, y_mm = self._px_to_mm(pt)
        board_id  = self._db.get_or_create_board(board)
        layer_row = self._db.get_layer(board_id, layer)
        if not layer_row:
            self._set_canvas_mode(CanvasMode.NORMAL)
            return

        obj_id = self._db.create_object(
            layer_id=layer_row["id"],
            obj_type="via",
            x_mm=x_mm, y_mm=y_mm,
            width_mm=drill, height_mm=drill,
            verified=1,
            properties={"drill_mm": drill, "manual": True},
        )
        self._last_via_drill_mm = drill
        self._last_placed_object_id = obj_id
        self._mode_place_count += 1
        self._reload_active_layer()
        # Refresh status bar with updated count, stay in ADD_VIA
        self._set_canvas_mode(CanvasMode.ADD_VIA)

    def _place_component_rect(self, rect, board: str, layer: str) -> None:
        """Place a component at the given scene rect (after rubber-band complete)."""
        from PyQt6.QtWidgets import QDialog as _QDialog
        board_id  = self._db.get_or_create_board(board)
        layer_row = self._db.get_layer(board_id, layer)
        if not layer_row:
            self._set_canvas_mode(CanvasMode.NORMAL)
            return

        cal = json.loads(layer_row["calibration"] or "{}")
        px_per_mm = cal.get("px_per_mm", 20.0)

        x_mm      = rect.x()      / px_per_mm
        y_mm      = rect.y()      / px_per_mm
        width_mm  = rect.width()  / px_per_mm
        height_mm = rect.height() / px_per_mm

        # drawn_px is the pixel-space ground truth used later for calibration refinement
        drawn_px = [rect.x(), rect.y(), rect.width(), rect.height()]

        # Log full coordinate chain so calibration errors are easy to spot
        self._log.append(
            "<b>── place component ──</b><br>"
            f"  rubber-band  : ({rect.x():.1f}, {rect.y():.1f})  "
            f"{rect.width():.1f} × {rect.height():.1f} px<br>"
            f"  px_per_mm    : {px_per_mm:.4f}<br>"
            f"  stored mm    : ({x_mm:.3f}, {y_mm:.3f})  "
            f"{width_mm:.3f} × {height_mm:.3f} mm<br>"
            f"  render back  : ({x_mm*px_per_mm:.1f}, {y_mm*px_per_mm:.1f})  "
            f"{width_mm*px_per_mm:.1f} × {height_mm*px_per_mm:.1f} px"
        )

        target_id = self._add_target_object_id
        if target_id is not None:
            # Updating an existing component outline — preserve drawn_px as ground truth
            existing = self._db.conn().execute(
                "SELECT properties FROM objects WHERE id=?", (target_id,)
            ).fetchone()
            existing_props = json.loads(existing["properties"] or "{}") if existing else {}
            existing_props["drawn_px"] = drawn_px
            self._db.update_object(
                target_id,
                x_mm=x_mm, y_mm=y_mm,
                width_mm=width_mm, height_mm=height_mm,
                properties=existing_props,
            )
            self._reload_active_layer()
            self._set_canvas_mode(CanvasMode.NORMAL)
            return

        # New component: ask for ref + part
        from PyQt6.QtWidgets import (
            QDialog, QDialogButtonBox, QFormLayout, QLineEdit, QVBoxLayout
        )
        dlg = QDialog(self)
        dlg.setWindowTitle("New Component")
        form = QFormLayout()
        ref_edit  = QLineEdit(); ref_edit.setPlaceholderText("e.g. U1")
        part_edit = QLineEdit(); part_edit.setPlaceholderText("e.g. SiI3512")
        form.addRow("Ref designator:", ref_edit)
        form.addRow("Part number:",    part_edit)
        btns = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        btns.accepted.connect(dlg.accept)
        btns.rejected.connect(dlg.reject)
        vl = QVBoxLayout(dlg)
        vl.addLayout(form)
        vl.addWidget(btns)
        if dlg.exec() != QDialog.DialogCode.Accepted:
            # Stay in ADD_COMPONENT — refresh status bar
            self._set_canvas_mode(CanvasMode.ADD_COMPONENT)
            return

        ref  = ref_edit.text().strip()
        part = part_edit.text().strip()
        if not ref:
            # Stay in ADD_COMPONENT even if ref was empty
            self._set_canvas_mode(CanvasMode.ADD_COMPONENT)
            return

        board_id = self._db.get_or_create_board(board)
        obj_id = self._db.create_object(
            layer_id=layer_row["id"],
            obj_type="component",
            x_mm=x_mm, y_mm=y_mm,
            width_mm=width_mm, height_mm=height_mm,
            label=ref,
            verified=1,
            properties={"drawn_px": drawn_px, "manual": True},
        )
        self._db.upsert_component(
            board_id,
            ref_designator=ref,
            object_id=obj_id,
            part_number=part or None,
        )
        self._last_placed_object_id = obj_id
        self._mode_place_count += 1
        self._reload_active_layer()
        # Stay in ADD_COMPONENT, refresh status bar with updated count
        self._set_canvas_mode(CanvasMode.ADD_COMPONENT)

    def _place_text(self, pt: QPointF, board: str, layer: str) -> None:
        """Place a text_label at *pt* in continuous ADD_TEXT mode."""
        from PyQt6.QtWidgets import QInputDialog as _QID
        text, ok = _QID.getText(self, "Text Label", "Label text:")
        if not ok or not text.strip():
            # Stay in ADD_TEXT — just refresh status bar
            self._set_canvas_mode(CanvasMode.ADD_TEXT)
            return

        x_mm, y_mm = self._px_to_mm(pt)
        board_id  = self._db.get_or_create_board(board)
        layer_row = self._db.get_layer(board_id, layer)
        if not layer_row:
            self._set_canvas_mode(CanvasMode.NORMAL)
            return

        obj_id = self._db.create_object(
            layer_id=layer_row["id"],
            obj_type="text_label",
            x_mm=x_mm, y_mm=y_mm,
            label=text.strip(),
            verified=1,
        )
        self._last_placed_object_id = obj_id
        self._mode_place_count += 1
        self._reload_active_layer()
        # Stay in ADD_TEXT, refresh status bar with updated count
        self._set_canvas_mode(CanvasMode.ADD_TEXT)

    # ── Trace placement ────────────────────────────────────────────────────

    _TRACE_SNAP_RADIUS_MM = 2.0   # snap to via/pad within this radius

    def _enter_trace_mode(self) -> None:
        """Ask for trace width (once per session entry) then enter ADD_TRACE mode."""
        from PyQt6.QtWidgets import QInputDialog as _QID
        w, ok = _QID.getDouble(
            self, "Trace Width", "Trace width (mm):",
            self._trace_width_mm, 0.01, 10.0, 3
        )
        if not ok:
            return
        self._trace_width_mm = w
        self._set_canvas_mode(CanvasMode.ADD_TRACE)

    def _snap_to_via_or_pad(
        self, x_mm: float, y_mm: float, layer_id: int
    ) -> tuple[float, float, int | None]:
        """Return (snapped_x, snapped_y, obj_id) — obj_id is None if no snap.

        Snaps to vias, pads, and pins (all point-like connection objects).
        """
        r = self._TRACE_SNAP_RADIUS_MM
        rows = self._db.conn().execute(
            """SELECT id, x_mm, y_mm FROM objects
               WHERE layer_id=? AND type IN ('via','pad','pin')
                 AND ABS(x_mm - ?) < ? AND ABS(y_mm - ?) < ?""",
            (layer_id, x_mm, r, y_mm, r),
        ).fetchall()
        if not rows:
            return x_mm, y_mm, None
        best = min(rows, key=lambda rw: (rw["x_mm"] - x_mm) ** 2 + (rw["y_mm"] - y_mm) ** 2)
        return best["x_mm"], best["y_mm"], best["id"]

    def _px_per_mm_for_active_layer(self) -> float:
        board, layer = self._active_board, self._active_layer
        if not board or not layer:
            return 20.0
        board_id  = self._db.get_or_create_board(board)
        layer_row = self._db.get_layer(board_id, layer)
        if not layer_row or not layer_row["calibration"]:
            return 20.0
        import json as _json
        return _json.loads(layer_row["calibration"]).get("px_per_mm", 20.0)

    def _trace_click(self, pt: QPointF, board: str, layer: str) -> None:
        """Handle a click in ADD_TRACE mode."""
        board_id  = self._db.get_or_create_board(board)
        layer_row = self._db.get_layer(board_id, layer)
        if not layer_row:
            return

        x_mm, y_mm = self._px_to_mm(pt)
        sx, sy, snap_id = self._snap_to_via_or_pad(x_mm, y_mm, layer_row["id"])

        if not self._trace_points:
            # First click — must be on a via, pad, or pin
            if snap_id is None:
                self._status.showMessage(
                    "ADD TRACE — first point must be on a via, pad, or pin  |  Esc to finish"
                )
                return
            self._trace_points = [(sx, sy)]
            self._trace_start_obj_id = snap_id
            self._trace_end_obj_id   = None
            self._draw_trace_anchor_dot(sx, sy)
            self._set_canvas_mode(CanvasMode.ADD_TRACE)
            return

        # Subsequent click — add waypoint (snap if near via/pad, otherwise free)
        last_x, last_y = self._trace_points[-1]
        if abs(sx - last_x) < 1e-6 and abs(sy - last_y) < 1e-6:
            return  # duplicate point, ignore

        self._trace_points.append((sx, sy))
        self._trace_end_obj_id = snap_id  # None if not snapped

        # Solidify the last committed segment as a permanent preview item
        self._solidify_last_segment()
        self._set_canvas_mode(CanvasMode.ADD_TRACE)

    def _solidify_last_segment(self) -> None:
        """Add a solid (non-dashed) preview line for the last committed segment."""
        from PyQt6.QtWidgets import QGraphicsLineItem as _GLI
        if len(self._trace_points) < 2:
            return
        sc = self._viewer.scene()
        if sc is None:
            return
        px_per_mm = self._px_per_mm_for_active_layer()
        x1, y1 = self._trace_points[-2]
        x2, y2 = self._trace_points[-1]
        line = _GLI(x1 * px_per_mm, y1 * px_per_mm, x2 * px_per_mm, y2 * px_per_mm)
        pen = QPen(THEME.trace_preview_color, 2)
        pen.setCosmetic(True)
        line.setPen(pen)
        line.setZValue(98)
        sc.addItem(line)
        self._trace_preview_items.append(line)

    def _commit_trace(self) -> None:
        """Validate and commit the in-progress trace on Enter."""
        if len(self._trace_points) < 2:
            self._status.showMessage(
                "ADD TRACE — need at least a start point + one more click  |  Esc to cancel"
            )
            return
        if self._trace_end_obj_id is None:
            self._status.showMessage(
                "ADD TRACE — last point must be on a via, pad, or pin before committing  |  Esc to cancel"
            )
            return

        board, layer = self._require_board_and_layer()
        if not board or not layer:
            return
        board_id  = self._db.get_or_create_board(board)
        layer_row = self._db.get_layer(board_id, layer)
        if not layer_row:
            return

        sx, sy = self._trace_points[0]
        props = {
            "waypoints":  [[x, y] for x, y in self._trace_points],
            "start_obj":  self._trace_start_obj_id,
            "end_obj":    self._trace_end_obj_id,
            "width":      self._trace_width_mm,
            # keep start/end for backward-compat with single-segment readers
            "start":      [sx, sy],
            "end":        list(self._trace_points[-1]),
        }
        obj_id = self._db.create_object(
            layer_id=layer_row["id"],
            obj_type="trace",
            x_mm=sx, y_mm=sy,
            verified=1,
            properties=props,
        )
        self._last_placed_object_id = obj_id
        self._mode_place_count += 1

        # Clear state for next trace
        self._clear_trace_preview()
        self._trace_points = []
        self._trace_start_obj_id = None
        self._trace_end_obj_id   = None

        self._reload_active_layer()
        self._set_canvas_mode(CanvasMode.ADD_TRACE)

    def _draw_trace_anchor_dot(self, x_mm: float, y_mm: float) -> None:
        """Place/move the start anchor dot at (x_mm, y_mm)."""
        from PyQt6.QtGui import QBrush as _QBrush
        from PyQt6.QtWidgets import QGraphicsEllipseItem as _GEI
        sc = self._viewer.scene()
        if sc is None:
            return
        r_px = 6
        px_per_mm = self._px_per_mm_for_active_layer()
        cx, cy = x_mm * px_per_mm, y_mm * px_per_mm
        if self._trace_anchor_dot is not None:
            try:
                sc.removeItem(self._trace_anchor_dot)
            except Exception:
                pass
        dot = _GEI(cx - r_px, cy - r_px, r_px * 2, r_px * 2)
        dot.setPen(QPen(THEME.trace_anchor_color, 2))
        dot.setBrush(_QBrush(QColor(THEME.trace_anchor_color.red(),
                                    THEME.trace_anchor_color.green(),
                                    THEME.trace_anchor_color.blue(), 140)))
        dot.setZValue(100)
        sc.addItem(dot)
        self._trace_anchor_dot = dot

    def _update_trace_preview(self, pt: QPointF) -> None:
        """Update the dashed live segment from the last point to the cursor."""
        from PyQt6.QtGui import QBrush as _QBrush
        from PyQt6.QtWidgets import (
            QGraphicsLineItem as _GLI,
            QGraphicsEllipseItem as _GEI,
        )
        sc = self._viewer.scene()
        if sc is None:
            return

        px_per_mm = self._px_per_mm_for_active_layer()
        x_mm, y_mm = self._px_to_mm(pt)

        # Snap ring for hover feedback
        board, layer = self._active_board, self._active_layer
        snap_id: int | None = None
        sx, sy = x_mm, y_mm
        if board and layer:
            board_id  = self._db.get_or_create_board(board)
            layer_row = self._db.get_layer(board_id, layer)
            if layer_row:
                sx, sy, snap_id = self._snap_to_via_or_pad(x_mm, y_mm, layer_row["id"])

        if self._trace_snap_ring is not None:
            try:
                sc.removeItem(self._trace_snap_ring)
            except Exception:
                pass
            self._trace_snap_ring = None

        if snap_id is not None:
            r_px = 10
            cx, cy_s = sx * px_per_mm, sy * px_per_mm
            ring = _GEI(cx - r_px, cy_s - r_px, r_px * 2, r_px * 2)
            ring.setPen(QPen(THEME.trace_snap_ring_color, 2))
            ring.setBrush(_QBrush(QColor(0, 0, 0, 0)))
            ring.setZValue(99)
            sc.addItem(ring)
            self._trace_snap_ring = ring
            end_x, end_y = sx * px_per_mm, sy * px_per_mm
        else:
            end_x, end_y = pt.x(), pt.y()

        # Remove old live-segment line (last item in preview_items if it's the dashed one)
        if (self._trace_preview_items
                and getattr(self._trace_preview_items[-1], "_is_live", False)):
            old = self._trace_preview_items.pop()
            try:
                sc.removeItem(old)
            except Exception:
                pass

        if not self._trace_points:
            return

        lx, ly = self._trace_points[-1]
        line = _GLI(lx * px_per_mm, ly * px_per_mm, end_x, end_y)
        pen  = QPen(THEME.trace_preview_color, 1)
        pen.setStyle(Qt.PenStyle.DashLine)
        pen.setCosmetic(True)
        line.setPen(pen)
        line.setZValue(98)
        line._is_live = True   # type: ignore[attr-defined]
        sc.addItem(line)
        self._trace_preview_items.append(line)

    def _clear_trace_preview(self) -> None:
        """Remove all transient trace preview graphics items."""
        sc = self._viewer.scene()
        for item in self._trace_preview_items:
            if sc is not None:
                try:
                    sc.removeItem(item)
                except Exception:
                    pass
        self._trace_preview_items = []
        for attr in ("_trace_anchor_dot", "_trace_snap_ring"):
            item = getattr(self, attr, None)
            if item is not None and sc is not None:
                try:
                    sc.removeItem(item)
                except Exception:
                    pass
                setattr(self, attr, None)

    # ── Photo enhancement ──────────────────────────────────────────────────

    def _on_photo_enhancement(self, params: dict) -> None:
        """Apply live enhancement to the active layer scene photo."""
        key = (self._active_board, self._active_layer)
        ls = self._layer_scenes.get(key)
        if ls is None:
            return
        ls.apply_photo_enhancement(
            brightness=params.get("brightness", 0),
            contrast=params.get("contrast", 1.0),
            gamma=params.get("gamma", 1.0),
            sharpen=params.get("sharpen", False),
            invert=params.get("invert", False),
        )

    # ── Pin placement ─────────────────────────────────────────────────────

    def _enter_add_pin_mode(self, component_object_id: int) -> None:
        """Enter ADD_PIN mode for the given component object."""
        if component_object_id == -1:
            # -1 is the "just reload" sentinel from _delete_selected_pin
            self._reload_active_layer()
            return
        board, layer = self._require_board_and_layer()
        if not board or not layer:
            return
        self._pin_target_object_id = component_object_id
        self._pending_pin_items = []
        self._set_canvas_mode(CanvasMode.ADD_PIN)

    def _add_pending_pin(self, pt: QPointF) -> None:
        """Add a temporary pin preview dot at scene position *pt*."""
        from PyQt6.QtGui import QBrush as _Brush
        from PyQt6.QtWidgets import QGraphicsEllipseItem as _Ellipse
        r = 4.0
        pc = THEME.pin_color
        dot = _Ellipse(pt.x() - r, pt.y() - r, r * 2, r * 2)
        dot.setPen(QPen(pc, 1))
        dot.setBrush(_Brush(QColor(pc.red(), pc.green(), pc.blue(), 180)))
        dot.setZValue(10)
        self._viewer.scene().addItem(dot)
        self._pending_pin_items.append((dot, pt))
        # Update status bar counter
        self._set_canvas_mode(CanvasMode.ADD_PIN)

    def _confirm_pin_placement(self) -> None:
        """Save all pending pin dots to the DB and exit ADD_PIN mode."""
        board, layer = self._require_board_and_layer()
        if not board or not layer:
            self._cancel_pin_placement()
            self._set_canvas_mode(CanvasMode.NORMAL)
            return

        if not self._pending_pin_items or self._pin_target_object_id is None:
            self._cancel_pin_placement()
            self._set_canvas_mode(CanvasMode.NORMAL)
            return

        board_id  = self._db.get_or_create_board(board)
        layer_row = self._db.get_layer(board_id, layer)
        if not layer_row:
            self._cancel_pin_placement()
            self._set_canvas_mode(CanvasMode.NORMAL)
            return

        cal       = json.loads(layer_row["calibration"] or "{}")
        px_per_mm = cal.get("px_per_mm", 20.0)
        layer_id  = layer_row["id"]

        saved = 0
        for _dot, pt in self._pending_pin_items:
            x_mm = pt.x() / px_per_mm
            y_mm = pt.y() / px_per_mm
            self._db.add_pin(layer_id, self._pin_target_object_id, x_mm, y_mm)
            saved += 1

        self._log.append(f"  Saved {saved} pin(s) for object {self._pin_target_object_id}")
        self._cancel_pin_placement()   # remove temp dots
        self._canvas_mode = CanvasMode.NORMAL   # avoid re-triggering cancel in _set_canvas_mode
        self._set_canvas_mode(CanvasMode.NORMAL)
        self._reload_active_layer()

    def _cancel_pin_placement(self) -> None:
        """Remove all temporary pin preview items from the scene."""
        for dot, _pt in self._pending_pin_items:
            self._viewer.scene().removeItem(dot)
        self._pending_pin_items = []
        self._pin_target_object_id = None

    def _on_selection_changed(self):
        items = self._viewer.scene().selectedItems()
        key = (self._active_board, self._active_layer)
        ls = self._layer_scenes.get(key)

        if not items:
            self._inspector.clear()
            if ls:
                ls.clear_highlight()
            return

        item = items[0]
        obj_id = item.data(0)   # stored in _make_item
        if obj_id is None:
            return

        # Highlight the selected object on the canvas
        if ls:
            ls.highlight_object(obj_id)

        # Check if this is a pin object — show pin panel + parent component
        obj_row = self._db.conn().execute(
            "SELECT type FROM objects WHERE id=?", (obj_id,)
        ).fetchone()
        if obj_row and obj_row["type"] == "pin":
            self._inspector.show_pin(obj_id)
            return

        # Find the component linked to this object
        row = self._db.conn().execute(
            "SELECT id FROM components WHERE object_id=?", (obj_id,)
        ).fetchone()
        if row:
            self._inspector.show_component(row["id"])
        else:
            self._inspector.show_object(obj_id)

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

        board_dir = self._db.get_board_abs_dir(board)
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
        self._tree.refresh(self._tree.get_full_vis_state())
        if saved and self._active_board and self._active_layer:
            key = (self._active_board, self._active_layer)
            if key in self._layer_scenes:
                del self._layer_scenes[key]
            self._open_layer(self._active_board, self._active_layer)

    def _require_board_and_layer(self) -> tuple[str | None, str | None]:
        if not self._active_board:
            QMessageBox.warning(self, "No board selected", "Select a board first.")
            return None, None
        if not self._active_layer:
            QMessageBox.warning(self, "No layer selected",
                                "Select a layer in the tree first.")
            return None, None
        return self._active_board, self._active_layer

    def _run_scan_layer(self, initial_scan_type: str | None = None, initial_opts: dict | None = None):
        """Open the unified Scan Layer wizard, run the scan, show preview, save on confirm."""
        board, layer = self._require_board_and_layer()
        if not board or not layer:
            return

        board_id  = self._db.get_or_create_board(board)
        layer_row = self._db.get_layer(board_id, layer)
        if not layer_row or not layer_row["calibrated"]:
            QMessageBox.warning(
                self, "Not calibrated",
                f"{board} / {layer} must be calibrated before scanning.\n"
                "Right-click the layer → Calibrate…"
            )
            return

        wizard = ScanLayerWizard(board, layer, parent=self)
        if initial_scan_type:
            wizard.set_scan_type(initial_scan_type)
        if initial_opts:
            wizard.set_opts(initial_opts)

        if wizard.exec() != QDialog.DialogCode.Accepted:
            return

        scan_result = wizard.result()
        if scan_result is None:
            return

        # Show the preview dialog
        preview = ScanPreviewDialog(scan_result, parent=self)
        preview_code = preview.exec()

        if preview.needs_retry():
            # Re-open wizard with same scan type + opts
            retry_opts = preview.retry_opts()
            self._run_scan_layer(
                initial_scan_type=scan_result.scan_type,
                initial_opts=retry_opts,
            )
            return

        if preview_code != QDialog.DialogCode.Accepted:
            return

        confirmed = preview.confirmed_items()
        self._on_scan_layer_confirmed(scan_result.scan_type, confirmed, board, layer)

    def _on_scan_layer_confirmed(
        self,
        scan_type: str,
        items: list,
        board: str,
        layer: str,
    ):
        """Persist confirmed scan results to DB and refresh the canvas + tree."""
        board_id  = self._db.get_or_create_board(board)
        layer_row = self._db.get_layer(board_id, layer)
        if not layer_row:
            return

        layer_id = layer_row["id"]
        cal       = json.loads(layer_row["calibration"] or "{}")
        px_per_mm = cal.get("px_per_mm", 20.0)

        if scan_type == "text":
            # Convert any manually-added dict items to a BomEntry-compatible
            # object so save_scan_results can handle them uniformly.
            from types import SimpleNamespace
            wrapped = []
            for item in items:
                if isinstance(item, dict):
                    wrapped.append(SimpleNamespace(
                        label=item.get("label", ""),
                        reference=item.get("label", ""),
                        ref_type=item.get("ref_type", "RefDes"),
                        x_mm=float(item.get("x_mm", -1)),
                        y_mm=float(item.get("y_mm", -1)),
                        confidence=float(item.get("confidence", 1.0)),
                        engine="manual",
                        raw_text=item.get("label", ""),
                    ))
                else:
                    wrapped.append(item)
            n = self._db.save_scan_results(board_id, layer_id, wrapped)
        else:
            n = self._db.save_feature_objects(layer_id, scan_type, items, layer_key=layer)

        self._log.append(
            f"✓ Scan Layer ({scan_type}) — saved {n} objects to DB for {board}/{layer}"
        )

        # Reload canvas overlays and tree
        key = (board, layer)
        if key in self._layer_scenes:
            self._layer_scenes[key].load_objects(self._db, layer_id, px_per_mm)
            self._viewer.scene().update()

        vis = self._tree.get_full_vis_state()
        self._tree.refresh(vis)

    def _on_component_selected(self, obj_id: int):
        """Show component details in the inspector panel and vignette-highlight the item."""
        # Highlight in the active layer scene
        key = (self._active_board, self._active_layer)
        if key in self._layer_scenes:
            self._layer_scenes[key].highlight_object(obj_id)

        # Try to find a components table row for this object
        comp_row = self._db.conn().execute(
            "SELECT id FROM components WHERE object_id=?", (obj_id,)
        ).fetchone()
        if comp_row:
            self._inspector.show_component(comp_row["id"])
            return

        # Fallback: show raw object info in the MCP result field
        obj_row = self._db.conn().execute(
            "SELECT * FROM objects WHERE id=?", (obj_id,)
        ).fetchone()
        if not obj_row:
            return
        self._inspector.show_object(obj_id)

    # ── Entity CRUD handlers ──────────────────────────────────────────────

    def _on_entity_delete(self, object_id: int) -> None:
        """Delete a single object and refresh canvas + tree."""
        self._db.delete_object(object_id)
        self._reload_active_layer()

    def _on_entity_edit(self, object_id: int) -> None:
        """Called after an inline label edit — just refresh the canvas."""
        self._reload_active_layer()

    def _on_entity_verify(self, object_id: int) -> None:
        self._db.update_object(object_id, verified=1)
        self._reload_active_layer()

    def _on_merge_requested(self, object_ids: list) -> None:
        """Open MergeEntitiesDialog for the given text_label object_ids."""
        board, layer = self._require_board_and_layer()
        if not board or not layer:
            return
        board_id  = int(self._db.get_or_create_board(board))
        layer_row = self._db.get_layer(board_id, layer)
        if not layer_row:
            return

        dlg = MergeEntitiesDialog(object_ids, self._db, layer_row["id"], board_id, parent=self)
        if dlg.exec() != MergeEntitiesDialog.DialogCode.Accepted:
            return

        if dlg.new_object_id:
            self._log.append(
                f"Created component (id={dlg.new_object_id}) from {len(object_ids)} labels"
            )
            self._reload_active_layer()
            # Show the new component in the inspector
            comp_row = self._db.conn().execute(
                "SELECT id FROM components WHERE object_id=?", (dlg.new_object_id,)
            ).fetchone()
            if comp_row:
                self._inspector.show_component(comp_row["id"])

    def _on_draw_outline_requested(self, object_id: int) -> None:
        """Inspector 'Draw outline' button: enter ADD_COMPONENT mode to update object bounds."""
        board, layer = self._require_board_and_layer()
        if not board or not layer:
            return
        self._set_canvas_mode(CanvasMode.ADD_COMPONENT, target_object_id=object_id)

    def _on_set_orientation_requested(self, object_id: int) -> None:
        """Inspector '⊙ Orientation' button: enter SET_ORIENTATION mode."""
        board, layer = self._require_board_and_layer()
        if not board or not layer:
            return
        self._set_canvas_mode(CanvasMode.SET_ORIENTATION, target_object_id=object_id)

    def _get_object_scene_rect(self, object_id: int) -> tuple[float, float, float, float] | None:
        """Return the (x, y, w, h) scene-pixel rect of an object, or None."""
        obj_row = self._db.conn().execute(
            "SELECT x_mm, y_mm, width_mm, height_mm FROM objects WHERE id=?", (object_id,)
        ).fetchone()
        if not obj_row:
            return None
        board, layer = self._active_board, self._active_layer
        if not board or not layer:
            return None
        board_id  = self._db.get_or_create_board(board)
        layer_row = self._db.get_layer(board_id, layer)
        if not layer_row or not layer_row["calibration"]:
            return None
        cal = json.loads(layer_row["calibration"])
        ppm = cal.get("px_per_mm", 20.0)
        x  = obj_row["x_mm"]    * ppm
        y  = obj_row["y_mm"]    * ppm
        w  = obj_row["width_mm"]  * ppm
        h  = obj_row["height_mm"] * ppm
        return x, y, w, h

    def _update_edge_preview(self, pt: QPointF) -> None:
        """Draw/update a cyan dashed line over the nearest edge of the target component."""
        if self._add_target_object_id is None:
            return
        bounds = self._get_object_scene_rect(self._add_target_object_id)
        if bounds is None:
            return
        from toolkit.analysis.orientation import nearest_edge, edge_midpoint
        from PyQt6.QtWidgets import QGraphicsLineItem
        from PyQt6.QtCore import Qt as _Qt
        bx, by, bw, bh = bounds
        edge = nearest_edge(pt.x(), pt.y(), bx, by, bw, bh)

        # Compute the two endpoints of that edge
        if edge == "top":
            x1, y1, x2, y2 = bx, by, bx + bw, by
        elif edge == "bottom":
            x1, y1, x2, y2 = bx, by + bh, bx + bw, by + bh
        elif edge == "left":
            x1, y1, x2, y2 = bx, by, bx, by + bh
        else:  # right
            x1, y1, x2, y2 = bx + bw, by, bx + bw, by + bh

        sc = self._viewer.scene()
        if sc is None:
            return

        # Remove old preview
        if self._edge_preview_item is not None:
            try:
                sc.removeItem(self._edge_preview_item)
            except Exception:
                pass
            self._edge_preview_item = None

        pen = QPen(THEME.footprint_xhair_color)
        pen.setStyle(Qt.PenStyle.DashLine)
        pen.setWidth(3)
        pen.setCosmetic(True)
        item = QGraphicsLineItem(x1, y1, x2, y2)
        item.setPen(pen)
        item.setZValue(200)
        sc.addItem(item)
        self._edge_preview_item = item

    def _clear_edge_preview(self) -> None:
        if self._edge_preview_item is not None:
            sc = self._viewer.scene()
            if sc is not None:
                try:
                    sc.removeItem(self._edge_preview_item)
                except Exception:
                    pass
            self._edge_preview_item = None

    def _place_orientation(self, pt: QPointF, board: str, layer: str) -> None:
        """Snap click to nearest edge of the target component and save pin1_edge."""
        from toolkit.analysis.orientation import nearest_edge
        obj_id = self._add_target_object_id
        if obj_id is None:
            self._set_canvas_mode(CanvasMode.NORMAL)
            return
        bounds = self._get_object_scene_rect(obj_id)
        if bounds is None:
            self._log.append("⚠ Could not determine component bounds for orientation.")
            self._set_canvas_mode(CanvasMode.NORMAL)
            return
        bx, by, bw, bh = bounds
        edge = nearest_edge(pt.x(), pt.y(), bx, by, bw, bh)

        # Update properties in DB
        obj_row = self._db.conn().execute(
            "SELECT properties FROM objects WHERE id=?", (obj_id,)
        ).fetchone()
        if not obj_row:
            self._set_canvas_mode(CanvasMode.NORMAL)
            return
        props = json.loads(obj_row["properties"] or "{}")
        props["pin1_edge"] = edge
        self._db.conn().execute(
            "UPDATE objects SET properties=? WHERE id=?",
            (json.dumps(props), obj_id)
        )
        self._db.conn().commit()

        self._log.append(f"<b>Orientation set</b>: pin-1 edge = <b>{edge}</b> for object {obj_id}")
        self._set_canvas_mode(CanvasMode.NORMAL)
        self._reload_active_layer()
        self._on_component_selected(obj_id)  # re-select to refresh inspector

    def _on_refine_scale_requested(self, object_id: int) -> None:
        """Inspector 'Refine scale' button: compute new px_per_mm from known component size."""
        from PyQt6.QtWidgets import (
            QDialog, QDialogButtonBox, QDoubleSpinBox, QFormLayout, QLabel, QVBoxLayout
        )
        # Look up the label for a friendlier prompt
        obj_row = self._db.conn().execute(
            "SELECT label, properties FROM objects WHERE id=?", (object_id,)
        ).fetchone()
        if not obj_row:
            return
        props = json.loads(obj_row["properties"] or "{}")
        drawn_px = props.get("drawn_px")
        if not drawn_px:
            self._log.append("⚠ This component has no drawn_px — draw its outline first.")
            return
        _, _, dpx_w, dpx_h = drawn_px
        label = obj_row["label"] or f"object {object_id}"

        dlg = QDialog(self)
        dlg.setWindowTitle("Refine Scale from Datasheet")
        vl = QVBoxLayout(dlg)
        vl.addWidget(QLabel(
            f"<b>{label}</b> was drawn as <b>{dpx_w:.0f} × {dpx_h:.0f} px</b>.<br>"
            "Enter its physical dimensions from the datasheet to refine px/mm calibration.<br>"
            "<i>All manually drawn objects on this layer will be rescaled.</i>"
        ))
        form = QFormLayout()
        w_spin = QDoubleSpinBox(); w_spin.setRange(0.1, 500); w_spin.setDecimals(3)
        w_spin.setSuffix(" mm"); w_spin.setValue(round(dpx_w / 20.0, 2))
        h_spin = QDoubleSpinBox(); h_spin.setRange(0.1, 500); h_spin.setDecimals(3)
        h_spin.setSuffix(" mm"); h_spin.setValue(round(dpx_h / 20.0, 2))
        form.addRow("Component width:", w_spin)
        form.addRow("Component height:", h_spin)
        vl.addLayout(form)
        btns = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        btns.accepted.connect(dlg.accept)
        btns.rejected.connect(dlg.reject)
        vl.addWidget(btns)
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return

        known_w = w_spin.value()
        known_h = h_spin.value()
        try:
            new_ppm = self._db.refine_calibration_from_component(
                object_id, known_w, known_h
            )
        except ValueError as exc:
            self._log.append(f"⚠ Refine scale failed: {exc}")
            return

        self._log.append(
            f"<b>Calibration refined</b> from <i>{label}</i>:<br>"
            f"  known size  : {known_w:.3f} × {known_h:.3f} mm<br>"
            f"  drawn px    : {dpx_w:.0f} × {dpx_h:.0f} px<br>"
            f"  new px/mm   : {new_ppm:.4f}"
        )
        self._reload_active_layer()

    def _reload_active_layer(self) -> None:
        """Reload canvas objects and rebuild tree for the active board/layer."""
        board, layer = self._active_board, self._active_layer
        if not board or not layer:
            return
        board_id  = self._db.get_or_create_board(board)
        layer_row = self._db.get_layer(board_id, layer)
        if not layer_row:
            return
        cal       = json.loads(layer_row["calibration"] or "{}")
        px_per_mm = cal.get("px_per_mm", 20.0)
        key = (board, layer)
        if key in self._layer_scenes:
            self._layer_scenes[key].load_objects(self._db, layer_row["id"], px_per_mm)
            self._viewer.scene().update()
        vis = self._tree.get_full_vis_state()
        self._tree.refresh(vis)

    def _scan_datasheet(self, board: str, layer: str, object_id: int) -> None:
        """Open the datasheet scan dialog for a component / text_label object."""
        # Resolve the part number label from the object row
        obj_row = self._db.conn().execute(
            "SELECT label, properties FROM objects WHERE id=?", (object_id,)
        ).fetchone()
        if not obj_row:
            return
        part_number = obj_row["label"] or ""
        if not part_number:
            import json as _j
            props = _j.loads(obj_row["properties"] or "{}")
            part_number = props.get("part_number") or props.get("ref", "") or "?"

        # Default folder: the board's own datasheets/ directory
        default_folder = self._db.get_board_abs_dir(board) / "datasheets"
        if not default_folder.is_dir():
            default_folder = REPO_ROOT

        dlg = DatasheetScanDialog(part_number, default_folder, parent=self)
        if dlg.exec() != DatasheetScanDialog.DialogCode.Accepted:
            return

        if not dlg.selected_paths:
            return

        # Ensure a components row exists (needed for text_label objects)
        self._db.ensure_component_row(object_id)

        linked = 0
        for pdf_path in dlg.selected_paths:
            ds_id = self._db.get_or_create_datasheet_by_path(pdf_path, part_number)
            self._db.link_object_datasheet(object_id, ds_id)
            linked += 1

        self._log.append(
            f"Linked {linked} datasheet(s) to {part_number} ({board}/{layer})"
        )

        # Refresh inspector to show the newly linked datasheets
        self._on_component_selected(object_id)

    def _find_datasheet(self, object_id: int, part_number: str, mode: str) -> None:
        """Open the DatasheetFindDialog for *object_id* in the given *mode*."""
        board = self._active_board or ""
        board_dir = self._db.get_board_abs_dir(board) / "datasheets"

        dlg = DatasheetFindDialog(
            part_number,
            board_dir,
            initial_mode=mode,
            parent=self,
        )
        if dlg.exec() != DatasheetFindDialog.DialogCode.Accepted:
            return
        if not dlg.selected_path:
            return

        self._db.ensure_component_row(object_id)
        ds_id = self._db.get_or_create_datasheet_by_path(dlg.selected_path, part_number)
        self._db.link_object_datasheet(object_id, ds_id)

        self._log.append(
            f"Linked datasheet '{dlg.selected_path.name}' to {part_number} ({board})"
        )
        self._on_component_selected(object_id)

    # ── Pinout wizard ──────────────────────────────────────────────────────

    def _open_pinout_wizard(self, object_id: int, pdf_path: str) -> None:
        """Open the pinout extraction wizard for a component + datasheet."""
        pdf = Path(pdf_path)
        if not pdf.exists():
            self._log.append(f"⚠ PDF not found: {pdf_path}")
            return

        # Resolve datasheet_id from path
        ds_rows = self._db.get_object_datasheets(object_id)
        datasheet_id = next(
            (ds["id"] for ds in ds_rows if ds["file_path"] == pdf_path), None
        )
        # Resolve component_id
        comp_row = self._db.conn().execute(
            "SELECT id FROM components WHERE object_id = ?", (object_id,)
        ).fetchone()
        if comp_row is None:
            self._db.ensure_component_row(object_id)
            comp_row = self._db.conn().execute(
                "SELECT id FROM components WHERE object_id = ?", (object_id,)
            ).fetchone()
        component_id = comp_row["id"]

        wiz = DatasheetPinoutWizard(
            pdf_path=pdf,
            datasheet_id=datasheet_id,
            component_id=component_id,
            parent=self,
        )
        if wiz.exec() != DatasheetPinoutWizard.DialogCode.Accepted:
            return
        if not wiz.result:
            return

        # Save to DB (without alignment coords yet — x_rel/y_rel set in align step)
        result = wiz.result
        pinout_id = self._db.save_component_pinout(
            component_id,
            datasheet_id=datasheet_id,
            source_page=result.source_page,
            source_bbox=result.source_bbox.to_dict(),
            pins=result.to_db_pins(),
        )
        self._footprint_pinout_id = pinout_id
        self._footprint_object_id = object_id

        self._log.append(
            f"Pinout saved: {len(result.pads)} pads.  "
            "Align the footprint on the canvas — press R, +/-, arrows, then Enter."
        )
        self._start_pinout_alignment(result, object_id)

    def _open_footprint_picker(self, object_id: int) -> None:
        """Open the KiCad footprint picker for a component."""
        from toolkit.analysis.datasheet_package import extract_package_hints
        from toolkit.analysis.kicad_footprint import footprint_to_pad_detections
        from toolkit.analysis.pinout import BBox, PinoutResult

        # Resolve component_id and pre-fill search query from part/package fields
        comp_row = self._db.conn().execute(
            "SELECT id, part_number, package FROM components WHERE object_id = ?",
            (object_id,),
        ).fetchone()
        if comp_row is None:
            self._db.ensure_component_row(object_id)
            comp_row = self._db.conn().execute(
                "SELECT id, part_number, package FROM components WHERE object_id = ?",
                (object_id,),
            ).fetchone()
        component_id = comp_row["id"]

        # Pre-fill the search query: prefer package (e.g. "SOIC-8"), then part_number
        initial_query = (comp_row["package"] or comp_row["part_number"] or "").strip()

        # Extract package hints from linked datasheets; keep first valid PDF for match scoring
        hints = []
        best_pdf: Path | None = None
        ds_rows = self._db.get_object_datasheets(object_id)
        for ds in ds_rows:
            pdf_path = Path(ds["file_path"])
            if pdf_path.suffix.lower() == ".pdf" and pdf_path.exists():
                if best_pdf is None:
                    best_pdf = pdf_path
                if not hints:
                    try:
                        hints = extract_package_hints(pdf_path)
                    except Exception:
                        pass

        dlg = FootprintPickerDialog(
            initial_query=initial_query,
            hints=hints or None,
            datasheet_pdf=best_pdf,
            parent=self,
        )
        if dlg.exec() != FootprintPickerDialog.DialogCode.Accepted:
            return
        fp = dlg.selected_footprint
        if fp is None or not fp.pads:
            return

        pads, _bbox_mm = footprint_to_pad_detections(fp)

        result = PinoutResult(
            pads=pads,
            image_width=1000,
            image_height=1000,
            source_page=0,
            source_bbox=BBox(0.0, 0.0, 1.0, 1.0),
        )

        pinout_id = self._db.save_component_pinout(
            component_id,
            datasheet_id=None,
            source_page=0,
            source_bbox=None,
            pins=result.to_db_pins(),
            source="kicad_library",
        )
        self._footprint_pinout_id = pinout_id
        self._footprint_object_id = object_id

        self._log.append(
            f'KiCad footprint "{fp.library}/{fp.name}" imported: '
            f"{len(fp.pads)} pads.  "
            "Align the footprint on the canvas — press R, +/-, arrows, then Enter."
        )
        self._start_pinout_alignment(result, object_id)

    def _start_pinout_alignment(self, result, object_id: int) -> None:
        """Place a FootprintOverlayItem on the canvas and enter alignment mode."""
        board, layer = self._active_board, self._active_layer
        if not board or not layer:
            self._log.append("⚠ No active layer — cannot align footprint.")
            return

        board_id = self._db.get_or_create_board(board)
        layer_row = self._db.get_layer(board_id, layer)
        cal = json.loads(layer_row["calibration"]) if (layer_row and layer_row["calibration"]) else {}
        px_per_mm = cal.get("px_per_mm", 20.0)

        # Get component bounding box in scene units
        obj = self._db.get_object(object_id)
        if not obj:
            return
        w_scene = (obj["width_mm"]  or 5.0) * px_per_mm
        h_scene = (obj["height_mm"] or 5.0) * px_per_mm
        cx_scene = ((obj["x_mm"] or 0.0) + (obj["width_mm"] or 5.0) / 2) * px_per_mm
        cy_scene = ((obj["y_mm"] or 0.0) + (obj["height_mm"] or 5.0) / 2) * px_per_mm

        # Remove any existing overlay
        self._cancel_footprint_alignment()

        overlay = FootprintOverlayItem(
            pads=result.pads,
            component_w_scene=w_scene,
            component_h_scene=h_scene,
        )
        scene = self._viewer.scene()
        scene.addItem(overlay)
        overlay.setPos(cx_scene - w_scene / 2, cy_scene - h_scene / 2)
        self._footprint_overlay = overlay

        self._set_canvas_mode(CanvasMode.ALIGN_FOOTPRINT)
        self.statusBar().showMessage(
            "Aligning footprint — Drag to move · R: rotate 90° · +/-: scale · Arrows: fine-move · Enter: confirm · Esc: cancel"
        )

    def _handle_alignment_key(self, event) -> None:
        """Process keyboard shortcuts for footprint alignment mode."""
        overlay = self._footprint_overlay
        if overlay is None:
            self._set_canvas_mode(CanvasMode.NORMAL)
            return

        board, layer = self._active_board, self._active_layer
        cal = {}
        if board and layer:
            board_id = self._db.get_or_create_board(board)
            layer_row = self._db.get_layer(board_id, layer)
            cal = json.loads(layer_row["calibration"]) if (layer_row and layer_row["calibration"]) else {}
        px_per_mm = cal.get("px_per_mm", 20.0)
        step = 0.5 * px_per_mm   # 0.5 mm in scene units

        key = event.key()
        modifiers = event.modifiers()

        if key == Qt.Key.Key_R:
            deg = -90 if (modifiers & Qt.KeyboardModifier.ShiftModifier) else 90
            overlay.rotate_by(deg)
        elif key in (Qt.Key.Key_Plus, Qt.Key.Key_Equal):
            overlay.scale_by(1.1)
        elif key == Qt.Key.Key_Minus:
            overlay.scale_by(0.9)
        elif key == Qt.Key.Key_Left:
            overlay.translate(-step, 0)
        elif key == Qt.Key.Key_Right:
            overlay.translate(step, 0)
        elif key == Qt.Key.Key_Up:
            overlay.translate(0, -step)
        elif key == Qt.Key.Key_Down:
            overlay.translate(0, step)
        elif key in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            self._confirm_footprint_alignment()
        elif key == Qt.Key.Key_Escape:
            self._cancel_footprint_alignment()
        else:
            super().keyPressEvent(event)

    def _confirm_footprint_alignment(self) -> None:
        """Save aligned pin positions to DB, create pad objects on canvas."""
        overlay   = self._footprint_overlay
        pinout_id = self._footprint_pinout_id
        object_id = self._footprint_object_id
        if overlay is None or pinout_id is None or object_id is None:
            self._cancel_footprint_alignment()
            return

        board, layer = self._active_board, self._active_layer
        cal = {}
        if board and layer:
            board_id = self._db.get_or_create_board(board)
            layer_row = self._db.get_layer(board_id, layer)
            cal = json.loads(layer_row["calibration"]) if (layer_row and layer_row["calibration"]) else {}
        px_per_mm = cal.get("px_per_mm", 20.0)

        obj = self._db.get_object(object_id)
        if not obj:
            self._cancel_footprint_alignment()
            return
        ox_mm  = obj["x_mm"]     or 0.0
        oy_mm  = obj["y_mm"]     or 0.0
        ow_mm  = obj["width_mm"] or 5.0
        oh_mm  = obj["height_mm"] or 5.0

        # Use scene-space positions so pads outside the component body are allowed
        scene_coords = overlay.to_absolute_scene_coords()

        # Update x_rel / y_rel on each pin row (values may be outside [0,1])
        pin_rows = self._db.get_component_pins(pinout_id)
        for row, coord in zip(pin_rows, scene_coords):
            x_mm  = coord["scene_x"] / px_per_mm
            y_mm  = coord["scene_y"] / px_per_mm
            x_rel = (x_mm - ox_mm) / ow_mm
            y_rel = (y_mm - oy_mm) / oh_mm
            self._db.update_pin(row["id"], x_rel=x_rel, y_rel=y_rel)
        self._db.confirm_component_pinout(pinout_id)

        # Create pad objects on the active layer using absolute mm coordinates
        if board and layer:
            board_id  = self._db.get_or_create_board(board)
            layer_row = self._db.get_layer(board_id, layer)
            if layer_row:
                pad_sz = 0.5   # mm
                for row, coord in zip(pin_rows, scene_coords):
                    x_mm = coord["scene_x"] / px_per_mm
                    y_mm = coord["scene_y"] / px_per_mm
                    lbl  = coord["pin_number"] or coord["label"] or ""
                    self._db.add_object(
                        layer_id=layer_row["id"],
                        obj_type="pad",
                        x_mm=x_mm,
                        y_mm=y_mm,
                        width_mm=pad_sz,
                        height_mm=pad_sz,
                        label=lbl,
                        confidence=None,
                        properties=json.dumps({"shape": coord.get("shape", "circle")}),
                    )

        n = len(scene_coords)
        self._log.append(f"✓ Footprint confirmed: {n} pad(s) saved.")
        self._cancel_footprint_alignment()

        # Reload the scene to show the new pads
        if board and layer:
            self._load_layer_into_scene(board, layer)

    def _cancel_footprint_alignment(self) -> None:
        """Remove overlay and return to normal mode."""
        if self._footprint_overlay is not None:
            scene = self._viewer.scene()
            if scene:
                scene.removeItem(self._footprint_overlay)
            self._footprint_overlay = None
        self._footprint_object_id = None
        self._footprint_pinout_id = None
        if self._canvas_mode == CanvasMode.ALIGN_FOOTPRINT:
            self._set_canvas_mode(CanvasMode.NORMAL)

    def _remove_layer_data(self, board: str, layer: str, type_filter: str):
        """Delete objects from the DB for a layer (or a specific type within it)."""
        board_id  = self._db.get_or_create_board(board)
        layer_row = self._db.get_layer(board_id, layer)
        if not layer_row:
            return

        label = f"{board}/{layer}" + (f" [{type_filter}]" if type_filter else " [all]")
        reply = QMessageBox.question(
            self,
            "Remove data",
            f"Remove all {type_filter or 'extracted'} data for {label}?\n\nThis cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        self._db.delete_objects(layer_row["id"], type_filter or None)
        self._log.append(
            f"Removed {'all' if not type_filter else type_filter} objects for {label}"
        )

        # Clear the canvas overlay for this layer
        key = (board, layer)
        if key in self._layer_scenes:
            cal = json.loads(layer_row["calibration"] or "{}")
            px_per_mm = cal.get("px_per_mm", 20.0)
            self._layer_scenes[key].load_objects(self._db, layer_row["id"], px_per_mm)

        # Rebuild tree to remove component children
        vis = self._tree.get_full_vis_state()
        self._tree.refresh(vis)

    def _run_generate_kicad(self):
        board = self._require_board()
        if not board:
            return
        self._log.clear()
        self._log.append(f"Generating KiCad PCB for {board} …")
        self._log.set_busy(True)

        output = self._db.get_board_abs_dir(board) / f"{board}.kicad_pcb"
        cmd = [
            sys.executable, "-m", "toolkit.analysis.kicad",
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

    def _run_coord_calibrate(self):
        self._log.clear()
        self._log.append("Starting coordinate calibration diagnostic …")
        self._log.set_busy(True)

        cmd = [sys.executable, "-m", "toolkit.analysis.calibrate", "--calibrate"]
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
        self._tree.refresh(self._tree.get_full_vis_state())
        self._log.append("Imported all calibration.json files into r1mx.db")

    def _index_datasheets(self):
        self._db.index_datasheets()
        self._log.append("Datasheet index updated.")

    # ── Probe wizard ──────────────────────────────────────────────────────

    def _run_probe_wizard(self):
        """Open (or bring to front) the probe wizard for the active board."""
        if not self._active_board:
            QMessageBox.information(self, "No board", "Open a board first.")
            return
        board_id = int(self._db.get_or_create_board(self._active_board))
        scene = self._layer_scenes.get((self._active_board, self._active_layer or ""))

        if self._probe_wizard is None or not self._probe_wizard.isVisible():
            self._probe_wizard = ProbeWizardDialog(
                self._db, board_id, layer_scene=scene, parent=self
            )
            self._probe_wizard.componentStatusChanged.connect(
                self._on_probe_status_changed
            )
        self._probe_wizard.show()
        self._probe_wizard.raise_()
        self._probe_wizard.activateWindow()

    def _on_probe_status_changed(self, component_id: int, status: str):
        """Called when the wizard changes a component's status."""
        self._refresh_unresolved_count()

    def _refresh_unresolved_count(self):
        """Update the permanent status-bar label with the unresolved count."""
        if not self._active_board:
            self._unresolved_label.setText("")
            return
        board_id = int(self._db.get_or_create_board(self._active_board))
        n = self._db.count_unresolved_components(board_id)
        if n == 0:
            self._unresolved_label.setText("")
        else:
            self._unresolved_label.setText(f"⚠ {n} unresolved component{'s' if n != 1 else ''}")

    def _open_board_dir(self):
        if not self._active_board:
            return
        path = self._db.get_board_abs_dir(self._active_board)
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
        board_dir = self._db.get_board_abs_dir(board_name)
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
        self._tree.refresh(self._tree.get_full_vis_state())

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

    def _on_layer_added(self, board: str, layer_name: str) -> None:
        """Called after a new layer was created via the tree context menu."""
        self._log.append(f"Layer '{layer_name}' added to '{board}'.")
        self._status.showMessage(f"Added layer {board}/{layer_name}")

    def _on_layer_deleted(self, board: str, layer_name: str) -> None:
        """Called after a layer was deleted via the tree context menu."""
        key = (board, layer_name)
        if key in self._layer_scenes:
            scene = self._layer_scenes.pop(key)
            scene.set_all_visible(False)
        if self._active_board == board and self._active_layer == layer_name:
            self._active_layer = None
            self._db.set_state("active_layer", "")
            self._status.showMessage(f"Board: {board}")
        self._log.append(f"Layer '{layer_name}' deleted from '{board}'.")

    def _on_objects_shifted(self, board: str, layer_name: str) -> None:
        """Reload the canvas if the shifted layer is currently displayed."""
        if self._active_board == board and self._active_layer == layer_name:
            self._reload_active_layer()
        self._log.append(f"Objects shifted on '{board} / {layer_name}'.")

    def _edit_layer(self, board_name: str, layer_name: str):
        """Open the layer editor dialog and refresh state on save."""
        dlg = EditLayerDialog(self._db, board_name, layer_name, parent=self)
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return

        # If the layer was renamed, the old scene key is stale — drop it
        old_key = (board_name, layer_name)
        if old_key in self._layer_scenes:
            del self._layer_scenes[old_key]

        self._tree.refresh(self._tree.get_full_vis_state())
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
        board_dir = self._db.get_board_abs_dir(board_name)
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
            self._tree.refresh(self._tree.get_full_vis_state())
            # Reload canvas for the calibrated layer
            key = (board_name, layer_name)
            if key in self._layer_scenes:
                del self._layer_scenes[key]
            self._open_layer(board_name, layer_name)

    def _toggle_lcd_dock(self, checked: bool) -> None:
        if checked:
            self._lcd_dock.show()
        else:
            self._lcd_dock.hide()

    def _show_about(self):
        QMessageBox.about(
            self,
            "r1mx Toolkit",
            "<b>r1mx Toolkit</b><br><br>"
            "Reverse engineering assistant for the RED ONE MX digital cinema camera.<br><br>"
            "Workflow: Calibrate → Scan Layer (vias / pads / traces / text) → Generate KiCad PCB<br><br>"
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
