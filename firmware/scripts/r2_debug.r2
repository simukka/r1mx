# r2_debug.r2 — radare2 session script for live QEMU debug of Build 32
#
# Usage (in a second terminal after starting qemu_boot.sh --debug):
#   r2 -a ppc -b 32 -e cfg.bigendian=true \
#      -D gdb gdb://localhost:1234 \
#      -i scripts/r2_debug.r2
#
# The script sets up the analysis context, applies known labels for Build 32,
# adds breakpoints at key VxWorks boot milestones, and prints current state.
#
# Build 32 v32.0.3 — key addresses:
#   usrInit (main boot init):   0x0036C350
#   WDB agent init:             0x0036B3DC
#   UART Lite init:             0x001C18DC
#   BSS start:                  0x00E9BF20
#   BSS end:                    0x01153480
#
# For Build 13 legacy debug: load scripts/r2_debug_build13.r2 instead.

# -----------------------------------------------------------------------
# Architecture / endianness
# -----------------------------------------------------------------------
e asm.arch=ppc
e asm.bits=32
e cfg.bigendian=true
e dbg.bep=entry

# -----------------------------------------------------------------------
# Known labels — Build 32 v32.0.3 (from static analysis of software.bin)
# -----------------------------------------------------------------------

# Exception vector table (at physical 0x0 — EVPR=0 at boot)
f sym.reset_vector        @ 0x00000000
f sym.machine_check_vec   @ 0x00000200
f sym.dsi_vec             @ 0x00000300
f sym.isi_vec             @ 0x00000400
f sym.ext_interrupt_vec   @ 0x00000500
f sym.alignment_vec       @ 0x00000600
f sym.program_check_vec   @ 0x00000700
f sym.fp_unavail_vec      @ 0x00000800
f sym.decrementer_vec     @ 0x00000900
f sym.sys_call_vec        @ 0x00000C00
f sym.trace_vec           @ 0x00000D00
f sym.halt_loop           @ 0x00000124

# Early boot
f sym.romInit_temp_stack  @ 0x0000FFF0
f sym.romInit_sp_patch    @ 0x00000084

# Hardware init
f sym.sysHwInit_seq       @ 0x0000DCB0
f sym.sysClkHelper        @ 0x0000D8A0
f sym.mmio_dispatch       @ 0x00012D90

# UART / Serial
f sym.sysSerialInit       @ 0x001C18DC
f sym.uart_first_mmio     @ 0x001C1A0C

# Main boot init (equivalent of usrInit/usrConfig)
f sym.usrInit             @ 0x0036C350
f sym.canary_wait_loop    @ 0x0036C380
f sym.canary_patch_1      @ 0x0036C388
f sym.canary_patch_2      @ 0x0036C394
f sym.bss_zero_init       @ 0x0036C398

# WDB agent
f sym.usrWdbInit          @ 0x0036B3DC
f sym.bsp_init_caller     @ 0x0036B7EC
f sym.wdbEndPktDevInit    @ 0x005A153C
f sym.wdb_task_spawn      @ 0x005A2A28
f sym.memset_bss          @ 0x00496698

# BSS boundaries (runtime — not in file)
f sym.bss_start           @ 0x00E9BF20
f sym.bss_end             @ 0x01153480
f sym.wdb_port_bss        @ 0x00E9C4BC
f sym.canary_addr_1       @ 0x00E269A4
f sym.canary_addr_2       @ 0x00E269A0

# Key data addresses
f sym.boot_config_str     @ 0x00D5C608
f sym.ssd_whitelist       @ 0x00D2E3E8
f sym.debug_usb_param     @ 0x00D35928
f sym.altshell_path       @ 0x00D30044
f sym.upgrade_path_tffs   @ 0x00D3632F
f sym.uiusbserial_vtable  @ 0x00DCB3BC
f sym.uartlite_cfgtable   @ 0x00DF7930
f sym.uartns550_cfgtable  @ 0x00DF7B3C

# -----------------------------------------------------------------------
# Breakpoints — key Build 32 boot milestones
# -----------------------------------------------------------------------

# Break at main boot init entry — confirms load address is correct
db 0x0036C350

# Break at UART init — boot messages will start appearing after this
db 0x001C18DC

# Break at WDB init — WDB agent is about to start
db 0x0036B3DC

# -----------------------------------------------------------------------
# Print current state and instructions
# -----------------------------------------------------------------------
dr
pd 8

# -----------------------------------------------------------------------
# Interactive workflow
# -----------------------------------------------------------------------
# dc           — continue to next breakpoint
# ds           — single step one instruction
# dr           — show all registers
# dr pc        — read PC
# dr r1        — read stack pointer
# pdf @ <sym>  — disassemble labelled function
# pd 4         — disassemble 4 instructions at PC
# db <addr>    — add breakpoint
# dbc <addr>   — clear breakpoint
# dbs          — list breakpoints
#
# After canary patches, boot should reach sym.sysSerialInit.
# If QEMU crashes before that (machine check), read PC with:
#   dr pc
# Then in a second terminal:
#   python3 scripts/patch_firmware.py --probe 0x$(r2 ... | grep PC | awk '{print $2}')
# Add the generated Patch() entry to BUILD32_PATCHES in patch_firmware.py.
#
# Build 32 vs Build 13 differences:
#   usrInit:     0x0036C350  (was 0x002ED020 in Build 13)
#   BSS start:   0x00E9BF20  (was 0x00C118D0 in Build 13)
#   BSS end:     0x01153480  (was 0x00D441B0 in Build 13)
#   Canary loop: 0x0036C380  (was 0x002ED050 in Build 13)
