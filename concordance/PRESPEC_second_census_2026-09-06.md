# Pre-specified analysis plan — second blinded census, 2026-09-06

**This document is written and committed BEFORE the second census exists and BEFORE anything is scored.**
That is its whole purpose. A decision rule chosen after seeing a result is not a decision rule. If this file
is ever edited after the census-2 results are computed, the edit invalidates the exercise and must be
disclosed rather than quietly made.

Git is the evidence: this file's commit must precede the commit that adds `reference_set_2026-09-06*.csv`,
which must in turn precede any commit containing census-2 results.

---

## 1. What this exercise is, and what it is not

**It is** a repeat of the *blinded census assembly* (isolated agents compile a reference set from stated
inclusion criteria, output transferred verbatim, file frozen and hashed before scoring) using fresh agents
that have not seen the first census. It measures how much of the benchmark's result is a property of the
literature and how much is a property of one particular pass through it.

**It is not** an independent replication. The initiating context is results-aware: the session commissioning
census 2 has seen the 2026-08-31 results in full. Structural blinding still holds for the *agents* — they
are instructed to read no repository file, to consult no S′/pS′/ΔpS′ value, and to avoid the manuscript —
but that isolation is enforced by instruction, not by a sandbox, and it is the same arrangement as census 1.
A genuinely independent replication would be commissioned by someone who has never seen the results, and
this exercise does not substitute for it.

**Both limitations are to be reported in the supplement**, in the same terms as census 1's.

## 2. Assembly procedure (identical to 2026-08-31)

Four agents, one per genotype (PTEN, CDKN2A, RB1, TP53), each in its own context, with PubMed plus
ChEMBL / Open Targets / BioGRID-ORCS for druggability confirmation only.

Inclusion criteria, unchanged from census 1:

1. experimental evidence in a cancer model that loss of the genotype confers selective sensitivity to
   inhibition of the named target;
2. the comparison is genotype-comparative, mutant or null versus wildtype or restored;
3. the target is druggable;
4. a live-verified PMID or DOI exists.

Exclusions, unchanged: reviews without primary data; pan-essential claims with no genotype comparison;
computational predictions without experimental validation.

Every row records the exact query string that surfaced it, the freeze date, and a one-line rationale.
Output is assembled **verbatim** — no row added, removed, reworded or reordered on the basis of anything
known about the results.

## 3. Directional exclusion

As in census 1, an agent that returns a row whose *sensitive* genotype is the wildtype one must flag it
**INVERSE-DIRECTION** in its own rationale, at authoring time. The **primary** analysis excludes those rows;
the full set is the sensitivity analysis. The flag is written blind, so the exclusion is not a post-hoc
choice.

## 4. Scoring

Unchanged and not to be tuned: `concordance_enrichment.py --perm 10000 --seed 20260811`, against the same
derived tables, with the SL window imported from `sprime_core.py`. The census is frozen, hashed and
committed before the engine is pointed at it.

## 5. The decision rule — fixed here, before any census-2 number exists

**A genotype's claim stands only if it clears chance against BOTH censuses independently.**

- Threshold: hypergeometric p < 0.05 **and** permutation p < 0.05, in the primary directional analysis of
  each census separately.
- **No pooling.** The two censuses are not merged into a combined reference set. A union assembled in two
  passes, the second commissioned after seeing the first, cannot be described as frozen.
- **The rule is symmetric.** A genotype that fails census 1 and clears census 2 is *also* not claimed. It is
  reported as a discordance. Only concordant positives are claimable, in either direction.
- **The Aurora narrowing carries over.** The RB1 claim as currently written is Aurora-specific, because
  removing AURKA and AURKB from census 1 drops RB1 to 6 of 69 recovered at p = 0.34. If RB1 clears both
  censuses, the leave-one-class-out is repeated on census 2 and the claim is narrowed to whatever class or
  classes carry it in **both**. If the carrying class differs between censuses, the claim is reported as
  unstable and is not made.
- Bonferroni correction across the four genotypes is reported for each census. It is reported, not used as
  the gate; the gate is the both-must-clear rule above.

**Anticipated outcomes, written down now so none of them can be presented as a surprise:**

| Census 1 | Census 2 | Reported as |
|---|---|---|
| clears | clears | **claimable**, narrowed to the class carrying it in both |
| clears | fails | not claimable; reported as a census-dependent result, with both numbers |
| fails | clears | not claimable; reported as a discordance, with both numbers |
| fails | fails | not claimable; the negative is strengthened |

For RB1 specifically, a census-2 failure would mean the paper's one positive validation claim does not
survive a second pass at the literature, and the supplement must say so plainly. That outcome is accepted
in advance as a possible result of this exercise. It is the reason the exercise is worth running.

## 6. Agreement measures to report regardless of the outcome

Computed and reported for all four genotypes, whatever the enrichment results:

- overlap of the two censuses at the level of `(genotype, target)` pairs — intersection, each census's
  unique rows, and Jaccard index;
- overlap of the *resolved PRISM compound* sets, which is what the enrichment actually scores;
- per-genotype row counts and how many rows resolve into the tested universe in each census.

Low agreement is itself a finding: it would mean the census, not the window, is the noisy component of this
benchmark, and that a single census is too thin an instrument to validate against.
