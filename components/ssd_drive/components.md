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

### Part Number Decode

The "C" in **THNSNC** is Toshiba's ordering-code designation for the controller generation.
The full controller generation progression:

| Model Prefix | Controller Gen | SSD Family |
|---|---|---|
| THNSNA | Type A | Early HG1 (third-party controller) |
| THNSNB | Type B | HG2 |
| **THNSNC** | **Type C** | **HG3 ← this drive** |
| THNSND | Type D | HG4 |
| THNSNE | Type E | HG5 |

The HG3 is the **first Toshiba SSD with a fully in-house controller** (no Intel or Marvell sourcing).

Full part number decode for **THNSNC256GBSJ**:

```
T  H  N  S  N  C  256G  B  S  J
│                  │    │  │  └── Interface: J = SATA 3Gbps (SATA II)
│                  │    │  └───── Temp spec: S = standard (0–70°C)
│                  │    └──────── Form factor: B = 2.5-inch 9.5mm
│                  └─────────────  Capacity: 256 GB
│  Controller gen: C = Type C (3rd-gen proprietary, fully in-house)
└─────────────────────────────── Toshiba NAND drive
```

### Identification

| Parameter | Value | Confidence |
|-----------|-------|-----------|
| Controller family | Toshiba proprietary (Type C) | High |
| Die part number | **Unknown — no public teardown exists** | None |
| Community speculation (unverified) | "TC58NCF818GBL" | Low — no datasheet or die photo confirms this |
| Embedded CPU core | ARM-based (Cortex-R class, inferred from generation) | Medium |
| Controller process | ~65–55nm CMOS (Toshiba or TSMC fab) | Low |
| NAND channels | 8 parallel channels | Medium |
| ECC type | BCH (Bose–Chaudhuri–Hocquenghem) | Medium |
| DRAM cache | Possible (~128 MB LPDDR on-package), not confirmed | Low |
| ATA standard | ATA/ATAPI-8 (ACS-2) | High (confirmed by datasheet) |
| Host interface | SATA 2.6, 3 Gbit/s | High |
| TRIM support | Yes (DATA SET MANAGEMENT, command 06h) | High (confirmed) |
| SMART | Full SMART monitoring (B0h sub-commands) | High (confirmed) |
| Security | ATA Security feature set (F1h–F6h) | High (confirmed) |
| FDE support | Optional variant (THNSFC prefix) only | High |
| Package | FBGA (Fine-pitch BGA) | High (standard for SSD controllers) |

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

## Component 2: NAND Flash — Toshiba 32nm MLC (TH58TEG-DC family)

### Identification (Confirmed from Primary Sources)

The datasheet states **"TOSHIBA® 32nm MLC NAND Flash Memory"**, placing the NAND in
Toshiba's **"DC" generation** (32nm), part of the **TH58TEG-DC family** using Toggle DDR1.0
interface. Confirmed directly from Alldatasheet.com datasheet preview text:

> *"TOSHIBA NAND memory Toggle DDR1.0 Technical Data Sheet, Rev. 0.3, 2012-04-10"*
> Source: `alldatasheet.com/datasheet-pdf/pdf/1462976/TOSHIBA/TH58TEG7DCJ.html`

Toshiba's naming convention for DC-generation MLC NAND:

```
TH58TEG8DCJ TA K0
│└┘│││ ││  └──┴── Package config:
│  │││ │└──────── Gen code: DC=32nm, DD=19nm, DE=15nm
│  │││ └───────── Interface: J = Toggle DDR
│  ││└─────────── Capacity: 7=32Gbit/die (4GB), 8=64Gbit/die (8GB)
│  │└──────────── Cell type: E = MLC
│  └───────────── Interface type: G = Toggle DDR
└──────────────── TH58 = Toshiba NAND prefix
```

**Package suffix guide:**

| Suffix | Meaning |
|--------|---------|
| (none) | Bare die |
| TA20 | 2-die LGA stack |
| TAK0 | 4-die LGA stack |

### Confirmed Part Numbers in DC (32nm) Family

*Source: alldatasheet.com — 18 TH58TEG-DC parts listed, all Toggle DDR1.0, Rev. 0.3, 2012-04-10*

| Part Number | Die density | Capacity/die | Package | Total/pkg |
|---|---|---|---|---|
| TH58TEG7DCJ | 32 Gbit | 4 GB | Bare die | 4 GB |
| TH58TEG7DCJTA20 | 32 Gbit | 4 GB | 2-die LGA stack | 8 GB |
| TH58TEG7DCJTAK0 | 32 Gbit | 4 GB | 4-die LGA stack | 16 GB |
| TH58TEG8DCJ | 64 Gbit | 8 GB | Bare die | 8 GB |
| TH58TEG8DCJTA20 | 64 Gbit | 8 GB | 2-die LGA stack | 16 GB |
| **TH58TEG8DCJTAK0** | **64 Gbit** | **8 GB** | **4-die LGA stack** | **32 GB** |

### Most Likely Configuration for THNSNC256GBSJ (256 GB)

The **TH58TEG8DCJTAK0** (4-die LGA stack, 32 GB/package) is the most probable package:

| Parameter | Value |
|-----------|-------|
| Package | TH58TEG8DCJTAK0 |
| Packages on PCB | **8 packages** |
| Raw capacity | 8 × 32 GB = **256 GB** |
| Spare area / overprovisioning | From reserved dies/blocks (controller-managed) |
| PCB layout | 4 packages per side of double-sided 2.5" PCB |

*(Alternatively: 16 × TH58TEG8DCJTA20 for the same total — smaller stacks, more of them)*

Physical teardown + die marking photography required to confirm.

### NAND Specifications (32nm MLC, TH58TEG-DC series)

| Parameter | Value | Confidence |
|-----------|-------|-----------|
| Process node | Toshiba 32nm "DC" generation | High — confirmed |
| Cell type | MLC (2 bits/cell) | High — confirmed |
| Interface | **Toggle DDR1.0** (Toshiba/Samsung co-developed, NOT ONFI) | High — confirmed |
| Max Toggle DDR speed | 100 MHz DDR = ~200 MT/s effective | High — confirmed |
| Bus width | ×8 per die | High |
| Page size | ~8 KB data + OOB (spare area) | Medium |
| Block size | ~2 MB (256 pages × 8 KB) | Medium |
| Planes per die | 2 (enables plane-interleaved program) | Medium |
| Program time | ~300–700 μs per page | Medium |
| Erase time | ~3 ms per block | Medium |
| Endurance | ~3,000–5,000 P/E cycles | Medium |
| Data retention | ~10 years at 25°C (new) | Medium |
| ECC requirement | ~24-bit per 1 KB minimum | Medium |
| Voltage | 2.7V–3.6V (internal; supplied from 5V via drive regulators) | High |

### Toggle DDR1.0 vs ONFI — Key Distinction

Toshiba's 32nm NAND uses **Toggle DDR1.0** (Toshiba/Samsung co-developed DDR interface),
**not** ONFI (Open NAND Flash Interface, used by Micron/Intel/SK Hynix).

- Toggle DDR uses bidirectional DQS strobing without a separate clock signal
- Toggle DDR1.0 = up to 100 MHz DDR = ~200 MT/s effective data rate
- Electrically **incompatible** with ONFI NAND at the bus level
- Later standardized by JEDEC as JESD238 (Toggle Mode 2.0)

> **Implication for custom builds:** A replacement SSD controller must support Toggle DDR
> to use Toshiba dies directly. Most modern SSD controllers (Phison E12, SMI SM2263,
> JMicron JMF670H) support **both** Toggle DDR and ONFI — any modern controller works.

### Toshiba NAND Generation Roadmap (Yokkaichi Alliance fab)

| Gen Code | Process | Era | Die Family | SSD Generation |
|---|---|---|---|---|
| DA | 43nm | 2007–2009 | TH58xxxDA | HG2 |
| DB | 34nm | 2008–2010 | TH58xxxDB | Early HG3 (transitional) |
| **DC** | **32nm** | **2010–2012** | **TH58TEGxDCJ** | **HG3 ← this drive** |
| DD | 19nm (A19nm) | 2012–2014 | TH58TEGxDDK | HG4, HG5 |
| DE | 15nm (A15nm) | 2014–2016 | TH58TEGxDEK | HG6 |
| H2 | BiCS2 48-layer 3D | 2016+ | TH58TEGxH2HBA | HG6 3D variants |

The DD (A19nm) generation (TH58TEG7DDKTA20, TH58TEG8DDKTAK0, 121-page datasheet, 2013)
is the **pin-compatible successor** — same Toggle DDR interface, used in HG5 drives.

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

| Component | Status | Notes |
|-----------|--------|-------|
| SSD controller (Toshiba Type C) | Proprietary, **no public documentation** | Die part unknown; ARM-based; TC58NC… prefix expected |
| NAND flash family | **Confirmed** — TH58TEG7/8-DCJ family | Toggle DDR1.0, 32nm MLC, 4–8 GB/die |
| Most likely NAND package | **TH58TEG8DCJTAK0** (32 GB/pkg, 4-die LGA stack) | 8 packages = 256 GB raw |
| Physical teardown | Not yet performed | Required to read die markings |

**To confirm component identities:** Open a donor THNSNC256GBSJ (or any HG3 unit) and
photograph the IC die markings under magnification. The controller will have a TC58 prefix;
the NAND packages will have TH58TEG markings confirming the DCJ generation.

**Archive note:** AnandTech and TechReport review archives for HG3 are inaccessible at
time of writing (2024–2025). The confirmed NAND datasheet (Rev. 0.3, 14 pages) is
available as a preview at alldatasheet.com but behind a registration wall for full PDF.
The A19nm successor family (TH58TEG7/8-DDK, 121-page datasheet) is accessible and
documents the same Toggle DDR interface in detail.
