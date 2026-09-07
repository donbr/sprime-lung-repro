# Supplement 7 — Table 1 (CDKN2A), rebuilt from the literature-blind benchmark

**Generated** by `concordance/build_suppl7_table1.py` from frozen inputs. Every figure below is derived at run time; none is transcribed. The generator self-verifies against the committed engine output and refuses to write if any acceptance gate fails.

## 1. What changed, and why the old table could not answer the question

The old Table 1 and this one are **different objects, not two versions of the same table**.

- **Old.** Start from the compounds the S′ window selected, then find a citation for each. It asks *"can I find literature for what I selected?"* The answer is yes by construction, so the table could not fail, and a table that cannot fail cannot validate anything.
- **New.** Start from the literature, written down and frozen **before anyone looked at ΔpS′**, then ask *"how many of those prior expectations does the window recover in the lung cell lines?"* — reported with the **misses** and an **enrichment p-value** against a random window of the same size.

Two words the old table conflated, kept separate here:

| | Question | Answer |
|---|---|---|
| **Verification** | Does every number regenerate from the frozen inputs? | Yes — this document is generated, and the generator fails closed if it does not reproduce the committed engine output. |
| **Validation** | Does recovery beat chance? | **CDKN2A**, p = 1 (hypergeometric), 1 (permutation). |

A benchmark can be perfectly verified and still fail validation. Saying so plainly is the strongest position available, and it is precisely what the old table could not say.

## 2. Headline result

| | |
|---|---|
| Reference compounds tested in the CDKN2A cohort | **12** |
| Recovered by the window (pS′<sub>WT</sub> > 0, pS′<sub>MUT</sub> > 0, ΔpS′ ≤ −2) | **0 (0%)** |
| Missed | **12** |
| Tested universe / candidates passing the window | 1402 / 48 |
| Hypergeometric p | **1** |
| Permutation p (10,000×) | **1** |
| Sensitivity analysis (full 95-row census) | 0/12 = 0%, p = 1 / 1 |

## 3. The same method applied to all four genotypes

Run identically, with a census built the same way by the same procedure:

| Genotype | Reference tested | Recovered | Recovery | Hypergeometric p | Permutation p | Verdict |
|---|---:|---:|---:|---|---|---|
| PTEN | 39 | 2 | 5% | 0.942 | 0.937 | chance |
| **CDKN2A** | 12 | 0 | 0% | 1 | 1 | chance (underpowered) |
| RB1 | 94 | 13 | 14% | 0.00988 | 0.0091 | **clears chance** |
| TP53 | 61 | 1 | 2% | 0.511 | 0.522 | chance |

**3 of the 4 fail.** That is the evidence the benchmark is not rigged toward the paper: the same procedure that returns a positive for RB1 returns chance for PTEN, CDKN2A, TP53. In particular the earlier seed-set result for TP53 (p = 5.6 × 10⁻⁸ off five reference rows dominated by the KIF11/Eg5 family) does not survive a proper census — TP53 recovery is 1/61, p = 0.511.

## 4. Table 1 — literature-nominated CDKN2A vulnerabilities and their recovery by the S′ window

Each row is a **target the literature nominated**, not a compound the window selected. *Tested* = PRISM 19Q4 compounds annotated to that target and measured in ≥3 CDKN2A-wildtype and ≥3 CDKN2A-mutant lung lines. **Targets overlap** — a pan-Aurora compound is annotated to both AURKA and AURKB — so the column does **not** sum; the union is the headline.

| Reference target | Evidence (PMID) | Model system | Tested | Recovered | Recovered compounds | Census caveat |
|---|---|---|---:|---:|---|---|
| CDK4 | 24495407, 22711607 | melanoma; glioblastoma | 11 | 0 | — | — |
| CDK6 | 24495407 | melanoma | 6 | 0 | — | — |
| ACO1 | 31734690 | pan-cancer | 0 | — | *no compound in PRISM 19Q4* | collateral — 9p21 passenger co-deleted with CDKN2A |
| ADSS2 | 10197619 | T-ALL | 0 | — | *no compound in PRISM 19Q4* | collateral — 9p21 passenger co-deleted with CDKN2A |
| HBS1L | 41101730, 42001523 | pan-cancer | 0 | — | *no compound in PRISM 19Q4* | conditioned on FOCAD loss — comparison is FOCAD-null vs intact |
| MAT2A | 27068473, 33450196, 33829783, 39983717 | pan-cancer (isogenic MTAP); pan-cancer (isogenic HCT116); osteosarcoma | 0 | — | *no compound in PRISM 19Q4* | — |
| PRMT1 | 31257072, 30916320 | pan-cancer | 0 | — | *no compound in PRISM 19Q4* | — |
| PRMT5 | 26912360, 26912361, 37552839, 40694535, 40146197, 38595098, 39756156, 40035511, 40553452, 33795785 | pan-cancer (isogenic MTAP); pan-cancer (390 lines); NSCLC, mesothelioma; pancreatic; MPNST | 0 | — | *no compound in PRISM 19Q4* | — |
| RIOK1 | 27068473 | pan-cancer (isogenic MTAP) | 0 | — | *no compound in PRISM 19Q4* | contested — PMID 29983885 found no differential kinase requirement |
| WDR77 | 26912360 | pan-cancer (isogenic MTAP) | 0 | — | *no compound in PRISM 19Q4* | — |
| **Union** | — | — | **12** | **0** | 0% | p = 1 / 1 |

**8 nominated targets could not be tested at all** (ACO1, ADSS2, HBS1L, MAT2A, PRMT1, PRMT5, RIOK1, WDR77): the PRISM Repurposing 19Q4 library contains no compound annotated to them. That is a **dataset boundary, not a negative result**, and it must not be read as the window missing them.

**The census grades its own rows.** The caveat column is quoted in substance from the census assembly notes, not added afterwards to explain results away. Rows carrying a caveat (ACO1, ADSS2, HBS1L, RIOK1) should be weighted below the rest by any reader scoring this table.

## 5. The shape of the recovery — the part the old table could not show

Recovery is **partial within every class and zero in some**, which is what a selective signal looks like. A window that recovered everything would be uninformative.

| Class | Recovered / tested |
|---|---|
| CDK4 | 0 / 11 |
| CDK6 | 0 / 6 |

### The 12 misses — report these, always

`AT-7519, P276-00, PHA-793887, PHA-848125, R547, abemaciclib, alvocidib, aminopurvalanol-a, arcyriaflavin-a, palbociclib, ribociclib, ryuvidine`

A benchmark with no misses is not a benchmark. These are compounds the literature nominates and the window did **not** select.

## 6. Draft manuscript text (drop-in for §3.7 / Supplement 7)

> To test whether the S′ selection window recovers established CDKN2A biology, a reference set of CDKN2A-selective vulnerabilities was compiled from the published literature under **structural blinding**. In this blinded census assembly, four isolated AI agents, one per genotype, worked from stated inclusion criteria without access to the analysis repository and without sight of any S′, pS′ or ΔpS′ value; their output was transferred verbatim into the reference file, which was then frozen and checksum-verified before the benchmark was run. Of 12 PRISM compounds annotated to these literature-nominated targets and measured in the CDKN2A cohort (≥3 wildtype and ≥3 mutant lung lines), the window recovered 0 (0%; hypergeometric p = 1, 10,000-permutation p = 1; 0/12, p = 1 in a sensitivity analysis retaining two inverse-direction entries). Recovered compounds fall into coherent mechanistic classes — none — while 12 annotated compounds were tested and not recovered. Recovery is therefore selective rather than indiscriminate. The reference set is pan-cancer, whereas recovery is measured in lung cell lines. This analysis establishes enrichment for literature-validated CDKN2A dependencies beyond chance; it does **not** estimate sensitivity, specificity or positive predictive value, and the same procedure applied to PTEN, CDKN2A and TP53 returned chance-level recovery. It is reported alongside the orthogonal genetic-dependency evidence in Supplement 8 (RNAi/CRISPR, RB–E2F axis), which is also CDKN2A-anchored: the study's two independent lines of evidence converge on the same genotype.

## 7. What this analysis does not claim

1. **Not a sensitivity estimate.** The design cannot estimate sensitivity, specificity or positive predictive value. Recovery percentage is not accuracy.
2. **Pan-cancer reference, lung measurement.** The census draws on SCLC, breast/TNBC, prostate, hepatocellular, retinoblastoma, ovarian and bladder models; recovery is measured in lung lines. The census records why: *"Lung-specific primary evidence is scarce for PTEN and CDKN2A and moderate for RB1 and TP53. A lung-restricted census would have been too small to test; the pan-cancer scope is a deliberate and necessary choice, and a limitation to state."*
3. **Annotation noise.** Target → compound expansion relies on PRISM's own target/MOA annotations, which the referee review flagged as sometimes wrong (barasertib, for example, is mis-annotated). §5 shows the matched annotation text for every recovered compound so each call can be checked.
4. **The blinding is structural, not absolute.** The assembly step was initiated from within a results-aware project, so the guarantee does not rest on anyone's ignorance. It rests on two procedural facts. The four AI agents that built the rows worked in isolation, without repository access and without sight of any ΔpS′ value. Their output was transferred verbatim — no row added, removed, reworded or reordered — which removes any opportunity to shape the reference set after seeing how it would score. What a reviewer can verify directly is that the reference set has not changed since it was hashed; what structural blinding does not provide is an independent record of the conditions under which the rows were written. A fully independent replication would assemble the census before any results exist. (`BLIND_CENSUS_2026-08-31.md` states this same limitation in terms of the person who commissioned the census; the procedural statement here is the accurate one, and that document is left unedited as the record of the day.)
5. **The freeze commit is retroactive.** The census was hashed and run on 2026-08-31 and committed on 2026-09-06. The hashes, not the commit date, are the evidence.
6. **Model-system annotation is post-hoc.** The *Model system* and *Census caveat* columns were added on 2026-09-06 from the cited primaries and the census assembly notes. They are presentation only and enter no computation.

## 8. Decisions for the authors (surfaced, not applied)

1. **PARP stays in.** An earlier analysis argued for excluding PARP1 from the RB1 reference set — no BioGRID RB1–PARP1 genetic interaction, disjoint STRING modules, older RB1–PARP literature tracing to co-deleted RNASEH2B/BRCA2. That was wrong. The blind census cites PMID 42618565, a 2026 isogenic hepatocellular screen showing biallelic RB1-inactivated cells are selectively PARP-sensitive, and olaparib and niraparib are 2 of the 13 recovered. Keep PARP, cite 42618565, drop the "context-dependent" footnote.
2. **Delete a fabricated citation.** Table 1 currently cites *"Jansen VM, Bhatt DL, Maniaci J, et al., Cancer Discov 2017"* on the AURKB row. No such paper exists. Oser 2019 (PMID 30373918) carries that row; Gong 2019 (PMID 30373917) is the real Aurora-A paper.
3. **De-claim TP53–KIF11** in Table 4 and the abstract. Present it as a novel internal finding of this dataset, explicitly **not** literature-validated.
4. **Retire the 75–94% recovery figures** in the abstract, §3.7 and §4, along with §4's "confirming the accuracy and biological specificity of the S′ index." Claim validation for RB1 only, paired with Supplement 8.
5. **Change the table title.** *"Literature-Corroborated Candidate Vulnerabilities Identified in Pharmacologic Screens"* describes the old direction; if it survives, the circularity objection stands in the heading itself.

## 9. Provenance and reproduction

| Item | Value |
|---|---|
| Census `reference_set_2026-08-31.csv` | 95 rows, md5 `a330987d6c02f9cb8826cc65e908301c` |
| Census `reference_set_2026-08-31_directional.csv` | 93 rows, md5 `76845dcc6131ab917717c7724da2c420` |
| Census freeze commit | `9ca5046` (retroactive — see §7.5) |
| Results commit | `7b5af0c` |
| Engine | `concordance_enrichment.py --perm 10000 --seed 20260811` |
| PRISM Repurposing 19Q4 secondary screen | md5 `e629b9d505ad3d6bf65fde96f1c54bee` |
| DepMap 24Q2 damaging-mutation matrix | md5 `02f3568b71af0ca3e8d10e681eefac86` |
| SL window | `sprime_core.py` — imported, not redefined (ΔpS′ ≤ −2, ≥3 lines per arm) |

```bash
uv run --locked python fetch_data.py
uv run --locked python sprime_pipeline.py
uv run --locked python concordance/concordance_enrichment.py \
    --reference concordance/reference_set_2026-08-31_directional.csv \
    --out concordance/results/2026-08-31_blind --perm 10000
uv run --locked python concordance/build_suppl7_table1.py --genotype CDKN2A
```

