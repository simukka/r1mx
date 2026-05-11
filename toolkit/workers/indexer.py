"""
indexer.py — Continuous background datasheet indexer worker.

Scans ``components/*/datasheets/*.pdf`` every ``SCAN_INTERVAL_S`` seconds
and indexes any PDFs that are not yet in ChromaDB.  Designed to run for the
lifetime of the toolkit application.

Signals
-------
statusChanged(str)
    Emitted when the indexer state changes.
    Values: ``"idle"`` | ``"running"`` | ``"error"``

newChunks(int)
    Emitted after a scan that added new chunks. Carries the count of newly
    added chunks across all newly indexed PDFs.

logLine(str)
    Emitted with human-readable progress lines (HTML-safe).

Usage
-----
    worker = DatasheetIndexWorker()
    worker.statusChanged.connect(status_bar.update_indexer)
    worker.logLine.connect(log_panel.append)
    worker.start()
    # later:
    worker.stop()
    worker.wait()
"""

from __future__ import annotations

import logging
import time
from pathlib import Path

from PyQt6.QtCore import QThread, pyqtSignal

log = logging.getLogger(__name__)

SCAN_INTERVAL_S = 60   # seconds between full scans


class DatasheetIndexWorker(QThread):
    """Background thread that continuously indexes new datasheet PDFs."""

    statusChanged = pyqtSignal(str)    # "idle" | "running" | "error"
    newChunks     = pyqtSignal(int)    # total new chunks from this scan
    logLine       = pyqtSignal(str)    # HTML progress message

    def __init__(self, parent=None):
        super().__init__(parent)
        self._stop = False

    # ── QThread.run ──────────────────────────────────────────────────────────

    def run(self) -> None:
        while not self._stop:
            self._scan()
            # Sleep in small increments so stop() is responsive
            for _ in range(SCAN_INTERVAL_S * 4):
                if self._stop:
                    return
                time.sleep(0.25)

    def stop(self) -> None:
        self._stop = True

    # ── Internal ─────────────────────────────────────────────────────────────

    def _scan(self) -> None:
        try:
            self._do_scan()
        except Exception as exc:
            log.exception("Indexer scan failed")
            self.statusChanged.emit("error")
            self.logLine.emit(f"<b>⚠ Indexer error:</b> {exc}")

    def _do_scan(self) -> None:
        # Import lazily — these pull in fastembed/chromadb which are heavy
        from toolkit.datasheets.index import (
            already_indexed,
            embed_texts,
            find_pdfs,
            get_collection,
            index_pdf,
            wait_for_services,
        )
        import chromadb
        from urllib.parse import urlparse
        import os
        from toolkit.paths import REPO_ROOT

        _env_file = REPO_ROOT / ".env"
        if _env_file.exists():
            for _line in _env_file.read_text().splitlines():
                _line = _line.strip()
                if _line and not _line.startswith("#") and "=" in _line:
                    _k, _, _v = _line.partition("=")
                    import os as _os
                    _os.environ.setdefault(_k.strip(), _v.strip())

        chroma_host_str = os.environ.get("CHROMA_HOST", "http://localhost:8000")
        parsed     = urlparse(chroma_host_str)
        host       = parsed.hostname or "localhost"
        port       = parsed.port or 8000

        # Quick health check — silently skip if ChromaDB is not ready yet
        import requests
        try:
            r = requests.get(f"{chroma_host_str}/api/v2/heartbeat", timeout=3)
            if r.status_code != 200:
                return
        except Exception:
            return

        try:
            client     = chromadb.HttpClient(host=host, port=port)
            collection = get_collection(client)
        except Exception as exc:
            log.warning("Indexer: cannot connect to ChromaDB: %s", exc)
            return

        pdfs = find_pdfs(board_filter=None)
        new_pdfs = [
            (p, b) for p, b in pdfs
            if not already_indexed(collection, _sha256(p))
        ]

        if not new_pdfs:
            self.statusChanged.emit("idle")
            return

        self.statusChanged.emit("running")
        self.logLine.emit(
            f"<b>Indexer:</b> {len(new_pdfs)} new datasheet(s) found — indexing…"
        )

        total_chunks = 0
        for pdf_path, board in new_pdfs:
            if self._stop:
                break
            added = index_pdf(pdf_path, board, collection, reindex=False)
            if added:
                total_chunks += added
                self.logLine.emit(
                    f"  ✓ indexed <i>{pdf_path.name}</i> ({board}) — {added} chunks"
                )

        if total_chunks:
            self.newChunks.emit(total_chunks)
            self.logLine.emit(
                f"<b>Indexer:</b> done — {total_chunks} new chunks added"
            )

        self.statusChanged.emit("idle")


def _sha256(path: Path) -> str:
    import hashlib
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(65536), b""):
            h.update(block)
    return h.hexdigest()
