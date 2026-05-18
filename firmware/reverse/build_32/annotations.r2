# radare2 annotation script for Build 32 firmware
# Generated from ISE EDK 10.1 xparameters.h, xreg405.h, and firmware analysis
#
# Usage (load firmware at correct base):
#   r2 -a ppc -b 32 -e cfg.bigendian=true -m 0x0 software.patched.r1mx.bin
#   . annotations.r2
#
# Or from within r2:
#   . firmware/reverse/build_32/annotations.r2

# ---------- MMIO Peripheral Bases (from xparameters.h, CONFIRMED) ----------

f XPAR_UARTLITE_0_BASEADDR     = 0xE0600000
f XPAR_UARTLITE_TX_FIFO        = 0xE0600004
f XPAR_UARTLITE_STATUS         = 0xE0600008
f XPAR_UARTLITE_CONTROL        = 0xE060000C

f XPAR_UARTNS550_0_BASEADDR    = 0xE0640000
f XPAR_UARTNS550_0_THR         = 0xE0641003
f XPAR_UARTNS550_0_LSR         = 0xE0641017
f XPAR_UARTNS550_1_BASEADDR    = 0xE0650000
f XPAR_UARTNS550_1_THR         = 0xE0651003

f XPAR_INTC_0_BASEADDR         = 0xE0800000
f XPAR_INTC_0_ISR              = 0xE0800000
f XPAR_INTC_0_IPR              = 0xE0800004
f XPAR_INTC_0_IER              = 0xE0800008
f XPAR_INTC_0_IAR              = 0xE080000C
f XPAR_INTC_0_SIE              = 0xE0800010
f XPAR_INTC_0_CIE              = 0xE0800014
f XPAR_INTC_0_IVR              = 0xE0800018
f XPAR_INTC_0_MER              = 0xE080001C

f XPAR_IIC_0_BASEADDR          = 0xB2600000
f XPAR_IIC_0_CR                = 0xB2600103
f XPAR_IIC_0_SR                = 0xB2600107
f XPAR_IIC_0_DTR               = 0xB260010B
f XPAR_IIC_0_DRR               = 0xB260010F

f XPAR_EMACLITE_0_BASEADDR     = 0xE1020000
f XPAR_EMACLITE_0_TXBUF        = 0xE1020000
f XPAR_EMACLITE_0_TSR          = 0xE10207FC
f XPAR_EMACLITE_0_RXBUF        = 0xE1021000
f XPAR_EMACLITE_0_RSR          = 0xE10217FC

f XPAR_DMACHANNEL_0_BASEADDR   = 0x64010000

# ---------- Confirmed Function Names (Boot & Init) ----------

af+ 0x00000000 fn_reset_vector
afn 0x00000000 romInit
af+ 0x00000124 fn_halt
afn 0x00000124 halt_loop

af+ 0x0000D8A0 fn_d8a0
afn 0x0000D8A0 timer_clock_helper
af+ 0x0000DCB0 fn_dcb0
afn 0x0000DCB0 sysHwInit_seq
af+ 0x0000DDB8 fn_ddb8
afn 0x0000DDB8 rootTask_wrapper
af+ 0x0000E898 fn_e898
afn 0x0000E898 XIo_In32
af+ 0x0000E904 fn_e904
afn 0x0000E904 XIo_Out32

af+ 0x00012D90 fn_12d90
afn 0x00012D90 mmio_dispatch_table

af+ 0x001C18DC fn_1c18dc
afn 0x001C18DC sysSerialInit
af+ 0x001C1A0C fn_1c1a0c
afn 0x001C1A0C sysSerialInit_uartlite_first_access

af+ 0x0036860C fn_36860c
afn 0x0036860C usrInit_conditional_task_spawner
af+ 0x0036B3DC fn_36b3dc
afn 0x0036B3DC usrWdbInit
af+ 0x0036B7EC fn_36b7ec
afn 0x0036B7EC bsp_init_caller
af+ 0x0036C350 fn_36c350
afn 0x0036C350 usrInit
af+ 0x0036E168 fn_36e168
afn 0x0036E168 vxworks_exc_handler_installer

af+ 0x00371EC8 fn_371ec8
afn 0x00371EC8 mfmsr_wrapper
af+ 0x00371ED0 fn_371ed0
afn 0x00371ED0 mtmsr_wrapper
af+ 0x00371F30 fn_371f30
afn 0x00371F30 sysPvrGet_candidate

af+ 0x0037C440 fn_37c440
afn 0x0037C440 rootTask
af+ 0x0037CC94 fn_37cc94
afn 0x0037CC94 fn_37cc94
af+ 0x0037CD4C fn_37cd4c
afn 0x0037CD4C dispatch_entry_0_epilogue
af+ 0x0037CE78 fn_37ce78
afn 0x0037CE78 dispatch_entry_1

af+ 0x00458A14 fn_458a14
afn 0x00458A14 driver_dispatch_PATCHED
af+ 0x00496698 fn_496698
afn 0x00496698 memset_bss

af+ 0x004A5F00 fn_4a5f00
afn 0x004A5F00 fn_4a5f00_crash_site
af+ 0x004A6438 fn_4a6438
afn 0x004A6438 core_lib_fn_4a6438
af+ 0x00548D78 fn_548d78
afn 0x00548D78 driver_init_stub

af+ 0x005A7F30 fn_5a7f30
afn 0x005A7F30 kernelInit
af+ 0x005AB0DC fn_5ab0dc
afn 0x005AB0DC windWorker_workQ_spin

# ---------- BSS Key Addresses ----------

f bss_start        = 0x00E9BF20
f bss_end          = 0x01153480
f wdb_port_var     = 0x00E9C4BC
f canary_a         = 0x00E269A4
f canary_b         = 0x00E269A0
f workQ_flag       = 0x010D0584

# ---------- WDB Agent ----------

af+ 0x005A153C fn_5a153c
afn 0x005A153C wdbEndPktDevInit
af+ 0x005A2A28 fn_5a2a28
afn 0x005A2A28 wdb_task_spawn

# ---------- XIo register access helpers (for comments in disasm) ----------
# When you see: bl 0xe898 with r3=addr, annotate as XIo_In32(addr)
# When you see: bl 0xe904 with r3=addr,r4=val, annotate as XIo_Out32(addr,val)
#
# Register offset quick-ref (add to MMIO base):
#   UartLite:  +0=RX, +4=TX, +8=Status, +12=Control
#   INTC:      +0=ISR, +4=IPR, +8=IER, +12=IAR, +16=SIE, +20=CIE, +24=IVR, +28=MER
#   IIC:       base+0x103=CR, +0x107=SR, +0x10B=TX, +0x10F=RX
#   NS550:     base+0x1003=THR/RBR, +0x1007=IER, +0x1017=LSR

echo "Annotations loaded: MMIO flags + function names from ISE 10.x xparameters.h + firmware analysis"
