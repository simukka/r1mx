# Replacement Drive Options

*Phase 5 of the REDMAG 256GB SSD reverse engineering effort.*

---

## Context

The RED ONE MX's `DigMagMgrModule::IsCompatible()` function validates the drive model string
against a hardcoded list. Any replacement drive must either:

- **Match** an approved model string, OR
- **Cause the firmware to be patched** to bypass the check

Additionally, any replacement must meet the physical and electrical interface requirements
established in Phases 3 and 4.

---

## Minimum Requirements (All Options)

| Requirement | Value | Source |
|-------------|-------|--------|
| Form factor | 2.5-inch | Physical constraint |
| Interface | SATA II / SATA III (backward compatible) | ssd_board interface |
| Power | 5V ±5% only (no 3.3V or 12V) | Phase 3 — SATA pin P8/P9 only |
| Sector size | 512 bytes (512n or 512e) | firmware-analysis.md |
| Capacity | ≥ 256 GB recommended | datasheets/README.md |
| Sequential write | ≥ 180 MB/s at 128 KB blocks | Recording bandwidth |
| IDENTIFY DEVICE | Must respond correctly | ataDevIdentify() required |
| ATA Security | SECURITY FREEZE LOCK (F5h) must be handled | Standard VxWorks behaviour |
| Model string | Must match firmware list OR firmware patched | firmware-analysis.md |
| Connector height | ≤ 9.5 mm (2.5" standard) | Mechanical fit |

---

## Option A — Drop-In Approved Drive (Simplest)

### Concept
Use a drive whose model string already appears in the firmware's approved list.
No firmware modification needed.

### Approach 1: Use the Original Toshiba HG3 (or equivalent)

The original REDMAG 256GB SSD is the Toshiba **THNSNC256GBSJ** (HG3 Series, 2011).
This drive is end-of-sale but still available used/refurbished:

| Source | Typical price |
|--------|--------------|
| eBay (used) | $20–$60 USD |
| Japanese electronics surplus | ¥3,000–¥8,000 |
| Enterprise surplus resellers | $15–$40 USD |

**Risk:** End-of-life hardware. Used drives may have high wear (product life is ~5 years / 20,000 hours).

### Approach 2: Identify Other Approved Drives from Later Firmware

Build 13 lists: `Adtron A25FB-32GC21N`, `WDC WD800BEVS-22LAT0`, `HTS721010G9SA00`.  
Later builds (Build 17–32) almost certainly add more approved drives. **Extracting the
approved list from Build 32 is the highest-priority next step.** Procedure:

```bash
# 1. Decrypt build 32 package
openssl enc -d -aes-256-cbc -md md5 \
  -pass pass:M1H5gwOXh757rIRVY6Gj2tN080AYSX03 \
  -in firmware/builds/build_32_v32.0.3.zip -out /tmp/build32.tar.gz

# 2. Extract su.tar and firmware binary
tar xf /tmp/build32.tar.gz -C /tmp/build32/

# 3. Search for model strings adjacent to known entries
strings /tmp/build32/SundanceBootable.bin | grep -A5 -B5 "THNSNC\|Adtron\|WDC\|Hitachi"
```

**Expected outcome:** A list of 5–15 approved drive model strings covering all official
RED Magazines across all generations.

---

## Option B — Model String Reprogramming (Modern SSD)

### Concept
Some SATA SSD controllers allow the `IDENTIFY DEVICE` model string (words 27–46, 40 bytes)
to be changed via vendor-specific commands or EEPROM/flash programming. Program a modern
SSD to report an approved model string.

### Candidate Controllers

| Controller | Vendor | Model string configurable? | Notes |
|-----------|--------|--------------------------|-------|
| JMicron JMF667H | JMicron | Yes (via PC tool) | Common in older SSDs; EOL |
| JMicron JMF676A | JMicron | Yes | SATA III |
| Silicon Motion SM2246EN | SMI | Yes (via SM2246XT tool) | SATA III, widely available |
| Silicon Motion SM2258 | SMI | Yes | 3D NAND support |
| Phison S11 / PS2251-07 | Phison | Yes (via Phison UP tool) | Common in value SSDs |
| Phison S10 | Phison | Yes | Higher performance |
| Marvell 88SS1074 | Marvell | Limited (requires firmware build) | Used in Samsung EVO 850 |

### Practical Approach

1. Acquire a modern 2.5" SATA SSD with a Phison or SMI controller (very common in
   value SSDs — Kingston A400, Crucial BX series, etc.)
2. Use the appropriate vendor tool to re-program the model string to match an
   approved drive (e.g., `THNSNC256GBSJ` once confirmed from Build 32 analysis)
3. Verify the `IDENTIFY DEVICE` response with `hdparm -I /dev/sdX` on Linux

**Example tools:**
- `hdparm --drive-name` (limited support)
- Phison UP tool (Windows only, proprietary)
- SMI MPTool (Windows only, proprietary)

**Risk:** These vendor tools are difficult to obtain and may brick the drive if used
incorrectly. Some controllers prevent model string modification after manufacturing lock.

**Cost:** $15–$50 USD for a modern 256GB+ SATA SSD.

---

## Option C — Custom SATA Adapter Board (Custom Build)

### Concept
Design and build a small PCB that:
1. Accepts the 26-pin iVDR connector from the camera
2. Routes power (5V) and SATA signals to a standard 2.5" SATA drive bay
3. Pulls the PRSNT# (pin 20) correctly to signal drive presence

This is the "passive adapter" approach — it makes any standard 2.5" SATA SSD work in
the iVDR bay, **but still requires the firmware to accept the drive model string.**

### Bill of Materials (Passive Adapter)

| Component | Part | Qty | Est. cost |
|-----------|------|-----|-----------|
| iVDR 26-pin receptacle | Amphenol 10033998-002LF (or compatible) | 1 | $5–$15 |
| 2.5" SATA receptacle (22-pin combo) | 3M 5622 or equivalent | 1 | $2–$5 |
| Pull-down resistor (PRSNT#) | 10kΩ, 0402 or 0603 | 1 | <$1 |
| PCB | Custom 2-layer, ~30×30 mm | 1 | $5–$15 (JLCPCB/PCBWay) |

**Total BOM:** ~$15–$40 per unit

### PCB Design Requirements
- Must pass SATA differential pairs (impedance-controlled, 100Ω differential)
- Keep RX/TX trace length matched (±5 mm)
- Route 5V at least 1A capable (2× 0.5mm traces minimum)
- No level shifters needed (iVDR → SATA is direct SATA signalling)

---

## Option D — Firmware Patch (Universal Compatibility)

### Concept
Patch `DigMagMgrModule::IsCompatible()` in the firmware binary to always return
true (DigMag compatible). Any 2.5" SATA drive then works without modification.

### Procedure

1. **Decrypt a firmware build** (Build 17+ uses AES-256-CBC with known key):
   ```bash
   openssl enc -d -aes-256-cbc -md md5 \
     -pass pass:M1H5gwOXh757rIRVY6Gj2tN080AYSX03 \
     -in firmware/builds/build_32_v32.0.3.zip -out /tmp/build32_dec.gz
   gunzip /tmp/build32_dec.gz -c > /tmp/build32_sw.bin
   ```

2. **Locate `IsCompatible()` in the binary:**
   - Search for the mangled symbol `_ZN15DigMagMgrModule12IsCompatibleEv` in strings
   - If present: use the address directly
   - If stripped: trace calls from MEDIA.DIGMAG.TYPE parameter setter via cross-reference

3. **Identify the function prologue** (PowerPC 405, big-endian):
   ```
   stwu r1, -N(r1)    # 94 21 FF xx
   mflr r0            # 7C 08 02 A6
   stw  r0, N+4(r1)   # 90 01 00 xx
   ```

4. **Replace with an immediate return of "DigMag"** (true):
   - Set `r3 = 1` (or pointer to "DigMag" string) at the function entry
   - Insert `blr` after
   - Or more robustly: change any `cmpwi` or string-compare branch to always fall through

5. **Repackage and flash** the patched firmware via the standard upgrade procedure
   (`su.tar` on an SSD at `/upgrade/su.tar`)

### Risks
- If the function also performs media write-speed benchmarking (framerate check), patching
  `IsCompatible()` may not be sufficient — `BAD_FRAMERATE` rejection may remain
- Firmware patching voids any potential warranty claims (but camera is already out of support)
- A bad patch could brick the camera (recovery via JTAG or boot loader may be possible)

---

## Option E — FPGA-Based SATA Drive Emulator

### Concept
Use an FPGA development board with SATA capability to emulate a complete SATA SSD that:
- Reports approved drive identity in `IDENTIFY DEVICE`
- Stores data in external flash or DRAM
- Implements the required ATA command subset

### Candidate FPGA Boards with SATA

| Board | FPGA | SATA | Flash storage | Notes |
|-------|------|------|--------------|-------|
| Digilent Nexys Video | Artix-7 | Yes (via PMOD or direct) | No (external) | Limited PCIe/SATA |
| Xilinx KCU116 | Kintex UltraScale+ | Yes | No | Expensive |
| OrangeCrab (iCE40) | iCE40HX8K | Partial | No | Low speed only |
| Custom FPGA SSD | Any mid-range | Custom PHY | External NAND/DRAM | Most flexible |

**Open-source SATA implementations:**
- [LiteSATA](https://github.com/enjoy-digital/litesata) — Python-based SATA Gen1/2 core for Xilinx/ECP5
- [sata_gen3](https://opencores.org/) — OpenCores SATA III core (limited)

### Complexity Assessment
This option requires significant FPGA development effort (3–6 months for a functional device).
Only recommended as a last resort if no other option is viable.

---

## Recommendation

### Near-term (days)
1. **Extract Build 32 firmware** and get the complete approved drive list (Option A / Approach 2)
2. **Test known approved drives** (WDC WD800, Hitachi HTS721, Adtron if available) to confirm
   the model-string validation is the only barrier

### Mid-term (weeks)
3. **Option B (model string reprogramming)** using a Phison or SMI-based SATA SSD —
   cheapest path to a modern, in-production replacement
4. **Design the passive adapter PCB** (Option C) so any 2.5" drive can be used mechanically

### Long-term (months)
5. **Option D (firmware patch)** to `IsCompatible()` — provides universal compatibility
   without per-drive configuration; distribute the patched firmware to the RED ONE community

---

## Comparison Table

| Option | Cost | Complexity | Availability | Risk | Model Validation Bypass |
|--------|------|-----------|-------------|------|------------------------|
| A1 — Original Toshiba HG3 (used) | Low | None | Decreasing | Medium (EOL wear) | N/A (already approved) |
| A2 — Other approved drive (from Build 32 list) | Low | Low | TBD | Low | N/A |
| B — Model string reprogramming | Low–Medium | Medium | Good | Medium | Yes |
| C — Passive adapter PCB | Low | Medium (PCB design) | Any SATA SSD | Low (HW) | No (still needs firmware) |
| D — Firmware patch | Minimal | High | Universal | Medium (brick risk) | Yes |
| E — FPGA emulator | High | Very High | Any storage | Low | Yes |

**Best overall path:** A2 (if approved drives found) → B (if model reprogramming works) → D (firmware patch)  
**Quickest result:** A1 (source a used Toshiba HG3) while working on longer-term solutions
