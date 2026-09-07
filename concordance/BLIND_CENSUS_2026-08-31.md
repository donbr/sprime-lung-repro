# Literature-blind concordance benchmark — run of 2026-08-31

Executes `PROTOCOL_literature_blind_concordance.md` end to end with a reference census built for this
purpose. Supersedes the illustrative run on `reference_seed_grounded.csv` (7 rows) documented in
`README.md`.

**Frozen inputs**

| File | Rows | md5 |
|---|---|---|
| `reference_set_2026-08-31.csv` (full census) | 95 | `a330987d6c02f9cb8826cc65e908301c` |
| `reference_set_2026-08-31_directional.csv` (**primary**) | 93 | `76845dcc6131ab917717c7724da2c420` |

Both frozen, hashed and schema-validated **before** the engine was run: every row carries a target, at
least one of PMID/DOI, the exact query string that surfaced it, `date_frozen`, and a one-line rationale —
the four fields the protocol makes mandatory and which the seed set was missing on 5 of 7 rows.

**Derived inputs:** `run_all.py` output regenerated 2026-08-31 from md5-verified PRISM 19Q4 + DepMap 24Q2;
all six baseline CSVs reproduce byte-identically against the committed baseline. Engine:
`concordance_enrichment.py`, `--perm 10000`, seed 20260811.

---

## How the blind was enforced

The census was built by **four isolated agents, one per genotype**, each in its own context with no access
to this repository, no access to any S′/pS′/ΔpS′ value, and an explicit instruction not to seek out the
manuscript being benchmarked. They had PubMed plus ChEMBL/Open Targets/BioGRID-ORCS for druggability
confirmation only. Their CSV output was assembled **verbatim** — no row was added, removed, reworded or
reordered on the basis of anything known about the results.

**Stated limitation.** The person commissioning the census had previously seen the ΔpS′ results. The blind
therefore rests on the isolation of the four builders and on the verbatim-assembly rule, not on the
commissioner's ignorance. The frozen hashes above, the per-row query strings, and this note are the audit
trail. A fully independent replication would commission the census before any results exist.

**One pre-specified analysis decision.** The RB1 builder returned two rows (CDK4/palbociclib,
CDK6/palbociclib, PMID 38528594) which it flagged in its own rationale as **INVERSE-DIRECTION** — the
sensitive genotype there is RB1-*proficient*. It stated at authoring time that these "should be dropped
rather than counted as positives" if the benchmark scores RB1-loss→sensitivity. That instruction, written
blind, is the decision rule: the **primary** analysis excludes those two rows; the full 95-row census is
reported as a sensitivity analysis. Both are below.

---

## Result — primary (directional census, 93 rows)

| Genotype | Reference in universe | Candidates | Universe | Recovered | Recovery | Hypergeometric p | Permutation p |
|---|---|---|---|---|---|---|---|
| PTEN | 39 | 97 | 883 | 2 | 5% | 0.942 | 0.937 |
| CDKN2A | 12 | 48 | 1402 | 0 | 0% | 1 | 1 |
| **RB1** | **94** | **94** | **1360** | **13** | **14%** | **0.0099** | **0.0091** |
| TP53 | 61 | 16 | 1402 | 1 | 2% | 0.511 | 0.522 |

**Sensitivity (full 95-row census):** RB1 recovery 13/106 = 12%, hypergeometric p = 0.0258, permutation
p = 0.0245. PTEN, CDKN2A and TP53 unchanged. RB1 survives either treatment of the inverse-direction rows.

### What RB1 recovered

`AMG900, KW-2449, NVP-BEZ235, SB-218078, SNS-314, ZM-447439, barasertib, barasertib-HQPA, birinapant,
litronesib, niraparib, olaparib, tozasertib`

Two coherent mechanistic classes: **Aurora kinase** (barasertib, barasertib-HQPA, AMG900, SNS-314,
ZM-447439, tozasertib, KW-2449) and **PARP** (olaparib, niraparib), plus XIAP (birinapant) and CHK1
(SB-218078). These are the axes the manuscript reports for RB1, and they are recovered from a reference set
assembled without sight of the data.

---

## Reading

**RB1 is the one genotype where the window recovers published biology beyond chance.** p ≈ 0.009 against a
94-compound independently assembled reference, with the recovered set falling into two mechanistically
coherent classes rather than scattering. This is a real, falsifiable validation result and it is the claim
the paper is entitled to make.

**TP53 does not survive the blind test — and this is the most important change from the seed run.** The
illustrative run on the 7-row seed set reported TP53 at p = 5.6 × 10⁻⁸ off 5 reference compounds that were
essentially the KIF11/Eg5 family. Against a 61-compound literature census, TP53 recovery falls to 1/61
(2%, p = 0.51) — chance. The seed-set result was an artifact of a reference set small enough to be
dominated by one target family. This is exactly the failure mode the protocol exists to expose, and it is
consistent with the note already in `README.md`: no PubMed-indexed study demonstrates TP53-mutant-selective
KIF11 sensitivity. **The TP53–KIF11 finding is an internal empirical result of this dataset. It is not
corroborated by the literature, and it must not be presented as validated.**

**PTEN is not enriched** (2/39, p = 0.94), consistent with the seed run (p = 0.30) and with the underpowered
mutant cohort (n = 3).

**CDKN2A is still effectively untestable**, but for a newly documented reason rather than an empty
reference. The 25-row census resolved only 12 compounds into the PRISM universe: its dominant arm is
MTAP/PRMT5-MAT2A (MRTX1719, AMG 193, TNG908, TNG462, BMS-986504, AG-270), and **none of those compounds
exist in the PRISM Repurposing library**. What did resolve is the CDK4/6 arm — and all 12 are misses
(palbociclib, abemaciclib, ribociclib, alvocidib, AT-7519, R547, …), which independently reproduces the
manuscript's §3.6 finding that CDK4/6 inhibitors sit between −2 and 0 in CDKN2A-mutant lines.

---

## For the manuscript (reviewer item B1)

This closes the circularity objection with a defensible, falsifiable answer rather than by softening the
language:

1. **Replace the 75–94% recovery numbers** in the abstract, §3.7 and §4. They came from a reference set
   derived from the study's own output; the honest figures are the table above, reported with the
   enrichment p-values **and** the misses.
2. **Claim validation for RB1 only** — recovery of published Aurora and PARP dependencies at p ≈ 0.009,
   with the recovered compound list and the miss list both shown.
3. **State plainly that PTEN, CDKN2A and TP53 do not pass the blind test.** For TP53, say why the KIF11
   axis is nonetheless the study's strongest empirical signal: it is novel, not literature-corroborated,
   and therefore cannot be validated against the literature by construction.
4. **Note the CDKN2A library limitation** — the modern MTAP/PRMT5 agents are absent from PRISM 19Q4, so
   the metabolic arm of CDKN2A biology is untestable in this dataset. That is a dataset boundary, not a
   negative result.
5. Pair this with Supplement 8 (RNAi/CRISPR, RB–E2F axis), which is also RB1-anchored. **The paper's
   independent evidence converges on RB1 from two directions.** Leading with that is stronger than
   claiming four genotypes and defending none.

## Reproduce

```bash
python3 run_all.py --data <data_sources> --out <scratch>
python3 concordance/concordance_enrichment.py \
    --reference concordance/reference_set_2026-08-31_directional.csv \
    --derived <scratch> --out concordance/results/2026-08-31_blind --perm 10000
```

Outputs: `results/2026-08-31_blind/concordance_report_primary_directional.csv` and
`…_sensitivity_full.csv`. Census provenance, per-row queries and the builders' exclusion notes are in
`reference_set_2026-08-31.csv` and `BLIND_CENSUS_NOTES_2026-08-31.md`.
