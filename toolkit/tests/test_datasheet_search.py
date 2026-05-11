"""Unit tests for toolkit.datasheets.search — SearchCandidate, search_all_sources,
download_candidate, and _safe_stem.  No network calls; everything is mocked."""

from __future__ import annotations

import threading
from pathlib import Path
from unittest.mock import MagicMock, call, patch

import pytest

from toolkit.datasheets.search import (
    SOURCES,
    SearchCandidate,
    _safe_stem,
    download_candidate,
    search_all_sources,
)


# ─── SearchCandidate ─────────────────────────────────────────────────────────

class TestSearchCandidate:
    def test_filename_from_url_with_pdf(self):
        c = SearchCandidate(url="https://example.com/datasheets/SII3512.pdf", source_name="x")
        assert c.filename == "SII3512.pdf"

    def test_filename_from_url_with_path_segments(self):
        c = SearchCandidate(url="https://cdn.foo.com/a/b/c/MyPart.pdf", source_name="x")
        assert c.filename == "MyPart.pdf"

    def test_filename_fallback_when_no_pdf_extension(self):
        c = SearchCandidate(url="https://example.com/download?id=123", source_name="alldatasheet")
        # URL has no .pdf extension → fall back to "<source_name>.pdf"
        assert c.filename == "alldatasheet.pdf"

    def test_filename_fallback_on_empty_url_path(self):
        c = SearchCandidate(url="https://example.com/", source_name="wayback")
        assert c.filename == "wayback.pdf"

    def test_source_name_stored(self):
        c = SearchCandidate(url="https://x.com/a.pdf", source_name="duckduckgo")
        assert c.source_name == "duckduckgo"

    def test_url_stored(self):
        url = "https://x.com/a.pdf"
        c = SearchCandidate(url=url, source_name="x")
        assert c.url == url

    def test_case_insensitive_pdf_extension(self):
        c = SearchCandidate(url="https://x.com/part.PDF", source_name="s")
        assert c.filename == "part.PDF"


# ─── _safe_stem ──────────────────────────────────────────────────────────────

class TestSafeStem:
    def test_alphanumeric(self):
        assert _safe_stem("SII3512") == "SII3512"

    def test_spaces_replaced(self):
        assert _safe_stem("my part") == "my_part"

    def test_special_chars_replaced(self):
        assert _safe_stem("LM386/N1") == "LM386_N1"

    def test_hyphens_and_dots_kept(self):
        assert _safe_stem("XC4VLX25-10FF668") == "XC4VLX25-10FF668"

    def test_empty_string(self):
        assert _safe_stem("") == ""


# ─── search_all_sources ──────────────────────────────────────────────────────

class TestSearchAllSources:
    def _make_sources(self, return_values: dict[str, str | None]):
        """Build a patched SOURCES list with stub finders."""
        sources = []
        for name, fn in SOURCES:
            rv = return_values.get(name)
            stub = MagicMock(return_value=rv, side_effect=None)
            stub.__name__ = name
            sources.append((name, stub))
        return sources

    def test_returns_candidates_for_successful_sources(self):
        with patch(
            "toolkit.datasheets.search.SOURCES",
            [
                ("src_a", MagicMock(return_value="https://a.com/p.pdf")),
                ("src_b", MagicMock(return_value="https://b.com/p.pdf")),
            ],
        ):
            results = search_all_sources("PART")
        assert len(results) == 2
        assert results[0].source_name == "src_a"
        assert results[1].source_name == "src_b"

    def test_skips_none_results(self):
        with patch(
            "toolkit.datasheets.search.SOURCES",
            [
                ("src_a", MagicMock(return_value="https://a.com/p.pdf")),
                ("src_b", MagicMock(return_value=None)),
            ],
        ):
            results = search_all_sources("PART")
        assert len(results) == 1
        assert results[0].source_name == "src_a"

    def test_deduplicates_same_url(self):
        url = "https://same.com/p.pdf"
        with patch(
            "toolkit.datasheets.search.SOURCES",
            [
                ("src_a", MagicMock(return_value=url)),
                ("src_b", MagicMock(return_value=url)),
            ],
        ):
            results = search_all_sources("PART")
        assert len(results) == 1

    def test_progress_cb_called_for_each_source(self):
        cb = MagicMock()
        with patch(
            "toolkit.datasheets.search.SOURCES",
            [
                ("src_a", MagicMock(return_value=None)),
                ("src_b", MagicMock(return_value=None)),
            ],
        ):
            search_all_sources("PART", progress_cb=cb)
        assert cb.call_count == 2
        cb.assert_any_call("src_a")
        cb.assert_any_call("src_b")

    def test_stop_event_halts_search(self):
        stop = threading.Event()
        stop.set()
        src_a = MagicMock(return_value="https://a.com/p.pdf")
        with patch(
            "toolkit.datasheets.search.SOURCES",
            [("src_a", src_a)],
        ):
            results = search_all_sources("PART", stop_event=stop)
        src_a.assert_not_called()
        assert results == []

    def test_stop_event_checked_between_sources(self):
        stop = threading.Event()
        call_order = []

        def first_finder(pn):
            call_order.append("first")
            stop.set()   # set AFTER first runs
            return "https://a.com/p.pdf"

        second_finder = MagicMock(return_value="https://b.com/p.pdf")

        with patch(
            "toolkit.datasheets.search.SOURCES",
            [("first", first_finder), ("second", second_finder)],
        ):
            results = search_all_sources("PART", stop_event=stop)

        assert len(results) == 1
        assert results[0].source_name == "first"
        second_finder.assert_not_called()

    def test_exception_in_finder_is_swallowed(self):
        bad = MagicMock(side_effect=RuntimeError("network error"))
        good = MagicMock(return_value="https://b.com/p.pdf")
        with patch(
            "toolkit.datasheets.search.SOURCES",
            [("bad_src", bad), ("good_src", good)],
        ):
            results = search_all_sources("PART")
        assert len(results) == 1
        assert results[0].source_name == "good_src"

    def test_empty_sources_returns_empty_list(self):
        with patch("toolkit.datasheets.search.SOURCES", []):
            results = search_all_sources("PART")
        assert results == []

    def test_returns_correct_urls(self):
        with patch(
            "toolkit.datasheets.search.SOURCES",
            [("s", MagicMock(return_value="https://x.com/abc.pdf"))],
        ):
            results = search_all_sources("PART")
        assert results[0].url == "https://x.com/abc.pdf"


# ─── download_candidate ──────────────────────────────────────────────────────

class TestDownloadCandidate:
    def test_successful_download_returns_path(self, tmp_path):
        candidate = SearchCandidate(url="https://x.com/doc.pdf", source_name="x")
        expected = tmp_path / "doc.pdf"

        def fake_dl(url, dest, **kw):
            dest.write_bytes(b"%PDF")  # simulate download_pdf writing the file
            return True

        with patch("toolkit.datasheets.search.download_pdf", side_effect=fake_dl):
            result = download_candidate(candidate, tmp_path)

        assert result == expected

    def test_failed_download_returns_none(self, tmp_path):
        candidate = SearchCandidate(url="https://x.com/doc.pdf", source_name="x")

        with patch("toolkit.datasheets.search.download_pdf") as mock_dl:
            mock_dl.return_value = False
            result = download_candidate(candidate, tmp_path)

        assert result is None

    def test_creates_dest_dir_if_missing(self, tmp_path):
        new_dir = tmp_path / "a" / "b" / "c"
        assert not new_dir.exists()
        candidate = SearchCandidate(url="https://x.com/doc.pdf", source_name="x")

        with patch("toolkit.datasheets.search.download_pdf") as mock_dl:
            mock_dl.return_value = False
            download_candidate(candidate, new_dir)

        assert new_dir.is_dir()

    def test_avoids_overwriting_existing_file(self, tmp_path):
        (tmp_path / "doc.pdf").write_bytes(b"existing")
        candidate = SearchCandidate(url="https://x.com/doc.pdf", source_name="x")

        with patch("toolkit.datasheets.search.download_pdf") as mock_dl:
            def fake_dl(url, dest, **kw):
                dest.write_bytes(b"new")
                return True
            mock_dl.side_effect = fake_dl
            result = download_candidate(candidate, tmp_path)

        assert result is not None
        assert result.name == "doc_1.pdf"   # collision avoided

    def test_increments_counter_for_multiple_existing_files(self, tmp_path):
        (tmp_path / "doc.pdf").write_bytes(b"x")
        (tmp_path / "doc_1.pdf").write_bytes(b"x")
        candidate = SearchCandidate(url="https://x.com/doc.pdf", source_name="x")

        with patch("toolkit.datasheets.search.download_pdf") as mock_dl:
            def fake_dl(url, dest, **kw):
                dest.write_bytes(b"new")
                return True
            mock_dl.side_effect = fake_dl
            result = download_candidate(candidate, tmp_path)

        assert result is not None
        assert result.name == "doc_2.pdf"

    def test_uses_fallback_filename_when_url_has_no_pdf(self, tmp_path):
        candidate = SearchCandidate(url="https://x.com/download?id=99", source_name="wayback")
        expected = tmp_path / "wayback.pdf"

        with patch("toolkit.datasheets.search.download_pdf") as mock_dl:
            def fake_dl(url, dest, **kw):
                dest.write_bytes(b"%PDF")
                return True
            mock_dl.side_effect = fake_dl
            result = download_candidate(candidate, tmp_path)

        assert result == expected

    def test_download_pdf_called_with_correct_url(self, tmp_path):
        url = "https://x.com/part.pdf"
        candidate = SearchCandidate(url=url, source_name="s")

        with patch("toolkit.datasheets.search.download_pdf") as mock_dl:
            mock_dl.return_value = False
            download_candidate(candidate, tmp_path)

        args = mock_dl.call_args[0]
        assert args[0] == url
