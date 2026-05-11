"""Component probing protocol — measurement steps and value parsing.

Pure-logic module with no Qt or DB dependencies.

Classes / functions
-------------------
ProbeStep            — dataclass: one multimeter measurement instruction
PROBE_STEPS          — dict[ref_type_prefix → list[ProbeStep]]
parse_value(text)    — "4k7" / "220nF" / "0.47µ" → (si_float, unit_str)
snap_to_eia_series   — round to nearest EIA preferred value (E12 / E24 / E96)

Measurement methodology based on:
  - AVR Transistor Tester (Markus Reschke / Karl-Heinz Kübbeler, EUPL)
  - SparkFun DMM tutorial
  - Hardware-Hacking-Starter-Pack component-id guide
"""

from __future__ import annotations

import math
import re
from dataclasses import dataclass, field


# ─── ProbeStep dataclass ─────────────────────────────────────────────────────

@dataclass
class ProbeStep:
    """A single multimeter measurement step shown to the user."""

    measurement_type: str
    """DB key: "resistance" | "capacitance" | "inductance" | "dcr" |
               "forward_voltage" | "hfe" | "continuity" | "esr" """

    title: str
    """Short heading shown in bold."""

    instruction: str
    """Full user-facing instruction (may include \\n for line breaks)."""

    unit: str
    """SI unit string stored in DB: "Ω" | "F" | "H" | "V" | "dimensionless" """

    display_units: list[str]
    """Unit choices offered in the combobox (most specific first)."""

    optional: bool = False
    """True for supplementary measurements (ESR, DCR, leakage)."""

    in_circuit_warning: str = ""
    """Non-empty → show ⚠ warning with this text when in_circuit=True."""

    orientation: str = ""
    """Non-empty → stored as orientation in DB (e.g. "forward" / "reverse")."""


# ─── EIA preferred-value series ──────────────────────────────────────────────

_E12 = [1.0, 1.2, 1.5, 1.8, 2.2, 2.7, 3.3, 3.9, 4.7, 5.6, 6.8, 8.2]

_E24 = [
    1.0, 1.1, 1.2, 1.3, 1.5, 1.6, 1.8, 2.0, 2.2, 2.4, 2.7, 3.0,
    3.3, 3.6, 3.9, 4.3, 4.7, 5.1, 5.6, 6.2, 6.8, 7.5, 8.2, 9.1,
]

# E96 series (full 96 values per decade)
_E96 = [
    1.00, 1.02, 1.05, 1.07, 1.10, 1.13, 1.15, 1.18, 1.21, 1.24, 1.27, 1.30,
    1.33, 1.37, 1.40, 1.43, 1.47, 1.50, 1.54, 1.58, 1.62, 1.65, 1.69, 1.74,
    1.78, 1.82, 1.87, 1.91, 1.96, 2.00, 2.05, 2.10, 2.15, 2.21, 2.26, 2.32,
    2.37, 2.43, 2.49, 2.55, 2.61, 2.67, 2.74, 2.80, 2.87, 2.94, 3.01, 3.09,
    3.16, 3.24, 3.32, 3.40, 3.48, 3.57, 3.65, 3.74, 3.83, 3.92, 4.02, 4.12,
    4.22, 4.32, 4.42, 4.53, 4.64, 4.75, 4.87, 4.99, 5.11, 5.23, 5.36, 5.49,
    5.62, 5.76, 5.90, 6.04, 6.19, 6.34, 6.49, 6.65, 6.81, 6.98, 7.15, 7.32,
    7.50, 7.68, 7.87, 8.06, 8.25, 8.45, 8.66, 8.87, 9.09, 9.31, 9.53, 9.76,
]

_SERIES: dict[str, list[float]] = {"E12": _E12, "E24": _E24, "E96": _E96}


def snap_to_eia_series(value: float, series: str = "E24") -> tuple[float, str]:
    """Return the nearest EIA preferred value and a human-readable string.

    Parameters
    ----------
    value  : value in SI base units (e.g. 4700.0 for 4.7 kΩ)
    series : "E12", "E24", or "E96"

    Returns
    -------
    (snapped_si_value, formatted_string)
    e.g. (4700.0, "4.7 kΩ") or (220e-12, "220 pF")
    """
    if value <= 0:
        return (value, str(value))

    mantissa_series = _SERIES.get(series, _E24)

    # Decompose into mantissa ∈ [1, 10) and decade exponent
    exp = math.floor(math.log10(value))
    mantissa = value / (10 ** exp)

    # Find nearest preferred mantissa (wrap around 10)
    best = min(mantissa_series, key=lambda v: abs(v - mantissa))
    # Also check the first value of the next decade (handles e.g. mantissa=9.9 → 10.0=1.0 next)
    if abs(mantissa_series[0] * 10 - mantissa) < abs(best - mantissa):
        best = mantissa_series[0]
        exp += 1

    snapped = best * (10 ** exp)
    return (snapped, _format_si(snapped))


def _format_si(value: float) -> str:
    """Format a value with SI prefix, picking the most readable scale."""
    prefixes = [
        (1e12,  "T"), (1e9,  "G"), (1e6,  "M"), (1e3, "k"),
        (1.0,   "" ), (1e-3, "m"), (1e-6, "µ"), (1e-9, "n"), (1e-12, "p"),
    ]
    for scale, prefix in prefixes:
        scaled = value / scale
        if scaled >= 1.0:
            if scaled == int(scaled):
                return f"{int(scaled)} {prefix}"
            return f"{scaled:.3g} {prefix}"
    return str(value)


# ─── Value parsing ────────────────────────────────────────────────────────────

# SI prefix → multiplier
_PREFIX_MAP: dict[str, float] = {
    "p": 1e-12, "n": 1e-9, "u": 1e-6, "µ": 1e-6, "μ": 1e-6,
    "m": 1e-3,  "k": 1e3,  "K": 1e3,  "M": 1e6,  "G": 1e9,
}

# Unit aliases → canonical unit
_UNIT_ALIASES: dict[str, str] = {
    "ohm": "Ω", "ohms": "Ω", "r": "Ω", "Ω": "Ω", "ω": "Ω",
    "f":   "F", "farad": "F", "farads": "F",
    "h":   "H", "henry": "H", "henries": "H", "henrys": "H",
    "v":   "V", "volt": "V", "volts": "V",
}

# Regex that captures optional leading sign, integer/decimal portion,
# optional SI prefix embedded in the number (e.g. 4k7), optional unit.
_VALUE_RE = re.compile(
    r"""
    ^
    \s*
    (?P<sign>[-+])?
    (?P<int>\d+)?
    (?P<prefix1>[pnuµμmkKMG])?   # prefix between digits (e.g. 4k7)
    (?:\.(?P<frac>\d+))?
    (?P<prefix2>[pPnNuUµμmkKMG])? # prefix after all digits
    \s*
    (?P<unit>[A-Za-zΩωµμ]+)?
    \s*$
    """,
    re.VERBOSE,
)


def parse_value(text: str) -> tuple[float, str]:
    """Parse a user-entered measurement value into (SI float, canonical unit).

    Handles formats including:
      "4k7"   → (4700.0,  "Ω")
      "4.7k"  → (4700.0,  "Ω")
      "220n"  → (220e-9,  "F")
      "220nF" → (220e-9,  "F")
      "0.47µ" → (0.47e-6, "F")
      "1.5M"  → (1.5e6,   "Ω")
      "2.2mH" → (2.2e-3,  "H")
      "0.7V"  → (0.7,     "V")
      "100"   → (100.0,   "")

    The unit is inferred from the unit suffix when present;
    if absent, an empty string is returned and the caller should
    use the unit selected in the UI.

    Raises ValueError on unparseable input.
    """
    text = text.strip()
    if not text:
        raise ValueError("empty input")

    # ── Fast path: embedded-prefix notation e.g. "4k7", "2R2", "4n7" ────
    _embedded = re.match(
        r"^(?P<sign>[-+])?(?P<int>\d+)(?P<pfx>[pnuµμmkKMGrRoO])(?P<frac>\d+)"
        r"(?P<unit>[A-Za-zΩωµμ]*)$",
        text,
    )
    if _embedded:
        sign    = -1.0 if _embedded.group("sign") == "-" else 1.0
        pfx_raw = _embedded.group("pfx")
        # "r", "R", "o", "O" used as decimal point in resistor notation (4R7 = 4.7 Ω)
        if pfx_raw.lower() in ("r", "o"):
            numeric    = float(f"{_embedded.group('int')}.{_embedded.group('frac')}")
            multiplier = 1.0
        else:
            numeric    = float(f"{_embedded.group('int')}.{_embedded.group('frac')}")
            multiplier = _PREFIX_MAP.get(pfx_raw, 1.0)
        unit_s         = (_embedded.group("unit") or "").lower()
        canonical_unit = _UNIT_ALIASES.get(unit_s, "")
        return (sign * numeric * multiplier, canonical_unit)

    m = _VALUE_RE.match(text)
    if not m:
        raise ValueError(f"cannot parse {text!r}")

    sign    = -1.0 if m.group("sign") == "-" else 1.0
    int_s   = m.group("int")   or "0"
    frac_s  = m.group("frac")  or ""
    prefix1 = m.group("prefix1") or ""
    prefix2 = m.group("prefix2") or ""
    unit_s  = (m.group("unit")  or "").lower()

    # Build the numeric string: "4" + "k" (no frac) or "4" + "." + "7"
    if prefix1 and frac_s:
        # e.g. "4k.7" (unusual but covered)
        numeric = float(f"{int_s}.{frac_s}")
        prefix  = prefix1
    elif prefix1:
        numeric = float(int_s)
        prefix  = prefix1
    elif frac_s:
        numeric = float(f"{int_s}.{frac_s}")
        prefix  = prefix2
    else:
        numeric = float(int_s)
        prefix  = prefix2

    multiplier = _PREFIX_MAP.get(prefix, 1.0)
    si_value   = sign * numeric * multiplier

    # Resolve unit
    canonical_unit = _UNIT_ALIASES.get(unit_s, "")

    return (si_value, canonical_unit)


# ─── Probe step definitions ───────────────────────────────────────────────────

_IN_CIRCUIT_R_WARN = (
    "⚠ In-circuit reading: parallel paths will make this read LOWER than the true value. "
    "Lift one lead for an accurate measurement."
)
_IN_CIRCUIT_C_WARN = (
    "⚠ In-circuit reading: parallel capacitances and inductances will distort the result. "
    "Remove the component for an accurate value."
)
_IN_CIRCUIT_L_WARN = (
    "⚠ In-circuit reading for inductance is unreliable. Remove the component first."
)
_IN_CIRCUIT_Q_WARN = (
    "⚠ In-circuit transistor measurements are not reliable. "
    "Desolder the component for hFE / Vth measurement."
)

PROBE_STEPS: dict[str, list[ProbeStep]] = {

    # ── Resistors ──────────────────────────────────────────────────────────
    "R": [
        ProbeStep(
            measurement_type="resistance",
            title="Resistance",
            instruction=(
                "1. Power off the board and discharge any nearby capacitors.\n"
                "2. Set DMM to Ω (resistance), auto-range or start at 200 kΩ.\n"
                "3. Place probes across both leads of the resistor.\n"
                "4. Note the stable reading and enter it below.\n\n"
                "Tip: if the reading is near zero, try the 200 Ω range."
            ),
            unit="Ω",
            display_units=["Ω", "kΩ", "MΩ"],
            in_circuit_warning=_IN_CIRCUIT_R_WARN,
        ),
    ],
    "RN": [
        ProbeStep(
            measurement_type="resistance",
            title="Resistance (resistor network)",
            instruction=(
                "Resistor networks contain multiple resistors in a single package.\n"
                "1. Power off and discharge.\n"
                "2. Set DMM to Ω, auto-range.\n"
                "3. Measure between pin 1 and each other pin in turn.\n"
                "4. Record the most common stable value below."
            ),
            unit="Ω",
            display_units=["Ω", "kΩ", "MΩ"],
            in_circuit_warning=_IN_CIRCUIT_R_WARN,
        ),
    ],

    # ── Capacitors ────────────────────────────────────────────────────────
    "C": [
        ProbeStep(
            measurement_type="capacitance",
            title="Capacitance",
            instruction=(
                "1. Power off the board. Discharge the capacitor: short its leads\n"
                "   briefly with a 1 kΩ resistor or the DMM probes in Ω mode.\n"
                "2. Set DMM to capacitance (F) mode.\n"
                "3. Place probes across both leads (polarity matters for electrolytics:\n"
                "   red → + leg, black → − leg).\n"
                "4. Wait for the reading to stabilise (large caps may take 10 s).\n"
                "5. Enter the value below."
            ),
            unit="F",
            display_units=["pF", "nF", "µF", "mF"],
            in_circuit_warning=_IN_CIRCUIT_C_WARN,
        ),
        ProbeStep(
            measurement_type="esr",
            title="ESR (optional — requires ESR meter or LCR)",
            instruction=(
                "ESR (Equivalent Series Resistance) reveals capacitor health.\n"
                "1. Use a dedicated ESR meter or LCR meter's ESR function.\n"
                "2. Discharge the capacitor first.\n"
                "3. Measure ESR across the leads.\n\n"
                "Typical healthy electrolytic ESR:\n"
                "  < 100 µF  → < 1 Ω\n"
                "  > 1000 µF → < 0.1 Ω\n"
                "A high ESR (e.g. > 5 Ω) indicates a failing capacitor."
            ),
            unit="Ω",
            display_units=["Ω", "mΩ"],
            optional=True,
            in_circuit_warning=(
                "⚠ In-circuit ESR is valid as a first-pass health check. "
                "Parallel resistors may mask a bad reading — lift one lead to confirm."
            ),
        ),
    ],

    # ── Inductors / ferrite beads ─────────────────────────────────────────
    "L": [
        ProbeStep(
            measurement_type="dcr",
            title="DC Resistance (DCR)",
            instruction=(
                "1. Power off the board.\n"
                "2. Set DMM to Ω, lowest range (200 Ω or 20 Ω).\n"
                "3. Place probes across both leads.\n"
                "4. Subtract the probe lead resistance if significant\n"
                "   (measure the probes shorted together first).\n\n"
                "Most inductors have DCR < 10 Ω."
            ),
            unit="Ω",
            display_units=["Ω", "mΩ"],
            in_circuit_warning=_IN_CIRCUIT_R_WARN,
        ),
        ProbeStep(
            measurement_type="inductance",
            title="Inductance (requires LCR meter)",
            instruction=(
                "1. Remove the component or lift one lead.\n"
                "2. Set LCR meter to inductance (H) mode, 1 kHz test frequency.\n"
                "3. Place probes across both leads.\n"
                "4. Enter the reading below."
            ),
            unit="H",
            display_units=["µH", "mH", "H"],
            optional=True,
            in_circuit_warning=_IN_CIRCUIT_L_WARN,
        ),
    ],
    "FB": [
        ProbeStep(
            measurement_type="dcr",
            title="DC Resistance (ferrite bead)",
            instruction=(
                "Ferrite beads act as low-pass RF filters; their DC resistance is\n"
                "typically < 1 Ω.\n\n"
                "1. Power off the board.\n"
                "2. Set DMM to Ω, lowest range.\n"
                "3. Place probes across both leads.\n"
                "4. Enter the stable reading below."
            ),
            unit="Ω",
            display_units=["Ω", "mΩ"],
            in_circuit_warning=_IN_CIRCUIT_R_WARN,
        ),
    ],

    # ── Diodes ────────────────────────────────────────────────────────────
    "D": [
        ProbeStep(
            measurement_type="forward_voltage",
            title="Forward Voltage (Vf) — forward bias",
            instruction=(
                "1. Power off the board.\n"
                "2. Set DMM to diode test mode (diode symbol ⊣).\n"
                "3. Red probe → anode (usually the end WITHOUT the stripe).\n"
                "   Black probe → cathode (stripe end).\n"
                "4. Enter the reading (typically 0.15–0.70 V).\n\n"
                "Expected values:\n"
                "  Silicon:  0.55–0.70 V\n"
                "  Schottky: 0.15–0.45 V\n"
                "  Germanium:0.20–0.35 V"
            ),
            unit="V",
            display_units=["V", "mV"],
            orientation="forward",
        ),
        ProbeStep(
            measurement_type="forward_voltage",
            title="Reverse test",
            instruction=(
                "1. Reverse the probes:\n"
                "   Black probe → anode / Red probe → cathode.\n"
                "2. A healthy diode reads OL (open) in reverse.\n"
                "3. If you get a reading (not OL), note the value — it may be a\n"
                "   Zener conducting in reverse at the DMM's test voltage, or a leak."
            ),
            unit="V",
            display_units=["V", "mV"],
            orientation="reverse",
            optional=True,
        ),
    ],
    "CR": "__inherit__D",
    "ZD": [
        ProbeStep(
            measurement_type="forward_voltage",
            title="Forward Voltage (Vf) — Zener, forward bias",
            instruction=(
                "1. Power off the board.\n"
                "2. Set DMM to diode test mode.\n"
                "3. Red → anode, Black → cathode.\n"
                "4. Forward Vf of a Zener is the same as a normal Si diode (0.55–0.70 V).\n"
                "5. Enter the reading."
            ),
            unit="V",
            display_units=["V", "mV"],
            orientation="forward",
        ),
        ProbeStep(
            measurement_type="forward_voltage",
            title="Reverse breakdown (Zener voltage) — requires bench supply",
            instruction=(
                "⚠ DMM diode mode uses only ~1–3 V; it cannot trigger Zener breakdown.\n\n"
                "To measure Zener voltage (Vz):\n"
                "1. Desolder the diode.\n"
                "2. Connect: bench supply (+) → 1 kΩ resistor → cathode; anode → supply (−).\n"
                "3. Slowly raise voltage until current flows (a few mA).\n"
                "4. Measure voltage across the Zener — that is Vz.\n\n"
                "Common values: 2.4 V, 3.3 V, 3.6 V, 5.1 V, 5.6 V, 6.2 V, 12 V"
            ),
            unit="V",
            display_units=["V"],
            optional=True,
            orientation="reverse",
        ),
    ],
    "TVS": [
        ProbeStep(
            measurement_type="forward_voltage",
            title="Forward Voltage (Vf) — TVS diode",
            instruction=(
                "TVS (Transient Voltage Suppressor) diodes have two leads like a normal diode.\n"
                "Unidirectional TVS: test as a diode.\n"
                "Bidirectional TVS: both orientations will show a Vf reading.\n\n"
                "1. Set DMM to diode test mode.\n"
                "2. Red → one lead, Black → other.\n"
                "3. Enter reading, note orientation."
            ),
            unit="V",
            display_units=["V", "mV"],
            orientation="forward",
        ),
        ProbeStep(
            measurement_type="forward_voltage",
            title="Reverse orientation test",
            instruction=(
                "1. Swap probes: Black → previous anode, Red → previous cathode.\n"
                "2. Unidirectional TVS: reads OL. Bidirectional TVS: reads a Vf.\n"
                "3. Enter reading or 'OL' if open."
            ),
            unit="V",
            display_units=["V", "mV"],
            orientation="reverse",
            optional=True,
        ),
    ],

    # ── LEDs ─────────────────────────────────────────────────────────────
    "LED": [
        ProbeStep(
            measurement_type="forward_voltage",
            title="Forward Voltage (Vf) — LED",
            instruction=(
                "1. Set DMM to diode test mode.\n"
                "2. Red → anode (longer leg / no flat), Black → cathode (flat / shorter leg).\n"
                "3. Some DMMs supply enough current to faintly illuminate the LED — useful for\n"
                "   confirming polarity and colour.\n"
                "4. Enter the Vf reading.\n\n"
                "Expected by colour:\n"
                "  Red / IR:   1.6–2.2 V\n"
                "  Yellow/Green: 1.8–2.5 V\n"
                "  Blue / White: 2.8–3.5 V"
            ),
            unit="V",
            display_units=["V", "mV"],
            orientation="forward",
        ),
    ],
    "DS": "__inherit__LED",

    # ── BJT / MOSFET transistors ──────────────────────────────────────────
    "Q": [
        ProbeStep(
            measurement_type="forward_voltage",
            title="B-E Junction (base–emitter) forward Vf",
            instruction=(
                "Treat the transistor as two diodes (B-E and B-C).\n\n"
                "NPN: Red → Base, Black → Emitter → expect ~0.55–0.70 V (Si)\n"
                "PNP: Red → Emitter, Black → Base → expect ~0.55–0.70 V\n\n"
                "1. Set DMM to diode test mode.\n"
                "2. Measure B-E junction.\n"
                "3. Enter the Vf reading."
            ),
            unit="V",
            display_units=["V", "mV"],
            orientation="forward",
            in_circuit_warning=_IN_CIRCUIT_Q_WARN,
        ),
        ProbeStep(
            measurement_type="forward_voltage",
            title="B-C Junction (base–collector) forward Vf",
            instruction=(
                "1. Red → Base, Black → Collector (NPN) or Red → Collector, Black → Base (PNP).\n"
                "2. Enter the Vf reading (~0.55–0.70 V for Si BJT)."
            ),
            unit="V",
            display_units=["V", "mV"],
            orientation="forward",
            optional=True,
            in_circuit_warning=_IN_CIRCUIT_Q_WARN,
        ),
        ProbeStep(
            measurement_type="hfe",
            title="hFE (current gain) — DMM hFE socket",
            instruction=(
                "If your DMM has an hFE / transistor socket:\n"
                "1. Desolder the transistor.\n"
                "2. Insert into the B/C/E socket (NPN or PNP as appropriate).\n"
                "3. Enter the hFE reading.\n\n"
                "Typical small-signal NPN: hFE 100–400.\n"
                "Power transistors: 20–100."
            ),
            unit="dimensionless",
            display_units=[""],
            optional=True,
            in_circuit_warning=_IN_CIRCUIT_Q_WARN,
        ),
    ],
    "T":  "__inherit__Q",
    "TR": "__inherit__Q",

    # ── Fuses ─────────────────────────────────────────────────────────────
    "F": [
        ProbeStep(
            measurement_type="continuity",
            title="Continuity (fuse check)",
            instruction=(
                "1. Power off the board.\n"
                "2. Set DMM to continuity mode (beep symbol) or Ω mode.\n"
                "3. Place probes across both ends of the fuse.\n"
                "4. Good fuse: continuity beep or reading < 1 Ω.\n"
                "   Blown fuse: OL (open loop).\n"
                "5. Enter reading below (0 = good, OL = blown)."
            ),
            unit="Ω",
            display_units=["Ω"],
        ),
    ],

    # ── Crystals / resonators ─────────────────────────────────────────────
    "X": [
        ProbeStep(
            measurement_type="continuity",
            title="Quick check — should read open",
            instruction=(
                "1. Set DMM to highest Ω range (> 10 MΩ).\n"
                "2. Place probes across both crystal pins.\n"
                "3. A good crystal reads essentially open (> 10 MΩ).\n"
                "   If it reads low resistance (< 100 kΩ), the crystal may be shorted."
            ),
            unit="Ω",
            display_units=["MΩ", "kΩ", "Ω"],
        ),
        ProbeStep(
            measurement_type="capacitance",
            title="Parallel capacitance (optional — LCR meter)",
            instruction=(
                "1. Use an LCR meter at the crystal's rated frequency.\n"
                "2. Place probes across both pins.\n"
                "3. The parallel (shunt) capacitance (C0) is typically 1–10 pF.\n"
                "4. Enter the reading."
            ),
            unit="F",
            display_units=["pF", "nF"],
            optional=True,
        ),
    ],
    "Y": "__inherit__X",

    # ── MOVs / varistors ─────────────────────────────────────────────────
    "MOV": [
        ProbeStep(
            measurement_type="resistance",
            title="Off-state resistance",
            instruction=(
                "1. Power off the board.\n"
                "2. Set DMM to highest Ω range (> 10 MΩ).\n"
                "3. Place probes across the varistor.\n"
                "4. A good MOV reads essentially open (> 10 MΩ).\n"
                "   A failed MOV reads low resistance."
            ),
            unit="Ω",
            display_units=["MΩ", "kΩ", "Ω"],
        ),
    ],
    "VR": "__inherit__MOV",

    # ── Thermistors / PTC / NTC ───────────────────────────────────────────
    "RT": [
        ProbeStep(
            measurement_type="resistance",
            title="Resistance (at room temperature)",
            instruction=(
                "Thermistors change resistance with temperature.\n\n"
                "1. Power off the board.\n"
                "2. Set DMM to Ω, auto-range.\n"
                "3. Place probes across both leads.\n"
                "4. Note the ambient temperature if possible.\n"
                "5. Enter the reading."
            ),
            unit="Ω",
            display_units=["Ω", "kΩ"],
            in_circuit_warning=_IN_CIRCUIT_R_WARN,
        ),
    ],
    "NTC": "__inherit__RT",
    "PTC": "__inherit__RT",
}


def resolve_probe_steps(ref_type: str) -> list[ProbeStep]:
    """Return the list of ProbeSteps for a given ref_type prefix.

    Resolves ``"__inherit__X"`` aliases.  Falls back to a generic resistance
    check if the prefix is not known.
    """
    key = ref_type.upper()
    steps = PROBE_STEPS.get(key)

    if steps is None:
        # Try prefix matching (e.g. "R1" → "R")
        for k in PROBE_STEPS:
            if key.startswith(k):
                steps = PROBE_STEPS[k]
                break

    if steps is None:
        # Unknown component — offer a generic resistance/continuity measurement
        steps = [
            ProbeStep(
                measurement_type="resistance",
                title="Unknown component — resistance check",
                instruction=(
                    "Component type not recognised.\n\n"
                    "1. Power off the board.\n"
                    "2. Set DMM to Ω, auto-range.\n"
                    "3. Place probes across the component leads.\n"
                    "4. Enter any stable reading."
                ),
                unit="Ω",
                display_units=["Ω", "kΩ", "MΩ"],
            )
        ]
        return steps

    if isinstance(steps, str) and steps.startswith("__inherit__"):
        inherited_key = steps[len("__inherit__"):]
        return resolve_probe_steps(inherited_key)

    return list(steps)
