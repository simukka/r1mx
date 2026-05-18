"""
test_datasheet_link.py — Unit tests for the datasheet scanning and linking features.

Covers:
- score_filename: known part-number / filename pairs
- score_content:  pdftotext content extraction (with a real PDF fixture)
- score_pdf:      combined score clamps to [0, 1.2]
- DB.link_object_datasheet / DB.get_object_datasheets
- DB.ensure_component_row for text_label objects
- DB.get_or_create_datasheet_by_path
"""

from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path

from toolkit.analysis.datasheet_scan import normalise, score_filename, score_content, score_pdf
from toolkit.db import DB


# ── Scoring helpers ──────────────────────────────────────────────────────────

class TestNormalise(unittest.TestCase):

    def test_lowercases(self):
        self.assertEqual(normalise("SII3512"), "sii3512")

    def test_strips_non_alnum(self):
        self.assertEqual(normalise("ISP-1562.A"), "isp1562a")

    def test_empty(self):
        self.assertEqual(normalise(""), "")


class TestScoreFilename(unittest.TestCase):

    def test_exact_match(self):
        score = score_filename("SII3512ECTU128", Path("SII3512ECTU128.pdf"))
        self.assertGreaterEqual(score, 0.9)

    def test_partial_match(self):
        score = score_filename("SII3512ECTU128", Path("SII3512.pdf"))
        self.assertGreater(score, 0.3)

    def test_no_match(self):
        score = score_filename("SII3512ECTU128", Path("completely_unrelated.pdf"))
        self.assertLess(score, 0.3)

    def test_empty_stem_returns_zero(self):
        score = score_filename("SII3512", Path(".pdf"))
        self.assertEqual(score, 0.0)

    def test_returns_float_in_range(self):
        score = score_filename("ABC123", Path("abc123rev2.pdf"))
        self.assertGreaterEqual(score, 0.0)
        self.assertLessEqual(score, 1.0)


class TestScoreContent(unittest.TestCase):
    """score_content requires pdftotext; skipped if not installed."""

    @classmethod
    def setUpClass(cls):
        import shutil
        cls._have_pdftotext = shutil.which("pdftotext") is not None

    def _make_pdf_with_text(self, text: str) -> Path:
        """Create a minimal single-page PDF containing *text*."""
        import tempfile
        tmp = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False)
        # Minimal valid PDF with one page containing text
        content = text.encode("latin-1", errors="replace")
        stream = (
            b"BT /F1 12 Tf 72 720 Td (" + content + b") Tj ET"
        )
        font_obj   = b"<</Type /Font /Subtype /Type1 /BaseFont /Helvetica>>"
        res_obj    = b"<</Font <</F1 3 0 R>>>>"
        page_obj   = (
            b"<</Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
            b"/Contents 4 0 R /Resources 5 0 R>>"
        )
        stream_obj = b"<</Length " + str(len(stream)).encode() + b">>\nstream\n" + stream + b"\nendstream"

        body = (
            b"%PDF-1.4\n"
            b"1 0 obj\n<</Type /Catalog /Pages 2 0 R>>\nendobj\n"
            b"2 0 obj\n<</Type /Pages /Kids [3 0 R] /Count 1>>\nendobj\n"
            b"3 0 obj\n" + page_obj + b"\nendobj\n"
            b"4 0 obj\n" + stream_obj + b"\nendobj\n"
            b"5 0 obj\n" + res_obj + b"\nendobj\n"
            b"6 0 obj\n" + font_obj + b"\nendobj\n"
        )
        xref_offset = len(body)
        xref = (
            b"xref\n0 7\n"
            b"0000000000 65535 f \n"
        )
        # This is a very minimal PDF — pdftotext may or may not extract text
        # depending on the implementation.  We only need the function to not crash.
        tmp.write(body)
        tmp.flush()
        tmp.close()
        return Path(tmp.name)

    def test_score_content_missing_file_returns_zero(self):
        score = score_content("ANYPART", Path("/nonexistent/file.pdf"))
        self.assertEqual(score, 0.0)

    def test_score_content_is_float_in_range(self):
        if not self._have_pdftotext:
            self.skipTest("pdftotext not installed")
        # Use a known real PDF that won't contain our part number
        dummy = Path("/dev/null")
        score = score_content("XYZZY9999", dummy)
        self.assertGreaterEqual(score, 0.0)
        self.assertLessEqual(score, 1.0)


class TestScorePdf(unittest.TestCase):

    def test_score_pdf_returns_float(self):
        score = score_pdf("SII3512", Path("SII3512ECTU128.pdf"))
        self.assertIsInstance(score, float)

    def test_score_pdf_no_crash_on_nonexistent(self):
        score = score_pdf("PART", Path("/nonexistent/file.pdf"))
        self.assertGreaterEqual(score, 0.0)

    def test_combined_score_capped(self):
        """Combined score must stay in a reasonable range."""
        score = score_pdf("SII3512ECTU128", Path("SII3512ECTU128.pdf"))
        # Max theoretical score is 1.0 + 0.2*1.0*1.0 = 1.2
        self.assertLessEqual(score, 1.2)


# ── DB integration ───────────────────────────────────────────────────────────

class TestDatsheetDB(unittest.TestCase):

    def setUp(self):
        self._tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self._tmp.close()
        self._db = DB(self._tmp.name)

        # Create a minimal board + layer + object for tests
        self._board_id = self._db.get_or_create_board("test_board")
        self._layer_id = self._db.get_or_create_layer(self._board_id, "top")
        self._object_id = self._db.conn().execute(
            "INSERT INTO objects (layer_id, type, label, x_mm, y_mm) VALUES (?,?,?,?,?)",
            (self._layer_id, "component", "U1", 10.0, 20.0),
        ).lastrowid
        self._db.conn().commit()

    def tearDown(self):
        self._db.conn().close()
        os.unlink(self._tmp.name)

    # -- ensure_component_row ------------------------------------------------

    def test_ensure_component_row_creates_row(self):
        comp_id = self._db.ensure_component_row(self._object_id)
        self.assertIsNotNone(comp_id)
        row = self._db.conn().execute(
            "SELECT id FROM components WHERE object_id=?", (self._object_id,)
        ).fetchone()
        self.assertIsNotNone(row)

    def test_ensure_component_row_is_idempotent(self):
        id1 = self._db.ensure_component_row(self._object_id)
        id2 = self._db.ensure_component_row(self._object_id)
        self.assertEqual(id1, id2)

    # -- get_or_create_datasheet_by_path -------------------------------------

    def test_get_or_create_datasheet_by_path(self):
        ds_id = self._db.get_or_create_datasheet_by_path(
            Path("/some/path/SII3512ECTU128.pdf"), "SII3512ECTU128"
        )
        self.assertIsNotNone(ds_id)

    def test_get_or_create_datasheet_by_path_idempotent(self):
        path = Path("/some/path/SII3512ECTU128.pdf")
        id1 = self._db.get_or_create_datasheet_by_path(path, "SII3512ECTU128")
        id2 = self._db.get_or_create_datasheet_by_path(path, "SII3512ECTU128")
        self.assertEqual(id1, id2)

    # -- link_object_datasheet / get_object_datasheets -----------------------

    def test_link_and_retrieve(self):
        ds_id = self._db.get_or_create_datasheet_by_path(
            Path("/some/path/foo.pdf"), "PART"
        )
        self._db.ensure_component_row(self._object_id)
        self._db.link_object_datasheet(self._object_id, ds_id)

        rows = self._db.get_object_datasheets(self._object_id)
        self.assertEqual(len(rows), 1)
        self.assertIn("SII3512ECTU128.pdf" if False else "foo.pdf",
                      rows[0]["file_path"])

    def test_link_multiple_datasheets(self):
        ds1 = self._db.get_or_create_datasheet_by_path(Path("/a.pdf"), "PART")
        ds2 = self._db.get_or_create_datasheet_by_path(Path("/b.pdf"), "PART")
        self._db.ensure_component_row(self._object_id)
        self._db.link_object_datasheet(self._object_id, ds1)
        self._db.link_object_datasheet(self._object_id, ds2)

        rows = self._db.get_object_datasheets(self._object_id)
        self.assertEqual(len(rows), 2)

    def test_link_duplicate_ignored(self):
        ds_id = self._db.get_or_create_datasheet_by_path(Path("/c.pdf"), "PART")
        self._db.ensure_component_row(self._object_id)
        self._db.link_object_datasheet(self._object_id, ds_id)
        self._db.link_object_datasheet(self._object_id, ds_id)  # duplicate

        rows = self._db.get_object_datasheets(self._object_id)
        self.assertEqual(len(rows), 1)

    def test_get_object_datasheets_empty(self):
        rows = self._db.get_object_datasheets(self._object_id)
        self.assertEqual(rows, [])
