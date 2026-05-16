"""
StatusLCDWidget - live display of the RED ONE MX status LCD and main OSD framebuffer.

Receives pixel frames forwarded by the QEMU MMIO stub via a TCP socket on
localhost:17186. Renders them scaled up in a PyQt6 widget.

Wire protocol (binary, little-endian):
    [0:4]   magic      b'RLCD'
    [4:6]   width      uint16  pixels per row
    [6:8]   height     uint16  rows
    [8:12]  stride     uint32  bytes per row (may be > width * bytes_per_pixel)
    [12]    pixfmt     uint8   0=BGRA32  1=RGB24  2=MONO8  3=BGR565
    [13]    display    uint8   0=StatusLCD (small body LCD)  1=MainOSD (HDMI/SDI)
    [14:16] reserved   2 bytes (zero)
    [16:]   pixels     stride * height bytes
"""

from __future__ import annotations

import socket
import struct
import threading
import time
from typing import Optional

import numpy as np
from PyQt6.QtCore import QThread, pyqtSignal, Qt, QSize, QTimer
from PyQt6.QtGui import QImage, QPainter, QColor, QFont, QPixmap
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSizePolicy

MAGIC = b'RLCD'
HEADER_SIZE = 16
PORT = 17186
RECONNECT_DELAY_S = 2.0

PIXFMT_BGRA32 = 0
PIXFMT_RGB24  = 1
PIXFMT_MONO8  = 2
PIXFMT_BGR565 = 3

DISPLAY_STATUS = 0   # small body-mounted LCD (LcdManager/StatusLCD)
DISPLAY_OSD    = 1   # main HDMI/SDI OSD (FlashVx framebuffer)


class LcdFrame:
    """A single decoded pixel frame from QEMU."""

    def __init__(
        self,
        width: int,
        height: int,
        pixfmt: int,
        display: int,
        pixels: bytes,
        stride: int,
    ) -> None:
        self.width = width
        self.height = height
        self.pixfmt = pixfmt
        self.display = display
        self.pixels = pixels
        self.stride = stride

    def to_qimage(self) -> QImage:
        """Convert pixel data to a QImage (ARGB32 format)."""
        w, h = self.width, self.height

        if self.pixfmt == PIXFMT_BGRA32:
            arr = np.frombuffer(self.pixels, dtype=np.uint8)
            # Reshape to rows
            row_bytes = min(self.stride, w * 4)
            rows = []
            for row in range(h):
                start = row * self.stride
                rows.append(arr[start:start + w * 4])
            data = np.concatenate(rows)
            # BGRA -> ARGB (Qt wants ARGB32 = B,G,R,A in memory on LE)
            img = QImage(data.tobytes(), w, h, w * 4, QImage.Format.Format_ARGB32)
            return img.copy()

        elif self.pixfmt == PIXFMT_RGB24:
            arr = np.frombuffer(self.pixels, dtype=np.uint8)
            rows = []
            for row in range(h):
                start = row * self.stride
                rows.append(arr[start:start + w * 3])
            data = np.concatenate(rows)
            img = QImage(data.tobytes(), w, h, w * 3, QImage.Format.Format_RGB888)
            return img.copy()

        elif self.pixfmt == PIXFMT_MONO8:
            arr = np.frombuffer(self.pixels, dtype=np.uint8)
            rows = []
            for row in range(h):
                start = row * self.stride
                rows.append(arr[start:start + w])
            data = np.concatenate(rows)
            img = QImage(data.tobytes(), w, h, w, QImage.Format.Format_Grayscale8)
            return img.copy()

        elif self.pixfmt == PIXFMT_BGR565:
            arr = np.frombuffer(self.pixels, dtype=np.uint16)
            # Convert BGR565 -> RGBA8888 (top-bits only, no sub-LSB replication)
            b5 = (arr & 0x001F).astype(np.uint8)
            g6 = ((arr >> 5) & 0x003F).astype(np.uint8)
            r5 = ((arr >> 11) & 0x001F).astype(np.uint8)
            r8 = (r5 << 3).astype(np.uint8)
            g8 = (g6 << 2).astype(np.uint8)
            b8 = (b5 << 3).astype(np.uint8)
            rgba = np.stack([r8, g8, b8, np.full_like(r8, 255)], axis=-1)
            data = rgba.flatten().tobytes()
            img = QImage(data, w, h, w * 4, QImage.Format.Format_RGBA8888)
            return img.copy()

        # Fallback: blank grey image
        img = QImage(w, h, QImage.Format.Format_ARGB32)
        img.fill(QColor(80, 80, 80))
        return img


def _recv_exact(sock: socket.socket, n: int) -> Optional[bytes]:
    """Receive exactly n bytes; return None on connection close/error."""
    buf = bytearray()
    while len(buf) < n:
        try:
            chunk = sock.recv(n - len(buf))
        except OSError:
            return None
        if not chunk:
            return None
        buf.extend(chunk)
    return bytes(buf)


def parse_packet(data: bytes) -> Optional[LcdFrame]:
    """
    Parse one complete RLCD packet from a byte buffer.

    Returns an `LcdFrame` if the buffer is a valid, complete packet;
    returns `None` if the magic is wrong, the buffer is too short, or the
    dimensions are zero.
    """
    if len(data) < HEADER_SIZE:
        return None
    if data[:4] != MAGIC:
        return None
    width, height = struct.unpack_from("<HH", data, 4)
    (stride,) = struct.unpack_from("<I", data, 8)
    pixfmt = data[12]
    display = data[13]
    if width == 0 or height == 0 or stride == 0:
        return None
    payload_len = stride * height
    if len(data) < HEADER_SIZE + payload_len:
        return None
    pixels = data[HEADER_SIZE: HEADER_SIZE + payload_len]
    return LcdFrame(width, height, pixfmt, display, pixels, stride)


class LcdReceiverThread(QThread):
    """Background thread: connects to QEMU LCD socket, parses frames, emits signals."""

    frame_received = pyqtSignal(object)   # LcdFrame
    connection_changed = pyqtSignal(bool)  # True=connected, False=disconnected

    def __init__(self, host: str = "127.0.0.1", port: int = PORT, parent=None) -> None:
        super().__init__(parent)
        self.host = host
        self.port = port
        self._stop = threading.Event()

    def stop(self) -> None:
        self._stop.set()

    def run(self) -> None:
        while not self._stop.is_set():
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2.0)
            try:
                sock.connect((self.host, self.port))
                sock.settimeout(5.0)
                self.connection_changed.emit(True)
                self._read_frames(sock)
            except (ConnectionRefusedError, OSError, TimeoutError):
                pass
            finally:
                sock.close()
                self.connection_changed.emit(False)
            if not self._stop.is_set():
                time.sleep(RECONNECT_DELAY_S)

    def _read_frames(self, sock: socket.socket) -> None:
        while not self._stop.is_set():
            header = _recv_exact(sock, HEADER_SIZE)
            if header is None:
                return
            if header[:4] != MAGIC:
                # Bad magic; drop and try to re-sync (just return, let reconnect handle it)
                return
            width, height = struct.unpack_from("<HH", header, 4)
            (stride,) = struct.unpack_from("<I", header, 8)
            if width == 0 or height == 0 or stride == 0:
                continue
            pixel_data = _recv_exact(sock, stride * height)
            if pixel_data is None:
                return
            frame = parse_packet(header + pixel_data)
            if frame is not None:
                self.frame_received.emit(frame)


class StatusLCDWidget(QWidget):
    """
    Live display widget for the RED ONE MX status LCD and main OSD output.

    Connects to QEMU on TCP localhost:17186 and renders frames as they arrive.
    Shows a placeholder when QEMU is not running.

    Usage::

        widget = StatusLCDWidget()
        widget.show()
    """

    # Pixel scale factors for the two display types
    _SCALE_STATUS = 4   # StatusLCD: 4x zoom (small LCD)
    _SCALE_OSD = 1      # MainOSD: 1:1 or fit-to-window

    def __init__(
        self,
        host: str = "127.0.0.1",
        port: int = PORT,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)
        self._connected = False
        self._last_frame: Optional[LcdFrame] = None
        self._blink_state = False

        self._setup_ui()

        self._receiver = LcdReceiverThread(host, port, parent=self)
        self._receiver.frame_received.connect(self._on_frame)
        self._receiver.connection_changed.connect(self._on_connection_changed)
        self._receiver.start()

        # Blink timer - animates the indicator dot while connected
        self._blink_timer = QTimer(self)
        self._blink_timer.setInterval(800)
        self._blink_timer.timeout.connect(self._blink)
        self._blink_timer.start()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)

        # Header row: title + connection indicator
        header = QHBoxLayout()
        self._title_label = QLabel("STATUS LCD")
        self._title_label.setStyleSheet("font-weight: bold; font-size: 10px; color: #aaaaaa;")
        header.addWidget(self._title_label)
        header.addStretch()
        self._dot = QLabel("●")
        self._dot.setStyleSheet("color: #444444; font-size: 10px;")
        header.addWidget(self._dot)
        layout.addLayout(header)

        # Main display area
        self._display = _LCDCanvas(self)
        self._display.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        layout.addWidget(self._display, 1)

        # Status label
        self._status_label = QLabel("Waiting for QEMU on :17186...")
        self._status_label.setStyleSheet("font-size: 9px; color: #666666;")
        self._status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._status_label)

        self.setMinimumSize(QSize(200, 120))

    def _on_frame(self, frame: LcdFrame) -> None:
        self._last_frame = frame
        display_name = "STATUS LCD" if frame.display == DISPLAY_STATUS else "MAIN OSD"
        self._title_label.setText(f"{display_name}  {frame.width}x{frame.height}")
        self._display.set_frame(frame)
        self._status_label.setText(
            f"Display {frame.display} | "
            f"{frame.width}x{frame.height} | "
            f"pixfmt {frame.pixfmt}"
        )

    def _on_connection_changed(self, connected: bool) -> None:
        self._connected = connected
        if connected:
            self._dot.setStyleSheet("color: #00cc44; font-size: 10px;")
            self._status_label.setText("Connected to QEMU")
        else:
            self._dot.setStyleSheet("color: #444444; font-size: 10px;")
            if self._last_frame is None:
                self._status_label.setText("Waiting for QEMU on :17186...")
            else:
                self._status_label.setText("QEMU disconnected - showing last frame")

    def _blink(self) -> None:
        if self._connected:
            self._blink_state = not self._blink_state
            color = "#00cc44" if self._blink_state else "#006622"
            self._dot.setStyleSheet(f"color: {color}; font-size: 10px;")

    def closeEvent(self, event) -> None:
        self._receiver.stop()
        self._receiver.wait(2000)
        super().closeEvent(event)

    def get_last_frame(self) -> Optional[LcdFrame]:
        """Return the most recently received frame, or None."""
        return self._last_frame


class _LCDCanvas(QWidget):
    """Inner widget that renders the LCD pixel data."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._pixmap: Optional[QPixmap] = None
        self._frame: Optional[LcdFrame] = None
        self.setMinimumSize(128, 32)

    def set_frame(self, frame: LcdFrame) -> None:
        self._frame = frame
        qimage = frame.to_qimage()
        self._pixmap = QPixmap.fromImage(qimage)
        self.update()

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, False)
        rect = self.rect()

        if self._pixmap is None:
            painter.fillRect(rect, QColor(20, 20, 20))
            painter.setPen(QColor(80, 80, 80))
            painter.setFont(QFont("monospace", 9))
            painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, "No signal")
            return

        # Draw scaled pixmap preserving aspect ratio
        painter.fillRect(rect, QColor(10, 10, 10))
        pm = self._pixmap
        scaled = pm.scaled(
            rect.width(),
            rect.height(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.FastTransformation,
        )
        x = (rect.width() - scaled.width()) // 2
        y = (rect.height() - scaled.height()) // 2
        painter.drawPixmap(x, y, scaled)

    def sizeHint(self) -> QSize:
        if self._frame:
            scale = 4 if self._frame.display == DISPLAY_STATUS else 1
            return QSize(self._frame.width * scale, self._frame.height * scale)
        return QSize(256, 64)
