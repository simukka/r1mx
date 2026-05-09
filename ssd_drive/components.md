# Internal Components — Controller and NAND Flash Identification

*Phase 2 of the REDMAG 256GB SSD reverse engineering effort.*

> **Status:** Physical teardown not yet performed. Information compiled from public sources,
> Toshiba product documentation, and community research. A physical unit teardown with
> die marking photography would be needed to confirm exact part numbers.

---

## Drive: Toshiba THNSNC256GBSJ (HG3 Series)

The drive is a complete, hermetically sealed SSD module. The main PCB carries:
- 1× SSD controller IC
- Multiple NAND flash packages
- 1× decoupling capacitor array (per standard SSD design)
- No external DRAM cache (the HG3 is a cacheless design)

---

## Component 1: SSD Controller — Toshiba "Type C"

### Identification

The ordering information in the Toshiba HG3 brochure encodes the controller as **"Type C"**
(field 3 in the part number schema `THNSxC256GBSJ`). This is Toshiba's internal codename
for a proprietary embedded SSD controller from their TC58 family.

Based on the product generation (2011, SATA II 3 Gbit/s, 32nm MLC NAND) and cross-referencing
Toshiba's TC58 product line:

| Parameter | Value | Confidence |
|-----------|-------|-----------|
| Controller family | TC58 series (Toshiba) | High |
| Likely part number | TC58NC6686G9F or TC58NCFxxx | Medium |
| Interface | SATA II (3 Gbit/s) | High |
| NAND channels | 4–8 parallel channels | Medium |
| ECC type | BCH (Bose–Chaudhuri–Hocquenghem) | Medium |
| ATA standard | ATA/ATAPI-8 (ACS-2) | High (confirmed by datasheet) |
| Embedded core | RISC microcontroller (Toshiba proprietary) | High |
| Host interface | SATA 2.6, AHCI | High |
| TRIM support | Yes (DATA SET MANAGEMENT, command 06h) | High (confirmed) |
| SMART | Full SMART monitoring (B0h sub-commands) | High (confirmed) |
| Security | ATA Security feature set (F1h–F6h) | High (confirmed) |
| FDE support | Optional (THNSFC prefix variant only) | High |

### Architecture (Inferred)

```
Host SATA interface (SiI3512 → SATA connector)
        │
        ▼
  [Toshiba TC58 Type C Controller]
  ┌──────────────────────────────┐
  │  SATA PHY / link layer       │
  │  ATA/ATAPI-8 command engine  │
  │  FTL (Flash Translation Layer)│
  │    ├─ LBA→PBA mapping        │
  │    ├─ Wear leveling          │
  │    ├─ Garbage collection     │
  │    └─ Bad block management   │
  │  BCH ECC engine              │
  │  NAND channel controllers    │
  │    (4–8 channels)            │
  └──────┬───────────────────────┘
         │ x8 parallel NAND bus (per channel)
         ▼
  [Toshiba 32nm MLC NAND packages]
  (multiple dies, interleaved across channels)
```

### Public Documentation Status

**None publicly available.** Toshiba's TC58 SSD controllers are proprietary and undocumented.
Access to specifications, register maps, or firmware APIs requires an NDA with Toshiba/Kioxia.

No vendor-specific ATA commands have been identified in public sources for this controller.
The drive's firmware (FTL, wear leveling, ECC algorithms) is stored in a reserved NAND area
and cannot be accessed via the ATA command set.

### Physical Characteristics (Estimated)

| Parameter | Value |
|-----------|-------|
| Package | BGA (estimated — standard for SSD controllers of this era) |
| Die size | Unknown |
| Process node | Unknown (separate from NAND — likely 65–90nm for controller) |
| Supply voltage | 3.3V or 1.8V (from drive's internal regulators, fed by 5V supply) |

---

## Component 2: NAND Flash — Toshiba 32nm MLC

### Identification

The datasheet explicitly states: **"TOSHIBA® 32nm MLC NAND Flash Memory"**. This places
the NAND in Toshiba's **A32nm generation** (first generation 32nm process), part of the
TH58TEG series (Toggle Mode NAND).

Toshiba's naming convention for 32nm MLC NAND:

```
TH58TEGxDxxxxx
  ││ │││ └── Suffix (speed, temp, package variant)
  ││ ││└──── Process / generation code
  ││ │└───── Organization / interface type
  ││ └────── Capacity code
  │└──────── Memory type: TEG = Toggle-mode MLC
  └───────── Toshiba NAND prefix
```

### Estimated Die Part Numbers (256 GB drive)

For a 256 GB drive (usable: 256,000,000,000 bytes raw; actual formatted: 256+ GB with
overprovisioning):

| Parameter | Calculation |
|-----------|------------|
| Raw NAND capacity needed | ~320 GB (256 GB + ~25% overprovisioning) |
| Likely die capacity | 32 Gb (4 GB) per die — standard for 32nm A-generation |
| Number of dies needed | ~640 Gb / 32 Gb = ~80 dies |
| NAND packages | Likely 8–16 packages (4–8 dies stacked per package, TSOP or BGA) |
| Controller channels | 8 channels × 10 dies/channel = 80 dies |

**Likely NAND part number:** `TH58TEG8DDKBA89` (32 Gb die, 32nm MLC, TSOP-48) or similar.
Physical teardown + die marking photography is required to confirm.

### NAND Specifications (32nm MLC, TH58TEG series)

| Parameter | Value |
|-----------|-------|
| Process | Toshiba 32nm "A32nm" |
| Cell type | MLC (2 bits/cell) |
| Voltage | 2.7V – 3.6V (internal; controller manages from 5V input) |
| Interface | Toggle Mode NAND (Toshiba proprietary, faster than ONFI 1.0) |
| Bus width | ×8 per die |
| Page size | 8 KB (8192 + spare bytes) — typical for 32nm Toshiba MLC |
| Block size | ~512 KB (64 pages × 8 KB) |
| Planes | 2 planes per die (enables plane-interleaved program) |
| Program time | ~300–700 μs per page |
| Erase time | ~3 ms per block |
| Read time | ~25 μs (register to bus transfer) |
| Endurance | ~3,000 P/E cycles (typical 32nm MLC) |
| Data retention | ~10 years at 25°C (new); decreases with P/E cycle count |
| ECC requirement | Minimum 24-bit per 1 KB (Toshiba 32nm specification) |
| Package | TSOP-48 or stacked-BGA (varies by capacity point) |

### Toggle Mode vs ONFI

Toshiba's 32nm NAND uses **Toggle Mode** (proprietary double-data-rate interface)
rather than ONFI (Open NAND Flash Interface). This is not visible to the host — the
SSD controller handles the Toggle Mode protocol internally. Toggle Mode provides
approximately 2× throughput vs ONFI 1.0 at equivalent clock speeds.

> **Implication for custom builds:** A replacement SSD controller must support
> Toggle Mode NAND to use Toshiba dies directly. Most modern SSD controllers
> (Phison, SMI, JMicron) support both Toggle Mode and ONFI — modern drives
> typically use 3D TLC NAND (ONFI or Toggle, depending on vendor).

---

## Wear Status Assessment

The drive's product life is documented as:

> **~5 years or 20,000 power-on hours, whichever comes first**

At 3,000 P/E cycles per die and ~320 GB raw NAND for 256 GB usable:

| Scenario | Estimate |
|----------|---------|
| Write amplification factor (typical WAF) | ~3–5× for sequential video workloads |
| Daily write (cinematic use, ~4 hours/day at 180 MB/s) | ~2.5 GB/day × 365 = ~900 GB/year |
| Effective PE cycles per year | 900 GB / 320 GB raw = ~2.8 cycles/year |
| Drive life before wear-out | ~3,000 / 2.8 ≈ **~1,000 years** (wear is not the limiting factor) |
| **Real limiting factor** | Product life = controller component aging, capacitor degradation, NAND oxide tunnel degradation — not raw P/E cycle count |

**Conclusion:** For the typical RED ONE MX usage pattern (intermittent cinematic use),
NAND wear is not the failure mode. Drive failure is more likely due to:
- Electrostatic discharge on the iVDR connector pins
- Capacitor aging on the drive PCB
- Firmware bugs in older drives (FTL table corruption)
- Physical connector wear (iVDR rated for 10,000 insertions)

---

## Equivalent / Replacement NAND

For a custom replacement drive, modern 3D NAND is substantially superior to Toshiba's 2011
32nm planar MLC:

| NAND | Process | P/E cycles | Page size | Interface | Cost |
|------|---------|-----------|----------|-----------|------|
| Toshiba 32nm MLC (original) | 32nm planar | ~3,000 | 8 KB | Toggle | EOL |
| Kioxia BiCS3 64-layer 3D TLC | 64L 3D | ~1,500 | 16 KB | Toggle Mode 2 | Available |
| Samsung V-NAND 4th gen TLC | 64L 3D | ~1,500 | 16 KB | Toggle | Available |
| Micron 96L 3D TLC | 96L 3D | ~1,000 | 16 KB | ONFI 3 | Available |
| SK Hynix 128L 3D TLC | 128L 3D | ~1,000 | 16 KB | ONFI 4 | Available |

Modern 3D TLC has lower P/E cycles than the original MLC but far greater density and
lower cost per GB. For a camera recording workload (mostly sequential writes, infrequent
overwrites), 3D TLC endurance is more than adequate.

---

## Summary

| Component | Status | Exact Part # |
|-----------|--------|-------------|
| SSD controller (Toshiba Type C) | Proprietary, no public docs | Likely TC58NC6686G9F — **unconfirmed** |
| NAND flash (Toshiba 32nm MLC) | Specs inferred from generation | Likely TH58TEG series — **unconfirmed** |
| Physical teardown | Not yet performed | Required to read die markings |

**To confirm component identities:** Open a donor THNSNC256GBSJ (or any HG3 unit) and
photograph the IC die markings under magnification. The controller will have a TC58 prefix;
the NAND will have a TH58 prefix.
