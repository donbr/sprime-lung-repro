# Rebuilding Supplement 7 / Table 1 — a worked walkthrough (RB1)

**For:** Paul, and anyone who has to rebuild the verification/validation section.
**What this is:** a complete, standalone, step-by-step demonstration of how to rebuild the RB1
"literature-corroborated candidate vulnerabilities" analysis so that it is a real benchmark instead of a
circular one. It uses RB1 as the worked example, runs end to end on the committed data, and ends with a
draft of the rebuilt table and the manuscript sentences. Nothing here edits the current manuscript — it is
a template you can follow, reject, or adapt.

Companion files in this folder: `PROTOCOL_literature_blind_concordance.md` (the rules), `concordance_enrichment.py`
(the engine), `reference_set_RB1.csv` (the frozen reference set built below), `results_RB1/concordance_report.csv`
(the output produced below).

---

## The one idea, first

The reason the current Table 1 feels impossible to "rebuild" is that **it answers a question that can only
have one answer.** Today the table is made like this:

> take the compounds the S′ window already selected (ΔpS′ ≤ −2) → look each one up in the literature → keep
> the ones with a supportive citation → report "we corroborated N compounds."

That is asking *"how many of the compounds I chose for a strong negative ΔpS′ have a strong negative ΔpS′?"*
The answer is 100% by construction, and no amount of rearranging the same table changes that. **The problem
is not the table — it is the direction of the arrow.** You cannot fix a circular benchmark by editing it; you
have to turn it around.

**Turn the arrow around:**

```
   CIRCULAR (today)                          BLIND BENCHMARK (the rebuild)
   S′ window ──► find literature             Literature ──► does the S′ window recover it?
   "we corroborated the hits"                "of what the literature says should be selective,
                                              the window catches X of N — more than chance? (p)"
```

Build **two lists independently** — a literature reference list and the S′ candidate list — then measure the
overlap and whether it beats chance. That is the whole picture. Everything below is mechanics.

---

## Step 1 — Write down the inclusion rule BEFORE you search

State, in one sentence, what earns a place on the reference list — and freeze it:

> *A druggable target with a published experimental demonstration that RB1/RB **loss confers selective
> sensitivity or dependency** in a cancer model (drug screen, isogenic pair, or genetic screen), identified
> by PMID/DOI.*

This sentence is what makes the benchmark honest: entries get in because they meet the rule, **not** because
they scored well in S′. You are not allowed to look at ΔpS′ while doing Steps 1–3.

## Step 2 — Assemble the RB1 reference list from the literature (blind)

Search PubMed (and confirm the target is a real dependency in BioGRID ORCS). For RB1, four targets meet the
rule with clean, published RB1-selective evidence. *According to PubMed:*

| Target | RB1-selective evidence | PMID | DOI |
|---|---|---|---|
| **AURKB** | Oser 2019 — RB1-null SCLC is hyperdependent on Aurora B (CRISPR SL screen) | 30373918 | [10.1158/2159-8290.CD-18-0389](https://doi.org/10.1158/2159-8290.CD-18-0389) |
| **AURKA** | Gong 2019 — Aurora A inhibition is synthetic-lethal with RB1 loss | 30373917 | [10.1158/2159-8290.CD-18-0469](https://doi.org/10.1158/2159-8290.CD-18-0469) |
| **PLK1** | Witkiewicz 2018 — RB-loss drug screen; PLK1 (chromosome segregation) selective for RB loss | 29386107 | [10.1016/j.celrep.2018.01.022](https://doi.org/10.1016/j.celrep.2018.01.022) |
| **CHEK1** | Witkiewicz 2018 — same screen; CHK inhibitors RB-selective in vitro and in xenografts | 29386107 | [10.1016/j.celrep.2018.01.022](https://doi.org/10.1016/j.celrep.2018.01.022) |

**A target that was considered and rejected — this is the important part.** PARP1 appears in the current
Table 1, but it does **not** meet the RB1-selectivity rule, and this was checked rather than assumed. A
graph-based research pass (the `ob-research` competency question *"Is PARP1 a synthetic-lethal dependency in
RB1-deficient cells?"*) returned three convergent lines, all pointing the same way:
- **Literature:** the RB1–PARP association is driven by **co-deleted neighbors, not RB1** — RNASEH2B (13q14,
  immediately adjacent to RB1; Carmichael 2024, *JCI*, [10.1172/JCI178278](https://doi.org/10.1172/JCI178278))
  and BRCA2 (Chakraborty 2019, *Clin Cancer Res*, [10.1158/1078-0432.CCR-19-1570](https://doi.org/10.1158/1078-0432.CCR-19-1570)).
  And RB1-deficient cells are *not* simply PARP-sensitive: they need CK2 co-inhibition to be killed by PARP
  inhibitors (Bulanova 2024, *Sci Adv*, [10.1126/sciadv.adj1564](https://doi.org/10.1126/sciadv.adj1564)).
- **Network:** STRING places RB1 (cell-cycle / E2F module) and PARP1 (base-excision-repair module, which
  contains BRCA1/2) in **disjoint modules** — PARP1 is not among RB1's 40 highest-confidence partners, and
  vice versa. No functional RB1–PARP1 link.
- **Clinical:** no PARP-inhibitor trial is selected on RB1 loss (ClinicalTrials.gov).

So PARP1 is **excluded, and the exclusion is documented with evidence.** A benchmark you can trim by leaving
out inconvenient targets is not a benchmark; writing the rule down first — and checking borderline calls with
the tools rather than asserting them — is what stops that.

Two grounding tools did two different jobs here:
- **PubMed** established *RB1-selectivity* — the thing that actually matters.
- **BioGRID ORCS** confirmed each target is a genuine CRISPR dependency (AURKA/AURKB/PLK1/CHEK1 are hits in
  740–930 screens). Useful as a sanity check, but note it is **not** selectivity — these genes are broadly
  essential, so ORCS alone would let almost anything in. Selectivity comes from the genotype-contrasted
  literature, not from "is it essential." Do not confuse the two.

The frozen list lives in **`reference_set_RB1.csv`** (one row per target, each with PMID/DOI, the search
string used, the freeze date, and a one-line rationale). Targets are entered at the **target** level; the
engine expands each to every PRISM compound annotated to it.

## Step 3 — Freeze

Commit `reference_set_RB1.csv` with today's date in `date_frozen` **before** running Step 4. The commit is the
audit trail: it proves the reference set predates any look at ΔpS′. (Here: frozen 2026-09-02.)

## Step 4 — Run the benchmark

```
python concordance_enrichment.py --reference reference_set_RB1.csv --out results_RB1
```

The engine (reading the already-computed S′ tables in `../results/`):
1. expands the 4 targets to the PRISM compounds annotated to them, **restricted to compounds actually tested
   in the RB1 cohort** — that is the reference-in-universe count (R);
2. counts how many of those fall inside the S′ window (recovered, k) and, crucially, **which do not** (misses);
3. asks whether k is more overlap than you'd get drawing the same number of window compounds at random
   (hypergeometric + 10,000-permutation p).

## Step 5 — Read the output

Actual result on the committed data:

| gene | reference→universe (R) | S′ candidates (K) | tested universe (N) | recovered (k) | recovery | expected by chance | enrichment p |
|---|---|---|---|---|---|---|---|
| **RB1** | 42 | 94 | 1360 | **8** | **19%** | ≈2.9 | **p ≈ 0.006** |

Read it in words: of **42** PRISM compounds that independent literature ties to RB1-selective targets and
that were actually tested, the S′ window recovers **8**. That is only **19%** — but random draws of 94
compounds from 1,360 would hit the reference set about **2.9** times, so 8 is **~2.7× over chance, p ≈ 0.006**.
**The window is enriched for known RB1 biology, well beyond chance, even though it recovers a minority of it.**

The 34 misses are the honest core of the table — reference compounds tested but *not* recovered: `alisertib,
danusertib, MLN-8054, AT-9283, BI-2536, volasertib, GSK461364, rigosertib, AZD7762, LY2603618, CHIR-124,
PF-477736, SCH-900776 …` (many Aurora / PLK1 / CHK1 inhibitors whose ΔpS′ did not clear −2). Reporting them
is what makes the claim credible: the window is *selective*, not merely *recovering everything*.

## Step 6 — Write it up (drop-in replacements)

**Rebuilt Table 1** has three columns of numbers, not one:

| RB1-selective target (literature) | Compounds tested (R) | Recovered by S′ window (k) | Missed |
|---|---|---|---|
| AURKB — Oser 2019 | … | … | … |
| AURKA — Gong 2019 | … | … | … |
| PLK1 — Witkiewicz 2018 | … | … | … |
| CHEK1 — Witkiewicz 2018 | … | … | … |
| **Total** | **42** | **8 (19%)** | **34** |

*(the per-target split is in `results_RB1/concordance_report.csv`; expand target→compound with the same PRISM
annotation the engine uses.)*

**Draft manuscript sentence (replaces the current "confirming accuracy and specificity"):**

> *To test whether the S′ selection window recovers known RB1 biology, we assembled — blind to ΔpS′ — a
> reference set of RB1-selective druggable dependencies from the literature (AURKB, Oser 2019; AURKA, Gong
> 2019; PLK1 and CHEK1, Witkiewicz 2018). Of 42 PRISM compounds annotated to these targets and tested in the
> RB1 cohort, the window recovered 8 (19%), a significant enrichment over the ~2.9 expected by chance
> (hypergeometric p = 0.006; 10,000-permutation p = 0.007). The window is therefore enriched for
> literature-validated RB1 dependencies beyond chance, while remaining selective — 34 annotated compounds
> were tested but not recovered. This establishes plausibility and enrichment; it does not estimate
> sensitivity, specificity, or positive predictive value, and is reported alongside the orthogonal
> genetic-dependency evidence (Supplement 8).*

That paragraph is defensible because every number in it — including the misses — is on the table, and the
reference set was frozen before ΔpS′ was consulted.

---

## Extending to PTEN, CDKN2A, TP53 — done

The same procedure has now been run for all four genotypes with PubMed-grounded reference sets
(`reference_set_v1.csv` → `results_v1/`); full write-up in **`CONCORDANCE_REBUILD_all_genotypes.md`**. The
honest result: **only RB1 clears chance.**

| Genotype | Recovered / tested | Enrichment p | Verdict |
|---|---|---|---|
| RB1 | 8 / 42 (19%) | **0.006** | significant |
| TP53 | 1 / 9 (11%) | 0.098 | borderline (sensitive to whether a grounded spindle/KIF11 citation is added) |
| PTEN | 3 / 22 (14%) | 0.44 | not significant |
| CDKN2A | 0 / 12 (0%) | 1.0 | null; PRMT5/MAT2A (best SL) absent from PRISM 19Q4 → partly untestable |

The point of the rebuild is not to make every genotype look strong. It is to make each claim *true*: report
recovery **with its miss list and its enrichment p**, and lead the paper's validation with whatever survives
this (RB1) plus the ΔpS′-independent evidence (Supplement 8 genetic dependency; the correct-direction sign
recoveries). The circular 75–94% recovery numbers do not survive an honest reconstruction.

## What is already done vs. what remains

- **Done (in this repo):** the protocol, the engine, a grounded and frozen RB1 reference set, and a
  reproducible RB1 result (`reference_set_RB1.csv` → `results_RB1/concordance_report.csv`).
- **Remains (author judgment):** decide whether 4 grounded RB1 targets is the census you want or whether to
  extend it (same rule, same provenance discipline); build the PTEN / CDKN2A / TP53 reference sets the same
  way; then paste the numbers into Table 1 and the sentence above.

## Reproduce it
```
cd concordance
python concordance_enrichment.py --reference reference_set_RB1.csv --out results_RB1
# reads ../results/sprime_lung_pairs.csv + lung_genotypes.csv ; writes results_RB1/concordance_report.csv
```

**Attribution.** RB1-selectivity citations were retrieved and verified via PubMed on 2026-09-02:
Oser 2019 [10.1158/2159-8290.CD-18-0389](https://doi.org/10.1158/2159-8290.CD-18-0389);
Gong 2019 [10.1158/2159-8290.CD-18-0469](https://doi.org/10.1158/2159-8290.CD-18-0469);
Witkiewicz 2018 [10.1016/j.celrep.2018.01.022](https://doi.org/10.1016/j.celrep.2018.01.022).
CRISPR-dependency sanity checks via BioGRID ORCS.
