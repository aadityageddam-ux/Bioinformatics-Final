# Does the SOX17FNV disordered tail act by length, or by sequence?

A reproducible reanalysis of the C-terminal deletion panel published by
Hu *et al.* (2023), *Nucleic Acids Research* **51**, 8934–8956
([10.1093/nar/gkad597](https://doi.org/10.1093/nar/gkad597)).

PUBH 3201, Introduction to Bioinformatics, George Washington University, Fall 2026.
Aaditya Geddam.

## The question

Forcing OCT4, SOX2, KLF4 and MYC into an adult cell reprograms it. SOX2 is the
weak link, and Hu *et al.* engineered a SOX17 variant, SOX17FNV, that
outperforms it. They showed the gain depends on SOX17's intrinsically
disordered C-terminal tail rather than on its DNA-binding domain, then deleted
pieces of that tail and counted the resulting colonies.

What they did not establish is **how** the tail works. Two possibilities.

- **Bulk.** Efficiency tracks how many disordered residues are retained, and it
  does not matter much which ones.
- **Sequence.** Some region does something its length alone cannot explain.

The authors propose electrical charge as the mechanism, note that SOX2 sits
near +13 while SOX17 variants sit near −8, and list testing that correlation as
unfinished work. They published the raw colony counts and the cloning primers
needed to do it. This project does it.

Six properties of the retained tail are tested against normalised
reprogramming efficiency. **Retained length is the null model**; the other five
have to beat it. All six were fixed in `config/analysis.yaml` before any
outcome was examined.

## Why the primers matter

The paper never prints residue numbers for its deletion constructs. The only
published record of where each construct begins and ends is the set of cloning
primers in Supplementary Table S1. So the first real piece of work is recovering
those boundaries from the primer sequences, cross-checking them against UniProt
annotation that was not used to derive them, and publishing the result as an
auditable table. That table does not exist anywhere in the source paper, and
every downstream number depends on it being right.

## Reproducing this

```bash
git clone https://github.com/aadityageddam-ux/Bioinformatics-Final
cd Bioinformatics-Final
make reproduce
```

`make reproduce` installs the pinned environment with
[uv](https://docs.astral.sh/uv/), downloads every input from its public source,
extracts the published tables, and runs the test suite. No manual downloads and
no hand edits at any step.

Raw data are deliberately **not** committed. `data/raw/MANIFEST.tsv` records the
SHA-256 digest, byte count, source URL and retrieval time of every file, so
anyone who re-runs the fetch can prove byte-for-byte that they obtained the same
inputs.

## Data sources

| What | Source | Accession |
|---|---|---|
| Mouse *Sox17* mRNA and protein | NCBI RefSeq | `NM_011441.6` / `NP_035571.1` (419 aa) |
| Mouse *Sox2* mRNA and protein | NCBI RefSeq | `NM_011443.4` / `NP_035573.3` (319 aa) |
| Curated domain boundaries | UniProt | `Q61473`, `P48432` |
| Cloning primers (Table S1) | Europe PMC supplement | `PMC10516664` |
| Raw colony counts (Table S6) | Europe PMC supplement | `PMC10516664` |

Table S6 holds 543 colony counts across 38 construct labels, annotated by
technical replicate, biological replicate, species, delivery system and
detection method.

## Layout

```
config/analysis.yaml   pre-specified parameters, frozen before analysis
src/sox17/             the library; every step lives here
scripts/               numbered entry points, run in order
data/raw/              fetched, never edited, never committed
data/derived/          generated
results/               tables, including the boundary evidence
figures/
tests/
```

## Status

| Phase | What | State |
|---|---|---|
| 0 | Data acquisition, tidy tables | done |
| 1 | Primer to residue boundary recovery, UniProt validation | next |
| 2 | Construct reconstruction, alignment check | |
| 3 | Normalisation, reproduce source Figure 6 | |
| 4 | The six properties, collinearity matrix | |
| 5 | Correlations, partials, bootstrap, region residuals | |
| 6 | Figures and poster | |

## Generative AI

Developed with Claude (Anthropic), model Opus 5. Scope of use is recorded in
`GAI_ACKNOWLEDGMENT.md` and in commit messages.

## Licence

Code is MIT. The supplementary data belong to Hu *et al.* (2023), published open
access in *Nucleic Acids Research*, and are not redistributed here.
