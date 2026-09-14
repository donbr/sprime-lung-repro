# Literature-blind concordance rebuild — all four genotypes (results)

**Method:** see `WALKTHROUGH_RB1_concordance_rebuild.md` (the step-by-step; RB1 worked in full).
**This file:** applies the same blind-reference-set procedure to PTEN, CDKN2A, and TP53 and reports the
numbers, so the whole of Supplement 7 can be rebuilt on one honest basis.
**Reference set:** `reference_set_v1.csv` (frozen 2026-09-02, blind to ΔpS′; every row carries a PubMed PMID/DOI).
**Output:** `results_v1/concordance_report.csv`. Reproduce with
`python concordance_enrichment.py --reference reference_set_v1.csv --out results_v1`.

---

## The headline

When the reference set is assembled **blind to ΔpS′** — from published genotype-selective synthetic-lethal
evidence only — and recovery is reported **with its misses and an enrichment p-value**, only one genotype
clears chance:

| Genotype | Reference→tested (R) | S′ candidates (K) | Universe (N) | Recovered (k) | Recovery | Enrichment p | Verdict |
|---|---|---|---|---|---|---|---|
| **RB1** | 42 | 94 | 1360 | 8 | 19% | **0.006** | **Significant** — enriched beyond chance |
| **TP53** | 9 | 16 | 1402 | 1 | 11% | 0.098 | Borderline / not significant |
| **PTEN** | 22 | 97 | 883 | 3 | 14% | 0.44 | Not significant |
| **CDKN2A** | 12 | 48 | 1402 | 0 | 0% | 1.0 | Null (and partly untestable — see below) |

*(hypergeometric and 10,000-permutation p agree to two digits; full per-row output in
`results_v1/concordance_report.csv`.)*

**This is the honest result the rebuild exists to produce, and it matters:** the current Supplement 7 reports
75–94% recovery for PTEN/TP53/CDKN2A, but those numbers came from the circular construction (the reference
set *was* the window's output). Assemble the reference set independently and **only RB1 survives** — which is
exactly what the repository's permutation-null analysis already shows ("only RB1 rises above the null"). The
concordance benchmark, done correctly, corroborates RB1 and does **not** independently validate the other
three. That is a finding, not a failure — and it is far more defensible than an unfalsifiable 94%.

---

## Per genotype — what was cited, and what the misses mean

*(All citations verified via PubMed on 2026-09-02.)*

### RB1 — significant (p ≈ 0.006)
Targets: **AURKB** (Oser 2019, [10.1158/2159-8290.CD-18-0389](https://doi.org/10.1158/2159-8290.CD-18-0389)),
**AURKA** (Gong 2019, [10.1158/2159-8290.CD-18-0469](https://doi.org/10.1158/2159-8290.CD-18-0469)),
**PLK1 & CHEK1** (Witkiewicz 2018, [10.1016/j.celrep.2018.01.022](https://doi.org/10.1016/j.celrep.2018.01.022)).
8 of 42 recovered; ~2.7× over the ~2.9 expected by chance. Full detail in the RB1 walkthrough.

### PTEN — not significant (p ≈ 0.44)
Targets: **PIK3CB** and **AKT** (Wee 2008, [10.1073/pnas.0802655105](https://doi.org/10.1073/pnas.0802655105) —
PTEN-null cancers depend on PIK3CB→AKT), **PARP1** (Mendes-Pereira 2009,
[10.1002/emmm.200900041](https://doi.org/10.1002/emmm.200900041) — PTEN loss → HR defect → PARP sensitivity).
The window recovers only 3 of 22, no better than chance: the canonical PTEN drugs — alpelisib, GDC-0941/0980
(PI3K), AZD5363/GDC-0068 (AKT), olaparib/niraparib (PARP) — are **tested but not window-selective**. The S′
window does not flag PTEN's literature dependencies as PTEN-mutant-selective in this dataset.

### CDKN2A — null (p = 1.0), and partly untestable
Testable targets: **CDK4/CDK6** (Goodwin 2023, [10.1158/0008-5472.CAN-22-0391](https://doi.org/10.1158/0008-5472.CAN-22-0391) —
CDKN2A/p16 loss → CDK4/6 rationale). **0 of 12 recovered:** every CDK4/6 inhibitor (palbociclib, ribociclib,
abemaciclib …) is tested but missed — *correctly*, because CDK4/6 inhibitors act as **positive controls that
run WT-selective** (positive ΔpS′), not mutant-selective synthetic lethals. Separately, the best-characterized
CDKN2A-adjacent synthetic lethal — **PRMT5 / MAT2A via MTAP co-deletion** (Engstrom 2023,
[10.1158/2159-8290.CD-23-0669](https://doi.org/10.1158/2159-8290.CD-23-0669); Kalev 2021,
[10.1016/j.ccell.2020.12.010](https://doi.org/10.1016/j.ccell.2020.12.010)) — has **no compound in PRISM 19Q4**,
so it cannot be evaluated here at all. CDKN2A should be reported as **untestable / unsupported** by this
benchmark, which matches its status as the weakest arm elsewhere in the analysis.

### TP53 — borderline (p ≈ 0.10)
Targets: **WEE1** (Fukuda 2024, [10.1016/j.xcrm.2024.101578](https://doi.org/10.1016/j.xcrm.2024.101578) —
WEE1 inhibition selective in TP53-mutant NSCLC), **PLK1** (Degenhardt 2010,
[10.1158/1535-7163.MCT-10-0095](https://doi.org/10.1158/1535-7163.MCT-10-0095) — PLK1-inhibitor sensitivity
tracks p53 loss). Only 1 of 9 recovered (WEE1's MK-1775 and PD-407824, and most PLK1 compounds, are missed).
**Important caveat:** TP53's result is sensitive to the reference targets. The manuscript leans on the
**spindle-assembly / mitotic** class (e.g. KIF11/Eg5), and an earlier, ungrounded seed that included KIF11
scored TP53 as strongly enriched. I could **not** verify a clean primary TP53-selective KIF11/Eg5 citation in
this pass, so KIF11 was excluded and TP53 falls to borderline. **Action for the authors:** if the TP53–spindle
dependency is to carry weight, it needs a real genotype-selective citation; with one, TP53 may reach
significance — without one, it does not. This is precisely the discipline the rebuild enforces.

---

## What this means for the paper

1. **Lead the validation with RB1** — it is the only genotype the blind benchmark supports (p ≈ 0.006), and it
   is independently corroborated by the RB–E2F genetic-dependency result (Supplement 8). These two agree.
2. **Report PTEN, CDKN2A, TP53 honestly** — as recovery + misses + a non-significant (or untestable) enrichment
   p. Do not carry the 75–94% recovery numbers; they were artifacts of the circular construction.
3. **CDKN2A** should be stated as untestable in this library (positive-control CDK4/6 only; PRMT5/MAT2A absent).
4. **TP53** needs a grounded spindle/mitotic citation to be claimed; otherwise report it as borderline.

The rebuilt Supplement 7 is therefore shorter and more honest: one genotype (RB1) with a significant,
independently-corroborated concordance, and three reported transparently with their misses. That is a
defensible verification section; the current one is not.

## Files
- `reference_set_v1.csv` — the frozen, PubMed-grounded reference set (all four genotypes).
- `results_v1/concordance_report.csv` — recovery, enrichment p, and full miss lists.
- `WALKTHROUGH_RB1_concordance_rebuild.md` — the method, worked step by step on RB1.
- `reference_set_RB1.csv` / `results_RB1/` — the RB1-only worked example.

**Attribution.** All genotype-selectivity citations retrieved and verified via PubMed on 2026-09-02
(PMIDs 30373918, 30373917, 29386107, 18755892, 20049735, 36346366, 38776912, 20571075; untestable-but-noted
37552839, 33450196). CRISPR-dependency sanity checks via BioGRID ORCS.
