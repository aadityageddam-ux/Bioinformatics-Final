"""Retrieve every raw input from its public source, and record what was got.

Nothing in this project is downloaded by hand. Each file is fetched here, its
SHA-256 digest and byte count are written to data/raw/MANIFEST.tsv, and every
later step reads from data/raw/ only. That manifest is committed, so anyone can
re-run the fetch and prove byte-for-byte that they obtained the same inputs,
even though the data files themselves are not in the repository.

Sources
    NCBI E-utilities   reference mRNA and protein (RefSeq)
    UniProt REST       curated domain boundaries, in flat-file format
    Europe PMC         supplementary archive for Hu et al. (2023)
"""

from __future__ import annotations

import hashlib
import time
from datetime import datetime, timezone
from pathlib import Path

import requests

from .paths import DATA_RAW, MANIFEST, ensure_dirs

# NCBI asks automated clients to identify the tool making the request. No
# contact address is sent: it is not needed for this volume of requests and
# would publish a personal detail to a third party.
NCBI_TOOL = "sox17-tail-analysis"

EUTILS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
UNIPROT = "https://rest.uniprot.org/uniprotkb/{acc}.txt"
EUROPEPMC_SUPP = (
    "https://www.ebi.ac.uk/europepmc/webservices/rest/{pmcid}/supplementaryFiles"
)

TIMEOUT = 120
MANIFEST_HEADER = ["filename", "sha256", "bytes", "source_url", "retrieved_utc"]


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _record(filename: str, path: Path, url: str, rows: list[list[str]]) -> None:
    rows.append(
        [
            filename,
            sha256_of(path),
            str(path.stat().st_size),
            url,
            datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        ]
    )


def _download(url: str, dest: Path, params: dict | None = None) -> str:
    """GET url into dest. Returns the fully resolved URL that was used."""
    resp = requests.get(url, params=params, timeout=TIMEOUT, stream=True)
    resp.raise_for_status()
    with open(dest, "wb") as fh:
        for chunk in resp.iter_content(1 << 16):
            fh.write(chunk)
    return resp.url


def fetch_refseq(accession: str, rows: list[list[str]]) -> Path:
    """Fetch a RefSeq nucleotide record in GenBank flat-file format.

    GenBank rather than FASTA, because the flat file carries the CDS feature
    and its conceptual translation. That lets a later step take the coding
    sequence and the protein from one record and check they agree, instead of
    fetching two files and trusting that they correspond.
    """
    dest = DATA_RAW / f"{accession}.gb"
    params = {
        "db": "nuccore",
        "id": accession,
        "rettype": "gb",
        "retmode": "text",
        "tool": NCBI_TOOL,
    }
    url = _download(EUTILS, dest, params=params)
    _record(dest.name, dest, url, rows)
    time.sleep(0.4)  # stay under the NCBI rate limit for unauthenticated use
    return dest


def fetch_uniprot(accession: str, rows: list[list[str]]) -> Path:
    """Fetch a UniProt record as a flat file.

    Flat-file rather than FASTA or JSON, because the FT (feature table) lines
    carry the curated domain boundaries. The HMG-box range from this file is
    the independent annotation used to check boundaries derived from primers.
    """
    dest = DATA_RAW / f"{accession}.txt"
    url = _download(UNIPROT.format(acc=accession), dest)
    _record(dest.name, dest, url, rows)
    return dest


def fetch_supplementary(pmcid: str, rows: list[list[str]]) -> Path:
    """Fetch the supplementary archive for an open-access article."""
    dest = DATA_RAW / f"{pmcid}_supplementary.zip"
    url = _download(EUROPEPMC_SUPP.format(pmcid=pmcid), dest)
    _record(dest.name, dest, url, rows)
    return dest


def write_manifest(rows: list[list[str]]) -> None:
    ensure_dirs()
    lines = ["\t".join(MANIFEST_HEADER)]
    lines += ["\t".join(r) for r in sorted(rows)]
    MANIFEST.write_text("\n".join(lines) + "\n", encoding="utf-8")
