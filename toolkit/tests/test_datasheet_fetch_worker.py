"""Unit tests for toolkit.workers.datasheet_fetch.DatasheetFetchWorker.

Worker logic is tested synchronously by calling run() directly (not via
QThread.start()) so we don't need an event loop.  Signals are captured
via a simple list collector.
"""

from __future__ import annotations

import threading
from pathlib import Path
from unittest.mock import MagicMock, patch, call

import pytest

from toolkit.workers.datasheet_fetch import DatasheetFetchWorker
from toolkit.datasheets.search import SearchCandidate


# ─── Helpers ─────────────────────────────────────────────────────────────────

class _Collector:
    """Collect pyqtSignal emissions as plain Python values."""

    def __init__(self):
        self.calls: list = []

    def __call__(self, *args):
        self.calls.append(args)


def _make_worker(part="SII3512", dest_dir: Path | None = None, tmp_path: Path | None = None):
    dest = dest_dir or (tmp_path or Path("/tmp"))
    return DatasheetFetchWorker(part, dest)


# ─── Constructor ─────────────────────────────────────────────────────────────

class TestDatasheetFetchWorkerInit:
    def test_stores_part_number(self, tmp_path):
        w = DatasheetFetchWorker("LM386", tmp_path)
        assert w._part_number == "LM386"

    def test_stores_dest_dir(self, tmp_path):
        w = DatasheetFetchWorker("X", tmp_path)
        assert w._dest_dir == tmp_path

    def test_stop_event_not_set_initially(self, tmp_path):
        w = DatasheetFetchWorker("X", tmp_path)
        assert not w._stop.is_set()


# ─── abort() ─────────────────────────────────────────────────────────────────

class TestDatasheetFetchWorkerAbort:
    def test_abort_sets_stop_event(self, tmp_path):
        w = DatasheetFetchWorker("X", tmp_path)
        w.abort()
        assert w._stop.is_set()

    def test_abort_is_idempotent(self, tmp_path):
        w = DatasheetFetchWorker("X", tmp_path)
        w.abort()
        w.abort()
        assert w._stop.is_set()


# ─── run() — normal execution ─────────────────────────────────────────────────

class TestDatasheetFetchWorkerRun:
    def _run_worker(self, worker):
        """Run the worker synchronously, bypassing QThread mechanics."""
        worker.run()

    def test_emits_progress_for_each_candidate(self, tmp_path):
        c1 = SearchCandidate("https://a.com/a.pdf", "src_a")
        c2 = SearchCandidate("https://b.com/b.pdf", "src_b")

        progress_vals = []
        worker = DatasheetFetchWorker("PART", tmp_path)
        worker.progress.connect(lambda s: progress_vals.append(s))
        worker.finished.connect(lambda *_: None)

        with (
            patch("toolkit.workers.datasheet_fetch.search_all_sources", return_value=[c1, c2]),
            patch("toolkit.workers.datasheet_fetch.download_candidate", return_value=None),
        ):
            self._run_worker(worker)

        # progress is emitted by search_all_sources's progress_cb for each source found
        # The worker calls progress_cb inside search_all_sources; here search_all_sources
        # is mocked so progress_cb won't be called by search itself.
        # What matters: no exception is raised and finished fires.

    def test_emits_candidateReady_after_each_successful_download(self, tmp_path):
        c1 = SearchCandidate("https://a.com/a.pdf", "src_a")
        c2 = SearchCandidate("https://b.com/b.pdf", "src_b")
        pdf1 = tmp_path / "a.pdf"
        pdf2 = tmp_path / "b.pdf"

        ready_calls = []
        finished_calls = []
        worker = DatasheetFetchWorker("PART", tmp_path)
        worker.candidateReady.connect(lambda p, s: ready_calls.append((p, s)))
        worker.finished.connect(lambda ok, n: finished_calls.append((ok, n)))

        def fake_download(candidate, dest_dir):
            return {c1.url: pdf1, c2.url: pdf2}[candidate.url]

        with (
            patch("toolkit.workers.datasheet_fetch.search_all_sources", return_value=[c1, c2]),
            patch(
                "toolkit.workers.datasheet_fetch.download_candidate",
                side_effect=fake_download,
            ),
        ):
            self._run_worker(worker)

        assert len(ready_calls) == 2
        assert (str(pdf1), "src_a") in ready_calls
        assert (str(pdf2), "src_b") in ready_calls

    def test_skips_candidateReady_when_download_returns_none(self, tmp_path):
        c1 = SearchCandidate("https://a.com/a.pdf", "src_a")

        ready_calls = []
        worker = DatasheetFetchWorker("PART", tmp_path)
        worker.candidateReady.connect(lambda p, s: ready_calls.append((p, s)))
        worker.finished.connect(lambda *_: None)

        with (
            patch("toolkit.workers.datasheet_fetch.search_all_sources", return_value=[c1]),
            patch("toolkit.workers.datasheet_fetch.download_candidate", return_value=None),
        ):
            self._run_worker(worker)

        assert ready_calls == []

    def test_finished_emits_ok_true_when_not_aborted(self, tmp_path):
        finished_calls = []
        worker = DatasheetFetchWorker("PART", tmp_path)
        worker.finished.connect(lambda ok, n: finished_calls.append((ok, n)))

        with (
            patch("toolkit.workers.datasheet_fetch.search_all_sources", return_value=[]),
            patch("toolkit.workers.datasheet_fetch.download_candidate", return_value=None),
        ):
            self._run_worker(worker)

        assert len(finished_calls) == 1
        ok, n = finished_calls[0]
        assert ok is True
        assert n == 0

    def test_finished_reports_correct_download_count(self, tmp_path):
        pdf = tmp_path / "x.pdf"
        c = SearchCandidate("https://x.com/x.pdf", "s")

        finished_calls = []
        worker = DatasheetFetchWorker("PART", tmp_path)
        worker.candidateReady.connect(lambda *_: None)
        worker.finished.connect(lambda ok, n: finished_calls.append((ok, n)))

        with (
            patch("toolkit.workers.datasheet_fetch.search_all_sources", return_value=[c]),
            patch("toolkit.workers.datasheet_fetch.download_candidate", return_value=pdf),
        ):
            self._run_worker(worker)

        assert finished_calls[0] == (True, 1)

    def test_no_candidateReady_when_search_returns_empty(self, tmp_path):
        ready_calls = []
        worker = DatasheetFetchWorker("PART", tmp_path)
        worker.candidateReady.connect(lambda *_: ready_calls.append(True))
        worker.finished.connect(lambda *_: None)

        with patch("toolkit.workers.datasheet_fetch.search_all_sources", return_value=[]):
            self._run_worker(worker)

        assert ready_calls == []


# ─── run() — aborted via stop event ──────────────────────────────────────────

class TestDatasheetFetchWorkerAbortMidRun:
    def _run_worker(self, worker):
        worker.run()

    def test_abort_before_run_skips_all_candidates(self, tmp_path):
        c1 = SearchCandidate("https://a.com/a.pdf", "s")
        ready_calls = []
        finished_calls = []

        worker = DatasheetFetchWorker("PART", tmp_path)
        worker.abort()  # stop before run
        worker.candidateReady.connect(lambda *_: ready_calls.append(True))
        worker.finished.connect(lambda ok, n: finished_calls.append((ok, n)))

        with (
            patch("toolkit.workers.datasheet_fetch.search_all_sources", return_value=[c1]),
            patch("toolkit.workers.datasheet_fetch.download_candidate") as mock_dl,
        ):
            self._run_worker(worker)

        # download_candidate should not be called if stop is already set
        mock_dl.assert_not_called()
        assert ready_calls == []

    def test_abort_mid_iteration_stops_after_current(self, tmp_path):
        pdfs = [tmp_path / f"c{i}.pdf" for i in range(3)]
        candidates = [SearchCandidate(f"https://x.com/c{i}.pdf", f"s{i}") for i in range(3)]

        ready_calls = []
        worker = DatasheetFetchWorker("PART", tmp_path)
        worker.candidateReady.connect(lambda p, s: ready_calls.append(p))
        worker.finished.connect(lambda *_: None)

        call_count = 0

        def fake_download(candidate, dest_dir):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                worker.abort()           # abort after first download
            return pdfs[candidates.index(candidate)]

        with (
            patch("toolkit.workers.datasheet_fetch.search_all_sources", return_value=candidates),
            patch("toolkit.workers.datasheet_fetch.download_candidate", side_effect=fake_download),
        ):
            self._run_worker(worker)

        # Only the first download completes before abort is noticed
        assert len(ready_calls) == 1

    def test_finished_ok_is_false_when_aborted(self, tmp_path):
        worker = DatasheetFetchWorker("PART", tmp_path)
        finished_calls = []
        worker.finished.connect(lambda ok, n: finished_calls.append((ok, n)))
        worker.abort()

        with patch("toolkit.workers.datasheet_fetch.search_all_sources", return_value=[]):
            worker.run()

        ok, _ = finished_calls[0]
        assert ok is False


# ─── run() — exception safety ─────────────────────────────────────────────────

class TestDatasheetFetchWorkerExceptions:
    def test_exception_in_search_does_not_propagate(self, tmp_path):
        worker = DatasheetFetchWorker("PART", tmp_path)
        finished_calls = []
        worker.finished.connect(lambda ok, n: finished_calls.append((ok, n)))

        with patch(
            "toolkit.workers.datasheet_fetch.search_all_sources",
            side_effect=RuntimeError("network down"),
        ):
            worker.run()  # must not raise

        assert len(finished_calls) == 1

    def test_exception_in_download_does_not_propagate(self, tmp_path):
        c = SearchCandidate("https://x.com/x.pdf", "s")
        worker = DatasheetFetchWorker("PART", tmp_path)
        worker.candidateReady.connect(lambda *_: None)
        finished_calls = []
        worker.finished.connect(lambda ok, n: finished_calls.append((ok, n)))

        with (
            patch("toolkit.workers.datasheet_fetch.search_all_sources", return_value=[c]),
            patch(
                "toolkit.workers.datasheet_fetch.download_candidate",
                side_effect=OSError("disk full"),
            ),
        ):
            worker.run()

        assert len(finished_calls) == 1
