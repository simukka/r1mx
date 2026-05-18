"""PCB layer extraction worker."""
from __future__ import annotations

from PyQt6.QtCore import QThread

from toolkit.analysis.layers import load_calibration, process_board
from toolkit.paths import COMPONENTS_DIR
from toolkit.workers.base import WorkerSignals

class ExtractLayerWorker(QThread):
    """Run extract_pcb_layers.process_board() in-process for a single layer.

    Emits:
        signals.line(str)        — progress messages
        signals.layout(dict)     — the completed layout dict
        signals.finished(ok, msg)
    """

    def __init__(self, board_name: str, layer_name: str, parent=None):
        super().__init__(parent)
        self._board_name = board_name
        self._layer_name = layer_name
        self.signals = WorkerSignals()

    def run(self):
        """Extract copper-layer geometry for the active board layer."""
        try:
            board_dir = COMPONENTS_DIR / self._board_name
            self.signals.line.emit(f"Extracting {self._board_name} / {self._layer_name} …")
            cal = load_calibration(board_dir)
            layer_cal = cal.get("layers", {}).get(self._layer_name, {})
            px_per_mm = layer_cal.get("px_per_mm", 20.0)
            layout = process_board(
                board_dir=board_dir,
                px_per_mm=px_per_mm,
                debug=False,
                hsv_overrides={},
                cal=cal,
                review=False,
                layer_filter=self._layer_name,
                progress_cb=lambda msg: self.signals.line.emit(f"  {msg}"),
            )
            self.signals.layout.emit(layout)
            is_front = self._layer_name == "top"
            self.signals.finished.emit(
                True,
                f"{len(layout.get('vias', []))} vias  {len(layout.get('pads_front' if is_front else 'pads_back', []))} pads  {len(layout.get('tracks_front' if is_front else 'tracks_back', []))} trace segments",
            )
        except Exception as exc:
            import traceback

            self.signals.line.emit(traceback.format_exc())
            self.signals.finished.emit(False, str(exc))


