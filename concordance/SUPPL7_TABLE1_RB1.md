# Supplement 7 — Table 1 (RB1), rebuilt from the literature-blind benchmark

**Generated** by `concordance/build_suppl7_table1.py` from frozen inputs. Every figure below is derived at run time; none is transcribed. The generator self-verifies against the committed engine output and refuses to write if any acceptance gate fails.

## 1. What changed, and why the old table could not answer the question

The old Table 1 and this one are **different objects, not two versions of the same table**.

- **Old.** Start from the compounds the S′ window selected, then find a citation for each. It asks *"can I find literature for what I selected?"* The answer is yes by construction, so the table could not fail, and a table that cannot fail cannot validate anything.
- **New.** Start from the literature, written down and frozen **before anyone looked at ΔpS′**, then ask *"how many of those prior expectations does the window recover in the lung cell lines?"* — reported with the **misses** and an **enrichment p-value** against a random window of the same size.

Two words the old table conflated, kept separate here:

| | Question | Answer |
|---|---|---|
| **Verification** | Does every number regenerate from the frozen inputs? | Yes — this document is generated, and the generator fails closed if it does not reproduce the committed engine output. |
| **Validation** | Does recovery beat chance? | **RB1 only, of the four genotypes tested**, p = 0.00988 (hypergeometric), 0.0091 (permutation). |

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
| Reference compounds tested in the RB1 cohort | **94** |
| Recovered by the window (pS′<sub>WT</sub> > 0, pS′<sub>MUT</sub> > 0, ΔpS′ ≤ −2) | **13 (14%)** |
| Missed | **81** |
| Tested universe / candidates passing the window | 1360 / 94 |
| Hypergeometric p | **0.00988** |
| Permutation p (10,000×) | **0.0091** |
| Sensitivity analysis (full 95-row census) | 13/106 = 12%, p = 0.0258 / 0.0245 |

**The two-row decision rule was written blind.** The RB1 census agent flagged two rows (CDK4 and CDK6 / palbociclib, PMID 38528594) as inverse-direction — there the *RB1-proficient* genotype is the sensitive one — and stated, before any result existed, that they "should be dropped rather than counted as positives" if the benchmark scores RB1-loss → sensitivity. The primary analysis follows that instruction; the full census is reported as the sensitivity analysis above. RB1 clears chance either way.

## 4. The same method applied to all four genotypes

Run identically, with a census built the same way by the same procedure:

| Genotype | Reference tested | Recovered | Recovery | Hypergeometric p | Permutation p | Verdict |
|---|---:|---:|---:|---|---|---|
| PTEN | 39 | 2 | 5% | 0.942 | 0.937 | chance |
| CDKN2A | 12 | 0 | 0% | 1 | 1 | chance (underpowered) |
| **RB1** | 94 | 13 | 14% | 0.00988 | 0.0091 | **clears chance** |
| TP53 | 61 | 1 | 2% | 0.511 | 0.522 | chance |

**3 of the 4 fail.** That is the evidence the benchmark is not rigged toward the paper: the same procedure that returns a positive for RB1 returns chance for PTEN, CDKN2A, TP53. In particular the earlier seed-set result for TP53 (p = 5.6 × 10⁻⁸ off five reference rows dominated by the KIF11/Eg5 family) does not survive a proper census — TP53 recovery is 1/61, p = 0.511.

## 5. Table 1 — literature-nominated RB1 vulnerabilities and their recovery by the S′ window

Each row is a **target the literature nominated**, not a compound the window selected. *Tested* = PRISM 19Q4 compounds annotated to that target and measured in ≥3 RB1-wildtype and ≥3 RB1-mutant lung lines. **Targets overlap** — a pan-Aurora compound is annotated to both AURKA and AURKB — so the column does **not** sum; the union is the headline.

| Reference target | Evidence (PMID) | Model system | Tested | Recovered | Recovered compounds | Census caveat |
|---|---|---|---:|---:|---|---|
| **AURKB** | 30373918 | SCLC | 20 | **7** | AMG900, KW-2449, SNS-314, ZM-447439, barasertib, barasertib-HQPA, tozasertib | — |
| **AURKA** | 30373917, 34741392 | pan-cancer panel (SCLC, TNBC); retinoblastoma | 22 | **6** | AMG900, KW-2449, SNS-314, ZM-447439, barasertib, tozasertib | — |
| **PARP1** | 42618565 | hepatocellular | 7 | **2** | niraparib, olaparib | — |
| **CHEK1** | 29386107 | TNBC | 10 | **1** | SB-218078 | — |
| **XIAP** | 41285729 | TNBC | 5 | **1** | birinapant | — |
| **ATR** | 41442499 | breast | 4 | **1** | NVP-BEZ235 | — |
| **KIF11** | 42618565 | hepatocellular | 4 | **1** | litronesib | — |
| SRC | 33334906 | prostate | 16 | 0 | — | — |
| PLK1 | 29386107 | TNBC | 7 | 0 | — | — |
| AHR | 40276038 | bladder | 4 | 0 | — | prediction-first — single computational SL paper with validation |
| BCL2L1 | 40436896 | prostate | 4 | 0 | — | — |
| CCNA2 | 40836083 | SCLC | 2 | 0 | — | stratified by high-E2F / compromised G1-S — RB1 loss is one cause among others |
| CCNB1 | 40836083 | SCLC | 2 | 0 | — | stratified by high-E2F / compromised G1-S — RB1 loss is one cause among others |
| EZH2 | 28059767 | prostate | 2 | 0 | — | — |
| CSNK2A1 | 38781347 | ovarian (HGSC) | 1 | 0 | — | — |
| NUDT15 | 40904703 | pan-cancer (543 lines) | 1 | 0 | — | collateral — NUDT15 co-deleted with RB1; not a functional dependency |
| TTK | 36070391 | breast (ER+) | 1 | 0 | — | — |
| GPX4 | 36928314 | prostate | 0 | — | *no compound in PRISM 19Q4* | — |
| PKMYT1 | 41442499 | breast | 0 | — | *no compound in PRISM 19Q4* | — |
| SKP2 | 32265224 | SCLC (mouse + PDX) | 0 | — | *no compound in PRISM 19Q4* | genetics strong but pharmacology tool-grade — compound field deliberately blank |
| **Union** | — | — | **94** | **13** | 14% | p = 0.00988 / 0.0091 |

**3 nominated targets could not be tested at all** (GPX4, PKMYT1, SKP2): the PRISM Repurposing 19Q4 library contains no compound annotated to them. That is a **dataset boundary, not a negative result**, and it must not be read as the window missing them.

**The census grades its own rows.** The caveat column is quoted in substance from the census assembly notes, not added afterwards to explain results away. Rows carrying a caveat (AHR, CCNA2, CCNB1, NUDT15, SKP2) should be weighted below the rest by any reader scoring this table.

## 6. The shape of the recovery — the part the old table could not show

Recovery is **partial within every class and zero in some**, which is what a selective signal looks like. A window that recovered everything would be uninformative.

| Class | Recovered / tested |
|---|---|
| Aurora kinase (AURKA ∪ AURKB) | **7 / 25** |
| PARP1 | 2 / 7 |
| CHEK1 | 1 / 10 |
| XIAP | 1 / 5 |
| ATR | 1 / 4 |
| KIF11 | 1 / 4 |
| SRC | 0 / 16 |
| PLK1 | 0 / 7 |
| AHR | 0 / 4 |
| BCL2L1 | 0 / 4 |
| CCNA2 | 0 / 2 |
| CCNB1 | 0 / 2 |
| EZH2 | 0 / 2 |
| CSNK2A1 | 0 / 1 |
| NUDT15 | 0 / 1 |
| TTK | 0 / 1 |

### The 81 misses — report these, always

`1-azakenpaullone, 1-naphthyl-PP1, 2,3-DCPE, 3-amino-benzamide, 3-deazaneplanocin-A, 7-hydroxystaurosporine, ABT-737, AG-14361, AT-9283, AZ20, AZD7762, BI-2536, BX-912, CCT129202, CCT137690, CHIR-124, CR8-(R), CX-4945, CYC116, E7449, ENMD-2076, ETP-46464, GDC-0152, GSK1070916, GSK461364, GW-843682X, HMN-214, JNJ-7706621, K-858, KX2-391, LCL-161, LY2603618, MK-5108, MK-8745, MLN-8054, MNS-(3,4-Methylenedioxy-nitrostyrene), MPI-0479605, NMS-1286937, NU6027, PD-168393, PD-98059, PF-03814735, PF-477736, PHA-680632, PJ-34, PP-1, PP-121, PP-2, SCH-900776, TAK-901, TG-100572, TW-37, U-0126, VE-821, ZM-306416, alisertib, atorvastatin, aurora-a-inhibitor-i, bosutinib, cisplatin, danusertib, dasatinib, embelin, filanesib, flutamide, hesperadin, inosine, ispinesib, kenpaullone, masitinib, mercaptopurine, mexiletine, navitoclax, orantinib, ponatinib, rigosertib, saracatinib, stemregenin-1, tazemetostat, vandetanib, volasertib`

A benchmark with no misses is not a benchmark. These are compounds the literature nominates and the window did **not** select.

### How each recovered compound matched

Target → compound resolution runs against PRISM's own target/MOA annotation strings, which the review flagged as sometimes wrong. The matched text is shown so a reader can judge each call rather than take it on trust.

| Recovered compound | Matched target(s) | PRISM annotation text |
|---|---|---|
| AMG900 | AURKA, AURKB | `AURKA, AURKB, AURKC ; Aurora kinase inhibitor` |
| KW-2449 | AURKA, AURKB | `ABL1, AURKA, AURKB, FLT3 ; Abl kinase inhibitor, Aurora kinase inhibitor, FLT3 inhibitor` |
| NVP-BEZ235 | ATR | `ATR, MTOR, PIK3CA, PIK3CD, PIK3CG ; mTOR inhibitor, PI3K inhibitor` |
| SB-218078 | CHEK1 | `CHEK1 ; CHK inhibitor` |
| SNS-314 | AURKA, AURKB | `AURKA, AURKB, AURKC ; Aurora kinase inhibitor` |
| ZM-447439 | AURKA, AURKB | `AURKA, AURKB ; Aurora kinase inhibitor` |
| barasertib | AURKA, AURKB | `AURKA, AURKB ; Aurora kinase inhibitor` |
| barasertib-HQPA | AURKB | `AURKB ; Aurora kinase inhibitor` |
| birinapant | XIAP | `BIRC2, XIAP ; XIAP inhibitor` |
| litronesib | KIF11 | `KIF11 ; kinesin-like spindle protein inhibitor` |
| niraparib | PARP1 | `PARP1 ; PARP inhibitor` |
| olaparib | PARP1 | `PARP1, PARP2 ; PARP inhibitor` |
| tozasertib | AURKA, AURKB | `AURKA, AURKB, AURKC, LCK ; Aurora kinase inhibitor, Bcr-Abl kinase inhibitor, FLT3 inhibitor, JAK inhibitor` |

## 7. Robustness — what the enrichment does and does not survive

Every figure in this section is computed, not asserted. The closed-form test is used throughout; it agrees with the permutation test in the headline analysis.

### 7.1 Leave-one-class-out

Targets are grouped into **overlap-closed classes**: two targets share a class when some PRISM compound resolves to both, so a class is exactly the unit that can be removed without partially removing another target's compounds. Each row removes one class from the reference set and rescores.

| Class removed | Its tested / recovered | Reference left | Recovered left | p |
|---|---|---:|---:|---|
| *nothing removed* | — | 94 | 13 | **0.00988** |
| AURKA + AURKB + SRC | 40 / 7 | 54 | 6 | **0.164** |
| PARP1 | 7 / 2 | 87 | 11 | 0.0324 |
| CHEK1 | 10 / 1 | 84 | 12 | 0.0102 |
| XIAP | 5 / 1 | 89 | 12 | 0.016 |
| ATR | 4 / 1 | 90 | 12 | 0.0174 |
| KIF11 | 4 / 1 | 90 | 12 | 0.0174 |
| PLK1 | 7 / 0 | 87 | 13 | 0.00506 |
| AHR | 4 / 0 | 90 | 13 | 0.00681 |
| BCL2L1 | 4 / 0 | 90 | 13 | 0.00681 |
| CCNA2 | 2 / 0 | 92 | 13 | 0.00823 |
| CCNB1 | 2 / 0 | 92 | 13 | 0.00823 |
| EZH2 | 2 / 0 | 92 | 13 | 0.00823 |
| CSNK2A1 | 1 / 0 | 93 | 13 | 0.00902 |
| NUDT15 | 1 / 0 | 93 | 13 | 0.00902 |
| TTK | 1 / 0 | 93 | 13 | 0.00902 |

### 7.2 The result is carried by the Aurora kinase class

AURKA and AURKB are the same pharmacological intervention: 25 compounds resolve to the pair and 7 of the 13 recovered compounds are among them. Removing both leaves **6 of 69 recovered, p = 0.341** — chance.

Single leave-one-out hides this, because dropping AURKA leaves AURKB and almost all of the same compounds. **The defensible claim is therefore specific: RB1-loss lines are selectively sensitive to Aurora kinase inhibitors.** It is not broad recovery of RB1 biology across the nominated targets, and the supplement should not be written as though it were. No other class is load-bearing: removing any one of them leaves the enrichment significant.

### 7.3 Annotation noise is not driving it

Repeating the analysis using only PRISM's structured target field, discarding every match made through free-text mechanism annotation, gives **13 of 90 recovered, p = 0.00681**. No recovered compound depended on free-text matching.

### 7.4 The window threshold is not cherry-picked

| ΔpS′ threshold | Candidates | Recovered | p |
|---|---:|---:|---|
| ≤ −1 | 224 | 27 | 0.00141 |
| ≤ −1.5 | 136 | 19 | 0.0015 |
| **≤ −2** | 94 | 13 | **0.00988** |
| ≤ −2.5 | 56 | 11 | 0.00105 |
| ≤ −3 | 34 | 6 | 0.0257 |

The reported threshold is not the most favourable setting in this range, which is what an artifact of threshold choice would look like.

### 7.5 Multiple testing across the four genotypes

| Genotype | p | Bonferroni across 4 |
|---|---|---|
| PTEN | 0.942 | 1 |
| CDKN2A | 1 | 1 |
| RB1 | 0.00988 | 0.0395 |
| TP53 | 0.511 | 1 |

## 8. Draft manuscript text (drop-in for §3.7 / Supplement 7)

> To test whether the S′ selection window recovers established RB1 biology, a reference set of RB1-selective vulnerabilities was compiled from the published literature under **structural blinding**. In this blinded census assembly, four isolated AI agents, one per genotype, worked from stated inclusion criteria without access to the analysis repository and without sight of any S′, pS′ or ΔpS′ value; their output was transferred verbatim into the reference file, which was then frozen and checksum-verified before the benchmark was run. Of 94 PRISM compounds annotated to these literature-nominated targets and measured in the RB1 cohort (≥3 wildtype and ≥3 mutant lung lines), the window recovered 13 (14%; hypergeometric p = 0.00988, 10,000-permutation p = 0.0091; 13/106, p = 0.0258 in a sensitivity analysis retaining two inverse-direction entries). Recovered compounds fall into coherent mechanistic classes — Aurora kinase (AMG900, KW-2449, SNS-314, ZM-447439, barasertib, barasertib-HQPA, tozasertib); PARP1 (niraparib, olaparib); CHEK1 (SB-218078); XIAP (birinapant); ATR (NVP-BEZ235); KIF11 (litronesib) — while 81 annotated compounds were tested and not recovered. Recovery is therefore selective rather than indiscriminate. The enrichment is carried by the Aurora kinase class: removing AURKA and AURKB from the reference set leaves 6 of 69 recovered at p = 0.341, so the supported claim is the specific one, that RB1-deficient lines are selectively sensitive to Aurora kinase inhibitors, rather than a broad recovery of RB1 biology. No other target class is load-bearing. The reference set is pan-cancer, whereas recovery is measured in lung cell lines. This analysis establishes enrichment for literature-validated RB1 dependencies beyond chance; it does **not** estimate sensitivity, specificity or positive predictive value, and the same procedure applied to PTEN, CDKN2A and TP53 returned chance-level recovery. It is reported alongside the orthogonal genetic-dependency evidence in Supplement 8 (RNAi/CRISPR, RB–E2F axis), which is also RB1-anchored: the study's two independent lines of evidence converge on the same genotype.

## 9. What this analysis does not claim

1. **Not a sensitivity estimate.** The design cannot estimate sensitivity, specificity or positive predictive value. Recovery percentage is not accuracy.
2. **Pan-cancer reference, lung measurement.** The census draws on SCLC, breast/TNBC, prostate, hepatocellular, retinoblastoma, ovarian and bladder models; recovery is measured in lung lines. The census records why: *"Lung-specific primary evidence is scarce for PTEN and CDKN2A and moderate for RB1 and TP53. A lung-restricted census would have been too small to test; the pan-cancer scope is a deliberate and necessary choice, and a limitation to state."*
3. **Annotation noise.** Target → compound expansion relies on PRISM's own target/MOA annotations, which the referee review flagged as sometimes wrong (barasertib, for example, is mis-annotated). §6 shows the matched annotation text for every recovered compound so each call can be checked.
4. **The blinding is structural, not absolute.** The assembly step was initiated from within a results-aware project, so the guarantee does not rest on anyone's ignorance. It rests on two procedural facts. The four AI agents that built the rows worked in isolation, without repository access and without sight of any ΔpS′ value. Their output was transferred verbatim — no row added, removed, reworded or reordered — which removes any opportunity to shape the reference set after seeing how it would score. What a reviewer can verify directly is that the reference set has not changed since it was hashed; what structural blinding does not provide is an independent record of the conditions under which the rows were written. A fully independent replication would assemble the census before any results exist. (`BLIND_CENSUS_2026-08-31.md` states this same limitation in terms of the person who commissioned the census; the procedural statement here is the accurate one, and that document is left unedited as the record of the day.)
5. **The enrichment rests on one target class.** Removing the Aurora pair leaves 6 of 69 recovered at p = 0.341. The result supports a single specific dependency, not recovery of the genotype's biology in general. See §7.2.
6. **The freeze commit is retroactive.** The census was hashed and run on 2026-08-31 and committed on 2026-09-06. The hashes, not the commit date, are the evidence.
7. **Model-system annotation is post-hoc.** The *Model system* and *Census caveat* columns were added on 2026-09-06 from the cited primaries and the census assembly notes. They are presentation only and enter no computation.

## 10. Decisions for the authors (surfaced, not applied)

1. **PARP stays in.** An earlier analysis argued for excluding PARP1 from the RB1 reference set — no BioGRID RB1–PARP1 genetic interaction, disjoint STRING modules, older RB1–PARP literature tracing to co-deleted RNASEH2B/BRCA2. That was wrong. The blind census cites PMID 42618565, a 2026 isogenic hepatocellular screen showing biallelic RB1-inactivated cells are selectively PARP-sensitive, and olaparib and niraparib are 2 of the 13 recovered. Keep PARP, cite 42618565, drop the "context-dependent" footnote.
2. **Delete a fabricated citation.** Table 1 currently cites *"Jansen VM, Bhatt DL, Maniaci J, et al., Cancer Discov 2017"* on the AURKB row. No such paper exists. Oser 2019 (PMID 30373918) carries that row; Gong 2019 (PMID 30373917) is the real Aurora-A paper.
3. **De-claim TP53–KIF11** in Table 4 and the abstract. Present it as a novel internal finding of this dataset, explicitly **not** literature-validated.
4. **Retire the 75–94% recovery figures** in the abstract, §3.7 and §4, along with §4's "confirming the accuracy and biological specificity of the S′ index." Claim validation for RB1 only, paired with Supplement 8.
5. **Change the table title.** *"Literature-Corroborated Candidate Vulnerabilities Identified in Pharmacologic Screens"* describes the old direction; if it survives, the circularity objection stands in the heading itself.

## 11. Provenance and reproduction

| Item | Value |
|---|---|
| Census `reference_set_2026-08-31.csv` | 95 rows, md5 `a330987d6c02f9cb8826cc65e908301c` |
| Census `reference_set_2026-08-31_directional.csv` | 93 rows, md5 `76845dcc6131ab917717c7724da2c420` |
| Census freeze commit | `9ca5046` (retroactive — see §9.6) |
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
uv run --locked python concordance/build_suppl7_table1.py --genotype RB1
```

