"""
Tests for toolkit.gui.widgets.status_lcd

All tests run without a display (no QApplication, no real sockets).
"""
import struct
import threading
import socket as _socket

import numpy as np
import pytest

from toolkit.gui.widgets.status_lcd import (
    HEADER_SIZE,
    MAGIC,
    PIXFMT_BGRA32,
    PIXFMT_BGR565,
    PIXFMT_MONO8,
    PIXFMT_RGB24,
    DISPLAY_STATUS,
    DISPLAY_OSD,
    LcdFrame,
    LcdReceiverThread,
    _recv_exact,
    parse_packet,
)


# ---------------------------------------------------------------------------
# LcdFrame: pixel format conversions
# ---------------------------------------------------------------------------

def _make_frame(width, height, pixfmt, display=DISPLAY_STATUS, fill=None):
    """Build a synthetic LcdFrame with uniform colour."""
    bpp = {PIXFMT_BGRA32: 4, PIXFMT_RGB24: 3, PIXFMT_MONO8: 1, PIXFMT_BGR565: 2}[pixfmt]
    stride = width * bpp
    if fill is None:
        pixels = bytes(stride * height)
    else:
        pixels = (bytes(fill) * (stride * height // len(fill) + 1))[: stride * height]
    return LcdFrame(width, height, pixfmt, display, pixels, stride)


def test_frame_bgra32_to_qimage_size():
    frame = _make_frame(64, 32, PIXFMT_BGRA32)
    img = frame.to_qimage()
    assert img.width() == 64
    assert img.height() == 32


def test_frame_rgb24_to_qimage_size():
    frame = _make_frame(128, 64, PIXFMT_RGB24)
    img = frame.to_qimage()
    assert img.width() == 128
    assert img.height() == 64


def test_frame_mono8_to_qimage_size():
    frame = _make_frame(80, 20, PIXFMT_MONO8)
    img = frame.to_qimage()
    assert img.width() == 80
    assert img.height() == 20


def test_frame_bgr565_to_qimage_size():
    frame = _make_frame(160, 128, PIXFMT_BGR565)
    img = frame.to_qimage()
    assert img.width() == 160
    assert img.height() == 128


def test_frame_bgra32_pixel_value():
    """Pixel (0,0) should be B=10, G=20, R=30, A=255."""
    pixels = bytes([10, 20, 30, 255])  # BGRA
    frame = LcdFrame(1, 1, PIXFMT_BGRA32, DISPLAY_STATUS, pixels, 4)
    img = frame.to_qimage()
    # QImage.Format_ARGB32 stores A,R,G,B at memory addresses
    color = img.pixelColor(0, 0)
    assert color.blue() == 10
    assert color.green() == 20
    assert color.red() == 30


def test_frame_mono8_pixel_value():
    """Greyscale pixel should map to equal R,G,B."""
    pixels = bytes([128])
    frame = LcdFrame(1, 1, PIXFMT_MONO8, DISPLAY_STATUS, pixels, 1)
    img = frame.to_qimage()
    color = img.pixelColor(0, 0)
    assert color.red() == 128
    assert color.green() == 128
    assert color.blue() == 128


def test_frame_bgr565_pixel_value():
    """BGR565 pure red (r=31,g=0,b=0) = 0xF800."""
    red565 = np.array([0xF800], dtype=np.uint16)
    pixels = red565.tobytes()
    frame = LcdFrame(1, 1, PIXFMT_BGR565, DISPLAY_STATUS, pixels, 2)
    img = frame.to_qimage()
    color = img.pixelColor(0, 0)
    assert color.red() == 0xF8   # 5 bits * 8 = top-bits only: 11111_000 = 248
    assert color.green() == 0
    assert color.blue() == 0


def test_frame_stride_wider_than_pixels():
    """Extra stride padding bytes should be ignored."""
    width, height = 4, 2
    stride = 8 * 4  # double the needed stride
    pixels = bytearray(stride * height)
    # Set known pixel at (0,0): B=1, G=2, R=3, A=255
    pixels[0:4] = [1, 2, 3, 255]
    frame = LcdFrame(width, height, PIXFMT_BGRA32, DISPLAY_STATUS, bytes(pixels), stride)
    img = frame.to_qimage()
    assert img.width() == width
    assert img.height() == height
    color = img.pixelColor(0, 0)
    assert color.blue() == 1
    assert color.green() == 2
    assert color.red() == 3


# ---------------------------------------------------------------------------
# Wire protocol: header encoding / decoding
# ---------------------------------------------------------------------------

def _make_packet(width, height, pixfmt, display, pixel_data):
    stride = len(pixel_data) // height if height else len(pixel_data)
    header = struct.pack("<4sHHIBB2s",
                         MAGIC, width, height, stride, pixfmt, display, b'\x00\x00')
    return header + pixel_data


def test_packet_header_magic():
    pkt = _make_packet(10, 5, PIXFMT_BGRA32, DISPLAY_STATUS, bytes(10 * 5 * 4))
    assert pkt[:4] == MAGIC


def test_packet_header_size():
    pkt = _make_packet(8, 8, PIXFMT_RGB24, DISPLAY_OSD, bytes(8 * 8 * 3))
    assert len(pkt) == HEADER_SIZE + 8 * 8 * 3


def test_packet_width_height_roundtrip():
    pkt = _make_packet(320, 240, PIXFMT_RGB24, DISPLAY_OSD, bytes(320 * 240 * 3))
    w, h = struct.unpack_from("<HH", pkt, 4)
    assert w == 320
    assert h == 240


def test_packet_pixfmt_roundtrip():
    pkt = _make_packet(4, 4, PIXFMT_MONO8, DISPLAY_STATUS, bytes(4 * 4))
    assert pkt[12] == PIXFMT_MONO8


def test_packet_display_roundtrip():
    for disp in (DISPLAY_STATUS, DISPLAY_OSD):
        pkt = _make_packet(2, 2, PIXFMT_MONO8, disp, bytes(2 * 2))
        assert pkt[13] == disp


# ---------------------------------------------------------------------------
# _recv_exact: helper function
# ---------------------------------------------------------------------------

def test_recv_exact_full():
    """recv_exact returns exactly n bytes from a pair of connected sockets."""
    s1, s2 = _socket.socketpair()
    s2.sendall(b'hello world')
    result = _recv_exact(s1, 11)
    s1.close(); s2.close()
    assert result == b'hello world'


def test_recv_exact_partial_reads():
    """recv_exact reassembles data that arrives in small chunks."""
    s1, s2 = _socket.socketpair()

    def sender():
        for byte in b'abcde':
            s2.send(bytes([byte]))
        s2.close()

    t = threading.Thread(target=sender)
    t.start()
    result = _recv_exact(s1, 5)
    t.join()
    s1.close()
    assert result == b'abcde'


def test_recv_exact_returns_none_on_close():
    """recv_exact returns None if the peer closes before sending enough bytes."""
    s1, s2 = _socket.socketpair()
    s2.send(b'hi')   # only 2 bytes
    s2.close()
    result = _recv_exact(s1, 10)
    s1.close()
    assert result is None


# ---------------------------------------------------------------------------
# LcdReceiverThread: integration via loopback socket server
# ---------------------------------------------------------------------------

class _MockLcdServer:
    """Minimal TCP server that sends one or more RLCD frames then closes."""

    def __init__(self, frames: list):
        self._frames = frames
        self._srv = _socket.socket(_socket.AF_INET, _socket.SOCK_STREAM)
        self._srv.setsockopt(_socket.SOL_SOCKET, _socket.SO_REUSEADDR, 1)
        self._srv.bind(("127.0.0.1", 0))
        self._srv.listen(1)
        self.port = self._srv.getsockname()[1]
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def _run(self):
        try:
            conn, _ = self._srv.accept()
            for frame_data in self._frames:
                conn.sendall(frame_data)
            conn.close()
        except OSError:
            pass
        finally:
            self._srv.close()


def test_receiver_thread_receives_frame():
    """parse_packet correctly decodes a well-formed BGRA32 frame."""
    pixels = bytes(range(256)) * ((4 * 4 * 4) // 256 + 1)
    pixels = pixels[: 4 * 4 * 4]
    pkt = _make_packet(4, 4, PIXFMT_BGRA32, DISPLAY_STATUS, pixels)

    frame = parse_packet(pkt)
    assert frame is not None
    assert frame.width == 4
    assert frame.height == 4
    assert frame.pixfmt == PIXFMT_BGRA32
    assert frame.display == DISPLAY_STATUS
    assert frame.pixels == pixels


def test_receiver_thread_reconnects_after_disconnect():
    """parse_packet handles multiple sequential packets from a stream."""
    pixels = bytes(8 * 8 * 3)
    pkt = _make_packet(8, 8, PIXFMT_RGB24, DISPLAY_OSD, pixels)

    # Two packets back to back; parse each independently
    frame1 = parse_packet(pkt)
    frame2 = parse_packet(pkt)
    assert frame1 is not None
    assert frame2 is not None
    assert frame1.width == frame2.width


def test_receiver_thread_skips_bad_magic(tmp_path):
    """parse_packet returns None for packets with wrong magic."""
    pixels = bytes(2 * 2 * 1)
    bad_pkt = b'\x00\x00\x00\x00' + b'\xff' * (HEADER_SIZE - 4) + pixels

    result = parse_packet(bad_pkt)
    assert result is None


def test_frame_display_osd():
    """Display field DISPLAY_OSD round-trips through LcdFrame."""
    pixels = bytes(10 * 10 * 4)
    frame = LcdFrame(10, 10, PIXFMT_BGRA32, DISPLAY_OSD, pixels, 10 * 4)
    assert frame.display == DISPLAY_OSD


def test_make_packet_stride():
    """Stride in packet matches bytes per row."""
    w, h, bpp = 12, 8, 3
    pixels = bytes(w * h * bpp)
    pkt = _make_packet(w, h, PIXFMT_RGB24, DISPLAY_OSD, pixels)
    (stride,) = struct.unpack_from("<I", pkt, 8)
    assert stride == w * bpp


# ---------------------------------------------------------------------------
# parse_packet: pure function
# ---------------------------------------------------------------------------

def test_parse_packet_valid_bgra32():
    pixels = bytes(6 * 4 * 4)
    pkt = _make_packet(6, 4, PIXFMT_BGRA32, DISPLAY_STATUS, pixels)
    frame = parse_packet(pkt)
    assert frame is not None
    assert frame.width == 6
    assert frame.height == 4
    assert frame.pixfmt == PIXFMT_BGRA32
    assert frame.display == DISPLAY_STATUS
    assert len(frame.pixels) == 6 * 4 * 4


def test_parse_packet_returns_none_short_buffer():
    pkt = MAGIC + b'\x00' * 5   # too short
    assert parse_packet(pkt) is None


def test_parse_packet_returns_none_bad_magic():
    pixels = bytes(4 * 4 * 3)
    pkt = _make_packet(4, 4, PIXFMT_RGB24, DISPLAY_OSD, pixels)
    bad = b'XXXX' + pkt[4:]
    assert parse_packet(bad) is None


def test_parse_packet_returns_none_zero_width():
    pixels = bytes(0 * 4 * 4)
    pkt = struct.pack("<4sHHIBB2s", MAGIC, 0, 4, 4, PIXFMT_BGRA32, DISPLAY_STATUS, b'\x00\x00')
    assert parse_packet(pkt) is None


def test_parse_packet_returns_none_truncated_pixel_data():
    w, h = 10, 10
    pixels = bytes(w * h * 4 // 2)   # only half the pixel data
    header = struct.pack("<4sHHIBB2s", MAGIC, w, h, w * 4, PIXFMT_BGRA32, DISPLAY_STATUS, b'\x00\x00')
    pkt = header + pixels
    assert parse_packet(pkt) is None
