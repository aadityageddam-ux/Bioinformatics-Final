"""Tests for the published-supplement parser.

These run against the real downloaded archive, so they are also a check that
the fetch step produced what the rest of the pipeline expects.
"""

from __future__ import annotations

import pandas as pd
import pytest

from sox17 import tables
from sox17.paths import DATA_DERIVED, DATA_RAW, load_config

CFG = load_config()
ARCHIVE = DATA_RAW / f"{CFG['sources']['hu2023_pmcid']}_supplementary.zip"

pytestmark = pytest.mark.skipif(
    not ARCHIVE.exists(), reason="raw data not fetched; run `make data`"
)


@pytest.fixture(scope="module")
def workbook():
    return tables.open_workbook(ARCHIVE)


def test_s6_has_the_published_number_of_rows(workbook):
    s6 = tables.extract_s6(workbook)
    assert len(s6) == CFG["expected"]["s6_colony_count_rows"]


def test_s6_colony_counts_are_non_negative_integers(workbook):
    s6 = tables.extract_s6(workbook)
    assert s6["colony_count"].dtype.kind == "i"
    assert (s6["colony_count"] >= 0).all()


def test_s1_recovers_the_cloning_primer_block(workbook):
    s1 = tables.extract_s1(workbook)
    cloning = s1[s1["section"] == "Primers for cloning"]
    assert len(cloning) > 50
    assert cloning["sequence"].str.fullmatch(r"[ACGT]+").all()


def test_s1_contains_the_deletion_panel_primers(workbook):
    """The constructs this study rebuilds must have their primers present.

    If any of these disappear, the boundary recovery in Phase 1 has no source
    and the project cannot proceed, so it is worth failing loudly here.
    """
    s1 = tables.extract_s1(workbook)
    names = set(s1["primer_name"])
    for required in (
        "mSox17-ΔC1-F",
        "mSox17-ΔC2-F",
        "mSox17-ΔC3-SalI-R",
        "mSox17-ΔN-AgeI-F",
        "mSox17-ΔTA-F",
        "mSox17-TAD-R",
    ):
        assert required in names, f"primer {required!r} not recovered from S1"
