"""
datasheet_scan.py — QThread worker that scans a folder for datasheets matching
a part-number query and streams results to the UI.

Signals
-------
resultReady(score: float, path: str)
    Emitted once per PDF as it is scored.  The UI adds a row to the results
    list immediately so the user can see matches stream in live.

progress(done: int, total: int)
    Emitted after each PDF is processed.

finished(bool, str)
    Emitted when the scan is complete (True) or aborted (False).
"""

from __future__ import annotations

from pathlib import Path

from PyQt6.QtCore import QThread, pyqtSignal

from toolkit.analysis.datasheet_scan import score_pdf


class DatasheetScanWorker(QThread):
    """Scan a folder for PDFs matching *part_number* and emit scored results."""

    resultReady = pyqtSignal(float, str)   # score, absolute path string
    progress    = pyqtSignal(int, int)     # done, total
    finished    = pyqtSignal(bool, str)    # success, message

    def __init__(
        self,
        part_number: str,
        folder: Path,
        *,
        recursive: bool = True,
        parent=None,
    ):
        super().__init__(parent)
        self._part   = part_number
        self._folder = Path(folder)
        self._recursive = recursive
        self._abort  = False

    def abort(self) -> None:
        """Request early termination (checked between PDFs)."""
        self._abort = True

    def run(self) -> None:
        """Collect all PDFs first (for progress total), then score each one."""
        glob_fn = self._folder.rglob if self._recursive else self._folder.glob
        pdfs: list[Path] = []
        for pattern in ("*.pdf", "*.PDF"):
            pdfs.extend(p for p in glob_fn(pattern) if p.is_file())
        pdfs = sorted(set(pdfs))

        total = len(pdfs)
        if total == 0:
            self.finished.emit(True, "No PDF files found in the selected folder.")
            return

        for idx, pdf in enumerate(pdfs, 1):
            if self._abort:
                self.finished.emit(False, "Scan cancelled.")
                return
            score = score_pdf(self._part, pdf)
            self.resultReady.emit(score, str(pdf))
            self.progress.emit(idx, total)

        self.finished.emit(True, f"Scanned {total} PDF{'s' if total != 1 else ''}.")
