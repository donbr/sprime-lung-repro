# concordance — literature-blind benchmark scaffold

Machinery to replace the circular §3.7 concordance analysis with a defensible one: recovery of an
**independently assembled, results-blind** reference set, **with misses reported** and an **enrichment
p-value**. This folder provides the protocol, the reference schema, a grounded starter set, and the
enrichment engine. It does **not** invent literature — the reference census is built by hand per the
protocol.

## Contents
- `PROTOCOL_literature_blind_concordance.md` — the method (assemble blind → freeze → run → report).
- `reference_template.csv` — the schema to fill (every row needs a PMID/DOI and a rationale).
- `reference_seed_grounded.csv` — the original **starter** reference set (BioGRID ORCS / ChEMBL / PubMed,
  2026-07-05). Superseded for reporting by the grounded sets below; kept for provenance.
- `concordance_enrichment.py` — resolves the reference to PRISM compounds (by name and/or target/MOA),
  computes recovery + misses + hypergeometric and permutation enrichment against the real candidate lists.
- `results/concordance_report.csv` — output of the starter set.

### The Supplement 7 rebuild (worked, PubMed-grounded — start here)
- **`WALKTHROUGH_RB1_concordance_rebuild.md`** — a standalone, step-by-step rebuild of Supplement 7 / Table 1,
  worked in full on RB1. Read this first; it turns the circular table into a real benchmark.
- **`CONCORDANCE_REBUILD_all_genotypes.md`** — the same procedure applied to all four genotypes, with the
  honest results table and per-genotype notes.
- `reference_set_RB1.csv` — the frozen, PubMed-verified RB1 reference set (with the documented PARP1 exclusion).
- `reference_set_v1.csv` — the frozen, PubMed-verified reference set for **all four** genotypes.
- `results_RB1/` and `results_v1/concordance_report.csv` — outputs of the grounded sets.
- `OB_RESEARCH_competency_questions.md` — which biosciences-plugin competency questions map to this work, and
  a genuine (BioGRID genetic + STRING + PubMed + trials) validation of the RB1×PARP1 exclusion.

## Run
```bash
python concordance_enrichment.py --reference reference_seed_grounded.csv    # or your frozen reference_set.csv
```
(Requires `../results/` from `run_all.py`. Requires scipy — `scipy.stats.hypergeom` computes the
hypergeometric enrichment; there is no fallback, and the script exits 4 with an install message if
scipy is missing.)

## Results on the grounded reference set (`reference_set_v1.csv`, PubMed-verified, frozen 2026-09-02)

Every target carries a verified RB1/PTEN/CDKN2A/TP53-selectivity citation; targets expand to all PRISM
compounds annotated to them, restricted to the tested cohort. Full write-up: `CONCORDANCE_REBUILD_all_genotypes.md`.

| genotype | reference (in universe) | candidates | universe | recovered | recovery | hypergeometric p | permutation p | verdict |
|---|---|---|---|---|---|---|---|---|
| RB1 | 42 | 94 | 1360 | 8 | 19% | **0.0064** | **0.0067** | significant |
| TP53 | 9 | 16 | 1402 | 1 | 11% | 0.098 | 0.098 | borderline |
| PTEN | 22 | 97 | 883 | 3 | 14% | 0.44 | 0.44 | not significant |
| CDKN2A | 12 | 48 | 1402 | 0 | 0% | 1.0 | 1.0 | null / partly untestable |

**The honest headline: only RB1 clears chance.** This supersedes the circular §3.7 result (75–94% recovery),
which was an artifact of using the window's own output as the reference. Assembled blind, only RB1 is enriched.
- **RB1** — enriched ~2.7× over chance (p ≈ 0.006); the one genotype the concordance supports, and it agrees
  with the independent RB–E2F genetic-dependency result (Supplement 8).
- **TP53** — borderline (p ≈ 0.10) and **sensitive to the spindle/KIF11 target**: an earlier ungrounded seed
  that included KIF11 scored TP53 as strongly enriched, but no clean primary TP53-selective KIF11 citation was
  verified, so KIF11 is excluded and TP53 falls to borderline. Ground it or report it as borderline.
- **PTEN** — not supported (p = 0.44); the canonical PI3K/AKT/PARP drugs are tested but not window-selective.
- **CDKN2A** — null (CDK4/6 controls all missed, correctly) and partly untestable (PRMT5/MAT2A, the best
  CDKN2A-co-deletion SL, has no compound in PRISM 19Q4).
- The engine **reports the misses** (e.g. alisertib, BI-2536, volasertib, AZD7762 for RB1) — the informative
  rows a real benchmark must show.

## Demonstration on the grounded starter set (illustrative — NOT the final benchmark)

> **Superseded for reporting** by the grounded rebuild above. This section documents the original
> starter set (`reference_seed_grounded.csv`) and is retained for provenance: it is the table
> `concordance/results/concordance_report.csv` still carries, and it shows why the starter set
> could not serve as the benchmark.

Reference targets expanded to all PRISM compounds annotated to them, restricted to the tested cohort:

| genotype | reference (in universe) | candidates | universe | recovered | recovery | hypergeometric p | permutation p |
|---|---|---|---|---|---|---|---|
| RB1 | 49 | 94 | 1360 | 10 | 20% | **0.0013** | **0.0010** |
| TP53 | 5 | 16 | 1402 | 4 | 80% | **5.6e-08** | **1e-4** |
| PTEN | 10 | 97 | 883 | 2 | 20% | 0.30 | 0.30 |
| CDKN2A | 0 | 48 | 1402 | 0 | n/a | — | — |

**What this already shows** (and why it is more defensible than the circular 100%):
- **RB1 (Aurora/PLK targets) is enriched beyond chance** (p ≈ 0.001) — a real, falsifiable signal, and one
  corroborated by independent literature on Aurora-kinase synthetic lethality with RB1 loss (see
  `docs/evidence.md` for the citations), even though the *overall* candidate lists sit near the permutation
  null (see `../results/candidate_null.csv` and the headline table in `../README.md`).
- **TP53 (KIF11) is also enriched beyond chance** (p ≈ 6e-8), and the enrichment is real and reproducible —
  but it has **no independent literature support**: no PubMed-indexed study demonstrates TP53-mutant-selective
  sensitivity to KIF11/Eg5 inhibitors, and KIF11 is broadly common-essential rather than genotype-selective
  (see `CONNECTORS.md`, and the `inclusion_rationale` on the KIF11 row of `reference_seed_grounded.csv`
  itself). TP53's enrichment should therefore be read as an internal empirical finding of this dataset, not
  as corroboration of known biology.
  The honest read: the window recovers literature-corroborated biology for RB1 (Aurora/PLK in RB1-loss) and a
  reproducible but as-yet-uncorroborated enrichment for TP53 (KIF11), while not being a genome-wide selective
  classifier either way.
- **PTEN concordance is not supported** by the blind test (p = 0.30) — do not claim it as validation.
- **CDKN2A cannot be benchmarked** from the starter set (no entries) — add CDKN2A literature or report that
  its selective-SL evidence is too limited to test.
- The engine **reports the misses** (e.g. many Aurora/PLK inhibitors like volasertib, alisertib, BI-2536
  for RB1) — the informative rows a real benchmark must show.

## Caveats before treating this as the benchmark
1. The starter set is **incomplete** (no CDKN2A; a handful of targets per gene) and was assembled during this
   project — blind to ΔpS′, but not a full independent census. Expand it per the protocol and **freeze with a
   timestamp** before reporting.
2. Target→compound expansion uses PRISM's own MOA/target annotations, which the review flagged as sometimes
   wrong (e.g. barasertib mis-annotated). Spot-check the resolved compound lists.
3. Report recovery **with** the enrichment p and the misses — never recovery alone.
