#!/usr/bin/env python3
"""Step 01. Download every raw input and write data/raw/MANIFEST.tsv.

Run:  python scripts/01_fetch_raw.py
"""

from __future__ import annotations

import sys

from sox17 import fetch
from sox17.paths import MANIFEST, load_config, ensure_dirs


def main() -> int:
    ensure_dirs()
    cfg = load_config()
    src = cfg["sources"]
    rows: list[list[str]] = []

    for acc in (src["sox17_refseq_mrna"], src["sox2_refseq_mrna"]):
        print(f"RefSeq   {acc}", flush=True)
        fetch.fetch_refseq(acc, rows)

    for acc in (src["sox17_uniprot"], src["sox2_uniprot"]):
        print(f"UniProt  {acc}", flush=True)
        fetch.fetch_uniprot(acc, rows)

    print(f"EuropePMC {src['hu2023_pmcid']} supplementary archive", flush=True)
    fetch.fetch_supplementary(src["hu2023_pmcid"], rows)

    fetch.write_manifest(rows)
    print(f"\nwrote {MANIFEST} ({len(rows)} files)")
    for r in sorted(rows):
        print(f"  {r[0]:<34} {int(r[2]):>9,} bytes  {r[1][:16]}...")
    return 0


if __name__ == "__main__":
    sys.exit(main())
