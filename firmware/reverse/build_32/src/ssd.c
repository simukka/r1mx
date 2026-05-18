/*
 * ssd.c — DigMag (Digital Magazine) storage driver decompilation
 *
 * RED ONE MX firmware build 32, r1mx reverse engineering project.
 *
 * The RED ONE MX uses the term "Digital Magazine" (DigMag) for all
 * removable storage: RED SSD modules (REDMAG), CompactFlash, RAM modules
 * (RedRAM/RedRAID), and LEXAR CF cards.  Storage is validated by comparing
 * the ATA IDENTIFY model string against a hardcoded approved list before
 * the drive is allowed to be mounted for recording.
 *
 * Source file in binary:  app_modules/digmag/digmagmgr.cpp  (@ 0xD2E720)
 *
 * Key data addresses (confirmed from binary):
 *   0xD2E3E8–0xD2E484  approved model string table (null-terminated, 4-byte aligned)
 *   0xD2E484            drive path "/ata00:1"
 *   0xD2E4F8            drive state enum strings
 *   0xD2E5C0–0xD2E720  revision/version model strings
 *   0xD2E7F0            serial prefix "CP-5723_"
 *   0xD2E7FC            serial suffix "_X_F"
 *
 * Key function addresses:
 *   0x0039AC2C  memcmp (standard)
 *   0x0039ACEC  strncmp (standard)
 *   0x0039B1D4  strncpy (standard)
 *   0x004A6438  VxWorks log (severity, fmt, file, col, line)
 *   0x004AB25C  drive object lookup / type converter
 *   0x004BC2A0  DigMag object getter (reads "MEDIA.DIGMAG.DRIVE?" param)
 *   0x004C9ADC  model string registration wrapper
 *   0x004CA1E0  DigMag_IsApprovedModel — iterates approved string table; called via vtable
 *   0x004B4B80  VxWorks param lookup
 *   0x004B50DC  VxWorks param registration API (tertiary)
 *   0x004B600C  VxWorks param registration API (secondary)
 *   0x004B7BD8  VxWorks param registration API (primary)
 *   0x004D04D0  drive type switch dispatch
 *   0x004D06C4  DigMagDrive::SetType
 *   0x004D1B64  DigMag_IsCompatible(drive_obj) — vtable dispatch to IsApprovedModel
 *                 returns 0 if model not in approved list → drive set INCOMPATIBLE
 *
 * SSD bypass patch sites (see firmware/scripts/patch_firmware.py, phase=3):
 *   Site A  0x005D552C  bl 0x4D1B64 → li r3,1   (hotplug/mount handler)
 *   Site B  0x005D58E8  bl 0x4D1B64 → li r3,1   (state re-validate)
 *   Both sites: replacing bl with li r3,1 makes IsCompatible appear to return
 *   "compatible" unconditionally; the following bne/beq branches then take the
 *   success path instead of storing INCOMPATIBLE (6) to drive->state.
 *
 * Decompilation methodology:
 *   Ghidra 12.0.4, PPC405BE, base 0x0; cross-ref against VxWorks param DB
 *   conventions and Xilinx BSP driver patterns.
 *
 * ATA IDENTIFY fields:
 *   Words 27–46 (bytes 54–93):  model number, 40 bytes, space-padded,
 *                                byte-swapped within each 16-bit word (ATA spec).
 *   Words 10–19 (bytes 20–39):  serial number, 20 bytes, space-padded,
 *                                byte-swapped within each 16-bit word.
 *   The firmware byte-swaps before comparison (see ata_fixup_string below).
 *
 * Compiler: g++-powerpc-linux-gnu -mcpu=405 -mbig-endian -O2 -std=c++03
 *           -ffreestanding -nostdlib -fno-stack-protector -fno-pic -fno-rtti
 */

#include <stdint.h>
#include <string.h>     /* strncmp, strncpy (from VxWorks libc) */

/* -------------------------------------------------------------------------
 * Drive state enumeration
 * Strings for each state are registered in the VxWorks parameter database.
 * String table at 0xD2E4F8 (confirmed from binary):
 *   DRIVE0, NOTPRESENT, PRESENT, EJECTED, EXPORTED, NOTMOUNTED,
 *   UNCONFIGURED, INCOMPATIBLE, MOUNTED, UNMOUNTED
 * ------------------------------------------------------------------------- */
typedef enum {
    DRIVE_STATE_NOTPRESENT    = 0,
    DRIVE_STATE_PRESENT       = 1,
    DRIVE_STATE_EJECTED       = 2,
    DRIVE_STATE_EXPORTED      = 3,
    DRIVE_STATE_NOTMOUNTED    = 4,
    DRIVE_STATE_UNCONFIGURED  = 5,
    DRIVE_STATE_INCOMPATIBLE  = 6,
    DRIVE_STATE_MOUNTED       = 7,
    DRIVE_STATE_UNMOUNTED     = 8,
} DriveState;

/* -------------------------------------------------------------------------
 * Drive type codes (from 0x4D04D0 switch dispatch)
 * Valid range: 21–26.  Type < 21 or > 26 → error in 0x4D04D0.
 * Callers pass specific types:
 *   Type 22 @ 0x5D1CF4 (li r4, 22)  — likely SSD module
 *   Type 23 @ 0x5D2700 (li r4, 23)  — likely CF card
 *   Type 26 @ 0x4CF768 (li r4, 26)  — likely RAM module
 * ------------------------------------------------------------------------- */
typedef enum {
    DRIVE_TYPE_RAM       = 21,   /* RedRAM / RedRAID */
    DRIVE_TYPE_SSD_MOD   = 22,   /* REDMAG SSD module (iVDR) */
    DRIVE_TYPE_CF        = 23,   /* CompactFlash card */
    DRIVE_TYPE_UNKNOWN24 = 24,
    DRIVE_TYPE_UNKNOWN25 = 25,
    DRIVE_TYPE_RAMRAID   = 26,   /* RedRAID (multi-module) */
} DriveTypeCode;

/* -------------------------------------------------------------------------
 * Approved ATA IDENTIFY model strings
 *
 * Address: 0xD2E3E8–0xD2E484 in software.bin
 * Format: null-terminated, 4-byte aligned.
 * These are compared against the ATA model string (words 27–46, 40 bytes)
 * AFTER byte-swapping within each 16-bit word.
 *
 * NOTE: The drive reports e.g. "RED 64GB SSD " (with trailing space)
 * padded to 40 characters. The firmware uses strncmp with n = 14 (or similar)
 * so only the prefix needs to match.
 * ------------------------------------------------------------------------- */
static const char * const kApprovedModels[] = {
    /* 0xD2E3E8 */ "RedRAM",             /* RED RAM module (RedRAM)             */
    /* 0xD2E3F0 */ "RedRAID",            /* RED RAID module (RedRAID)           */
    /* 0xD2E3F8 */ "LEXAR ATA FLASH CARD", /* Lexar CF cards (approved OEM)    */
    /* 0xD2E410 */ "RED 16GB CF",        /* RED-branded 16 GB CompactFlash      */
    /* 0xD2E41C */ "RED 32GB CF",        /* RED-branded 32 GB CompactFlash      */
    /* 0xD2E428 */ "RED 64GB CF",        /* RED-branded 64 GB CompactFlash      */
    /* 0xD2E434 */ "RED 55GB SSD ",      /* REDMAG 55 GB (v1/v2)               */
    /* 0xD2E444 */ "RED 64GB SSD ",      /* REDMAG 64 GB                        */
    /* 0xD2E454 */ "RED 128GB SSD ",     /* REDMAG 128 GB (v1/v2/v3)           */
    /* 0xD2E464 */ "RED 256GB SSD ",     /* REDMAG 256 GB (v1/v2/v3)           */
    /* 0xD2E474 */ "RED 512GB SSD ",     /* REDMAG 512 GB (v1/v2/v3/v4)        */
    0,
};

#define NUM_APPROVED_MODELS  11
#define MODEL_STR_COMPARE_LEN  40   /* ATA IDENTIFY model field width          */

/* -------------------------------------------------------------------------
 * Serial number format strings (at 0xD2E7F0/0xD2E7FC)
 *
 * RED SSD serial numbers follow the pattern:
 *   CP-5723_XXXXXXXX_X_F
 * where X = hex digit.  The prefix "CP-5723_" is at 0xD2E7F0 and the
 * suffix "_X_F" is at 0xD2E7FC.
 *
 * ATA IDENTIFY words 10–19 (bytes 20–39) hold the 20-byte serial number,
 * also byte-swapped within each 16-bit word.
 * ------------------------------------------------------------------------- */
static const char kSerialPrefix[] = "CP-5723_";   /* 0xD2E7F0 */
static const char kSerialSuffix[] = "_X_F";       /* 0xD2E7FC */

/* -------------------------------------------------------------------------
 * Revision/version model strings (0xD2E5C0–0xD2E720)
 * These are the human-readable names registered in the VxWorks param DB.
 * The digmag module picks the matching rev-string when reporting drive type.
 *
 *   "RED 16GB REV B"     "RED 32GB REV A1"   "RED 64GB REV B"
 *   "RED 55GB V1"        "RED 55GB V2"
 *   "RED 128GB V1"       "RED 128GB V2"       "RED 128GB V3"
 *   "RED 256GB V1"       "RED 256GB V2"       "RED 256GB V3"
 *   "RED 512GB V1"       "RED 512GB V2"       "RED 512GB V3"  "RED 512GB V4"
 *   "External Disk 0"
 * ------------------------------------------------------------------------- */

/* -------------------------------------------------------------------------
 * Drive path constant (at 0xD2E484)
 * VxWorks ATA driver mounts the SSD module as "/ata00:1"
 * ------------------------------------------------------------------------- */
static const char kDrivePath[] = "/ata00:1";   /* 0xD2E484 */

/* -------------------------------------------------------------------------
 * VxWorks parameter API (forward declarations)
 * These are the VxWorks param-database functions called from digmag module.
 * All four flavours appear in the registration stubs:
 *   0x4B7BD8 — register with default and range
 *   0x4B600C — register enumeration value
 *   0x4B4B80 — lookup parameter by path string
 *   0x4B50DC — register notification callback
 * ------------------------------------------------------------------------- */
extern int  vxw_param_register_default(const char *path, const char *value,
                                       const char *range);  /* 0x4B7BD8 */
extern int  vxw_param_set_enum(const char *path, const char *value);         /* 0x4B600C */
extern void *vxw_param_lookup(const char *path);                             /* 0x4B4B80 */
extern int  vxw_param_register_cb(const char *path, void *cb, void *ref);   /* 0x4B50DC */

/* -------------------------------------------------------------------------
 * DigMag drive object (partial reconstruction)
 *
 * Ghidra identifies these field offsets from indirect reads in digmag code.
 * The object is heap-allocated; a global pointer to the current drive object
 * lives at the VxWorks param "MEDIA.DIGMAG.DRIVE?" (path accessed via
 * 0x4BC2A0 → 0xD2C4D4).
 * ------------------------------------------------------------------------- */
typedef struct DigMagDrive {
    uint32_t  TypeCode;       /* +0x00  DriveTypeCode enum value         */
    uint32_t  Flags;          /* +0x04  status/error flags               */
    DriveState State;         /* +0x08  current drive state              */
    char      ModelStr[40];   /* +0x0C  ATA model string (byte-swapped)  */
    char      SerialStr[20];  /* +0x34  ATA serial number (byte-swapped) */
    char      FirmwareRev[8]; /* +0x48  ATA firmware revision            */
    uint64_t  CapacityBytes;  /* +0x50  reported capacity                */
    uint32_t  WriteSpeedKBs;  /* +0x58  max write speed (KB/s)           */
    void     *VxWksHandle;    /* +0x5C  VxWorks ATA device handle        */
    /* ... additional fields not yet recovered ... */
} DigMagDrive;

/* -------------------------------------------------------------------------
 * ata_fixup_string
 *
 * ATA IDENTIFY strings are encoded with bytes swapped within each 16-bit
 * word (ATA spec — big-endian hardware effect).  This function swaps them
 * back to readable ASCII in-place, then trims trailing spaces.
 *
 * The firmware performs this operation on both the model string (40 bytes)
 * and the serial number string (20 bytes) before any comparison.
 * ------------------------------------------------------------------------- */
static void ata_fixup_string(char *buf, int len)
{
    int i;
    /* Swap bytes within each 16-bit word */
    for (i = 0; i + 1 < len; i += 2) {
        char tmp  = buf[i];
        buf[i]    = buf[i + 1];
        buf[i + 1] = tmp;
    }
    /* Trim trailing spaces (ATA pads with 0x20) */
    for (i = len - 1; i >= 0 && buf[i] == ' '; i--)
        buf[i] = '\0';
}

/* -------------------------------------------------------------------------
 * DigMag_IsApprovedModel  (reconstructed from strncmp call pattern)
 *
 * Tests whether the ATA model string in `model` (after byte-swap fixup)
 * matches any entry in the approved list.
 *
 * The firmware iterates the kApprovedModels table and calls strncmp with
 * n = strlen(approved_entry) for each entry.  If any matches, the drive
 * is approved (returns 1).  Otherwise returns 0.
 *
 * Called from the drive enumeration path in digmagmgr.cpp when a new drive
 * is detected (DRIVE_STATE_PRESENT → validation → DRIVE_STATE_MOUNTED or
 * DRIVE_STATE_INCOMPATIBLE).
 *
 * NOTE: The exact function address is not confirmed — the strncmp callers
 * at 0x4AE3C8 (n=16), 0x4AE758 (n=16), and 0x4AEAA8 (n=140) are
 * candidates.  This implementation matches the pattern described in
 * ssd_validation_analysis.md.
 * ------------------------------------------------------------------------- */
static int DigMag_IsApprovedModel(const char *model)
{
    const char * const *p;
    for (p = kApprovedModels; *p != 0; p++) {
        int n = 0;
        /* strlen equivalent for the approved entry */
        while ((*p)[n] != '\0')
            n++;
        if (n == 0)
            continue;
        if (strncmp(model, *p, n) == 0)
            return 1;
    }
    return 0;
}

/* -------------------------------------------------------------------------
 * DigMag_IsApprovedSerial  (reconstructed from serial format analysis)
 *
 * Tests whether the ATA serial number in `serial` (after byte-swap fixup)
 * matches the RED serial format: "CP-5723_XXXXXXXX_X_F" where X = hex.
 *
 * The firmware compares:
 *   - first 8 chars against "CP-5723_" (prefix)
 *   - chars 17..20 against "_X_F" suffix (where X = 1 hex char + '_' + 'F')
 *
 * Serial number is read from ATA IDENTIFY words 10–19 (20 bytes, swapped).
 * Confirmed string addresses: prefix @ 0xD2E7F0, suffix @ 0xD2E7FC.
 * ------------------------------------------------------------------------- */
static int DigMag_IsApprovedSerial(const char *serial)
{
    if (strncmp(serial, kSerialPrefix, 8) != 0)
        return 0;
    /* Suffix starts at offset 16 (after "CP-5723_XXXXXXXX") */
    if (strncmp(serial + 16, kSerialSuffix, 4) != 0)
        return 0;
    return 1;
}

/* -------------------------------------------------------------------------
 * DigMagDrive_Validate
 *
 * Main entry point for drive validation.  Called when a new drive is
 * detected (ATA hotplug interrupt or polling).  Reads model + serial from
 * the ATA IDENTIFY data, applies byte-swap fixup, then:
 *   - If model is approved AND serial format is correct → MOUNTED
 *   - Otherwise → INCOMPATIBLE
 *
 * The function then updates the VxWorks parameter database with the new
 * state string so the UI (Scaleform SWF) can display the correct icon.
 *
 * VxWorks param paths used:
 *   "MEDIA.DIGMAG.DRIVE?"  — handle to current drive object
 *   "MEDIA.DIGMAG.STATE"   — current state string
 *   "MEDIA.DIGMAG.MODEL"   — model string (for display)
 * ------------------------------------------------------------------------- */
void DigMagDrive_Validate(DigMagDrive *drive,
                          const char  *ata_model_raw,   /* 40 bytes, ATA-swapped */
                          const char  *ata_serial_raw)  /* 20 bytes, ATA-swapped */
{
    char model[41];
    char serial[21];

    /* Copy and fix byte order */
    strncpy(model, ata_model_raw, 40);
    model[40] = '\0';
    ata_fixup_string(model, 40);

    strncpy(serial, ata_serial_raw, 20);
    serial[20] = '\0';
    ata_fixup_string(serial, 20);

    /* Store in drive object */
    strncpy(drive->ModelStr,  model,  40);
    strncpy(drive->SerialStr, serial, 20);

    /* Validate against approved lists */
    if (DigMag_IsApprovedModel(model) && DigMag_IsApprovedSerial(serial)) {
        drive->State = DRIVE_STATE_MOUNTED;
    } else {
        drive->State = DRIVE_STATE_INCOMPATIBLE;
    }
}

/* -------------------------------------------------------------------------
 * DigMagDrive_GetState  (trivial accessor, inlined in Ghidra output)
 * ------------------------------------------------------------------------- */
static DriveState DigMagDrive_GetState(const DigMagDrive *drive)
{
    return drive->State;
}

/* -------------------------------------------------------------------------
 * DigMagDrive_SetState  (wrapper around VxWorks param update)
 * Called from multiple places in digmagmgr.cpp to transition state.
 * ------------------------------------------------------------------------- */
static void DigMagDrive_SetState(DigMagDrive *drive, DriveState new_state)
{
    static const char * const state_strings[] = {
        /* Strings from 0xD2E4F8, in enum order */
        "NOTPRESENT", "PRESENT", "EJECTED",  "EXPORTED",
        "NOTMOUNTED", "UNCONFIGURED", "INCOMPATIBLE", "MOUNTED", "UNMOUNTED",
    };
    drive->State = new_state;
    if ((unsigned)new_state < 9) {
        vxw_param_set_enum("MEDIA.DIGMAG.STATE", state_strings[new_state]);
    }
}

/* -------------------------------------------------------------------------
 * DigMag_RegisterParams
 *
 * Called during module initialization to register all DigMag parameter
 * paths in the VxWorks parameter database.  Each of the 11 model strings,
 * 9 state strings, serial format strings, and version strings gets a param
 * registration call using the pattern:
 *
 *   bl 0x4B7BD8  (vxw_param_register_default)
 *   bl 0x4B600C  (vxw_param_set_enum)
 *   bl 0x4B4B80  (vxw_param_lookup)
 *   bl 0x4B50DC  (vxw_param_register_cb)
 *
 * This function corresponds to the cluster of tiny registration stubs
 * in 0x4BBFC8–0x4DD2E0, each consisting of 4 bl instructions to the
 * VxWorks param API with a pointer to one of the model/state strings.
 *
 * Confirmed by: all `lis r?, 0x00D3; addi r?, r?, <offset>` pairs
 * in the digmag module (0x4A0000–0x4E0000) resolve to 0xD2E3EC–0xD2E7F4.
 * ------------------------------------------------------------------------- */
void DigMag_RegisterParams(void)
{
    int i;
    /* Register approved model strings */
    for (i = 0; i < NUM_APPROVED_MODELS && kApprovedModels[i]; i++) {
        vxw_param_register_default("MEDIA.DIGMAG.MODEL", kApprovedModels[i], 0);
        vxw_param_set_enum("MEDIA.DIGMAG.MODEL", kApprovedModels[i]);
        vxw_param_lookup("MEDIA.DIGMAG.MODEL");
        vxw_param_register_cb("MEDIA.DIGMAG.MODEL", 0, 0);
    }

    /* Register serial format strings */
    vxw_param_register_default("MEDIA.DIGMAG.SERIAL.PREFIX", kSerialPrefix, 0);
    vxw_param_set_enum("MEDIA.DIGMAG.SERIAL.PREFIX", kSerialPrefix);
    vxw_param_lookup("MEDIA.DIGMAG.SERIAL.PREFIX");
    vxw_param_register_cb("MEDIA.DIGMAG.SERIAL.PREFIX", 0, 0);
}

/* -------------------------------------------------------------------------
 * DigMag_GetDriveObject  (wrapper — function at 0x4BC2A0)
 *
 * Looks up the current DigMag drive handle from the VxWorks parameter
 * database using the path "MEDIA.DIGMAG.DRIVE?" (stored at 0xD2C4D4).
 * Returns a pointer to the current DigMagDrive object, or NULL if no
 * drive is present.
 * ------------------------------------------------------------------------- */
DigMagDrive *DigMag_GetDriveObject(void)
{
    return (DigMagDrive *)vxw_param_lookup("MEDIA.DIGMAG.DRIVE?");
}

/* -------------------------------------------------------------------------
 * DigMag_DriveTypeDispatch  (function at 0x4D04D0)
 *
 * Switch dispatch based on drive type code.  Valid codes: 21–26.
 *
 * The jump table at the binary's link address 0xD2E444 is populated at
 * runtime (BSS/RAM region), not from the file's data segment.  At file
 * offset 0xD2E444 the bytes are ASCII "RED 64GB SSD " — confirming this
 * region is NOT initialized from the file: it is zero-initialized BSS
 * that VxWorks fills with function pointers during module init.
 *
 * Args:
 *   object_ptr   — pointer to the DigMag context object (r3, saved→r31)
 *   drive_type   — DriveTypeCode enum value (r4, saved→r29)
 *
 * Drive type → handler mapping (from callers and type analysis):
 *   21  → RAM module handler
 *   22  → SSD module handler       (caller: 0x5D1CF4, li r4, 22)
 *   23  → CF card handler          (caller: 0x5D2700, li r4, 23)
 *   24  → (unknown)
 *   25  → (unknown)
 *   26  → RAID module handler      (caller: 0x4CF768, li r4, 26)
 *   other → error / returns 0 via log at 0x4D06A0
 * ------------------------------------------------------------------------- */
int DigMag_DriveTypeDispatch(void *object_ptr, int drive_type)
{
    typedef int (*dispatch_fn)(void *, int);
    extern dispatch_fn _digmag_dispatch_table[];  /* BSS, populated at init */

    int idx = drive_type - 21;
    if ((unsigned)idx > 5)
        return 0;   /* error: unknown drive type */

    return _digmag_dispatch_table[idx](object_ptr, drive_type);
}

/* -------------------------------------------------------------------------
 * PATCH NOTE — SSD Compatibility Bypass
 *
 * The model validation chain is:
 *   Drive mount handler (0x5D5574)
 *     → bl 0x4D1B64  DigMag_IsCompatible(drive)   [Site A: 0x5D552C]
 *       → deref drive vtable → vtable[+24]
 *       → call 0x4CA1E0  DigMag_IsApprovedModel
 *         → iterate table at 0xD2E3E8–0xD2E484
 *         → memcmp each entry; return 1 if match, 0 if no match
 *     ← mr. r28,r3 + bne 0x5D5454  ← if 0: fall to INCOMPATIBLE store
 *   State re-validate (0x5D5A64)
 *     → bl 0x4D1B64  DigMag_IsCompatible(drive)   [Site B: 0x5D58E8]
 *     ← mr. r26,r3 + beq 0x5D5A28  ← if 0: jump to INCOMPATIBLE store
 *
 * Confirmed firmware patch (see firmware/scripts/patch_firmware.py, phase=3):
 *
 * Option A — Firmware patch (CONFIRMED, implemented):
 *   Site A  0x005D552C:  4B EF C6 39  bl 0x4D1B64  →  38 60 00 01  li r3,1
 *   Site B  0x005D58E8:  4B EF C2 7D  bl 0x4D1B64  →  38 60 00 01  li r3,1
 *   Effect: IsCompatible always appears to return 1 (compatible).
 *           bne/beq branches take the success path; INCOMPATIBLE never stored.
 *
 * Option B — SSD spoofing (program ATA IDENTIFY strings):
 *   The SSD must report via ATA IDENTIFY DEVICE (command 0xEC):
 *     Model string (words 27–46, 40 bytes, space-padded, byte-swapped):
 *       "RED 64GB SSD              " (or any other approved string, padded to 40)
 *     Serial number (words 10–19, 20 bytes, space-padded, byte-swapped):
 *       "CP-5723_XXXXXXXX_X_F    " (where X = any hex char)
 *   ATA byte-swap: each pair of bytes is swapped, so "RE" is stored as "ER".
 *
 * Confirmed from binary: the approved model strings at 0xD2E3E8–0xD2E484
 * and serial format at 0xD2E7F0/0xD2E7FC are the sole whitelist entries.
 * No cryptographic signing or capacity matching is performed.
 * ------------------------------------------------------------------------- */
