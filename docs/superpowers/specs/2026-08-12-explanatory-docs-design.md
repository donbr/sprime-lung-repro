# Explanatory documentation for sprime-lung-repro — design

**Date:** 2026-08-12
**Status:** approved, ready for implementation planning

## Problem

The repository reproduces an S′ genotype-selective-vulnerability analysis and runs the statistical
controls a referee review demanded of the companion manuscript. Someone landing on it cold — a reviewer,
an editor, or a reproducer — currently gets `README.md`, which states the metric and the headline table
but explains neither. Nothing in the repo says why a signed metric is needed, what each control asks, or
what the analysis does and does not establish. `CLAUDE.md` carries that context but is written for agents
working in the repo, not for readers evaluating it.

## Decisions

Settled during brainstorming, and binding on the implementation:

| Decision | Choice |
|---|---|
| Primary reader | Someone landing on the repo cold: reviewer, editor, or reproducer. Audience-neutral, outlives this manuscript. |
| Stance | Separated. The method is explained on its own terms first; the controls and their verdict come second. |
| Coverage | What the code implements, plus explicitly named gaps for paper concepts it does not. |
| Reader depth | Assume neither pharmacology nor statistics. Both primers included. |
| Structure | Four documents under `docs/` with an index. |

## Document set

### `docs/README.md`

Index and 60-second orientation. States what the repo is, gives the one-paragraph version of what it
found, and offers four reading paths: re-run it (root README quickstart), understand the metric
(`method.md`), understand what it establishes (`evidence.md`), understand its limits (`scope.md`).
Carries diagram D1.

### `docs/method.md`

Opens with the curve-fit pathology, not the formula — that ordering is deliberate, because the pathology
is what motivates a signed metric and the manuscript's own argument runs in that direction.

1. **Why the standard summaries fail.** Of the DepMap 4PL fits: 36% have a lower asymptote above 1.0,
   36% have AUC above 1.0, 3% have AUC at exactly 1 (suggesting capping), and roughly 49% have lower
   asymptotes above 0.5, leaving IC₅₀ undefined. Diagram D2.
2. **Pharmacology primer.** 4PL curve parameters, E_max, EC₅₀, AUC, and what a lower asymptote above 1
   means physically — the compound increased viability relative to control.
3. **S′ defined.** The signed ratio and the asinh transform; why asinh rather than log (it accepts
   negative, zero, and positive values, compresses extremes, and preserves sign and rank order). Both
   anchoring choices stated as choices: E_max on the percent (0–100) scale, and 1 µM as the reference
   concentration. Re-anchoring to the 10 µM top dose is **not** a uniform +2.30 shift and must not be
   described as one: asinh reaches the ln 10 offset only asymptotically, the offset carries the sign of S′
   (so it is −2.30 for disinhibitory values), and near zero the value is scaled by roughly 10 instead. Nor
   would a uniform shift move ΔpS′ at all — it cancels in a WT-minus-mutant difference. The anchoring is
   load-bearing because the window's **absolute activity gates** pS′_WT > 0 and pS′_mutant > 0 are stated in
   absolute S′ units; cross-reference Control 2 in `evidence.md`, which removes candidates by exactly that
   mechanism. Diagram D3.
4. **pS′ and ΔpS′.** Cohort means per compound, the WT-minus-mutant contrast, and the sign convention
   (negative ΔpS′ means mutant-selective inhibition).
5. **The SL window.** The three conditions and why each exists: activity in WT makes the effect an
   interpretable inhibition, activity in mutant makes the dependency pharmacologically accessible, and
   the −2 threshold imposes a minimum effect size. Include the fold-change reading — for candidates
   sitting at pS′ ≈ 2–4, ΔpS′ ≤ −2 amounts to requiring roughly a 7.4-fold greater potency–efficacy
   ratio in mutant cells. Note that `MIN_LINES = 3` per pool is a repo-level condition. Diagram D4.
6. **Interpretive framing.** Why retaining sign matters: one signed axis separates actionable
   vulnerabilities, counter-therapeutic states, and genotype-independent cytotoxicity. Attributed to the
   companion manuscript, not asserted as this repo's finding. Diagrams D5 and D6.
7. **Genotype calling.** The 0/1/2 encoding of the damaging-mutation matrix, the four genes, cohort sizes,
   and the detail that for TP53 the *wild-type* cohort is the small one (n = 18) — so outlier sensitivity
   applies to the wild-type side.
8. **Provenance.** How inputs are pinned and verified, and what happens when verification fails.
   Diagram D7.
9. **Worked example.** doxorubicin/A549 → S′ = 6.704, tied to `test_sprime_worked_example`, noting this
   value corrects an arithmetic error in the manuscript's own worked example.

### `docs/evidence.md`

1. **Statistics primer.** What a permutation null asks, how an empirical p differs from an FDR, what a
   bootstrap confidence interval on a difference of pooled means means, what a hypergeometric enrichment
   tests, and why a benchmark assembled from its own results carries no information.
2. **Control 1 — label-permutation null.** What it asks, the per-genotype table, and the reading: only
   RB1 rises above chance, and only marginally.
3. **Control 2 — line-centring.** The confound it tests (mutant lines simply being more drug-sensitive),
   the finding that cohort offsets are small and ΔpS′ is near-invariant to centring — which favors the
   method — and the separate finding that centring still removes most candidates because they fail the
   absolute pS′ > 0 gate, meaning the lists depend on the metric's absolute-scale anchoring.
4. **Control 3 — bootstrap CI gate.** Point estimate versus CI excluding zero versus CI entirely past −2,
   with survivor counts and the note that PTEN's survivors rest on n_mut = 3.
5. **Control 4 — concordance.** Why the original benchmark was circular, what blind assembly requires,
   and the current starter-set result. Diagrams D8 and D9.
6. **Cross-check — DEMETER2 RNAi.** State what the analysis is **constructed to test**, not what it found:
   the RB–E2F axis is expected to score mutant-selective while CDK4/6 is expected to score
   wild-type-selective in the same contrast — a two-directional check on contrast direction rather than
   merely a hit list. Attribute the CDK4/6 expectation to `demeter_validation.py`'s own output legend
   ("a positive control"). No run of that script is committed, so the section must assert no outcome, in
   either direction — the same standard that already bars quoting its numbers. Note that the one-sided q
   tests only "mutant more dependent", so a real WT-selective effect scores q ≈ 1 — read `direction`
   before any q, and prefer two-sided `q_two`.
7. **What the totality supports.** The window recovers specific known biology (Aurora/PLK under RB1 loss,
   KIF11 under TP53 mutation) without being a genome-wide selective classifier.

### `docs/scope.md`

Framed as what a reader may not conclude from this repository. A table of manuscript concepts against
implementation status, then prose on each gap:

- **No fit-quality or minimum-|E_max| gate.** Flat curves make EC₅₀ unidentifiable while |S′| explodes.
  State explicitly that the bootstrap CI gate does not substitute — stable-but-artifactual values survive
  it.
- **No EC₅₀ range censoring.** The secondary screen runs 8 steps at 4-fold dilution from 10 µM, so fitted
  EC₅₀ values below roughly 0.61 nM are extrapolations.
- **No copy-number genotypes.** Calls come from the damaging-mutation matrix alone, which is why the
  CDKN2A arm is weakest — that gene is inactivated predominantly by homozygous deletion.
- **No GMM embedding, no Benjamini–Hochberg on the main significance test, no interaction terms.** The
  last is where the manuscript's network thesis would have to be tested, and it is not tested here.
- **No network access at analysis runtime.** Curation-time connectors are a separate, upstream step.
- **The concordance reference set is incomplete.** Five of its seven rows carry neither PMID nor DOI and
  the search-terms field is empty throughout, though the protocol makes both mandatory.

## Diagram inventory

Nine mermaid diagrams. Type is specified because it determines whether GitHub renders it.

| # | Diagram | Type | Document | Must show |
|---|---|---|---|---|
| D1 | Pipeline overview | `flowchart LR` | README | Pinned inputs → `sprime_pipeline.py` → the two derived tables → the four consuming scripts → `results/`. Script filenames included so the diagram doubles as repo navigation. |
| D2 | 4PL fit outcomes | `flowchart TD` | method | One fit branching into canonical and the four pathologies, each labeled with its percentage. |
| D3 | S′ construction | `flowchart LR` | method | upper/lower asymptote → signed E_max → ×100 → ÷EC₅₀ → ×1 µM → asinh → signed S′. Each convention visible at the step where it enters. |
| D4 | SL window decision tree | `flowchart TD` | method | The four gates in order (≥3 lines per pool, pS′_WT > 0, pS′_MUT > 0, ΔpS′ ≤ −2) with labeled reject branches. |
| D5 | Two-mode operational states | `stateDiagram-v2` | method | Inhibitory, inert, and disinhibitory as distinct states sharing one signed axis, with genotype governing which are accessible rather than altering a state's internal structure. |
| D6 | Triage framework | `flowchart TD` | method | One signed axis resolving to actionable, unsafe/counter-therapeutic, and genotype-independent cytotoxic. |
| D7 | Provenance chain | `flowchart LR` | method | Versioned figshare record → `.part` → md5 + size check → placed on pass, quarantined as `.bad` on fail → pipeline re-verifies and reports release. |
| D8 | The gauntlet | `flowchart TD` | evidence | Compounds tested → per-genotype candidates → CI survivors, counts on the edges. |
| D9 | Circular vs blind benchmark | `flowchart LR`, two subgraphs | evidence | Left: ΔpS′ ranks compounds → reference set → window tested against it → 100% recovery, with the arrow looping back to its own source. Right: literature → frozen timestamped reference → recovery, misses, and enrichment computed after. |

### Deliberate omissions

- **No mermaid rendering of asinh versus log, and none of the pS′_WT/pS′_MUT scatter.** `xychart-beta`
  cannot draw either honestly, and `quadrantChart` would place the four sign-combinations correctly while
  silently dropping the diagonal — which is the load-bearing feature, since mutant-selective means above
  the diagonal, not inside a quadrant. If these are wanted, generate them as SVG from the numpy/pandas
  stack already pinned in `requirements.txt` and commit the image files.
- **`sankey-beta` is not used for D8** despite being the natural shape for attrition. GitHub's mermaid
  version lags upstream and sankey support is inconsistent; a flowchart with edge counts renders
  everywhere. Sankey is a later upgrade once rendering is confirmed.
- **`scope.md` gets no diagram.** A concept-versus-status table is clearer than any graph of absences.

## Consistency rules

1. **Every number the repo computes traces to a committed CSV**, and the prose names the file it came
   from. No repo finding is transcribed from the review.

   Numbers the repo does *not* compute must be attributed inline to their source and never presented as
   repo output. Two categories appear in these docs: the 4PL pathology percentages in `method.md` §1 and
   diagram D2, which come from the manuscript's own audit; and the PRISM assay design in `scope.md` (8
   steps at 4-fold dilution from 10 µM), which is a property of the screen. Both must read as attributed
   facts, not as findings established here.
2. **`tests/test_docs_numbers.py` enforces rule 1 for the headline repo figures.** The four source CSVs — `results/candidate_null.csv`,
   `results/line_centring.csv`, `results/bootstrap_ci_summary.csv`,
   `concordance/results/concordance_report.csv` — are all committed, so the test needs no gated data and
   runs in CI.

   Design: the test reads each CSV, formats the value at the precision the docs present it (integer
   counts, two decimals for permutation FDR), and asserts that string appears in the relevant markdown
   file. No markdown parsing and no marker comments — if a CSV value changes, the expected string changes
   and the assertion fails until the doc is updated. Add it to the `smoke.yml` step that already runs
   `tests/test_synthetic.py`.
3. **The manuscript stays third-party.** The docs explain the method the code implements and the findings
   the code establishes. They refer to the companion manuscript as in review, do not reproduce its
   unpublished narrative or abstract claims, and do not carry the Drive URL. Diagrams D5 and D6 render
   manuscript ideas as interpretive framing, attributed as such.
4. **One minus-sign glyph.** Standardize on U+2212 in ΔpS′ ≤ −2 throughout; the review flagged mixed
   U+2212 and U+2013 usage, which differ at the boundary.
5. **The root README gains a short Documentation section** linking to `docs/README.md` without
   duplicating its content, and `CLAUDE.md` gains a pointer noting that the docs quote committed results
   and must move with them.

## Out of scope

Rewriting the root `README.md`; changing any analysis code; implementing any of the gaps listed in
`scope.md`; expanding the concordance reference set; and generating the deferred SVG plots.

## Next step

Invoke the writing-plans skill to produce an implementation plan against this spec.
