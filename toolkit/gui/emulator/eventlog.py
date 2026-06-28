from __future__ import annotations

import socket
import struct
import sys
import time
from collections import deque
from dataclasses import dataclass, field
from typing import Deque, Dict, List, Optional, Tuple

from PyQt6.QtCore import (
    QAbstractTableModel,
    QModelIndex,
    QObject,
    Qt,
    QThread,
    QTimer,
    pyqtSignal,
)
from PyQt6.QtGui import QColor, QFont, QFontDatabase, QPalette
from PyQt6.QtWidgets import (
    QApplication,
    QComboBox,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMainWindow,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QSplitter,
    QStatusBar,
    QTableView,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from toolkit.gui.emulator.consts import decode_register_note
from toolkit.gui.emulator.broker import ActivityPacket

_LOG_COLUMNS = ["Time (ms)", "Device", "R/W", "Address", "Register", "Value", "sz"]
_LOG_MAX     = 40          # keep last N events
_COL_TS   = 0
_COL_DEV  = 1
_COL_DIR  = 2
_COL_ADDR = 3
_COL_REG  = 4
_COL_VAL  = 5
_COL_SZ   = 6

class EventLogModel(QAbstractTableModel):
    def __init__(self, parent: Optional[QObject] = None) -> None:
        super().__init__(parent)
        self._rows: Deque[ActivityPacket] = deque(maxlen=_LOG_MAX)

    def append(self, pkt: ActivityPacket) -> None:
        if len(self._rows) < _LOG_MAX:
            # Below capacity: normal row insertion.
            insert_pos = len(self._rows)
            self.beginInsertRows(QModelIndex(), insert_pos, insert_pos)
            self._rows.append(pkt)
            self.endInsertRows()
        else:
            # At capacity: the deque silently drops the oldest entry.
            # layoutAboutToBeChanged/layoutChanged keeps the view coherent
            # (row count stays at _LOG_MAX) without clearing scroll position,
            # column widths, or selections the way beginResetModel would.
            # Using beginResetModel here would fire on every single packet
            # once full, causing an O(visible_rows) repaint each time.
            self.layoutAboutToBeChanged.emit()
            self._rows.append(pkt)
            self.layoutChanged.emit()

    def clear(self) -> None:
        self.beginResetModel()
        self._rows.clear()
        self.endResetModel()

    # --- QAbstractTableModel interface ---

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return len(self._rows)

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return len(_LOG_COLUMNS)

    def headerData(self, section: int, orientation: Qt.Orientation,
                   role: int = Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole and \
                orientation == Qt.Orientation.Horizontal:
            return _LOG_COLUMNS[section]
        return None

    def data(self, index: QModelIndex,
             role: int = Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None
        pkt = self._rows[index.row()]
        col = index.column()

        if role == Qt.ItemDataRole.DisplayRole:
            if col == _COL_TS:   return pkt.ts_ms_str
            if col == _COL_DEV:  return pkt.dev_short
            if col == _COL_DIR:  return pkt.direction
            if col == _COL_ADDR: return f"0x{pkt.addr:08X}"
            if col == _COL_REG:  return pkt.reg_name
            if col == _COL_VAL:  return pkt.value_hex
            if col == _COL_SZ:   return str(pkt.size)

        if role == Qt.ItemDataRole.ForegroundRole:
            if col == _COL_DIR:
                return QColor("#3a82f7") if pkt.is_read else QColor("#f77f3a")

        if role == Qt.ItemDataRole.BackgroundRole:
            if pkt.is_read:
                return QColor("#1a2035")
            else:
                return QColor("#201a10")

        if role == Qt.ItemDataRole.ToolTipRole:
            note = decode_register_note(pkt.addr)
            return (
                f"Device: {pkt.dev_long}\n"
                f"Addr:   0x{pkt.addr:08X}\n"
                f"Reg:    {pkt.reg_name}\n"
                f"Value:  {pkt.value_hex}\n"
                f"Time:   {pkt.ts_ms_str} ms\n"
                + (f"Fields: {note}" if note else "")
            )

        return None