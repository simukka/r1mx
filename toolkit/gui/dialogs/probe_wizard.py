"""Probe Wizard — guided multimeter workflow for identifying unknown passives."""

from __future__ import annotations

import json

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor, QFont
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QSplitter,
    QStackedWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from toolkit.analysis.probe import ProbeStep, parse_value, resolve_probe_steps, snap_to_eia_series
from toolkit.db import DB

# Status colours for the queue list
_STATUS_COLORS: dict[str, str] = {
    "unknown":    "#888888",
    "probing":    "#e6b400",
    "measured":   "#3a9dda",
    "identified": "#4caf50",
    "verified":   "#2e7d32",
}


class _StepWidget(QWidget):
    """Widget showing a single ProbeStep: instructions + value input."""

    valueEntered = pyqtSignal(str, str)  # raw_value, selected_unit

    def __init__(self, step: ProbeStep, parent: QWidget | None = None):
        super().__init__(parent)
        self.step = step

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Title
        title = QLabel(step.title)
        title.setFont(QFont("sans-serif", 11, QFont.Weight.Bold))
        title.setWordWrap(True)
        layout.addWidget(title)

        # Optional badge
        if step.optional:
            opt_label = QLabel("  (optional)")
            opt_label.setStyleSheet("color: #888; font-style: italic;")
            layout.addWidget(opt_label)

        # In-circuit warning
        if step.in_circuit_warning:
            self._warn_box = QLabel(step.in_circuit_warning)
            self._warn_box.setWordWrap(True)
            self._warn_box.setStyleSheet(
                "background:#4a3800; color:#f5c518; padding:6px; border-radius:4px;"
            )
            self._warn_box.setVisible(False)
            layout.addWidget(self._warn_box)
        else:
            self._warn_box = None

        # Instructions text
        instr = QTextEdit()
        instr.setReadOnly(True)
        instr.setPlainText(step.instruction)
        instr.setMinimumHeight(140)
        instr.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        layout.addWidget(instr)

        # Value input row
        input_row = QHBoxLayout()
        input_row.addWidget(QLabel("Reading:"))
        self._value_edit = QLineEdit()
        self._value_edit.setPlaceholderText("e.g. 4.7k  or  220n  or  0.7")
        self._value_edit.returnPressed.connect(self._on_enter)
        input_row.addWidget(self._value_edit, stretch=1)

        self._unit_combo = QComboBox()
        for u in step.display_units:
            self._unit_combo.addItem(u)
        input_row.addWidget(self._unit_combo)
        layout.addLayout(input_row)

        # In-circuit checkbox
        self._in_circuit = QCheckBox("In-circuit (one lead still soldered)")
        self._in_circuit.setChecked(True)
        self._in_circuit.stateChanged.connect(self._on_in_circuit_changed)
        layout.addWidget(self._in_circuit)

        # Error label
        self._error_label = QLabel("")
        self._error_label.setStyleSheet("color: #e53935;")
        layout.addWidget(self._error_label)

    # ── Properties ─────────────────────────────────────────────────────────

    @property
    def in_circuit(self) -> bool:
        return self._in_circuit.isChecked()

    def raw_value(self) -> str:
        return self._value_edit.text().strip()

    def selected_unit(self) -> str:
        return self._unit_combo.currentText()

    def set_error(self, msg: str):
        self._error_label.setText(msg)

    def clear(self):
        self._value_edit.clear()
        self._error_label.setText("")

    def show_in_circuit_warning(self, show: bool):
        if self._warn_box is not None:
            self._warn_box.setVisible(show)

    # ── Slots ───────────────────────────────────────────────────────────────

    def _on_enter(self):
        self.valueEntered.emit(self.raw_value(), self.selected_unit())

    def _on_in_circuit_changed(self, _state: int):
        self.show_in_circuit_warning(self._in_circuit.isChecked())


class ProbeWizardDialog(QDialog):
    """Non-modal dialog that guides the user through measuring unknown components.

    Usage::

        wizard = ProbeWizardDialog(db, board_id, layer_scene=self._scene, parent=self)
        wizard.componentStatusChanged.connect(self._on_probe_status_changed)
        wizard.show()   # non-modal
    """

    componentStatusChanged = pyqtSignal(int, str)  # component_id, new_status

    def __init__(
        self,
        db: DB,
        board_id: int,
        *,
        layer_scene=None,   # LayerScene | None
        parent: QWidget | None = None,
    ):
        super().__init__(parent, Qt.WindowType.Window)
        self.setWindowTitle("Probe Wizard — Identify Components")
        self.resize(900, 620)
        self.setSizeGripEnabled(True)

        self._db          = db
        self._board_id    = board_id
        self._scene       = layer_scene
        self._components  : list[dict] = []  # list of dicts from DB rows
        self._current_idx : int = -1
        self._step_idx    : int = 0
        self._step_widgets: list[_StepWidget] = []

        self._build_ui()
        self._load_queue()

    # ── UI construction ─────────────────────────────────────────────────────

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(8, 8, 8, 8)

        splitter = QSplitter(Qt.Orientation.Horizontal, self)

        # ── Left panel: component queue ──────────────────────────────────
        left = QWidget()
        lv   = QVBoxLayout(left)
        lv.setContentsMargins(0, 0, 0, 0)

        queue_label = QLabel("Components to probe")
        queue_label.setFont(QFont("sans-serif", 10, QFont.Weight.Bold))
        lv.addWidget(queue_label)

        self._queue = QListWidget()
        self._queue.setMinimumWidth(200)
        self._queue.currentRowChanged.connect(self._on_queue_row_changed)
        lv.addWidget(self._queue)

        reload_btn = QPushButton("↺ Refresh queue")
        reload_btn.clicked.connect(self._load_queue)
        lv.addWidget(reload_btn)

        splitter.addWidget(left)

        # ── Right panel: step instructions ───────────────────────────────
        right = QWidget()
        rv    = QVBoxLayout(right)
        rv.setContentsMargins(8, 0, 0, 0)

        # Component heading
        self._comp_heading = QLabel("Select a component →")
        self._comp_heading.setFont(QFont("sans-serif", 13, QFont.Weight.Bold))
        self._comp_heading.setWordWrap(True)
        rv.addWidget(self._comp_heading)

        self._comp_detail = QLabel("")
        self._comp_detail.setWordWrap(True)
        self._comp_detail.setStyleSheet("color: #aaa;")
        rv.addWidget(self._comp_detail)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        rv.addWidget(sep)

        # Step progress label
        self._step_label = QLabel("")
        self._step_label.setStyleSheet("color: #888; font-style: italic;")
        rv.addWidget(self._step_label)

        # Stacked widget — one page per step
        self._step_stack = QStackedWidget()
        rv.addWidget(self._step_stack, stretch=1)

        # Button row
        btn_row = QHBoxLayout()

        self._prev_btn = QPushButton("← Previous step")
        self._prev_btn.setEnabled(False)
        self._prev_btn.clicked.connect(self._go_prev_step)
        btn_row.addWidget(self._prev_btn)

        btn_row.addStretch()

        self._skip_btn = QPushButton("Skip component")
        self._skip_btn.setEnabled(False)
        self._skip_btn.clicked.connect(self._skip_component)
        btn_row.addWidget(self._skip_btn)

        self._record_btn = QPushButton("Record & Next →")
        self._record_btn.setDefault(True)
        self._record_btn.setEnabled(False)
        self._record_btn.clicked.connect(self._record_and_advance)
        btn_row.addWidget(self._record_btn)

        self._identify_btn = QPushButton("✓ Mark Identified")
        self._identify_btn.setEnabled(False)
        self._identify_btn.setStyleSheet("background:#1b5e20; color:white; font-weight:bold;")
        self._identify_btn.clicked.connect(self._mark_identified)
        btn_row.addWidget(self._identify_btn)

        rv.addLayout(btn_row)

        splitter.addWidget(right)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 3)

        root.addWidget(splitter)

        # Bottom close button
        close_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        close_box.rejected.connect(self.close)
        root.addWidget(close_box)

    # ── Queue loading ────────────────────────────────────────────────────────

    def _load_queue(self):
        """Reload the component queue from the database."""
        self._queue.blockSignals(True)
        self._queue.clear()
        self._components = []

        rows = self._db.get_components_to_probe(self._board_id)
        for row in rows:
            d = dict(row)
            self._components.append(d)
            ref  = d.get("ref_designator") or "?"
            pkg  = d.get("package") or ""
            val  = d.get("value")   or ""
            status = d.get("status") or "unknown"

            label = ref
            if val:
                label += f"  {val}"
            if pkg:
                label += f"  [{pkg}]"

            item = QListWidgetItem(label)
            color = _STATUS_COLORS.get(status, "#888")
            item.setForeground(QColor(color))
            self._queue.addItem(item)

        self._queue.blockSignals(False)

        if self._components:
            self._queue.setCurrentRow(0)
        else:
            self._comp_heading.setText("All components identified! 🎉")
            self._comp_detail.setText("")
            self._step_stack.setVisible(False)
            self._record_btn.setEnabled(False)
            self._skip_btn.setEnabled(False)
            self._identify_btn.setEnabled(False)

    # ── Navigation ───────────────────────────────────────────────────────────

    def _on_queue_row_changed(self, row: int):
        if row < 0 or row >= len(self._components):
            return
        self._current_idx = row
        self._step_idx    = 0
        self._load_component(row)

    def _load_component(self, idx: int):
        comp = self._components[idx]
        ref   = comp.get("ref_designator") or "?"
        pkg   = comp.get("package") or ""
        val   = comp.get("value")   or ""
        desc  = comp.get("description") or ""
        ref_type = self._infer_ref_type(ref)

        # Update heading
        heading = ref
        if val:
            heading += f"  =  {val}"
        self._comp_heading.setText(heading)
        detail_parts = []
        if pkg:
            detail_parts.append(f"Package: {pkg}")
        if desc:
            detail_parts.append(desc)
        self._comp_detail.setText("  ·  ".join(detail_parts) if detail_parts else "")

        # Build step widgets
        while self._step_stack.count():
            w = self._step_stack.widget(0)
            self._step_stack.removeWidget(w)
            w.deleteLater()
        self._step_widgets = []

        steps = resolve_probe_steps(ref_type)
        for step in steps:
            sw = _StepWidget(step)
            self._step_stack.addWidget(sw)
            self._step_widgets.append(sw)

        self._step_stack.setVisible(True)
        self._show_step(0)

        # Mark as probing in DB
        comp_id = comp.get("id")
        if comp_id and (comp.get("status") or "unknown") == "unknown":
            self._db.update_component_status(comp_id, "probing")
            comp["status"] = "probing"
            self._update_queue_item_color(idx, "probing")
            self.componentStatusChanged.emit(comp_id, "probing")

        # Highlight in scene
        obj_id = comp.get("object_id")
        if self._scene is not None and obj_id:
            self._scene.highlight_object(obj_id)

        # Enable buttons
        self._skip_btn.setEnabled(True)
        self._record_btn.setEnabled(True)
        self._identify_btn.setEnabled(True)

    def _show_step(self, step_idx: int):
        self._step_idx = step_idx
        self._step_stack.setCurrentIndex(step_idx)
        total = len(self._step_widgets)
        self._step_label.setText(f"Step {step_idx + 1} of {total}")
        self._prev_btn.setEnabled(step_idx > 0)
        sw = self._step_widgets[step_idx]
        sw.show_in_circuit_warning(sw.in_circuit)

    def _go_prev_step(self):
        if self._step_idx > 0:
            self._show_step(self._step_idx - 1)

    # ── Recording ────────────────────────────────────────────────────────────

    def _record_and_advance(self):
        if self._current_idx < 0 or not self._step_widgets:
            return

        sw = self._step_widgets[self._step_idx]
        raw = sw.raw_value()

        if not raw:
            # Allow skipping individual steps (just advance)
            self._advance_step()
            return

        sw.set_error("")

        # Parse the value
        try:
            si_val, parsed_unit = parse_value(raw)
        except ValueError:
            sw.set_error(f"Could not parse '{raw}'. Try: 4.7k  220n  0.7  1.5M")
            return

        # Resolve unit: prefer parsed unit, fall back to combo selection
        unit = parsed_unit or sw.selected_unit()

        comp = self._components[self._current_idx]
        comp_id = comp.get("id")
        if comp_id is None:
            return

        # Save measurement
        self._db.save_measurement(
            comp_id,
            sw.step.measurement_type,
            raw,
            si_val,
            unit,
            orientation=sw.step.orientation,
            in_circuit=sw.in_circuit,
        )

        # Try EIA snap for R, C, L, DCR
        if sw.step.measurement_type in ("resistance", "capacitance", "inductance", "dcr"):
            snapped, formatted = snap_to_eia_series(abs(si_val))
            # Suggest the snapped value if value is not yet set
            if not comp.get("value"):
                self._db.conn().execute(
                    "UPDATE components SET value=? WHERE id=?",
                    (formatted + " " + unit, comp_id),
                )
                self._db.conn().commit()
                comp["value"] = formatted + " " + unit

        # Advance status to "measured" after any real recording
        if (comp.get("status") or "unknown") in ("unknown", "probing"):
            self._db.update_component_status(comp_id, "measured")
            comp["status"] = "measured"
            self._update_queue_item_color(self._current_idx, "measured")
            self.componentStatusChanged.emit(comp_id, "measured")

        self._advance_step()

    def _advance_step(self):
        """Advance to the next step; if all done, move to next component."""
        next_step = self._step_idx + 1
        if next_step < len(self._step_widgets):
            self._show_step(next_step)
        else:
            # All steps done — move to next component in queue
            self._next_component()

    def _skip_component(self):
        """Skip the current component without recording."""
        if self._scene is not None:
            self._scene.clear_highlight()
        self._next_component()

    def _next_component(self):
        """Select the next component in the queue."""
        if self._scene is not None:
            self._scene.clear_highlight()
        next_idx = self._current_idx + 1
        if next_idx < len(self._components):
            self._queue.setCurrentRow(next_idx)
        else:
            # Reload to see if anything new is in the queue
            self._load_queue()

    def _mark_identified(self):
        """Mark the current component as fully identified."""
        if self._current_idx < 0:
            return
        comp = self._components[self._current_idx]
        comp_id = comp.get("id")
        if comp_id is None:
            return
        self._db.update_component_status(comp_id, "identified")
        comp["status"] = "identified"
        self._update_queue_item_color(self._current_idx, "identified")
        self.componentStatusChanged.emit(comp_id, "identified")
        if self._scene is not None:
            self._scene.clear_highlight()
        # Remove from queue (it is now resolved)
        del self._components[self._current_idx]
        self._queue.takeItem(self._current_idx)
        new_row = min(self._current_idx, len(self._components) - 1)
        if new_row >= 0:
            self._queue.setCurrentRow(new_row)
        else:
            self._load_queue()

    # ── Helpers ──────────────────────────────────────────────────────────────

    def _infer_ref_type(self, ref_designator: str) -> str:
        """Extract the alphabetic prefix from a reference designator."""
        prefix = ""
        for ch in ref_designator:
            if ch.isalpha() or ch in ("_", "-"):
                prefix += ch.upper()
            else:
                break
        return prefix or ref_designator

    def _update_queue_item_color(self, idx: int, status: str):
        item = self._queue.item(idx)
        if item is not None:
            color = _STATUS_COLORS.get(status, "#888")
            item.setForeground(QColor(color))

    def closeEvent(self, event):
        if self._scene is not None:
            self._scene.clear_highlight()
        super().closeEvent(event)
