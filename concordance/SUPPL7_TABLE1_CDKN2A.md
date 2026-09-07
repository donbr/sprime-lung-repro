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

## 2. Terms used in this supplement

A reader who does not hold *universe*, *recovered*, *miss* and *enrichment* cannot read the table below, so they are defined before the results rather than after.

**The metric**

| Term | Meaning |
|---|---|
| S′ | Signed potency–efficacy index for one compound in one cell line. Sign is kept: positive is net inhibition. |
| pS′ | Cohort mean of S′ for one compound across the cell lines of one genotype cohort. |
| ΔpS′ | pS′ in wildtype minus pS′ in mutant. **More negative means more mutant-selective.** |
| the window | The selection rule: pS′ positive in both cohorts **and** ΔpS′ ≤ −2, with at least 3 measured lines per cohort. |
| candidate | A compound that passes the window for a given genotype. |

**The benchmark**

| Term | Meaning |
|---|---|
| census, or reference set | The vulnerabilities compiled **from the literature**, frozen and hashed before any result was consulted. The thing the window is tested against. |
| blinded census assembly | The step that produces it: isolated agents compile the set from stated inclusion criteria, their output is transferred verbatim into a file, and the file is frozen and hashed before any scoring runs. |
| structural blinding | The safeguard. The blind follows from how that step is built, not from what anyone knew. See §9.4. |
| directional census | The **primary** 93-row set, excluding rows whose sensitive genotype is the wildtype one. The full 95-row set is reported as a sensitivity analysis. |
| universe | Compounds measured in enough wildtype **and** mutant lines to be scored at all. The testable pool. |
| reference-in-universe | Census compounds that are actually in the universe. The rest cannot be scored either way. |
| recovered | Reference-in-universe compounds that the window also selected. |
| miss | A reference compound that **was** tested and was **not** selected. Misses are reported; a benchmark without them is not a benchmark. |
| recovery | Recovered divided by reference-in-universe. **Not** a sensitivity, and not an accuracy. |
| enrichment | Whether the recovered count exceeds what a *random* window of the same size would recover. Reported two ways, closed-form and by 10,000 random draws. |

## 3. Headline result

| | |
|---|---|
| Reference compounds tested in the CDKN2A cohort | **12** |
| Recovered by the window (pS′<sub>WT</sub> > 0, pS′<sub>MUT</sub> > 0, ΔpS′ ≤ −2) | **0 (0%)** |
| Missed | **12** |
| Tested universe / candidates passing the window | 1402 / 48 |
| Hypergeometric p | **1** |
| Permutation p (10,000×) | **1** |
| Sensitivity analysis (full 95-row census) | 0/12 = 0%, p = 1 / 1 |

## 4. The same method applied to all four genotypes

Run identically, with a census built the same way by the same procedure:

| Genotype | Reference tested | Recovered | Recovery | Hypergeometric p | Permutation p | Verdict |
|---|---:|---:|---:|---|---|---|
| PTEN | 39 | 2 | 5% | 0.942 | 0.937 | chance |
| **CDKN2A** | 12 | 0 | 0% | 1 | 1 | chance (underpowered) |
| RB1 | 94 | 13 | 14% | 0.00988 | 0.0091 | **clears chance** |
| TP53 | 61 | 1 | 2% | 0.511 | 0.522 | chance |

**3 of the 4 fail.** That is the evidence the benchmark is not rigged toward the paper: the same procedure that returns a positive for RB1 returns chance for PTEN, CDKN2A, TP53. In particular the earlier seed-set result for TP53 (p = 5.6 × 10⁻⁸ off five reference rows dominated by the KIF11/Eg5 family) does not survive a proper census — TP53 recovery is 1/61, p = 0.511.

## 5. Table 1 — literature-nominated CDKN2A vulnerabilities and their recovery by the S′ window

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

## 6. The shape of the recovery — the part the old table could not show

Recovery is **partial within every class and zero in some**, which is what a selective signal looks like. A window that recovered everything would be uninformative.

| Class | Recovered / tested |
|---|---|
| CDK4 | 0 / 11 |
| CDK6 | 0 / 6 |

### The 12 misses — report these, always

`AT-7519, P276-00, PHA-793887, PHA-848125, R547, abemaciclib, alvocidib, aminopurvalanol-a, arcyriaflavin-a, palbociclib, ribociclib, ryuvidine`

A benchmark with no misses is not a benchmark. These are compounds the literature nominates and the window did **not** select.

## 7. Robustness — what the enrichment does and does not survive

Every figure in this section is computed, not asserted. The closed-form test is used throughout; it agrees with the permutation test in the headline analysis.

### 7.1 Leave-one-class-out

Targets are grouped into **overlap-closed classes**: two targets share a class when some PRISM compound resolves to both, so a class is exactly the unit that can be removed without partially removing another target's compounds. Each row removes one class from the reference set and rescores.

| Class removed | Its tested / recovered | Reference left | Recovered left | p |
|---|---|---:|---:|---|
| *nothing removed* | — | 12 | 0 | **1** |
| CDK4 + CDK6 | 12 / 0 | 0 | 0 | n/a |

### 7.2 Annotation noise is not driving it

Repeating the analysis using only PRISM's structured target field, discarding every match made through free-text mechanism annotation, gives **0 of 12 recovered, p = 1**. No recovered compound depended on free-text matching.

### 7.3 The window threshold is not cherry-picked

| ΔpS′ threshold | Candidates | Recovered | p |
|---|---:|---:|---|
| ≤ −1 | 155 | 3 | 0.138 |
| ≤ −1.5 | 87 | 1 | 0.538 |
| **≤ −2** | 48 | 0 | **1** |
| ≤ −2.5 | 27 | 0 | 1 |
| ≤ −3 | 13 | 0 | 1 |

The reported threshold is not the most favourable setting in this range, which is what an artifact of threshold choice would look like.

### 7.4 Multiple testing across the four genotypes

| Genotype | p | Bonferroni across 4 |
|---|---|---|
| PTEN | 0.942 | 1 |
| CDKN2A | 1 | 1 |
| RB1 | 0.00988 | 0.0395 |
| TP53 | 0.511 | 1 |

## 8. Draft manuscript text (drop-in for §3.7 / Supplement 7)

> To test whether the S′ selection window recovers established CDKN2A biology, a reference set of CDKN2A-selective vulnerabilities was compiled from the published literature under **structural blinding**. In this blinded census assembly, four isolated AI agents, one per genotype, worked from stated inclusion criteria without access to the analysis repository and without sight of any S′, pS′ or ΔpS′ value; their output was transferred verbatim into the reference file, which was then frozen and checksum-verified before the benchmark was run. Of 12 PRISM compounds annotated to these literature-nominated targets and measured in the CDKN2A cohort (≥3 wildtype and ≥3 mutant lung lines), the window recovered 0 (0%; hypergeometric p = 1, 10,000-permutation p = 1; 0/12, p = 1 in a sensitivity analysis retaining the 2 inverse-direction entries). **Recovery is at chance.** The window does not recover literature-nominated CDKN2A biology in this dataset, and this analysis provides no validation for CDKN2A. The reference set is pan-cancer whereas recovery is measured in lung cell lines, and recovery is not a sensitivity estimate; but neither caveat is needed to read this result, which is simply negative. Of the nominated targets, 8 resolved to no compound in the PRISM 19Q4 library and could not be tested at all — a dataset boundary rather than a negative result. A negative here is informative: the same procedure returns a significant result for RB1, so the benchmark is capable of detecting recovery when it is present.

## 9. What this analysis does not claim

1. **Not a sensitivity estimate.** The design cannot estimate sensitivity, specificity or positive predictive value. Recovery percentage is not accuracy.
2. **Pan-cancer reference, lung measurement.** The census draws on SCLC, breast/TNBC, prostate, hepatocellular, retinoblastoma, ovarian and bladder models; recovery is measured in lung lines. The census records why: *"Lung-specific primary evidence is scarce for PTEN and CDKN2A and moderate for RB1 and TP53. A lung-restricted census would have been too small to test; the pan-cancer scope is a deliberate and necessary choice, and a limitation to state."*
3. **Annotation noise.** Target → compound expansion relies on PRISM's own target/MOA annotations, which the referee review flagged as sometimes wrong (barasertib, for example, is mis-annotated). §6 shows the matched annotation text for every recovered compound so each call can be checked.
4. **The blinding is structural, not absolute.** The assembly step was initiated from within a results-aware project, so the guarantee does not rest on anyone's ignorance. It rests on two procedural facts. The four AI agents that built the rows worked in isolation, without repository access and without sight of any ΔpS′ value. Their output was transferred verbatim — no row added, removed, reworded or reordered — which removes any opportunity to shape the reference set after seeing how it would score. What a reviewer can verify directly is that the reference set has not changed since it was hashed; what structural blinding does not provide is an independent record of the conditions under which the rows were written. A fully independent replication would assemble the census before any results exist. (`BLIND_CENSUS_2026-08-31.md` states this same limitation in terms of the person who commissioned the census; the procedural statement here is the accurate one, and that document is left unedited as the record of the day.)
5. **The freeze commit is retroactive.** The census was hashed and run on 2026-08-31 and committed on 2026-09-06. The hashes, not the commit date, are the evidence.
6. **Model-system annotation is post-hoc.** The *Model system* and *Census caveat* columns were added on 2026-09-06 from the cited primaries and the census assembly notes. They are presentation only and enter no computation.

## 10. Decisions for the authors (surfaced, not applied)

The decisions below concern the RB1 arm, which is the only genotype with a positive result. For CDKN2A the only decision is not to claim validation. See `SUPPL7_TABLE1_RB1.md`.


## 11. Provenance and reproduction

| Item | Value |
|---|---|
| Census `reference_set_2026-08-31.csv` | 95 rows, md5 `a330987d6c02f9cb8826cc65e908301c` |
| Census `reference_set_2026-08-31_directional.csv` | 93 rows, md5 `76845dcc6131ab917717c7724da2c420` |
| Census freeze commit | `9ca5046` (retroactive — see §9.5) |
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

