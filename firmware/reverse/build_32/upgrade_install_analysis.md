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
- **Legacy `su.tar` lead (unverified):** Build 32's `UpgradeMC::SmartUpgrade` still
  emits `"Upgrade file 'su.tar' detected"`. If the signed firmware still *processes* a
  legacy unsigned `su.tar` (vs only the signed `redone.su`), that is a **signature
  bypass** — modified firmware installable unsigned. TODO: trace SmartUpgrade to
  confirm whether the `su.tar` path skips verification or is vestigial GUI text.

Right-to-repair takeaways: Builds 13/15 are freely modifiable but only directly useful
on a camera already running an unsigned build (a signed camera won't downgrade through
the verified path). The high-value leads are the **legacy `su.tar` path** (if live) and
the **embedded-key swap after a hardware reflash**.

## Components on disk
Original `redone.su` is at `firmware/reverse/build_32/build_32_v32.0.3/upgrade/redone.su`
(and `firmware/builds/build_32_v32.0.3.zip`). Extract `redone.1–4` from it for any
packaging work; `redone.1` decrypts+gunzips to `software.bin` (SHA `416e148c…`),
confirming key + format.
