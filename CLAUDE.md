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
| B1 concordance is circular | blind reference set, report misses, enrichment p | `concordance/` | RB1 p=0.0099 (replicated at p=0.00097 in a second blind census), PTEN p=0.94, CDKN2A p=1, TP53 p=0.51 — three concordant negatives |
| B2 no null model | candidate sizes, permutation FDR, bootstrap gate | `blocking_analyses.py` §1, `bootstrap_ci_gate.py` | 97/48/94/16; FDR 1.00/0.87/0.68/1.27; survivors 26/3/16/1 |
| B3 sensitivity confound | per-line median S′ split by genotype | `blocking_analyses.py` §2 | offsets −0.13 to +0.07, corr 0.996–1.000 |
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

`concordance/reference_seed_grounded.csv` has a provenance hole: 5 of its 7 rows carry neither PMID nor
DOI, and `search_terms` is empty on all 7, though the protocol makes both mandatory. **That set is
superseded** by `reference_set_2026-08-31_directional.csv` (93 rows, every row carrying a PMID or DOI, the
query string, a freeze date and a rationale), which is the benchmark of record. The seed set and its results
stay in the tree, labelled, because its TP53 p = 5.6e-08 collapsing to 0.51 against a real census is the
clearest argument for why the census was needed.

## Commands

Commands below use `python` as the docs do; on this machine only `python3` is on PATH (numpy/pandas are
already importable there). `run_all.py` shells out to `sys.executable`, so the stages stay consistent.

```bash
pip install -r requirements.txt       # requirements.txt is generated (uv export); see below
# or: uv sync --locked                # builds a .venv from the hashed uv.lock — same pins, then `uv run ...`

python fetch_data.py                  # download + md5-verify ~560 MB of inputs into data_sources/
python fetch_data.py --only demeter2_rnai        # just the optional DEMETER2 matrix
python run_all.py                     # STEP 1 pipeline → STEP 2 blocking → STEP 3 bootstrap CI

# individual stages (all take --out/--derived, default ./results, runnable from any cwd)
python sprime_pipeline.py [--data DIR] [--mutations FILE] [--skip-checksum]
python blocking_analyses.py [--perm 2000] [--seed 20260811]
python bootstrap_ci_gate.py [--B 2000] [--seed 20260811]
python demeter_validation.py [--genes AURKB PLK1 ...] [--reference concordance/reference_seed_grounded.csv]

# concordance — the benchmark of record is the 2026-08-31 census, NOT reference_seed_grounded.csv
python concordance/concordance_enrichment.py     --reference concordance/reference_set_2026-08-31_directional.csv     --out concordance/results/2026-08-31_blind --perm 10000
python concordance/assemble_census.py                      # verbatim assembly of per-agent output
python concordance/build_suppl7_table1.py --genotype RB1   # self-verifying; fails closed
python concordance/compare_censuses.py                     # both-must-clear rule + diagnostics
python concordance/census_agreement.py                     # census-to-census agreement

# web dashboard & automated browser verification
cd dashboard && npm install && npm run dev            # local web app on http://localhost:5173/
cd dashboard && node verify_ui.js                     # automated Playwright E2E UI & data tests

# tests — plain asserts, no pytest in requirements.txt; runs without the gated data
python tests/test_synthetic.py                        # what CI runs; prints "ALL PASSED"
python -m pytest tests/test_synthetic.py::test_sprime_sign     # single test, if pytest is installed

# what CI also does — keep this passing, it is the only check that runs on every push
python -m py_compile $(git ls-files '*.py')            # discovered, not a hardcoded file list
```

`pyproject.toml` declares `numpy`, `pandas`, `scipy`, and `requests`; `uv.lock` is the hashed, pinned
resolution (`uv lock`); `requirements.txt` is generated from it (`uv export --no-hashes --no-annotate`)
for reviewers on plain pip or conda — regenerate it from `uv.lock`, don't hand-edit it.

CI (`.github/workflows/smoke.yml`) runs two jobs, both on the synthetic smoke test (never on the ~400 MB
gated real inputs — real-data reproduction is a local step, always): `locked` runs `uv sync --locked`
against the committed `uv.lock` (so a stale lock fails CI, not just a local `uv lock --check`); `portability`
installs from the generated `requirements.txt` on Python 3.10 and 3.12 plain pip, so scipy's real code paths
actually execute there too. Both run the compile check, `tests/test_synthetic.py`, and
`tests/test_docs_numbers.py`.

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

**The SL window is genuinely single-sourced.** `sprime_core.py` is imported for `DELTA_LE = -2.0`,
`MIN_LINES = 3`, and `passes_window` by all three consumers — `blocking_analyses.py`,
`bootstrap_ci_gate.py`, and `concordance/concordance_enrichment.py` — with no local duplicate literals
left behind. Changing `sprime_core` now actually changes the real analysis in all three places at once;
do not reintroduce a local `-2` or a module-level `MINN = 3` in any consumer.

**Byte-reproducibility is a maintained invariant, not an accident.** Derived tables must be identical
across environments: `sort_values(..., kind="stable")` (the default quicksort leaves tie order
unspecified, which would change which replicate `drop_duplicates(keep="last")` retains), a canonical row
order before every `to_csv`, and the fixed seed `20260811` in all three RNG-using scripts. Don't drop a
`kind="stable"` or reorder a write. The six **reported** CSV writers (in `blocking_analyses.py`,
`bootstrap_ci_gate.py`, `concordance/concordance_enrichment.py`, `demeter_validation.py`) additionally use
`float_format="%.12g"`, so those committed CSVs no longer vary in their last digit across BLAS builds
(see `docs/verifying.md`). `sprime_pipeline.py`'s writers are deliberately **not** formatted:
`results/sprime_lung_pairs.csv` is an intermediate re-read at full precision by four downstream scripts,
so rounding it would shift every downstream number; `results/lung_genotypes.csv` is already byte-stable
0/1/2 values with nothing to round.

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

**Exit codes carry meaning.** `sprime_pipeline.py`: 0 = ok, 1 = a validation anchor mismatched **or** the
cohort-size check failed (continue but review), 2 = missing input, 3 = checksum/wrong release.
`run_all.py` aborts on ≥ 2 and only warns on 1. `demeter_validation.py` and
`concordance/concordance_enrichment.py` both exit 4 with an install message if scipy is missing —
scipy is a required dependency (`pyproject.toml`), not an optional one, so this should only fire on a
broken environment.

**The docs quote committed results.** `docs/evidence.md`, `docs/method.md`, `README.md`,
`concordance/README.md`, `docs/verifying.md` and **`CLAUDE.md` itself** all reproduce figures from
`results/*.csv`, `concordance/results/concordance_report.csv`,
`concordance/results/2026-08-31_blind/*.csv` and `concordance/results/census_comparison.csv` in markdown
tables, and `tests/test_docs_numbers.py` asserts every one of them matches — it runs in CI. Editing a
figure in this file without updating its CSV (or the reverse) turns CI red; that has already happened once.
`docs/scope.md` and `docs/README.md` are **not** under that check. Regenerating the results baseline therefore requires
updating those tables in the same commit, or the build fails. Numbers the repo does not compute (the 4PL
pathology percentages, the PRISM dilution scheme) are attributed inline and are not covered by the test.

## Validation anchors

These are correctness checks, not decoration — if a change breaks one, the change is wrong:
doxorubicin/A549 → S′ ≈ 6.70; 94 lung lines; cohort sizes near Suppl-9 (`EXPECTED_COHORTS` in
`sprime_pipeline.py`); genotype encoding in the damaging-mutation matrix is `0 = WT, 2 = mutant,
1 = excluded`.

## Concordance benchmark

The cardinal rule in `PROTOCOL_literature_blind_concordance.md`: the reference set must be assembled from
literature and frozen **before** anyone looks at ΔpS′ — adding a compound because it scored well invalidates
the benchmark. Always report recovery together with the enrichment p-value and the misses; recovery alone is
what made the original analysis circular.

**There are two runs in the tree and only one is the benchmark of record.**

| | Reference | Results | Status |
|---|---|---|---|
| Benchmark of record | `reference_set_2026-08-31_directional.csv` (93 rows) | `results/2026-08-31_blind/` | quote this |
| Superseded first pass | `reference_seed_grounded.csv` (7 rows) | `results/concordance_report.csv` | illustrative only, labelled in place |

Do not quote the seed run's figures as findings; its TP53 p = 5.6e-08 collapsed to 0.51 against the census.
Both stay committed, and `tests/test_docs_numbers.py` pins each to the documents that cite it.

`build_suppl7_table1.py` generates the manuscript-facing `SUPPL7_TABLE1_<GENE>.md` from the frozen census.
It imports `candidates` and `token_match` from `concordance_enrichment.py` rather than reimplementing the
window — do not reintroduce a local `-2` or `MINN = 3` there either — and it fails closed, exiting 1 without
writing if any acceptance gate stops reproducing.

**The RB1 result is Aurora-carried, and that is stable across two censuses.** Removing AURKA and AURKB
leaves 6 of 69 recovered at p = 0.34 (`concordance/results/2026-08-31_blind/robustness_RB1.csv`); the
2026-09-06 census gives 6 of 48 at p = 0.11. Any claim built on this benchmark must be Aurora-specific;
§7 of the generated supplement holds the leave-one-class-out, threshold and multiple-testing sweeps.

**A second blinded census was run on 2026-09-06 and RB1 passes the gate again**, 13/94 at p=0.0099 and
13/73 at p=0.00097, under a rule pre-specified in `PRESPEC_second_census_2026-09-06.md` and committed
before the census existed. **Do not over-read it.** Census 2's RB1 reference is a strict subset of census
1's (73 of 94) and both are scored against the same candidate set, so the identical recovered set is
arithmetic and the smaller p comes from nominating 21 fewer compounds that were all misses. Quote 0.0099.
What replicated is the target nomination. The Aurora narrowing does not replicate under a
class-versus-remainder rate test (Fisher 0.024 then 0.095), and `census_comparison.csv` records the
narrowing as `curated-pair-only`, not computed stability. PTEN, CDKN2A and TP53 are concordant negatives.
Do not pool the censuses; the pre-specification forbids it. See `RESULT_second_census_2026-09-06.md`.
