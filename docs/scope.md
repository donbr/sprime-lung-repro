# What this repository does not establish

The controls documented in [evidence.md](evidence.md) are specific: each one tests a particular confound
against a particular candidate list, and each states plainly what it found. None of them, individually or
together, adds up to a general guarantee that every remaining candidate is real. A reader should not infer
that a control not listed there was quietly passed elsewhere in the code. This document names, plainly, the
analyses this repository does not perform — every gap below is a real analysis a peer reviewer of the
companion manuscript (in review) asked for, and that this code does not carry out.

## Coverage at a glance

| Concept | Implemented here |
|---|---|
| S′ / pS′ / ΔpS′ and the SL window | yes |
| Label-permutation null | yes |
| Line-centring / general-sensitivity control | yes |
| Per-compound bootstrap CI gate | yes |
| Literature-blind concordance engine | yes (engine only; reference set incomplete) |
| DEMETER2 RNAi cross-check | yes (output committed; regenerating needs the optional input) |
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
inactivated in lung cancer predominantly by homozygous deletion rather than by point mutation (TCGA Research
Network 2012, PMID 22960745 [L6]), so cell lines
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
`demeter_validation.py`, for the DEMETER2 RNAi cross-check. What is missing from the primary significance
analysis — the SL window and the label-permutation null in `evidence.md` — is specifically the
Benjamini–Hochberg procedure, not FDR control as such: `blocking_analyses.py` already computes an empirical
permutation FDR for every gene (`perm_fdr = null.mean() / nobs`, logged with the guidance that only
genotypes with perm_FDR well below roughly 0.5 carry signal beyond chance), and `evidence.md` reports that
quantity as its own column for all four genes. So it would be wrong to say this repository's primary
analysis lacks FDR control; it estimates FDR by permutation rather than by the Benjamini–Hochberg procedure.
That is a separate question from what the companion manuscript's own primary significance rule does: the
manuscript's ΔpS′ ≤ −2 cutoff is a family-wise threshold, a single fixed effect-size bar applied without any
FDR estimate attached to it — a distinct statistical concept from FDR control, whether permutation-estimated
or BH-derived, and the two are easy to conflate on a skim. This repository's own primary analysis is not
that: it carries a permutation-estimated FDR alongside the same effect-size cutoff, and the gap named in the
table above is only that it never routes that estimate through Benjamini–Hochberg specifically.

No multi-gene interaction term is fitted anywhere in this repository. This is the gap that matters most,
because it is precisely where the companion manuscript's network-level thesis — that these vulnerabilities
interact across genes rather than acting as four independent single-gene effects — would have to be tested,
and this repository does not test it. Every analysis here is a single-gene, two-cohort contrast: one gene,
wild type versus mutant, repeated independently across PTEN, CDKN2A, RB1, and TP53. Nothing here fits a
model in which two or more genotypes jointly predict response.

## The DEMETER2 cross-check's real caveats

`results/demeter_validation.csv` is committed, and its RB–E2F/CDK4-6 result is now a checkable, obtained
finding rather than an unverifiable one (see [evidence.md](evidence.md) and [verifying.md](verifying.md)) —
the missing artifact is no longer the honest caveat here. Two narrower ones remain. RB1's own RNAi result
rests on a mutant cohort of only 6 cell lines, smaller than any of the four PRISM cohorts in `method.md`'s
cohort table and the same kind of small-cohort fragility PTEN's 3-line mutant pool carries in the
drug-response analysis — a result resting on 6 lines should be read as suggestive, not as backed by a broad,
well-powered cohort. And PTEN itself is entirely absent from that CSV: its DEMETER2-covered mutant cohort
falls below the `--min-lines` floor of 5 that `demeter_validation.py` applies uniformly to every target, so
no PTEN target can be assessed by RNAi at all under this cross-check. That is a coverage gap in this
analysis, not evidence that PTEN dependencies do not exist.

## The concordance reference set is incomplete

`concordance/reference_seed_grounded.csv` holds 7 rows: 5 for RB1, 1 for PTEN, 1 for TP53, and none for
CDKN2A. The blind-assembly protocol described in `evidence.md` and `CONNECTORS.md` makes a PMID/DOI and a
recorded `search_terms` string mandatory on every row: search terms and provenance are supposed to be
recorded precisely so the reference set can be checked as having been assembled independently of this
analysis's own output, not selected to match it. Those fields are load-bearing, not bookkeeping — the whole
remedy for the manuscript's circularity problem rests on them.

A re-documentation pass (`date_redocumented` 2026-09-13) narrowed that gap. A distinct, re-runnable query is
now recorded on each of the 7 rows, and 6 of the 7 carry a PMID and DOI — 5 of them as support, and one
(TP53→KIF11) as counter-evidence. The five supporting citations are the two Aurora rows (Gong 2019,
PMID 30373917; Oser 2019, PMID 30373918), RB1→PLK1 and RB1→CHEK1 (both Nastase 2021, PMID 34580349,
doi:10.1038/s41598-021-98414-w [L10]), and RB1→PARP1 (Zoumpoulidou 2021, PMID 34862364,
doi:10.1038/s41467-021-27291-8 [L11]). The pass did **not** re-freeze the set: `date_frozen` remains
2026-07-05 on every row, because that date is the audit trail showing the set predates the ΔpS′ scoring, and
overwriting it would destroy the very independence B1 exists to demonstrate.

That audit trail is an attestation, not a verified timestamp, and the distinction is load-bearing. The freeze
date is a self-asserted column value: it predates this repository's initial commit (`02b06ce`, 2026-08-11) by
five weeks, and that initial commit is where `reference_seed_grounded.csv` and the scored
`concordance_report.csv` both first appear. The repository carries no tags. So the protocol's "commit with a
timestamp / git tag" has neither, and no possible ordering evidence exists within this history — the claim
that the set was assembled blind to ΔpS′ rests on the curator's word rather than on version control.
Restoring `date_frozen` was still right, because overwriting it would have removed even the attestation; but
an attestation is what it is, and it should not be read as a verified freeze.

Each row now also carries a `support_status` — `supported`, `supported-no-contrast`, `uncited` or
`contradicted` — so a reader does not have to infer the strength of a row from whether its `pmid` cell
happens to be filled. The distinction matters: Zoumpoulidou 2021 reports an explicit genotype contrast
(including engineered RB1 loss, with sensitivity exceeding BRCA-mutant backgrounds), whereas Nastase 2021
reports RB1 deletion in 26% of cases *and* sub-micromolar PLK1/CHEK1-inhibitor responses without ever
comparing RB1-deleted against RB1-intact cells. The latter establishes dependency but not *selective*
dependency, which is the property this benchmark actually scores; both PLK1 and CHEK1 rows are therefore
marked `supported-no-contrast`.

`inclusion_rationale` now also carries a BioGRID ORCS hit fraction, separating rows labelled common-essential
(PLK1 0.63, CHEK1 0.59, KIF11 0.60) from those labelled context-selective (PARP1 0.046, AKT1 0.037) by a
factor of roughly 13–16. **That fraction is marginal across all ORCS screens, so it can establish
pan-essentiality but never genotype-selectivity.** AURKA (0.50) and AURKB (0.61) accordingly sit in the high
band despite the RB1-selective literature; the Aurora rows rest on their publications, not on ORCS, and no
claim of selectivity should be sourced to an ORCS fraction.

Because the pass is retrospective rather than blind assembly, it documents what the seed set already
claimed; it does not make the set an independent census. Two rows carry no supporting citation, and both are
findings rather than clerical gaps:

- **PTEN→AKT1 (MK-2206) is `uncited`.** Three recorded queries over roughly 380 PubMed hits produced no study
  establishing PTEN-deficient-selective sensitivity to AKT1 inhibition. ORCS shows AKT1 is context-selective
  (0.037), but that is a marginal fact and does not tie the selectivity to PTEN. This is also the arm the
  blind benchmark scores at p = 0.30. The row needs manual curation or removal.
- **TP53→KIF11 (ispinesib) is `contradicted` rather than merely uncited.** Its PMID cell is populated with
  Fujiwara 2018 (PMID 30049386, doi:10.1016/j.ebiom.2018.06.031 [L12]) as **counter-evidence**: that paper
  describes a p53–miR-101 circuit repressing EG5 whose prognostic association is in p53 **wild-type** cases,
  the opposite direction from the row's implied claim. With KIF11 pan-essential at 0.60, this independently
  corroborates the caveat in `concordance/README.md`: TP53's p = 5.6e-08 reflects a common-essential target,
  not genotype-selective biology.

The provenance columns are documentation only — `concordance_enrichment.py` reads just `genotype`,
`compound` and `target` — so the pass changed no computed figure, and
`concordance/results/concordance_report.csv` is byte-identical before and after it
(md5 `6f8c724e1986a7fc10edc7db1934263a`).

There is a second, separate gap in that reference set, about resolution rather than provenance, and nothing
in this repository closes it. A reference row names a *target*, not a compound, so
`concordance_enrichment.py` expands each row by token-matching that target against **PRISM's own target and
MOA annotation strings** — which is how 7 curated rows become the 49, 10 and 5 "reference in universe"
compounds reported in `evidence.md`. Those annotations are third-party metadata that this repository takes
at face value and never audits: the referee review of the companion manuscript (in review) flagged them as
sometimes wrong, and `concordance/README.md` (caveat 2) records barasertib as a specific mis-annotated
example. Every enrichment p-value in `evidence.md` therefore inherits whatever annotation errors PRISM
carries — a compound annotated to the wrong target inflates or deflates the reference set silently, and no
script here spot-checks the resolved lists. Neither the recovery counts nor the misses can be read as
cleaner than the annotation layer underneath them.

Treat the concordance numbers reported in `evidence.md` as illustrative of the protocol working, not as a
finished or comprehensive benchmark.

## No network access at analysis time

To be clear about what is *not* a gap: the numeric pipeline itself never calls a network service while it
computes. All literature and database lookups happen upstream of the pipeline, in an interactive session,
to build the frozen input files (`concordance/reference_seed_grounded.csv` among them) that the pipeline
then reads — see `CONNECTORS.md` for how that boundary is kept. This is what makes the analysis
reproducible and safe to run in CI. The cost is that curation — including the incomplete provenance
described above — is a manual step that happens outside the pipeline and is not itself verified by any
script in this repository.

## References

[L6] The Cancer Genome Atlas Research Network. Comprehensive genomic characterization of squamous cell lung
cancers. *Nature* 2012;489(7417):519–525. PMID 22960745. doi:10.1038/nature11404

[L10] Nastase A, Mandal A, Lu SK, et al. Integrated genomics point to immune vulnerabilities in pleural
mesothelioma. *Scientific Reports* 2021;11(1):19138. PMID 34580349. doi:10.1038/s41598-021-98414-w

[L11] Zoumpoulidou G, Alvarez-Mendoza C, Mancusi C, et al. Therapeutic vulnerability to PARP1,2 inhibition
in RB1-mutant osteosarcoma. *Nature Communications* 2021;12(1):7064. PMID 34862364.
doi:10.1038/s41467-021-27291-8

[L12] Fujiwara Y, Saito M, Robles AI, et al. A Nucleolar Stress-Specific p53-miR-101 Molecular Circuit
Functions as an Intrinsic Tumor-Suppressor Network. *EBioMedicine* 2018;33:33–48. PMID 30049386.
doi:10.1016/j.ebiom.2018.06.031
