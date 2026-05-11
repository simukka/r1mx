"""Board tree panel."""
from __future__ import annotations

import json as _json

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QBrush, QColor, QFont
from PyQt6.QtWidgets import (
    QInputDialog,
    QMenu,
    QMessageBox,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

from toolkit.db import DB
from toolkit.gui.scene import LAYER_COLORS, OBJECT_TYPES

_ROLE_KIND   = Qt.ItemDataRole.UserRole          # "board"|"layer"|"objtype"|"entity"
_ROLE_BOARD  = Qt.ItemDataRole.UserRole + 1      # board name
_ROLE_LAYER  = Qt.ItemDataRole.UserRole + 2      # layer name
_ROLE_OBJT   = Qt.ItemDataRole.UserRole + 3      # object type key
_ROLE_OBJID  = Qt.ItemDataRole.UserRole + 4      # object row id
_ROLE_ETYPE  = Qt.ItemDataRole.UserRole + 5      # entity object type (e.g. "text_label")

# Types shown with individual children (interactive editing supported)
_INDIVIDUAL_TYPES = {"component", "text_label", "via", "pad"}
# Cap on individual children; beyond this show a "…more" node
_CHILD_CAP = 100


class BoardTreePanel(QWidget):
    """Left dock: tree of boards → layers → object types with visibility checkboxes."""

    # Emitted when a node is selected (board/layer) or visibility toggled
    boardSelected           = pyqtSignal(str)                    # board name
    layerSelected           = pyqtSignal(str, str)               # board, layer
    visibilityChanged       = pyqtSignal(str, str, str, bool)    # board, layer, objtype, visible
    imageSelectRequested    = pyqtSignal(str, str)               # board, layer
    calibrateRequested      = pyqtSignal(str, str)               # board, layer
    editLayerRequested      = pyqtSignal(str, str)               # board, layer
    componentSelected       = pyqtSignal(int)                    # object_id
    removeDataRequested     = pyqtSignal(str, str, str)          # board, layer, type_filter ("" = all)
    scanDatasheetRequested  = pyqtSignal(str, str, int)          # board, layer, object_id
    # Entity CRUD signals
    entityDeleteRequested   = pyqtSignal(int)                    # object_id
    entityEditRequested     = pyqtSignal(int)                    # object_id
    entityVerifyRequested   = pyqtSignal(int)                    # object_id
    mergeRequested          = pyqtSignal(list)                   # list[int] object_ids

    def __init__(self, db: DB, parent=None):
        super().__init__(parent)
        self._db = db
        self._ignore_check = False

        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)

        self._tree = QTreeWidget()
        self._tree.setHeaderHidden(True)
        self._tree.setColumnCount(1)
        self._tree.setSelectionMode(QTreeWidget.SelectionMode.ExtendedSelection)
        self._tree.itemClicked.connect(self._on_click)
        self._tree.itemChanged.connect(self._on_check)
        self._tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self._tree.customContextMenuRequested.connect(self._on_context_menu)
        layout.addWidget(self._tree)

        self.refresh()

    def refresh(self, vis_state: dict | None = None):
        """Rebuild tree from DB.

        Parameters
        ----------
        vis_state : optional dict from DB.load_visibility_state().
                    When provided, checkboxes are restored from it.
                    When None, all items default to Checked.
        """
        self._ignore_check = True
        self._tree.clear()
        vs = vis_state or {}

        for board in self._db.list_boards():
            bname = board["name"]
            board_vis = vs.get(bname, {})
            b_checked = board_vis.get("__board__", True)

            b_item = QTreeWidgetItem([bname])
            b_item.setData(0, _ROLE_KIND,  "board")
            b_item.setData(0, _ROLE_BOARD, bname)
            b_item.setCheckState(
                0, Qt.CheckState.Checked if b_checked else Qt.CheckState.Unchecked
            )
            b_item.setFont(0, QFont("sans-serif", 9, QFont.Weight.Bold))

            for layer in self._db.list_layers(board["id"]):
                lname = layer["name"]
                src = layer["source_image"] or ""
                cal_mark = "  ✓" if layer["calibrated"] else ""
                lbl = f"{lname}{cal_mark}"
                if src:
                    lbl += f"  [{src}]"

                layer_vis = board_vis.get(lname, {})
                l_checked = layer_vis.get("__layer__", True)

                l_item = QTreeWidgetItem([lbl])
                l_item.setData(0, _ROLE_KIND,  "layer")
                l_item.setData(0, _ROLE_BOARD, bname)
                l_item.setData(0, _ROLE_LAYER, lname)
                l_item.setCheckState(
                    0, Qt.CheckState.Checked if l_checked else Qt.CheckState.Unchecked
                )
                color = LAYER_COLORS.get(lname, QColor(150, 150, 150))
                l_item.setForeground(0, QBrush(color))
                l_item.setToolTip(0, f"Source image: {src or '(none)'}\n"
                                     "Right-click → Select image…")

                layer_id = layer["id"]
                for key, label, color in OBJECT_TYPES:
                    # Count objects of this type
                    count = self._db.conn().execute(
                        "SELECT COUNT(*) FROM objects WHERE layer_id=? AND type=?",
                        (layer_id, key),
                    ).fetchone()[0]

                    ot_checked = layer_vis.get(key, True)
                    count_suffix = f"  ({count})" if count else ""
                    ot_item = QTreeWidgetItem([f"{label}{count_suffix}"])
                    ot_item.setData(0, _ROLE_KIND,  "objtype")
                    ot_item.setData(0, _ROLE_BOARD, bname)
                    ot_item.setData(0, _ROLE_LAYER, lname)
                    ot_item.setData(0, _ROLE_OBJT,  key)
                    ot_item.setCheckState(
                        0, Qt.CheckState.Checked if ot_checked else Qt.CheckState.Unchecked
                    )
                    ot_item.setForeground(0, QBrush(color))

                    # Individual children for interactive types
                    if key in _INDIVIDUAL_TYPES and count > 0:
                        self._populate_entity_children(
                            ot_item, layer_id, key, bname, lname, color
                        )

                    l_item.addChild(ot_item)

                b_item.addChild(l_item)

            self._tree.addTopLevelItem(b_item)
            b_item.setExpanded(True)
            for i in range(b_item.childCount()):
                b_item.child(i).setExpanded(False)

        self._ignore_check = False

    def _populate_entity_children(
        self,
        parent_item: QTreeWidgetItem,
        layer_id: int,
        obj_type: str,
        board: str,
        layer: str,
        color: QColor,
    ) -> None:
        """Add individual entity rows as children of a type node (capped at 100)."""
        objs = self._db.conn().execute(
            "SELECT id, label, confidence, verified FROM objects "
            "WHERE layer_id=? AND type=? ORDER BY label, id LIMIT ?",
            (layer_id, obj_type, _CHILD_CAP + 1),
        ).fetchall()

        shown = objs[:_CHILD_CAP]
        overflow = len(objs) > _CHILD_CAP

        for obj in shown:
            props_raw = self._db.conn().execute(
                "SELECT properties FROM objects WHERE id=?", (obj["id"],)
            ).fetchone()
            props = _json.loads((props_raw["properties"] if props_raw else None) or "{}")
            ref_type = props.get("ref_type", "")
            conf_pct = int((obj["confidence"] or 0) * 100)
            verify_badge = " ✓" if obj["verified"] else ""

            if ref_type:
                row_lbl = f"{obj['label'] or '—'}  [{ref_type}] {conf_pct}%{verify_badge}"
            else:
                row_lbl = f"{obj['label'] or '—'}  {conf_pct}%{verify_badge}"

            c_item = QTreeWidgetItem([row_lbl])
            c_item.setData(0, _ROLE_KIND,  "entity")
            c_item.setData(0, _ROLE_BOARD, board)
            c_item.setData(0, _ROLE_LAYER, layer)
            c_item.setData(0, _ROLE_OBJID, obj["id"])
            c_item.setData(0, _ROLE_ETYPE, obj_type)
            c_item.setForeground(0, QBrush(color))
            parent_item.addChild(c_item)

        if overflow:
            more_item = QTreeWidgetItem([f"  … {len(objs) - _CHILD_CAP} more (use filter)"])
            more_item.setData(0, _ROLE_KIND, "more")
            more_item.setForeground(0, QBrush(QColor(140, 140, 140)))
            more_item.setFlags(Qt.ItemFlag.ItemIsEnabled)
            parent_item.addChild(more_item)

    def get_full_vis_state(self) -> dict:
        """Return a nested dict of current checkbox states for persistence."""
        state = {}
        root = self._tree.invisibleRootItem()
        for bi in range(root.childCount()):
            b_item = root.child(bi)
            bname = b_item.data(0, _ROLE_BOARD)
            b_checked = b_item.checkState(0) == Qt.CheckState.Checked
            board_dict: dict = {"__board__": b_checked}
            for li in range(b_item.childCount()):
                l_item = b_item.child(li)
                lname = l_item.data(0, _ROLE_LAYER)
                l_checked = l_item.checkState(0) == Qt.CheckState.Checked
                layer_dict: dict = {"__layer__": l_checked}
                for oi in range(l_item.childCount()):
                    ot_item = l_item.child(oi)
                    key = ot_item.data(0, _ROLE_OBJT)
                    if key:
                        layer_dict[key] = ot_item.checkState(0) == Qt.CheckState.Checked
                board_dict[lname] = layer_dict
            state[bname] = board_dict
        return state

    def set_solo_layer(self, board: str, layer: str):
        """
        Uncheck every board/layer EXCEPT (board, layer).
        The target layer is checked; everything else is unchecked.

        Crucially, the target layer's *objtype* children (Vias, Traces, etc.)
        are left untouched so their saved per-type visibility is preserved.
        Non-target layers' objtype children are all unchecked for clarity.
        """
        self._ignore_check = True
        root = self._tree.invisibleRootItem()
        for bi in range(root.childCount()):
            b_item = root.child(bi)
            bname = b_item.data(0, _ROLE_BOARD)
            is_target_board = (bname == board)
            b_state = Qt.CheckState.Checked if is_target_board else Qt.CheckState.Unchecked
            b_item.setCheckState(0, b_state)
            for li in range(b_item.childCount()):
                l_item = b_item.child(li)
                lname = l_item.data(0, _ROLE_LAYER)
                is_target = is_target_board and (lname == layer)
                l_state = Qt.CheckState.Checked if is_target else Qt.CheckState.Unchecked
                l_item.setCheckState(0, l_state)
                if not is_target:
                    # Cascade unchecked to all objtype children for non-target layers
                    for oi in range(l_item.childCount()):
                        l_item.child(oi).setCheckState(0, Qt.CheckState.Unchecked)
                # Target layer: leave objtype children as-is (preserves saved state)
        self._ignore_check = False

    def _on_click(self, item: QTreeWidgetItem, col: int):
        kind = item.data(0, _ROLE_KIND)
        if kind == "board":
            self.boardSelected.emit(item.data(0, _ROLE_BOARD))
        elif kind in ("layer", "objtype"):
            self.layerSelected.emit(
                item.data(0, _ROLE_BOARD), item.data(0, _ROLE_LAYER)
            )
        elif kind == "entity":
            obj_id = item.data(0, _ROLE_OBJID)
            if obj_id is not None:
                self.componentSelected.emit(obj_id)

    def _on_check(self, item: QTreeWidgetItem, col: int):
        if self._ignore_check:
            return
        kind    = item.data(0, _ROLE_KIND)
        board   = item.data(0, _ROLE_BOARD) or ""
        layer   = item.data(0, _ROLE_LAYER) or ""
        objtype = item.data(0, _ROLE_OBJT)  or ""
        visible = item.checkState(0) == Qt.CheckState.Checked

        if kind == "board":
            # Cascade to all children
            self._ignore_check = True
            state = Qt.CheckState.Checked if visible else Qt.CheckState.Unchecked
            for i in range(item.childCount()):
                l_item = item.child(i)
                l_item.setCheckState(0, state)
                for j in range(l_item.childCount()):
                    l_item.child(j).setCheckState(0, state)
            self._ignore_check = False
            self.visibilityChanged.emit(board, "", "", visible)
        elif kind == "layer":
            self._ignore_check = True
            state = Qt.CheckState.Checked if visible else Qt.CheckState.Unchecked
            for i in range(item.childCount()):
                item.child(i).setCheckState(0, state)
            self._ignore_check = False
            self.visibilityChanged.emit(board, layer, "", visible)
        elif kind == "objtype":
            self.visibilityChanged.emit(board, layer, objtype, visible)

    def _selected_entity_ids(self) -> list[int]:
        """Return object_ids for all currently selected entity items."""
        ids = []
        for item in self._tree.selectedItems():
            if item.data(0, _ROLE_KIND) == "entity":
                oid = item.data(0, _ROLE_OBJID)
                if oid is not None:
                    ids.append(oid)
        return ids

    def _on_context_menu(self, pos):
        item = self._tree.itemAt(pos)
        if item is None:
            return
        kind   = item.data(0, _ROLE_KIND)
        board  = item.data(0, _ROLE_BOARD) or ""
        layer  = item.data(0, _ROLE_LAYER) or ""
        objtype = item.data(0, _ROLE_OBJT) or ""

        menu = QMenu(self)
        if kind == "layer":
            sel_act = menu.addAction("Select image…")
            sel_act.triggered.connect(lambda checked, _b=board, _l=layer: self.imageSelectRequested.emit(_b, _l))
            cal_act = menu.addAction("Calibrate…")
            cal_act.triggered.connect(lambda checked, _b=board, _l=layer: self.calibrateRequested.emit(_b, _l))
            menu.addSeparator()
            edit_act = menu.addAction("Edit layer…")
            edit_act.triggered.connect(lambda checked, _b=board, _l=layer: self.editLayerRequested.emit(_b, _l))

            # "Remove data" if the layer has any objects at all
            board_id  = self._db.get_or_create_board(board)
            layer_row = self._db.get_layer(board_id, layer)
            if layer_row:
                count = self._db.conn().execute(
                    "SELECT COUNT(*) FROM objects WHERE layer_id=?",
                    (layer_row["id"],),
                ).fetchone()[0]
                if count:
                    menu.addSeparator()
                    rm_act = menu.addAction(f"Remove all data  ({count} objects)…")
                    rm_act.triggered.connect(
                        lambda checked, _b=board, _l=layer: self.removeDataRequested.emit(_b, _l, "")
                    )

        elif kind == "objtype":
            # "Remove data" for this specific object type
            board_id  = self._db.get_or_create_board(board)
            layer_row = self._db.get_layer(board_id, layer)
            if layer_row and objtype:
                count = self._db.conn().execute(
                    "SELECT COUNT(*) FROM objects WHERE layer_id=? AND type=?",
                    (layer_row["id"], objtype),
                ).fetchone()[0]
                if count:
                    rm_act = menu.addAction(f"Remove {objtype} data  ({count} objects)…")
                    rm_act.triggered.connect(
                        lambda checked, _b=board, _l=layer, _t=objtype:
                            self.removeDataRequested.emit(_b, _l, _t)
                    )

        elif kind == "entity":
            obj_id = item.data(0, _ROLE_OBJID)
            etype  = item.data(0, _ROLE_ETYPE) or ""
            selected_ids = self._selected_entity_ids()

            if obj_id is not None:
                # Single-entity actions
                edit_act = menu.addAction("✎ Edit label…")
                edit_act.triggered.connect(
                    lambda checked, _oid=obj_id: self._edit_label(_oid)
                )

                verify_act = menu.addAction("✓ Mark as verified")
                verify_act.triggered.connect(
                    lambda checked, _oid=obj_id: self.entityVerifyRequested.emit(_oid)
                )

                menu.addSeparator()
                scan_act = menu.addAction("🔍 Scan for datasheet…")
                scan_act.triggered.connect(
                    lambda checked, _b=board, _l=layer, _oid=obj_id:
                        self.scanDatasheetRequested.emit(_b, _l, _oid)
                )

                menu.addSeparator()
                del_act = menu.addAction("🗑 Delete")
                del_act.triggered.connect(
                    lambda checked, _oid=obj_id: self._confirm_delete([_oid])
                )

            # Multi-select: offer merge only if ≥2 text_labels selected
            text_label_ids = []
            for sel in self._tree.selectedItems():
                if (sel.data(0, _ROLE_KIND) == "entity" and
                        sel.data(0, _ROLE_ETYPE) == "text_label"):
                    tid = sel.data(0, _ROLE_OBJID)
                    if tid is not None:
                        text_label_ids.append(tid)

            if len(text_label_ids) >= 2:
                menu.addSeparator()
                merge_act = menu.addAction(
                    f"⊕ Create component from {len(text_label_ids)} selected labels…"
                )
                merge_act.triggered.connect(
                    lambda checked, _ids=list(text_label_ids):
                        self.mergeRequested.emit(_ids)
                )

            # Multi-entity delete
            if len(selected_ids) >= 2:
                menu.addSeparator()
                del_all_act = menu.addAction(f"🗑 Delete {len(selected_ids)} selected…")
                del_all_act.triggered.connect(
                    lambda checked, _ids=list(selected_ids): self._confirm_delete(_ids)
                )

        elif kind == "board":
            act = menu.addAction("Refresh")
            act.triggered.connect(self.refresh)

        if not menu.isEmpty():
            menu.exec(self._tree.viewport().mapToGlobal(pos))

    def _edit_label(self, object_id: int) -> None:
        """Prompt user to edit the label of an entity inline."""
        row = self._db.conn().execute(
            "SELECT label FROM objects WHERE id=?", (object_id,)
        ).fetchone()
        current = row["label"] if row else ""
        new_label, ok = QInputDialog.getText(
            self, "Edit Label", "Label:", text=current or ""
        )
        if ok and new_label.strip() != current:
            self._db.update_object(object_id, label=new_label.strip())
            self.entityEditRequested.emit(object_id)
            self.refresh()

    def _confirm_delete(self, object_ids: list[int]) -> None:
        n = len(object_ids)
        reply = QMessageBox.question(
            self,
            "Delete",
            f"Delete {n} object{'s' if n > 1 else ''}?  This cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            for oid in object_ids:
                self.entityDeleteRequested.emit(oid)

    def is_layer_visible(self, board: str, layer: str) -> bool:
        """Return the current checkbox state for a layer node."""
        root = self._tree.invisibleRootItem()
        for bi in range(root.childCount()):
            b_item = root.child(bi)
            if b_item.data(0, _ROLE_BOARD) != board:
                continue
            if b_item.checkState(0) != Qt.CheckState.Checked:
                return False
            for li in range(b_item.childCount()):
                l_item = b_item.child(li)
                if l_item.data(0, _ROLE_LAYER) == layer:
                    return l_item.checkState(0) == Qt.CheckState.Checked
        return True  # default visible if not found



