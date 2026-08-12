# sprime-lung-repro

**Reproducible S′ analysis and statistical controls for genotype-selective drug vulnerabilities in lung
cancer cell lines**, computed from public PRISM (drug response) and DepMap (mutations) data.

This repository builds the S′ / pS′ / ΔpS′ operational drug-response metrics per compound–cell-line pair,
calls tumor-suppressor genotypes (PTEN, CDKN2A, RB1, TP53), and runs the statistical controls needed to
interpret candidate synthetic-lethal lists: a **label-permutation null**, a **line-centring
(general-sensitivity) control**, a **per-compound bootstrap confidence-interval gate**, and a scaffold for a
**literature-blind concordance benchmark**. Everything is deterministic (fixed seed) and checksum-guarded.

> The metric: **S′ = asinh((E_max / EC₅₀) × 1 µM)** on the percent E_max scale; **pS′** is the cohort mean;
> **ΔpS′ = pS′_WT − pS′_mutant**. A candidate requires pS′_WT > 0, pS′_mutant > 0, ΔpS′ ≤ −2.

## Quickstart

```bash
pip install -r requirements.txt
python fetch_data.py          # download + md5-verify the public inputs into data_sources/ (see below)
python run_all.py             # build S′ + genotypes, then all three statistical controls
```

`run_all.py` executes: **(1)** `sprime_pipeline.py` (build + validate), **(2)** `blocking_analyses.py`
(candidate sizes, permutation null, line-centring), **(3)** `bootstrap_ci_gate.py`. The optional
literature-blind concordance benchmark and the DEMETER2 genetic-dependency validation are separate commands
(below). Outputs land in `results/` as machine-readable CSVs.

If you prefer to download by hand, `DOWNLOAD_CHECKLIST.md` lists the exact portal selections, filenames and
md5s; `fetch_data.py` automates the same thing and skips any file already present with the right checksum.

## What it validates on the real data
- **Metric:** doxorubicin/A549 → S′ = 6.704 (an internal correctness check).
- **Cohorts:** 94 lung lines; RB1 84/8 and PTEN 90/3 reproduce the published cohorts.
- **Release:** DepMap 24Q2 and 24Q4 give identical genotype calls for the analyzed genes (a
  citation-consistency matter, not a results one).

## Headline results (from `results/`)
| genotype | candidates | permutation FDR | survive bootstrap CI ≤ −2 |
|---|---|---|---|
| PTEN | 97 | 1.00 | 26 (on n_mut = 3 — fragile) |
| CDKN2A | 48 | 0.87 | 3 |
| RB1 | 94 | 0.68 | 16 |
| TP53 | 16 | 1.27 | 1 |

Only RB1 rises above the permutation null (marginally); the candidate lists are otherwise not distinguishable
from random genotype labels, and thin sharply under a bootstrap-CI gate.

## Layout
```
sprime-lung-repro/
├── fetch_data.py            # deterministic downloader (version-pinned figshare API + md5 verify)
├── DOWNLOAD_CHECKLIST.md    # manual-download alternative, with checksums
├── sprime_core.py           # the metric + SL-window definitions (single source of truth)
├── _common.py               # shared input-dir resolution + console encoding (stdlib only)
├── sprime_pipeline.py       # build S′ + genotype calls + validation → results/
├── blocking_analyses.py     # permutation null + line-centring
├── bootstrap_ci_gate.py     # per-compound bootstrap CI gate
├── demeter_validation.py    # DEMETER2 RNAi genetic-dependency validation (needs the DEMETER2 file)
├── concordance/             # literature-blind concordance benchmark scaffold (protocol + engine)
├── CONNECTORS.md            # how the bio-research MCP connectors support the curation steps
├── requirements.txt · run_all.py · tests/ · .github/workflows/
└── data_sources/            # (gitignored) the large public inputs go here
```

## Data & licensing
Input data are public but redistributed under DepMap terms and are **not committed** (gitignored). Sources
and checksums: `DOWNLOAD_CHECKLIST.md`. Every input is resolved through a **version-pinned** figshare record
and verified against a hard-pinned md5 before use, so a later data release cannot silently substitute itself;
a file that fails verification is quarantined rather than left where the pipeline would read it.
PRISM methodology: Corsello et al. 2020, *Nat Cancer*, PMID 32613204.
Code is released under the MIT License (`LICENSE`). Mint a Zenodo DOI on a tagged release for citation.

CI runs a synthetic-data smoke test only (the real 400 MB inputs cannot live in CI); see
`.github/workflows/smoke.yml`.

## Documentation
`docs/` explains the analysis for a reader arriving cold: [`docs/method.md`](docs/method.md) for the S′
metric and genotype calling, [`docs/evidence.md`](docs/evidence.md) for the four statistical controls and
what each established, and [`docs/scope.md`](docs/scope.md) for the analyses this repository deliberately
does not perform. Start at [`docs/README.md`](docs/README.md).
