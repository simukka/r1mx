#!/usr/bin/env python3
"""pci_isp1562_probe.py — validate the QEMU ISP1562 PCI stub at the config level.

Drives the XPci_v3 bridge's CAR/CDR config-cycle ports exactly the way the Build-32
firmware enumerator does (FUN_00000b3c/FUN_000005a4): CAR = enable | bus<<16 |
dev<<11 | fn<<8 | (off & 0xfc), read CDR. Because gdb-stub *debug* writes to MMIO do
NOT reach QEMU device models, this injects a tiny PPC stub into scratch RAM and
single-steps it so a REAL CPU store/load performs each config cycle.

Why this exists: the cold-boot device layer (FUN_00367f54) scans PCI for USB host
controllers (class 0x0C03); finding none leaves the device count (0xE26978) at 0 and
the keystone allocator (0x5652D0) returns -7. The ISP1562 stub (hw/pci-host/
xilinx_opb_pci.c) makes two devices discoverable. See
firmware/reverse/build_32/boot_reconstruction_status.md "ROOT CAUSE LOCALIZED".

Usage:
    ./firmware/scripts/qemu_boot.sh --patched --debug --background
    python3 firmware/scripts/pci_isp1562_probe.py
    ./firmware/scripts/qemu_boot.sh --stop
"""
import struct
import sys
from rsp import RSP

CAR_ADDR = 0xe120010c     # XPci_v3 base 0xe1200000 + 0x10C
CDR_ADDR = 0xe1200110     # + 0x110


def _stub(car_val):
    hi, lo = (car_val >> 16) & 0xffff, car_val & 0xffff
    ins = [
        0x3C60E120,            # lis  r3,0xe120
        0x6063010C,            # ori  r3,r3,0x010c   (CAR addr)
        0x3C800000 | hi,       # lis  r4,hi
        0x60840000 | lo,       # ori  r4,r4,lo       (CAR value)
        0x90830000,            # stw  r4,0(r3)
        0x3CA0E120,            # lis  r5,0xe120
        0x60A50110,            # ori  r5,r5,0x0110   (CDR addr)
        0x80C50000,            # lwz  r6,0(r5)
        0x48000000,            # b .
    ]
    return b"".join(struct.pack(">I", w) for w in ins)


def main():
    t = RSP("127.0.0.1", 1234, allow_write=True)
    t.connect()
    scratch = [0x02000000]

    def cfg(bus, dev, fn, off):
        car = 0x80000000 | (bus << 16) | (dev << 11) | (fn << 8) | (off & 0xfc)
        a = scratch[0]
        scratch[0] += 0x100
        t.write_mem(a, _stub(car))
        t.write_reg('pc', a)
        for _ in range(8):       # execute through the lwz r6
            t.step(timeout=5)
        return t.regs().get('r6')

    tests = [
        ("bridge  d0 off0x00 vid/did", 0, 0, 0, 0x00, 0x000710EE),
        ("ISP-A   d1 off0x00 vid/did", 0, 1, 0, 0x00, 0x156204CC),
        ("ISP-A   d1 off0x08 class",   0, 1, 0, 0x08, 0x0C03A001),
        ("ISP-A   d1 off0x0c hdrtype", 0, 1, 0, 0x0c, 0x00000000),
        ("ISP-B   d2 off0x00 vid/did", 0, 2, 0, 0x00, 0x156204CC),
        ("ISP-B   d2 off0x08 class",   0, 2, 0, 0x08, 0x0C032001),
        ("ISP-B   d2 off0x10 BAR0",    0, 2, 0, 0x10, 0xA0000000),
        ("empty   d3 off0x00",         0, 3, 0, 0x00, 0xFFFFFFFF),
        ("empty   d1 fn1 off0x00",     0, 1, 1, 0x00, 0xFFFFFFFF),
    ]
    ok = True
    for name, b, d, f, o, exp in tests:
        g = cfg(b, d, f, o)
        flag = "OK " if g == exp else "FAIL"
        ok &= (g == exp)
        print(f"  [{flag}] {name}: {hex(g) if g is not None else None} exp {exp:#010x}")
    t.close()
    print("ALL CONFIG-DISCOVERY TESTS PASS" if ok else "SOME FAILED")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
