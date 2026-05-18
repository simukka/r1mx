"""
manager.py — Background service lifecycle management for r1mx toolkit.

Manages two external processes that the datasheet RAG pipeline depends on:

  ChromaDB  — vector database for semantic datasheet search
              Command: .venv/bin/chroma run --host localhost --port <port>
                       --path <repo>/chroma_data
              Health:  GET localhost:8000/api/v2/heartbeat

  Ollama    — local LLM inference for RAG answers
              Command: ollama serve
              Health:  GET localhost:11434/api/tags

Usage
-----
    mgr = ServiceManager()
    mgr.start_all()                  # start processes that aren't yet running
    status = mgr.status()            # {"chromadb": "up", "ollama": "down", ...}
    mgr.stop_all()                   # graceful shutdown (called in closeEvent)

Status Monitor (Qt)
-------------------
    monitor = ServiceMonitor(mgr, parent)
    monitor.statusChanged.connect(my_slot)   # slot receives dict[str, str]
    monitor.start()
"""

from __future__ import annotations

import logging
import os
import signal
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

import requests
from PyQt6.QtCore import QThread, pyqtSignal

from toolkit.paths import REPO_ROOT

log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Environment / config
# ---------------------------------------------------------------------------

_env_file = REPO_ROOT / ".env"
if _env_file.exists():
    for _line in _env_file.read_text().splitlines():
        _line = _line.strip()
        if _line and not _line.startswith("#") and "=" in _line:
            _k, _, _v = _line.partition("=")
            os.environ.setdefault(_k.strip(), _v.strip())

CHROMA_HOST  = os.environ.get("CHROMA_HOST",  "http://localhost:8000")
OLLAMA_HOST  = os.environ.get("OLLAMA_HOST",  "http://localhost:11434")
CHROMA_DATA  = REPO_ROOT / "chroma_data"

# Locate the chroma binary inside the venv (same Python prefix as the app)
_VENV_BIN = Path(sys.executable).parent
_CHROMA_BIN = _VENV_BIN / "chroma"
_OLLAMA_BIN = os.environ.get("OLLAMA_BIN", "ollama")   # full path or just 'ollama'

MONITOR_INTERVAL_S = 5   # health-check poll interval

# ---------------------------------------------------------------------------
# Health check helpers
# ---------------------------------------------------------------------------

def _is_healthy(url: str, timeout: float = 3.0) -> bool:
    """Return True if the service at *url* responds with HTTP 200."""
    try:
        r = requests.get(url, timeout=timeout)
        return r.status_code == 200
    except Exception:
        return False


def chromadb_healthy() -> bool:
    return _is_healthy(f"{CHROMA_HOST}/api/v2/heartbeat")


def ollama_healthy() -> bool:
    return _is_healthy(f"{OLLAMA_HOST}/api/tags")


# ---------------------------------------------------------------------------
# ServiceProcess — wraps a single background subprocess
# ---------------------------------------------------------------------------

class ServiceProcess:
    """Manages the lifecycle of a single external service subprocess.

    Parameters
    ----------
    name     : human-readable name for logging
    cmd      : command list passed to ``subprocess.Popen``
    healthy_fn: callable() → bool — returns True when the service is up
    """

    def __init__(self, name: str, cmd: list[str], healthy_fn):
        self.name = name
        self._cmd = cmd
        self._healthy_fn = healthy_fn
        self._proc: subprocess.Popen | None = None

    # ── Public API ──────────────────────────────────────────────────────────

    def start(self) -> bool:
        """Start the service if not already running or already healthy.

        Returns True if the service was started (or was already running).
        Returns False if the binary was not found.
        """
        if self._healthy_fn():
            log.info("[%s] already running", self.name)
            return True

        if self._proc and self._proc.poll() is None:
            log.info("[%s] process already launched", self.name)
            return True

        log.info("[%s] starting: %s", self.name, " ".join(self._cmd))
        try:
            self._proc = subprocess.Popen(
                self._cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                # New process group so Ctrl-C in terminal doesn't kill it
                start_new_session=True,
            )
            return True
        except FileNotFoundError:
            log.warning("[%s] binary not found: %s", self.name, self._cmd[0])
            return False
        except Exception as exc:
            log.error("[%s] failed to start: %s", self.name, exc)
            return False

    def stop(self) -> None:
        """Gracefully stop the service if we own its process."""
        if self._proc is None:
            return
        if self._proc.poll() is not None:
            self._proc = None
            return
        log.info("[%s] stopping", self.name)
        try:
            self._proc.terminate()
            try:
                self._proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self._proc.kill()
        except Exception as exc:
            log.warning("[%s] stop error: %s", self.name, exc)
        finally:
            self._proc = None

    def is_running(self) -> bool:
        """Return True if the process we started is still alive."""
        if self._proc is None:
            return False
        return self._proc.poll() is None

    def is_healthy(self) -> bool:
        return self._healthy_fn()

    def status(self) -> str:
        """Return ``"up"``, ``"starting"``, or ``"down"``."""
        if self._healthy_fn():
            return "up"
        if self.is_running():
            return "starting"
        return "down"


# ---------------------------------------------------------------------------
# ServiceManager — owns all service processes
# ---------------------------------------------------------------------------

class ServiceManager:
    """Manages ChromaDB and Ollama service processes."""

    def __init__(self):
        from urllib.parse import urlparse
        parsed = urlparse(CHROMA_HOST)
        chroma_host = parsed.hostname or "localhost"
        chroma_port = str(parsed.port or 8000)

        self.chromadb = ServiceProcess(
            name="chromadb",
            cmd=[
                str(_CHROMA_BIN),
                "run",
                "--host", chroma_host,
                "--port", chroma_port,
                "--path", str(CHROMA_DATA),
            ],
            healthy_fn=chromadb_healthy,
        )

        self.ollama = ServiceProcess(
            name="ollama",
            cmd=[str(_OLLAMA_BIN), "serve"],
            healthy_fn=ollama_healthy,
        )

        self._services: list[ServiceProcess] = [self.chromadb, self.ollama]

    def start_all(self) -> None:
        """Start all services (skips those already running)."""
        CHROMA_DATA.mkdir(parents=True, exist_ok=True)
        for svc in self._services:
            svc.start()

    def stop_all(self) -> None:
        """Stop all services that *we* started."""
        for svc in reversed(self._services):
            svc.stop()

    def status(self) -> dict[str, str]:
        """Return {service_name: status_str} for all managed services."""
        return {svc.name: svc.status() for svc in self._services}


# ---------------------------------------------------------------------------
# ServiceMonitor — polls health in a QThread, emits signal on changes
# ---------------------------------------------------------------------------

class ServiceMonitor(QThread):
    """Background thread that polls service health and emits ``statusChanged``.

    Parameters
    ----------
    manager : ServiceManager
    parent  : QObject parent (optional)

    Signals
    -------
    statusChanged(dict)
        Emitted whenever any service status changes, and once on first poll.
        Dict keys: ``"chromadb"``, ``"ollama"`` — values: ``"up" | "starting" | "down"``
    """

    statusChanged = pyqtSignal(dict)

    def __init__(self, manager: ServiceManager, parent=None):
        super().__init__(parent)
        self._manager = manager
        self._stop = False
        self._last: dict[str, str] = {}

    def run(self) -> None:
        while not self._stop:
            current = self._manager.status()
            if current != self._last:
                self._last = dict(current)
                self.statusChanged.emit(dict(current))
            # Sleep in small increments so stop() is responsive
            for _ in range(MONITOR_INTERVAL_S * 4):
                if self._stop:
                    return
                time.sleep(0.25)

    def stop(self) -> None:
        self._stop = True
