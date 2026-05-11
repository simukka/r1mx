"""
search.py — Programmatic datasheet search API for r1mx.

Wraps the individual web-source scrapers from fetch.py into a clean,
Qt-free API suitable for use in background workers.

Public surface
--------------
SearchCandidate   — dataclass: url, source_name, filename (derived)
search_all_sources(part_number, *, stop_event=None) → list[SearchCandidate]
    Tries every source in order; returns all non-None URLs as candidates.
    stop_event: optional threading.Event; checked between sources to allow
    cooperative cancellation.
download_candidate(candidate, dest_dir) → Path | None
    Downloads one SearchCandidate to dest_dir.  Returns the local Path on
    success, None on failure.
"""

from __future__ import annotations

import re
import threading
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable
from urllib.parse import urlparse

from toolkit.datasheets.fetch import (
    _alldatasheet_find,
    _datasheetpdf_find,
    _datasheetspdf_find,
    _duckduckgo_find,
    _wayback_find,
    download_pdf,
)


# ─── SearchCandidate ─────────────────────────────────────────────────────────

@dataclass
class SearchCandidate:
    """A candidate datasheet URL found by one of the search sources."""

    url: str
    source_name: str

    @property
    def filename(self) -> str:
        """Best-effort filename extracted from the URL path."""
        try:
            path = urlparse(self.url).path
            name = Path(path).name
            if name.lower().endswith(".pdf"):
                return name
        except Exception:
            pass
        return f"{self.source_name}.pdf"


# ─── Source registry ─────────────────────────────────────────────────────────

#: Ordered list of (source_name, finder_fn) pairs.
#: Each finder_fn takes a part_number string and returns a URL or None.
SOURCES: list[tuple[str, Callable[[str], str | None]]] = [
    ("alldatasheet",   _alldatasheet_find),
    ("datasheet-pdf",  _datasheetpdf_find),
    ("datasheetspdf",  _datasheetspdf_find),
    ("duckduckgo",     _duckduckgo_find),
    ("wayback",        _wayback_find),
]


# ─── Search ──────────────────────────────────────────────────────────────────

def search_all_sources(
    part_number: str,
    *,
    stop_event: threading.Event | None = None,
    progress_cb: Callable[[str], None] | None = None,
) -> list[SearchCandidate]:
    """Search all configured sources and return a list of unique candidates.

    Parameters
    ----------
    part_number : str
        The part number to search for (e.g. "SiI3512ECTU128").
    stop_event  : threading.Event | None
        When set, the search stops after the current source finishes.
    progress_cb : callable(str) | None
        Called with the source_name string before each source is queried.

    Returns
    -------
    list[SearchCandidate]
        Deduplicated candidates ordered by discovery.
    """
    seen_urls: set[str] = set()
    results:   list[SearchCandidate] = []

    for source_name, finder in SOURCES:
        if stop_event and stop_event.is_set():
            break
        if progress_cb:
            progress_cb(source_name)
        try:
            url = finder(part_number)
        except Exception:
            url = None
        if url and url not in seen_urls:
            seen_urls.add(url)
            results.append(SearchCandidate(url=url, source_name=source_name))

    return results


# ─── Download ────────────────────────────────────────────────────────────────

def _safe_stem(part_number: str) -> str:
    """Return a filesystem-safe stem for part_number."""
    return re.sub(r"[^\w\-.]", "_", part_number)


def download_candidate(candidate: SearchCandidate, dest_dir: Path) -> Path | None:
    """Download *candidate* into *dest_dir*.

    The local filename is derived from the URL path when it looks like a
    real PDF filename, otherwise ``<source_name>_<safe_part>.pdf`` is used.

    Returns the local ``Path`` on success, ``None`` on failure.
    """
    dest_dir.mkdir(parents=True, exist_ok=True)

    # Prefer the filename from the URL if it looks meaningful
    url_name = candidate.filename
    dest = dest_dir / url_name

    # Avoid overwriting existing files by appending a counter
    stem   = dest.stem
    suffix = dest.suffix
    counter = 1
    while dest.exists():
        dest = dest_dir / f"{stem}_{counter}{suffix}"
        counter += 1

    ok = download_pdf(candidate.url, dest)
    return dest if ok and dest.exists() else None
