# Build 32 — Upgrade package & install-path analysis

**Question this answers:** can we build modified firmware and install it on a real
camera via the normal upgrade flow? **Short answer: not directly — upgrades are
RSA-signed.** A modified payload needs a valid signature (RED's private key) or the
verification must be defeated first (practically: a one-time hardware reflash).

## Upgrade package `redone.su` (CORRECTED)

`redone.su` is a POSIX tar of four parts. The previous guess ("redone.2 = splash,
redone.4 = version manifest") is **wrong** — both are 128 bytes, i.e. RSA-1024
signatures:

| Part | Size (v32.0.3) | Contents | Verified by |
|------|------|----------|-------------|
| `redone.1` | 8.55 MB | `AES-256-CBC( gzip(software.bin) )` | `redone.2` |
| `redone.2` | **128 B** | **RSA-1024 signature** over the software payload | — |
| `redone.3` | 1.62 MB | `AES-256-CBC( gzip(fpga.bin) )` | `redone.4` |
| `redone.4` | **128 B** | **RSA-1024 signature** over the FPGA payload | — |

- AES is **transport obfuscation only**: `aes-256-cbc`, MD5 KDF, password embedded at
  `0xD43140` = `M1H5gwOXh757rIRVY6Gj2tN080AYSX03`. Recoverable → not a real gate.
- `redone.2`/`redone.4` are not AES (no OpenSSL `Salted__` header), 128 bytes =
  1024 bits, high entropy → RSA-1024 signatures (confirmed by the flow strings below).

## Upgrade flow (from the string table at `0xD43100–0xD43400`)

```
Extracting the tarball...            -> /ramFs/su_tmp
Decrypting %s...                     (redone.1, redone.3 ; aes-256-cbc, key @0xD43140)
Decompressing %s to %s...            (gunzip)
Verifying %s's signature...          <-- RSA signature verification
Error reading signature file %s      (redone.2 / redone.4)
Error Verifying Data
... get size of / erase / write flash region '%s' ...
```

So: extract → AES-decrypt → gunzip → **RSA-verify signature** → erase+flash. The
`%s: Bad Signature (%c%c%c%c)` string elsewhere is a separate 4-byte *format magic*
check, not the crypto step.

## How verification works (CONFIRMED — `lib/libflashutils/extract.c`)

The verifier is `lib/libflashutils/extract.c`, `FUN_000a8bdc` (+ the decrypt/verify
driver `FUN_000aa840`), in the upgrade/flash module `0x000a8000–0x000b0000`. Strings
in its cluster (`0xD43000–0xD43100`) spell out the exact scheme:

```
libflashutils/extract.c        (0xD43000 — the source file)
/roFs/WindRiver.pem            (0xD43018 — public key file #1)
/roFs/Red.pem                 (0xD43038 — public key file #2)
Error setting digest md5      (0xD43058 — digest is MD5)
Error opening signature file %s / Error reading signature file %s
Verification Failure
```

So the algorithm is **md5WithRSAEncryption (RSA-1024 + MD5)** via OpenSSL `EVP_Verify*`:

1. SmartUpgrade extracts `redone.su` → `/ramFs/su_tmp` (`redone.1–4`).
2. AES-256-CBC-decrypt `redone.1`/`redone.3` (embedded key), gunzip → software / fpga.
3. Load the RSA-1024 public key (`/roFs/Red.pem`, `/roFs/WindRiver.pem`).
4. `EVP_VerifyInit(md5)` → `EVP_VerifyUpdate(payload)` → `EVP_VerifyFinal(sig, key)`,
   where `sig` is the 128-byte `redone.2` / `redone.4`. "Verifying %s's signature...".
5. Fail → "Verification Failure" / "Error Verifying Data", abort. Pass → erase + write
   the flash region.

**What is signed — EMPIRICALLY CONFIRMED (2026-06-04).** The signature covers the
**fully decrypted *and* decompressed** payload, not the encrypted `redone.1`/`redone.3`
nor the compressed intermediate. Verified with real OpenSSL against the embedded keys:

```
openssl dgst -md5 -verify pub_0x9D29A8.pem -signature redone.2 software.bin  -> Verified OK
openssl dgst -md5 -verify pub_0x9D29A8.pem -signature redone.4 fpga.bin      -> Verified OK
```

So `redone.2 = RSA1024_MD5( software.bin )` and `redone.4 = RSA1024_MD5( fpga.bin )`,
both signed by the **same** key — the one embedded at **`0x9D29A8`** (the other key,
`0x6726F0`, verifies neither; it is a second trust anchor used elsewhere / unused for
upgrades). Both keys are RSA-1024. Consequence: forging acceptance of a *modified*
`software.bin` requires an **MD5 collision against the plaintext image** (Flame-style)
or RED's private key.

**Where the keys live — CONFIRMED.** `Red.pem`/`WindRiver.pem` are **not written at
runtime**. At file offset `0x672560` there is an **`RFS1`** read-only-filesystem image
*embedded inside `software.bin`* whose directory lists `WindRiver.pem`, `Red.pem`,
`gui.swf`, `splash*.gz`, `vpfpga_top.bin.*`, `FactoryDefaults.xml`, … The firmware
mounts this region as **`/roFs`** at boot via `romfsFsLib` (read-only — hence the
name). So the verification keys **ship inside the firmware binary** and travel with
each flashed image; there is no separate provisioning write to intercept. To change
the trusted key you edit the `RFS1`/`0x9D29A8` PEM region of `software.bin` — itself a
carve-out modification that must first be installed (→ reflash for the first image).

**Two weaknesses this exposes (both right-to-repair levers):**
- **MD5.** RSA-over-MD5 is the exact construction the *Flame* malware forged against
  Microsoft code-signing (2012) via a chosen-prefix MD5 collision. A collision lets a
  modified payload match a legitimately-signed MD5 → acceptance **without** the private
  key. Advanced but real.
- **Keys are files on `/roFs`.** If the `/roFs` partition is writable/reflashable,
  replacing `/roFs/Red.pem` (+ `WindRiver.pem`) with **our** public key lets us sign
  upgrades with our key — **no binary patching of the firmware needed**. This is likely
  the cleanest install path if `/roFs` is accessible.

## Crypto: RSA-1024, keys embedded in the image

OpenSSL 0.9.8a (WR Security Libraries) provides the verify stack — present in the
image: `RSA_verify`, `EVP_VerifyFinal`, `RSA_public_decrypt`, `d2i_X509`, `PEM_read`,
`sha1WithRSA`, `md5WithRSA`.

Two **RSA-1024, e=65537** public keys are embedded as PEM text (which is why a raw
DER/`02 03 01 00 01` search misses them — `AQAB` is base64 for the exponent):

- **`0x006726F0`** — code/data region → the **upgrade-verification key** (primary suspect).
- **`0x009D29A8`** — SWF/resources region → second key (FPGA sig, or UI/SSL — TBD).

Full keys are in the binary; key #1:
```
-----BEGIN PUBLIC KEY-----
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDdaUCzCZiYQT6MqxZP3X0lS7H0
0yntCSLZGSmS6ijYgHUFblP11n3QQtw83EXqHM3fx1o2oNqHEW0WyrA4v5wOUawd
ebIhr+6fpyUDZHRIupuAEU4OJ69fDRivIZxAuBXBSWNLHMPO2/BSPHIeVPJ2/rCl
VcX55RMXnuW9arit9QIDAQAB
-----END PUBLIC KEY-----
```

## Implication for installing modified firmware

The `repackage_firmware.sh` recipe ("re-encrypt redone.1, **keep** redone.2/3/4")
produces a package that **fails verification** on a real camera as soon as the
software payload changes — `redone.2` no longer matches the modified software.
That recipe is only valid for *repackaging the unmodified image*.

To install **modified** firmware, one of:

1. **Sign with RED's private key** — unavailable. ✗
2. **Forge an RSA-1024 signature** — factoring 1024-bit RSA is not DIY-feasible
   (public record ≈795–829-bit). Note RED used RSA-1024 (2013); weak by modern
   standards but not a practical individual attack. ✗ for DIY.
3. **Bypass verify in the installed firmware** — but the check runs in the *stock*
   (signed) firmware before our code executes. Chicken-and-egg. ✗ alone.
4. **Hardware reflash (JTAG / NOR programmer at `0xF0000000`)** — write a modified
   image directly, bypassing SmartUpgrade entirely. ✓ robust first-install path.
5. **Embedded-key replacement (the clean right-to-repair design):** once we can write
   firmware (via #4), replace the upgrade public key at `0x006726F0` with **our own**
   RSA-1024 public key (a localized carve-out modification). Then sign future
   `redone.su` upgrades with *our* private key and normal OTA works — we own the
   signing chain. Combine with relaxing/removing the verify as a fallback.
6. **Exploit the verify/extract path** (tar→`/ramFs/su_tmp`, decrypt, ASN.1/RSA) for
   code execution — research path, not relied upon.

**Recommended path:** #4 + #5 — reflash once with a modified image whose embedded
upgrade key is ours (and/or verify relaxed), then sign OTA upgrades ourselves.

## Next steps (to make the install path real)

1. **Pin the verify function:** trace xrefs of `Verifying %s's signature...`
   (`0xD432F8`) and `Error reading signature file %s` (`0xD43104`) — needs
   Ghidra-resolved xrefs (the pure-binary `lis/addi` scanner is unreliable here).
   Determine: hash algo (SHA-1 vs MD5), what is signed (decompressed software vs
   `redone.1`), and which key (`0x6726F0`).
2. **Design the key-swap unit:** the embedded PEM at `0x6726F0` is data, not code —
   overlay our public key there via the relink build (`src/units/`), keeping byte
   length ≤ original (pad the PEM). Verify localized with `make verify-relink`.
3. **Validate empirically (needs hardware + JTAG):**
   - First, prove the round-trip: re-tar the *original* `redone.1–4` unchanged and
     confirm the camera accepts it (sanity: our packaging is correct).
   - Then flash a reflashed modified image and an OTA upgrade signed by our key.

## Cross-build security evolution (when signing was introduced)

`firmware/scripts/build_security_matrix.sh` sweeps every archive in
`firmware/builds/` (run it to reproduce):

| Builds | Versions | Package | Encrypted | Sig files | RSA verify | Pubkeys |
|--------|----------|---------|-----------|-----------|-----------|---------|
| **13, 15** | v1.8.8 – v2.2.5 | `su.tar` | **no** | **no** | **no** | **0** |
| **16 → 32** | v3.2.5 – v32.0.3 | `redone.su` | yes | 2 × 128 B | **yes** | 2 |

- **Signing + encryption were introduced at Build 16 (v3.2.5).** Builds 13 and 15 are
  plain gzipped `su.tar` with no AES, no signatures, and **no OpenSSL/verify stack in
  the firmware at all**. (Corrects the old `analyze_build.py` note "≤16 unencrypted":
  the real boundary is ≤15.)
- **Key reuse:** only **two** distinct RSA-1024 public keys appear across *all* signed
  builds 16→32 (sha256[:16] `5ab5989ca561bcd7`, `867c16beec236b18`) — never rotated in
  ~5 years. So a single embedded-key swap (or key compromise) covers every signed build.
- **No private key is shipped (verified).** Only the two *public* keys are embedded.
  Builds 16→32 do contain the strings `ENCRYPTED PRIVATE KEY` (@0xD6A338) and
  `privateExponent` (@0xD6DF50), but these are OpenSSL **library boilerplate** — the
  PEM type-name table (next to `pem_pkey.c`, `p12_crpt.c`) and `RSA_print` field labels
  (next to `modulus:`, `publicExponent:`). No `BEGIN (RSA )PRIVATE KEY` block exists in
  any build. Builds 13/15 have no crypto at all. So RED's signing key cannot be
  recovered from firmware — it lives only on their build server (as it must).
- **Legacy `su.tar` lead (unverified):** Build 32's `UpgradeMC::SmartUpgrade` still
  emits `"Upgrade file 'su.tar' detected"`. If the signed firmware still *processes* a
  legacy unsigned `su.tar` (vs only the signed `redone.su`), that is a **signature
  bypass** — modified firmware installable unsigned. TODO: trace SmartUpgrade to
  confirm whether the `su.tar` path skips verification or is vestigial GUI text.

Right-to-repair takeaways: Builds 13/15 are freely modifiable but only directly useful
on a camera already running an unsigned build (a signed camera won't downgrade through
the verified path). The high-value leads are the **legacy `su.tar` path** (if live) and
the **embedded-key swap after a hardware reflash**.

## No-reflash install paths (investigated 2026-06-04)

Goal: install modified firmware **without** opening the camera / JTAG. Four candidate
vectors were evaluated:

### ✅ Primary: WDB-over-Ethernet (always-on, unauthenticated) — VIABLE
The strongest finding. `usrWdbInit` (`0x0036B3DC`) is called **unconditionally** from
BSP init (`0x0036B7EC`); no build flag or runtime check disables it (see
`debug_interfaces.md`). The agent links the **full** capability set —
`wdbMemCoreLibInit` (memory read/**write**), `wdbFuncCallLibInit` (**call any
function**), `wdbDirectCallLibInit`. Transport: UDP `192.168.0.2:17185`, **no
authentication** — any host on the subnet gets full control of the live camera.

That is sufficient to install modified firmware with no reflash and no valid signature:

1. **Patch verify in RAM, then upgrade (cleanest).** The upgrade verify result is
   gated through a global error flag: a failed `EVP_VerifyFinal` → the per-file verify
   `FUN_00210800` calls `FUN_0005da9c(result==-1, …)` which sets `*(0x00E9E85C)=1`, and
   the master flow skips the flash. Over WDB, `MEM_WRITE` the verify wrapper
   `FUN_000af634` (`0x000AF634`) to `li r3,0; blr` (`38 60 00 00 4E 80 00 20`) so every
   signature "passes", drop a modified `redone.su` (re-encrypted with the known AES
   key) on a CF card, and run the normal SmartUpgrade. The upgrader does the correct
   flash-region erase/write; your image lands **persistently**. (Flat image → runtime
   addr == file offset, so the patch address is literally `0xAF634`.)
2. **Direct flash write via FUNC_CALL.** `MEM_WRITE` the modified image into a RAM
   buffer, then `WDB_FUNC_CALL` the flash-program routine (`FUN_000adc28` region) to
   write the firmware flash partition directly — no upgrade package at all.
3. **Enable the shell.** Set `DEBUG.USB.CONNECTION=1` (or `FUNC_CALL runTargetShell`)
   → VxWorks shell over USB CDC-ACM → write flash interactively.

Status: `firmware/scripts/wdb_probe.py` already implements `MEM_READ` + a gated
`MEM_WRITE` (framing validated); it just needs to be run against the camera on the
`192.168.0.2` subnet, then `MEM_WRITE` confirmed live before attempting (1).

### ✅ Secondary: enrolling our own key (after any one install)
Once a modified image is installed by any path above, replace the embedded `RFS1`
`/roFs` public key (`0x9D29A8`) with **ours** and remove the verify patch — future OTA
`redone.su` upgrades then require *our* signature, no WDB needed thereafter.

### ◻︎ MD5 collision — theoretically possible, impractical for an individual
The signature is RSA-1024 over **MD5 of the plaintext image** (confirmed above), so a
*chosen-prefix MD5 collision* between RED's legitimately-signed image and a modified
one would forge acceptance with no key and no WDB (the Flame technique). Real, but the
compute cost puts it out of individual reach; listed for completeness.

### ✗ Legacy `su.tar` bypass — DEAD END
Build 32's `UpgradeMC::SmartUpgrade` still prints `Upgrade file 'su.tar' detected`, but
that is **legacy GUI log text only**: there are zero `/upgrade/su.tar` path strings —
the firmware searches exclusively for `redone.su` (`/upgrade/redone.su` ×5). No
unsigned legacy code path exists.

**Bottom line:** the practical no-reflash route is **WDB over Ethernet → patch the
in-RAM verify → normal upgrade** (or `FUNC_CALL` the flasher directly). The signature
scheme is moot once you have unauthenticated WDB memory-write to the running camera.

## Components on disk
Original `redone.su` is at `firmware/reverse/build_32/build_32_v32.0.3/upgrade/redone.su`
(and `firmware/builds/build_32_v32.0.3.zip`). Extract `redone.1–4` from it for any
packaging work; `redone.1` decrypts+gunzips to `software.bin` (SHA `416e148c…`),
confirming key + format.
