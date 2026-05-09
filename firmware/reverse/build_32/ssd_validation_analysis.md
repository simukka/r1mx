# RED ONE Build 32 — SSD Validation Analysis
**Status: In Progress**  
**Goal:** Patch firmware to accept any SSD, or identify exactly what SSD must report via ATA IDENTIFY.

---

## Binary Layout (CRITICAL)
- **File:** `reverse/build_32/extracted/software.bin` (15.25 MB)
- **CPU:** PowerPC 405GP, big-endian, flat binary loads at `0x00000000`
- **Code:** `0x000000–0x6FFFFF` and `0xE00000–0xE8BF20`
- **Data:** `0x700000–0xDFFFFF`
- **BSS:** `0xE9BF20–0x01153480` (zero-init at runtime, NOT in file)
- **ha/lo rule:** For address 0xD2Exxxh: `lis rX, 0x00D3` then `addi rX, rX, (addr - 0xD30000)` (negative)

---

## Approved SSD Model String Table
**Location: `0xD2E3E8–0xD2E490`** (null-terminated, each aligned to 4 bytes)

| Address    | String                  | Notes                     |
|------------|-------------------------|---------------------------|
| 0xD2E3E8   | `RedRAM\0\0`            | 8-byte aligned            |
| 0xD2E3F0   | `RedRAID\0`             | 8-byte aligned            |
| 0xD2E3F8   | `LEXAR ATA FLASH CARD\0\0\0\0` | 24-byte aligned     |
| 0xD2E410   | `RED 16GB CF\0`         |                           |
| 0xD2E41C   | `RED 32GB CF\0`         |                           |
| 0xD2E428   | `RED 64GB CF\0`         |                           |
| 0xD2E434   | `RED 55GB SSD \0\0\0`   | trailing space + padding  |
| 0xD2E444   | `RED 64GB SSD \0\0\0`   | trailing space + padding  |
| 0xD2E454   | `RED 128GB SSD \0\0`    |                           |
| 0xD2E464   | `RED 256GB SSD \0\0`    |                           |
| 0xD2E474   | `RED 512GB SSD \0\0`    |                           |
| 0xD2E484   | `/ata00:1\0\0\0\0`      | drive path                |

Drive state enum strings (at `0xD2E4F8`):
`DRIVE0`, `NOTPRESENT`, `PRESENT`, `EJECTED`, `EXPORTED`, `NOTMOUNTED`,
`UNCONFIGURED`, `INCOMPATIBLE`, `MOUNTED`, `UNMOUNTED`

Serial format strings:
- `CP-5723_` at `0xD2E7F0`
- `_X_F` at `0xD2E7FC`

Source file reference: `app_modules/digmag/digmagmgr.cpp` at `0xD2E720`

Revision/version model strings at `0xD2E5C0–0xD2E720`:
- `RED 16GB REV B`, `RED 32GB REV A1`, `RED 64GB REV B`,
- `RED 55GB V1/V2`, `RED 128GB V1/V2/V3`, `RED 256GB V1/V2/V3`,
- `RED 512GB V1/V2/V3/V4`, `RED 55GB V1/V2`, `External Disk 0`

---

## Key Functions

### strncmp: `0x0039ACEC`
Standard strncmp. Called throughout digmag module.

### strncpy: `0x0039B1D4`
Standard strncpy.

### Error/log function: `0x4A6438`
Called with (severity, format_str_ptr, file_line, col, line). VxWorks log.

### `0x4AB25C` — Drive Object Lookup / Type Converter
- Called with `r3 = drive_type_code`
- Compares r3 against `0x2EE` (758)
- Uses base register `lis r12, 0xE3; addi r12, -15140` → `0xE2C4FC` (VxWorks param DB?)
- Scales index and loads pointer from a table
- Returns a POINTER to a drive object or descriptor
- Critical: this is called at start of `0x4D04D0`

### `0x4D04D0` — Drive Type Switch Dispatch
**Args:** `r3 = object_ptr` (saved→r31), `r4 = drive_type_code` (saved→r29)

**Logic:**
```
1. Call 0x4AB25C(r3=drive_type) → r3 = drive_obj_ptr (or similar)
2. r0 = drive_type - 21
3. cmpli cr7, r0, 5   → is drive_type in [21..26]?
4. bc if r0 > 5 → 0x4D06A0 (ERROR, returns 0 via log message)
   -- if drive_type ∈ {21,22,23,24,25,26} falls through:
5. lis r9, 0xD3; rlwinm r0, r0, 2, 0, 29; addi r9, r9, -7100
   → r9 = 0xD2E444, r0 = (type-21)*4
6. lwzx r11, r9, r0   → r11 = *(0xD2E444 + index*4)
7. add r11, r11, r9; mtspr CTR, r11; bctr  → SWITCH DISPATCH
```

**UNRESOLVED:** The data at 0xD2E444 is ASCII string "RED 64GB SSD " bytes, which do NOT produce valid code addresses when used as relative jump offsets. Possible explanations:
- BSS/RAM at 0xD2E444 is populated at runtime with real function pointers before this code runs (the file data there is overwritten)
- The switch table is elsewhere (wrong address calculation?)
- The memory map differs from flat-file assumption

**Callers of 0x4D04D0:**
- `0x4CF768` — large digmag function, calls with `r4 = 26` (li r4, 26)
- `0x4D06FC` — function 0x4D06C4, recursive-style
- `0x5D1CF4` — calls with `r4 = 22`
- `0x5D2700` — calls with `r4 = 23`

### `0x4D06C4` — Sibling dispatch function
Called with `r3=object_ptr, r4=drive_type`. Calls `0x4BC2A0`, then `0x4D04D0`, then `0x4D03F8`. Likely `DigMagDrive::SetType` or similar.

### `0x4BC2A0` — DigMag object getter
- Loads `r3 = 0xD2C4D4` ("MEDIA.DIGMAG.DRIVE?" param path)
- Calls `0x4B4B80` (VxWorks param lookup)
- Returns handle to digmag drive object

### `0x4C9ADC` — Model string registration wrapper
- Args: `r3=model_string_ptr`, `r4=drive_handle`, `r5=...`
- Reorganizes args and calls `0x4B600C`
- Called from: `0x4BBFCC`, `0x4C9C34`, `0x4D858C`, `0x4D865C`, `0x4D872C`, `0x4D87FC`, `0x4D89A0`, `0x4D8A40`
- These callers pass PARTIAL model string pointers (e.g. 0xD2E3EC = "AM" = 4 bytes into "RedRAM")
- **Purpose:** Registers media types in the VxWorks parameter system, NOT model string comparison

### Parameter Registration Stubs (VxWorks param DB)
The digmag module registers all media type strings as named parameters. The pattern is always:
```
mfspr r0, LR
lis rX, 0x00D3
stwu r1, -16(r1)
addi rX, rX, <offset>   ; rX → model/state string
stw r0, 20(r1)
bl 0x4B7BD8 / 0x4B600C / 0x4B4B80 / 0x4B50DC  ; param registration API
lwz r0, 20(r1)
addi r1, r1, 16
mtspr LR, r0
blr
```
Functions `0x4B7BD8`, `0x4B600C`, `0x4B4B80`, `0x4B50DC` are VxWorks parameter API calls.
These stubs exist for: RedRAM, RedRAID, CF cards, all SSDs, drive states, serial format, etc.

---

## strncmp Calls in Digmag Module (0x4A0000–0x4E0000)

| Address    | n (r5) | Notes                                          |
|------------|--------|------------------------------------------------|
| 0x4A2F54   | var    | String buffer utilities (strnstr-like)         |
| 0x4A2FFC   | var    | String buffer utilities                        |
| 0x4A3050   | var    | String buffer utilities                        |
| 0x4A3110   | var    | String buffer utilities                        |
| 0x4A40EC   | 40     | In function 0x4A4098 (alloc/resource fn)       |
| 0x4A960C   | ?      |                                                |
| 0x4ACB90   | ?      |                                                |
| 0x4AD1D8   | 20     | Tiny wrapper: strncmp(arg1, NULL, 20) — unclear |
| 0x4AE3C8   | 16     |                                                |
| 0x4AE64C   | ?      |                                                |
| 0x4AE6D0   | ?      |                                                |
| 0x4AE758   | 16     |                                                |
| 0x4AEAA8   | 140    |                                                |
| 0x4AF40C   | 140    |                                                |
| 0x4B2C10   | ?      |                                                |
| 0x4B3FB4   | 5      |                                                |
| 0x4B4998   | ?      |                                                |
| 0x4B4A88   | ?      |                                                |
| 0x4BBC38   | ?      |                                                |
| 0x4C1CD4   | 32     |                                                |
| 0x4C21BC   | 28     |                                                |
| 0x4C6E28   | 20     | In tiny function 0x4C6E0C                      |
| 0x4C6EF4   | 20     |                                                |
| 0x4C6F1C   | 20     |                                                |
| 0x4C8FF0   | ?      |                                                |
| 0x4CD6D4   | ?      |                                                |
| 0x4DB078   | ?      |                                                |

**Unanalyzed high-value candidates:** 0x4AE3C8 (n=16), 0x4AE758 (n=16), 0x4AEAA8 (n=140), 0x4BBC38

---

## Code References to Model String Data

All `lis r?, 0x00D3` + `addi` pairs resolved to model string area (`0xD2E3EC–0xD2E7F4`):

| Code Address | Target       | String                      | Caller chain                         |
|-------------|--------------|-----------------------------|------------------------------------|
| 0x4BBFC8    | 0xD2E3EC     | "AM" (in RedRAM)            | bl 0x4C9ADC → param registration   |
| 0x4BBFFC    | 0xD2E3EC     | "AM" (in RedRAM)            | bl 0x4C9BDC → param registration   |
| 0x4BC030    | 0xD2E3EC     | "AM" (in RedRAM)            | bl 0x4C9628 → param registration   |
| 0x4BC064    | 0xD2E3EC     | "AM" (in RedRAM)            | bl 0x4C96CC → param registration   |
| 0x4CFA34    | 0xD2E3EC     | "AM"                        | bl 0x4B7BD8 → param registration   |
| 0x4CFA5C    | 0xD2E3EC     | "AM"                        | bl 0x4B600C → param registration   |
| 0x4CFA84    | 0xD2E3EC     | "AM"                        | bl 0x4B4B80 → param registration   |
| 0x4CFAAC    | 0xD2E3EC     | "AM"                        | bl 0x4B50DC → param registration   |
| 0x4D0508    | 0xD2E444     | "RED 64GB SSD "             | Switch dispatch base (see 0x4D04D0)|
| 0x4D3EF4    | 0xD2E45C     | "B SSD " (in RED 128GB SSD) | bl 0x4B7BD8 → param registration   |
| 0x4D3F1C    | 0xD2E45C     | "B SSD "                    | bl 0x4B600C → param registration   |
| 0x4D3F44    | 0xD2E45C     | "B SSD "                    | bl 0x4B4B80 → param registration   |
| 0x4D3F6C    | 0xD2E45C     | "B SSD "                    | bl 0x4B50DC → param registration   |
| 0x4D5FFC    | 0xD2E53C     | "INCOMPATIBLE"              | bl 0x4B7BD8 → param registration   |
| 0x4D6024    | 0xD2E53C     | "INCOMPATIBLE"              | bl 0x4B600C → param registration   |
| 0x4D604C    | 0xD2E53C     | "INCOMPATIBLE"              | bl 0x4B4B80 → param registration   |
| 0x4D6074    | 0xD2E53C     | "INCOMPATIBLE"              | bl 0x4B50DC → param registration   |
| 0x4DD268    | 0xD2E7F4     | "723_" (in CP-5723_)        | bl 0x4B7BD8 → param registration   |
| 0x4DD290    | 0xD2E7F4     | "723_"                      | bl 0x4B600C → param registration   |
| 0x4DD2B8    | 0xD2E7F4     | "723_"                      | bl 0x4B4B80 → param registration   |
| 0x4DD2E0    | 0xD2E7F4     | "723_"                      | bl 0x4B50DC → param registration   |

**CONCLUSION so far:** All discovered model string code references are VxWorks **parameter registration** stubs (not comparison code). The actual IsCompatible comparison function has NOT yet been located.

---

## Unresolved: Drive Type Codes

| Type | Caller / Context                              |
|------|-----------------------------------------------|
| 21   | (unknown caller to 0x4D04D0)                  |
| 22   | `0x5D1CF4` → called as `li r4, 22`           |
| 23   | `0x5D2700` → called as `li r4, 23`           |
| 24   | (unknown)                                     |
| 25   | (unknown)                                     |
| 26   | `0x4CF768` → called as `li r4, 26`           |

Drive types < 21 or > 26 → rejected by `0x4D04D0` with error.

---

## Next Steps

### Priority 1: Find IsCompatible / ATA model string comparison
The function that reads the ATA IDENTIFY model string from a drive and compares it against the approved table has NOT been found yet. Approach:

1. **Analyze `0x4AE3C8` (n=16), `0x4AE758` (n=16), `0x4AEAA8` (n=140)** — strncmp calls with n close to model string lengths; disassemble full enclosing functions.

2. **Analyze `0x4BBC38`** — unknown strncmp; find its enclosing function.

3. **Look for ATA IDENTIFY processing** — search for code that reads 40-byte ATA model string (lhz/lwz in a loop, byte-swap pattern) and then calls strncmp.

4. **Resolve the 0x4D04D0 switch table mystery** — determine if 0xD2E444 is truly the jump table base or if the table resides in BSS (populated at runtime). Check if BSS initialization code writes pointers to 0xD2E444.

5. **Trace from MOUNTED/INCOMPATIBLE state transitions** — find code that calls `setState(INCOMPATIBLE)` or `setState(MOUNTED)` on the drive object, then trace upward to the comparison.

6. **Check 0x4D0CB4, 0x4D03F8, 0x4D114C** — called immediately after the 0x4D04D0 invocations; may implement the actual type-check logic.

### Priority 2: Serial Number Validation
- Format: `CP-5723_XXXXXXXX_X_F` (prefix at 0xD2E7F0, suffix at 0xD2E7FC)
- Find where serial number is read from ATA IDENTIFY (words 10-19, 20 bytes) and compared

### Priority 3: R3D Write Speed Gating
- Once drive is accepted, find where write speed is limited for non-certified drives
- Look near filesystem write path and frame rate/resolution checks

---

## Patch Candidates (Hypothetical)

### Option A: Firmware Patch (force all SSDs compatible)
- **Target:** The branch instruction that leads to `INCOMPATIBLE` state
- **Not yet identified** — need to find IsCompatible function first
- Once found: NOP the branch or change `bne→b` to always take compatible path

### Option B: SSD Spoofing (ATA IDENTIFY strings)
The SSD must report (via ATA IDENTIFY):
- **Model string** (words 27–46, 40 bytes, space-padded): exactly one of the approved strings above, e.g. `"RED 64GB SSD             "` (padded to 40 chars with spaces)
- **Serial number** (words 10–19, 20 bytes): format `CP-5723_XXXXXXXX_X_F` where X = hex digits

**ATA IDENTIFY note:** All word fields are reported as big-endian words with bytes swapped within each word (ATA spec). The firmware likely byte-swaps before comparison.

---

## QEMU Patches (for emulation, separate from SSD bypass)
- `0x000084`: `3C200001 → 3C200800` (SP relocation)
- `0x36C388`: `409EFFF8 → 60000000` (canary NOP 1)
- `0x36C394`: `409EFFEC → 60000000` (canary NOP 2)

---

## Session History
- Firmware decrypted: AES-256-CBC, MD5 KDF, password `M1H5gwOXh757rIRVY6Gj2tN080AYSX03`
- VxWorks param registration API: `0x4B7BD8`, `0x4B600C`, `0x4B4B80`, `0x4B50DC`
- Error/log fn: `0x4A6438`
- Digmag module code: `0x4A0000–0x4E0000` (main), `0x5D0000–0x5D3000` (additional)
