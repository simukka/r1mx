"""
r1mx QEMU emulator monitor: package public API.

Re-exports the constants, dataclasses, Qt models and widgets used by the
emulator monitor GUI and by toolkit/tests/test_emulator.py so callers can do
``from toolkit.gui.emulator import ActivityPacket`` etc.
"""
from toolkit.gui.emulator.consts import (
    BROKER_HOST,
    BROKER_PORT,
    PACKET_SIZE,
    PACKET_MAGIC,
    DEV_UART,
    DEV_ETHERNET,
    DEV_DMA,
    DEV_VPFPGA,
    DEV_SDIO,
    DEV_AUDIO,
    DEV_IODMA,
    DEV_FRMBUF,
    DEV_FPGA,
    DEV_CPU,
    DEV_RAM,
    DEV_ROM,
    DEV_SDCARD,
    DEV_SSD,
    DEVICE_INFO,
    REG_MAP,
    decode_register,
    decode_register_note,
)
from toolkit.gui.emulator.broker import ActivityPacket, BrokerThread
from toolkit.gui.emulator.eventlog import EventLogModel, _LOG_MAX
from toolkit.gui.emulator.uart import UartMonitor

__all__ = [
    "BROKER_HOST",
    "BROKER_PORT",
    "PACKET_SIZE",
    "PACKET_MAGIC",
    "DEV_UART",
    "DEV_ETHERNET",
    "DEV_DMA",
    "DEV_VPFPGA",
    "DEV_SDIO",
    "DEV_AUDIO",
    "DEV_IODMA",
    "DEV_FRMBUF",
    "DEV_FPGA",
    "DEV_CPU",
    "DEV_RAM",
    "DEV_ROM",
    "DEV_SDCARD",
    "DEV_SSD",
    "DEVICE_INFO",
    "REG_MAP",
    "decode_register",
    "decode_register_note",
    "ActivityPacket",
    "BrokerThread",
    "EventLogModel",
    "_LOG_MAX",
    "UartMonitor",
]
