# Census assembly notes — second blinded census, 2026-09-06

Provenance companion to `reference_set_2026-09-06.csv` and its directional primary variant. Assembled
under `PRESPEC_second_census_2026-09-06.md`, which was written and committed **before** this census
existed and fixes the decision rule for comparing it against the 2026-08-31 census.

Four agents, one per genotype, each in its own context with PubMed plus ChEMBL / Open Targets /
BioGRID-ORCS for druggability confirmation, instructed to read no repository file, to consult no
S′/pS′/ΔpS′ value, and not to seek out the manuscript. Their output was assembled verbatim by
`assemble_census.py`, which applies exactly two transformations: concatenation in a fixed genotype
order, and the directional split on the agents' own `INVERSE-DIRECTION` flag.

| genotype | rows returned | inverse-direction | in primary census |
|---|---:|---:|---:|
| PTEN | 42 | 4 | 38 |
| CDKN2A | 26 | 1 | 25 |
| RB1 | 30 | 3 | 27 |
| TP53 | 23 | 3 | 20 |
| **total** | **121** | **11** | **110** |

Frozen hashes: `reference_set_2026-09-06.csv` = `45c5b69f467092a8370cf5672d36be0f` (121 rows);
`reference_set_2026-09-06_directional.csv` = `2d57e870e07fe5a3a6cde0aa894ccd4a` (110 rows).

---

## Formatting repairs made during transcription — disclosed, not silent

Two defects were repaired between the agents' emitted text and the staged files. Neither changes any
field's meaning, and both are recorded here because the verbatim rule is worth more than a clean story.

1. **A broken CSV quoting in the CDKN2A GART row.** The compound name contains a comma and its field
   was emitted with mismatched quotes, so the line did not parse. The quoting was repaired to
   `"5,10-dideazatetrahydrofolate"`. No character of the name was changed.
2. **Two HTML entities.** `&gt;` and `&lt;` appeared inside two `inclusion_rationale` fields (the CDKN2A
   MRTX1719 row and the PTEN AZD8186 row) as an artifact of the transport encoding. They were converted
   to `>` and `<`.

No row was added, removed, reworded or reordered.

## What the blinding here does and does not cover

Identical in kind to the 2026-08-31 census, and stated again because it is the load-bearing limitation:
the assembly step was **initiated from a results-aware context**, and agent isolation is enforced by
instruction rather than by a sandbox. This exercise measures whether the benchmark's result is a property
of the literature or of one pass through it. It is not an independent replication and must not be
reported as one.

---

## PTEN — 42 rows, 4 inverse-direction

**Excluded:** reviews (37533462, 41383404, 40278910, 34050264 and others); computational predictions with
no wet validation (37120674, 39009815, 39305483, 38076921, 41046457, 20124458); targets with no inhibitor,
so failing the druggability criterion — WDHD1 (33221821), ARID4B (31551414), PAX7 (34535684), NLK
(23144700); wrong genotype anchor — ATAD1 (36409067, a 10q23 collateral co-deletion rather than PTEN
itself), MTAP/9p21 papers, CDK12/CDK13, and 37163614 which requires combined PTEN and TP53 deficiency;
single-arm clinical studies with no wildtype comparator (28281183, 23810788).

> **The PTEN → homologous-recombination → PARP axis is genuinely contested, with primaries on both
> sides.** For: 20049735, 20530668, 29500400, 24625059. Against: 33138032 could not reproduce
> PTEN-dependent RAD51 function, 27375368 shows PARG depletion is not synthetic lethal with PTEN loss,
> and 29500400 itself reports no association between PTEN status and RAD51 across 1500 prostate tumours,
> partially undercutting the mechanism it supports. Two PARP1 rows are included. A scorer may
> legitimately down-weight them.

**Thin or caveated:** ACLY and SQLE rest on genetic ablation rather than a named selective compound; LOX
is a microenvironment mechanism that will not reproduce in monoculture; RAD51 uses a cell-penetrating
antibody rather than a small molecule; IMPDH2 is a PubMed-indexed preprint and the paper says "IMPDH"
without resolving the isoform; PSMB5 is a stand-in symbol for the 20S proteasome; SMARCA4 has only
tool-grade chemistry.

> **A gene-symbol trap the agent flagged explicitly:** the PDK1 row means pyruvate dehydrogenase kinase 1
> (HGNC PDK1), not 3-phosphoinositide-dependent kinase 1 (PDPK1). Reading it as PDPK1 gives the wrong gene.

**Coverage gap — lung.** The lung-specific PTEN evidence is small and mostly combination therapy rather
than monotherapy. Prostate, breast, glioblastoma and colorectal dominate.

## CDKN2A — 26 rows, 1 inverse-direction

Both arms covered deliberately: the cell-cycle arm (CDK4/6) and the 9p21 metabolic arm (MTAP co-deletion
→ MAT2A/PRMT5), plus 9p21 passenger collateral lethality via ACO1.

**Excluded:** reviews and commentaries; single-arm studies in which every model carries the deletion, so
there is no comparator (26183925 chordoma, 28704762 mesothelioma, 39293516 AMG 193 first-in-human, the
L-alanosine phase II literature); combination-context screens where the comparison is drug-versus-drug
inside deleted cells rather than deleted-versus-intact (40694540, 40694535).

> **RIOK1 was deliberately not included.** 27068473 proposed it, but 29983885 is an explicit negative:
> RIOK1 kinase activity was required irrespective of MTAP status in analog-sensitive isogenic pairs. The
> agent chose to omit rather than include a contested row. The 2026-08-31 census made the opposite call
> and included RIOK1 with a contested flag — a real curatorial disagreement between the two passes.
> **41120713** is a second explicit negative: PRMT5i/PARPi synergy independent of MTAP status.
> **41101730** (HBS1L/PELO under FOCAD loss) was excluded solely because no inhibitor exists; it belongs
> the moment a tool compound appears.

**Thin or caveated:** the three ADSS2/DHFR/GART rows all come from one 1996 transfection-based isogenic
A549 pair, using historical and clinically discontinued agents, and methotrexate is close to a
general-sensitivity agent. ADSS2 as the symbol for the L-alanosine target is the agent's mapping, not the
papers' — treat those rows as pathway-level. The CDK4-versus-CDK6 split is artificial, since every agent
here is a dual CDK4/6 inhibitor and no paper separates the two kinases pharmacologically.

> **A caveat against the whole metabolic arm:** 34244484 reports that primary MTAP-deleted glioblastomas
> do not accumulate MTA in vivo, because MTAP-expressing stroma consumes it. Every MTAP/PRMT5/MAT2A row
> depends on intratumoural MTA elevation, so the in-vitro-to-patient extrapolation is contested for at
> least one tissue.

**Coverage gap — lung, again.** Only the 1996 A549 isogenic MTAP pair and the inverse-direction EGFR row
are lung. There is no CDKN2A-versus-intact CDK4/6-inhibitor row in NSCLC at all.

**Structural warning the agent raised:** everything in the metabolic arm is stratified by MTAP, not by
CDKN2A. A genotype call taken from a mutation matrix alone will systematically mislabel CDKN2A point
mutants, and MTAP-deleted, CDKN2A-intact cases would be false positives.

## RB1 — 30 rows, 3 inverse-direction

**Excluded:** reviews and genomic-landscape papers; studies where RB1 loss is a constant background rather
than the varied axis (30688657, 33334906, 29760044, 40504161, 37773632); non-cancer or non-druggable
endpoints — MED4 (24858910) is a genuine RB1-null survival gene with no inhibitor; Drosophila and mouse
embryogenesis papers.

> **A machine-curation trap worth recording:** the string "Rb1" retrieves ginsenoside Rb1 papers
> (34124194, 30439402). Any automated query on this genotype needs a filter for it.
> A duplicate was also caught: 37502925 is the preprint of 38480701, and only the journal version is in
> the census, so they cannot be counted as two citations.

**Thin or caveated:** AHR is prediction-first and the authors call the effect indirect; NUDT15 is
collateral lethality from 13q14 co-deletion rather than RB1 synthetic lethality, and mercaptopurine is not
a NUDT15 inhibitor; the PARP1 and ATR rows from 32460015 use combined TP53 plus RB1 loss, so the
RB1-specific contribution is not isolated; CD276 has no isogenic RB1 manipulation; the AURKA row from
39918479 requires MYCN amplification as well as RB1 loss; the AURKB row from 30373917 rests on a
target-class statement rather than a dedicated validation arm, unlike 30373918.

**Belongs but not evidenceable:** mitochondrial translation via tigecycline (27571409) is strong,
genotype-comparative primary evidence, but the mitoribosome does not resolve to a single HGNC symbol;
SUCLA2 (32694611) has the same collateral-lethality caveat as NUDT15; the spliceosome paper (35412907)
names no gene or compound; cyclin A/B RxL macrocycles (40810865) lost their gene symbols in the indexed
abstract. **WEE1 has no qualifying row** — no clean RB1-genotype-comparative WEE1 paper was found.

**Coverage gap — lung, severely.** Breast and prostate dominate. SCLC, the canonical RB1-null disease,
has two rows; NSCLC has exactly one (33037191, the RB1-isogenic lung pair). Most rows are cross-tissue
extrapolations.

**Compound-level thinness:** 12 of 30 rows have no named inhibitor because the abstracts name only target
classes. The agent left those fields empty rather than guessing, which is the correct call and also means
the census under-resolves at the compound level relative to what full-text curation would give.

## TP53 — 23 rows, 3 inverse-direction

**Excluded:** papers whose own conclusion is that the effect is p53-independent (26975930 for WEE1;
27515963 for AURKB, "irrespective of p53 status"); computational-only (23629686 for PLK1); reviews;
trials enrolling only TP53-mutant patients, so lacking the wildtype comparator (34538072, 32611648);
32522823-style designs where the primary genetic axis is another gene.

> **Explicit negative report on mitotic and spindle-assembly targets.** The agent ran dedicated searches
> for PLK1, AURKA, AURKB, TTK/MPS1, KIF11/Eg5 and BUB1/CENPE and **could not evidence any of them to
> criterion**. What came back was p53-independent by the authors' own conclusion, computational,
> review-level, driven by a different genotype, or lacking a wildtype comparator. Zero mitotic rows is
> stated as a deliberate finding, not a gap in searching.
>
> **Assembler's note, not blind:** this independently reproduces the same explicit negative recorded by a
> different agent in the 2026-08-31 census. Two separate passes at the literature, run six days apart,
> both failed to find genotype-comparative TP53 evidence for KIF11.

**Contested:** the CHEK1 rows rest on chemo-combination designs rather than single-agent lethality, and
CBP-93872 suppresses CHK1 phosphorylation without inhibiting the kinase in cell-free assays, so its target
assignment is pathway-level. 21289082 is a direct counterweight to the CHK1 axis. The two statin papers
disagree about which allele is sensitive, though both agree the effect is allele-specific rather than a
general TP53-mutant effect.

> **A design choice worth stating:** the mutant-p53 reactivator rows (APR-246, arsenic trioxide, ZMC1)
> are mutant-selective in a different sense from the checkpoint rows. They act *on* the mutant protein
> rather than exploiting a dependency created by its loss. Mixing them with loss-of-function synthetic
> lethality in one reference set is defensible but is a choice, not a neutral fact.

**Belongs but not evidenceable:** ATM, PARP1, CDK9, BRD4, XPO1, NAMPT, CDC7 and MELK were all searched
and none returned a genotype-comparative TP53 design. HDAC6 appears only inside a combination.

**Skews:** 11 of 20 primary-direction rows are G2/M checkpoint or DNA-damage-response targets. That is a
real property of the literature, but a benchmark built on it rewards DNA-damage-response-adjacent
compounds regardless of whether they are genuinely TP53-selective. Several rows are allele-specific; a
benchmark that collapses all damaging TP53 mutations into one class will mis-score them in both
directions.

**Inverse direction:** MDM2 and MDMX antagonists are the largest and best-evidenced class in this space
and all of them belong on the wildtype side. If a candidate list scores MDM2 antagonists as TP53-mutant
hits, that is a false positive rather than a recovery.

---

## Cross-cutting

1. **Lung is thin in all four genotypes**, and both censuses now say so independently. The pan-cancer
   scope is a necessary choice given the literature, and a limitation to state whenever recovery measured
   in lung lines is presented.
2. **Two genotypes are stratified by something other than the named gene.** The CDKN2A metabolic arm is
   really MTAP, and several RB1 and CDKN2A rows are 9p21 or 13q14 collateral lethality. A genotype call
   read from a damaging-mutation matrix cannot represent either.
3. **The two censuses disagree on curatorial calls, not only on coverage** — RIOK1 is included with a
   contested flag in one and deliberately omitted in the other. That kind of disagreement is exactly what
   the agreement measures are meant to quantify.
4. All PMIDs and DOIs were retrieved live from PubMed during assembly; none was written from memory.
   According to PubMed.
