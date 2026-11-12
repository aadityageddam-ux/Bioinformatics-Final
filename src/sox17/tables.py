"""Turn the published Excel supplement into tidy CSV.

The supplement arrives as a zip inside a zip, and the workbook inside is laid
out for a human reader rather than a program: Table S1 is a stack of titled
blocks with repeated header rows, and every sheet starts with a title line
above the real header. Nothing downstream should have to know that, so this
module is the single place where the published layout is understood, and
everything after it reads plain CSV.

The published file is never modified. It is read out of the zip in memory.
"""

from __future__ import annotations

import io
import re
import zipfile
from pathlib import Path

import openpyxl
import pandas as pd

# The outer archive from Europe PMC holds figures plus one inner archive.
INNER_ZIP_SUFFIX = "_supplemental_files.zip"
WORKBOOK_SUFFIX = ".xlsx"

SHEET_S1 = "S1 Primers, plasmids, oligos"
SHEET_S6 = "S6 Raw colony counts"

S6_COLUMNS = [
    "variant",         # published header is misspelled "varient"
    "colony_count",
    "technical_replicate",
    "biological_replicate",
    "category",
    "colony_type",
    "condition",
    "cell_type",
    "species",
]

DNA = re.compile(r"^[ACGTacgt]+$")


def open_workbook(archive: Path) -> openpyxl.Workbook:
    """Return the supplementary workbook from the nested archive, read-only."""
    outer = zipfile.ZipFile(archive)
    inner_name = next(
        n for n in outer.namelist() if n.endswith(INNER_ZIP_SUFFIX)
    )
    inner = zipfile.ZipFile(io.BytesIO(outer.read(inner_name)))
    book_name = next(
        n for n in inner.namelist() if n.endswith(WORKBOOK_SUFFIX)
    )
    return openpyxl.load_workbook(
        io.BytesIO(inner.read(book_name)), read_only=True, data_only=True
    )


def _clean(value: object) -> str:
    return "" if value is None else str(value).strip()


def extract_s1(wb: openpyxl.Workbook) -> pd.DataFrame:
    """Flatten Table S1 into one row per primer sequence.

    S1 is a stack of blocks. A block title sits alone in column A; a block
    header has a label in column A and something like "Sequence (5'-3')" in
    column B; a data row has a name in column A and an actual DNA string in
    column B, and sometimes a second DNA string in column C (the qPCR block
    lists forward and reverse side by side).

    Rather than hard-coding row numbers, which would break silently if the
    publisher ever reflowed the sheet, rows are classified by what they
    contain. A row counts as data only when the sequence cell is DNA.
    """
    ws = wb[SHEET_S1]
    records: list[dict[str, str]] = []
    skipped: list[dict[str, str]] = []
    section = ""
    block = ""

    for number, row in enumerate(ws.iter_rows(values_only=True), start=1):
        cells = [_clean(c) for c in row]
        cells += [""] * (4 - len(cells))
        name, b, c, source = cells[0], cells[1], cells[2], cells[3]

        if not any(cells):
            continue

        if name and not (b or c or source):
            section = name
            block = ""
            continue

        # A row is data when either sequence cell holds DNA. Testing both
        # columns matters: the EMSA block carries a "Cy5 " label in front of
        # the forward sequence, and a rule that looked only at column B would
        # read that row as a header and silently drop its reverse sequence
        # as well.
        found = [(v, o) for v, o in ((b, "forward"), (c, "reverse")) if DNA.match(v)]
        if found:
            for value, orientation in found:
                records.append(
                    {
                        "section": section,
                        "block": block,
                        "primer_name": name,
                        "orientation": orientation,
                        "sequence": value.upper(),
                        "length_nt": str(len(value)),
                        "source": source,
                    }
                )
            continue

        if name and (b or c):
            block = name          # a header row; the sequence cells hold labels
            skipped.append(
                {
                    "row": str(number),
                    "section": section,
                    "label": name,
                    "cell_b": b,
                    "cell_c": c,
                    "reason": "no plain-DNA sequence in either sequence column",
                }
            )

    df = pd.DataFrame.from_records(records)
    if df.empty:
        raise ValueError(f"no primer rows recovered from {SHEET_S1!r}")
    df.attrs["skipped"] = pd.DataFrame.from_records(skipped)
    return df


def extract_s6(wb: openpyxl.Workbook) -> pd.DataFrame:
    """Return Table S6 as one row per colony count.

    The first sheet row is a title and the second is the header, so the data
    begin on row three. Column names are taken from this module rather than
    from the sheet, because the published header misspells "variant" and
    downstream code should not inherit that.
    """
    ws = wb[SHEET_S6]
    rows = list(ws.iter_rows(min_row=3, values_only=True))
    rows = [r for r in rows if any(_clean(c) for c in r)]

    df = pd.DataFrame(rows, columns=S6_COLUMNS)
    for col in ("colony_count", "technical_replicate", "biological_replicate"):
        df[col] = pd.to_numeric(df[col], errors="raise").astype(int)
    for col in df.columns.difference(
        ["colony_count", "technical_replicate", "biological_replicate"]
    ):
        df[col] = df[col].map(_clean)
    return df
