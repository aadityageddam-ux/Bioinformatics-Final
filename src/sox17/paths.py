"""Canonical project paths and config loading.

Every module resolves paths through here so that no script ever hard-codes a
location. This is what lets the pipeline run identically from any directory.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[2]

CONFIG = ROOT / "config" / "analysis.yaml"
DATA_RAW = ROOT / "data" / "raw"
DATA_DERIVED = ROOT / "data" / "derived"
FIGURES = ROOT / "figures"
RESULTS = ROOT / "results"

MANIFEST = DATA_RAW / "MANIFEST.tsv"


def load_config(path: Path | None = None) -> dict[str, Any]:
    """Load the pre-specified analysis parameters."""
    with open(path or CONFIG, encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def ensure_dirs() -> None:
    for d in (DATA_RAW, DATA_DERIVED, FIGURES, RESULTS):
        d.mkdir(parents=True, exist_ok=True)
