# concordance — literature-blind benchmark scaffold

Machinery to replace the circular §3.7 concordance analysis with a defensible one: recovery of an
**independently assembled, results-blind** reference set, **with misses reported** and an **enrichment
p-value**. This folder provides the protocol, the reference schema, a grounded starter set, and the
enrichment engine. It does **not** invent literature — the reference census is built by hand per the
protocol.

## Contents
- `PROTOCOL_literature_blind_concordance.md` — the method (assemble blind → freeze → run → report).
- `reference_template.csv` — the schema to fill (every row needs a PMID/DOI and a rationale).
- `reference_seed_grounded.csv` — a **starter** reference set, externally grounded (BioGRID ORCS / ChEMBL /
  PubMed, 2026-07-05) and independent of ΔpS′. **Incomplete** — expand per protocol before using as a benchmark.
- `concordance_enrichment.py` — resolves the reference to PRISM compounds (by name and/or target/MOA),
  computes recovery + misses + hypergeometric and permutation enrichment against the real candidate lists.
- `results/concordance_report.csv` — output.

## Run
```bash
python concordance_enrichment.py --reference reference_seed_grounded.csv    # or your frozen reference_set.csv
```
(Requires `../results/` from `run_all.py`. Uses scipy if present, else an exact hypergeometric fallback.)

## Demonstration on the grounded starter set (illustrative — NOT the final benchmark)

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
