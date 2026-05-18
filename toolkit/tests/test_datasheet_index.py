"""Unit tests for toolkit.datasheets.index — PDF text extraction + OCR fallback.

No real PDFs required — all subprocess calls are mocked.
"""

from __future__ import annotations

import subprocess
from pathlib import Path
from unittest.mock import MagicMock, patch, call

import pytest

from toolkit.datasheets.index import (
    _pdftotext,
    _ocr_pdf,
    pdf_to_text,
    chunk_text,
    sha256,
    already_indexed,
)


# ---------------------------------------------------------------------------
# _pdftotext
# ---------------------------------------------------------------------------

class TestPdfToText:

    def test_returns_stdout_on_success(self, tmp_path):
        dummy = tmp_path / "test.pdf"
        dummy.write_bytes(b"%PDF-1.4 dummy")
        with patch("subprocess.run") as m:
            m.return_value.returncode = 0
            m.return_value.stdout = "pin 1  VCC\npin 2  GND\n"
            result = _pdftotext(dummy)
        assert result == "pin 1  VCC\npin 2  GND\n"

    def test_returns_empty_on_nonzero_returncode(self, tmp_path):
        dummy = tmp_path / "test.pdf"
        dummy.write_bytes(b"%PDF-1.4 dummy")
        with patch("subprocess.run") as m:
            m.return_value.returncode = 1
            m.return_value.stderr = "error"
            result = _pdftotext(dummy)
        assert result == ""

    def test_returns_empty_when_pdftotext_missing(self, tmp_path):
        dummy = tmp_path / "test.pdf"
        dummy.write_bytes(b"%PDF-1.4 dummy")
        with patch("subprocess.run", side_effect=FileNotFoundError):
            result = _pdftotext(dummy)
        assert result == ""

    def test_returns_empty_on_timeout(self, tmp_path):
        dummy = tmp_path / "test.pdf"
        dummy.write_bytes(b"%PDF-1.4 dummy")
        with patch("subprocess.run",
                   side_effect=subprocess.TimeoutExpired("pdftotext", 60)):
            result = _pdftotext(dummy)
        assert result == ""


# ---------------------------------------------------------------------------
# _ocr_pdf
# ---------------------------------------------------------------------------

class TestOcrPdf:

    def _mock_pdftoppm_success(self, tmp_dir: str, page_text: str):
        """Return a context manager that makes pdftoppm create a fake PNG and
        pytesseract return *page_text*."""
        from contextlib import contextmanager

        @contextmanager
        def ctx(pdf_path, dpi=200):
            png = Path(tmp_dir) / "page-1.png"
            png.write_bytes(b"\x89PNG fake")
            yield

        return page_text

    def test_returns_empty_when_pytesseract_missing(self, tmp_path):
        dummy = tmp_path / "test.pdf"
        dummy.write_bytes(b"%PDF-1.4 dummy")
        with patch("builtins.__import__", side_effect=ImportError):
            # Simulate pytesseract not installed
            pass
        with patch.dict("sys.modules", {"pytesseract": None}):
            result = _ocr_pdf(dummy)
        assert result == ""

    def test_returns_empty_when_pdftoppm_missing(self, tmp_path):
        dummy = tmp_path / "test.pdf"
        dummy.write_bytes(b"%PDF-1.4 dummy")
        mock_pytesseract = MagicMock()
        mock_PIL = MagicMock()
        with patch.dict("sys.modules", {"pytesseract": mock_pytesseract,
                                        "PIL": mock_PIL,
                                        "PIL.Image": mock_PIL.Image}), \
             patch("subprocess.run", side_effect=FileNotFoundError):
            result = _ocr_pdf(dummy)
        assert result == ""

    def test_returns_empty_when_pdftoppm_nonzero(self, tmp_path):
        dummy = tmp_path / "test.pdf"
        dummy.write_bytes(b"%PDF-1.4 dummy")
        mock_pyt = MagicMock()
        mock_pil = MagicMock()
        with patch.dict("sys.modules", {"pytesseract": mock_pyt,
                                        "PIL": mock_pil,
                                        "PIL.Image": mock_pil.Image}):
            with patch("subprocess.run") as m:
                m.return_value.returncode = 1
                m.return_value.stderr = b"error"
                result = _ocr_pdf(dummy)
        assert result == ""

    def test_ocr_returns_text_from_image_pages(self, tmp_path):
        """pdftoppm produces a PNG, tesseract reads it."""
        dummy = tmp_path / "test.pdf"
        dummy.write_bytes(b"%PDF-1.4 dummy")

        mock_pyt = MagicMock()
        mock_pyt.image_to_string.return_value = "QTH CONNECTOR 25 PAIRS"

        mock_pil_image = MagicMock()
        mock_pil_mod = MagicMock()
        mock_pil_mod.Image = mock_pil_image

        def fake_run(cmd, **kw):
            # Simulate pdftoppm creating page-1.png in the temp dir
            if "pdftoppm" in cmd[0]:
                prefix = Path(cmd[-1])  # last arg is prefix path
                (prefix.parent / "page-1.png").write_bytes(b"\x89PNG fake")
                r = MagicMock()
                r.returncode = 0
                return r
            return MagicMock(returncode=0, stdout="")

        with patch.dict("sys.modules", {"pytesseract": mock_pyt,
                                        "PIL": mock_pil_mod,
                                        "PIL.Image": mock_pil_image}), \
             patch("subprocess.run", side_effect=fake_run):
            result = _ocr_pdf(dummy)

        assert "QTH CONNECTOR" in result

    def test_ocr_returns_empty_when_no_png_produced(self, tmp_path):
        dummy = tmp_path / "test.pdf"
        dummy.write_bytes(b"%PDF-1.4 dummy")

        mock_pyt = MagicMock()
        mock_pil_mod = MagicMock()

        def fake_run(cmd, **kw):
            # pdftoppm succeeds but writes nothing
            r = MagicMock()
            r.returncode = 0
            return r

        with patch.dict("sys.modules", {"pytesseract": mock_pyt,
                                        "PIL": mock_pil_mod,
                                        "PIL.Image": mock_pil_mod.Image}), \
             patch("subprocess.run", side_effect=fake_run):
            result = _ocr_pdf(dummy)

        assert result == ""


# ---------------------------------------------------------------------------
# pdf_to_text — integration of pdftotext + OCR fallback
# ---------------------------------------------------------------------------

class TestPdfToTextFull:

    def test_uses_pdftotext_when_it_returns_text(self, tmp_path):
        dummy = tmp_path / "digital.pdf"
        dummy.write_bytes(b"%PDF-1.4")
        with patch("toolkit.datasheets.index._pdftotext",
                   return_value="I2C address 0x20") as mpt, \
             patch("toolkit.datasheets.index._ocr_pdf") as mocr:
            result = pdf_to_text(dummy)
        mpt.assert_called_once()
        mocr.assert_not_called()
        assert result == "I2C address 0x20"

    def test_falls_back_to_ocr_when_pdftotext_empty(self, tmp_path):
        dummy = tmp_path / "scanned.pdf"
        dummy.write_bytes(b"%PDF-1.4")
        with patch("toolkit.datasheets.index._pdftotext", return_value=""), \
             patch("toolkit.datasheets.index._ocr_pdf",
                   return_value="OCR TEXT") as mocr:
            result = pdf_to_text(dummy)
        mocr.assert_called_once()
        assert result == "OCR TEXT"

    def test_falls_back_to_ocr_when_pdftotext_whitespace_only(self, tmp_path):
        dummy = tmp_path / "blank.pdf"
        dummy.write_bytes(b"%PDF-1.4")
        with patch("toolkit.datasheets.index._pdftotext", return_value="  \n\t "), \
             patch("toolkit.datasheets.index._ocr_pdf",
                   return_value="REAL CONTENT") as mocr:
            result = pdf_to_text(dummy)
        mocr.assert_called_once()

    def test_returns_empty_when_both_fail(self, tmp_path):
        dummy = tmp_path / "empty.pdf"
        dummy.write_bytes(b"%PDF-1.4")
        with patch("toolkit.datasheets.index._pdftotext", return_value=""), \
             patch("toolkit.datasheets.index._ocr_pdf", return_value=""):
            result = pdf_to_text(dummy)
        assert result == ""


# ---------------------------------------------------------------------------
# chunk_text
# ---------------------------------------------------------------------------

class TestChunkText:

    def test_empty_returns_no_chunks(self):
        assert chunk_text("") == []

    def test_whitespace_returns_no_chunks(self):
        assert chunk_text("   \n\t  ") == []

    def test_short_text_fits_in_one_chunk(self):
        chunks = chunk_text("hello world")
        assert len(chunks) == 1
        assert chunks[0] == "hello world"

    def test_chunks_overlap(self):
        # 10 tokens, chunk_size=6, overlap=2 → starts at 0, 4, 8
        tokens = " ".join(str(i) for i in range(10))  # "0 1 2 3 4 5 6 7 8 9"
        chunks = chunk_text(tokens, chunk_size=6, overlap=2)
        # chunk 0: 0-5, chunk 1: 4-9 (starts at 4 = 6-2)
        assert len(chunks) >= 2
        # overlap: last token of chunk 0 is "5", first tokens of chunk 1 start at "4"
        assert "4" in chunks[0] and "4" in chunks[1]

    def test_exact_size_text_single_chunk(self):
        tokens = " ".join(["x"] * 10)
        chunks = chunk_text(tokens, chunk_size=10, overlap=0)
        assert len(chunks) == 1

    def test_no_trailing_empty_chunk(self):
        tokens = " ".join(["a"] * 5)
        chunks = chunk_text(tokens, chunk_size=3, overlap=1)
        for c in chunks:
            assert c.strip()


# ---------------------------------------------------------------------------
# sha256
# ---------------------------------------------------------------------------

class TestSha256:

    def test_consistent_for_same_content(self, tmp_path):
        f = tmp_path / "a.bin"
        f.write_bytes(b"hello world")
        assert sha256(f) == sha256(f)

    def test_different_for_different_content(self, tmp_path):
        f1 = tmp_path / "a.bin"
        f2 = tmp_path / "b.bin"
        f1.write_bytes(b"hello")
        f2.write_bytes(b"world")
        assert sha256(f1) != sha256(f2)

    def test_returns_hex_string(self, tmp_path):
        f = tmp_path / "a.bin"
        f.write_bytes(b"data")
        h = sha256(f)
        assert isinstance(h, str)
        assert len(h) == 64
        assert all(c in "0123456789abcdef" for c in h)


# ---------------------------------------------------------------------------
# already_indexed
# ---------------------------------------------------------------------------

class TestAlreadyIndexed:

    def test_returns_false_when_no_matching_ids(self):
        coll = MagicMock()
        coll.get.return_value = {"ids": []}
        assert already_indexed(coll, "abc123") is False

    def test_returns_true_when_ids_present(self):
        coll = MagicMock()
        coll.get.return_value = {"ids": ["abc123_0", "abc123_1"]}
        assert already_indexed(coll, "abc123") is True
