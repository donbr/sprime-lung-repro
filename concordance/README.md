# concordance — literature-blind benchmark

Machinery to replace the circular §3.7 concordance analysis with a defensible one: recovery of a
**structurally blinded** reference set, **with misses reported** and an **enrichment p-value**. This folder provides the protocol, the reference schema, a grounded starter set, and the
enrichment engine. It does **not** invent literature — the reference census is built by hand per the
protocol.

## Contents

**Method and schema**
- `PROTOCOL_literature_blind_concordance.md` — assemble blind, freeze, run, report.
- `PRESPEC_second_census_2026-09-06.md` — the decision rule for comparing two censuses, committed before
  the second census existed.
- `reference_template.csv` — the row schema (every row needs a PMID/DOI, a query string and a rationale).

**Censuses** (frozen and md5-pinned; `.gitattributes` marks them `-text` so the hashes hold on every platform)
- `reference_set_2026-08-31{,_directional}.csv` plus `BLIND_CENSUS_2026-08-31.md` and its notes — the
  **benchmark of record**. Its freeze commit is **retroactive** (`9ca5046`, six days after scoring).
- `reference_set_2026-09-06{,_directional}.csv` plus `CENSUS_NOTES_2026-09-06.md` and
  `census_2026-09-06_raw/` — the second census. Its freeze commit **precedes** scoring
  (`38ce6f6` then `0fb42f8`), and the raw per-agent output is committed so the verbatim assembly can be
  re-derived by a reviewer.
- `reference_seed_grounded.csv` — the 7-row starter set. **Superseded**, illustrative only.
- `reference_annotations_2026-08-31.csv` — post-hoc tissue and caveat columns, presentation only.

**Code**
- `concordance_enrichment.py` — the engine: resolves reference rows to PRISM compounds, computes recovery,
  misses, hypergeometric and permutation enrichment.
- `assemble_census.py` — verbatim assembly of per-agent output into a frozen census.
- `build_suppl7_table1.py` — generates `SUPPL7_TABLE1_<GENE>.md`; self-verifying, fails closed.
- `compare_censuses.py` — applies the pre-specified rule, with nesting and rate diagnostics.
- `census_agreement.py` — target- and compound-level agreement between two censuses.

**Reports** — `RESULT_second_census_2026-09-06.md`, `SUPPL7_TABLE1_{RB1,PTEN,CDKN2A,TP53}.md`, `results/`.

## Run
```bash
# the benchmark of record
uv run --locked python concordance_enrichment.py \
    --reference reference_set_2026-08-31_directional.csv \
    --out results/2026-08-31_blind --perm 10000
uv run --locked python build_suppl7_table1.py --genotype RB1
uv run --locked python compare_censuses.py      # both-must-clear rule plus diagnostics
uv run --locked python census_agreement.py      # census-to-census agreement
```
(Requires `../results/` from `run_all.py`. Requires scipy — `scipy.stats.hypergeom` computes the
hypergeometric enrichment; there is no fallback, and the script exits 4 with an install message if
scipy is missing.)

## The benchmark of record — 2026-08-31 literature-blind census

The protocol was executed against a 93-row census frozen and md5-hashed before scoring (95 rows before two
inverse-direction entries are excluded by a rule the census agent wrote before any result existed). This is
the run to quote. Source: `results/2026-08-31_blind/concordance_report_primary_directional.csv`.

| genotype | reference (in universe) | candidates | universe | recovered | recovery | hypergeometric p | permutation p |
|---|---|---|---|---|---|---|---|
| PTEN | 39 | 97 | 883 | 2 | 5% | 0.94 | 0.94 |
| CDKN2A | 12 | 48 | 1402 | 0 | 0% | 1 | 1 |
| RB1 | 94 | 94 | 1360 | 13 | 14% | **0.0099** | **0.0091** |
| TP53 | 61 | 16 | 1402 | 1 | 2% | 0.51 | 0.52 |

The blinding here is **structural**: the assembly step was initiated from a results-aware context and
agent isolation was enforced by instruction, not by a sandbox. It is not an independent replication. See
`RESULT_second_census_2026-09-06.md` §6.

**Only RB1 clears chance, and one target class carries it.** Removing AURKA and AURKB from the reference set
leaves 6 of 69 recovered at p = 0.34. The defensible claim is that RB1-loss lines are selectively sensitive
to Aurora kinase inhibitors, not that the window recovers RB1 biology broadly. Full per-target breakdown,
misses, leave-one-class-out, threshold sweep and multiple-testing correction are generated into
`SUPPL7_TABLE1_RB1.md` by `build_suppl7_table1.py`.

**RB1 passes the same gate against a second blinded census (2026-09-06):** 13/73 at p = 0.00097, under a
rule pre-specified before that census existed. Read that with §2 of `RESULT_second_census_2026-09-06.md`:
census 2's RB1 reference set is a strict subset of census 1's, so the identical recovered set and the
smaller p-value are consequences of the nesting, not independent corroboration. What replicated is the
target nomination. The Aurora narrowing does not replicate under a rate test (Fisher p = 0.024 then 0.095).
PTEN, CDKN2A and TP53 are concordant negatives. Census agreement is only moderate (Jaccard 0.39 to 0.70 on
targets), itself a finding about how noisy a single census is. See also
`PRESPEC_second_census_2026-09-06.md`.

**Three of four genotypes fail**, which is the evidence that the benchmark is not rigged: the same procedure
that returns a positive for RB1 returns chance for PTEN, CDKN2A and TP53.

## Superseded first pass — the 7-row starter set (illustrative only)

**Do not quote these numbers.** Retained because the way this failed is the argument for the census above:
TP53's p = 5.6e-08 came off five reference compounds that were essentially one target family, and collapsed
to 1/61 at p = 0.51 once a real census was assembled. Source: `results/concordance_report.csv`.

| genotype | reference (in universe) | candidates | universe | recovered | recovery | hypergeometric p | permutation p |
|---|---|---|---|---|---|---|---|
| RB1 | 49 | 94 | 1360 | 10 | 20% | 0.0013 | 0.0010 |
| TP53 | 5 | 16 | 1402 | 4 | 80% | 5.6e-08 | 1e-4 |
| PTEN | 10 | 97 | 883 | 2 | 20% | 0.30 | 0.30 |
| CDKN2A | 0 | 48 | 1402 | 0 | n/a | — | — |

**What the starter run showed, and how the census revised it.** All past tense; none of these are current
findings.
- RB1 appeared enriched at p ≈ 0.001 off 49 reference compounds. The census of record gives **0.0099** off
  94, so the direction held and the magnitude did not.
- TP53 appeared enriched at p ≈ 6e-8 off **five** reference compounds that were essentially the KIF11/Eg5
  family. Against a 61-compound census TP53 recovery is **1/61, p = 0.51**, which is chance, and 0/38 in the
  second census. The seed figure was an artifact of a reference set small enough to be dominated by one
  target family. The TP53–KIF11 signal remains a real internal result of this dataset and is **not**
  literature-corroborated.
- PTEN was unsupported at p = 0.30 and remains unsupported at **0.94**.
- CDKN2A had no starter entries at all. Both censuses carry CDKN2A rows; the arm is still uninformative, but
  now for a documented reason — its dominant MTAP/PRMT5 agents are absent from the PRISM 19Q4 library.
- The engine reported the misses then and reports them now. That has not changed, and it is the point.

## Caveats on the superseded starter set
1. It was **incomplete** (no CDKN2A; a handful of targets per gene) and was assembled during this project.
   Both gaps are closed by the 2026-08-31 census, so this caveat is historical.

## Caveats that apply to the census of record
1. Target-to-compound expansion uses PRISM's own MOA/target annotations, which the review flagged as
   sometimes wrong (barasertib is the known example). Every enrichment p-value inherits those errors.
   `SUPPL7_TABLE1_RB1.md` §6 prints the matched annotation text for each recovered compound for exactly
   this reason.
2. Report recovery **with** the enrichment p and the misses — never recovery alone.
3. The blinding is **structural**, not absolute, and neither census is an independent replication.
