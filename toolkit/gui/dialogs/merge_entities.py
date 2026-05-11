"""
merge_entities.py — MergeEntitiesDialog

Dialog that lets the user merge two or more selected text_label objects into
a single component object with clean metadata.

Layout::

    ┌─────────────────────────────────────────────────────────┐
    │  Create component from 3 selected labels                │
    │                                                         │
    │  Selected labels:                                       │
    │  ┌───────────────────────────────────────────────────┐  │
    │  │ SiI3512   72%   (12.5, 8.3)                       │  │
    │  │ SiI3512   71%   (13.1, 8.3)                       │  │
    │  │ ECTU128   64%   (14.0, 9.0)                       │  │
    │  └───────────────────────────────────────────────────┘  │
    │                                                         │
    │  Ref designator:  [U1          ]                        │
    │  Part number:     [SiI3512     ]  ← auto-suggested      │
    │  Manufacturer:    [            ]                        │
    │  Value:           [            ]                        │
    │  Package:         [            ]                        │
    │                                                         │
    │                    [Cancel]  [Create Component]         │
    └─────────────────────────────────────────────────────────┘
"""

from __future__ import annotations

from collections import Counter

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QFrame,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QVBoxLayout,
)

from toolkit.db import DB


class MergeEntitiesDialog(QDialog):
    """Merge selected text_label objects into a single component.

    Parameters
    ----------
    object_ids : list of object row ids to merge (should all be text_label type)
    db         : open DB instance
    layer_id   : destination layer id for the new component object
    board_id   : parent board id

    After ``exec()`` returns ``QDialog.DialogCode.Accepted``, ``new_object_id``
    holds the id of the newly created component object.
    """

    def __init__(
        self,
        object_ids: list[int],
        db: DB,
        layer_id: int,
        board_id: int,
        parent=None,
    ):
        super().__init__(parent)
        self._db = db
        self._object_ids = object_ids
        self._layer_id = layer_id
        self._board_id = board_id
        self.new_object_id: int | None = None

        self.setWindowTitle("Create Component from Selection")
        self.setMinimumWidth(480)
        self.setSizeGripEnabled(True)

        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        # Title
        n = len(object_ids)
        title = QLabel(f"Create component from {n} selected label{'s' if n != 1 else ''}")
        title.setFont(QFont("sans-serif", 10, QFont.Weight.Bold))
        layout.addWidget(title)

        # Selected-labels list
        list_label = QLabel("Selected labels:")
        layout.addWidget(list_label)

        self._list = QListWidget()
        self._list.setMaximumHeight(120)
        self._list.setSelectionMode(QListWidget.SelectionMode.NoSelection)
        layout.addWidget(self._list)

        # Populate list and compute suggestion
        rows = db.conn().execute(
            "SELECT id, label, confidence, x_mm, y_mm FROM objects WHERE id IN ({})".format(
                ",".join("?" * len(object_ids))
            ),
            object_ids,
        ).fetchall()

        labels = []
        for r in rows:
            conf = int((r["confidence"] or 0) * 100)
            x = f"{r['x_mm']:.1f}" if r["x_mm"] is not None else "—"
            y = f"{r['y_mm']:.1f}" if r["y_mm"] is not None else "—"
            self._list.addItem(
                QListWidgetItem(f"{r['label'] or '(empty)'}   {conf}%   ({x}, {y})")
            )
            if r["label"]:
                labels.append(r["label"])

        # Auto-suggest: most common label (case-insensitive)
        suggestion = ""
        if labels:
            counter = Counter(lbl.strip().upper() for lbl in labels if lbl.strip())
            if counter:
                suggestion = counter.most_common(1)[0][0]

        # Divider
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(line)

        # Form fields
        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        self._ref  = QLineEdit()
        self._ref.setPlaceholderText("e.g. U1, R3, C12")
        form.addRow("Ref designator:", self._ref)

        self._part = QLineEdit(suggestion)
        form.addRow("Part number:", self._part)

        self._mfr = QLineEdit()
        form.addRow("Manufacturer:", self._mfr)

        self._value = QLineEdit()
        form.addRow("Value:", self._value)

        self._pkg = QLineEdit()
        form.addRow("Package:", self._pkg)

        layout.addLayout(form)

        # Info tip
        tip = QLabel(
            "The new component will be placed at the centroid of the selected labels.\n"
            "Source labels will be removed."
        )
        tip.setWordWrap(True)
        tip.setStyleSheet("color: #888; font-size: 11px;")
        layout.addWidget(tip)

        # Buttons
        btns = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        btns.button(QDialogButtonBox.StandardButton.Ok).setText("Create Component")
        btns.accepted.connect(self._on_accept)
        btns.rejected.connect(self.reject)
        layout.addWidget(btns)

        self._ref.setFocus()

    def _on_accept(self) -> None:
        ref = self._ref.text().strip()
        part = self._part.text().strip()

        if not ref:
            QMessageBox.warning(self, "Required", "Please enter a ref designator (e.g. U1).")
            self._ref.setFocus()
            return

        self.new_object_id = self._db.merge_to_component(
            self._object_ids,
            ref_designator=ref,
            part_number=part,
            layer_id=self._layer_id,
            board_id=self._board_id,
            manufacturer=self._mfr.text().strip() or None,
            value=self._value.text().strip() or None,
            package=self._pkg.text().strip() or None,
        )
        self.accept()
