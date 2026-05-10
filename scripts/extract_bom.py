#!/usr/bin/env python3
"""
extract_bom.py — PCB Bill of Materials extractor for the r1mx project.

Extracts component reference designators and visible part numbers from
high-resolution PCB photographs. Uses EasyOCR (primary, best accuracy),
Tesseract (fallback, zero-download), or both.

Produces a bom.csv per board and a master bom_master.csv at the repo root.

Usage:
    # Process all boards with EasyOCR (default)
    python scripts/extract_bom.py

    # Single board
    python scripts/extract_bom.py --board cpu_io_board

    # Use Tesseract instead
    python scripts/extract_bom.py --engine tesseract

    # Save preprocessed tiles for debugging
    python scripts/extract_bom.py --board sd_board --debug

    # Minimum confidence for EasyOCR results (0–1, default 0.4)
    python scripts/extract_bom.py --min-confidence 0.5
"""

import argparse
import csv
import logging
import re
import sys
from pathlib import Path
from typing import NamedTuple

import cv2
import numpy as np

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parent.parent
COMPONENTS_DIR = REPO_ROOT / "components"

# Image extensions to process (exclude .RW2 raw files)
IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".JPG", ".PNG"}

# Tile configuration — smaller tiles give more effective zoom for tiny silkscreen text
TILE_SIZE_EASYOCR = 512
TILE_SIZE_TESSERACT = 1024
TILE_OVERLAP = 100

# Minimum tile dimension to bother OCR-ing
MIN_TILE_DIM = 128

# ---------------------------------------------------------------------------
# Reference designator patterns
# ---------------------------------------------------------------------------

# Standard EIA reference designator prefixes
_REF_PREFIXES = (
    r"IC|U|R|C|L|D|Q|T|F|Y|X|SW|J|P|CN|TP|CR|TR|BT|RN|VR|FB|BR|MH|MP|"
    r"DS|LED|M|E|SP|A|K|G|H|S|Z|W|V|N|FD|ZD|TVS|MOV|NTC|PTC"
)

# Matches: U7, R273, C12B, IC3, TP14, RN5, etc.
REF_PATTERN = re.compile(
    rf"\b(?:{_REF_PREFIXES})\d{{1,5}}[A-Z]?\b", re.IGNORECASE
)

# Generic part-number-like strings (4+ chars, mix of letters/digits/hyphens)
PARTNUM_PATTERN = re.compile(r"\b[A-Z0-9][A-Z0-9\-]{3,20}\b")

# Tokens that are clearly noise (pure noise, too generic, or hex addresses)
NOISE_PATTERN = re.compile(r"^(EE+|[0-9A-F]{6,}|[EIOU]{3,}|(.)\2{3,})$", re.IGNORECASE)

# Common English words that slip through as "part numbers" — not exhaustive
# but catches the most frequent false positives from OCR on PCB backgrounds.
_COMMON_WORDS = {
    "ACETATE", "ACTER", "ADIT", "AHEM", "AIRED", "ALATE", "AMAS",
    "AREA", "AERO", "ACRE", "AGES", "AIDE", "AIMS", "AIRS", "ALSO",
    "AMID", "AMOK", "AMPS", "ANTI", "ANTS", "ARCH", "ARCS", "ARMS",
    "ARMY", "ARTS", "ATOM", "ATOP", "AUNT", "AXES", "AXIS", "BACK",
    "BADE", "BAIL", "BAKE", "BALD", "BALE", "BALL", "BAND", "BANE",
    "BANK", "BARE", "BARK", "BARN", "BASE", "BASH", "BASK", "BASS",
    "BATH", "BATS", "BEAD", "BEAM", "BEAN", "BEAR", "BEAT", "BEEN",
    "BELT", "BEST", "BIAS", "BITE", "BITS", "BLOB", "BOND", "BONE",
    "BOOK", "BOOT", "BORE", "BORN", "BOTH", "BUFF", "BULK", "BUMP",
    "BURN", "CALL", "CAME", "CAMP", "CAPS", "CARD", "CARE", "CART",
    "CASE", "CAST", "CAVE", "CELL", "CHIP", "CITE", "CLAD", "CLAM",
    "CLAP", "CLIP", "CODE", "COIL", "COLD", "COME", "COMP", "CONE",
    "COPY", "CORD", "CORE", "COST", "COUP", "CREW", "CROP", "CUBE",
    "DATA", "DATE", "DEAD", "DEAL", "DEAN", "DECK", "DEEP", "DEFT",
    "DESK", "DIAL", "DIES", "DIFF", "DIODE", "DISK", "DIST", "DIVE",
    "DONE", "DOSE", "DOTS", "DOVE", "DOWN", "DRAW", "DRIP", "DROP",
    "DRUM", "DUAL", "DUMP", "DUST", "EACH", "EARL", "EARN", "EAST",
    "EASY", "EDGE", "EMIT", "EPIC", "EVEN", "EVER", "EXIT", "EXPO",
    "FACE", "FACT", "FADE", "FAIL", "FAIR", "FALL", "FAME", "FARE",
    "FAST", "FATE", "FEAT", "FEED", "FEEL", "FEET", "FILE", "FILL",
    "FILM", "FIND", "FINE", "FIRE", "FIRM", "FISH", "FIST", "FLAG",
    "FLAT", "FLAW", "FLIP", "FLOW", "FOAM", "FOLD", "FONT", "FOOD",
    "FORK", "FORM", "FUSE", "GAIN", "GAME", "GATE", "GAVE", "GAZE",
    "GEAR", "GLOW", "GLUE", "GOAL", "GOLD", "GOLF", "GONE", "GOOD",
    "GRAB", "GRID", "GRIP", "GROW", "HALF", "HALL", "HALT", "HAND",
    "HANG", "HARD", "HARM", "HASH", "HEAD", "HEAT", "HELD", "HELP",
    "HIGH", "HINT", "HOME", "HOOK", "HOPE", "HOST", "HOUR", "HULL",
    "IDLE", "INCH", "INTO", "IRON", "ISLE", "ITEM", "JOIN", "JUMP",
    "KEEP", "KEYS", "KICK", "KILL", "KIND", "KING", "KNOT", "LACK",
    "LAKE", "LAMP", "LANE", "LAST", "LATE", "LEAD", "LEAK", "LEAN",
    "LEAP", "LEFT", "LESS", "LIFT", "LIKE", "LIME", "LINE", "LINK",
    "LIST", "LIVE", "LOAD", "LOCK", "LONG", "LOOK", "LOOP", "LOSS",
    "LOST", "LOUD", "LOVE", "LUMP", "MADE", "MAIL", "MAIN", "MAKE",
    "MANY", "MARK", "MASK", "MASS", "MAST", "MATE", "MATH", "MAZE",
    "MEAN", "MEET", "MELT", "MEMO", "MESH", "MILD", "MINE", "MINT",
    "MODE", "MOLE", "MORE", "MOST", "MUCH", "MUST", "NAIL", "NAME",
    "NEAR", "NECK", "NEED", "NEXT", "NICE", "NODE", "NONE", "NORM",
    "NOSE", "NOTE", "NULL", "OPEN", "OPTS", "OVER", "PACK", "PAGE",
    "PAID", "PAIR", "PALM", "PART", "PASS", "PAST", "PATH", "PEAK",
    "PICK", "PILE", "PINS", "PIPE", "PLAN", "PLAY", "PLUG", "PLUS",
    "POLE", "POLL", "POOL", "PORT", "POSE", "PULL", "PUMP", "PURE",
    "PUSH", "RACK", "RAIL", "RAMP", "RANG", "RANK", "RATE", "READ",
    "REAL", "REEF", "RELY", "REPO", "REST", "RISE", "RISK", "ROAD",
    "ROLE", "ROLL", "ROOF", "ROOM", "ROPE", "ROSE", "ROUT", "RULE",
    "RUNS", "SAFE", "SAID", "SAIL", "SALE", "SALT", "SAME", "SAND",
    "SAVE", "SCAN", "SEAL", "SEED", "SELF", "SELL", "SEND", "SETS",
    "SHED", "SHIP", "SHOP", "SHOT", "SHOW", "SIDE", "SIGN", "SINK",
    "SIZE", "SKIP", "SLAB", "SLAG", "SLIP", "SLOT", "SLOW", "SNAP",
    "SOIL", "SOLE", "SOME", "SORT", "SPAN", "SPIN", "SPOT", "SPUR",
    "STAR", "STAY", "STEM", "STEP", "STOP", "STUB", "SUIT", "SWAP",
    "TABS", "TAIL", "TAKE", "TALK", "TALL", "TANK", "TAPE", "TASK",
    "TEST", "TEXT", "THAN", "THAT", "THEM", "THEN", "THIN", "THIS",
    "TICK", "TIDE", "TIED", "TILT", "TIME", "TIPS", "TOLD", "TOLL",
    "TONE", "TOOL", "TOPS", "TOUR", "TOWN", "TRIM", "TRUE", "TUBE",
    "TUNE", "TURN", "TYPE", "UNIT", "UNTO", "UPON", "USED", "USER",
    "VARY", "VAST", "VEIN", "VERY", "VIEW", "VOID", "VOLT", "VOTE",
    "WATT", "WAVE", "WEAR", "WERE", "WHEN", "WIDE", "WIND", "WIRE",
    "WISE", "WITH", "WORD", "WORE", "WORK", "WRAP", "YARD", "YEAR",
    "ZERO", "ZONE",
}

# ---------------------------------------------------------------------------
# Data types
# ---------------------------------------------------------------------------


class BomEntry(NamedTuple):
    board: str
    reference: str
    ref_type: str        # component class inferred from prefix
    source_image: str
    engine: str
    raw_text: str        # full OCR token as found


def ref_type_from_designator(ref: str) -> str:
    """Return a human-readable component class from a reference designator."""
    prefix = re.match(r"^[A-Z]+", ref.upper())
    if not prefix:
        return "Unknown"
    p = prefix.group(0)
    mapping = {
        "R": "Resistor", "RN": "Resistor Network",
        "C": "Capacitor",
        "L": "Inductor", "FB": "Ferrite Bead",
        "D": "Diode", "ZD": "Zener Diode", "LED": "LED",
        "CR": "Diode", "TVS": "TVS Diode",
        "Q": "Transistor", "T": "Transistor", "TR": "Transistor",
        "U": "IC", "IC": "IC",
        "Y": "Crystal/Oscillator", "X": "Crystal/Oscillator",
        "J": "Connector", "P": "Connector", "CN": "Connector",
        "SW": "Switch",
        "F": "Fuse",
        "TP": "Test Point",
        "BT": "Battery",
        "VR": "Voltage Regulator",
        "MOV": "MOV", "NTC": "Thermistor", "PTC": "Thermistor",
    }
    return mapping.get(p, "Component")


# ---------------------------------------------------------------------------
# Image discovery
# ---------------------------------------------------------------------------


def find_board_images(board_dir: Path) -> list[Path]:
    """Return all PCB images in a board folder, excluding datasheets."""
    images = []
    for path in sorted(board_dir.iterdir()):
        if path.is_dir() and path.name == "datasheets":
            continue
        if path.is_file() and path.suffix in IMAGE_EXTS:
            images.append(path)
    return images


# ---------------------------------------------------------------------------
# Image preprocessing
# ---------------------------------------------------------------------------


def preprocess(gray: np.ndarray) -> list[np.ndarray]:
    """
    Return a list of binary variants of the grayscale image suited for OCR.
    PCB silkscreen can be light-on-dark or dark-on-light depending on the
    board and camera exposure, so we try both polarities.
    """
    variants = []

    # Apply CLAHE to boost local contrast
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)

    # Otsu threshold — normal polarity
    _, otsu = cv2.threshold(enhanced, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    variants.append(otsu)

    # Otsu threshold — inverted (catches light silkscreen on dark board)
    _, otsu_inv = cv2.threshold(enhanced, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    variants.append(otsu_inv)

    # Adaptive Gaussian threshold — handles uneven illumination
    adaptive = cv2.adaptiveThreshold(
        enhanced, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 10
    )
    variants.append(adaptive)

    return variants


def tile_image(img: np.ndarray, tile_size: int, overlap: int) -> list[tuple[np.ndarray, int, int]]:
    """Yield (tile, x_offset, y_offset) tuples with overlapping tiles."""
    h, w = img.shape[:2]
    step = tile_size - overlap
    tiles = []
    y = 0
    while y < h:
        x = 0
        while x < w:
            tile = img[y: y + tile_size, x: x + tile_size]
            if tile.shape[0] >= MIN_TILE_DIM and tile.shape[1] >= MIN_TILE_DIM:
                tiles.append((tile, x, y))
            x += step
        y += step
    return tiles


# ---------------------------------------------------------------------------
# OCR engines
# ---------------------------------------------------------------------------

# Shared EasyOCR reader — lazy-initialised once per process
_easyocr_reader = None


def _get_easyocr_reader(gpu: bool = False):
    global _easyocr_reader
    if _easyocr_reader is None:
        import easyocr
        log.info("Initialising EasyOCR (gpu=%s) — first run downloads ~100 MB model", gpu)
        _easyocr_reader = easyocr.Reader(["en"], gpu=gpu, verbose=False)
    return _easyocr_reader


def ocr_with_easyocr(
    tiles: list[tuple[np.ndarray, int, int]],
    min_confidence: float = 0.35,
    gpu: bool = False,
) -> list[str]:
    """
    Run EasyOCR on all tiles and return text tokens above min_confidence.
    EasyOCR handles arbitrary text orientations internally.
    """
    reader = _get_easyocr_reader(gpu=gpu)
    tokens: list[str] = []
    for tile, _x, _y in tiles:
        try:
            results = reader.readtext(tile, detail=1)
        except Exception as exc:
            log.debug("EasyOCR tile error: %s", exc)
            continue
        for _bbox, text, conf in results:
            if conf >= min_confidence and text.strip():
                tokens.append(text.strip())
    return tokens


def ocr_with_tesseract(tiles: list[tuple[np.ndarray, int, int]]) -> list[str]:
    """
    Run Tesseract OCR in sparse-text mode on all tiles.
    Tries both PSM 11 (sparse) and PSM 6 (block) to capture more text.
    """
    import subprocess
    import tempfile
    import os

    tokens: list[str] = []
    for tile, _x, _y in tiles:
        # Scale up small tiles — Tesseract works better at 300+ DPI equivalent
        h, w = tile.shape[:2]
        if max(h, w) < 600:
            scale = 2
            tile = cv2.resize(tile, (w * scale, h * scale), interpolation=cv2.INTER_CUBIC)

        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            cv2.imwrite(f.name, tile)
            for psm in ("11", "6"):
                try:
                    result = subprocess.run(
                        ["tesseract", f.name, "stdout", "--psm", psm,
                         "-c", "tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_./"],
                        capture_output=True, text=True, timeout=30,
                    )
                    for word in re.split(r"\s+", result.stdout):
                        w_tok = word.strip()
                        if w_tok:
                            tokens.append(w_tok)
                except (subprocess.TimeoutExpired, FileNotFoundError):
                    pass
            os.unlink(f.name)
    return tokens


# ---------------------------------------------------------------------------
# Text filtering
# ---------------------------------------------------------------------------


def normalize_ref(ref: str) -> str:
    """
    Fix common OCR character substitutions in reference designators.

    In a ref like C71O, R2O5, U4O the trailing letter(s) in what should be
    the numeric suffix often have O→0, I→1, S→5, Z→2 confusion.  We correct
    the *numeric part* of the designator only (everything after the leading
    alpha prefix).
    """
    m = re.match(r"^([A-Z]+)(.+)$", ref)
    if not m:
        return ref
    prefix, suffix = m.group(1), m.group(2)
    suffix = (
        suffix
        .replace("O", "0")
        .replace("I", "1")
        .replace("S", "5")
        .replace("Z", "2")
        .replace("B", "8")
        .replace("G", "6")
    )
    return prefix + suffix


def filter_tokens(tokens: list[str]) -> tuple[set[str], set[str]]:
    """
    Separate tokens into:
    - ref_designators: matches known component reference patterns
    - part_numbers: other plausible identifiers (IC part numbers, etc.)
    """
    refs: set[str] = set()
    parts: set[str] = set()

    for token in tokens:
        # Normalise: strip punctuation at edges, uppercase
        clean = re.sub(r"^[^A-Z0-9]+|[^A-Z0-9]+$", "", token.upper())
        if not clean or len(clean) < 2:
            continue
        if NOISE_PATTERN.match(clean):
            continue
        if clean in _COMMON_WORDS:
            continue

        if REF_PATTERN.fullmatch(clean):
            refs.add(normalize_ref(clean))
        elif PARTNUM_PATTERN.fullmatch(clean) and len(clean) >= 4:
            if re.search(r"\d", clean):
                parts.add(clean)

    return refs, parts


# ---------------------------------------------------------------------------
# Per-image processing
# ---------------------------------------------------------------------------


def process_image(
    image_path: Path,
    engine: str,
    debug_dir: Path | None,
    min_confidence: float = 0.35,
    gpu: bool = False,
) -> tuple[set[str], set[str]]:
    """
    Load, preprocess, tile, and OCR a single PCB image.
    Returns (ref_designators, part_numbers).
    """
    log.info("  Processing %s", image_path.name)

    bgr = cv2.imread(str(image_path))
    if bgr is None:
        log.warning("  Could not load %s", image_path)
        return set(), set()

    gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
    log.info("  Image size: %dx%d", gray.shape[1], gray.shape[0])

    # Build preprocessing variants
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)

    if engine == "easyocr":
        # EasyOCR handles binarisation internally; give it colour-enhanced variants
        enhanced_bgr = cv2.cvtColor(enhanced, cv2.COLOR_GRAY2BGR)
        inverted_bgr = cv2.cvtColor(255 - enhanced, cv2.COLOR_GRAY2BGR)
        variants = [enhanced_bgr, inverted_bgr]
    else:
        # Tesseract: provide binary images
        variants = preprocess(gray)

    if debug_dir:
        debug_dir.mkdir(parents=True, exist_ok=True)
        stem = image_path.stem
        for i, v in enumerate(variants):
            cv2.imwrite(str(debug_dir / f"{stem}_variant{i}.png"), v)

    all_tokens: list[str] = []
    for vi, variant in enumerate(variants):
        tile_size = TILE_SIZE_EASYOCR if engine == "easyocr" else TILE_SIZE_TESSERACT
        tiles = tile_image(variant, tile_size, TILE_OVERLAP)
        log.info("  Variant %d/%d: %d tiles", vi + 1, len(variants), len(tiles))

        if engine == "easyocr":
            tokens = ocr_with_easyocr(tiles, min_confidence=min_confidence, gpu=gpu)
        else:
            tokens = ocr_with_tesseract(tiles)

        all_tokens.extend(tokens)

    refs, parts = filter_tokens(all_tokens)
    log.info("  Found %d refs, %d part-number tokens", len(refs), len(parts))
    return refs, parts


# ---------------------------------------------------------------------------
# Per-board processing
# ---------------------------------------------------------------------------


def process_board(
    board_dir: Path,
    engine: str,
    debug: bool,
    min_confidence: float = 0.35,
    gpu: bool = False,
) -> list[BomEntry]:
    board_name = board_dir.name
    log.info("Board: %s", board_name)

    images = find_board_images(board_dir)
    if not images:
        log.warning("No images found in %s", board_dir)
        return []

    debug_dir = board_dir / "_debug" if debug else None

    entries: list[BomEntry] = []
    seen_refs: set[str] = set()

    for img_path in images:
        refs, parts = process_image(
            img_path, engine, debug_dir,
            min_confidence=min_confidence, gpu=gpu,
        )

        for ref in sorted(refs):
            if ref in seen_refs:
                continue
            seen_refs.add(ref)
            entries.append(BomEntry(
                board=board_name,
                reference=ref,
                ref_type=ref_type_from_designator(ref),
                source_image=img_path.name,
                engine=engine,
                raw_text=ref,
            ))

        for part in sorted(parts):
            if part in seen_refs:
                continue
            entries.append(BomEntry(
                board=board_name,
                reference=part,
                ref_type="PartNumber",
                source_image=img_path.name,
                engine=engine,
                raw_text=part,
            ))

    log.info("Board %s: %d total entries", board_name, len(entries))
    return entries


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------

BOM_FIELDS = ["board", "reference", "ref_type", "source_image", "engine", "raw_text"]


def write_board_bom(board_dir: Path, entries: list[BomEntry]) -> None:
    out = board_dir / "bom.csv"
    with out.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=BOM_FIELDS)
        w.writeheader()
        for e in sorted(entries, key=lambda x: (x.ref_type, x.reference)):
            w.writerow(e._asdict())
    log.info("Wrote %s (%d entries)", out, len(entries))


def write_master_bom(all_entries: list[BomEntry], output_dir: Path) -> None:
    out = output_dir / "bom_master.csv"
    with out.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=BOM_FIELDS)
        w.writeheader()
        for e in sorted(all_entries, key=lambda x: (x.board, x.ref_type, x.reference)):
            w.writerow(e._asdict())
    log.info("Wrote master BOM: %s (%d total entries)", out, len(all_entries))


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Extract component BOM from PCB photographs."
    )
    parser.add_argument(
        "--board",
        metavar="NAME",
        help="Process only this board (folder name under components/). "
             "Omit to process all boards.",
    )
    parser.add_argument(
        "--engine",
        choices=["easyocr", "tesseract"],
        default="easyocr",
        help="OCR engine: 'easyocr' (default, best accuracy) or 'tesseract' (fast, no download)",
    )
    parser.add_argument(
        "--min-confidence",
        type=float,
        default=0.35,
        metavar="FLOAT",
        help="Minimum EasyOCR confidence threshold 0–1 (default: 0.4)",
    )
    parser.add_argument(
        "--gpu",
        action="store_true",
        help="Use GPU for EasyOCR inference (requires CUDA/ROCm PyTorch)",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Save preprocessed tile images to <board>/_debug/ for inspection.",
    )
    parser.add_argument(
        "--output-dir",
        metavar="DIR",
        default=str(REPO_ROOT),
        help="Directory for bom_master.csv (default: repo root).",
    )
    args = parser.parse_args()

    output_dir = Path(args.output_dir)

    if args.board:
        board_dirs = [COMPONENTS_DIR / args.board]
        if not board_dirs[0].is_dir():
            log.error("Board directory not found: %s", board_dirs[0])
            sys.exit(1)
    else:
        board_dirs = sorted(
            d for d in COMPONENTS_DIR.iterdir() if d.is_dir()
        )

    all_entries: list[BomEntry] = []

    for board_dir in board_dirs:
        entries = process_board(
            board_dir, args.engine, args.debug,
            min_confidence=args.min_confidence,
            gpu=args.gpu,
        )
        if entries:
            write_board_bom(board_dir, entries)
            all_entries.extend(entries)

    if all_entries:
        write_master_bom(all_entries, output_dir)
    else:
        log.warning("No entries found — check image paths and OCR output.")


if __name__ == "__main__":
    main()
