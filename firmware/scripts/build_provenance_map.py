#!/usr/bin/env python3
"""build_provenance_map.py — classify firmware functions by provenance (confidence-tiered).

Goal: scope the decompilation. Partition the 10,554 Ghidra-identified functions of
build_32 software.bin into {vxworks, openssl, xilinx, red:<module>, unknown} so we
know which functions are proprietary RED code to lift to C/C++ (the rest stay blob).

This is a STRIPPED, fully-linked flat image (file offset == runtime address, base 0x0)
with no symbol table, GOT/TOC, or SDA base — so exhaustive automatic attribution is a
hard problem. We therefore emit a CONFIDENCE-TIERED map and label what we cannot pin
down as `unknown` (honest) rather than guessing.

Signals (recorded with confidence):
  high  source-path xref : code materializes a __FILE__ source-path string address
  high  named-symbol     : Ghidra-named libc/VxWorks routine (memset, strncmp, ...)
  high  region-openssl   : inside the WR-Security/OpenSSL block (cross-checked by strings)
  med   string-flavor    : dominant "flavor" of all strings the function references
  med   callgraph         : provenance shared by (almost) all callers
  low   region            : coarse address-range fallback (kernel / BSP tail)
  -     unknown           : not attributable yet (reconstruction/triage candidates)

Outputs: src/manifest.json, src/manifest.csv, and a printed summary.
"""
from __future__ import annotations
import struct, re, json, csv, bisect
from pathlib import Path
from collections import defaultdict, Counter

REPO = Path("/home/simukka/src/RED/r1mx")
BIN  = REPO / "firmware/reverse/build_32/extracted/software.bin"
FUNCS_DIR = REPO / "firmware/reverse/build_32/src/all_functions"
OUT_JSON  = REPO / "firmware/reverse/build_32/src/manifest.json"
OUT_CSV   = REPO / "firmware/reverse/build_32/src/manifest.csv"

data = BIN.read_bytes(); N = len(data)
def u32(o): return struct.unpack_from(">I", data, o)[0]

CONF = {"source-path": 3, "named-symbol": 3, "region-openssl": 3,
        "string-flavor": 2, "callgraph": 2, "region": 1, "unknown": 0}

# --- 1. function table -------------------------------------------------------
HDR = re.compile(r"address=0x([0-9a-fA-F]+)\s+name=(\S+)\s+size=(\d+)\s+xrefs=(\d+)")
funcs = {}
for p in FUNCS_DIR.glob("0x*.c"):
    m = HDR.search(p.read_text(errors="replace")[:400])
    if not m: continue
    a = int(m.group(1), 16)
    funcs[a] = {"addr": a, "name": m.group(2), "size": int(m.group(3)),
                "xrefs": int(m.group(4)), "provenance": None, "module": None,
                "method": "unknown"}
print(f"[1] parsed {len(funcs)} functions")
faddrs = sorted(funcs)
def fn_of(addr):
    i = bisect.bisect_right(faddrs, addr) - 1
    if i < 0: return None
    s = faddrs[i]
    return s if s <= addr < s + max(funcs[s]["size"], 4) else None

# --- 2. classify every embedded string: source-path -> (prov,module); else flavor
STR = re.compile(rb"[ -~]{4,}")
def classify_path(s):
    if s.startswith("C:/WindRiver") or "/vxworks-" in s: return ("vxworks", None)
    if "xsrc/x" in s or "/ppc405_0_drv_csp/" in s:
        return ("xilinx", re.sub(r".*/", "", s))
    if re.match(r"(app_modules|lib|drivers|apps)/\S+\.(c|cpp|cxx|h)$", s):
        return ("red", "/".join(s.split("/")[:2]))
    if re.match(r"(v3_|a_|asn1|x509|evp_|bn_|rsa_|pem_|obj_|conf|by_)\w*\.(c|h)$", s):
        return ("openssl", None)
    return None

OSSL_KW = ("X509", "x509", "ASN1", "OpenSSL", "Wind River Security", "PKCS",
           "CRLDistribution", "POLICY_MAPPING", "RSA", "BIGNUM", "EVP_", "->ASN")
VXW_KW  = ("taskLib", "semTake", "semGive", "msgQ", "vxWorks", "WIND", "tyCo",
           "intLib", "/tyCo/", "kernelInit", "usrRoot", "VXWORKS", "wdbDbg",
           "memPartLib", "smObjLib", "%s : %d", "EDR")
RED_KW  = ("SYSTEM.", "UPGRADE.", "SENSOR.", "DEBUG.", "GNCamera", "DigMag",
           "RED ", "REDMAG", "Sundance", "FLUT", "redone", "OSD::", "::SmartUpgrade",
           "Histogram", "Waveform", "vpimgproc", "ParamMgr", "MasterModule")
def flavor(s):
    if any(k in s for k in OSSL_KW): return "openssl"
    if any(k in s for k in RED_KW):  return "red"
    if any(k in s for k in VXW_KW):  return "vxworks"
    return None

pathstr = {}    # addr -> (prov, module, text)
flavstr = {}    # addr -> (flavor, text)
for m in STR.finditer(data):
    try: s = m.group().decode("ascii")
    except Exception: continue
    c = classify_path(s)
    if c: pathstr[m.start()] = (c[0], c[1], s); continue
    fv = flavor(s)
    if fv: flavstr[m.start()] = (fv, s)
print(f"[2] {len(pathstr)} source-path strings; {len(flavstr)} flavored strings")

path_starts = sorted(pathstr); flav_starts = sorted(flavstr)
def lookup(addr):
    i = bisect.bisect_right(path_starts, addr) - 1
    if i >= 0:
        s = path_starts[i]
        if s <= addr < s + len(pathstr[s][2]):
            return ("path", pathstr[s][0], pathstr[s][1])
    i = bisect.bisect_right(flav_starts, addr) - 1
    if i >= 0:
        s = flav_starts[i]
        if s <= addr < s + len(flavstr[s][1]):
            return ("flavor", flavstr[s][0], None)
    return None

# --- 3. single pass: derive referenced addresses + bl call-graph -------------
CODE = [(0x000000, 0x700000), (0xE00000, 0xE8BF20)]
callgraph = defaultdict(set)
pathhits = defaultdict(Counter)   # fn -> Counter[(prov,module)]
flavhits = defaultdict(Counter)   # fn -> Counter[flavor]
for a, b in CODE:
    for i in range(a, min(b, N) - 4, 4):
        w = u32(i); op = w >> 26
        if op == 18 and (w & 1):                  # bl
            li = w & 0x03FFFFFC
            if li & 0x02000000: li -= 0x04000000
            cf, tf = fn_of(i), fn_of((i + li) & 0xFFFFFFFF)
            if cf is not None and tf is not None and cf != tf:
                callgraph[cf].add(tf)
            continue
        if op != 15 or ((w >> 16) & 0x1F):         # need lis (addis rA=0)
            continue
        rD = (w >> 21) & 0x1F; hi = w & 0xFFFF
        for j in range(i + 4, min(i + 36, N - 4), 4):
            w2 = u32(j); op2 = w2 >> 26
            if op2 < 14: continue
            if ((w2 >> 16) & 0x1F) != rD:
                if op2 == 15 and ((w2 >> 21) & 0x1F) == rD: break
                continue
            lo = w2 & 0xFFFF
            addr = ((hi << 16) | lo) if op2 == 24 else \
                   ((hi << 16) + (lo - 0x10000 if lo & 0x8000 else lo))
            hit = lookup(addr & 0xFFFFFFFF)
            if hit:
                cf = fn_of(i)
                if cf is not None:
                    if hit[0] == "path": pathhits[cf][(hit[1], hit[2])] += 1
                    else:                flavhits[cf][hit[1]] += 1
            break
print(f"[3] {sum(len(v) for v in callgraph.values())} bl edges; "
      f"{len(pathhits)} fns w/ path-ref, {len(flavhits)} fns w/ flavor-ref")

def setp(fn, prov, mod, meth):
    funcs[fn]["provenance"] = prov; funcs[fn]["module"] = mod; funcs[fn]["method"] = meth

# --- 4a. named-symbol (high) -------------------------------------------------
LIBC = re.compile(r"^(memset|memcpy|memmove|strn?cpy|strn?cmp|strn?cat|strlen|"
                  r"strchr|strstr|sprintf|printf|malloc|free|bzero|bcopy|qsort|"
                  r"atoi|memcmp)$")
for fn, r in funcs.items():
    nm = r["name"]
    if LIBC.match(nm): setp(fn, "vxworks", "libc", "named-symbol")

# --- 4b. source-path xref (high) ---------------------------------------------
for fn, cnt in pathhits.items():
    (prov, mod), _ = cnt.most_common(1)[0]
    setp(fn, prov, mod, "source-path")

# --- 4c. string-flavor (med), only where not already high --------------------
for fn, cnt in flavhits.items():
    if CONF[funcs[fn]["method"]] >= 3: continue
    fv, n = cnt.most_common(1)[0]
    if n >= 2 and n >= 0.6 * sum(cnt.values()):
        setp(fn, fv, None, "string-flavor")

# --- 4d. region-openssl (high) -----------------------------------------------
for fn, r in funcs.items():
    if 0x380000 <= fn < 0x384800 and CONF[r["method"]] < 3:
        setp(fn, "openssl", None, "region-openssl")

# --- 5. callgraph propagation (med) ------------------------------------------
callers = defaultdict(set)
for cf, cs in callgraph.items():
    for tf in cs: callers[tf].add(cf)
for _ in range(8):
    ch = 0
    for fn, r in funcs.items():
        if CONF[r["method"]] >= 2: continue
        # Don't propagate onto shared utilities (high fan-in) or boot/runtime stubs:
        # a widely-called leaf belongs to no single module.
        if r["xrefs"] > 6 or fn < 0x800: continue
        labs = [funcs[c]["provenance"] for c in callers.get(fn, ()) if funcs[c]["provenance"]]
        if len(labs) < 2: continue
        top, nt = Counter(labs).most_common(1)[0]
        if nt >= 0.8 * len(labs):
            mods = {funcs[c]["module"] for c in callers[fn]
                    if funcs[c]["provenance"] == top and funcs[c]["module"]}
            setp(fn, top, (mods.pop() if len(mods) == 1 else None), "callgraph"); ch += 1
    if not ch: break

# --- 6. region fallback (low) ------------------------------------------------
REGIONS = [(0x370000, 0x373000, "vxworks"), (0x5A0000, 0x5C0000, "vxworks"),
           (0xE00000, 0xE8BF20, "xilinx")]
for fn, r in funcs.items():
    if r["method"] != "unknown": continue
    for a, b, prov in REGIONS:
        if a <= fn < b: setp(fn, prov, None, "region"); break

# fidelity overlay from recon_status.py (run in the toolchain container); default raw.
RECON = REPO / "firmware/reverse/build_32/src/recon_status.json"
recon = ({e["name"]: e.get("fidelity", "raw")
          for e in json.loads(RECON.read_text()).get("functions", [])}
         if RECON.exists() else {})
for r in funcs.values():
    r["confidence"] = CONF[r["method"]]
    r["reconstruct"] = (r["provenance"] == "red")
    r["fidelity"] = recon.get(r["name"], "raw")

# --- 7. emit + summary -------------------------------------------------------
recs = [funcs[a] for a in faddrs]
OUT_JSON.write_text(json.dumps(recs, indent=1))
with OUT_CSV.open("w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["addr","name","size","xrefs","provenance","module","method","confidence","reconstruct","fidelity"])
    for r in recs:
        w.writerow([f"0x{r['addr']:08x}", r["name"], r["size"], r["xrefs"],
                    r["provenance"] or "unknown", r["module"] or "", r["method"],
                    r["confidence"], int(r["reconstruct"]), r.get("fidelity","raw")])

def kb(b): return f"{b/1024:8.1f} KB"
print("\n=== provenance (fns / bytes) ===")
bp = defaultdict(lambda: [0, 0])
for r in recs:
    k = r["provenance"] or "unknown"; bp[k][0]+=1; bp[k][1]+=r["size"]
for k in sorted(bp, key=lambda k:-bp[k][1]):
    print(f"  {k:9} {bp[k][0]:6} fns  {kb(bp[k][1])}")
print("\n=== method / confidence ===")
for meth, n in Counter(r["method"] for r in recs).most_common():
    print(f"  {meth:14} {n:6}  (conf {CONF[meth]})")
print("\n=== RED modules (high+med conf only) ===")
mc = Counter(r["module"] for r in recs
             if r["provenance"]=="red" and r["module"] and r["confidence"]>=2)
for mod, n in mc.most_common(30): print(f"  {mod:30} {n:4}")
hi = sum(1 for r in recs if r["confidence"]>=2)
unk = sum(1 for r in recs if r["method"]=="unknown")
print(f"\nattributed (med+high): {hi}/{len(recs)} ({100*hi//len(recs)}%); "
      f"unknown: {unk} ({100*unk//len(recs)}%)")
print(f"wrote {OUT_JSON.name}, {OUT_CSV.name}")
