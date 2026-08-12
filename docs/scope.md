# What this repository does not establish

The controls documented in [evidence.md](evidence.md) are specific: each one tests a particular confound
against a particular candidate list, and each states plainly what it found. None of them, individually or
together, adds up to a general guarantee that every remaining candidate is real. A reader should not infer
that a control not listed there was quietly passed elsewhere in the code. This document names, plainly, the
analyses this repository does not perform — every gap below is a real check the companion manuscript (in
review)'s referee review asked for, and that this code does not carry out.

## Coverage at a glance

| Concept | Implemented here |
|---|---|
| S′ / pS′ / ΔpS′ and the SL window | yes |
| Label-permutation null | yes |
| Line-centring / general-sensitivity control | yes |
| Per-compound bootstrap CI gate | yes |
| Literature-blind concordance engine | yes (engine only; reference set incomplete) |
| DEMETER2 RNAi cross-check | yes (needs the optional input) |
| Curve fit-quality / minimum-E_max gate | no |
| EC₅₀ censoring at the tested dose range | no |
| Copy-number (deep deletion) genotype calls | no |
| Gaussian-mixture embedding of response profiles | no |
| Benjamini–Hochberg on the primary significance test | no |
| Multi-gene interaction terms | no |

## No fit-quality gate

This is the most consequential gap, and the one most likely to be misread, so it goes first.

For a near-inactive compound — one whose fitted E_max spans only a point or two of assay noise around
zero — EC₅₀ is essentially unidentifiable: the fit is trying to locate the midpoint of a transition that
barely exists. Yet S′ = asinh((E_max / EC₅₀) × 1 µM) grows without bound as the fitted EC₅₀ shrinks toward
zero, regardless of how small or noise-driven E_max is. A curve that is, physically, flat can still produce
an arbitrarily large |S′| purely because the fitting routine placed EC₅₀ close to zero. This is the most
likely explanation for implausible hits — compounds such as aspirin or ranitidine, with no known
genotype-selective mechanism, appearing as apparent synthetic-lethal candidates.

**The bootstrap CI gate documented in `evidence.md` does not remove these.** A flat, noise-dominated curve
whose S′ is artifactual can still be *numerically stable*: refit the same near-flat curve on a bootstrap
resample of cell lines and the fitting routine tends to land on a similar unidentifiable EC₅₀ each time,
producing a tight, reproducible confidence interval around a wrong number. Stability across resamples is
evidence the estimate doesn't jump around — it is not evidence the estimate is measuring a real effect. A
reader who sees `bootstrap_ci_gate.py` in this repository and concludes that flat-curve artifacts are
therefore handled has drawn exactly the wrong conclusion from its presence.

A fit-quality gate — for example, a minimum E_max magnitude below which a fit is excluded regardless of its
S′ — would need to run before S′ is computed at all, upstream in `sprime_pipeline.py`. No such gate exists
in this repository.

## No EC₅₀ range censoring

The PRISM secondary screen this data comes from runs 8 dose steps at 4-fold serial dilution starting from
10 µM, reaching approximately 0.61 nM at the lowest step — a property of the screen's design, not a figure
computed anywhere in this repository. A fitted EC₅₀ below that lowest tested concentration is an
extrapolation past the edge of the measured dose range, not an interpolation within it. This repository does
not flag or censor such values: every fitted EC₅₀, however far outside the tested range, feeds into S′ on
equal footing with EC₅₀ values that fall squarely inside it. An S′ built on an extrapolated EC₅₀ is model
output, not measurement.

## No copy-number genotypes

Genotype calls, as described in `method.md`, come from the damaging-mutation matrix alone. That matrix
cannot see a deep deletion — a gene lost entirely, with no point mutation to call. CDKN2A in particular is
inactivated in lung cancer predominantly by homozygous deletion rather than by point mutation, so cell lines
carrying a CDKN2A deep deletion are scored wild type by this pipeline's genotype-calling logic, quietly
contaminating the wild-type cohort with lines that are functionally CDKN2A-null. That contamination biases
ΔpS′ toward zero for the CDKN2A arm — a real mutant-selective effect would be diluted by wild-type-labeled
lines that are not, in fact, wild type — which is one reason the CDKN2A arm is the weakest of the four in
`evidence.md`, and part of why its concordance cannot be benchmarked at all (`concordance/` has no CDKN2A
reference entries). RB1 and PTEN losses are also frequently copy-number events in lung cancer, so this gap
is not unique to CDKN2A, only most acute there.

`DOWNLOAD_CHECKLIST.md` names `CRISPRGeneDependency.csv` (DepMap CRISPR, 24Q2) as an available input — it
could, in principle, support a copy-number-aware genotype call — but it is deliberately not wired into any
script in this repository.

## No GMM, no BH-FDR, no interaction terms

Three further gaps, briefly.

The companion manuscript's mixture-model embedding of compound response profiles — a Gaussian-mixture
clustering over curve shape, rather than a direct threshold on pS′ and ΔpS′ — is not implemented here.

Benjamini–Hochberg multiple-testing correction is implemented in this repository, but only inside
`demeter_validation.py`, for the DEMETER2 RNAi cross-check. The primary significance analysis — the SL
window and the label-permutation null in `evidence.md` — uses a family-wise threshold (ΔpS′ ≤ −2, and an
empirical p-value against the null) instead of an FDR-controlled procedure.

No multi-gene interaction term is fitted anywhere in this repository. This is the gap that matters most,
because it is precisely where the companion manuscript's network-level thesis — that these vulnerabilities
interact across genes rather than acting as four independent single-gene effects — would have to be tested,
and this repository does not test it. Every analysis here is a single-gene, two-cohort contrast: one gene,
wild type versus mutant, repeated independently across PTEN, CDKN2A, RB1, and TP53. Nothing here fits a
model in which two or more genotypes jointly predict response.

## The concordance reference set is incomplete

`concordance/reference_seed_grounded.csv` holds 7 rows: 5 for RB1, 1 for PTEN, 1 for TP53, and none for
CDKN2A. Of those 7 rows, 5 carry neither a PMID nor a DOI, and the `search_terms` column is empty on all 7
— even though the blind-assembly protocol described in `evidence.md` and `CONNECTORS.md` makes both fields
mandatory: search terms and provenance are supposed to be recorded precisely so the reference set can be
checked as having been assembled independently of this analysis's own output, not selected to match it.
With those fields unfilled on most or all rows, that independence is asserted rather than demonstrated for
this seed set. Those fields are load-bearing, not bookkeeping — the whole remedy for the manuscript's
circularity problem rests on them. Treat the concordance numbers reported in `evidence.md` as illustrative
of the protocol working, not as a finished or comprehensive benchmark.

## No network access at analysis time

To be clear about what is *not* a gap: the numeric pipeline itself never calls a network service while it
computes. All literature and database lookups happen upstream of the pipeline, in an interactive session,
to build the frozen input files (`concordance/reference_seed_grounded.csv` among them) that the pipeline
then reads — see `CONNECTORS.md` for how that boundary is kept. This is what makes the analysis
reproducible and safe to run in CI. The cost is that curation — including the incomplete provenance
described above — is a manual step that happens outside the pipeline and is not itself verified by any
script in this repository.
