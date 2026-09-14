# Result — second blinded census, 2026-09-06

Executes `PRESPEC_second_census_2026-09-06.md` (committed `343203f`, before this census existed) against
the census frozen in `38ce6f6` (committed before anything was scored). The rule was fixed in advance; this
document reports what it returned, and what that does and does not establish.

**Verdict: RB1 passes the pre-specified gate and is the only claimable genotype. But the second census
adds far less than a naive reading of the gate suggests, and the Aurora narrowing does not replicate under
a properly posed test.** Both statements are in this document because both are true.

---

## 1. The pre-specified rule, applied

A genotype's claim stands only if it clears chance against **both** censuses **separately** (the
pre-specification's word is "independently", which there means *without pooling* — it does **not** mean the
two censuses are statistically independent; see §3). No pooling. Symmetric.

| Genotype | 2026-08-31 | p | Bonferroni ×4 | 2026-09-06 | p | Bonferroni ×4 | Verdict |
|---|---|---|---|---|---|---|---|
| PTEN | 2 / 39 | 0.94 | 1 | 3 / 71 | 0.99 | 1 | concordant negative |
| CDKN2A | 0 / 12 | 1 | 1 | 0 / 15 | 1 | 1 | concordant negative |
| **RB1** | **13 / 94** | **0.0099** | **0.040** | **13 / 73** | **0.00097** | **0.0039** | **passes the gate** |
| TP53 | 1 / 61 | 0.51 | 1 | 0 / 38 | 1 | 1 | concordant negative |

Source: `results/census_comparison.csv`. Permutation p agrees with the closed form throughout, which is
expected rather than corroborating: the permutation draws a uniform random candidate-sized subset of the
universe, so it is a 10,000-draw Monte-Carlo estimate **of the same hypergeometric null**, not a second
line of evidence. Requiring both to clear can only fail on simulation noise.

**Sensitivity analysis**, full censuses with the inverse-direction rows retained. Both arms, because
quoting one while framing both is how the first draft of this document misled:

| | RB1 | Bonferroni ×4 |
|---|---|---|
| 2026-08-31, 95-row census | 13 / 106, p = 0.026 | **0.103 — does not survive correction** |
| 2026-09-06, 121-row census | 13 / 85, p = 0.0041 | 0.016 |

Census 1's sensitivity analysis fails Bonferroni. That is worth stating plainly: the primary directional
result survives correction at 0.040, and the version retaining the inverse-direction rows does not.

## 2. What the second census actually adds — much less than it appears

`results/census_comparison.csv` records the reference nesting, and for RB1 it is decisive:

| | RB1 |
|---|---|
| Census 1 resolved reference compounds | 94 |
| Census 2 resolved reference compounds | 73 |
| Shared | 73 |
| Census 2 ⊆ census 1 | **yes** |
| Compounds unique to census 1 | 21, of which **0** recovered (16 come from SRC alone) |
| Compounds unique to census 2 | 0 |

**Census 2's RB1 reference set is a strict subset of census 1's.** Both are intersected with the *same*
fixed 94-compound candidate set, derived from the *same* drug-response data. Under nesting, census 2's
recovered set is forced to be a subset of census 1's, so equal counts entail identical sets. The earlier
claim that recovering "exactly the same 13 compounds — set identity, not merely equal counts" was the
strongest evidence in the exercise was wrong: under nesting those two statements are the same statement,
and neither is evidence of independent convergence.

The same nesting explains the smaller p-value. The numerator is unchanged at 13, the universe is unchanged
at 1360, and the candidate set is unchanged at 94. Census 2 obtained p = 0.00097 rather than 0.0099 purely
by nominating **21 fewer compounds, every one of them a miss**. A smaller denominator of failures is not a
stronger result. **Quote 0.0099, the census-of-record figure**, and treat 0.00097 as what it is.

It follows that the earlier statement "neither set of census-unique targets contains a recovered compound,
so the disagreement does not touch the result" was also wrong. The disagreement is the *only* thing that
differs between the two analyses. Census 2's three unique RB1 targets (CD276, KDM1A, PRMT5) resolve to zero
tested compounds and are inert; census 1's four unique targets contribute the 21 misses that account
entirely for the difference in p.

What genuinely replicated for RB1 is therefore narrower than "the result": a second set of curators,
working blind, again nominated the Aurora, PARP and IAP targets that the window recovers. That is roughly
three or four independent curatorial decisions, not thirteen compound-level replications.

## 3. What is and is not independent between the two censuses

Shared and fixed across both analyses: the drug-response data, the S′ window, the tested universe, the
candidate set, and the target→compound annotation map. Varying: only which targets the curators nominated.
The two censuses are therefore strongly dependent by construction. The both-must-clear rule remains a
**valid conservative gate** — an intersection rule cannot inflate type-I error — but nothing here licenses
treating the two p-values as independent evidence, and they must never be multiplied.

## 4. The narrowing — and why it does not replicate

The pre-specification required the leave-one-class-out to be repeated and the claim narrowed to the class
carrying it in both censuses, with a differing carrying class reported as unstable and not claimed.

| Census | Full | Removing AURKA + AURKB | Computed overlap-closed class carrying it |
|---|---|---|---|
| 2026-08-31 | 13 / 94, p = 0.0099 | 6 / 69, p = 0.34 | `AURKA+AURKB+SRC` |
| 2026-09-06 | 13 / 73, p = 0.00097 | 6 / 48, p = 0.11 | `AURKA+AURKB` |

**The computed classes differ, and their intersection is empty.** Stability holds only for the
`AURKA+AURKB` pair, which the pre-specification named explicitly by number in advance, and which the
generator treats as a curated special case alongside the computed partition. `census_comparison.csv`
records this as `narrowing_stable = curated-pair-only` rather than as computed stability, because the two
units disagree. Two further caveats a reader is owed:

- The classes differ for a mechanical reason. Census 1 chains SRC into the Aurora class through **one**
  compound, ENMD-2076, which PRISM annotates to both. Census 2 contains no SRC row, so no chaining occurs.
  Single-linkage merging on a single annotation is a known fragility of the overlap-closed unit.
- Removing the Aurora pair in census 1 removes 1 of SRC's 16 compounds, so the curated removal itself
  partially removes another target's compounds — the very thing the overlap-closed unit exists to prevent.

**Under a better-posed test, the narrowing does not replicate.** "Does this class carry the enrichment"
is a question about recovery *rate*, not about whether removing the class costs enough sample size to lose
significance. A one-sided Fisher test of class versus remainder:

| Census | Aurora | Remainder | Fisher p |
|---|---|---|---|
| 2026-08-31 | 7 / 25 | 6 / 69 | **0.024** |
| 2026-09-06 | 7 / 25 | 6 / 48 | **0.095 — does not clear** |

The Aurora compound set is byte-identical in both censuses (25 compounds, 7 recovered), so this test varies
only in the remainder. The narrowing is supported in census 1 and inconclusive in census 2.

Finally, "removing the Aurora pair leaves the remainder at chance" overstates. The remainder is
**underpowered, not demonstrably null**: 6/69 = 8.7% (95% CI 4.0–17.7%) and 6/48 = 12.5% (95% CI
5.9–24.7%) against a base rate of 6.9%. The census-2 remainder still sits at 1.8× the base rate. Absence of
significance here is absence of evidence.

## 5. Agreement between the two censuses

Required by the pre-specification whatever the enrichment showed. Source: `results/census_agreement.csv`.

| Genotype | Targets A | Targets B | Shared | Jaccard, targets | Jaccard, compounds |
|---|---|---|---|---|---|
| PTEN | 20 | 30 | 19 | 0.61 | 0.49 |
| CDKN2A | 10 | 9 | 7 | 0.58 | 0.80 |
| RB1 | 20 | 19 | 16 | 0.70 | 0.78 |
| TP53 | 15 | 10 | 7 | 0.39 | 0.50 |

**Agreement is moderate, and that is a finding.** Two passes over the same literature under the same
written criteria agree on 39% to 70% of targets. A single census is a noisier instrument than its frozen,
hashed presentation suggests. Compound-level Jaccard is not a second independent measurement — resolution
is a deterministic function of the target string and the fixed annotation map — so read it as target
agreement re-weighted by how many PRISM compounds each target pulls in.

## 6. What replicated, and what this does not establish

**Replicated.** RB1 passes the gate in both censuses. The three negatives are concordant. A second set of
blind curators again nominated the Aurora, PARP and IAP targets the window recovers. And, in both passes
independently, the TP53 agent reported that no mitotic or spindle-assembly target, KIF11 included, could be
evidenced to criterion — though note this is agreement between two searches on an *absence*, for the
genotype with the lowest target agreement of the four, so it is weak evidence for a strong-sounding
conclusion. The conservative reading it supports is the one already taken: the TP53–KIF11 signal is an
internal result of this dataset and must not be presented as literature-validated.

**Not established.** This is not an independent replication. Both censuses were commissioned from a
results-aware context, and agent isolation was enforced by instruction rather than by a sandbox. Beyond
that, §2 and §3 show the two censuses share almost everything that determines the answer. What the
exercise shows is that the *target nomination* is reasonably stable, not that the enrichment has been
independently reproduced. A genuinely independent replication would be commissioned by someone who has
never seen the results and remains the right next step.

The first census's limitations all still apply: its freeze commit is retroactive, the reference sets are
pan-cancer while recovery is measured in lung lines, PRISM's target annotations are imperfect, and recovery
is not a sensitivity estimate.

## 7. Provenance notes

- `census_agreement.py` was committed at `ee365d6`, before the census existed, and then modified in the
  scoring commit `0fb42f8`. The change was cosmetic — canonical row ordering — and no metric definition
  changed, but a reviewer auditing "committed before" will see a post-hoc diff and is entitled to know why.
- The audit chain for census 2 begins at `census_2026-09-06_raw/`, the staged agent output. The two
  formatting repairs disclosed in `CENSUS_NOTES_2026-09-06.md` were applied upstream of those files, so the
  raw directory is the earliest artifact a reviewer can re-derive the frozen census from.
- All eleven commits on this branch are unpushed, unsigned, and authored in one local session by a party
  who already knew census 1's results. The commit ordering is real and filesystem timestamps corroborate
  it, but an unpushed local commit is an attestation, not an externally witnessed timestamp.

## 8. Reproduce

```bash
uv run --locked python concordance/assemble_census.py

# primary (directional) and sensitivity (full) runs; the engine writes concordance_report.csv,
# which is renamed to the two names this document cites
uv run --locked python concordance/concordance_enrichment.py \
    --reference concordance/reference_set_2026-09-06_directional.csv \
    --out concordance/results/2026-09-06_census2 --perm 10000
mv concordance/results/2026-09-06_census2/concordance_report.csv \
   concordance/results/2026-09-06_census2/concordance_report_primary_directional.csv
uv run --locked python concordance/concordance_enrichment.py \
    --reference concordance/reference_set_2026-09-06.csv \
    --out /tmp/c2full --perm 10000
cp /tmp/c2full/concordance_report.csv \
   concordance/results/2026-09-06_census2/concordance_report_sensitivity_full.csv

uv run --locked python concordance/compare_censuses.py
uv run --locked python concordance/census_agreement.py
```

Frozen inputs: `reference_set_2026-09-06.csv` = `45c5b69f467092a8370cf5672d36be0f` (121 rows);
`reference_set_2026-09-06_directional.csv` = `2d57e870e07fe5a3a6cde0aa894ccd4a` (110 rows).
Engine seed 20260811, 10,000 permutations, on md5-verified PRISM 19Q4 and DepMap 24Q2.
