"""toolkit/paths.py — Canonical path constants for the r1mx toolkit.

This is the *only* module in the toolkit that computes the repo root from
``__file__``.  All other modules must import from here instead of
recomputing it themselves.
"""
from pathlib import Path

REPO_ROOT: Path = Path(__file__).resolve().parent.parent
DB_PATH: Path = REPO_ROOT / "r1mx.db"
COMPONENTS_DIR: Path = REPO_ROOT / "components"
SCHEMATICS_DIR: Path = REPO_ROOT / "schematics"
