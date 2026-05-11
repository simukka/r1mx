"""DatasheetFetchWorker — background QThread for online datasheet search + download."""

from __future__ import annotations

import threading
from pathlib import Path

from PyQt6.QtCore import QThread, pyqtSignal

from toolkit.datasheets.search import SearchCandidate, download_candidate, search_all_sources


class DatasheetFetchWorker(QThread):
    """Search all online sources for a part number and download each candidate.

    Signals
    -------
    progress(source_name)
        Emitted just before querying each source (e.g. "alldatasheet").
    candidateReady(local_path, source_name)
        Emitted after each PDF is successfully downloaded.
    finished(ok, n_downloaded)
        Emitted once when the worker completes or is aborted.
    """

    progress       = pyqtSignal(str)         # source_name being queried
    candidateReady = pyqtSignal(str, str)     # (local_path, source_name)
    finished       = pyqtSignal(bool, int)    # (ok, n_downloaded)

    def __init__(
        self,
        part_number: str,
        dest_dir: Path,
        parent=None,
    ):
        super().__init__(parent)
        self._part_number = part_number
        self._dest_dir    = dest_dir
        self._stop        = threading.Event()

    def abort(self) -> None:
        """Request cooperative cancellation."""
        self._stop.set()

    def run(self) -> None:
        n_downloaded = 0
        try:
            candidates = search_all_sources(
                self._part_number,
                stop_event=self._stop,
                progress_cb=lambda s: self.progress.emit(s),
            )

            for candidate in candidates:
                if self._stop.is_set():
                    break
                local_path = download_candidate(candidate, self._dest_dir)
                if local_path is not None:
                    n_downloaded += 1
                    self.candidateReady.emit(str(local_path), candidate.source_name)

        except Exception:
            pass

        self.finished.emit(not self._stop.is_set(), n_downloaded)
