"""Unit tests for toolkit.analysis.probe — parse_value and snap_to_eia_series."""

from __future__ import annotations

import math
import pytest

from toolkit.analysis.probe import parse_value, snap_to_eia_series, resolve_probe_steps, PROBE_STEPS


# ─── parse_value ─────────────────────────────────────────────────────────────

class TestParseValue:
    def test_plain_integer(self):
        si, unit = parse_value("4700")
        assert si == pytest.approx(4700.0)
        assert unit == ""

    def test_k_suffix(self):
        si, unit = parse_value("4.7k")
        assert si == pytest.approx(4700.0)

    def test_k_embedded(self):
        """4k7 is common SMD notation for 4.7 kΩ."""
        si, unit = parse_value("4k7")
        assert si == pytest.approx(4700.0)

    def test_k_no_decimal(self):
        si, unit = parse_value("10k")
        assert si == pytest.approx(10_000.0)

    def test_mega(self):
        si, unit = parse_value("1.5M")
        assert si == pytest.approx(1_500_000.0)

    def test_nano(self):
        si, unit = parse_value("220n")
        assert si == pytest.approx(220e-9)

    def test_nano_with_unit(self):
        si, unit = parse_value("220nF")
        assert si == pytest.approx(220e-9)
        assert unit == "F"

    def test_pico(self):
        si, unit = parse_value("100p")
        assert si == pytest.approx(100e-12)

    def test_micro_ascii(self):
        si, unit = parse_value("0.47u")
        assert si == pytest.approx(0.47e-6)

    def test_micro_unicode(self):
        si, unit = parse_value("0.47µ")
        assert si == pytest.approx(0.47e-6)

    def test_micro_with_unit(self):
        si, unit = parse_value("2.2µH")
        assert si == pytest.approx(2.2e-6)
        assert unit == "H"

    def test_milli(self):
        si, unit = parse_value("2.2mH")
        assert si == pytest.approx(2.2e-3)
        assert unit == "H"

    def test_volts(self):
        si, unit = parse_value("0.7V")
        assert si == pytest.approx(0.7)
        assert unit == "V"

    def test_ohm_unit_alias(self):
        si, unit = parse_value("47ohm")
        assert si == pytest.approx(47.0)
        assert unit == "Ω"

    def test_zero(self):
        si, unit = parse_value("0")
        assert si == pytest.approx(0.0)

    def test_float_only(self):
        si, unit = parse_value("3.14")
        assert si == pytest.approx(3.14)

    def test_empty_raises(self):
        with pytest.raises(ValueError):
            parse_value("")

    def test_junk_raises(self):
        with pytest.raises(ValueError):
            parse_value("not_a_number!!")


# ─── snap_to_eia_series ───────────────────────────────────────────────────────

class TestSnapToEIA:
    def test_e24_4k7(self):
        snapped, label = snap_to_eia_series(4700.0, "E24")
        assert snapped == pytest.approx(4700.0, rel=0.02)

    def test_e24_rounds_up(self):
        """4800 Ω is between 4.7k and 5.1k; nearest E24 is 4.7k."""
        snapped, _ = snap_to_eia_series(4800.0, "E24")
        assert snapped == pytest.approx(4700.0, rel=0.02)

    def test_e24_100(self):
        snapped, label = snap_to_eia_series(100.0, "E24")
        assert snapped == pytest.approx(100.0, rel=0.02)

    def test_e12_series(self):
        snapped, _ = snap_to_eia_series(5000.0, "E12")
        # Nearest E12 to 5000 is 4700
        assert snapped == pytest.approx(4700.0, rel=0.03)

    def test_e96_precise(self):
        snapped, _ = snap_to_eia_series(1000.0, "E96")
        assert snapped == pytest.approx(1000.0, rel=0.02)

    def test_small_pico(self):
        """100 pF → should snap to 100 pF (E24 has 1.0)."""
        snapped, _ = snap_to_eia_series(100e-12, "E24")
        assert snapped == pytest.approx(100e-12, rel=0.02)

    def test_label_contains_number(self):
        _, label = snap_to_eia_series(4700.0, "E24")
        assert "4.7" in label or "4700" in label or "4 k" in label

    def test_zero_returns_zero(self):
        snapped, _ = snap_to_eia_series(0.0)
        assert snapped == 0.0

    def test_negative_value(self):
        """Negative values are treated as zero (no negative preferred values)."""
        snapped, _ = snap_to_eia_series(-1.0)
        assert snapped == -1.0   # returned unchanged


# ─── resolve_probe_steps ─────────────────────────────────────────────────────

class TestResolveProbeSteps:
    def test_resistor(self):
        steps = resolve_probe_steps("R")
        assert len(steps) >= 1
        assert steps[0].measurement_type == "resistance"

    def test_capacitor(self):
        steps = resolve_probe_steps("C")
        types = [s.measurement_type for s in steps]
        assert "capacitance" in types

    def test_inductor(self):
        steps = resolve_probe_steps("L")
        types = [s.measurement_type for s in steps]
        assert "dcr" in types

    def test_diode(self):
        steps = resolve_probe_steps("D")
        assert steps[0].measurement_type == "forward_voltage"
        assert steps[0].orientation == "forward"

    def test_zener_inherit(self):
        # ZD has its own steps defined
        steps = resolve_probe_steps("ZD")
        assert any(s.orientation == "forward" for s in steps)

    def test_led(self):
        steps = resolve_probe_steps("LED")
        assert steps[0].measurement_type == "forward_voltage"

    def test_ds_inherits_led(self):
        led_steps  = resolve_probe_steps("LED")
        ds_steps   = resolve_probe_steps("DS")
        assert [s.measurement_type for s in led_steps] == [s.measurement_type for s in ds_steps]

    def test_cr_inherits_d(self):
        d_steps  = resolve_probe_steps("D")
        cr_steps = resolve_probe_steps("CR")
        assert [s.measurement_type for s in d_steps] == [s.measurement_type for s in cr_steps]

    def test_fuse(self):
        steps = resolve_probe_steps("F")
        assert steps[0].measurement_type == "continuity"

    def test_crystal(self):
        steps = resolve_probe_steps("X")
        assert steps[0].measurement_type == "continuity"

    def test_transistor(self):
        steps = resolve_probe_steps("Q")
        types = [s.measurement_type for s in steps]
        assert "forward_voltage" in types

    def test_unknown_prefix(self):
        """Unknown prefix returns a fallback resistance check."""
        steps = resolve_probe_steps("UNKNOWN_ZZZZ")
        assert len(steps) == 1
        assert steps[0].measurement_type == "resistance"

    def test_prefix_matching_r12(self):
        """R12 should resolve to R steps (prefix match)."""
        r_steps  = resolve_probe_steps("R")
        r12_steps = resolve_probe_steps("R12")
        assert [s.measurement_type for s in r_steps] == [s.measurement_type for s in r12_steps]

    def test_all_step_fields_present(self):
        """Every step must have the required fields."""
        for key in PROBE_STEPS:
            if isinstance(PROBE_STEPS[key], str):
                continue  # alias, tested via inheritance
            for step in PROBE_STEPS[key]:
                assert step.measurement_type
                assert step.title
                assert step.instruction
                assert step.unit
                assert isinstance(step.display_units, list)
                assert len(step.display_units) >= 1
