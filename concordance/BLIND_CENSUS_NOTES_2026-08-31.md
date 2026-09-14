# Census builders' notes — 2026-08-31

Provenance companion to `reference_set_2026-08-31.csv`. Each genotype was built by an isolated agent with
PubMed plus ChEMBL/Open Targets/BioGRID-ORCS, no repository access and no sight of any S′/ΔpS′ value.
Recorded here verbatim in substance: what each builder excluded, what it flagged as contested, and what it
believed belonged but could not evidence to criterion. Read this before scoring any individual row.

**Inclusion criteria applied by all four:** (1) experimental evidence in a cancer model that loss of the
genotype confers selective sensitivity to inhibition of the named target; (2) the comparison is
genotype-comparative — mutant/null vs wildtype or restored; (3) the target is druggable; (4) a live-verified
PMID or DOI exists. Exclusions: reviews without primary data, pan-essential claims without a genotype
comparison, computational predictions without experimental validation.

---

## PTEN — 25 rows, 29 queries

**Excluded as reviews:** PMIDs 41383404, 37533462, 40914134, 27308567, 20049732, 29109859, 24333356.
**Excluded, wrong direction or not comparative:** 39119276 (NAE inhibitors — PTEN loss associated with
*resistance*), 30118842 (PTEN-mutant CRC *resistant* to dual FLT3–AURKA), 39368479, 42133901, 40554389.
**Excluded as contradictory:** 27375368, 33138032 and 32901889 all report *no* PTEN-conditioned synthetic
lethality for PARP/PARG.

> **The PARP1/PTEN axis is genuinely contested** — the founding report (20049735) and several confirmations
> on one side, explicit refutations on the other. One PARP1 row was kept, not several. A scorer may
> legitimately down-weight it.

**Belongs but not evidenceable:** WDHD1 (33221821 — cleanest isogenic screen hit in TNBC, but no inhibitor
exists); mitochondrial complex I (29617673 — strong genotype-comparative data, but no single honest HGNC
symbol for the drug target); STK11 (29566768 — not itself druggable); CD276 (37163614 — comparison is
PTEN+TP53 co-deficiency, not PTEN alone).
**Coverage gap:** *lung*. Five dedicated lung-scoped queries returned essentially no primary,
genotype-comparative PTEN synthetic-lethal study in lung cancer. This census is prostate, glioma,
colorectal and breast. Any lung expectation for PTEN is extrapolation from other lineages.

## CDKN2A — 25 rows, 30 queries

Covers both arms deliberately: the cell-cycle arm (CDK4/6–RB1) and the 9p21 metabolic arm (MTAP
co-deletion → MAT2A/PRMT5), plus 9p21 passenger collateral lethality (ACO1, ADSS2, HBS1L/FOCAD).

**Excluded, single-arm:** 26183925 (eight chordoma lines, all CDKN2A-lost — no comparator), 30236142,
31709901, 34592265 (genotype comparison is for immunotherapy resistance, not CDK4/6i selectivity).
**Excluded, combination-context:** 40694540 and the MAPK arms of 40694535 — comparison is drug-vs-drug
within MTAP-null cells, not MTAP-null vs intact. KRAS/MAP2K1/BRAF therefore have no rows.
**Excluded, not a gene target:** 35430564 (recombinant methioninase depletes a metabolite).

> **RIOK1 is the weakest row** — Hörmann 2018 (PMID 29983885) used analogue-sensitive alleles in isogenic
> MTAP-null/WT lines and found no differential requirement for RIOK1 *kinase activity*. Kept for coverage,
> flagged as contested.
> **HBS1L rows are conditioned on FOCAD loss**, not CDKN2A or MTAP directly — genuine 9p21-adjacent
> collateral lethality, but the isogenic comparison is FOCAD-null vs intact.
> **Clinical caveat on the metabolic arm:** Barekatain 2021 (PMID 34244484) found primary MTAP-deleted
> glioblastomas do *not* accumulate MTA in vivo, because MTAP-expressing stroma metabolises it.

**Coverage gap:** no primary genotype-comparative CDK4/6-inhibitor study in CDKN2A-deleted vs intact
*NSCLC* models was found. The cell-cycle rows are melanoma and glioblastoma. No credible evidence surfaced
for p14ARF-specific (MDM2/TP53-axis) dependencies, or for WEE1/ATR/PLK1/Aurora as CDKN2A-selective targets.

## RB1 — 24 rows, 25 queries

Isoform separation was requested and observed: AURKA and AURKB are separate rows from separate primaries
(published back-to-back; LY3295668 is >1000-fold AURKA-selective), as are CDK4/CDK6 and CCNA2/CCNB1.

**The two inverse-direction rows.** CDK4 and CDK6 / palbociclib (PMID 38528594) are included as the
cleanest *genotype-comparative* form of the negative case — isogenic RB1-knockout clones losing palbociclib
sensitivity, with CDKN2A-deletion and CDK4/MYC-overexpression controls that did not. The builder's own
instruction: *"If the downstream benchmark scores only 'RB1 loss → sensitivity', these two rows should be
dropped rather than counted as positives."* That instruction is the pre-specified rule for the primary
analysis.

**Excluded:** 29617654 (CDC25 — authors report efficacy in deficient *and* proficient TNBC), 32123578
(pevonedistat — no RB1-proficient arm), 30885218 (single-line selectivity claim), 32307447 (CDK7 —
correlative only; the target the builder most believed belongs), 33271982 (three-way combination).
**Thin or caveated:** SKP2 (genetics very strong, pharmacology tool-grade — compound field deliberately
blank); AHR (single prediction-first paper); NUDT15/mercaptopurine (*collateral*, following from chromosomal
proximity to RB1 rather than RB1 function — should not be scored as a functional dependency); CCNA2/CCNB1
(stratified by "compromised G1-S checkpoint / high E2F", of which RB1 loss is the canonical but not the only
cause).

## TP53 — 21 rows, 38 queries

**Excluded as inverse-genotype:** all MDM2/MDMX antagonists; 25758253 (alisertib in TNBC — p53 deficiency
*shifts* response from apoptosis to senescence); 24616378 (efficacy explicitly p53-dependent); 32168910
(MK2 inhibition p53-dependent and, in p53-mutant stem cells, pro-proliferative).
**Excluded, no or negative genotype comparison:** 32522823 (authors state the ATR-CHK1 interaction is
*independent of p53 status*), 28652249 (stratifier is STK11, not TP53), 23873850, 24819061, 30349649.

> **Mitotic / spindle-assembly evidence is the thinnest part of this census, and this matters.** The best
> genotype-comparative mitotic row is PLK1 (19225112). PMID 22592527 (reversine in isogenic HCT116
> TP53−/− vs +/+) is a genuine p53-null-selective post-mitotic-tetraploidy result, but the authors show the
> selectivity is *not* reproduced by MPS1/TTK, AURKA or AURKB knockdown — so it could not be attributed to a
> named target. **KIF18A and KIF11 could not be evidenced to criterion at all:** the KIF18A literature
> stratifies on whole-genome doubling / chromosomal instability, not TP53 genotype, and no retrieved primary
> makes the TP53-mutant vs TP53-WT comparison for KIF11 directly.

**Contested:** CHEK1 rows rest on chemo-combination designs, not single-agent lethality; UCN-01 also
inhibits MK2 (17292828), so its p53-selectivity may be partly MK2-mediated. PRKDC is combination-only and
should be weighted below the POLQ row from the same paper. PMID 22430210 is a caution flag for the whole
CHK1 axis — in mouse models CDKN1A/p21 loss, not p53 loss, was the dominant determinant.
**Belongs but not evidenceable:** MTOR, TTK/MPS1, AURKB, FOXM1, NAMPT, BRD4, CDK9.
**Lung coverage:** two lung-anchored rows — MAPKAPK2 (24239348, autochthonous NSCLC) and WEE1 (21799033).

---

## Cross-cutting observations

1. **The TP53 census contains no KIF11 row, and the builder explains why**: the published mitotic-selectivity
   evidence for TP53 does not resolve to a named, druggable target under a genotype-comparative design. This
   is an independent, blind confirmation of the point already recorded in `README.md`.
2. **The CDKN2A metabolic arm cannot be tested in PRISM 19Q4** — MRTX1719, AMG 193, TNG908, TNG462,
   BMS-986504 and AG-270 are all absent from the library. Twelve of 25 CDKN2A rows resolve, and they are the
   CDK4/6 arm.
3. **Lung-specific primary evidence is scarce for PTEN and CDKN2A** and moderate for RB1 and TP53. A
   lung-restricted census would have been too small to test; the pan-cancer scope is a deliberate and
   necessary choice, and a limitation to state.
4. All PMIDs and DOIs were retrieved live from PubMed during census construction; none were written from
   memory. According to PubMed.
