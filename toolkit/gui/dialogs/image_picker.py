"""Image picker dialog."""
from __future__ import annotations

from pathlib import Path

from PyQt6.QtCore import Qt, QSize
from PyQt6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from toolkit.gui.scene import _IMAGE_EXTS
from toolkit.gui.viewer import bgr_to_pixmap

class ImagePickerDialog(QDialog):
    """
    Shows thumbnail previews of every image file in a board directory.
    The user selects one; the chosen filename is returned via `selected_file`.

    Usage::

        dlg = ImagePickerDialog(board_dir, current_image, parent=self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            chosen = dlg.selected_file   # relative filename, e.g. "P1003481.JPG"
    """

    _THUMB_W = 200
    _THUMB_H = 150

    def __init__(self, board_dir: Path, current_image: str = "", parent=None):
        super().__init__(parent)
        self.selected_file: str = current_image
        self._board_dir = board_dir

        self.setWindowTitle(f"Select image — {board_dir.name}")
        self.resize(900, 600)
        self.setSizeGripEnabled(True)

        layout = QVBoxLayout(self)
        layout.setSpacing(8)

        info = QLabel(f"Board directory: <code>{board_dir}</code><br>"
                      "Double-click an image to select it.")
        info.setTextFormat(Qt.TextFormat.RichText)
        layout.addWidget(info)

        # Scroll area containing a grid of thumbnail buttons
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        grid_widget = QWidget()
        self._grid = QHBoxLayout(grid_widget)   # wrapping done via flow — simpler: use list
        scroll.setWidget(grid_widget)
        layout.addWidget(scroll, stretch=1)

        # Use QListWidget in icon mode — handles wrapping and selection automatically
        self._list = QListWidget()
        self._list.setViewMode(QListWidget.ViewMode.IconMode)
        self._list.setIconSize(
            __import__("PyQt6.QtCore", fromlist=["QSize"]).QSize(self._THUMB_W, self._THUMB_H)
        )
        self._list.setResizeMode(QListWidget.ResizeMode.Adjust)
        self._list.setSpacing(8)
        self._list.setWordWrap(True)
        self._list.itemDoubleClicked.connect(self._accept_item)
        layout.addWidget(self._list, stretch=1)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self._on_ok)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self._populate()

    def _populate(self):
        """Scan board dir and add thumbnails to the list."""
        import cv2
        from PyQt6.QtCore import QSize
        from PyQt6.QtGui import QIcon

        files = sorted(
            f for f in self._board_dir.iterdir()
            if f.suffix in _IMAGE_EXTS
        )
        if not files:
            item = QListWidgetItem("No image files found")
            self._list.addItem(item)
            return

        for fpath in files:
            img = cv2.imread(str(fpath))
            if img is None:
                continue
            # Scale thumbnail preserving aspect ratio
            h, w = img.shape[:2]
            scale = min(self._THUMB_W / w, self._THUMB_H / h)
            tw, th = int(w * scale), int(h * scale)
            thumb = cv2.resize(img, (tw, th), interpolation=cv2.INTER_AREA)
            pixmap = bgr_to_pixmap(thumb)

            item = QListWidgetItem(QIcon(pixmap), fpath.name)
            item.setData(Qt.ItemDataRole.UserRole, fpath.name)
            item.setToolTip(f"{fpath.name}\n{w}×{h} px")
            self._list.addItem(item)

            # Pre-select the current image
            if fpath.name == self.selected_file:
                self._list.setCurrentItem(item)

    def _accept_item(self, item: QListWidgetItem):
        self.selected_file = item.data(Qt.ItemDataRole.UserRole) or item.text()
        self.accept()

    def _on_ok(self):
        item = self._list.currentItem()
        if item:
            self.selected_file = item.data(Qt.ItemDataRole.UserRole) or item.text()
        self.accept()

