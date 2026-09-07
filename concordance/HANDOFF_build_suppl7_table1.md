# Handoff → Claude Code (sprime-lung-repro): rebuild Supplement 7 Table 1 from the repo's own data

**Paul's blocker has two halves.** The mechanical half is "regenerate the table." The conceptual half —
his actual holdup — is *"the guiding picture is fuzzy."* §1 is the picture. Do not skip it: if the emitted
document does not make §1 legible to a reader, the rebuild has not solved the problem it exists to solve.

---

## 1. The picture (state this explicitly in the emitted document)

**The old Table 1 and the new one are different objects, not two versions of the same table.**

- **Old:** starts from the window's hits and finds a citation for each. It answers *"can I find literature
  for what I selected?"* The answer is always yes, so **it measures nothing.**
- **New:** starts from the literature, frozen before anyone looked at ΔpS′, and asks *"how many of those
  prior expectations does the window recover in the lung lines?"* — reported with the misses and a p-value
  against a random window of the same size.

**Keep two words separate, because the old table conflated them:**

| | Question | Answer here |
|---|---|---|
| **Verification** | Does every number regenerate byte-identically from the frozen census? | Yes — that is what the generator and its gates enforce. |
| **Validation** | Does recovery beat chance? | **RB1 only**, p ≈ 0.01. PTEN, CDKN2A and TP53 do not. |

A benchmark can be perfectly verified and still fail validation. Saying so plainly is the strongest
available position, and it is what the old table could not say in principle.

---

## 2. Step zero — two blockers before anything runs

**(a) The freeze step was never satisfied.** `PROTOCOL_literature_blind_concordance.md` Step 2 requires the
census be committed *before* the benchmark runs — that commit is the audit trail. **All six files are
currently untracked**, so the provenance block cannot cite a commit. Commit them first, unmodified:

```bash
git add concordance/reference_set_2026-08-31.csv \
        concordance/reference_set_2026-08-31_directional.csv \
        concordance/BLIND_CENSUS_2026-08-31.md \
        concordance/BLIND_CENSUS_NOTES_2026-08-31.md \
        concordance/results/2026-08-31_blind/concordance_report_primary_directional.csv \
        concordance/results/2026-08-31_blind/concordance_report_sensitivity_full.csv
git commit -m "concordance: freeze 2026-08-31 blind census and results (retroactive; see note)"
```
Verified md5s to cite in the provenance block:
`reference_set_2026-08-31.csv` = `a330987d6c02f9cb8826cc65e908301c` (95 rows);
`reference_set_2026-08-31_directional.csv` = `76845dcc6131ab917717c7724da2c420` (93 rows).
**Be honest in the commit message and the supplement that this freeze is retroactive** — the hashes and the
builders' notes are the audit trail, not the commit date.

**(b) The user-site interpreter is broken.** Bare `python3` fails to import `pandas` (numpy binary
mismatch in `%APPDATA%\Python\Python311\site-packages`). Do not repair it — sidestep it. The locked
environment works and is what CI uses: `uv sync --locked` builds `.venv` (verified 2026-09-06, Python
3.13.2, 12 packages), then run **every** step as `uv run --locked python <script>`. `run_all.py` shells out
to `sys.executable`, so its stages inherit the same interpreter. The §3 import
(`from concordance_enrichment import candidates, token_match`) was confirmed to resolve in that environment.

**(c) A required derived input is missing.** `results/lung_genotypes.csv` is present; **`results/sprime_lung_pairs.csv`
is not** (gitignored, ~18 MB). Regenerate from md5-verified sources: `python sprime_pipeline.py` (or `run_all.py`).

---

## 3. What to build

Create **`concordance/build_suppl7_table1.py`** — a generator, not a hand-written document. Every figure
must be derived from the frozen inputs at run time so it cannot drift. It must self-verify (§5) and exit
non-zero on any mismatch. Emit `concordance/SUPPL7_TABLE1_RB1.md`; support `--genotype` for the other three.

Inputs: the two census CSVs, the two blind-result CSVs, `BLIND_CENSUS_NOTES_2026-08-31.md`, plus
`results/sprime_lung_pairs.csv` + `results/lung_genotypes.csv`.

**Import the engine's window and resolution — do not re-implement them.** The SL window
(`DELTA_LE = -2.0`, `MIN_LINES = 3`, the two positivity checks) is single-sourced in `sprime_core.py`
(commit `9c8b9ce`), and `concordance_enrichment.py` already exposes the two functions the generator needs.
A local copy would be a fourth definition of the window, the only one outside the repo's control, and the
generator could silently drift from the run it reports on. `CLAUDE.md` forbids reintroducing a local `-2`
or `MINN = 3` in any consumer.

```python
import os, sys
here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, here)                                   # concordance/  → concordance_enrichment
sys.path.insert(0, os.path.dirname(here))                  # repo root     → _common, sprime_core
from concordance_enrichment import candidates, token_match  # window + target resolution, engine's own
# importing the engine also runs its scipy check (exit 4 if missing) and safe_stdout() — both wanted

pairs = pd.read_csv(pairs_csv).dropna(subset=["name"])
geno  = pd.read_csv(geno_csv).set_index("ModelID")
M = pairs.pivot_table(index="name", columns="depmap_id", values="sprime", aggfunc="mean")  # same pivot as every consumer
ann = (pairs.assign(txt=(pairs.get("target", "").fillna("") + " ; " + pairs.get("moa", "").fillna("")))
            .groupby("name").txt.apply(lambda s: " ; ".join(sorted(set(s)))).to_dict())

v  = geno[GENE]
wt = [c for c in M.columns if v.get(c) == 0]; mu = [c for c in M.columns if v.get(c) == 2]
universe, cand = candidates(M, wt, mu)                     # engine: MIN_LINES + passes_window

# per census row — mirror the engine's resolution loop exactly:
#   exact compound-name match (case-insensitive) OR token_match(target, ann[name]); both ∩ universe
for _, r in census[census.genotype == GENE].iterrows():
    comp = str(r.get("compound", "") or "").strip().lower()
    tgt  = str(r.get("target", "") or "").strip()
    hits = {nm for nm in universe if (comp and nm.lower() == comp) or (tgt and token_match(tgt, ann.get(nm, "")))}
    tested, recovered = hits, hits & cand
    # keep ann[nm] for each recovered compound — the emitted table shows the matched annotation text
```

The `ann` dict and pivot are copied from the engine's `main()` because they are not exposed as
functions; if the engine is refactored to expose them, import those too. **Never** redefine `MIN_LINES`,
`DELTA_LE`, or the window test locally.

**Targets overlap** (pan-Aurora compounds match both AURKA and AURKB). Per-target counts must **not** be
summed; report the **union** as the headline with a footnote saying so.

---

## 4. Five content requirements the previous draft missed

1. **The title must change.** *"Literature-Corroborated Candidate Vulnerabilities Identified in
   Pharmacologic Screens for RB1-Deficient Lung Cancer Cell Lines"* describes the **old** direction — if it
   survives, the circularity objection stands in the heading. Emit something like:
   **"Literature-nominated RB1 vulnerabilities and their recovery by the S′ window."**
2. **"Lung" in the title vs a pan-cancer census.** The RB1 reference rows are SCLC, breast/TNBC, prostate,
   hepatocellular, retinoblastoma, HGSC and bladder — not lung. Add a **tissue column** and one sentence:
   *the reference set is pan-cancer; recovery is measured in lung cell lines.* Quote the builders' own note:
   > "Lung-specific primary evidence is scarce for PTEN and CDKN2A and moderate for RB1 and TP53. A
   > lung-restricted census would have been too small to test; the pan-cancer scope is a deliberate…"
   Do **not** edit the frozen census to add the column — emit tissue from a small committed mapping file
   (or parse `inclusion_rationale`), and label it post-hoc annotation.
3. **Say "AI agents," not "curators."** The draft manuscript text called the builders *"four independent
   curators."* They were **four isolated AI agents**, one per genotype. The paper must say so plainly, and
   the census's own stated limitation — *the person commissioning the census had already seen the ΔpS′
   results, so the blind rests on builder isolation and verbatim assembly, not on the commissioner's
   ignorance* — belongs in the supplement. A reviewer who opens this repo will find both.
4. **Carry the annotation-noise caveat.** `concordance/README.md` warns PRISM target/MOA annotations are
   sometimes wrong (e.g. barasertib mis-annotated), and target→compound expansion depends on them. The
   emitted doc must carry that caveat **and** state that **14% recovery is not a sensitivity estimate** —
   the design cannot estimate sensitivity, specificity or PPV.
5. **AURKA has two census rows with different PMIDs** (`30373917`, LY3295668 panel; and `34741392`,
   retinoblastoma, doi 10.1002/kjm2.12469). The generator must carry **all** PMIDs/DOIs per target, not the
   first one.

---

## 5. Acceptance gates (fail the build on mismatch)

From `concordance_report_primary_directional.csv`:

| gene | ref_in_universe | candidates | universe | recovered | hypergeometric p | permutation p |
|---|---:|---:|---:|---:|---|---|
| RB1 | 94 | 94 | 1360 | 13 | 0.00987648640793 | 0.00909909009099 |
| PTEN | 39 | 97 | 883 | 2 | 0.94180453779 | 0.937306269373 |
| CDKN2A | 12 | 48 | 1402 | 0 | 1 | 1 |
| TP53 | 61 | 16 | 1402 | 1 | 0.511135535274 | 0.521847815218 |

Sensitivity (full 95-row census): RB1 13/106 = 12%, hypergeometric 0.0258, permutation 0.0245.

RB1 union **must** equal 94 tested / 13 recovered. The 13: `AMG900, KW-2449, NVP-BEZ235, SB-218078,
SNS-314, ZM-447439, barasertib, barasertib-HQPA, birinapant, litronesib, niraparib, olaparib, tozasertib`.

Per-target expansion independently reproduced 2026-09-06 — assert against it:

| target | PMID(s) | tested | recovered |
|---|---|---:|---:|
| AURKB | 30373918 | 20 | 7 |
| AURKA | 30373917, **34741392** | 22 | 6 |
| SRC | 33334906 | 16 | 0 |
| CHEK1 | 29386107 | 10 | 1 |
| PARP1 | 42618565 | 7 | 2 |
| PLK1 | 29386107 | 7 | 0 |
| XIAP | 41285729 | 5 | 1 |
| ATR | 41442499 | 4 | 1 |
| KIF11 | 42618565 | 4 | 1 |
| BCL2L1 | 40436896 | 4 | 0 |
| AHR | 40276038 | 4 | 0 |
| EZH2 / CCNA2 / CCNB1 | 28059767 / 40836083 / 40836083 | 2 each | 0 |
| TTK / CSNK2A1 / NUDT15 | 36070391 / 38781347 / 40904703 | 1 each | 0 |
| SKP2 / GPX4 / PKMYT1 | 32265224 / 36928314 / 41442499 | 0 | — absent from PRISM 19Q4 |

Targets resolving to **0 compounds** must be shown explicitly as *"no compound in PRISM 19Q4"* — a dataset
boundary, not a miss. If regenerating `sprime_lung_pairs.csv` shifts any value, **stop and report the
delta** rather than publishing new numbers.

---

## 6. Emitted document structure

1. §1's picture (old vs new object; verification vs validation) — in plain language.
2. Headline table: tested / recovered / recovery % / both p-values / sensitivity row.
3. Table 1 proper: per-target rows with **all PMIDs**, **tissue**, tested, recovered, recovered names;
   sorted recovered-desc then tested-desc; zero-resolution targets listed as a dataset boundary.
4. Full miss list (81 for RB1) from the results `misses` column, plus **computed** within-class recovery
   (Aurora n/N, PLK1 0/7, SRC 0/16) — compute, don't assert.
5. Draft manuscript paragraph with figures interpolated, saying "AI agents," carrying the pan-cancer
   sentence, the annotation-noise caveat, and "not a sensitivity estimate."
6. Author decisions (§7) as open items.
7. Provenance: census filenames + md5s + **the freeze commit**, engine invocation, `--perm 10000`,
   seed 20260811, data checksums, and the retroactive-freeze note.

---

## 7. Author decisions to surface, not apply

1. **PARP stays in.** An earlier Cowork analysis argued to exclude PARP1 from RB1 (no BioGRID RB1–PARP1
   genetic interaction; disjoint STRING modules; older RB1–PARP literature tracing to co-deleted
   RNASEH2B/BRCA2). **That was wrong** — the census cites **PMID 42618565**, a 2026 isogenic hepatocellular
   screen showing biallelic RB1-inactivated cells are selectively PARP-sensitive; olaparib and niraparib are
   2 of the 13 recovered. Keep PARP, cite it, drop the "context-dependent" footnote.
2. **Delete a fabricated citation.** Table 1 cites *"Jansen VM, Bhatt DL, Maniaci J, et al., Cancer Discov
   2017"* on the AURKB row. **No such paper exists.** Oser 2019 (30373918) carries that row; Gong 2019
   (30373917) is the real Aurora-A paper. See `cowork-ws/lung-paper/REFCHECK_Suppl7_Suppl9.md`.
3. **De-claim TP53–KIF11** (Table 4 / abstract). Blind TP53 recovery is 1/61, p = 0.51; the earlier
   p = 5.6e-8 was an artifact of a 5-row reference dominated by the KIF11/Eg5 family. Present it as a novel
   internal finding, **not** literature-validated.
4. **Retire the 75–94% figures** and §4's "confirming the accuracy and biological specificity of the S′
   index." Claim validation for **RB1 only**; pair with Supplement 8 (RNAi/CRISPR, RB–E2F), also RB1-anchored.

---

## 8. Repo-copy warning
The 08-31 census exists **only here** (`codex/sprime-lung-repro`). The copy at
`cowork-ws/lung-paper/sprime-lung-repro` holds a separate, smaller **2026-09-02** rebuild (11-row reference,
RB1 8/42, p ≈ 0.006) that this work **supersedes** — do not merge its numbers. Its
`WALKTHROUGH_RB1_concordance_rebuild.md` is still useful, but only as the conceptual explainer.

## 9. Definition of done
- [ ] Six census/result files committed (freeze satisfied, retroactivity disclosed); md5s recorded.
- [ ] pandas/numpy repaired; `results/sprime_lung_pairs.csv` regenerated.
- [ ] `build_suppl7_table1.py` deterministic and self-verifying against §5.
- [ ] Window and resolution **imported** from `concordance_enrichment` (`candidates`, `token_match`); no local `-2`, `MINN`, or window test anywhere in the generator (`grep -n "MINN\|<= -2\|MIN_LINES *=" concordance/build_suppl7_table1.py` returns nothing).
- [ ] `SUPPL7_TABLE1_RB1.md` emitted; every figure traceable to a frozen input.
- [ ] Title changed; tissue column present; pan-cancer sentence included.
- [ ] "AI agents" stated; commissioner limitation carried into the supplement.
- [ ] Annotation-noise caveat and "not a sensitivity estimate" present.
- [ ] All PMIDs per target (AURKA shows both).
- [ ] Misses listed in full; within-class recovery computed.
- [ ] §7 decisions surfaced as open items, not applied.
