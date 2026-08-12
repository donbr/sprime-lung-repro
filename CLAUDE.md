# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A deterministic, checksum-guarded reproduction of an S′ (drug-response) synthetic-lethality analysis on
public PRISM + DepMap data for lung cancer cell lines. It is a *scientific-controls* repo: most of the code
exists to test whether the candidate lists survive a permutation null, a general-sensitivity control, a
bootstrap CI gate, and a literature-blind concordance benchmark. The honest headline (see `README.md`) is
that they mostly do **not** — only RB1 rises marginally above the null. Do not "improve" results by
loosening a gate; the null result is the finding.

## Relationship to the referee review

This code is the evidence apparatus for a referee review of manuscript V4 (an external document, not in
this repo). Almost every script exists to substantiate one numbered issue in that review, and the committed
CSVs in `results/` are the exact numbers quoted in it. That is why the summary CSVs are committed at all —
treat them as cited figures, not as scratch output, and regenerate the whole chain rather than one stage if
they must change.

| Review issue | What it demands | Implementation | Committed result |
|---|---|---|---|
| B1 concordance is circular | blind reference set, report misses, enrichment p | `concordance/` | RB1 p=0.0013, TP53 p=5.6e-08, PTEN p=0.30, CDKN2A untestable |
| B2 no null model | candidate sizes, permutation FDR, bootstrap gate | `blocking_analyses.py` §1, `bootstrap_ci_gate.py` | 97/48/94/16; FDR 1.00/0.87/0.68/1.27; survivors 26/3/16/1 |
| B3 sensitivity confound | per-line median S′ split by genotype | `blocking_analyses.py` §2 | offsets −0.02 to −0.13, corr 0.996–1.000 |
| B4 worked example wrong | recompute to S′ ≈ 6.70 | `sprime_pipeline.py` anchor, `test_sprime_worked_example` | 6.704 |
| M3 fold-change claim | ΔpS′ ≤ −2 *is* ≈7.4-fold | `sprime_core.fold_change`, `test_fold_change_converges` | e² = 7.389 |
| M9 RNAi reframing | emit two-sided + WT-direction q-values | `demeter_validation.py` | added in `01425ea` |

The manuscript's Supplement 1 claimed S′ = 7.382508; the review showed that arithmetic is wrong and
self-inconsistent. `test_sprime_worked_example` (`abs(s - 6.70) < 0.05`) is that correction frozen as a
regression test — the one test whose failure would mean the manuscript was right and this code is wrong.

### Review items with no implementation here

Do not assume a control exists because the review asks for it:

- **M1 fit-quality / minimum-|E_max| gate — the significant gap.** Flat curves make EC₅₀ unidentifiable
  while |S′| explodes, which is the likely source of the non-credible hits (aspirin, ranitidine). The
  review states explicitly that **the bootstrap CI gate does not substitute** — aspirin and MK-2206 survive
  it because their artifactual S′ is stable, not noisy. Such a filter would have to run *before*
  `sprime_core.sprime` is called in `sprime_pipeline.py`.
- **M2** EC₅₀ censoring at the tested dose range (8 steps, 4-fold from 10 µM, to ≈0.61 nM).
- **M6** copy-number loss — genotype calls read the damaging-mutation matrix only, which is precisely why
  the CDKN2A arm is weakest (predominantly homozygous deletion). `CRISPRGeneDependency.csv` is noted in
  `DOWNLOAD_CHECKLIST.md` but deliberately not wired into any script.
- **M4** clustering on `(pS′_WT, pS′_MUT)` instead of the shared-term embedding; **M5** Benjamini–Hochberg
  for the main significance analysis (`bh_fdr` exists, but only inside `demeter_validation.py`);
  **M8** an RB1 × TP53 interaction term.

`concordance/reference_seed_grounded.csv` also has a provenance hole: 5 of its 7 rows carry neither PMID nor
DOI, and `search_terms` is empty on all 7, though the protocol makes both mandatory. B1's remedy rests on
documented blind assembly, so those fields are load-bearing, not bookkeeping.

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
