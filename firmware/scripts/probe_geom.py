#!/usr/bin/env python3
"""probe_geom.py — inspect the free-block / tree geometry right after addToPool
(BEFORE any malloc), to see why the first carve takes the no-split branch and
empties the tree.  Then single-step ONE malloc through FUN_0045a428 to log the
branch + computed sizes.
"""
import struct
from rsp import RSP
from build_allocator import _call, _w32, POOL_BASE, POOL_SIZE, PART_ADDR, CATCH
from probe_malloc import reach_wall

def u32(t, a): return struct.unpack(">I", t.read_mem(a, 4))[0]

def main():
    t = RSP("127.0.0.1", 1234, allow_write=True, timeout=30.0, label="qemu").connect()
    try:
        sp = reach_wall(t)
        print(f"[*] wall sp=0x{sp:08x} 0x274 intact={u32(t,0x274)==0x7c632b78}")
        # build WITHOUT the verify malloc
        _call(t, sp, 0x004593a8, 0, 0, 0xBB0)
        _w32(t, 0xE295D4, u32(t, 0xE26D3C))
        _w32(t, 0xE295F4, 0)
        pc, lr, r3 = _call(t, sp, 0x0045AA38, PART_ADDR, POOL_BASE, POOL_SIZE)
        _w32(t, 0xE295C4, PART_ADDR)
        print(f"[*] addToPool stop=0x{pc:08x}")
        p = PART_ADDR
        root = u32(t, p+0x40)
        print(f"[*] tree root(+0x40)=0x{root:08x} nodepool(+0x48)=0x{u32(t,p+0x48):08x} "
              f"nodecnt(+0x4c)=0x{u32(t,p+0x4c):08x} granule *0xE26D3C=0x{u32(t,0xE26D3C):08x} "
              f"e295e4=0x{u32(t,0xE295E4):08x} e295d4=0x{u32(t,0xE295D4):08x}")
        if root:
            # tree node layout: [0]=left [1]=right [2]=? [3]=key [4]/+0x10=block ptr +0x14=?
            for off in (0,4,8,0xc,0x10,0x14):
                print(f"    node[+0x{off:02x}]=0x{u32(t,root+off):08x}")
            blk = u32(t, root+0x10)
            print(f"[*] free block @0x{blk:08x}: hdr[0]=0x{u32(t,blk):08x} "
                  f"size[1]=0x{u32(t,blk+4):08x} (size&~1=0x{u32(t,blk+4)&~1:08x}) "
                  f"[2]=0x{u32(t,blk+8):08x} [3]=0x{u32(t,blk+0xc):08x}")
            sz = u32(t, blk+4) & 0xfffffffe
            end = blk + sz
            print(f"[*] block end = 0x{blk:08x}+0x{sz:08x} = 0x{end:08x} "
                  f"(pool end=0x{POOL_BASE+POOL_SIZE:08x})")
            # boundary tag at end
            print(f"[*] end tag @0x{end:08x}: [0]=0x{u32(t,end):08x} [1]=0x{u32(t,end+4):08x}")
    finally:
        t.close()

if __name__ == "__main__":
    main()
