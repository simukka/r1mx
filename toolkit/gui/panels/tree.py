"""Board tree panel."""
from __future__ import annotations

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QBrush, QColor, QFont
from PyQt6.QtWidgets import QMenu, QTreeWidget, QTreeWidgetItem, QVBoxLayout, QWidget

from toolkit.db import DB
from toolkit.gui.scene import LAYER_COLORS, OBJECT_TYPES

_ROLE_KIND   = Qt.ItemDataRole.UserRole          # "board" | "layer" | "objtype" | "component"
_ROLE_BOARD  = Qt.ItemDataRole.UserRole + 1      # board name
_ROLE_LAYER  = Qt.ItemDataRole.UserRole + 2      # layer name
_ROLE_OBJT   = Qt.ItemDataRole.UserRole + 3      # object type key
_ROLE_OBJID  = Qt.ItemDataRole.UserRole + 4      # object row id (for components)


class BoardTreePanel(QWidget):
    """Left dock: tree of boards → layers → object types with visibility checkboxes."""

    # Emitted when a node is selected (board/layer) or visibility toggled
    boardSelected        = pyqtSignal(str)                    # board name
    layerSelected        = pyqtSignal(str, str)               # board, layer
    visibilityChanged    = pyqtSignal(str, str, str, bool)    # board, layer, objtype, visible
    imageSelectRequested = pyqtSignal(str, str)               # board, layer
    calibrateRequested   = pyqtSignal(str, str)               # board, layer
    editLayerRequested   = pyqtSignal(str, str)               # board, layer
    componentSelected    = pyqtSignal(int)                    # object_id
    removeDataRequested  = pyqtSignal(str, str, str)          # board, layer, type_filter ("" = all)

    def __init__(self, db: DB, parent=None):
        super().__init__(parent)
        self._db = db
        self._ignore_check = False

        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)

        self._tree = QTreeWidget()
        self._tree.setHeaderHidden(True)
        self._tree.setColumnCount(1)
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

                for key, label, color in OBJECT_TYPES:
                    ot_checked = layer_vis.get(key, True)
                    ot_item = QTreeWidgetItem([label])
                    ot_item.setData(0, _ROLE_KIND,  "objtype")
                    ot_item.setData(0, _ROLE_BOARD, bname)
                    ot_item.setData(0, _ROLE_LAYER, lname)
                    ot_item.setData(0, _ROLE_OBJT,  key)
                    ot_item.setCheckState(
                        0, Qt.CheckState.Checked if ot_checked else Qt.CheckState.Unchecked
                    )
                    ot_item.setForeground(0, QBrush(color))

                    # Populate children for scanned object types
                    if key in ("component", "text_label"):
                        layer_id = layer["id"]
                        comp_objs = self._db.conn().execute(
                            "SELECT id, label, confidence, properties FROM objects "
                            "WHERE layer_id=? AND type=? ORDER BY label",
                            (layer_id, key),
                        ).fetchall()
                        for obj in comp_objs:
                            import json as _j
                            props = _j.loads(obj["properties"] or "{}")
                            ref_type = props.get("ref_type", "")
                            conf_pct = int((obj["confidence"] or 0) * 100)
                            c_item = QTreeWidgetItem(
                                [f"{obj['label']}  [{ref_type}] {conf_pct}%"]
                            )
                            c_item.setData(0, _ROLE_KIND,  "component")
                            c_item.setData(0, _ROLE_BOARD, bname)
                            c_item.setData(0, _ROLE_LAYER, lname)
                            c_item.setData(0, _ROLE_OBJID, obj["id"])
                            ot_item.addChild(c_item)

                    l_item.addChild(ot_item)

                b_item.addChild(l_item)

            self._tree.addTopLevelItem(b_item)
            b_item.setExpanded(True)
            for i in range(b_item.childCount()):
                b_item.child(i).setExpanded(False)

        self._ignore_check = False

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
                    layer_dict[key] = ot_item.checkState(0) == Qt.CheckState.Checked
                board_dict[lname] = layer_dict
            state[bname] = board_dict
        return state

    def set_solo_layer(self, board: str, layer: str):
        """
        Uncheck every board/layer EXCEPT (board, layer).
        The target layer is checked; everything else is unchecked.
        This is called when the user clicks a layer to open it,
        so the canvas only shows the selected layer.
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
                for oi in range(l_item.childCount()):
                    l_item.child(oi).setCheckState(0, l_state)
        self._ignore_check = False

    def _on_click(self, item: QTreeWidgetItem, col: int):
        kind = item.data(0, _ROLE_KIND)
        if kind == "board":
            self.boardSelected.emit(item.data(0, _ROLE_BOARD))
        elif kind in ("layer", "objtype"):
            self.layerSelected.emit(
                item.data(0, _ROLE_BOARD), item.data(0, _ROLE_LAYER)
            )
        elif kind == "component":
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
        else:
            self.visibilityChanged.emit(board, layer, objtype, visible)

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
            sel_act.triggered.connect(lambda: self.imageSelectRequested.emit(board, layer))
            cal_act = menu.addAction("Calibrate…")
            cal_act.triggered.connect(lambda: self.calibrateRequested.emit(board, layer))
            menu.addSeparator()
            edit_act = menu.addAction("Edit layer…")
            edit_act.triggered.connect(lambda: self.editLayerRequested.emit(board, layer))

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
                        lambda: self.removeDataRequested.emit(board, layer, "")
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
                        lambda _b=board, _l=layer, _t=objtype:
                            self.removeDataRequested.emit(_b, _l, _t)
                    )

        elif kind == "board":
            act = menu.addAction("Refresh")
            act.triggered.connect(self.refresh)

        if not menu.isEmpty():
            menu.exec(self._tree.viewport().mapToGlobal(pos))

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

