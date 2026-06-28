# Host → XMD live-debug bridge (operator runbook)

Lets the **Linux host** drive the live PPC405 over JTAG directly, instead of
hand-typing XMD commands in the VM and copy/pasting output through the shared
folder. Two independent channels; use A for speed and QEMU lock-step, B as the
no-network fallback and for XMD-only commands.

```
 Linux host (Claude)                 WinXP VM "r1mx_32"            Camera
  RSP scripts + lockstep_diff  --TCP-->  XMD: connect ppc hw  --USB JTAG--> PPC405
        (Channel A, :2345)              GDB stub :1234
  xmd_rpc.py  <--shared folder-->  XMD: source xmd_agent.tcl
        (Channel B, file queue)
```

> Tool note: this assumes **XMD** (ISE/EDK 10.1, `connect ppc hw`). If the VM
> instead has Vivado's **xsdb**, Channel A is identical (it also serves a gdb
> stub) — only the in-VM launch commands change.

---

## READ-ONLY discipline (unchanged from debug_interfaces.md §7)

This broken bench unit is the sandbox; keep the procedure clean for the eventual
working camera. Allowed: `stop`/`con`/`bps`/`stp`/`mrd`/`rrd`, RSP `?/g/m/s/c/D`,
**hardware** breakpoints. **Never**: `rst`/`mwr`/`rwr`/`dow`/program/erase, RSP
software breakpoints (`Z0` patches memory), any RSP write/reset.

- `rsp.py` is read-only unless `allow_write=True`, and `set_bp` defaults to
  **hardware** (`Z1`/IAC) which does not touch memory.
- `xmd_agent.tcl` refuses denylisted commands without running them.

---

## Channel A — GDB-stub over TCP (primary)

### 1. Forward a host port to the VM's stub (runtime, reversible)
QEMU keeps `:1234`; hardware gets host `:2345`.
```bash
VBoxManage controlvm r1mx_32 natpf1 "xmdgdb,tcp,127.0.0.1,2345,,1234"
# undo: VBoxManage controlvm r1mx_32 natpf1 delete xmdgdb
```

### 2. In the VM: start the stub (standalone XMD avoids address-map gating)
```
xmd
xmd% connect ppc hw      ;# prints: GDB server ... at TCP port no 1234
```

### 3. From the host: verify
```bash
# In the VM, confirm the stub is NOT loopback-only:
#   netstat -an | find "1234"   -> want 0.0.0.0:1234  (see Troubleshooting)
python3 firmware/scripts/gdb_halt_inspect.py --port 2345 --samples 1
```
Live PC/regs => Channel A is up. **Every `--port`-aware probe script now works
against hardware**, e.g.:
```bash
python3 firmware/scripts/dump_regs_at_bp.py --port 2345 --addr 0x5bb11c
```

---

## Lock-step vs QEMU (the point of all this)

```bash
# terminal 1
firmware/scripts/qemu_boot.sh --patched --debug          # QEMU gdbstub :1234
# (Channel A already up: HW stub on :2345)

# terminal 2 — step both from usrInit, watch the console UART + ctor ptr
python3 firmware/scripts/lockstep_diff.py \
    --bp 0x36c350 --steps 500 \
    --watch 0xe0600000:16 --watch 0x00e26d28:4
```
Prints the **first** instruction where HW and QEMU registers/memory disagree —
usually an unmodeled or wrong peripheral read in QEMU. Then grab ground truth:
```bash
# HW-only: what does the real device return here?
python3 firmware/scripts/lockstep_diff.py --mmio-capture --watch 0xe0600000:16
```
Feed that into the QEMU device model (`hw/ppc/r1mx_virtex4.c` et al.), per
`plans/qemu_xilinx_drivers.md`. Prime targets: Phase-5 external timer tick, the
device-ready poll at `[base+0x80]` (bits 15 & 17) behind the boot loop
(`test-unit-bootloop-cause`).

---

## Channel B — file-queue (no network; XMD-only commands)

For SPRs, gated `mrd`, JTAG, or if Channel A networking can't be made to work.

In the VM (after `connect ppc hw`):
```
xmd% source {Y:/r1mx/firmware/scripts/xmd_agent.tcl}
xmd% agent_loop            ;# blocks, polling the shared folder
```
From the host:
```bash
python3 firmware/scripts/xmd_rpc.py "rrd"
python3 firmware/scripts/xmd_rpc.py --parse-mrd "mrd 0xe0600000 4"
python3 firmware/scripts/xmd_rpc.py "rst"     # -> ERROR: refused (read-only)
```
Scratch dir: `firmware/scratch/xmd_bridge/` (= `Y:\r1mx\firmware\scratch\xmd_bridge\`).

---

## Troubleshooting

- **Channel A connects but times out / refused:** the XMD stub may bind
  `127.0.0.1:1234` only, so NAT pf to the guest IP can't reach it. Options, in
  order: (a) run a relay inside the VM (`0.0.0.0:2345 -> 127.0.0.1:1234`) if a
  relay/Python is available; (b) fall back to **Channel B** (needs no network).
- **Register layout (already mapped):** XMD's `g` block is **146 words**, QEMU's
  is **38**. `rsp.py` selects the layout by word count: GPRs `r0..r31` line up in
  both, but on XMD `pc/msr/cr/lr/ctr/xer` sit at words 96–101 (after 32 64-bit
  FPRs) and `pvr` at 103. If a stub reports an **unrecognised** block size,
  `lockstep_diff` flags it — map it with `rsp_discover.py --addr <known-pc>` and
  add the layout to `REG_LAYOUTS` in `rsp.py`.
- **SPRs (`evpr/srr0/dear/esr`) absent:** not in the RSP core set by design —
  use Channel B.
- **Camera reboots mid-session:** the watchdog tripped on a long halt; keep
  lock-step runs bounded and resume (`con`/`D`) promptly.
