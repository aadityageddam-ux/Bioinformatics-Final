#!/usr/bin/env python3
"""Step 02. Extract Supplementary Tables S1 and S6 to tidy CSV.

Checks the recovered row counts against the values pre-recorded in
config/analysis.yaml. A mismatch means the published file changed or the
parser drifted, and either way the run stops rather than continuing on data
nobody has looked at.

Run:  python scripts/02_extract_tables.py
"""

from __future__ import annotations

import sys

from sox17 import tables
from sox17.paths import DATA_DERIVED, DATA_RAW, RESULTS, ensure_dirs, load_config


def main() -> int:
    ensure_dirs()
    cfg = load_config()
    archive = DATA_RAW / f"{cfg['sources']['hu2023_pmcid']}_supplementary.zip"
    if not archive.exists():
        print(f"missing {archive}; run scripts/01_fetch_raw.py first", file=sys.stderr)
        return 1

    wb = tables.open_workbook(archive)

    s1 = tables.extract_s1(wb)
    s1_path = DATA_DERIVED / "s1_primers.csv"
    s1.to_csv(s1_path, index=False)
    print(f"S1  {len(s1):>4} primer sequences  -> {s1_path}")
    for section, n in s1.groupby("section").size().items():
        print(f"      {n:>4}  {section}")

    skipped = s1.attrs.get("skipped")
    if skipped is not None and len(skipped):
        skipped_path = RESULTS / "s1_skipped_rows.tsv"
        skipped.to_csv(skipped_path, sep="\t", index=False)
        print(f"      {len(skipped):>4}  rows carried no plain DNA -> {skipped_path}")

    s6 = tables.extract_s6(wb)
    expected = cfg["expected"]["s6_colony_count_rows"]
    if len(s6) != expected:
        print(
            f"S6 row count {len(s6)} does not match the expected {expected}",
            file=sys.stderr,
        )
        return 1
    s6_path = DATA_DERIVED / "s6_colony_counts.csv"
    s6.to_csv(s6_path, index=False)
    print(f"\nS6  {len(s6):>4} colony counts     -> {s6_path}")
    print(f"      {s6['variant'].nunique():>4} distinct construct labels")
    print(f"      {s6['biological_replicate'].nunique():>4} biological replicates")

    return 0


if __name__ == "__main__":
    sys.exit(main())
