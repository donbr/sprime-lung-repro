# Protocol — literature-blind concordance benchmark

**Purpose.** Replace the current §3.7 concordance analysis, which is circular (the reference set was
assembled from the study's own ΔpS′ values, so 100% of reference compounds already pass the −2 window and
the "recovery" carries no information). This protocol builds the reference set from the **literature alone,
blind to the S′ results**, then measures recovery **and reports misses**, and computes an **enrichment
p-value** so the reader can tell whether recovery beats chance.

The cardinal rule: **the reference set must be frozen before anyone looks at ΔpS′.** If a compound is added
to the reference because it scored well, the benchmark is invalid.

---

## Step 1 — Assemble the reference set (blind)

For each genotype (PTEN, CDKN2A, RB1, TP53), compile compounds/targets with **published, genotype-specific
synthetic-lethal or selective-dependency evidence in cancer**, drawn only from external sources:

- Databases: PubMed, and optionally curated resources (e.g. SynLethDB, DepMap/BioGRID ORCS for
  genetic dependency, ChEMBL for mechanism). Record exactly which were searched.
- Search strategy: record the query strings (e.g. `"RB1" AND ("synthetic lethal" OR "selective dependency")
  AND (lung OR SCLC)`), the date run, and the databases.
- Inclusion criteria: state them up front (e.g. "experimental SL/dependency evidence in a cancer model;
  a druggable target with ≥1 compound in ChEMBL/PRISM"). Record why each entry is included.
- **Do not consult the S′ candidate lists, ΔpS′ values, Supplement 6, or Figure 8 while building this.**

Populate `reference_set.csv` using the schema in `reference_template.csv`. Every row must carry a PMID or
DOI and a one-line rationale. Target-level entries (e.g. "RB1 → AURKA") are expanded automatically to all
PRISM compounds annotated to that target, so you can specify a `target` and leave `compound` blank.

`reference_seed_grounded.csv` is a **starter** — the externally grounded set already assembled from
BioGRID ORCS / ChEMBL / PubMed (2026-07-05), which predates and is independent of the ΔpS′ ranking. It is
**incomplete** (no CDKN2A entries; a handful of targets per gene). Expand it to a genuine literature census
per the criteria above before treating the result as a benchmark.

## Step 2 — Freeze

Commit `reference_set.csv` with a timestamp / git tag **before** running Step 3. Note the freeze date in the
file's `date_frozen` column and in the commit message. This is the audit trail that makes the benchmark
credible.

## Step 3 — Run the benchmark

```
python concordance_enrichment.py --reference reference_set.csv
```

The script (using the already-computed candidate lists in `../results/`):

1. Resolves each reference row to PRISM compounds (by `compound` name and/or by `target` via PRISM's target/
   MOA annotation), restricted to compounds **actually tested** in that genotype's cohort.
2. Reports, per genotype: reference-in-universe (R), candidates (K), tested universe (N), **recovered (k)**,
   **recovery rate**, and the **list of misses** (reference compounds tested but not recovered).
3. Computes enrichment two ways:
   - **Hypergeometric**: p = P(X ≥ k) drawing K candidates from N with R reference compounds present.
   - **Permutation**: draw K random compounds from N, count overlap with R, ≥10,000×; empirical p.

## Step 4 — Report

State recovery **with its enrichment p-value and the misses**, per genotype. A benchmark with no misses is
not a benchmark. Interpretation:
- Enrichment p ≪ 0.05 → the window recovers known biology beyond chance (real validation).
- Enrichment p ≈ chance → recovery is uninformative; do not claim validation from it.

Lead the paper's validation with whatever survives this test plus the independent evidence that does not
depend on ΔpS′ (Supplement 8 genetic dependency; the correct-direction sign recoveries for CDK4/6, MDM2,
KIF11, Aurora).

---

### Why this fixes the problem
The circular version asked "how many compounds selected for strong negative ΔpS′ have strong negative
ΔpS′?" — necessarily 100%. This version asks "of the compounds independent literature says should be
selective, how many does the window recover, and is that more than chance given how many compounds the
window passes overall?" — a question with a real, falsifiable answer.
