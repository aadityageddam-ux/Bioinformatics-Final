# Reproduce the whole study:  make reproduce
#
# Each target depends on the one before it, so `make` alone brings everything
# up to date and skips work that is already done.

PY := uv run python

.PHONY: setup data tables test clean reproduce

setup:            ## install the pinned environment
	uv sync --extra dev

data: data/raw/MANIFEST.tsv   ## download every raw input

data/raw/MANIFEST.tsv: config/analysis.yaml src/sox17/fetch.py scripts/01_fetch_raw.py
	$(PY) scripts/01_fetch_raw.py

tables: data/derived/s1_primers.csv data/derived/s6_colony_counts.csv  ## extract S1 and S6

data/derived/s1_primers.csv data/derived/s6_colony_counts.csv: data/raw/MANIFEST.tsv src/sox17/tables.py scripts/02_extract_tables.py
	$(PY) scripts/02_extract_tables.py

test:             ## run the test suite
	uv run pytest -q

reproduce: setup data tables test

clean:            ## remove everything that can be regenerated
	rm -rf data/derived/* figures/* results/*
	@touch data/derived/.gitkeep
