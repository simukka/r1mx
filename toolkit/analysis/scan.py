"""
scan.py — PCB Bill of Materials extractor for the r1mx project.

Extracts component reference designators and visible part numbers from
high-resolution PCB photographs. Uses EasyOCR (primary, best accuracy),
Tesseract (fallback, zero-download), or both.

Produces a bom.csv per board and a master bom_master.csv at the repo root.

Usage:
    # Process all boards with EasyOCR (default)
    python -m toolkit.scan.py

    # Single board
    python -m toolkit.scan.py --board cpu_io_board

    # Use Tesseract instead
    python -m toolkit.scan.py --engine tesseract

    # Save preprocessed tiles for debugging
    python -m toolkit.scan.py --board sd_board --debug

    # Minimum confidence for EasyOCR results (0–1, default 0.4)
    python -m toolkit.scan.py --min-confidence 0.5
"""

from __future__ import annotations

import csv
import logging
import re
import sys
from pathlib import Path
from dataclasses import dataclass

import cv2
import numpy as np

from toolkit.paths import COMPONENTS_DIR, REPO_ROOT

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

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


@dataclass(frozen=True)
class BomEntry:
    """Normalized OCR result for either a reference designator or part number."""

    label: str
    ref_type: str
    x_mm: float = -1.0
    y_mm: float = -1.0
    confidence: float = 1.0
    source: str = ""
    board: str = ""
    engine: str = "easyocr"
    raw_text: str = ""
    x_px: int = -1
    y_px: int = -1

    @property
    def reference(self) -> str:
        """Backward-compatible alias for the label field."""
        return self.label

    @property
    def source_image(self) -> str:
        """Backward-compatible alias for the source field."""
        return self.source

    def _asdict(self) -> dict:
        """Return a CSV-friendly representation of the entry."""
        return {
            "board": self.board,
            "reference": self.reference,
            "ref_type": self.ref_type,
            "source_image": self.source_image,
            "engine": self.engine,
            "raw_text": self.raw_text,
            "x_px": self.x_px,
            "y_px": self.y_px,
        }


def ref_type_from_designator(ref: str) -> str:
    """Return the normalized reference prefix, or an empty string when unknown."""
    match = re.match(r"^[A-Z]+", normalize_ref(ref))
    if not match:
        return ""
    prefix = match.group(0)
    known = {
        "A", "BT", "C", "CN", "CR", "D", "DS", "E", "F", "FB", "FD", "G", "H",
        "IC", "J", "K", "L", "LED", "M", "MH", "MOV", "MP", "N", "NTC", "P", "PTC",
        "Q", "R", "RN", "S", "SP", "SW", "T", "TP", "TR", "TVS", "U", "V", "VR",
        "W", "X", "Y", "Y", "Z", "ZD",
    }
    return prefix if prefix in known else ""


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
) -> list[tuple[str, int, int]]:
    """
    Run EasyOCR on all tiles.
    Returns list of (text, abs_x_px, abs_y_px) — pixel position is
    the centroid of the text bbox in the original (pre-tiling) image.
    """
    from tqdm import tqdm
    reader = _get_easyocr_reader(gpu=gpu)
    tokens: list[tuple[str, int, int]] = []
    for tile, tile_x, tile_y in tqdm(tiles, desc="  tiles", leave=False, unit="tile"):
        try:
            results = reader.readtext(tile, detail=1)
        except Exception as exc:
            log.debug("EasyOCR tile error: %s", exc)
            continue
        for bbox, text, conf in results:
            if conf >= min_confidence and text.strip():
                # bbox = [[x1,y1],[x2,y2],[x3,y3],[x4,y4]] (four corners)
                xs = [pt[0] for pt in bbox]
                ys = [pt[1] for pt in bbox]
                cx = int(sum(xs) / 4) + tile_x
                cy = int(sum(ys) / 4) + tile_y
                tokens.append((text.strip(), cx, cy))
    return tokens


def ocr_with_tesseract(tiles: list[tuple[np.ndarray, int, int]]) -> list[tuple[str, int, int]]:
    """
    Run Tesseract OCR in sparse-text mode on all tiles.
    Returns list of (text, abs_x_px, abs_y_px).
    """
    import subprocess
    import tempfile
    import os

    tokens: list[tuple[str, int, int]] = []
    for tile, tile_x, tile_y in tiles:
        h, w = tile.shape[:2]
        scale = 2 if max(h, w) < 600 else 1
        if scale > 1:
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
                            # Tesseract stdout mode doesn't give positions; use tile centre
                            tokens.append((w_tok, tile_x + w // 2, tile_y + h // 2))
                except (subprocess.TimeoutExpired, FileNotFoundError):
                    pass
            os.unlink(f.name)
    return tokens


# ---------------------------------------------------------------------------
# Text filtering
# ---------------------------------------------------------------------------


def normalize_ref(ref: str) -> str:
    """Normalize a reference designator by stripping spaces and OCR confusion."""
    ref = re.sub(r"\s+", "", ref).upper()
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


def filter_tokens(
    tokens: list[tuple[str, int, int]],
) -> tuple[list[tuple[str, int, int]], list[tuple[str, int, int]]]:
    """Separate OCR tokens into reference-designator and part-number groups."""
    refs: list[tuple[str, int, int]] = []
    parts: list[tuple[str, int, int]] = []
    seen_refs: set[str] = set()
    seen_parts: set[str] = set()

    for token, x, y in tokens:
        clean = re.sub(r"^[^A-Z0-9]+|[^A-Z0-9]+$", "", token.upper())
        if not clean or len(clean) < 2:
            continue
        if clean in _COMMON_WORDS:
            continue
        if NOISE_PATTERN.match(clean) and not (re.search(r"[A-Z]", clean) and re.search(r"\d", clean)):
            continue

        if REF_PATTERN.fullmatch(clean):
            norm = normalize_ref(clean)
            if ref_type_from_designator(norm):
                if norm not in seen_refs:
                    refs.append((norm, x, y))
                    seen_refs.add(norm)
                continue
        if PARTNUM_PATTERN.fullmatch(clean) and len(clean) >= 4 and re.search(r"\d", clean):
            if clean not in seen_parts:
                parts.append((clean, x, y))
                seen_parts.add(clean)

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
) -> tuple[list[tuple[str, int, int]], list[tuple[str, int, int]]]:
    """
    Load, preprocess, tile, and OCR a single PCB image.
    Returns (refs, parts) where each is a dict of clean_text → (x_px, y_px).
    """
    log.info("  Processing %s", image_path.name)

    bgr = cv2.imread(str(image_path))
    if bgr is None:
        log.warning("  Could not load %s", image_path)
        return {}, {}

    gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
    log.info("  Image size: %dx%d", gray.shape[1], gray.shape[0])

    # For very dark images (mean < 80), apply gamma correction to lift shadows
    mean_brightness = float(gray.mean())
    if mean_brightness < 80:
        gamma = 1 / max(0.3, mean_brightness / 128)
        gamma = min(gamma, 3.0)
        log.info("  Dark image (mean=%.0f) — applying gamma %.2f", mean_brightness, gamma)
        lut = np.array([min(255, int(((i / 255.0) ** (1.0 / gamma)) * 255))
                        for i in range(256)], dtype=np.uint8)
        bgr = cv2.LUT(bgr, lut)
        gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)

    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)

    if engine == "easyocr":
        enhanced_bgr = cv2.cvtColor(enhanced, cv2.COLOR_GRAY2BGR)
        inverted_bgr = cv2.cvtColor(255 - enhanced, cv2.COLOR_GRAY2BGR)
        # For dark boards, also add sharpened variant to catch fine silkscreen
        if mean_brightness < 80:
            sharp_kernel = np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]])
            sharpened = cv2.filter2D(enhanced_bgr, -1, sharp_kernel)
            variants = [enhanced_bgr, inverted_bgr, sharpened]
        else:
            variants = [enhanced_bgr, inverted_bgr]
    else:
        variants = preprocess(gray)

    if debug_dir:
        debug_dir.mkdir(parents=True, exist_ok=True)
        stem = image_path.stem
        for i, v in enumerate(variants):
            cv2.imwrite(str(debug_dir / f"{stem}_variant{i}.png"), v)

    all_tokens: list[tuple[str, int, int]] = []
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

        for ref, x, y in sorted(refs):
            if ref in seen_refs:
                continue
            seen_refs.add(ref)
            entries.append(BomEntry(
                board=board_name,
                label=ref,
                ref_type=ref_type_from_designator(ref),
                source=img_path.name,
                engine=engine,
                raw_text=ref,
                x_px=x,
                y_px=y,
            ))

        for part, x, y in sorted(parts):
            if part in seen_refs:
                continue
            entries.append(BomEntry(
                board=board_name,
                label=part,
                ref_type="PartNumber",
                source=img_path.name,
                engine=engine,
                raw_text=part,
                x_px=x,
                y_px=y,
            ))

    log.info("Board %s: %d total entries", board_name, len(entries))
    return entries


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------

BOM_FIELDS = ["board", "reference", "ref_type", "source_image", "engine",
              "raw_text", "x_px", "y_px"]


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


def rebuild_master_bom(output_dir: Path) -> None:
    """
    Re-read all per-board bom.csv files and write a fresh master BOM.
    Used after single-board runs to avoid clobbering the full master.
    """
    all_entries: list[BomEntry] = []
    for board_csv in sorted((COMPONENTS_DIR).glob("*/bom.csv")):
        with board_csv.open() as f:
            for row in csv.DictReader(f):
                try:
                    all_entries.append(BomEntry(
                        board=row["board"],
                        label=row["reference"],
                        ref_type=row["ref_type"],
                        source=row["source_image"],
                        engine=row["engine"],
                        raw_text=row["raw_text"],
                        x_px=int(row.get("x_px", -1)),
                        y_px=int(row.get("y_px", -1)),
                    ))
                except (KeyError, ValueError):
                    continue
    if all_entries:
        write_master_bom(all_entries, output_dir)
    else:
        log.warning("No per-board bom.csv files found")


# ---------------------------------------------------------------------------
# In-app entry point — operates on a pre-warped BGR image
# ---------------------------------------------------------------------------


def process_warped_image(
    bgr: "np.ndarray",
    board_name: str,
    layer_name: str,
    px_per_mm: float,
    engine: str = "easyocr",
    min_confidence: float = 0.35,
    gpu: bool = False,
    tile_size: int | None = None,
    tile_overlap: int = TILE_OVERLAP,
    debug_dir: "Path | None" = None,
    progress_cb=None,
) -> list[BomEntry]:
    """OCR a perspective-corrected (warped) BGR image and return BomEntry objects.

    Coordinates are returned in both px (relative to the warped image) and mm
    (px / px_per_mm).  This is the function called by r1mx_app's ScanBoardWorker.

    Parameters
    ----------
    bgr          : pre-warped board image (output of cv2.warpPerspective)
    board_name   : board folder name, stored in BomEntry
    layer_name   : "top" / "bottom", stored in source_image
    px_per_mm    : from calibration — used to convert pixel coords → mm
    engine       : "easyocr" (default) or "tesseract"
    min_confidence : EasyOCR confidence threshold
    gpu          : use CUDA for EasyOCR
    tile_size    : override tile size (default: 512 for easyocr, 1024 for tesseract)
    tile_overlap : overlap between tiles in pixels (default: 100)
    debug_dir    : optional dir to save preprocessed tile images
    progress_cb  : optional callable(str) for progress messages
    """
    def _prog(msg: str):
        log.info(msg)
        if progress_cb:
            progress_cb(msg)

    _prog(f"Scanning {board_name}/{layer_name} ({bgr.shape[1]}×{bgr.shape[0]} px, {engine}) …")

    gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
    mean_brightness = float(gray.mean())

    if mean_brightness < 80:
        gamma = min(3.0, 1 / max(0.3, mean_brightness / 128))
        _prog(f"  Dark image (mean={mean_brightness:.0f}) — gamma {gamma:.2f}")
        lut = np.array([min(255, int(((i / 255.0) ** (1.0 / gamma)) * 255))
                        for i in range(256)], dtype=np.uint8)
        bgr = cv2.LUT(bgr, lut)
        gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)

    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)

    if engine == "easyocr":
        enhanced_bgr = cv2.cvtColor(enhanced, cv2.COLOR_GRAY2BGR)
        inverted_bgr = cv2.cvtColor(255 - enhanced, cv2.COLOR_GRAY2BGR)
        variants = [enhanced_bgr, inverted_bgr]
        if mean_brightness < 80:
            sharp_kernel = np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]])
            variants.append(cv2.filter2D(enhanced_bgr, -1, sharp_kernel))
    else:
        variants = preprocess(gray)

    if debug_dir:
        debug_dir.mkdir(parents=True, exist_ok=True)
        for i, v in enumerate(variants):
            cv2.imwrite(str(debug_dir / f"scan_variant{i}.png"), v)

    all_tokens: list[tuple[str, int, int, float]] = []   # text, x, y, confidence
    _tile_size = tile_size if tile_size is not None else (
        TILE_SIZE_EASYOCR if engine == "easyocr" else TILE_SIZE_TESSERACT
    )

    for vi, variant in enumerate(variants):
        _prog(f"  OCR variant {vi + 1}/{len(variants)} …")
        tiles = tile_image(variant, _tile_size, tile_overlap)

        if engine == "easyocr":
            reader = _get_easyocr_reader(gpu=gpu)
            for tile, tile_x, tile_y in tiles:
                try:
                    results = reader.readtext(tile, detail=1)
                except Exception as exc:
                    log.debug("EasyOCR tile error: %s", exc)
                    continue
                for bbox, text, conf in results:
                    if conf >= min_confidence and text.strip():
                        xs = [pt[0] for pt in bbox]
                        ys = [pt[1] for pt in bbox]
                        cx = int(sum(xs) / 4) + tile_x
                        cy = int(sum(ys) / 4) + tile_y
                        all_tokens.append((text.strip(), cx, cy, float(conf)))
        else:
            raw = ocr_with_tesseract(tiles)
            all_tokens.extend((t, x, y, 1.0) for t, x, y in raw)

    _prog(f"  {len(all_tokens)} raw OCR tokens")
    refs, parts = filter_tokens([(t, x, y) for t, x, y, _ in all_tokens])

    # Build confidence map (first occurrence)
    conf_map: dict[str, float] = {}
    for text, x, y, conf in all_tokens:
        clean = re.sub(r"^[^A-Z0-9]+|[^A-Z0-9]+$", "", text.upper())
        if clean not in conf_map:
            conf_map[clean] = conf

    entries: list[BomEntry] = []
    seen: set[str] = set()

    for ref, x, y in sorted(refs):
        if ref in seen:
            continue
        seen.add(ref)
        entries.append(BomEntry(
            board=board_name,
            label=ref,
            ref_type=ref_type_from_designator(ref),
            source=layer_name,
            engine=engine,
            raw_text=ref,
            x_px=x, y_px=y,
            x_mm=round(x / px_per_mm, 3),
            y_mm=round(y / px_per_mm, 3),
            confidence=conf_map.get(ref, 1.0),
        ))

    for part, x, y in sorted(parts):
        if part in seen:
            continue
        seen.add(part)
        entries.append(BomEntry(
            board=board_name,
            label=part,
            ref_type="PartNumber",
            source=layer_name,
            engine=engine,
            raw_text=part,
            x_px=x, y_px=y,
            x_mm=round(x / px_per_mm, 3),
            y_mm=round(y / px_per_mm, 3),
            confidence=conf_map.get(part, 1.0),
        ))

    _prog(f"  Found {len(entries)} components/labels "
          f"({sum(1 for e in entries if e.ref_type != 'PartNumber')} refs, "
          f"{sum(1 for e in entries if e.ref_type == 'PartNumber')} part numbers)")
    return entries
