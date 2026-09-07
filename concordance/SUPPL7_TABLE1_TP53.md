# Supplement 7 — Table 1 (TP53), rebuilt from the literature-blind benchmark

**Generated** by `concordance/build_suppl7_table1.py` from frozen inputs. Every figure below is derived at run time; none is transcribed. The generator self-verifies against the committed engine output and refuses to write if any acceptance gate fails.

## 1. What changed, and why the old table could not answer the question

The old Table 1 and this one are **different objects, not two versions of the same table**.

- **Old.** Start from the compounds the S′ window selected, then find a citation for each. It asks *"can I find literature for what I selected?"* The answer is yes by construction, so the table could not fail, and a table that cannot fail cannot validate anything.
- **New.** Start from the literature, written down and frozen **before anyone looked at ΔpS′**, then ask *"how many of those prior expectations does the window recover in the lung cell lines?"* — reported with the **misses** and an **enrichment p-value** against a random window of the same size.

Two words the old table conflated, kept separate here:

| | Question | Answer |
|---|---|---|
| **Verification** | Does every number regenerate from the frozen inputs? | Yes — this document is generated, and the generator fails closed if it does not reproduce the committed engine output. |
| **Validation** | Does recovery beat chance? | **TP53**, p = 0.511 (hypergeometric), 0.522 (permutation). |

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
| Reference compounds tested in the TP53 cohort | **61** |
| Recovered by the window (pS′<sub>WT</sub> > 0, pS′<sub>MUT</sub> > 0, ΔpS′ ≤ −2) | **1 (2%)** |
| Missed | **60** |
| Tested universe / candidates passing the window | 1402 / 16 |
| Hypergeometric p | **0.511** |
| Permutation p (10,000×) | **0.522** |
| Sensitivity analysis (full 95-row census) | 1/61 = 2%, p = 0.511 / 0.522 |

## 4. The same method applied to all four genotypes

Run identically, with a census built the same way by the same procedure:

| Genotype | Reference tested | Recovered | Recovery | Hypergeometric p | Permutation p | Verdict |
|---|---:|---:|---:|---|---|---|
| PTEN | 39 | 2 | 5% | 0.942 | 0.937 | chance |
| CDKN2A | 12 | 0 | 0% | 1 | 1 | chance (underpowered) |
| RB1 | 94 | 13 | 14% | 0.00988 | 0.0091 | **clears chance** |
| **TP53** | 61 | 1 | 2% | 0.511 | 0.522 | chance |

**3 of the 4 fail.** That is the evidence the benchmark is not rigged toward the paper: the same procedure that returns a positive for RB1 returns chance for PTEN, CDKN2A, TP53. In particular the earlier seed-set result for TP53 (p = 5.6 × 10⁻⁸ off five reference rows dominated by the KIF11/Eg5 family) does not survive a proper census — TP53 recovery is 1/61, p = 0.511.

## 5. Table 1 — literature-nominated TP53 vulnerabilities and their recovery by the S′ window

Each row is a **target the literature nominated**, not a compound the window selected. *Tested* = PRISM 19Q4 compounds annotated to that target and measured in ≥3 TP53-wildtype and ≥3 TP53-mutant lung lines. **Targets overlap** — a pan-Aurora compound is annotated to both AURKA and AURKB — so the column does **not** sum; the union is the headline.

| Reference target | Evidence (PMID) | Model system | Tested | Recovered | Recovered compounds | Census caveat |
|---|---|---|---:|---:|---|---|
| **PLK1** | 19225112 | colorectal (isogenic HCT116) | 7 | **1** | rigosertib | — |
| HDAC6 | 21637290 | pan-cancer | 13 | 0 | — | — |
| CHEK1 | 23839309, 22446188, 30103170 | HNSCC; TNBC; breast | 10 | 0 | — | chemo-combination design / chemo-combination; UCN-01 also inhibits MK2 (PMID 17292828) |
| HSP90AA1 | 26009011 | mouse (mutant-p53) | 9 | 0 | — | — |
| HMGCR | 22265415 | breast | 7 | 0 | — | — |
| DNMT1 | 25238040 | pan-cancer | 5 | 0 | — | — |
| ATR | 21490603, 26563132, 21552262 | pan-cancer; CLL | 4 | 0 | — | — |
| PRKDC | 35972384 | pan-cancer | 3 | 0 | — | combination-only — weight below the POLQ row from the same paper |
| WEE1 | 19887545, 21799033 | pan-cancer; lung, breast, prostate | 2 | 0 | — | chemo-combination design / radiosensitisation design |
| POLQ | 35972384 | pan-cancer | 1 | 0 | — | — |
| CDC7 | 31578521 | hepatocellular | 0 | — | *no compound in PRISM 19Q4* | — |
| MAPKAPK2 | 24239348 | NSCLC (lung) | 0 | — | *no compound in PRISM 19Q4* | — |
| MVK | 27775703 | pan-cancer | 0 | — | *no compound in PRISM 19Q4* | — |
| PIP4K2A | 34001596 | pan-cancer | 0 | — | *no compound in PRISM 19Q4* | — |
| PIP4K2B | 34001596 | pan-cancer | 0 | — | *no compound in PRISM 19Q4* | — |
| **Union** | — | — | **61** | **1** | 2% | p = 0.511 / 0.522 |

**5 nominated targets could not be tested at all** (CDC7, MAPKAPK2, MVK, PIP4K2A, PIP4K2B): the PRISM Repurposing 19Q4 library contains no compound annotated to them. That is a **dataset boundary, not a negative result**, and it must not be read as the window missing them.

**The census grades its own rows.** The caveat column is quoted in substance from the census assembly notes, not added afterwards to explain results away. Rows carrying a caveat (CHEK1, PRKDC, WEE1) should be weighted below the rest by any reader scoring this table.

## 6. The shape of the recovery — the part the old table could not show

Recovery is **partial within every class and zero in some**, which is what a selective signal looks like. A window that recovered everything would be uninformative.

| Class | Recovered / tested |
|---|---|
| PLK1 | 1 / 7 |
| HDAC6 | 0 / 13 |
| CHEK1 | 0 / 10 |
| HSP90AA1 | 0 / 9 |
| HMGCR | 0 / 7 |
| DNMT1 | 0 / 5 |
| ATR | 0 / 4 |
| PRKDC | 0 / 3 |
| WEE1 | 0 / 2 |
| POLQ | 0 / 1 |

### The 60 misses — report these, always

`7-hydroxystaurosporine, ACY-1215, AT13387, AZ20, AZD7762, BI-2536, BIIB021, BX-912, CHIR-124, ETP-46464, GSK461364, GW-843682X, HMN-214, JNJ-26481585, LY2603618, MK-1775, NMS-1286937, NVP-AUY922, NVP-BEZ235, PCI-24781, PD-407824, PD-98059, PF-477736, PI-103, PIK-75, PP-121, PU-H71, RG108, SB-218078, SCH-900776, SGI-1027, SNX-5422, U-0126, VE-821, VER-49009, alvespimycin, atorvastatin, azacitidine, belinostat, dacinostat, decitabine, fluvastatin, ganetespib, givinostat, lovastatin, mevastatin, nadide, nexturastat-a, novobiocin, panobinostat, pitavastatin, resminostat, romidepsin, scriptaid, simvastatin, tanespimycin, trichostatin-a, triclabendazole, volasertib, vorinostat`

A benchmark with no misses is not a benchmark. These are compounds the literature nominates and the window did **not** select.

### How each recovered compound matched

Target → compound resolution runs against PRISM's own target/MOA annotation strings, which the review flagged as sometimes wrong. The matched text is shown so a reader can judge each call rather than take it on trust.

| Recovered compound | Matched target(s) | PRISM annotation text |
|---|---|---|
| rigosertib | PLK1 | `PLK1 ; cell cycle inhibitor, PLK inhibitor` |

## 7. Robustness — what the enrichment does and does not survive

Every figure in this section is computed, not asserted. The closed-form test is used throughout; it agrees with the permutation test in the headline analysis.

### 7.1 Leave-one-class-out

Targets are grouped into **overlap-closed classes**: two targets share a class when some PRISM compound resolves to both, so a class is exactly the unit that can be removed without partially removing another target's compounds. Each row removes one class from the reference set and rescores.

| Class removed | Its tested / recovered | Reference left | Recovered left | p |
|---|---|---:|---:|---|
| *nothing removed* | — | 61 | 1 | **0.511** |
| PLK1 | 7 / 1 | 54 | 0 | **1** |
| HDAC6 | 13 / 0 | 48 | 1 | **0.429** |
| CHEK1 | 10 / 0 | 51 | 1 | **0.449** |
| HSP90AA1 | 9 / 0 | 52 | 1 | **0.456** |
| HMGCR | 7 / 0 | 54 | 1 | **0.468** |
| DNMT1 | 5 / 0 | 56 | 1 | **0.481** |
| ATR | 4 / 0 | 57 | 1 | **0.487** |
| PRKDC | 3 / 0 | 58 | 1 | **0.493** |
| WEE1 | 2 / 0 | 59 | 1 | **0.499** |
| POLQ | 1 / 0 | 60 | 1 | **0.505** |

### 7.2 Annotation noise is not driving it

Repeating the analysis using only PRISM's structured target field, discarding every match made through free-text mechanism annotation, gives **1 of 61 recovered, p = 0.511**. No recovered compound depended on free-text matching.

### 7.3 The window threshold is not cherry-picked

| ΔpS′ threshold | Candidates | Recovered | p |
|---|---:|---:|---|
| ≤ −1 | 68 | 7 | 0.0249 |
| ≤ −1.5 | 34 | 1 | 0.784 |
| **≤ −2** | 16 | 1 | **0.511** |
| ≤ −2.5 | 8 | 1 | 0.3 |
| ≤ −3 | 6 | 1 | 0.235 |

The reported threshold is not the most favourable setting in this range, which is what an artifact of threshold choice would look like.

### 7.4 Multiple testing across the four genotypes

| Genotype | p | Bonferroni across 4 |
|---|---|---|
| PTEN | 0.942 | 1 |
| CDKN2A | 1 | 1 |
| RB1 | 0.00988 | 0.0395 |
| TP53 | 0.511 | 1 |

## 8. Draft manuscript text (drop-in for §3.7 / Supplement 7)

> To test whether the S′ selection window recovers established TP53 biology, a reference set of TP53-selective vulnerabilities was compiled from the published literature under **structural blinding**. In this blinded census assembly, four isolated AI agents, one per genotype, worked from stated inclusion criteria without access to the analysis repository and without sight of any S′, pS′ or ΔpS′ value; their output was transferred verbatim into the reference file, which was then frozen and checksum-verified before the benchmark was run. Of 61 PRISM compounds annotated to these literature-nominated targets and measured in the TP53 cohort (≥3 wildtype and ≥3 mutant lung lines), the window recovered 1 (2%; hypergeometric p = 0.511, 10,000-permutation p = 0.522; 1/61, p = 0.511 in a sensitivity analysis retaining the 2 inverse-direction entries). **Recovery is at chance.** The window does not recover literature-nominated TP53 biology in this dataset, and this analysis provides no validation for TP53. The reference set is pan-cancer whereas recovery is measured in lung cell lines, and recovery is not a sensitivity estimate; but neither caveat is needed to read this result, which is simply negative. Of the nominated targets, 5 resolved to no compound in the PRISM 19Q4 library and could not be tested at all — a dataset boundary rather than a negative result. A negative here is informative: the same procedure returns a significant result for RB1, so the benchmark is capable of detecting recovery when it is present.

## 9. What this analysis does not claim

1. **Not a sensitivity estimate.** The design cannot estimate sensitivity, specificity or positive predictive value. Recovery percentage is not accuracy.
2. **Pan-cancer reference, lung measurement.** The census draws on SCLC, breast/TNBC, prostate, hepatocellular, retinoblastoma, ovarian and bladder models; recovery is measured in lung lines. The census records why: *"Lung-specific primary evidence is scarce for PTEN and CDKN2A and moderate for RB1 and TP53. A lung-restricted census would have been too small to test; the pan-cancer scope is a deliberate and necessary choice, and a limitation to state."*
3. **Annotation noise.** Target → compound expansion relies on PRISM's own target/MOA annotations, which the referee review flagged as sometimes wrong (barasertib, for example, is mis-annotated). §6 shows the matched annotation text for every recovered compound so each call can be checked.
4. **The blinding is structural, not absolute.** The assembly step was initiated from within a results-aware project, so the guarantee does not rest on anyone's ignorance. It rests on two procedural facts. The four AI agents that built the rows worked in isolation, without repository access and without sight of any ΔpS′ value. Their output was transferred verbatim — no row added, removed, reworded or reordered — which removes any opportunity to shape the reference set after seeing how it would score. What a reviewer can verify directly is that the reference set has not changed since it was hashed; what structural blinding does not provide is an independent record of the conditions under which the rows were written. A fully independent replication would assemble the census before any results exist. (`BLIND_CENSUS_2026-08-31.md` states this same limitation in terms of the person who commissioned the census; the procedural statement here is the accurate one, and that document is left unedited as the record of the day.)
5. **The freeze commit is retroactive.** The census was hashed and run on 2026-08-31 and committed on 2026-09-06. The hashes, not the commit date, are the evidence.
6. **Model-system annotation is post-hoc.** The *Model system* and *Census caveat* columns were added on 2026-09-06 from the cited primaries and the census assembly notes. They are presentation only and enter no computation.

## 10. Decisions for the authors (surfaced, not applied)

The decisions below concern the RB1 arm, which is the only genotype with a positive result. For TP53 the only decision is not to claim validation. See `SUPPL7_TABLE1_RB1.md`.


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
uv run --locked python concordance/build_suppl7_table1.py --genotype TP53
```

