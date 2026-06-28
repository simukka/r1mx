---
title: "Wiring Up the Live Camera"
summary: "The emulator is stuck. But there's a real camera on a JTAG cable, running real firmware in real time. Getting a host machine to listen — carefully, read-only, without wrecking anything."
tags: [jtag, hardware, xmd]
---

Consider the rental house version of this story.

Somewhere in a city near you, there is a camera rental operation run by one or two people who bought their equipment when it was the professional standard and are now watching the replacement cycle lap them while they try to keep good gear in rentable condition. The RED ONE MX on their shelf still delivers images that clients pay for. The firmware is frozen at Build 32 because that's the last build RED shipped, and "last" is a word that arrived without a press release or an explanation.

The rental house tech doesn't have source code. They don't have documentation beyond what the community has assembled. They have the camera and they have experience, and when something breaks in a way they haven't seen before, they are working with a black box that the manufacturer has no incentive to help them open.

We have a black box too. We also have a JTAG cable.

---

## The Setup

The Xilinx Virtex-4 FX100 FPGA in the RED ONE MX exposes a JTAG chain with two TAPs: the FX100 itself and a XC2C256 CPLD. The PPC405 core is inside the FX100. Xilinx Microprocessor Debugger (XMD) connects to the CPU over that chain, attaches to the PPC405, and exposes a GDB remote stub on TCP port 1234.

XMD runs inside a Windows XP virtual machine (`r1mx_32`). VirtualBox handles the VM. Getting from the host machine to the camera's PPC405 core takes one VBoxManage command:

```bash
# Forward VM's XMD stub to host port 2345
VBoxManage controlvm r1mx_32 natpf1 "xmdgdb,tcp,127.0.0.1,2345,,1234"
```

After that, [`rsp.py`](https://github.com/simukka/r1mx/blob/master/firmware/scripts/rsp.py) — the shared RSP client — can talk to the camera's CPU the same way it talks to QEMU:

```bash
# Read the current program counter from the live camera
python3 - <<'EOF'
import sys; sys.path.insert(0, 'firmware/scripts')
from rsp import RSPClient
r = RSPClient('127.0.0.1', 2345)
regs = r.read_registers()
# XMD exposes 146 register words; pc is at word 96 (after 32 GPR + 64 FPR)
pc = int.from_bytes(regs[96*4:(96+1)*4], 'big')
print(f'PC = {pc:#010x}')
EOF
```

The full bridge setup — including the Channel B file-queue fallback for XMD-only commands — is documented in [`host_xmd_bridge.md`](https://github.com/simukka/r1mx/blob/master/firmware/reverse/build_32/host_xmd_bridge.md).

---

## The Register Bug

The first attempt at reading the program counter returned zero. Garbage. Clearly wrong.

The RSP protocol's register block has a fixed layout: GPRs 0–31, then special registers. QEMU exposes 38 registers total. XMD exposes 146 — it includes 64 floating-point slots that QEMU doesn't have. The register offsets are completely different:

| Register | QEMU word | XMD word |
|----------|-----------|----------|
| GPR 0–31 | 0–31 | 0–31 |
| PC | 32 | 96 |
| MSR | 33 | 97 |
| CR | 34 | 98 |
| LR | 35 | 99 |

The old code was reading word 32 — QEMU's PC location — which maps to an FP slot in XMD. FP registers on an idle camera are zero. Hence: zero.

Fix the offsets. Read word 96. The PC comes back as `0x5BB0DC`. Disassemble that in the firmware image:

```bash
# file offset = live VA - relocation (0x10040 for bench unit)
python3 - <<'EOF'
import subprocess
live_pc = 0x5BB0DC
reloc   = 0x10040        # bench unit relocation
file_off = live_pc - reloc
cmd = [
    'powerpc-linux-gnu-objdump',
    '-D', '-b', 'binary', '-m', 'powerpc:403', '-EB',
    f'--start-address={file_off:#x}',
    f'--stop-address={file_off + 0x10:#x}',
    f'--adjust-vma={reloc:#x}',
    'firmware/reverse/build_32/extracted/software.bin'
]
print(subprocess.check_output(cmd).decode())
EOF
```

The output is a tight infinite loop — exactly where VxWorks idles when there's nothing to do. The camera is alive, quietly spinning, waiting for work.

---

## What XMD Can and Cannot Read

The PPC405 has a full software MMU. Memory access over JTAG depends on which TLB entries are currently resident. At idle, in the WIND idle task:

- **GPRs and PC**: readable, reliable
- **`.text` (code pages)**: I-side only at idle — `mrd` returns `0x00000000`, not errors. The instruction cache has the code; the data TLB doesn't
- **Peripheral registers** (`0xE0xxxxxx`, `0x64xxxxxx`): bus-residue filler — unreadable without halting inside a driver that has those pages mapped
- **NOR flash** (`0xF0000000`): EBC/FPGA gated, not TLB — invisible at idle regardless of MMU state

The address-space gating quirk: launching XMD with a `system.xml` project file restricts JTAG access to seven PLB windows. Without it, you get full 4 GB. Always launch XMD from a neutral directory:

```bash
# Inside the WinXP VM — standalone XMD, no project file
cd C:\temp
xmd
# > connect ppc hw
# Connected to PowerPC PPC405 target.
```

And `rst` does not cold-boot the camera. It resets only the PPC405 core — the FPGA and peripherals are left in running state. The camera hangs at the machine check handler (`0x700`). True cold boot requires a physical power cycle.

---

## Lockstep Diffing

With both QEMU and the live camera reachable on TCP, [`lockstep_diff.py`](https://github.com/simukka/r1mx/blob/master/firmware/scripts/lockstep_diff.py) can step both CPUs instruction-by-instruction and report the first divergence:

```bash
# Terminal 1: boot QEMU with debug stub on port 1234
firmware/scripts/qemu_boot.sh --debug

# Terminal 2: diff HW (port 2345) vs QEMU (port 1234)
python3 firmware/scripts/lockstep_diff.py \
  --hw-port 2345 \
  --qemu-port 1234 \
  --bp 0x36c350 \
  --steps 500 \
  --watch 0xe0600000:16
```

Each line of output is either `OK` (registers match) or a divergence report showing which register differs and the disassembled instruction that caused it. Divergences point directly at unmodeled peripherals.

---

## The Recording Incident

The camera is not a test fixture. It belongs to a person. It has a job.

One session, a hardware breakpoint was left armed while the camera was recording. JTAG halt freezes the PPC405 for however long it takes to read registers and resume. Long enough — tens of milliseconds — for the audio pipeline to miss its real-time interrupt. The driver logged an underrun error. The recording stopped.

The operator lost a take.

After that: no halts during active recording. Set breakpoints only when the camera is idle or in a setup phase. The full read-only discipline is in [`host_xmd_bridge.md`](https://github.com/simukka/r1mx/blob/master/firmware/reverse/build_32/host_xmd_bridge.md) under "READ-ONLY rules."

This is what working with a tool that belongs to the world actually means. The debugging session is not the only thing happening. The camera is still a camera. The filmmaker is still trying to make something.
