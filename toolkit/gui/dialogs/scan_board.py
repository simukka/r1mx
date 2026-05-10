"""Scan options dialog."""
from __future__ import annotations

from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFormLayout,
    QGroupBox,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

class ScanBoardDialog(QDialog):
    """Options dialog shown before running 'Scan Board'.

    What to scan
    ────────────
    ☑ Reference designators  (R1, C12, U7, …)
    ☑ Part numbers           (alphanumeric tokens that look like part IDs)

    Advanced (collapsible)
    ──────────────────────
    Engine: [EasyOCR ▾]
    Min confidence: [0.35 ⇕]
    Tile size: [512 ⇕]  px
    Tile overlap: [100 ⇕]  px
    ☐ Use GPU (CUDA)
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Scan Board — Options")
        self.setMinimumWidth(380)

        root = QVBoxLayout(self)
        root.setSpacing(10)

        # ── What to scan ──────────────────────────────────────────────────
        scan_box = QGroupBox("What to scan")
        scan_lay = QVBoxLayout(scan_box)
        self._cb_refs  = QCheckBox("Reference designators  (R1, C12, U7 …)")
        self._cb_parts = QCheckBox("Part numbers  (alphanumeric part IDs)")
        self._cb_refs.setChecked(True)
        self._cb_parts.setChecked(True)
        scan_lay.addWidget(self._cb_refs)
        scan_lay.addWidget(self._cb_parts)
        root.addWidget(scan_box)

        # ── Advanced (collapsible via toggle button) ───────────────────────
        self._adv_btn = QPushButton("▶  Advanced settings")
        self._adv_btn.setCheckable(True)
        self._adv_btn.setFlat(True)
        self._adv_btn.setStyleSheet("text-align:left; font-weight:bold;")
        self._adv_btn.toggled.connect(self._toggle_advanced)
        root.addWidget(self._adv_btn)

        self._adv_widget = QWidget()
        adv_form = QFormLayout(self._adv_widget)
        adv_form.setContentsMargins(12, 4, 4, 4)
        adv_form.setVerticalSpacing(6)

        self._engine = QComboBox()
        self._engine.addItems(["EasyOCR", "Tesseract"])
        adv_form.addRow("Engine:", self._engine)

        self._confidence = QDoubleSpinBox()
        self._confidence.setRange(0.0, 1.0)
        self._confidence.setSingleStep(0.05)
        self._confidence.setDecimals(2)
        self._confidence.setValue(0.35)
        self._confidence.setToolTip(
            "Minimum OCR confidence threshold (0 = accept everything, 1 = perfect only).\n"
            "Lower values find more text but with more noise."
        )
        adv_form.addRow("Min confidence:", self._confidence)

        self._tile_size = QSpinBox()
        self._tile_size.setRange(128, 4096)
        self._tile_size.setSingleStep(128)
        self._tile_size.setValue(512)
        self._tile_size.setSuffix(" px")
        self._tile_size.setToolTip(
            "Image tile size fed to the OCR engine.\n"
            "Larger tiles = more context, slower. Smaller = faster, may miss long strings."
        )
        adv_form.addRow("Tile size:", self._tile_size)

        self._tile_overlap = QSpinBox()
        self._tile_overlap.setRange(0, 512)
        self._tile_overlap.setSingleStep(16)
        self._tile_overlap.setValue(100)
        self._tile_overlap.setSuffix(" px")
        self._tile_overlap.setToolTip(
            "Overlap between adjacent tiles so text on a tile boundary is not cut off."
        )
        adv_form.addRow("Tile overlap:", self._tile_overlap)

        self._cb_gpu = QCheckBox("Use GPU (CUDA) — requires CUDA-enabled EasyOCR")
        self._cb_gpu.setChecked(False)
        adv_form.addRow("", self._cb_gpu)

        self._adv_widget.setVisible(False)
        root.addWidget(self._adv_widget)

        # ── Buttons ───────────────────────────────────────────────────────
        btns = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)
        root.addWidget(btns)

    def _toggle_advanced(self, on: bool):
        self._adv_widget.setVisible(on)
        self._adv_btn.setText(("▼" if on else "▶") + "  Advanced settings")
        self.adjustSize()

    # ── Result accessors ──────────────────────────────────────────────────

    def scan_refs(self) -> bool:
        return self._cb_refs.isChecked()

    def scan_parts(self) -> bool:
        return self._cb_parts.isChecked()

    def engine(self) -> str:
        return self._engine.currentText().lower().replace("easyocr", "easyocr")\
                                                  .replace("tesseract", "tesseract")

    def min_confidence(self) -> float:
        return self._confidence.value()

    def tile_size(self) -> int:
        return self._tile_size.value()

    def tile_overlap(self) -> int:
        return self._tile_overlap.value()

    def use_gpu(self) -> bool:
        return self._cb_gpu.isChecked()


