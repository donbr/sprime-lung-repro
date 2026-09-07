# Result — second blinded census, 2026-09-06

Executes `PRESPEC_second_census_2026-09-06.md` (committed `343203f`, before this census existed) against
the census frozen in `38ce6f6` (committed before anything was scored). Nothing below is a decision made
after seeing a result; the rule was fixed in advance and this document reports what it returned.

**Verdict: RB1 replicates and is the only claimable genotype. The claim is narrowed to the Aurora kinase
class, which carries the enrichment in both censuses.**

---

## 1. The pre-specified rule, applied

A genotype's claim stands only if it clears chance against **both** censuses independently, hypergeometric
and permutation p both below 0.05, in each census's primary directional analysis. No pooling. Symmetric.

| Genotype | 2026-08-31 recovered | p | 2026-09-06 recovered | p | Verdict |
|---|---|---|---|---|---|
| PTEN | 2 / 39 | 0.94 | 3 / 71 | 0.99 | concordant negative |
| CDKN2A | 0 / 12 | 1 | 0 / 15 | 1 | concordant negative |
| **RB1** | **13 / 94** | **0.0099** | **13 / 73** | **0.00097** | **claimable** |
| TP53 | 1 / 61 | 0.51 | 0 / 38 | 1 | concordant negative |

Permutation p agrees with the closed form throughout: RB1 gives 0.0091 and 0.0004, the other three sit at
or near 1. Source: `results/census_comparison.csv`.

**Sensitivity analysis**, full censuses with the inverse-direction rows retained (95 and 121 rows). RB1
holds at 13/85, p = 0.0041. CDKN2A rises to 4/65, p = 0.18, still not clearing. PTEN 10/135, p = 0.95.
TP53 0/45, p = 1. The reference counts inflate here because the inverse-direction rows are EGFR and IGF1R
entries that expand to large annotated compound families, which is exactly why the directional exclusion
exists.

## 2. The narrowing step

The pre-specification required that, for any genotype clearing both censuses, the leave-one-class-out be
repeated and the claim narrowed to the class carrying it in **both** — and that a differing carrying class
be reported as unstable and not claimed.

| Census | Full | Removing AURKA + AURKB | Carrying classes |
|---|---|---|---|
| 2026-08-31 | 13 / 94, p = 0.0099 | 6 / 69, p = 0.34 | AURKA+AURKB, and AURKA+AURKB+SRC |
| 2026-09-06 | 13 / 73, p = 0.00097 | 6 / 48, p = 0.11 | AURKA+AURKB |

The intersection is **AURKA+AURKB**. The carrying class is stable, so the claim is made and narrowed:

> RB1-deficient lung cell lines are selectively sensitive to Aurora kinase inhibitors.

It is not a broad recovery of RB1 biology. In both censuses, removing the Aurora pair leaves the remainder
of the reference set at chance. The first census additionally shows SRC chained into the Aurora class by
promiscuous kinase inhibitors; the second census contains no SRC row, so that chaining does not arise, and
the Aurora pair alone is carrying in both.

## 3. The recovered compounds are identical

The two censuses were assembled six days apart by different agents and share only 16 of their roughly 20
RB1 targets. They nonetheless recover **exactly the same 13 compounds**:

`AMG900, KW-2449, NVP-BEZ235, SB-218078, SNS-314, ZM-447439, barasertib, barasertib-HQPA, birinapant,
litronesib, niraparib, olaparib, tozasertib`

Set identity, not merely equal counts. This is the strongest single piece of evidence in the exercise: the
recovered set is a property of the drug-response data and the window, not of which curator assembled the
reference. What differs between the censuses is the **denominator** — 94 tested compounds versus 73 —
which is why the recovery rate moves from 14% to 18% and the p-value tightens.

## 4. Agreement between the two censuses

Required by the pre-specification whatever the enrichment showed. Source: `results/census_agreement.csv`.

| Genotype | Targets A | Targets B | Shared | Jaccard, targets | Jaccard, compounds |
|---|---|---|---|---|---|
| PTEN | 20 | 30 | 19 | 0.61 | 0.49 |
| CDKN2A | 10 | 9 | 7 | 0.58 | 0.80 |
| RB1 | 20 | 19 | 16 | 0.70 | 0.78 |
| TP53 | 15 | 10 | 7 | 0.39 | 0.50 |

**Agreement is moderate, and that is itself a finding.** Two passes over the same literature, under the
same written criteria, agree on roughly 40% to 70% of targets. A single census is a noisier instrument
than its frozen, hashed presentation suggests, and any future benchmark built on one census should say so.

RB1 has the highest target agreement of the four, which is consistent with its being the one genotype with
a dense, unambiguous primary literature. TP53 has the lowest, which is consistent with the census notes
from both passes describing the TP53 evidence base as skewed toward DNA-damage-response targets and
allele-specific effects.

Targets each census found alone, for RB1: only in the first are CCNA2, CCNB1, EZH2 and SRC; only in the
second are CD276, KDM1A and PRMT5. Neither set contains a recovered compound, so the disagreement does not
touch the result.

## 5. What replicated, and what this does not establish

**Replicated.** The RB1 positive, at a smaller p-value than the first census. The three negatives, all
concordant. The identity of the recovered compound set. The Aurora dependence of the enrichment. And,
independently in both passes, the explicit negative report on TP53: two different agents searching six
days apart both concluded that no mitotic or spindle-assembly target, KIF11 included, can be evidenced to
criterion for TP53. The manuscript's TP53–KIF11 finding is therefore an internal empirical result of this
dataset twice over, and must not be presented as literature-validated.

**Not established.** This is not an independent replication. Both censuses were commissioned from a
results-aware context, and agent isolation was enforced by instruction rather than by a sandbox. What the
exercise shows is that the result is a property of the literature rather than of one pass through it. A
genuinely independent replication would be commissioned by someone who has never seen the results, and
remains the right next step for anyone who wants to close this objection completely.

The remaining limitations from the first census all still apply: the reference sets are pan-cancer while
recovery is measured in lung lines, PRISM's target annotations are imperfect, and recovery is not a
sensitivity estimate.

## 6. Reproduce

```bash
uv run --locked python concordance/assemble_census.py
uv run --locked python concordance/concordance_enrichment.py \
    --reference concordance/reference_set_2026-09-06_directional.csv \
    --out concordance/results/2026-09-06_census2 --perm 10000
uv run --locked python concordance/compare_censuses.py
uv run --locked python concordance/census_agreement.py
```

Frozen inputs: `reference_set_2026-09-06.csv` = `45c5b69f467092a8370cf5672d36be0f` (121 rows);
`reference_set_2026-09-06_directional.csv` = `2d57e870e07fe5a3a6cde0aa894ccd4a` (110 rows).
Engine seed 20260811, 10,000 permutations, on md5-verified PRISM 19Q4 and DepMap 24Q2.
