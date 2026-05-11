"""
datasheet_scan.py — DatasheetScanDialog

Dialog that lets the user scan a folder for PDF datasheets that match a
given part number.  Results stream in live as each PDF is scored.  Multiple
results can be selected via checkboxes, and the selected PDFs are returned
as ``selected_paths`` for the caller to register and link.

Layout::

    ┌──────────────────────────────────────────────────────┐
    │  Scan for datasheet: SII3512ECTU128                  │
    │                                                      │
    │  Folder: [/path/to/datasheets/]        [Browse…]    │
    │                                        [Scan]        │
    │  [████████████████░░░░░░░░░░]  14 / 20 PDFs         │
    │                                                      │
    │  Results (3 matches):               ☐ Show all      │
    │  ☑  1.00  SII3512ECTU128.pdf                        │
    │  ☑  0.71  SiI-DS-0107-C.pdf                        │
    │  ☐  0.38  SII3132.pdf                               │
    │                                                      │
    │                   [Cancel]  [Link selected (2)]      │
    └──────────────────────────────────────────────────────┘

Score thresholds
----------------
≥ 0.6   Pre-checked, normal text
≥ 0.2   Visible but unchecked, dimmed
< 0.2   Hidden unless "Show all" is ticked
"""

from __future__ import annotations

from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QFont
from PyQt6.QtWidgets import (
    QCheckBox,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QProgressBar,
    QPushButton,
    QVBoxLayout,
)

from toolkit.workers.datasheet_scan import DatasheetScanWorker

# Score thresholds
_THRESHOLD_HIGH = 0.6   # pre-checked, shown normally
_THRESHOLD_LOW  = 0.2   # shown unchecked/dimmed; below this, hidden by default

_COLOR_HIGH   = QColor(0, 0, 0)        # black
_COLOR_DIM    = QColor(140, 140, 140)  # grey
_COLOR_HIDDEN = QColor(200, 200, 200)  # very light grey (used when Show all)


class DatasheetScanDialog(QDialog):
    """Scan a folder for PDFs matching *part_number* and let the user link some."""

    def __init__(self, part_number: str, default_folder: Path | None = None, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Scan for datasheet: {part_number}")
        self.resize(580, 460)
        self.setSizeGripEnabled(True)

        self._part_number   = part_number
        self._worker: DatasheetScanWorker | None = None
        self._all_items: list[tuple[float, Path, QListWidgetItem]] = []
        self.selected_paths: list[Path] = []

        layout = QVBoxLayout(self)
        layout.setSpacing(8)

        # ── Header ──────────────────────────────────────────────────────────
        hdr = QLabel(f"Part number: <b>{part_number}</b>")
        layout.addWidget(hdr)

        # ── Folder picker row ────────────────────────────────────────────────
        folder_row = QHBoxLayout()
        self._folder_edit = QLineEdit()
        self._folder_edit.setPlaceholderText("Select a folder to scan…")
        if default_folder and default_folder.is_dir():
            self._folder_edit.setText(str(default_folder))
        browse_btn = QPushButton("Browse…")
        browse_btn.setFixedWidth(80)
        browse_btn.clicked.connect(self._browse)
        self._scan_btn = QPushButton("Scan")
        self._scan_btn.setFixedWidth(60)
        self._scan_btn.clicked.connect(self._start_scan)
        folder_row.addWidget(QLabel("Folder:"))
        folder_row.addWidget(self._folder_edit, 1)
        folder_row.addWidget(browse_btn)
        folder_row.addWidget(self._scan_btn)
        layout.addLayout(folder_row)

        # ── Progress bar ─────────────────────────────────────────────────────
        self._progress = QProgressBar()
        self._progress.setTextVisible(True)
        self._progress.setFormat("%v / %m PDFs")
        self._progress.setVisible(False)
        layout.addWidget(self._progress)

        # ── Results header (count + show-all toggle) ─────────────────────────
        results_row = QHBoxLayout()
        self._results_label = QLabel("Results:")
        results_row.addWidget(self._results_label)
        results_row.addStretch()
        self._show_all_cb = QCheckBox("Show all")
        self._show_all_cb.stateChanged.connect(self._apply_visibility)
        results_row.addWidget(self._show_all_cb)
        layout.addLayout(results_row)

        # ── Results list ─────────────────────────────────────────────────────
        self._list = QListWidget()
        self._list.setAlternatingRowColors(True)
        self._list.itemChanged.connect(self._update_link_button)
        layout.addWidget(self._list, 1)

        # ── Button box ───────────────────────────────────────────────────────
        self._btn_box = QDialogButtonBox()
        self._cancel_btn = self._btn_box.addButton(QDialogButtonBox.StandardButton.Cancel)
        self._link_btn   = self._btn_box.addButton("Link selected (0)", QDialogButtonBox.ButtonRole.AcceptRole)
        self._link_btn.setEnabled(False)
        self._cancel_btn.clicked.connect(self._on_cancel)
        self._link_btn.clicked.connect(self._on_accept)
        layout.addWidget(self._btn_box)

    # ── Folder browser ───────────────────────────────────────────────────────

    def _browse(self) -> None:
        current = self._folder_edit.text() or str(Path.home())
        chosen = QFileDialog.getExistingDirectory(self, "Select folder to scan", current)
        if chosen:
            self._folder_edit.setText(chosen)

    # ── Scan ─────────────────────────────────────────────────────────────────

    def _start_scan(self) -> None:
        folder = Path(self._folder_edit.text())
        if not folder.is_dir():
            self._results_label.setText("Results: (invalid folder)")
            return

        # Abort any running scan
        if self._worker and self._worker.isRunning():
            self._worker.abort()
            self._worker.wait()

        self._all_items.clear()
        self._list.clear()
        self._progress.setVisible(True)
        self._progress.setValue(0)
        self._scan_btn.setEnabled(False)
        self._results_label.setText("Scanning…")

        self._worker = DatasheetScanWorker(self._part_number, folder)
        self._worker.resultReady.connect(self._on_result)
        self._worker.progress.connect(self._on_progress)
        self._worker.finished.connect(self._on_finished)
        self._worker.start()

    def _on_result(self, score: float, path_str: str) -> None:
        """Add a result row as it arrives from the worker."""
        pdf = Path(path_str)
        checked = score >= _THRESHOLD_HIGH
        visible = self._show_all_cb.isChecked() or score >= _THRESHOLD_LOW

        item = QListWidgetItem()
        item.setText(f"  {score:.2f}  {pdf.name}")
        item.setData(Qt.ItemDataRole.UserRole, path_str)
        item.setCheckState(Qt.CheckState.Checked if checked else Qt.CheckState.Unchecked)

        if score >= _THRESHOLD_HIGH:
            item.setForeground(_COLOR_HIGH)
            font = item.font()
            font.setWeight(QFont.Weight.Bold)
            item.setFont(font)
        elif score >= _THRESHOLD_LOW:
            item.setForeground(_COLOR_DIM)
        else:
            item.setForeground(_COLOR_HIDDEN)

        self._list.addItem(item)
        item.setHidden(not visible)
        self._all_items.append((score, pdf, item))

    def _on_progress(self, done: int, total: int) -> None:
        self._progress.setMaximum(total)
        self._progress.setValue(done)

    def _on_finished(self, ok: bool, msg: str) -> None:
        self._scan_btn.setEnabled(True)
        self._progress.setVisible(False)
        visible_count = sum(1 for _, _, it in self._all_items if not it.isHidden())
        self._results_label.setText(f"Results ({visible_count} shown): {msg}")
        self._update_link_button()

    # ── Visibility / "Show all" toggle ───────────────────────────────────────

    def _apply_visibility(self) -> None:
        show_all = self._show_all_cb.isChecked()
        for score, _, item in self._all_items:
            item.setHidden(not show_all and score < _THRESHOLD_LOW)
        visible_count = sum(1 for _, _, it in self._all_items if not it.isHidden())
        total = len(self._all_items)
        self._results_label.setText(f"Results ({visible_count} / {total} shown):")
        self._update_link_button()

    # ── Link button label ────────────────────────────────────────────────────

    def _update_link_button(self) -> None:
        n = sum(
            1 for i in range(self._list.count())
            if self._list.item(i).checkState() == Qt.CheckState.Checked
        )
        self._link_btn.setText(f"Link selected ({n})")
        self._link_btn.setEnabled(n > 0)

    # ── Accept / cancel ──────────────────────────────────────────────────────

    def _on_accept(self) -> None:
        self.selected_paths = [
            Path(self._list.item(i).data(Qt.ItemDataRole.UserRole))
            for i in range(self._list.count())
            if self._list.item(i).checkState() == Qt.CheckState.Checked
        ]
        if self._worker and self._worker.isRunning():
            self._worker.abort()
            self._worker.wait()
        self.accept()

    def _on_cancel(self) -> None:
        if self._worker and self._worker.isRunning():
            self._worker.abort()
            self._worker.wait()
        self.reject()

    def closeEvent(self, event) -> None:
        if self._worker and self._worker.isRunning():
            self._worker.abort()
            self._worker.wait()
        super().closeEvent(event)
