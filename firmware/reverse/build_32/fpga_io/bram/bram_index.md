# BRAM Blob Index — XC4VFX100 IO-FPGA

Total frames: 25170, frame size: 164B  
All-zero frames: 6644 (26.4%)  
Candidate BRAM blobs: 20  

**Key structural invariant:** `word[20]` (21st of 41 words) = 0x00000000 in 100% of BRAM data frames; 0% in CLB frames.  
**BRAM data block:** frames ~19136–25170 (empirical). CLB region: frames 0–18750.

## Non-zero BRAM blocks (highest value — contain actual initialization data)

| file | frames | length | entropy (active) | popcount | notes |
|------|--------|--------|------------------|----------|-------|
| block_B_f22024.bin | 22024–22063 | 40 | 5.09 bits/B | 0.234 | Structured table; 65% mono-rising u16 |
| block_A_f22088.bin | 22088–22125 | 38 | **7.17 bits/B** | 0.359 | Dense data — 3D LUT / coefficient table |
| block_C_f22152.bin | 22152–22189 | 38 | **7.25 bits/B** | 0.360 | Dense data — 3D LUT / coefficient table |
| block_D_f22216.bin | 22216–22253 | 38 | 4.75 bits/B | 0.177 | Structured table; 65% mono-rising u16 |

## All blobs (including all-zero)

## All blobs (including all-zero)

| idx | start_frame | minors | size_B | notes |
|-----|-------------|--------|--------|-------|
|   0 |        3616 |     64 |  10496 | ALL_ZERO (BRAM INIT=0) |
|   1 |       11981 |     64 |  10496 | ALL_ZERO (BRAM INIT=0) |
|   2 |       18748 |     64 |  10496 | ALL_ZERO (BRAM INIT=0) |
|   3 |       19134 |     64 |  10496 | ALL_ZERO (BRAM INIT=0) |
|   4 |       19456 |     64 |  10496 | ALL_ZERO (BRAM INIT=0) |
|   5 |       19584 |     64 |  10496 | ALL_ZERO (BRAM INIT=0) |
|   6 |       19776 |     64 |  10496 | ALL_ZERO (BRAM INIT=0) |
|   7 |       20042 |     64 |  10496 | ALL_ZERO (BRAM INIT=0) |
|   8 |       22329 |     64 |  10496 | ALL_ZERO (BRAM INIT=0) |
|   9 |       22603 |     64 |  10496 | ALL_ZERO (BRAM INIT=0) |
|  10 |       23245 |     64 |  10496 | ALL_ZERO (BRAM INIT=0) |
|  11 |       23887 |     64 |  10496 | ALL_ZERO (BRAM INIT=0) |
|  12 |       24529 |     64 |  10496 | ALL_ZERO (BRAM INIT=0) |
|  13 |       24721 |     64 |  10496 | ALL_ZERO (BRAM INIT=0) |
|  14 |        1651 |     46 |   7544 | entropy=0.457 bits/byte; REPEATING period=2 (×115) |
|  15 |       10016 |     34 |   5576 | entropy=0.599 bits/byte; REPEATING period=2 (×122) |
|  16 |       13362 |     34 |   5576 | entropy=0.551 bits/byte; REPEATING period=2 (×122) |
|  17 |       15035 |     32 |   5248 | entropy=0.418 bits/byte; MONOTONIC_RISING u16 (245/255); REPEATING period=2 (×12 |
|  18 |       17161 |     33 |   5412 | entropy=0.404 bits/byte |
|  19 |       18171 |     33 |   5412 | entropy=0.355 bits/byte; REPEATING period=2 (×104) |
