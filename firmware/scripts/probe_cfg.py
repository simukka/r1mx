#!/usr/bin/env python3
"""probe_cfg.py — at the natural allocator wall, drive the firmware's own PCI config
primitives to localize why FUN_00367f54's scan finds 0 devices:
  - raw CAR/CDR byte-reverse cycle (FUN_00000118 / FUN_0000010c)
  - FUN_000005a4(bus,dev,fn,off,&buf) config-read wrapper
  - FUN_00000b3c(class, instance, &bus,&dev,&fn) class scanner
Compare against the known-good devices: bus0/dev1 class 0x0C03A0, bus0/dev2 0x0C0320.
"""
import struct
from rsp import RSP
from build_allocator import build, _call

CATCH = 0x0000000C
def u32(t, a): return struct.unpack(">I", t.read_mem(a, 4))[0]
def w32(t, a, v): t.write_mem(a, struct.pack(">I", v & 0xFFFFFFFF))

def cfg_read(t, sp, bus, dev, fn, off):
    """Call FUN_000005a4(bus,dev,fn,off,&scratch) and return the dword read."""
    scratch = 0x08E00000
    w32(t, scratch, 0xDEADBEEF)
    pc, lr, r3 = _call(t, sp, 0x000005A4, bus, dev, fn, off, scratch)
    return pc, u32(t, scratch)

def main():
    t = RSP("127.0.0.1", 1234, allow_write=True, timeout=30.0, label="qemu").connect()
    try:
        t.run_to(0x00371CD0, hw=True, timeout=60.0)
        w32(t, 0xE9C5C0, 0xE9C5C0); w32(t, 0xE9C5C4, 0xE9C5C0)
        t.set_bp(0x00555488, hw=True); t.cont(timeout=20); t.clear_bp(0x00555488, hw=True)
        sp = t.regs()["r1"]
        build(t, sp)
        print(f"[*] wall sp=0x{sp:08x}  gate=*0xE0BDFC=0x{u32(t,0xE0BDFC):08x} "
              f"mech=*0xE0BDF8=0x{u32(t,0xE0BDF8):08x} CAR=0x{u32(t,0xE9C708):08x} "
              f"CDR=0x{u32(t,0xE9C70C):08x} maxbus=0x{u32(t,0xE0BDF4):08x}")

        # 1) raw CAR/CDR byte-reverse cycle for dev0..3 off0 (FUN_00000118/FUN_0000010c)
        print("\n--- raw CAR/CDR byte-reverse (FUN_00000118 write, FUN_0000010c read) ---")
        car = u32(t, 0xE9C708); cdr = u32(t, 0xE9C70C)
        for dev in range(4):
            addr = 0x80000000 | (dev << 11)
            _call(t, sp, 0x00000118, car, addr)          # mWriteReg(CAR, addr)
            pc, lr, r3 = _call(t, sp, 0x0000010C, cdr)    # mReadReg(CDR) -> r3
            print(f"  dev{dev} off0: CAR<-0x{addr:08x}  CDR-> 0x{r3:08x}")

        # 2) FUN_000005a4 wrapper for dev0..3 off0 and off8
        print("\n--- FUN_000005a4 config-read wrapper ---")
        for dev in range(4):
            pc0, v0 = cfg_read(t, sp, 0, dev, 0, 0)
            pc8, v8 = cfg_read(t, sp, 0, dev, 0, 8)
            print(f"  bus0/dev{dev}/fn0: off0=0x{v0:08x} (pc=0x{pc0:x})  "
                  f"off8=0x{v8:08x} class>>8=0x{(v8>>8)&0xffffff:06x} (pc=0x{pc8:x})")

        # 3) FUN_00000b3c class scanner for 0x0C03A0 and 0x0C0320
        print("\n--- FUN_00000b3c class scanner ---")
        for cls in (0x0C03A0, 0x0C0320):
            b, d, f = 0x08E00010, 0x08E00014, 0x08E00018
            for a in (b, d, f): w32(t, a, 0xFFFFFFFF)
            pc, lr, r3 = _call(t, sp, 0x00000B3C, cls, 0, b, d, f)
            print(f"  class 0x{cls:06x}: ret=0x{r3:08x} (0=found) "
                  f"bus={u32(t,b):#x} dev={u32(t,d):#x} fn={u32(t,f):#x} (pc=0x{pc:x})")
    finally:
        t.close()

if __name__ == "__main__":
    main()
