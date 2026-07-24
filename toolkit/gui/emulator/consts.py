from typing import Deque, Dict, List, Optional, Tuple

BROKER_HOST = "127.0.0.1"
BROKER_PORT = 17187
PACKET_SIZE = 32
PACKET_MAGIC = b"RDEV"

# ---------------------------------------------------------------------------
# Device IDs: indices into r1mx_activity.h.  The qemu-r1mx activity broker
# sends one of these as the dev_id byte in every RDEV packet.  The integer
# values MUST stay in sync with include/hw/ppc/r1mx_activity.h in the fork.
#
# IDs 3-7 were originally labelled RED "histogram" IP blocks.  The firmware
# device table (software.bin @0xe0be10) shows those five FPGA blocks were
# misattributed; their real identities are vpfpga / sdio / audio / dma / frmbuf.
# Only the names are corrected (here and in the header); the integer values are
# unchanged.  See firmware/reverse/build_32/qemu_frmbuf_dma.md.
# ---------------------------------------------------------------------------
DEV_UART       = 0    # XPS UARTLite            0xE060_0000
DEV_ETHERNET   = 1    # XPS EthernetLite        0xE102_0000
DEV_DMA        = 2    # OPB / XPS Central DMA   0x6401_0000
DEV_VPFPGA     = 3    # VP-FPGA comm FIFO       0xE008_0000  (was "Luma Histogram")
DEV_SDIO       = 4    # SD / SDIO block         0xE00A_0000  (was "RGB Histogram")
DEV_AUDIO      = 5    # Audio block             0xE010_0000  (was "RGB Comp Histo")
DEV_IODMA      = 6    # IOFPGA DMA block        0xE012_0000  (was "Mono Histogram")
DEV_FRMBUF     = 7    # Frame buffer block      0xE020_0000  (was "Luma Waveform")
DEV_FPGA       = 8    # IOFPGA fabric/catch-all 0xE000_0000-0xE3FF_FFFF
DEV_CPU        = 9    # PPC405F6 CPU sampler    (addr = current PC)
DEV_RAM        = 10   # System SDRAM            0x0000_0000
DEV_ROM        = 11   # NOR flash + boot ROM    0xF000_0000 / 0xFFFF_0000
DEV_SDCARD     = 12   # Block backend slot 0    (CF / SD)
DEV_SSD        = 13   # Block backend slot 1    (SiI3512 SATA SSD)

# Short name, long name, base address (0xFFFF_FFFF base = no single MMIO base).
DEVICE_INFO: Dict[int, Tuple[str, str, int]] = {
    DEV_UART:     ("UART",   "XPS UARTLite",              0xE060_0000),
    DEV_ETHERNET: ("ETH",    "XPS EthernetLite",          0xE102_0000),
    DEV_DMA:      ("DMA",    "OPB / XPS Central DMA",     0x6401_0000),
    DEV_VPFPGA:   ("VPFPGA", "VP-FPGA comm FIFO",         0xE008_0000),
    DEV_SDIO:     ("SDIO",   "SD / SDIO block",           0xE00A_0000),
    DEV_AUDIO:    ("AUDIO",  "Audio block",               0xE010_0000),
    DEV_IODMA:    ("IO-DMA", "IOFPGA DMA block",          0xE012_0000),
    DEV_FRMBUF:   ("FRMBUF", "Frame buffer block",        0xE020_0000),
    DEV_FPGA:     ("IOFPGA", "IOFPGA fabric / catch-all", 0xE000_0000),
    DEV_CPU:      ("CPU",    "PPC405F6 CPU sampler",      0xFFFF_FFFF),
    DEV_RAM:      ("RAM",    "System SDRAM",              0x0000_0000),
    DEV_ROM:      ("ROM",    "NOR flash + boot ROM",      0xF000_0000),
    DEV_SDCARD:   ("SDCARD", "Block slot 0 (CF / SD)",    0xFFFF_FFFF),
    DEV_SSD:      ("SSD",    "Block slot 1 (SATA SSD)",   0xFFFF_FFFF),
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

    # --- Corrected FPGA-block registers (firmware device table @0xe0be10) --
    # VP-FPGA comm block (0xe0080000, was mislabelled "Luma Histogram").  The
    # VPFPGA driver-init routine (fn @0x374ba4) drains a command/response FIFO
    # and polls +0x18 bit10 for "FIFO drained / ready"; modelled in qemu-r1mx
    # hw/misc/red_histogram_ip.c for the 0xe0080000 instance.
    0xE008_0010: ("VPFPGA_FIFO_D0",   "VP-FPGA response FIFO data word 0"),
    0xE008_0014: ("VPFPGA_FIFO_D1",   "VP-FPGA response FIFO data word 1"),
    0xE008_0018: ("VPFPGA_FIFO_STAT", "FIFO drained / ready[10]"),

    # IOFPGA status/control (0xe2000000, inside the FPGA catch-all range).
    # Video-pipeline bringup polls these; values modelled in r1mx_virtex4.c.
    0xE200_00F8: ("IOFPGA_RIO_STAT",   "RocketIO/MGT channel up[0]"),
    0xE200_0224: ("IOFPGA_GPIO_BB",    "Serial bit-bang GPIO: clk[0] data[2] -> display/DAC"),
    0xE200_028C: ("IOFPGA_VPCFG_STAT", "VP-FPGA config: DONE[8]"),

    # XPS IIC (I2C controller) at 0xb2600000.  Drives the 3 PCA9698 I2C GPIO
    # expanders (status LCD / board I/O) and the HDMI / HD-SDI / audio codecs.
    0xB260_001C: ("IIC_GIE",     "Global interrupt enable[31]"),
    0xB260_0020: ("IIC_ISR",     "Interrupt status"),
    0xB260_0028: ("IIC_IER",     "Interrupt enable"),
    0xB260_0040: ("IIC_SOFTR",   "Software reset (write 0xA)"),
    0xB260_0100: ("IIC_CR",      "Control: EN[0] MSMS[1] TXRX[2] TXAK[3] RSTA[4] TX[5]"),
    0xB260_0104: ("IIC_SR",      "Status: TXFIFO_empty[2] AAS[5] BB[6]"),
    0xB260_0108: ("IIC_TX_FIFO", "TX byte"),
    0xB260_010C: ("IIC_RX_FIFO", "RX byte"),
    0xB260_0110: ("IIC_ADR",     "Slave address (7-bit in 7:1)"),
    0xB260_0124: ("IIC_GPO",     "General-purpose output (AuxGpio)"),
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
