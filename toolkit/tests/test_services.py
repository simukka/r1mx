"""test_services.py — Unit tests for background service management and
the datasheet query API.

Covers:
  ServiceProcess      — health-check-only start (already running), status
  ServiceManager      — status dict shape, stop_all noop when nothing started
  chromadb_healthy    — mock HTTP responses (up / down)
  ollama_healthy      — mock HTTP responses (up / down)
  DatasheetAPI.search — mock ChromaDB HTTP
  DatasheetAPI.ask    — mock ChromaDB + Ollama HTTP
  DatasheetAPI.ask_for_object — DB lookup + scoped query
  DatasheetAPI.is_available   — mock heartbeat
  ServiceStatusBar    — dot color states via update_services / update_indexer
"""

from __future__ import annotations

import sys
import json
import pytest
from unittest.mock import MagicMock, patch


# ---------------------------------------------------------------------------
# Service health helpers (no Qt, no real HTTP)
# ---------------------------------------------------------------------------

class TestHealthHelpers:

    def test_chromadb_healthy_true_on_200(self):
        from toolkit.services.manager import chromadb_healthy
        with patch("toolkit.services.manager.requests.get") as mock_get:
            mock_get.return_value = MagicMock(status_code=200)
            assert chromadb_healthy() is True

    def test_chromadb_healthy_false_on_500(self):
        from toolkit.services.manager import chromadb_healthy
        with patch("toolkit.services.manager.requests.get") as mock_get:
            mock_get.return_value = MagicMock(status_code=500)
            assert chromadb_healthy() is False

    def test_chromadb_healthy_false_on_exception(self):
        from toolkit.services.manager import chromadb_healthy
        with patch("toolkit.services.manager.requests.get", side_effect=ConnectionError):
            assert chromadb_healthy() is False

    def test_ollama_healthy_true_on_200(self):
        from toolkit.services.manager import ollama_healthy
        with patch("toolkit.services.manager.requests.get") as mock_get:
            mock_get.return_value = MagicMock(status_code=200)
            assert ollama_healthy() is True

    def test_ollama_healthy_false_on_exception(self):
        from toolkit.services.manager import ollama_healthy
        with patch("toolkit.services.manager.requests.get", side_effect=OSError):
            assert ollama_healthy() is False


# ---------------------------------------------------------------------------
# ServiceProcess
# ---------------------------------------------------------------------------

class TestServiceProcess:

    def _make_svc(self, healthy: bool):
        from toolkit.services.manager import ServiceProcess
        return ServiceProcess(
            name="test",
            cmd=["false"],             # command that would fail if actually run
            healthy_fn=lambda: healthy,
        )

    def test_status_up_when_healthy(self):
        svc = self._make_svc(healthy=True)
        assert svc.status() == "up"

    def test_status_down_when_not_healthy_and_not_running(self):
        svc = self._make_svc(healthy=False)
        assert svc.status() == "down"

    def test_is_healthy_delegates_to_fn(self):
        svc = self._make_svc(healthy=True)
        assert svc.is_healthy() is True

    def test_start_skips_when_already_healthy(self):
        """start() must not spawn a new process if healthy_fn returns True."""
        from toolkit.services.manager import ServiceProcess
        svc = ServiceProcess("test", ["false"], healthy_fn=lambda: True)
        result = svc.start()
        assert result is True
        assert svc._proc is None   # no process spawned

    def test_stop_noop_when_no_process(self):
        svc = self._make_svc(healthy=False)
        svc.stop()   # must not raise

    def test_is_running_false_with_no_process(self):
        svc = self._make_svc(healthy=False)
        assert svc.is_running() is False

    def test_status_starting_when_process_alive_but_not_healthy(self):
        """status() == "starting" when process is running but health check fails."""
        from toolkit.services.manager import ServiceProcess
        mock_proc = MagicMock()
        mock_proc.poll.return_value = None  # still running

        svc = ServiceProcess("test", ["echo"], healthy_fn=lambda: False)
        svc._proc = mock_proc
        assert svc.status() == "starting"

    def test_start_returns_false_for_missing_binary(self):
        from toolkit.services.manager import ServiceProcess
        svc = ServiceProcess(
            "test",
            ["/nonexistent/binary/xyz"],
            healthy_fn=lambda: False,
        )
        result = svc.start()
        assert result is False


# ---------------------------------------------------------------------------
# ServiceManager
# ---------------------------------------------------------------------------

class TestServiceManager:

    def test_status_returns_dict_with_expected_keys(self):
        from toolkit.services.manager import ServiceManager
        mgr = ServiceManager()
        s = mgr.status()
        assert "chromadb" in s
        assert "ollama" in s

    def test_status_values_are_valid(self):
        from toolkit.services.manager import ServiceManager
        mgr = ServiceManager()
        valid = {"up", "starting", "down"}
        for v in mgr.status().values():
            assert v in valid

    def test_stop_all_noop_when_nothing_started(self):
        from toolkit.services.manager import ServiceManager
        mgr = ServiceManager()
        mgr.stop_all()   # must not raise

    def test_start_all_skips_when_services_healthy(self):
        """start_all() should not spawn processes if services are already up."""
        from toolkit.services.manager import ServiceManager
        mgr = ServiceManager()
        with patch.object(mgr.chromadb, "start", return_value=True) as mc, \
             patch.object(mgr.ollama,   "start", return_value=True) as mo:
            mgr.start_all()
            mc.assert_called_once()
            mo.assert_called_once()


# ---------------------------------------------------------------------------
# DatasheetAPI
# ---------------------------------------------------------------------------

def _mock_chroma_query_response(docs=None, metas=None, dists=None):
    """Build the dict that _chroma_query returns."""
    docs  = docs  or ["Test document text about register map."]
    metas = metas or [{"part_number": "PCA9698", "board": "cpu_io_board",
                        "pdf_filename": "PCA9698.pdf", "chunk_index": 0}]
    dists = dists or [0.1]
    return {
        "documents": [docs],
        "metadatas": [metas],
        "distances": [dists],
    }


class TestDatasheetAPI:

    def _api(self):
        from toolkit.datasheets.api import DatasheetAPI
        return DatasheetAPI()

    # ── is_available ─────────────────────────────────────────────────────────

    def test_is_available_true_when_200(self):
        api = self._api()
        with patch("toolkit.datasheets.api.requests.get") as mg:
            mg.return_value = MagicMock(status_code=200)
            assert api.is_available() is True

    def test_is_available_false_on_connection_error(self):
        api = self._api()
        with patch("toolkit.datasheets.api.requests.get", side_effect=ConnectionError):
            assert api.is_available() is False

    def test_is_available_false_on_non_200(self):
        api = self._api()
        with patch("toolkit.datasheets.api.requests.get") as mg:
            mg.return_value = MagicMock(status_code=503)
            assert api.is_available() is False

    # ── search ────────────────────────────────────────────────────────────────

    def test_search_returns_list_of_dicts(self):
        api = self._api()
        with patch.object(api, "_embed", return_value=[0.1] * 384), \
             patch.object(api, "_get_collection_id", return_value="col-1"), \
             patch.object(api, "_chroma_query", return_value=_mock_chroma_query_response()):
            results = api.search("I2C address")
        assert isinstance(results, list)
        assert len(results) == 1
        assert results[0]["part_number"] == "PCA9698"

    def test_search_returns_similarity_field(self):
        api = self._api()
        with patch.object(api, "_embed", return_value=[0.0] * 384), \
             patch.object(api, "_get_collection_id", return_value="col-1"), \
             patch.object(api, "_chroma_query",
                          return_value=_mock_chroma_query_response(dists=[0.2])):
            results = api.search("test")
        assert "similarity" in results[0]
        assert abs(results[0]["similarity"] - 0.8) < 1e-6

    def test_search_empty_query_returns_empty(self):
        api = self._api()
        assert api.search("") == []
        assert api.search("   ") == []

    def test_search_handles_no_results_gracefully(self):
        api = self._api()
        with patch.object(api, "_embed", return_value=[0.0] * 384), \
             patch.object(api, "_get_collection_id", return_value="col-1"), \
             patch.object(api, "_chroma_query",
                          return_value={"documents": [[]], "metadatas": [[]], "distances": [[]]}):
            results = api.search("no match")
        assert results == []

    def test_search_returns_empty_on_exception(self):
        api = self._api()
        with patch.object(api, "_embed", side_effect=RuntimeError("embed fail")):
            results = api.search("test query")
        assert results == []

    # ── ask ──────────────────────────────────────────────────────────────────

    def test_ask_returns_string(self):
        api = self._api()
        with patch.object(api, "_embed", return_value=[0.0] * 384), \
             patch.object(api, "_get_collection_id", return_value="col-1"), \
             patch.object(api, "_chroma_query", return_value=_mock_chroma_query_response()), \
             patch.object(api, "_ask_llm", return_value="The I2C address is 0x20"):
            result = api.ask("What is the I2C address?")
        assert "I2C address" in result

    def test_ask_includes_sources(self):
        api = self._api()
        with patch.object(api, "_embed", return_value=[0.0] * 384), \
             patch.object(api, "_get_collection_id", return_value="col-1"), \
             patch.object(api, "_chroma_query", return_value=_mock_chroma_query_response()), \
             patch.object(api, "_ask_llm", return_value="Answer"):
            result = api.ask("test")
        assert "Sources:" in result
        assert "PCA9698.pdf" in result

    def test_ask_empty_question_returns_error(self):
        api = self._api()
        result = api.ask("")
        assert result.startswith("Error:")

    def test_ask_no_chunks_found(self):
        api = self._api()
        with patch.object(api, "_embed", return_value=[0.0] * 384), \
             patch.object(api, "_get_collection_id", return_value="col-1"), \
             patch.object(api, "_chroma_query",
                          return_value={"documents": [[]], "metadatas": [[]], "distances": [[]]}):
            result = api.ask("no data question")
        assert "No relevant" in result

    def test_ask_returns_error_on_exception(self):
        api = self._api()
        with patch.object(api, "_embed", side_effect=ConnectionError("down")):
            result = api.ask("test")
        assert result.startswith("Error:")

    # ── ask_for_object ────────────────────────────────────────────────────────

    def test_ask_for_object_uses_part_number_filter(self):
        """When a component has a known part_number, the query should be scoped."""
        api = self._api()
        db = MagicMock()
        db.conn.return_value.execute.return_value.fetchone.return_value = {
            "part_number": "PCA9698"
        }
        db.get_object_datasheets.return_value = []

        with patch.object(api, "_embed", return_value=[0.0] * 384), \
             patch.object(api, "_get_collection_id", return_value="col-1"), \
             patch.object(api, "_chroma_query_filtered",
                          return_value=_mock_chroma_query_response()) as mf, \
             patch.object(api, "_ask_llm", return_value="Answer"):
            api.ask_for_object(db, 42, "What are the power rails?")

        mf.assert_called_once()
        assert "PCA9698" in mf.call_args[0][1]  # part_numbers list

    def test_ask_for_object_falls_back_to_global_when_no_part_number(self):
        api = self._api()
        db = MagicMock()
        db.conn.return_value.execute.return_value.fetchone.return_value = {
            "part_number": None
        }
        db.get_object_datasheets.return_value = []

        with patch.object(api, "_embed", return_value=[0.0] * 384), \
             patch.object(api, "_get_collection_id", return_value="col-1"), \
             patch.object(api, "_chroma_query",
                          return_value=_mock_chroma_query_response()) as mg, \
             patch.object(api, "_ask_llm", return_value="Answer"):
            api.ask_for_object(db, 99, "test question")

        mg.assert_called()

    def test_ask_for_object_empty_question_returns_error(self):
        api = self._api()
        db = MagicMock()
        result = api.ask_for_object(db, 1, "")
        assert result.startswith("Error:")


# ---------------------------------------------------------------------------
# ServiceStatusBar (Qt)
# ---------------------------------------------------------------------------

pytest.importorskip("PyQt6.QtWidgets", reason="PyQt6 not available")

import sys
from PyQt6.QtWidgets import QApplication


@pytest.fixture(scope="module")
def qapp():
    app = QApplication.instance() or QApplication(sys.argv[:1])
    return app


class TestServiceStatusBar:

    def test_initial_status_all_starting(self, qapp):
        from toolkit.gui.widgets.service_status import ServiceStatusBar
        bar = ServiceStatusBar()
        assert bar.chromadb_status == "starting"
        assert bar.ollama_status   == "starting"
        assert bar.indexer_status  == "starting"

    def test_update_services_sets_chromadb_up(self, qapp):
        from toolkit.gui.widgets.service_status import ServiceStatusBar
        bar = ServiceStatusBar()
        bar.update_services({"chromadb": "up", "ollama": "down"})
        assert bar.chromadb_status == "up"
        assert bar.ollama_status   == "down"

    def test_update_services_partial_update(self, qapp):
        from toolkit.gui.widgets.service_status import ServiceStatusBar
        bar = ServiceStatusBar()
        bar.update_services({"chromadb": "up"})
        assert bar.chromadb_status == "up"
        assert bar.ollama_status   == "starting"   # unchanged

    def test_update_indexer_idle(self, qapp):
        from toolkit.gui.widgets.service_status import ServiceStatusBar
        bar = ServiceStatusBar()
        bar.update_indexer("idle")
        assert bar.indexer_status == "idle"

    def test_update_indexer_running(self, qapp):
        from toolkit.gui.widgets.service_status import ServiceStatusBar
        bar = ServiceStatusBar()
        bar.update_indexer("running")
        assert bar.indexer_status == "running"

    def test_update_indexer_error(self, qapp):
        from toolkit.gui.widgets.service_status import ServiceStatusBar
        bar = ServiceStatusBar()
        bar.update_indexer("error")
        assert bar.indexer_status == "error"

    def test_all_three_status_transitions(self, qapp):
        from toolkit.gui.widgets.service_status import ServiceStatusBar
        bar = ServiceStatusBar()
        bar.update_services({"chromadb": "up", "ollama": "up"})
        bar.update_indexer("running")
        assert bar.chromadb_status == "up"
        assert bar.ollama_status   == "up"
        assert bar.indexer_status  == "running"
