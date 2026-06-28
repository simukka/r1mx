from typing import Deque, Dict, List, Optional, Tuple

BROKER_HOST = "127.0.0.1"
BROKER_PORT = 17187
PACKET_SIZE = 32
PACKET_MAGIC = b"RDEV"

# Device IDs (must match r1mx_activity.h)
DEV_UART       = 0
DEV_ETHERNET   = 1
DEV_DMA        = 2
DEV_HIST_LUMA  = 3
DEV_HIST_RGB   = 4
DEV_HIST_RGBC  = 5
DEV_HIST_MONO  = 6
DEV_HIST_WAVE  = 7
DEV_FPGA       = 8

# Short name, long name, base address
DEVICE_INFO: Dict[int, Tuple[str, str, int]] = {
    DEV_UART:      ("UART",      "XPS UARTLite",         0xE060_0000),
    DEV_ETHERNET:  ("ETH",       "XPS EthernetLite",     0xE102_0000),
    DEV_DMA:       ("DMA",       "OPB DMA Channel",      0x6401_0000),
    DEV_HIST_LUMA: ("HIST-LUMA", "Luma Histogram",       0xE008_0000),
    DEV_HIST_RGB:  ("HIST-RGB",  "RGB Histogram",        0xE00A_0000),
    DEV_HIST_RGBC: ("HIST-RGBC", "RGB Comp Histogram",   0xE010_0000),
    DEV_HIST_MONO: ("HIST-MONO", "Mono Histogram",       0xE012_0000),
    DEV_HIST_WAVE: ("HIST-WAVE", "Luma Waveform",        0xE020_0000),
    DEV_FPGA:      ("FPGA",      "FPGA Catch-all",       0xE000_0000),
}

# ---------------------------------------------------------------------------
# Register map: guest physical address → (register name, notes)
# ---------------------------------------------------------------------------

REG_MAP: Dict[int, Tuple[str, str]] = {
    # XPS UARTLite (DS570)
    0xE060_0000: ("ULITE_RX_FIFO",  "RX data / status"),
    0xE060_0004: ("ULITE_TX_FIFO",  "TX data byte"),
    0xE060_0008: ("ULITE_STATUS",   "RX valid[0], TX full[3], parity err[4], frame err[5], overrun[6]"),
    0xE060_000C: ("ULITE_CONTROL",  "RST_TX[0] RST_RX[1] EN_INTR[4]"),

    # XPS EthernetLite (DS599) — key registers; buffer area is 0x7F40 bytes
    0xE102_7F40: ("ETHLITE_MDIOADDR",  "MDIO address"),
    0xE102_7F44: ("ETHLITE_MDIOWR",    "MDIO write data"),
    0xE102_7F48: ("ETHLITE_MDIORD",    "MDIO read data"),
    0xE102_7F4C: ("ETHLITE_MDIOCTRL",  "MDIO control"),
    0xE102_7F50: ("ETHLITE_TX0_LEN",   "TX buf-0 frame length"),
    0xE102_7F54: ("ETHLITE_GIE",       "Global interrupt enable"),
    0xE102_7F5C: ("ETHLITE_TX0_CTRL",  "TX buf-0 control: SND[0] PROG[1]"),
    0xE102_7F7C: ("ETHLITE_RX0_CTRL",  "RX buf-0 control: RDY[0] IE[3]"),
    0xE102_FF50: ("ETHLITE_TX1_LEN",   "TX buf-1 frame length"),
    0xE102_FF5C: ("ETHLITE_TX1_CTRL",  "TX buf-1 control"),
    0xE102_FF7C: ("ETHLITE_RX1_CTRL",  "RX buf-1 control"),

    # OPB DMA Channel (dma_v1_10_b)
    0x6401_0000: ("DMA_RST",   "Reset (write 0xA)"),
    0x6401_0004: ("DMA_DMAC",  "DMA Control (reset=0x98000000)"),
    0x6401_0008: ("DMA_SA",    "Source Address"),
    0x6401_000C: ("DMA_DA",    "Destination Address"),
    0x6401_0010: ("DMA_LEN",   "Byte count — write triggers transfer"),
    0x6401_0014: ("DMA_DMAS",  "DMA Status: BUSY[31]"),
    0x6401_0018: ("DMA_BDA",   "Buffer Descriptor Address"),
    0x6401_001C: ("DMA_SWCR",  "SW Control: SG_ENABLE[31]"),
    0x6401_0020: ("DMA_UPC",   "Unserviced Packet Count"),
    0x6401_0024: ("DMA_PCT",   "Packet Count Threshold"),
    0x6401_0028: ("DMA_PWB",   "Packet Wait Bound"),
    0x6401_002C: ("DMA_IS",    "Interrupt Status (W1C)"),
    0x6401_0030: ("DMA_IE",    "Interrupt Enable"),

    # RED Histogram IPs — inferred from firmware disassembly
    0xE008_0034: ("LUMA_HIST_STATUS0", ""),
    0xE008_0038: ("LUMA_HIST_CTRL",    "Enable[5]"),
    0xE008_003C: ("LUMA_HIST_STATUS1", "Done[5]"),
    0xE00A_0034: ("RGB_HIST_STATUS0",  ""),
    0xE00A_0038: ("RGB_HIST_CTRL",     "Enable[5]"),
    0xE00A_003C: ("RGB_HIST_STATUS1",  "Done[5]"),
    0xE010_0034: ("RGBC_HIST_STATUS0", ""),
    0xE010_0038: ("RGBC_HIST_CTRL",    "Enable[5]"),
    0xE010_003C: ("RGBC_HIST_STATUS1", "Done[5]"),
    0xE012_0034: ("MONO_HIST_STATUS0", ""),
    0xE012_0038: ("MONO_HIST_CTRL",    "Enable[5]"),
    0xE012_003C: ("MONO_HIST_STATUS1", "Done[5]"),
    0xE020_0034: ("LUMA_WAVE_STATUS0", ""),
    0xE020_0038: ("LUMA_WAVE_CTRL",    "Enable[5]"),
    0xE020_003C: ("LUMA_WAVE_STATUS1", "Done[5]"),
}


def decode_register(addr: int) -> str:
    """Return 'REGNAME' if address is in the map, or '+0xOFFSET' relative to device base."""
    if addr in REG_MAP:
        return REG_MAP[addr][0]
    # Find closest device base
    for dev_id, (_, _, base) in DEVICE_INFO.items():
        if base <= addr < base + 0x40000:
            return f"+0x{addr - base:04X}"
    return f"0x{addr:08X}"


def decode_register_note(addr: int) -> str:
    """Return field description if available."""
    if addr in REG_MAP:
        return REG_MAP[addr][1]
    return ""
