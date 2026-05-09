# R1 Firmware

## Notes 
1. The binary starts with PPC405 machine code (bare metal, not ELF)
2. The DCR registers found include: `SDRAM0_CFGADDR`, `SDRAM0_CFGDATA`, `EBC0_CFGADDR`, `EBC0_CFGDATA`, `CPC0_PLLMR`, `CPC0_CR0`, `CPC0_CR1` — these are PPC405GP/GPr/EP DCRs
3. The BSP is `bsp_ppc405_0_revB` which sounds like it's a Xilinx PPC405 embedded in an FPGA (as in the Xilinx ML300/ML310/ML310e reference designs, or a custom Virtex-II Pro/Virtex-4 with embedded PPC405 hard cores)
4. The xemaclite driver handles Ethernet through a Xilinx Ethernet Lite IP core, and the boot configuration shows it's connecting to a host at 192.168.0.1 with the device at 192.168.0.2
5. Looking at the actual machine code, the first instruction loads zero into r4, which sits in the reset/exception vector area where PPC405 exception handlers live, and I'm tracing through the initial setup instructions to understand the boot sequence.

what looks like SDRAM initialization starting at address 0x00000000. 
Looking at typical Xilinx ML300/ML310 board configurations with PPC405 processors, 
the memory layout suggests SDRAM starting at 0x00000000 with Flash higher up, and 
the VxWorks image is likely loaded around 0x00100000 based on that `lis r1, 0x0001` 
instruction setting up the initial stack pointer.

Now I have a clear picture. The entry function at 0x2ED020 is interesting:
1. It sets up a stack frame with `stwu r1, -0x20(r1)` — classic PPC function prologue
2. Loads magic values 0x12348765 and 0x5a5ac3c3 — these are stack canary markers for VxWorks (known VxWorks patterns for stack checking)
3. It spins waiting for something at memory address 0x00BC3174 to equal 0x12348765 (and 0x00BC3170 to equal 0x5a5ac3c3) — this is the 
VxWorks stack canary fill check!


4. The loop loads from those memory addresses and keeps checking until they match the expected canary values, essentially waiting for the 
stack to be properly initialized before proceeding.
5. Once the canary check passes, it sets up r28 to point to 0x00D441B0 and begins loading additional addresses into r3, likely preparing 
for the next phase of initialization.
6. The code then calculates the difference between these two addresses (about 1.2MB) and calls a function that appears to zero out this 
entire memory region — this is the BSS segment being cleared, which confirms the binary is loaded at address 0x00000000 and this is the 
VxWorks `usrInit()` routine.

Now looking at what comes after the BSS zeroing, I see two function calls at 0x2EF094 and 0x2EEE20 that are likely the next bootstrap 
stages like `usrKernelInit()` and `usrRootInit()`. The BSS segment spans from 0x00C118D0 to 0x00D441B0, placing it near the end of the 
image around 12.3MB, and the stack canary at 0x00BC3174 sits just before it in the initialized data section. This means the system needs at
 least 13MB of memory plus additional space for the stack.

But I'm realizing there's a timing issue here—the initial stack pointer at 0x00010000 is set during romInit and sits within the first 64KB,
 which would collide with the code itself. That's the temporary bootstrap stack. Once VxWorks copies itself to DRAM, it sets up the real 
stack at the top of the BSS region. The canary check at 0x00BC3174 is actually checking a location within the loaded binary, so if the 
binary starts at 0x00000000, that address is directly accessible in the file.

The real question is whether SundanceBootable.bin is the complete ROM image with exception vectors and a boot stub, or just the RAM image 
that U-Boot loads directly at 0x00000000.

Looking at the actual flow: the binary gets loaded at 0x00000000, the CPU jumps there, and the initialization code runs. But there's a 
complication—the branch instruction at offset 0x9c that jumps to usrInit at 0x2ED020 uses a relative offset, so I need to figure out what 
the actual target address resolves to.

If the binary is loaded at 0, then the PC at 0x9c plus the relative offset 0x2ecf84 gives exactly 0x2ED020, which confirms the load address
 is correct. The exception vectors sit at 0x100, 0x200, and so on within the binary itself, which aligns with PPC405's non-offset exception
 table. The temporary stack initialized with `lis r1, 0x1` points to 0x10000, which is just used for early setup—VxWorks takes over and 
sets up the real stack once usrInit runs.

For QEMU, I need to load the binary at 0x00000000 with the entry point also at 0x00000000, allocate at least 64MB of RAM since VxWorks will
 need more than the 13MB binary size for heap, and accept that the temporary stack at 0x10000 will overlap with binary data initially. 
Since gdb-multiarch isn't available, I can use radare2's built-in debugger to connect to QEMU's GDB stub instead.

So radare2 becomes my primary tool—it handles disassembly, analysis, symbol labeling, and debugging through the GDB stub connection. This 
means the `p1-disasm` task shifts from writing a capstone script to running an r2 analysis session, and I'll replace the GDB init script 
with an r2 debug script. The BSS section at 0xC118D0–0xD441B0 confirms the load address is indeed 0, so now I need to update the plan and 
SQL todos accordingly.