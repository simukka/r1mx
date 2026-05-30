# Plan: Cross-Reference Build 32 Firmware Against Scaleform GFx SDKs

## Context

`re_reference.md` already concludes "GFx 2.x, exact minor version unrecoverable." We now have actual SDK source archives (2.0.41, 2.1.53, 2.1.57, 3.x, 4.x) which let us do a real API-level comparison against the decompiled firmware symbols to narrow this down — and potentially confirm or refute the 2.x conclusion with hard evidence.

**What we know going in:**
- Firmware uses SWF v7 / ActionScript 2.0 (rules out GFx 3.x+)
- C++ wrapper class `FlashVx` wraps `GFxPlayer`/`GFxMovieView` — flat pre-namespace API
- 100+ `CorePlayer` method symbols survive in the binary (mangled PPC names)
- SDK 2.0 (2.0.41) is fully extracted; 2.1.53 and 2.1.57 are in partial .zip archives
- Key structural difference: 2.1+ split GFxMovieDef.h into a separate GFxLoaderImpl.h

## Implementation Steps

### Step 1 — Extract API method lists from each SDK version

For each available SDK version (2.0.41, 2.1.53, 2.1.57, and one 3.x as negative control):
- Unzip partial archives to a temp dir (or inspect in-place with `unzip -p`)
- Parse `GFxPlayer.h` and `GFxLoader.h` for public method signatures
- Produce a per-version list of: class names, method names, argument counts

Key files to diff across versions:
- `Include/GFxPlayer.h` — `GFxMovieView` method list
- `Include/GFxLoader.h` — `GFxLoader` / `GFxState` hierarchy
- `Include/GTypes.h` — version macros (GFC_FX_MAJOR/MINOR/BUILD_VERSION)
- `Src/GFxPlayer/GFxPlayer.cpp` — if present, internal assert strings that survive in binaries

### Step 2 — Extract firmware symbol list

From `SundanceBootable.patched.bin`:
```bash
# Demangle all C++ symbols
strings firmware/reverse/Upgrade_Build\ 13/Upgrade/SundanceBootable.patched.bin \
  | grep '^_Z' | c++filt | grep -iE "(Flash|GFx|Gfc|CorePlayer|Script)" > /tmp/fw_symbols.txt
```

Also extract printable strings for any surviving assert paths or version literals:
```bash
strings ... | grep -E "GFx|GFC_|Scaleform|gfxplayer" > /tmp/fw_strings.txt
```

### Step 3 — Diff firmware CorePlayer methods against SDK GFxPlayer methods per version

The firmware's `CorePlayer` class is the internal name for `GFxPlayer`. Map:
- `CorePlayer::GetTargetPath` → `GFxMovieView::GetVariable` or `GetTargetPath` depending on version
- `CorePlayer::HandleKeyPress` → `GFxMovieView::HandleEvent(GFxKeyEvent&)`
- `CorePlayer::GetActiveActionScriptPlayer` — check if this method exists in 2.0 vs 2.1 headers

Build a match matrix: for each firmware symbol, which SDK version(s) contain a corresponding method.

### Step 4 — Check version-specific API additions

Known API changes between GFx 2.x minor versions to test:
- **2.0 → 2.1**: Added `GFxValue` class, extended `GFxExternalInterface`, added `GFxTaskManager`
- **2.1.53 → 2.1.57**: Minor bugfix release — check for any added methods in GFxPlayer.h
- Check firmware for presence/absence of `GFxValue`-mapped symbols, `GFxTaskManager`-mapped symbols

If firmware has symbols matching 2.1-only APIs → version is ≥ 2.1.
If firmware lacks 2.1-only APIs → version is 2.0.x.

### Step 5 — Cross-reference 3rdParty library versions

GFx SDK bundles specific 3rdParty library versions that leave their own strings in linked binaries:
- **GFx 2.0.41**: ships zlib 1.2.3, jpeg-6b, libpng (specific versions)
- Later SDKs may ship updated versions

Check firmware binary for zlib/jpeg/libpng version strings and compare against what each SDK version bundles.
```bash
strings firmware/... | grep -iE "(zlib|jpeg|libpng|inflate|JFIF)" 
```

### Step 6 — Update re_reference.md

Update section 23.3 ("Scaleform GFx version") with:
- The version determination methodology (SDK comparison approach)
- A confidence-rated conclusion: e.g. "GFx 2.0.41 (high confidence)" or "GFx 2.1.x (medium confidence)"
- The specific evidence that narrows or confirms the version
- A table of SDK versions tested and whether each matches/excludes

## Verification

- The updated re_reference.md section should cite specific firmware symbol names matched to specific SDK header method signatures
- Run the MCP `search_firmware` tool to verify key symbol queries return expected results
- Cross-check against `mcp__r1mx__lookup_function` for any CorePlayer methods to confirm decompilation quality

## Files Modified

- `firmware/reverse/build_32/re_reference.md` — update section 23.3 with SDK comparison results

## Files Referenced (read-only)

- `libraries/scaleform-gfx-sdks/GFx SDK 2.0/Include/GFxPlayer.h`
- `libraries/scaleform-gfx-sdks/GFx SDK 2.0/Include/GTypes.h`
- `libraries/scaleform-gfx-sdks/GFx SDK 2.1 (partial).zip`
- `libraries/scaleform-gfx-sdks/GFx SDK 2.1.57 (partial).zip`
- `firmware/reverse/Upgrade_Build 13/Upgrade/SundanceBootable.patched.bin`
- `firmware/reverse/build_32/src/all_functions/` (decompiled CorePlayer symbols)
