"""
Tests for toolkit.gui.emulator

Pure-logic tests (no QApp):
  - decode_register / decode_register_note
  - ActivityPacket construction and properties
  - BrokerThread._parse() valid / invalid packets

Qt model / widget tests (require a QApplication):
  - EventLogModel row-count behaviour when at capacity
  - UartMonitor byte-cap and dirty-flag logic
"""
from __future__ import annotations

import struct
import sys

import pytest

from toolkit.gui.emulator import (
    DEV_DMA,
    DEV_UART,
    PACKET_MAGIC,
    PACKET_SIZE,
    ActivityPacket,
    BrokerThread,
    decode_register,
    decode_register_note,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_raw_packet(
    dev_id:    int = DEV_UART,
    direction: int = ord("W"),
    size:      int = 1,
    addr:      int = 0xE060_0004,
    value:     int = 0x41,
    ts_ns:     int = 1_000_000,
) -> bytes:
    """Build a valid 32-byte RDEV packet."""
    return (
        PACKET_MAGIC
        + bytes([dev_id, direction, size, 0])   # [4:8]
        + struct.pack(">I", addr)               # [8:12]
        + struct.pack(">I", value)              # [12:16]
        + struct.pack(">Q", ts_ns)              # [16:24]
        + bytes(8)                              # [24:32] reserved
    )


def _make_pkt(
    dev_id:    int = DEV_UART,
    direction: str = "W",
    addr:      int = 0xE060_0004,
    value:     int = 0x41,
    ts_ns:     int = 1_000_000,
) -> ActivityPacket:
    return ActivityPacket(dev_id=dev_id, direction=direction,
                          size=1, addr=addr, value=value, ts_ns=ts_ns)


# ---------------------------------------------------------------------------
# decode_register / decode_register_note — pure functions, no QApp
# ---------------------------------------------------------------------------

def test_decode_register_known_address_returns_reg_name():
    assert decode_register(0xE060_0004) == "ULITE_TX_FIFO"


def test_decode_register_known_address_note_is_non_empty():
    assert decode_register_note(0xE060_0008) != ""


def test_decode_register_device_relative_offset():
    # 0x6401_0100 is inside the DMA device range but not in REG_MAP
    result = decode_register(0x6401_0100)
    assert result.startswith("+0x")


def test_decode_register_far_address_returns_raw_hex():
    result = decode_register(0x1234_5678)
    assert result == "0x12345678"


def test_decode_register_note_unknown_address_empty():
    assert decode_register_note(0x1234_5678) == ""


# ---------------------------------------------------------------------------
# ActivityPacket — pure dataclass, no QApp
# ---------------------------------------------------------------------------

def test_activity_packet_dev_short():
    pkt = _make_pkt(dev_id=DEV_UART)
    assert pkt.dev_short == "UART"


def test_activity_packet_is_read_false_for_write():
    pkt = _make_pkt(direction="W")
    assert pkt.is_read is False


def test_activity_packet_is_read_true_for_read():
    pkt = _make_pkt(direction="R")
    assert pkt.is_read is True


def test_activity_packet_value_hex_1byte():
    pkt = _make_pkt(value=0xAB)
    assert pkt.value_hex == "0xAB"


def test_activity_packet_ts_ms_str():
    pkt = _make_pkt(ts_ns=2_500_000)
    assert pkt.ts_ms_str == "2.500"


def test_activity_packet_reg_name_known():
    pkt = _make_pkt(addr=0xE060_0004)
    assert pkt.reg_name == "ULITE_TX_FIFO"


# ---------------------------------------------------------------------------
# BrokerThread._parse() — static method, no QApp
# ---------------------------------------------------------------------------

def test_broker_parse_valid_write_packet():
    raw = _make_raw_packet(dev_id=DEV_UART, direction=ord("W"),
                           addr=0xE060_0004, value=0x48, ts_ns=5_000)
    pkt = BrokerThread._parse(raw)
    assert pkt is not None
    assert pkt.dev_id    == DEV_UART
    assert pkt.direction == "W"
    assert pkt.addr      == 0xE060_0004
    assert pkt.value     == 0x48
    assert pkt.ts_ns     == 5_000


def test_broker_parse_valid_read_packet():
    raw = _make_raw_packet(direction=ord("R"), addr=0xE060_0000, value=0x00)
    pkt = BrokerThread._parse(raw)
    assert pkt is not None
    assert pkt.direction == "R"


def test_broker_parse_bad_magic_returns_none():
    raw = b"XXXX" + _make_raw_packet()[4:]
    assert BrokerThread._parse(raw) is None


def test_broker_parse_bad_direction_returns_none():
    raw = _make_raw_packet(direction=ord("X"))
    assert BrokerThread._parse(raw) is None


def test_broker_parse_dma_packet():
    raw = _make_raw_packet(dev_id=DEV_DMA, addr=0x6401_0010, value=0x1000)
    pkt = BrokerThread._parse(raw)
    assert pkt is not None
    assert pkt.dev_short == "DMA"
    assert pkt.reg_name  == "DMA_LEN"


# ---------------------------------------------------------------------------
# Qt fixtures — EventLogModel + UartMonitor need a QApplication
# ---------------------------------------------------------------------------

pytest.importorskip("PyQt6.QtWidgets", reason="PyQt6 not available")

from PyQt6.QtWidgets import QApplication  # noqa: E402


@pytest.fixture(scope="module")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv[:1])
    return app


# ---------------------------------------------------------------------------
# EventLogModel — row count stays at _LOG_MAX after overflow (no more
# beginResetModel-on-every-packet)
# ---------------------------------------------------------------------------

def test_event_log_model_appends_below_cap(qapp):
    from toolkit.gui.emulator import EventLogModel, _LOG_MAX
    model = EventLogModel()
    for i in range(10):
        model.append(_make_pkt(ts_ns=i))
    assert model.rowCount() == 10


def test_event_log_model_row_count_caps_at_log_max(qapp):
    from toolkit.gui.emulator import EventLogModel, _LOG_MAX
    model = EventLogModel()
    for i in range(_LOG_MAX + 50):
        model.append(_make_pkt(ts_ns=i))
    assert model.rowCount() == _LOG_MAX


def test_event_log_model_newest_packet_at_last_row_after_overflow(qapp):
    """After overflowing the cap, the last row should be the most recently appended packet."""
    from toolkit.gui.emulator import EventLogModel, _LOG_MAX
    model = EventLogModel()
    for i in range(_LOG_MAX + 1):
        model.append(_make_pkt(ts_ns=i))
    last_row_idx = model.index(model.rowCount() - 1, 0)
    # The packet stored at the last deque position has ts_ns == _LOG_MAX
    last_pkt = model._rows[-1]
    assert last_pkt.ts_ns == _LOG_MAX


def test_event_log_model_clear_resets_to_zero(qapp):
    from toolkit.gui.emulator import EventLogModel
    model = EventLogModel()
    for i in range(20):
        model.append(_make_pkt(ts_ns=i))
    model.clear()
    assert model.rowCount() == 0


# ---------------------------------------------------------------------------
# UartMonitor — byte cap and dirty-flag behaviour
# ---------------------------------------------------------------------------

def test_uart_monitor_tx_bytes_capped_at_max(qapp):
    from toolkit.gui.emulator import UartMonitor
    mon = UartMonitor()
    max_bytes = UartMonitor._MAX_UART_BYTES
    # Send twice the cap limit
    for i in range(max_bytes + 200):
        pkt = _make_pkt(dev_id=DEV_UART, direction="W",
                        addr=UartMonitor.UART_TX_ADDR, value=i & 0xFF)
        mon.handle_packet(pkt)
    assert len(mon._tx_bytes) <= max_bytes


def test_uart_monitor_rx_bytes_capped_at_max(qapp):
    from toolkit.gui.emulator import UartMonitor
    mon = UartMonitor()
    max_bytes = UartMonitor._MAX_UART_BYTES
    for i in range(max_bytes + 200):
        pkt = _make_pkt(dev_id=DEV_UART, direction="R",
                        addr=UartMonitor.UART_RX_ADDR, value=i & 0xFF)
        mon.handle_packet(pkt)
    assert len(mon._rx_bytes) <= max_bytes


def test_uart_monitor_tx_dirty_set_on_write(qapp):
    from toolkit.gui.emulator import UartMonitor
    mon = UartMonitor()
    assert mon._tx_dirty is False
    pkt = _make_pkt(dev_id=DEV_UART, direction="W",
                    addr=UartMonitor.UART_TX_ADDR, value=0x41)
    mon.handle_packet(pkt)
    assert mon._tx_dirty is True


def test_uart_monitor_rx_dirty_set_on_read(qapp):
    from toolkit.gui.emulator import UartMonitor
    mon = UartMonitor()
    assert mon._rx_dirty is False
    pkt = _make_pkt(dev_id=DEV_UART, direction="R",
                    addr=UartMonitor.UART_RX_ADDR, value=0x42)
    mon.handle_packet(pkt)
    assert mon._rx_dirty is True


def test_uart_monitor_clear_resets_dirty_flags(qapp):
    from toolkit.gui.emulator import UartMonitor
    mon = UartMonitor()
    pkt = _make_pkt(dev_id=DEV_UART, direction="W",
                    addr=UartMonitor.UART_TX_ADDR, value=0x41)
    mon.handle_packet(pkt)
    assert mon._tx_dirty is True
    mon._clear()
    assert mon._tx_dirty is False
    assert mon._rx_dirty is False


def test_uart_monitor_non_uart_packet_ignored(qapp):
    from toolkit.gui.emulator import UartMonitor
    mon = UartMonitor()
    pkt = _make_pkt(dev_id=DEV_DMA, direction="W",
                    addr=0x6401_0010, value=0x1000)
    mon.handle_packet(pkt)
    assert len(mon._tx_bytes) == 0
    assert mon._tx_dirty is False
