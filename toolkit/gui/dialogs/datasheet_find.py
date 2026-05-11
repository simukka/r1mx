"""
datasheet_find.py — DatasheetFindDialog

Combined "find + review" dialog for locating datasheets for a component.
Two search modes (tabs):

  Filesystem — scan a local folder using DatasheetScanWorker (existing scorer)
  Internet   — query web sources via DatasheetFetchWorker; downloads to board dir

Both modes add candidates to a shared list.  Clicking a candidate renders its
first page (via pdftoppm) in an inline PDF viewer with prev/next navigation.
The user can link the visible PDF or skip it.

Layout::

    ┌──────────────────────────────────────────────────────────────────────┐
    │ Find datasheet: SII3512ECTU128                                       │
    │ ┌──────────────────────────┐  ┌──────────────────────────────────┐  │
    │ │ [Filesystem] [Internet]  │  │  [PDF page preview]              │  │
    │ │ ─────────────────────    │  │                                  │  │
    │ │ Folder: [...]  [Browse]  │  │                                  │  │
    │ │         [Scan]           │  │  Page N of M                     │  │
    │ │ ──── Candidates ────     │  │  [← Prev page]  [Next page →]   │  │
    │ │  0.9  local.pdf  ← sel  │  └──────────────────────────────────┘  │
    │ │  0.7  web1.pdf           │                                        │
    │ │  0.5  web2.pdf           │                                        │
    │ │  Progress: Wayback…      │                                        │
    │ └──────────────────────────┘                                        │
    │            [✓ Link this datasheet]  [✗ Skip candidate]  [Cancel]   │
    └──────────────────────────────────────────────────────────────────────┘
"""

from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QFont, QPixmap
from PyQt6.QtWidgets import (
    QCheckBox,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QSplitter,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from toolkit.workers.datasheet_fetch import DatasheetFetchWorker
from toolkit.workers.datasheet_scan import DatasheetScanWorker

_SCORE_HIGH  = 0.6   # pre-checked, bold
_SCORE_LOW   = 0.2   # dimmed; below → hidden unless "Show all"

_COL_HIGH    = QColor(0,   0,   0)
_COL_DIM     = QColor(140, 140, 140)
_COL_WEB     = QColor( 30, 100, 200)   # blue for internet results


def _render_page(pdf_path: Path, page_number: int, dpi: int = 130) -> QPixmap | None:
    """Render one page of *pdf_path* to a QPixmap using pdftoppm.

    page_number is 1-based.  Returns None on failure.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        out_base = Path(tmpdir) / "page"
        try:
            result = subprocess.run(
                [
                    "pdftoppm",
                    "-r", str(dpi),
                    "-png",
                    "-singlefile",
                    "-f", str(page_number),
                    "-l", str(page_number),
                    str(pdf_path),
                    str(out_base),
                ],
                capture_output=True,
                timeout=15,
            )
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return None

        # pdftoppm writes <out_base>.png (singlefile mode)
        out_file = Path(tmpdir) / "page.png"
        if not out_file.exists():
            return None

        pixmap = QPixmap(str(out_file))
        return pixmap if not pixmap.isNull() else None


def _count_pages(pdf_path: Path) -> int:
    """Return the number of pages in *pdf_path* using pdfinfo."""
    try:
        result = subprocess.run(
            ["pdfinfo", str(pdf_path)],
            capture_output=True, text=True, timeout=10,
        )
        for line in result.stdout.splitlines():
            if line.startswith("Pages:"):
                return int(line.split(":", 1)[1].strip())
    except Exception:
        pass
    return 1


class _PdfViewer(QWidget):
    """Inline PDF viewer: renders one page at a time via pdftoppm."""

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self._pdf_path:   Path | None = None
        self._total_pages: int = 1
        self._current_page: int = 1

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Page image in a scroll area
        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._img_label = QLabel()
        self._img_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._img_label.setMinimumSize(400, 300)
        self._img_label.setStyleSheet("background: #222;")
        self._img_label.setText("← Select a candidate to preview")
        self._img_label.setStyleSheet(
            "QLabel { background: #222; color: #555; font-size: 14px; }"
        )
        self._scroll.setWidget(self._img_label)
        layout.addWidget(self._scroll, stretch=1)

        # Navigation bar
        nav_row = QHBoxLayout()
        self._prev_btn = QPushButton("← Prev page")
        self._prev_btn.setEnabled(False)
        self._prev_btn.clicked.connect(self._prev_page)
        nav_row.addWidget(self._prev_btn)

        self._page_label = QLabel("Page — of —")
        self._page_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        nav_row.addWidget(self._page_label, stretch=1)

        self._next_btn = QPushButton("Next page →")
        self._next_btn.setEnabled(False)
        self._next_btn.clicked.connect(self._next_page)
        nav_row.addWidget(self._next_btn)
        layout.addLayout(nav_row)

    # ── Public API ───────────────────────────────────────────────────────────

    def load(self, pdf_path: Path) -> None:
        """Load and display page 1 of *pdf_path*."""
        self._pdf_path     = pdf_path
        self._current_page = 1
        self._total_pages  = _count_pages(pdf_path)
        self._refresh()

    def clear(self) -> None:
        self._pdf_path = None
        self._img_label.setPixmap(QPixmap())
        self._img_label.setText("← Select a candidate to preview")
        self._page_label.setText("Page — of —")
        self._prev_btn.setEnabled(False)
        self._next_btn.setEnabled(False)

    # ── Navigation ───────────────────────────────────────────────────────────

    def _prev_page(self) -> None:
        if self._current_page > 1:
            self._current_page -= 1
            self._refresh()

    def _next_page(self) -> None:
        if self._current_page < self._total_pages:
            self._current_page += 1
            self._refresh()

    def _refresh(self) -> None:
        if not self._pdf_path:
            return
        self._page_label.setText(f"Page {self._current_page} of {self._total_pages}")
        self._prev_btn.setEnabled(self._current_page > 1)
        self._next_btn.setEnabled(self._current_page < self._total_pages)

        pixmap = _render_page(self._pdf_path, self._current_page)
        if pixmap:
            # Scale to fit viewer width while keeping aspect ratio
            view_w = self._scroll.viewport().width() or 500
            scaled = pixmap.scaledToWidth(view_w, Qt.TransformationMode.SmoothTransformation)
            self._img_label.setPixmap(scaled)
            self._img_label.setFixedSize(scaled.size())
            self._img_label.setText("")
        else:
            self._img_label.setPixmap(QPixmap())
            self._img_label.setText(f"(Could not render page {self._current_page})")


class DatasheetFindDialog(QDialog):
    """Find + review dialog for locating a datasheet for a component.

    Usage::

        dlg = DatasheetFindDialog(
            part_number="SII3512ECTU128",
            board_dir=COMPONENTS_DIR / "audio_pci_board" / "datasheets",
            initial_mode="internet",   # or "filesystem"
            parent=self,
        )
        if dlg.exec() == QDialog.DialogCode.Accepted:
            path = dlg.selected_path   # Path to the confirmed PDF
    """

    def __init__(
        self,
        part_number: str,
        board_dir: Path,
        *,
        initial_mode: str = "filesystem",
        parent: QWidget | None = None,
    ):
        super().__init__(parent)
        self.setWindowTitle(f"Find datasheet: {part_number}")
        self.resize(1000, 640)

        self._part_number  = part_number
        self._board_dir    = board_dir
        self._fs_worker:   DatasheetScanWorker | None = None
        self._web_worker:  DatasheetFetchWorker | None = None

        # Candidate items: list of (score_or_None, Path, QListWidgetItem)
        self._candidates:  list[tuple[float | None, Path, QListWidgetItem]] = []
        self.selected_path: Path | None = None

        self._build_ui()

        # Select initial tab
        if initial_mode == "internet":
            self._tabs.setCurrentIndex(1)
        else:
            self._tabs.setCurrentIndex(0)

    # ── UI construction ─────────────────────────────────────────────────────

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(8, 8, 8, 8)

        # Header — editable part number
        hdr_row = QHBoxLayout()
        hdr_lbl = QLabel("Part number:")
        hdr_lbl.setFont(QFont("sans-serif", 11))
        hdr_row.addWidget(hdr_lbl)
        self._part_edit = QLineEdit(self._part_number)
        self._part_edit.setFont(QFont("sans-serif", 11, QFont.Weight.Bold))
        self._part_edit.setPlaceholderText("e.g. SII3512ECTU128")
        self._part_edit.setToolTip("Edit to refine the search term before scanning")
        self._part_edit.textChanged.connect(
            lambda t: self.setWindowTitle(f"Find datasheet: {t.strip() or '—'}")
        )
        hdr_row.addWidget(self._part_edit, stretch=1)
        root.addLayout(hdr_row)

        splitter = QSplitter(Qt.Orientation.Horizontal, self)

        # ── Left panel ───────────────────────────────────────────────────────
        left = QWidget()
        lv   = QVBoxLayout(left)
        lv.setContentsMargins(0, 0, 4, 0)

        # Search mode tabs
        self._tabs = QTabWidget()

        # Filesystem tab
        fs_tab = QWidget()
        fst = QVBoxLayout(fs_tab)
        folder_row = QHBoxLayout()
        self._folder_edit = QLineEdit()
        self._folder_edit.setPlaceholderText("Select a folder to scan…")
        if self._board_dir.is_dir():
            self._folder_edit.setText(str(self._board_dir))
        browse_btn = QPushButton("Browse…")
        browse_btn.setFixedWidth(75)
        browse_btn.clicked.connect(self._browse_folder)
        folder_row.addWidget(self._folder_edit, 1)
        folder_row.addWidget(browse_btn)
        fst.addLayout(folder_row)

        self._fs_scan_btn = QPushButton("🔍 Scan filesystem")
        self._fs_scan_btn.clicked.connect(self._start_fs_scan)
        fst.addWidget(self._fs_scan_btn)

        self._fs_progress = QProgressBar()
        self._fs_progress.setTextVisible(True)
        self._fs_progress.setFormat("%v / %m PDFs")
        self._fs_progress.setVisible(False)
        fst.addWidget(self._fs_progress)

        self._show_all_cb = QCheckBox("Show low-score matches")
        self._show_all_cb.stateChanged.connect(self._apply_fs_visibility)
        fst.addWidget(self._show_all_cb)
        fst.addStretch()
        self._tabs.addTab(fs_tab, "📁 Filesystem")

        # Internet tab
        web_tab = QWidget()
        wt = QVBoxLayout(web_tab)
        self._web_search_btn = QPushButton("🌐 Search online")
        self._web_search_btn.clicked.connect(self._start_web_search)
        wt.addWidget(self._web_search_btn)

        self._web_progress_lbl = QLabel("")
        self._web_progress_lbl.setStyleSheet("color: #888; font-style: italic;")
        wt.addWidget(self._web_progress_lbl)

        web_note = QLabel(
            "Searches: AllDatasheet, Datasheet-PDF,\n"
            "DuckDuckGo, Wayback Machine.\n"
            "Downloads are saved to the board's\n"
            "datasheets/ folder."
        )
        web_note.setStyleSheet("color: #666; font-size: 10px;")
        wt.addWidget(web_note)
        wt.addStretch()
        self._tabs.addTab(web_tab, "🌐 Internet")

        lv.addWidget(self._tabs)

        # Candidates list (shared between both modes)
        cand_lbl = QLabel("Candidates:")
        cand_lbl.setFont(QFont("sans-serif", 9, QFont.Weight.Bold))
        lv.addWidget(cand_lbl)

        self._cand_list = QListWidget()
        self._cand_list.setMinimumHeight(150)
        self._cand_list.currentRowChanged.connect(self._on_candidate_selected)
        lv.addWidget(self._cand_list, stretch=1)

        self._status_lbl = QLabel("")
        self._status_lbl.setStyleSheet("color: #888; font-style: italic; font-size: 10px;")
        lv.addWidget(self._status_lbl)

        splitter.addWidget(left)

        # ── Right panel: PDF viewer ───────────────────────────────────────────
        self._viewer = _PdfViewer()
        splitter.addWidget(self._viewer)
        splitter.setStretchFactor(0, 2)
        splitter.setStretchFactor(1, 3)

        root.addWidget(splitter, stretch=1)

        # ── Bottom action buttons ─────────────────────────────────────────────
        btn_row = QHBoxLayout()

        self._link_btn = QPushButton("✓ Link this datasheet")
        self._link_btn.setDefault(True)
        self._link_btn.setEnabled(False)
        self._link_btn.setStyleSheet("font-weight: bold; background: #1b5e20; color: white;")
        self._link_btn.clicked.connect(self._on_link)
        btn_row.addWidget(self._link_btn)

        self._skip_btn = QPushButton("✗ Skip candidate")
        self._skip_btn.setEnabled(False)
        self._skip_btn.clicked.connect(self._on_skip)
        btn_row.addWidget(self._skip_btn)

        btn_row.addStretch()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        btn_row.addWidget(cancel_btn)

        root.addLayout(btn_row)

    # ── Filesystem scan ──────────────────────────────────────────────────────

    def _browse_folder(self) -> None:
        current = self._folder_edit.text() or str(Path.home())
        chosen = QFileDialog.getExistingDirectory(self, "Select folder to scan", current)
        if chosen:
            self._folder_edit.setText(chosen)

    def _start_fs_scan(self) -> None:
        folder = Path(self._folder_edit.text())
        if not folder.is_dir():
            self._status_lbl.setText("⚠ Invalid folder")
            return

        if self._fs_worker and self._fs_worker.isRunning():
            self._fs_worker.abort()
            self._fs_worker.wait()

        self._fs_scan_btn.setEnabled(False)
        self._fs_progress.setVisible(True)
        self._fs_progress.setValue(0)
        self._status_lbl.setText("Scanning…")

        self._fs_worker = DatasheetScanWorker(self._part_edit.text().strip() or self._part_number, folder)
        self._fs_worker.resultReady.connect(self._on_fs_result)
        self._fs_worker.progress.connect(
            lambda done, total: (
                self._fs_progress.setMaximum(total),
                self._fs_progress.setValue(done),
            )
        )
        self._fs_worker.finished.connect(self._on_fs_finished)
        self._fs_worker.start()

    def _on_fs_result(self, score: float, path_str: str) -> None:
        pdf = Path(path_str)
        visible = self._show_all_cb.isChecked() or score >= _SCORE_LOW
        item = self._make_candidate_item(pdf, score=score, source="filesystem")
        item.setHidden(not visible)

    def _on_fs_finished(self, ok: bool, msg: str) -> None:
        self._fs_scan_btn.setEnabled(True)
        self._fs_progress.setVisible(False)
        count = self._cand_list.count()
        self._status_lbl.setText(f"{count} candidate(s). {msg}")
        if self._cand_list.currentRow() < 0 and count > 0:
            self._cand_list.setCurrentRow(0)

    def _apply_fs_visibility(self) -> None:
        show_all = self._show_all_cb.isChecked()
        for score, _, item in self._candidates:
            if score is not None:
                item.setHidden(not show_all and score < _SCORE_LOW)

    # ── Internet search ──────────────────────────────────────────────────────

    def _start_web_search(self) -> None:
        if self._web_worker and self._web_worker.isRunning():
            self._web_worker.abort()
            self._web_worker.wait()

        self._web_search_btn.setEnabled(False)
        self._web_progress_lbl.setText("Trying sources…")
        self._status_lbl.setText("Searching online…")

        self._board_dir.mkdir(parents=True, exist_ok=True)
        self._web_worker = DatasheetFetchWorker(
            self._part_edit.text().strip() or self._part_number,
            self._board_dir,
        )
        self._web_worker.progress.connect(
            lambda src: self._web_progress_lbl.setText(f"Querying: {src}…")
        )
        self._web_worker.candidateReady.connect(self._on_web_candidate)
        self._web_worker.finished.connect(self._on_web_finished)
        self._web_worker.start()

    def _on_web_candidate(self, local_path: str, source_name: str) -> None:
        pdf = Path(local_path)
        if not pdf.exists():
            return
        item = self._make_candidate_item(pdf, score=None, source=source_name)
        item.setHidden(False)
        if self._cand_list.currentRow() < 0:
            self._cand_list.setCurrentRow(self._cand_list.count() - 1)

    def _on_web_finished(self, ok: bool, n_downloaded: int) -> None:
        self._web_search_btn.setEnabled(True)
        self._web_progress_lbl.setText("")
        if n_downloaded == 0:
            self._status_lbl.setText("No datasheets found online.")
        else:
            self._status_lbl.setText(f"{n_downloaded} download(s) complete.")
        if self._cand_list.currentRow() < 0 and self._cand_list.count() > 0:
            self._cand_list.setCurrentRow(0)

    # ── Candidate list helpers ────────────────────────────────────────────────

    def _make_candidate_item(
        self,
        pdf: Path,
        *,
        score: float | None,
        source: str,
    ) -> QListWidgetItem:
        if score is not None:
            label = f"  {score:.2f}  {pdf.name}"
            color = _COL_HIGH if score >= _SCORE_HIGH else _COL_DIM
        else:
            label = f"  {source}  {pdf.name}"
            color = _COL_WEB

        item = QListWidgetItem(label)
        item.setData(Qt.ItemDataRole.UserRole, str(pdf))
        item.setForeground(color)
        if score is not None and score >= _SCORE_HIGH:
            font = item.font()
            font.setWeight(QFont.Weight.Bold)
            item.setFont(font)
        self._cand_list.addItem(item)
        self._candidates.append((score, pdf, item))
        return item

    def _on_candidate_selected(self, row: int) -> None:
        if row < 0:
            self._viewer.clear()
            self._link_btn.setEnabled(False)
            self._skip_btn.setEnabled(False)
            return

        item = self._cand_list.item(row)
        if item is None:
            return
        path_str = item.data(Qt.ItemDataRole.UserRole)
        if not path_str:
            return
        pdf = Path(path_str)
        if pdf.exists():
            self._viewer.load(pdf)
        else:
            self._viewer.clear()
        self._link_btn.setEnabled(True)
        self._skip_btn.setEnabled(True)

    # ── Accept / skip ────────────────────────────────────────────────────────

    def _on_link(self) -> None:
        row = self._cand_list.currentRow()
        if row < 0:
            return
        item = self._cand_list.item(row)
        path_str = item.data(Qt.ItemDataRole.UserRole) if item else None
        if path_str:
            self.selected_path = Path(path_str)
        self._stop_workers()
        self.accept()

    def _on_skip(self) -> None:
        row = self._cand_list.currentRow()
        if row < 0:
            return
        # Remove from list
        self._cand_list.takeItem(row)
        # Remove from candidates list (by matching row index, after insertion order)
        if 0 <= row < len(self._candidates):
            del self._candidates[row]
        self._viewer.clear()
        self._link_btn.setEnabled(False)
        self._skip_btn.setEnabled(False)
        # Auto-select next
        new_count = self._cand_list.count()
        if new_count > 0:
            self._cand_list.setCurrentRow(min(row, new_count - 1))
        else:
            self._status_lbl.setText("No more candidates.")

    # ── Cleanup ──────────────────────────────────────────────────────────────

    def _stop_workers(self) -> None:
        for worker in (self._fs_worker, self._web_worker):
            if worker and worker.isRunning():
                worker.abort()
                worker.wait()

    def closeEvent(self, event) -> None:
        self._stop_workers()
        super().closeEvent(event)

    def reject(self) -> None:
        self._stop_workers()
        super().reject()
