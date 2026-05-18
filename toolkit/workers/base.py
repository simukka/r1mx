"""Background worker primitives."""
from __future__ import annotations

import subprocess

from PyQt6.QtCore import QThread, QObject, pyqtSignal

class WorkerSignals(QObject):
    line     = pyqtSignal(str)
    finished = pyqtSignal(bool, str)   # success, message
    layout   = pyqtSignal(dict)        # emitted by ExtractLayerWorker with the layout dict


class SubprocessWorker(QThread):
    """Run an external command in a thread and stream its output."""

    def __init__(self, cmd: list[str], parent=None):
        super().__init__(parent)
        self._cmd = cmd
        self.signals = WorkerSignals()

    def run(self):
        try:
            proc = subprocess.Popen(
                self._cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
            )
            for line in proc.stdout:
                self.signals.line.emit(line.rstrip())
            proc.wait()
            ok = proc.returncode == 0
            self.signals.finished.emit(ok, "Done" if ok else f"Exit {proc.returncode}")
        except Exception as exc:
            self.signals.finished.emit(False, str(exc))

