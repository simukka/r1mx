---
title: "Reading a Running System"
summary: "Enumerate the tasks. Decode the relocation. Find where the firmware actually lives in memory. All from the outside, through a JTAG cable, without touching a byte."
tags: [jtag, vxworks, relocation]
---

The thing nobody tells you about a "discontinued" camera is that the camera doesn't know it's discontinued. It boots. It initializes. It runs fifteen tasks in a perfectly choreographed sequence and then idles at the ready, waiting for someone to press record.

The abandonment is entirely on the institutional side. It exists in support contracts, in parts matrices, in which engineers still have the domain knowledge in their heads and whether the company has any incentive to retain them. The camera is indifferent to all of it. The silicon just runs code.

So: if the camera still runs code, can we read what it's running? Not modify — read. From the outside. Without access to documentation that was never public, without ELF headers that were stripped before the binary ever shipped, without asking RED for anything they have no incentive to give.

Yes. With enough patience, a JTAG cable, and a systematic approach to observing a system that wasn't designed to be observed.

---

## Finding the Relocation

The firmware binary is linked for a base address of `0x10000`. Where a given camera actually loads it depends on the bootloader — and it varies per unit. The bench unit uses `D_text = 0x10040`. The working camera (`cam-working-01`) uses `D_text = 0x10180`. Same bytes, different runtime offsets.

Finding the offset without ELF headers:

1. Read a known return address from a kernel stack frame or TCB field (live VA, readable over JTAG)
2. Subtract candidate offsets until the result lands on a `bl` instruction (PowerPC call opcode, `0x4B..` or `0x48..`) in the binary file
3. Verify against multiple data points

[`reloc_verify.py`](https://github.com/simukka/r1mx/blob/master/firmware/scripts/reloc_verify.py) does this systematically — it reads eleven post-call return addresses from readable memory and checks each against the candidate offset:

```bash
# Verify a candidate relocation against live camera (port 2345)
python3 firmware/scripts/reloc_verify.py \
  --port 2345 \
  --reloc 0x10180 \
  --image firmware/reverse/build_32/extracted/software.bin
# Correct: 11/11 post-call addresses verified
# Wrong:    0/11 (0x10040, 0x10000, 0x0 all fail immediately)
```

---

## Walking the Task List

VxWorks maintains a doubly-linked list of active TCBs (Task Control Blocks). The head pointer is a global at `0x010D0584` on this build. Walk the list, subtract `0x50` from each node address to get the TCB base, and read the fields:

```bash
# Enumerate all running tasks (Channel B, read-only)
python3 firmware/scripts/task_walker.py \
  --port 2345 \
  --reloc 0x10180 \
  --image firmware/reverse/build_32/extracted/software.bin
```

The empirically derived [`task_walker.py`](https://github.com/simukka/r1mx/blob/master/firmware/scripts/task_walker.py) knows the WIND_TCB layout for this build:

| Offset | Field |
|--------|-------|
| `+0x08` | Signature: `0x00810600` |
| `+0x40` | Name pointer |
| `+0x48` | Priority |
| `+0x50` | Active-list node (next/prev) |
| `+0xC0` | Entry point (static — task type, not live PC) |

On a healthy camera, roughly fifteen tasks enumerate: `tTffsPTask` (flash filesystem), `tUiIpServer` (remote access over TCP), the network stack, the RED application thread, and others. The `+0xC0` field gives task identity — what function the task was created to run — but not where it's currently executing. Live program counter lives in the context-switch save area, at a location that varies by VxWorks internal state.

---

## The Embedded Symbol Table

Every exported function and global variable has an entry in a symbol table embedded directly in `software.bin`. The format: 16-byte entries, `{flags, pad, namePtr, value, pad, type}`. Finding a function's runtime address from its name:

```bash
python3 - <<'EOF'
import struct
from pathlib import Path

image = Path('firmware/reverse/build_32/extracted/software.bin').read_bytes()
name  = b'XIic_MasterSend\x00'
reloc = 0x10000   # file base

# 1. Find the name string in the image
name_off = image.find(name)
name_va  = name_off + reloc

# 2. Find a 4-byte big-endian pointer to that VA
ptr = struct.pack('>I', name_va)
ptr_off = image.find(ptr)
if ptr_off == -1:
    print('not found'); raise SystemExit

# 3. The symbol entry starts 4 bytes before the namePtr field (+4 in the struct)
sym_off  = ptr_off - 4      # points to flags word; namePtr is at +4
value_va = struct.unpack_from('>I', image, sym_off + 8)[0]
print(f'{name.rstrip(b chr(0)).decode()}: {value_va:#010x}')
# XIic_MasterSend: 0x00251ec0  (+ reloc offset for your unit)
EOF
```

This resolves any C symbol to its absolute code address. C++ instance methods mostly don't get symbol entries — only vtable entries, functor thunks, and constructors do. But it's enough to anchor the major driver paths.

---

## Remote Access Transports

Two network transports ride the XEmacLite Ethernet MAC (`0xe1020000`):

**WDB agent** — UDP 17185, unauthenticated, always running. Wind River's debug agent. [`wdb_probe.py`](https://github.com/simukka/r1mx/blob/master/firmware/scripts/wdb_probe.py) can read memory and registers, set breakpoints, and invoke functions at arbitrary addresses. No authentication. Designed for a development LAN. Present on every production camera ever shipped.

```bash
# Check if WDB agent is reachable (camera Ethernet required)
python3 firmware/scripts/wdb_probe.py --host 192.168.0.2 --ping
```

**GPDB/Connection** — TCP, password-authenticated. `GET_FILE` and `ReadAnyFile` read any TFFS path through the running flash filesystem driver. This matters because the NOR flash at `0xF0000000` is bus-gated at idle and unreadable through JTAG — but the TFFS driver knows how to reach it, and GPDB can ask the driver.

USB Type-B is CDC-ACM serial only. No USB-Ethernet gadget. All network access goes through the physical Ethernet port.

---

## The Harvest

After all of this — relocation decoded, task list walked, symbol table indexed, remote transports confirmed — a single session captures the live values of the key dispatch and allocation pointers that the emulator needs to seed correctly:

```bash
python3 firmware/scripts/harvest_slots.py \
  --port 2345 \
  --reloc 0x10180 \
  --image firmware/reverse/build_32/extracted/software.bin \
  --out firmware/reverse/build_32/camera_reports/cam-working-01/harvest_$(date +%Y%m%dT%H%M%S).json
```

The output from [`harvest_20260614T160424.md`](https://github.com/simukka/r1mx/blob/master/firmware/reverse/build_32/camera_reports/cam-working-01/harvest_20260614T160424.md):

```
slot             label            live        qemu_seed
0x00e293f4  dispatch_fnptr    0x00e293f0  0x00e293f0
0x00e3a790  dispatch_selector 0x00e3a78c  0x00e3a78c
0x00e295c4  allocator_obj     0x00e295c0  0x00e295c0
0x00e9c34c  alloc_fnptr       0x00e9c348  0x00e9c348
0x00e9c648  free_fnptr        0x00e9c644  0x00e9c644
0x00e26978  dev_count         0x00e26974  0x00e26974
0x00e3a624  dev_table         0x00e3a620  0x00e3a620
0x00e3a630  dev_ctx_count     0x00e3a62c  0x00e3a62c
```

These are the live values — what the addresses actually hold when the camera is running. Cross-referencing them against the static binary is how the gap between "binary we have" and "binary we understand" closes. One address at a time, from a camera that still doesn't know it's been abandoned.
