# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A deterministic, checksum-guarded reproduction of an S′ (drug-response) synthetic-lethality analysis on
public PRISM + DepMap data for lung cancer cell lines. It is a *scientific-controls* repo: most of the code
exists to test whether the candidate lists survive a permutation null, a general-sensitivity control, a
bootstrap CI gate, and a literature-blind concordance benchmark. The honest headline (see `README.md`) is
that they mostly do **not** — only RB1 rises marginally above the null. Do not "improve" results by
loosening a gate; the null result is the finding.

## Commands

Commands below use `python` as the docs do; on this machine only `python3` is on PATH (numpy/pandas are
already importable there). `run_all.py` shells out to `sys.executable`, so the stages stay consistent.

```bash
pip install -r requirements.txt

python fetch_data.py                  # download + md5-verify ~560 MB of inputs into data_sources/
python fetch_data.py --only demeter2_rnai        # just the optional DEMETER2 matrix
python run_all.py                     # STEP 1 pipeline → STEP 2 blocking → STEP 3 bootstrap CI

# individual stages (all take --out/--derived, default ./results, runnable from any cwd)
python sprime_pipeline.py [--data DIR] [--mutations FILE] [--skip-checksum]
python blocking_analyses.py [--perm 2000] [--seed 20260811]
python bootstrap_ci_gate.py [--B 2000] [--seed 20260811]
python demeter_validation.py [--genes AURKB PLK1 ...] [--reference concordance/reference_seed_grounded.csv]
python concordance/concordance_enrichment.py --reference concordance/reference_seed_grounded.csv

# tests — plain asserts, no pytest in requirements.txt; runs without the gated data
python tests/test_synthetic.py                        # what CI runs; prints "ALL PASSED"
python -m pytest tests/test_synthetic.py::test_sprime_sign     # single test, if pytest is installed

# what CI also does — keep this passing, it is the only check that runs on every push
python -m py_compile _common.py sprime_core.py sprime_pipeline.py blocking_analyses.py \
  bootstrap_ci_gate.py demeter_validation.py fetch_data.py run_all.py concordance/concordance_enrichment.py
```

CI (`.github/workflows/smoke.yml`, Python 3.10 + 3.12) can only run the synthetic smoke test — the real
inputs are ~400 MB and gated. Real-data reproduction is a local step, always.

## Data flow

```
fetch_data.py ──► data_sources/            (gitignored; md5-pinned public inputs)
                       │
sprime_pipeline.py ────┴──► results/sprime_lung_pairs.csv   (gitignored — large, regenerate)
                            results/lung_genotypes.csv      (committed)
                       ┌────────────┴────────────┬──────────────────────┐
        blocking_analyses.py   bootstrap_ci_gate.py   concordance_enrichment.py / demeter_validation.py
```

Everything downstream of `sprime_pipeline.py` reads only those two derived CSVs and rebuilds the
compound × cell-line S′ matrix itself via `pairs.pivot_table(index="name", columns="depmap_id",
values="sprime", aggfunc="mean")`. If you change that pivot in one script, change it in all of them.

Small summary CSVs in `results/` are committed; `results/sprime_lung_pairs.csv` is gitignored. A stale
committed summary is a real risk — regenerate the whole chain with `run_all.py` rather than one stage.

## Things that will bite you

**The SL window is duplicated.** `sprime_core.py` documents itself as the single source of truth
(`DELTA_LE = -2.0`, `MIN_LINES = 3`, `passes_window`), but `blocking_analyses.py`, `bootstrap_ci_gate.py`,
and `concordance/concordance_enrichment.py` each re-implement the window inline with a hardcoded `-2` and
their own module-level `MINN = 3`. Changing `sprime_core` alone silently does nothing to the real analysis.
Prefer routing the duplicates through `sprime_core` over editing constants in four places.

**Byte-reproducibility is a maintained invariant, not an accident.** Derived tables must be identical
across environments: `sort_values(..., kind="stable")` (the default quicksort leaves tie order
unspecified, which would change which replicate `drop_duplicates(keep="last")` retains), a canonical row
order before every `to_csv`, and the fixed seed `20260811` in all three RNG-using scripts. Don't drop a
`kind="stable"` or reorder a write.

**Checksums are pinned in three places** and must move together when a release is repinned:
`fetch_data.SOURCES` (article_id + version + md5 + size), `sprime_pipeline.MD5` (PRISM, and both the 24Q2
and 24Q4 mutation matrices — 24Q2 is the analyzed release, 24Q4 is accepted-and-reported), and
`demeter_validation.DEMETER_MD5`. `fetch_data.py` resolves through the *versioned* figshare endpoint on
purpose, quarantines a failed download as `.bad`, and only `os.replace`s into place after verification.

**No network at analysis runtime, ever.** The bio-research MCP connectors (PubMed / ChEMBL / BioGRID ORCS)
belong strictly upstream at the curation boundary — used in an interactive session to build frozen input
files like `concordance/reference_set.csv`, never called from pipeline code. See `CONNECTORS.md`.

**`_common.py` must stay stdlib-only.** `run_all.py` and `fetch_data.py` import it and must remain
runnable without numpy/pandas — that is why it can't live in `sprime_core.py`. Every entry point calls
`safe_stdout()` immediately after importing it, because the output contains `ΔpS′ ≤ −2` and a cp1252
console would otherwise raise `UnicodeEncodeError` *after* the CSVs are written. Any new script that
prints S′ notation needs the same call, and any file written with those characters needs an explicit
`encoding="utf-8"`.

**Exit codes carry meaning.** `sprime_pipeline.py`: 0 = ok, 1 = a validation anchor mismatched (continue
but review), 2 = missing input, 3 = checksum/wrong release. `run_all.py` aborts on ≥ 2 and only warns on 1.

## Validation anchors

These are correctness checks, not decoration — if a change breaks one, the change is wrong:
doxorubicin/A549 → S′ ≈ 6.70; 94 lung lines; cohort sizes near Suppl-9 (`EXPECTED_COHORTS` in
`sprime_pipeline.py`); genotype encoding in the damaging-mutation matrix is `0 = WT, 2 = mutant,
1 = excluded`.

## Concordance benchmark

`concordance/` is a *scaffold*, not a finished benchmark. The cardinal rule in
`PROTOCOL_literature_blind_concordance.md`: the reference set must be assembled from literature and frozen
**before** anyone looks at ΔpS′ — adding a compound because it scored well invalidates the benchmark.
`reference_seed_grounded.csv` is an incomplete starter set (no CDKN2A entries). Always report recovery
together with the enrichment p-value and the misses; recovery alone is what made the original analysis
circular.
