# Download checklist — S′ lung synthetic-lethality inputs

Two public DepMap files are needed. Put them in `data_sources/` at the root of this repo — the same
place `python fetch_data.py` writes them — then run `python run_all.py`. (`data_sources/` is
gitignored; if you already keep the inputs in a `data_sources/` directory *beside* the repo, that
layout is still detected, or pass `--data DIR` explicitly.) The pipeline **verifies every file by md5
before doing anything**, so the wrong release cannot slip in.

## What to download (DepMap portal → Downloads → "All Downloads")

<https://depmap.org/portal/download/all/>

| # | Portal selection | Portal file name | Save as (in `data_sources/`) | Size (bytes) | md5 |
|---|---|---|---|---|---|
| 1 | **PRISM Repurposing 19Q4** → *Secondary screen* | `secondary-screen-dose-response-curve-parameters.csv` | `secondary-screen-dose-response-curve-parameters.csv` | 264,340,589 | `e629b9d505ad3d6bf65fde96f1c54bee` |
| 2 | **DepMap Public 24Q2** → *Omics → Somatic mutations* | `OmicsSomaticMutationsMatrixDamaging.csv` | `OmicsSomaticMutationsMatrixDamaging.csv` | 135,585,447 | `02f3568b71af0ca3e8d10e681eefac86` |

**Release is the trap — pick the right one:**
- The mutation matrix must be **24Q2** (`02f3568b71af0ca3e8d10e681eefac86`). It is the release the paper's
  analysis was actually run on.
- The **24Q4** file has the *same file name* but a different checksum
  (`cb20fdbe1cf3b9b0d8ed4f53e1f399b6`, 147,655,356 bytes) — do **not** substitute it silently. Verified
  head-to-head, 24Q2 and 24Q4 give identical PTEN/CDKN2A/RB1/TP53 calls for the 94 analyzed lung lines, so
  the numbers do not change; but the deposit and the manuscript must cite whichever file is actually present.
  If you deliberately use 24Q4, save it as `OmicsSomaticMutationsMatrixDamaging_24q4.csv` and pass
  `--mutations OmicsSomaticMutationsMatrixDamaging_24q4.csv` (the pipeline will detect and report the release).

## Optional (only if re-running Supplement 8 genetic-dependency validation)

| Portal selection | File | Notes |
|---|---|---|
| DEMETER2 (combined RNAi) | combined RNAi gene-dependency | negative = dependent; align sign before use |
| DepMap CRISPR (24Q2) `CRISPRGeneDependency.csv` | gene-dependency probabilities | positive = dependent |

## Verify after download

```bash
cd data_sources
md5sum secondary-screen-dose-response-curve-parameters.csv   # expect e629b9d505ad3d6bf65fde96f1c54bee
md5sum OmicsSomaticMutationsMatrixDamaging.csv               # expect 02f3568b71af0ca3e8d10e681eefac86
# Windows:  certutil -hashfile <file> MD5
```

Both files are redistributed under DepMap terms; keep them out of version control (they are large).
Provenance: PRISM methodology — Corsello et al. 2020, *Nat Cancer*, PMID 32613204; DepMap 24Q2 figshare
doi:10.25452/figshare.plus.25880521.v1; DepMap 19Q4 figshare doi:10.6084/m9.figshare.11384241.v2.
