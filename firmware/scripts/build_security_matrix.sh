#!/usr/bin/env bash
# build_security_matrix.sh — map upgrade encryption/signature across RED build archives.
#
# For every firmware/builds/*.zip: unpack the upgrade tar (su.tar legacy / redone.su),
# classify the package (plain vs AES-encrypted), detect 128-byte RSA signature files,
# decrypt the software payload, and probe it for the RSA-verify stack + embedded
# public keys. Prints a per-build matrix and the distinct signing keys seen.
#
# Finding (2026-06-04): signing+encryption were introduced at Build 16 (v3.2.5);
# Builds 13/15 are plain & unsigned. The same two RSA-1024 keys are reused 16->32.
# See firmware/reverse/build_32/upgrade_install_analysis.md.
#
# Usage: firmware/scripts/build_security_matrix.sh
set -u
PASS='M1H5gwOXh757rIRVY6Gj2tN080AYSX03'   # public AES key (obfuscation only)
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
BUILDS="$REPO/firmware/builds"

printf "%-28s %-10s %-9s %-9s %-7s %s\n" "archive" "pkg" "encrypted" "sigfiles" "verify" "pubkeys"
printf '%.0s-' {1..80}; echo
declare -A KEYS
for z in "$BUILDS"/*.zip; do
  W=$(mktemp -d); unzip -oq "$z" -d "$W" 2>/dev/null
  TAR=$(find "$W" -type f \( -iname 'su.tar' -o -iname 'redone.su' -o -iname '*.su' \) ! -path '*__MACOSX*' | head -1)
  [ -z "$TAR" ] && { printf "%-28s %s\n" "$(basename "$z")" "(no upgrade tar)"; rm -rf "$W"; continue; }
  EX="$W/ex"; mkdir -p "$EX"; tar xf "$TAR" -C "$EX" 2>/dev/null
  enc="no"; sigfiles="no"; sw=""
  if ls "$EX"/redone.1 >/dev/null 2>&1; then
    enc="yes"
    nsig=$(find "$EX" -type f -size 128c | wc -l); [ "$nsig" -gt 0 ] && sigfiles="${nsig}x128B"
    openssl enc -d -aes-256-cbc -md md5 -pass "pass:$PASS" -in "$EX"/redone.1 2>/dev/null | gunzip 2>/dev/null > "$W/sw.bin"
    sw="$W/sw.bin"
  else
    big=$(ls -S "$EX"/*.gz 2>/dev/null | head -1)
    [ -n "$big" ] && { gunzip -c "$big" 2>/dev/null > "$W/sw.bin"; sw="$W/sw.bin"; }
  fi
  verify="no"; pubkeys="-"
  if [ -s "$sw" ]; then
    { grep -qaF "RSA_verify" "$sw" || grep -qaF "Verifying %s's signature" "$sw"; } && verify="YES"
    pubkeys=$(grep -caF "BEGIN PUBLIC KEY" "$sw")
    # record distinct keys
    while IFS= read -r kh; do KEYS[$kh]=1; done < <(python3 - "$sw" <<'PY'
import sys,re,hashlib
d=open(sys.argv[1],'rb').read()
for m in re.finditer(rb"-----BEGIN PUBLIC KEY-----.*?-----END PUBLIC KEY-----", d, re.S):
    print(hashlib.sha256(m.group().replace(b"\r",b"")).hexdigest()[:16])
PY
)
  else
    [ "$enc" = "yes" ] && verify="?(decrypt)"
  fi
  printf "%-28s %-10s %-9s %-9s %-7s %s\n" "$(basename "$z")" "$(basename "$TAR")" "$enc" "$sigfiles" "$verify" "$pubkeys"
  rm -rf "$W"
done
echo
echo "Distinct signing public keys seen across all builds:"
for k in "${!KEYS[@]}"; do echo "  sha256[:16]=$k"; done
