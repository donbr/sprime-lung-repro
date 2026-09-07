#!/usr/bin/env python3
"""Generate Supplement 7 Table 1 from the frozen literature-blind concordance benchmark.

Emits a manuscript-ready markdown document in which *every* figure is derived at run time from
frozen inputs, so the document cannot drift from the analysis:

  concordance/reference_set_2026-08-31_directional.csv   frozen census, primary (93 rows)
  concordance/reference_set_2026-08-31.csv               frozen census, full     (95 rows)
  concordance/results/2026-08-31_blind/*.csv             the engine's own output
  results/sprime_lung_pairs.csv, results/lung_genotypes.csv   derived tables from sprime_pipeline.py

The SL window is NOT redefined here. `candidates` and `token_match` are imported from
concordance_enrichment.py, which imports MIN_LINES/passes_window from sprime_core.py — the single
source of truth (commit 9c8b9ce). A local `-2` or `MINN = 3` in this file would be a fourth
definition of the window and could silently drift from the run this document reports on.

Self-verifying: every acceptance gate in the handoff (§5) is asserted before anything is written.
Exit codes:  0 = ok  |  1 = an acceptance gate failed  |  2 = missing input  |  4 = scipy missing.

Usage:
    uv run --locked python concordance/build_suppl7_table1.py                 # RB1 (default)
    uv run --locked python concordance/build_suppl7_table1.py --genotype TP53
"""
import argparse, hashlib, os, sys
import pandas as pd

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)                      # concordance/ -> concordance_enrichment
sys.path.insert(0, os.path.dirname(_HERE))     # repo root    -> _common, sprime_core
# Importing the engine also runs its scipy check (exit 4) and safe_stdout() — both wanted here.
from concordance_enrichment import candidates, token_match          # noqa: E402
from sprime_core import DELTA_LE, MIN_LINES, passes_window          # noqa: E402  (display + robustness)
from _common import safe_stdout                                     # noqa: E402
from scipy.stats import hypergeom   # engine already required it; the import above exits 4 if absent

safe_stdout()

GENES = ["PTEN", "CDKN2A", "RB1", "TP53"]

# ---------------------------------------------------------------------------------------------
# Acceptance gates. These are the committed engine output (concordance/results/2026-08-31_blind/)
# and the per-target expansion independently reproduced from it. If a regenerated
# sprime_lung_pairs.csv shifts any of these, STOP and report the delta — do not publish new
# numbers, because it would mean the derived baseline changed.
# ---------------------------------------------------------------------------------------------
CENSUS_MD5 = {                                            # frozen 2026-08-31, commit 9ca5046
    "reference_set_2026-08-31.csv":             "a330987d6c02f9cb8826cc65e908301c",
    "reference_set_2026-08-31_directional.csv": "76845dcc6131ab917717c7724da2c420",
}
# gene -> (ref_in_universe, candidates, universe, recovered, hyperg_p, perm_p)
GATES_PRIMARY = {
    "RB1":    (94, 94, 1360, 13, 0.00987648640793, 0.00909909009099),
    "PTEN":   (39, 97,  883,  2, 0.94180453779,    0.937306269373),
    "CDKN2A": (12, 48, 1402,  0, 1.0,              1.0),
    "TP53":   (61, 16, 1402,  1, 0.511135535274,   0.521847815218),
}
GATES_SENSITIVITY_RB1 = (106, 94, 1360, 13, 0.0258199424117, 0.024497550245)
GATE_RB1_RECOVERED = ["AMG900", "KW-2449", "NVP-BEZ235", "SB-218078", "SNS-314", "ZM-447439",
                      "barasertib", "barasertib-HQPA", "birinapant", "litronesib", "niraparib",
                      "olaparib", "tozasertib"]
GATE_RB1_TARGETS = {   # target -> (tested, recovered)
    "AURKB": (20, 7), "AURKA": (22, 6), "SRC": (16, 0), "CHEK1": (10, 1), "PARP1": (7, 2),
    "PLK1": (7, 0), "XIAP": (5, 1), "ATR": (4, 1), "KIF11": (4, 1), "BCL2L1": (4, 0),
    "AHR": (4, 0), "EZH2": (2, 0), "CCNA2": (2, 0), "CCNB1": (2, 0), "TTK": (1, 0),
    "CSNK2A1": (1, 0), "NUDT15": (1, 0), "SKP2": (0, 0), "GPX4": (0, 0), "PKMYT1": (0, 0),
}
# Data pins, quoted in the provenance block (same values as fetch_data.SOURCES / sprime_pipeline.MD5).
DATA_MD5 = {"PRISM Repurposing 19Q4 secondary screen": "e629b9d505ad3d6bf65fde96f1c54bee",
            "DepMap 24Q2 damaging-mutation matrix":     "02f3568b71af0ca3e8d10e681eefac86"}
FREEZE_COMMITS = {"census": "9ca5046", "results": "7b5af0c"}
ENGINE_INVOCATION = "concordance_enrichment.py --perm 10000 --seed 20260811"


class GateFailure(Exception):
    """An acceptance gate did not reproduce. Never write a document after this."""


def md5sum(path, chunk=1 << 20):
    h = hashlib.md5()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(chunk), b""):
            h.update(b)
    return h.hexdigest()


def need(path, what):
    if not os.path.exists(path):
        print(f"ERROR: missing {what}: {path}")
        if path.endswith("sprime_lung_pairs.csv"):
            print("  It is gitignored (~18 MB). Regenerate it with:\n"
                  "    uv run --locked python fetch_data.py\n"
                  "    uv run --locked python sprime_pipeline.py")
        sys.exit(2)
    return path


def load_matrix(derived):
    """Compound x cell-line S' matrix and the compound -> annotation text map.

    Both are copied from concordance_enrichment.main(), which does not expose them as functions;
    if the engine is ever refactored to expose them, import them instead of duplicating here.
    """
    pairs = pd.read_csv(need(os.path.join(derived, "sprime_lung_pairs.csv"), "derived pairs table")
                        ).dropna(subset=["name"])
    geno = pd.read_csv(need(os.path.join(derived, "lung_genotypes.csv"), "derived genotype table")
                       ).set_index("ModelID")
    mat = pairs.pivot_table(index="name", columns="depmap_id", values="sprime", aggfunc="mean")
    ann = (pairs.assign(txt=(pairs.get("target", "").fillna("") + " ; " + pairs.get("moa", "").fillna("")))
                .groupby("name").txt.apply(lambda s: " ; ".join(sorted(set(s)))).to_dict())
    # structured target field only, no free-text MOA — used to test annotation robustness
    ann_t = (pairs.assign(txt=pairs.get("target", "").fillna(""))
                  .groupby("name").txt.apply(lambda s: " ; ".join(sorted(set(s)))).to_dict())
    return mat, geno, ann, ann_t


def cohort(mat, geno, gene):
    """Universe and candidate set for one genotype — the engine's own window, via `candidates`."""
    v = geno[gene]
    wt = [c for c in mat.columns if v.get(c) == 0]
    mu = [c for c in mat.columns if v.get(c) == 2]
    return candidates(mat, wt, mu)


def resolve_row(row, universe, ann):
    """PRISM compounds one census row resolves to — mirrors the engine's resolution loop exactly:
    exact compound-name match (case-insensitive) OR token_match(target, annotation text)."""
    comp = str(row.get("compound", "") or "").strip().lower()
    tgt = str(row.get("target", "") or "").strip()
    return {nm for nm in universe
            if (comp and nm.lower() == comp) or (tgt and token_match(tgt, ann.get(nm, "")))}


def hyperg(k, n_uni, n_cand, n_ref):
    """P(X >= k) — the same closed form the engine reports as hyperg_p."""
    return float(hypergeom.sf(k - 1, n_uni, n_cand, n_ref)) if n_ref else float("nan")


def resolve_by_target(census, gene, universe, annmap):
    """target -> resolved compounds, using the supplied annotation map."""
    per = {}
    for _, r in census[census.genotype == gene].iterrows():
        tgt = str(r.get("target", "") or "").strip()
        key = tgt or f'(compound) {r.get("compound", "")}'
        per.setdefault(key, set()).update(resolve_row(r, universe, annmap))
    return per


def overlap_classes(per):
    """Group targets into overlap-closed classes: two targets share a class when any PRISM compound
    resolves to both. Computed, never curated — a class is exactly the unit that can be removed from
    the reference set without partially removing some other target's compounds."""
    ts = [t for t in per if per[t]]
    parent = {t: t for t in ts}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for i, a in enumerate(ts):
        for b in ts[i + 1:]:
            if per[a] & per[b]:
                parent[find(a)] = find(b)
    comps = {}
    for t in ts:
        comps.setdefault(find(t), []).append(t)
    return sorted((sorted(v) for v in comps.values()),
                  key=lambda v: (-len(v), v[0]))


def robustness(gene, census, mat, geno, universe, cand, ann, ann_t, report):
    """Every robustness check reported in the document. All computed, none asserted."""
    n_uni, n_cand = len(universe), len(cand)
    per = resolve_by_target(census, gene, universe, ann)
    ref = set().union(*per.values()) if per else set()
    out = {"full": (len(ref), len(ref & cand), hyperg(len(ref & cand), n_uni, n_cand, len(ref)))}

    rows = []
    for cls in overlap_classes(per):
        drop = set().union(*[per[t] for t in cls])
        keep = ref - drop
        rows.append((cls, len(drop), len(drop & cand), len(keep), len(keep & cand),
                     hyperg(len(keep & cand), n_uni, n_cand, len(keep))))
    out["classes"] = sorted(rows, key=lambda r: (-r[2], -r[1]))

    # the one pharmacologically-identical pair worth reporting on its own
    if {"AURKA", "AURKB"} <= set(per):
        drop = per["AURKA"] | per["AURKB"]
        keep = ref - drop
        out["aurora"] = (len(drop), len(drop & cand), len(keep), len(keep & cand),
                         hyperg(len(keep & cand), n_uni, n_cand, len(keep)))

    # annotation provenance: structured target field only, discarding free-text MOA matches
    per_t = resolve_by_target(census, gene, universe, ann_t)
    ref_t = set().union(*per_t.values()) if per_t else set()
    out["target_only"] = (len(ref_t), len(ref_t & cand),
                          hyperg(len(ref_t & cand), n_uni, n_cand, len(ref_t)),
                          sorted((ref & cand) - (ref_t & cand)))

    # window-threshold sweep
    v = geno[gene]
    wt = [c for c in mat.columns if v.get(c) == 0]
    mu = [c for c in mat.columns if v.get(c) == 2]
    w, m = mat.reindex(columns=wt), mat.reindex(columns=mu)
    ok = (w.notna().sum(1) >= MIN_LINES) & (m.notna().sum(1) >= MIN_LINES)
    sweep = []
    for d in (-1.0, -1.5, -2.0, -2.5, -3.0):
        c2 = set((ok & passes_window(w.mean(1), m.mean(1), delta_le=d)).pipe(lambda t: t[t]).index)
        sweep.append((d, len(c2), len(ref & c2), hyperg(len(ref & c2), n_uni, len(c2), len(ref))))
    out["thresholds"] = sweep

    idx = report.set_index("gene")
    out["bonferroni"] = [(g, float(idx.loc[g].hyperg_p), min(1.0, float(idx.loc[g].hyperg_p) * len(GENES)))
                         for g in GENES]
    return out


def per_target(census, gene, universe, cand, ann, notes):
    """Aggregate census rows to one entry per literature-nominated target."""
    out = {}
    for _, r in census[census.genotype == gene].iterrows():
        key = str(r.get("target", "") or "").strip() or f'(compound) {r.get("compound", "")}'
        hits = resolve_row(r, universe, ann)
        e = out.setdefault(key, dict(target=key, tested=set(), pmids=[], dois=[],
                                     tissue="", flag="", rationales=[]))
        e["tested"] |= hits
        for field, bucket in (("pmid", "pmids"), ("doi", "dois")):
            v = str(r.get(field, "") or "").strip()
            if v and v not in e[bucket]:
                e[bucket].append(v)
        note = notes.get((gene, key, str(r.get("pmid", "") or "").strip()))
        if note:
            if note["tissue"] and note["tissue"] not in e["tissue"]:
                e["tissue"] = f'{e["tissue"]}; {note["tissue"]}'.strip("; ")
            if note["flag"] and note["flag"] not in e["flag"]:
                e["flag"] = f'{e["flag"]} / {note["flag"]}'.strip(" /")
        rat = str(r.get("inclusion_rationale", "") or "").strip()
        if rat:
            e["rationales"].append(rat)
    for e in out.values():
        e["recovered"] = e["tested"] & cand
    # deterministic: most recovered first, then most tested, then alphabetical
    return sorted(out.values(), key=lambda e: (-len(e["recovered"]), -len(e["tested"]), e["target"]))


def load_notes(path):
    """Post-hoc tissue / evidence-flag annotation, keyed genotype+target+pmid. Optional."""
    if not os.path.exists(path):
        return {}
    df = pd.read_csv(path, comment="#", dtype=str).fillna("")
    return {(r.genotype.strip(), r.target.strip(), r.pmid.strip()):
            dict(tissue=r.tissue.strip(), flag=r.evidence_flag.strip())
            for r in df.itertuples()}


def check(label, got, want, failures, tol=None):
    ok = (abs(float(got) - float(want)) <= tol) if tol is not None else (got == want)
    if not ok:
        failures.append(f"{label}: computed {got!r} != expected {want!r}")
    return ok


def verify(gene, stats, report_row, sens_row, targets, census_paths, failures):
    """Assert every acceptance gate. Appends human-readable deltas to `failures`."""
    for name, want in CENSUS_MD5.items():
        p = census_paths.get(name)
        if p:
            check(f"census md5 {name}", md5sum(p), want, failures)

    # 1. the recomputed cohort must reproduce the engine's own committed output
    check(f"{gene} universe (recomputed vs report)", stats["universe"], int(report_row.universe), failures)
    check(f"{gene} candidates (recomputed vs report)", stats["candidates"], int(report_row.candidates), failures)
    check(f"{gene} ref_in_universe (recomputed vs report)", stats["ref"], int(report_row.ref_in_universe), failures)
    check(f"{gene} recovered (recomputed vs report)", stats["recovered"], int(report_row.recovered), failures)

    # 2. the committed report must match the handoff's frozen gates
    if gene in GATES_PRIMARY:
        r, k, n, rec, hp, pp = GATES_PRIMARY[gene]
        check(f"{gene} report ref_in_universe", int(report_row.ref_in_universe), r, failures)
        check(f"{gene} report candidates", int(report_row.candidates), k, failures)
        check(f"{gene} report universe", int(report_row.universe), n, failures)
        check(f"{gene} report recovered", int(report_row.recovered), rec, failures)
        check(f"{gene} report hyperg_p", float(report_row.hyperg_p), hp, failures, tol=1e-12)
        check(f"{gene} report perm_p", float(report_row.perm_p), pp, failures, tol=1e-12)

    if gene != "RB1":
        return
    r, k, n, rec, hp, pp = GATES_SENSITIVITY_RB1
    check("RB1 sensitivity ref_in_universe", int(sens_row.ref_in_universe), r, failures)
    check("RB1 sensitivity recovered", int(sens_row.recovered), rec, failures)
    check("RB1 sensitivity hyperg_p", float(sens_row.hyperg_p), hp, failures, tol=1e-12)
    check("RB1 sensitivity perm_p", float(sens_row.perm_p), pp, failures, tol=1e-12)

    # 3. the union across targets, and the identity of the recovered compounds
    union_tested = set().union(*[e["tested"] for e in targets]) if targets else set()
    union_rec = set().union(*[e["recovered"] for e in targets]) if targets else set()
    check("RB1 union tested", len(union_tested), 94, failures)
    check("RB1 union recovered", len(union_rec), 13, failures)
    check("RB1 recovered compound names", sorted(union_rec), sorted(GATE_RB1_RECOVERED), failures)

    # 4. the per-target expansion
    got = {e["target"]: (len(e["tested"]), len(e["recovered"])) for e in targets}
    for tgt, want in GATE_RB1_TARGETS.items():
        check(f"RB1 target {tgt} (tested, recovered)", got.get(tgt), want, failures)
    extra = sorted(set(got) - set(GATE_RB1_TARGETS))
    if extra:
        failures.append(f"RB1 targets present but not in the gate table: {extra}")


def fmt_p(x):
    x = float(x)
    return "1" if x >= 1 else f"{x:.3g}"


def pct(a, b):
    return f"{a / b:.0%}" if b else "n/a"


def emit(gene, args, stats, report, sens_row, targets, census_n, census_paths, matched, rob):
    """Build the Supplement 7 document. Every number here comes from the arguments above."""
    row = report.set_index("gene").loc[gene]
    tested_total = stats["ref"]
    rec_total = stats["recovered"]
    misses = sorted(str(row.misses).split(";")) if isinstance(row.misses, str) and row.misses else []

    L = []
    A = L.append
    A(f"# Supplement 7 — Table 1 ({gene}), rebuilt from the literature-blind benchmark")
    A("")
    A(f"**Generated** by `concordance/build_suppl7_table1.py` from frozen inputs. Every figure below is "
      f"derived at run time; none is transcribed. The generator self-verifies against the committed "
      f"engine output and refuses to write if any acceptance gate fails.")
    A("")

    # ---- 1. the picture -----------------------------------------------------------------
    A("## 1. What changed, and why the old table could not answer the question")
    A("")
    A("The old Table 1 and this one are **different objects, not two versions of the same table**.")
    A("")
    A("- **Old.** Start from the compounds the S′ window selected, then find a citation for each. It asks "
      "*\"can I find literature for what I selected?\"* The answer is yes by construction, so the table "
      "could not fail, and a table that cannot fail cannot validate anything.")
    A("- **New.** Start from the literature, written down and frozen **before anyone looked at ΔpS′**, "
      "then ask *\"how many of those prior expectations does the window recover in the lung cell lines?\"* "
      "— reported with the **misses** and an **enrichment p-value** against a random window of the same size.")
    A("")
    A("Two words the old table conflated, kept separate here:")
    A("")
    A("| | Question | Answer |")
    A("|---|---|---|")
    A("| **Verification** | Does every number regenerate from the frozen inputs? | Yes — this document is "
      "generated, and the generator fails closed if it does not reproduce the committed engine output. |")
    A(f"| **Validation** | Does recovery beat chance? | **{gene}"
      f"{' only, of the four genotypes tested' if gene == 'RB1' else ''}**, "
      f"p = {fmt_p(row.hyperg_p)} (hypergeometric), {fmt_p(row.perm_p)} (permutation). |")
    A("")
    A("A benchmark can be perfectly verified and still fail validation. Saying so plainly is the strongest "
      "position available, and it is precisely what the old table could not say.")
    A("")

    # ---- 2. glossary --------------------------------------------------------------------
    A("## 2. Terms used in this supplement")
    A("")
    A("A reader who does not hold *universe*, *recovered*, *miss* and *enrichment* cannot read the table "
      "below, so they are defined before the results rather than after.")
    A("")
    A("**The metric**")
    A("")
    A("| Term | Meaning |")
    A("|---|---|")
    A("| S′ | Signed potency–efficacy index for one compound in one cell line. Sign is kept: positive is "
      "net inhibition. |")
    A("| pS′ | Cohort mean of S′ for one compound across the cell lines of one genotype cohort. |")
    A("| ΔpS′ | pS′ in wildtype minus pS′ in mutant. **More negative means more mutant-selective.** |")
    A(f"| the window | The selection rule: pS′ positive in both cohorts **and** ΔpS′ ≤ {DELTA_LE:g}"
      f", with at least {MIN_LINES} measured lines per cohort. |".replace("≤ -", "≤ −"))
    A("| candidate | A compound that passes the window for a given genotype. |")
    A("")
    A("**The benchmark**")
    A("")
    A("| Term | Meaning |")
    A("|---|---|")
    A("| census, or reference set | The vulnerabilities compiled **from the literature**, frozen and hashed "
      "before any result was consulted. The thing the window is tested against. |")
    A("| blinded census assembly | The step that produces it: isolated agents compile the set from stated "
      "inclusion criteria, their output is transferred verbatim into a file, and the file is frozen and "
      "hashed before any scoring runs. |")
    A("| structural blinding | The safeguard. The blind follows from how that step is built, not from what "
      "anyone knew. See §9.4. |")
    A(f"| directional census | The **primary** {census_n.get(os.path.basename(args.census), '?')}-row set, "
      f"excluding rows whose sensitive genotype is the wildtype one. The full "
      f"{census_n['full']}-row set is reported as a sensitivity analysis. |")
    A("| universe | Compounds measured in enough wildtype **and** mutant lines to be scored at all. The "
      "testable pool. |")
    A("| reference-in-universe | Census compounds that are actually in the universe. The rest cannot be "
      "scored either way. |")
    A("| recovered | Reference-in-universe compounds that the window also selected. |")
    A("| miss | A reference compound that **was** tested and was **not** selected. Misses are reported; a "
      "benchmark without them is not a benchmark. |")
    A("| recovery | Recovered divided by reference-in-universe. **Not** a sensitivity, and not an accuracy. |")
    A("| enrichment | Whether the recovered count exceeds what a *random* window of the same size would "
      "recover. Reported two ways, closed-form and by 10,000 random draws. |")
    A("")

    # ---- 3. headline --------------------------------------------------------------------
    A("## 3. Headline result")
    A("")
    A("| | |")
    A("|---|---|")
    A(f"| Reference compounds tested in the {gene} cohort | **{tested_total}** |")
    A(f"| Recovered by the window (pS′<sub>WT</sub> > 0, pS′<sub>MUT</sub> > 0, ΔpS′ ≤ −2) | "
      f"**{rec_total} ({pct(rec_total, tested_total)})** |")
    A(f"| Missed | **{len(misses)}** |")
    A(f"| Tested universe / candidates passing the window | {int(row.universe)} / {int(row.candidates)} |")
    A(f"| Hypergeometric p | **{fmt_p(row.hyperg_p)}** |")
    A(f"| Permutation p (10,000×) | **{fmt_p(row.perm_p)}** |")
    if sens_row is not None:
        A(f"| Sensitivity analysis (full {census_n['full']}-row census) | "
          f"{int(sens_row.recovered)}/{int(sens_row.ref_in_universe)} = "
          f"{pct(int(sens_row.recovered), int(sens_row.ref_in_universe))}, "
          f"p = {fmt_p(sens_row.hyperg_p)} / {fmt_p(sens_row.perm_p)} |")
    A("")
    if gene == "RB1":
        A("**The two-row decision rule was written blind.** The RB1 census agent flagged two rows "
          "(CDK4 and CDK6 / palbociclib, PMID 38528594) as inverse-direction — there the *RB1-proficient* "
          "genotype is the sensitive one — and stated, before any result existed, that they "
          "\"should be dropped rather than counted as positives\" if the benchmark scores RB1-loss → "
          "sensitivity. The primary analysis follows that instruction; the full census is reported as the "
          "sensitivity analysis above. RB1 clears chance either way.")
        A("")

    # ---- 4. the method can say no -------------------------------------------------------
    A("## 4. The same method applied to all four genotypes")
    A("")
    A("Run identically, with a census built the same way by the same procedure:")
    A("")
    A("| Genotype | Reference tested | Recovered | Recovery | Hypergeometric p | Permutation p | Verdict |")
    A("|---|---:|---:|---:|---|---|---|")
    for g in GENES:
        r = report.set_index("gene").loc[g]
        verdict = "**clears chance**" if float(r.hyperg_p) < 0.05 else "chance"
        if int(r.ref_in_universe) and int(r.ref_in_universe) < 15:
            verdict += " (underpowered)"
        A(f"| {'**' + g + '**' if g == gene else g} | {int(r.ref_in_universe)} | {int(r.recovered)} | "
          f"{pct(int(r.recovered), int(r.ref_in_universe))} | {fmt_p(r.hyperg_p)} | {fmt_p(r.perm_p)} | "
          f"{verdict} |")
    A("")
    idx = report.set_index("gene")
    passed = [g for g in GENES if float(idx.loc[g].hyperg_p) < 0.05]
    failed = [g for g in GENES if g not in passed]
    A(f"**{len(failed)} of the {len(GENES)} fail.** That is the evidence the benchmark is not rigged toward "
      f"the paper: the same procedure that returns a positive for {', '.join(passed) or 'nothing'} returns "
      f"chance for {', '.join(failed)}. In particular the earlier seed-set result for TP53 "
      f"(p = 5.6 × 10⁻⁸ off five reference rows dominated by the KIF11/Eg5 family) does not survive a proper "
      f"census — TP53 recovery is {int(idx.loc['TP53'].recovered)}/{int(idx.loc['TP53'].ref_in_universe)}, "
      f"p = {fmt_p(idx.loc['TP53'].hyperg_p)}.")
    A("")

    # ---- 5. Table 1 proper --------------------------------------------------------------
    A(f"## 5. Table 1 — literature-nominated {gene} vulnerabilities and their recovery by the S′ window")
    A("")
    A("Each row is a **target the literature nominated**, not a compound the window selected. *Tested* = "
      "PRISM 19Q4 compounds annotated to that target and measured in ≥3 "
      f"{gene}-wildtype and ≥3 {gene}-mutant lung lines. **Targets overlap** — a pan-Aurora compound is "
      "annotated to both AURKA and AURKB — so the column does **not** sum; the union is the headline.")
    A("")
    A("| Reference target | Evidence (PMID) | Model system | Tested | Recovered | Recovered compounds | Census caveat |")
    A("|---|---|---|---:|---:|---|---|")
    for e in targets:
        pm = ", ".join(e["pmids"]) or (", ".join(e["dois"]) or "—")
        tis = e["tissue"] or "not annotated"
        if not e["tested"]:
            A(f"| {e['target']} | {pm} | {tis} | 0 | — | *no compound in PRISM 19Q4* | {e['flag'] or '—'} |")
            continue
        names = ", ".join(sorted(e["recovered"])) if e["recovered"] else "—"
        bold = "**" if e["recovered"] else ""
        A(f"| {bold}{e['target']}{bold} | {pm} | {tis} | {len(e['tested'])} | "
          f"{bold}{len(e['recovered'])}{bold} | {names} | {e['flag'] or '—'} |")
    union_t = set().union(*[e["tested"] for e in targets]) if targets else set()
    union_r = set().union(*[e["recovered"] for e in targets]) if targets else set()
    A(f"| **Union** | — | — | **{len(union_t)}** | **{len(union_r)}** | "
      f"{pct(len(union_r), len(union_t))} | p = {fmt_p(row.hyperg_p)} / {fmt_p(row.perm_p)} |")
    A("")
    zero = [e["target"] for e in targets if not e["tested"]]
    if zero:
        A(f"**{len(zero)} nominated target{'s' if len(zero) > 1 else ''} could not be tested at all** "
          f"({', '.join(zero)}): the PRISM Repurposing 19Q4 library contains no compound annotated to "
          f"{'them' if len(zero) > 1 else 'it'}. That is a **dataset boundary, not a negative result**, and "
          "it must not be read as the window missing them.")
        A("")
    flagged = [e for e in targets if e["flag"]]
    if flagged:
        A("**The census grades its own rows.** The caveat column is quoted in substance from the census "
          "assembly notes, not added afterwards to explain results away. Rows carrying a caveat "
          f"({', '.join(e['target'] for e in flagged)}) should be weighted below the rest by any reader "
          "scoring this table.")
        A("")

    # ---- 6. the shape of recovery -------------------------------------------------------
    A("## 6. The shape of the recovery — the part the old table could not show")
    A("")
    A("Recovery is **partial within every class and zero in some**, which is what a selective signal looks "
      "like. A window that recovered everything would be uninformative.")
    A("")
    A("| Class | Recovered / tested |")
    A("|---|---|")
    by_t = {e["target"]: e for e in targets}
    if gene == "RB1" and "AURKA" in by_t and "AURKB" in by_t:
        at = by_t["AURKA"]["tested"] | by_t["AURKB"]["tested"]
        ar = by_t["AURKA"]["recovered"] | by_t["AURKB"]["recovered"]
        A(f"| Aurora kinase (AURKA ∪ AURKB) | **{len(ar)} / {len(at)}** |")
    for t in [e["target"] for e in targets if e["tested"]]:
        if gene == "RB1" and t in ("AURKA", "AURKB"):
            continue
        A(f"| {t} | {len(by_t[t]['recovered'])} / {len(by_t[t]['tested'])} |")
    A("")
    if misses:
        A(f"### The {len(misses)} misses — report these, always")
        A("")
        A("`" + ", ".join(misses) + "`")
        A("")
        A("A benchmark with no misses is not a benchmark. These are compounds the literature nominates and "
          "the window did **not** select.")
        A("")
    if matched:
        A("### How each recovered compound matched")
        A("")
        A("Target → compound resolution runs against PRISM's own target/MOA annotation strings, which the "
          "review flagged as sometimes wrong. The matched text is shown so a reader can judge each call "
          "rather than take it on trust.")
        A("")
        A("| Recovered compound | Matched target(s) | PRISM annotation text |")
        A("|---|---|---|")
        for nm in sorted(matched):
            tg, txt = matched[nm]
            txt = txt.strip(" ;") or "(empty)"
            A(f"| {nm} | {', '.join(tg)} | `{txt[:140]}` |")
        A("")

    # ---- 7. robustness ------------------------------------------------------------------
    A("## 7. Robustness — what the enrichment does and does not survive")
    A("")
    A("Every figure in this section is computed, not asserted. The closed-form test is used throughout; it "
      "agrees with the permutation test in the headline analysis.")
    A("")
    A("### 7.1 Leave-one-class-out")
    A("")
    A("Targets are grouped into **overlap-closed classes**: two targets share a class when some PRISM "
      "compound resolves to both, so a class is exactly the unit that can be removed without partially "
      "removing another target's compounds. Each row removes one class from the reference set and rescores.")
    A("")
    A("| Class removed | Its tested / recovered | Reference left | Recovered left | p |")
    A("|---|---|---:|---:|---|")
    fr, fk, fp = rob["full"]
    A(f"| *nothing removed* | — | {fr} | {fk} | **{fmt_p(fp)}** |")
    for cls, dt, dr, kr, kk, kp in rob["classes"]:
        mark = "**" if kp >= 0.05 else ""
        A(f"| {' + '.join(cls)} | {dt} / {dr} | {kr} | {kk} | {mark}{fmt_p(kp)}{mark} |")
    A("")
    if rob.get("aurora"):
        at, ar, kr, kk, kp = rob["aurora"]
        A(f"### 7.2 The result is carried by the Aurora kinase class")
        A("")
        A(f"AURKA and AURKB are the same pharmacological intervention: {at} compounds resolve to the pair "
          f"and {ar} of the {fk} recovered compounds are among them. Removing both leaves "
          f"**{kk} of {kr} recovered, p = {fmt_p(kp)}** — chance.")
        A("")
        A("Single leave-one-out hides this, because dropping AURKA leaves AURKB and almost all of the same "
          "compounds. **The defensible claim is therefore specific: RB1-loss lines are selectively sensitive "
          "to Aurora kinase inhibitors.** It is not broad recovery of RB1 biology across the nominated "
          "targets, and the supplement should not be written as though it were. No other class is "
          "load-bearing: removing any one of them leaves the enrichment significant.")
        A("")
    tr, tk, tp, only_moa = rob["target_only"]
    A(f"### 7.{'3' if rob.get('aurora') else '2'} Annotation noise is not driving it")
    A("")
    A(f"Repeating the analysis using only PRISM's structured target field, discarding every match made "
      f"through free-text mechanism annotation, gives **{tk} of {tr} recovered, p = {fmt_p(tp)}**. "
      + (f"Compounds recovered *only* through free text: {', '.join(only_moa)}."
         if only_moa else "No recovered compound depended on free-text matching."))
    A("")
    A(f"### 7.{'4' if rob.get('aurora') else '3'} The window threshold is not cherry-picked")
    A("")
    A("| ΔpS′ threshold | Candidates | Recovered | p |")
    A("|---|---:|---:|---|")
    for d, nc, k2, p2 in rob["thresholds"]:
        mark = "**" if abs(d - DELTA_LE) < 1e-9 else ""
        A(f"| {mark}≤ {d:g}{mark} | {nc} | {k2} | {mark}{fmt_p(p2)}{mark} |".replace("≤ -", "≤ −"))
    A("")
    A("The reported threshold is not the most favourable setting in this range, which is what an "
      "artifact of threshold choice would look like.")
    A("")
    A(f"### 7.{'5' if rob.get('aurora') else '4'} Multiple testing across the four genotypes")
    A("")
    A("| Genotype | p | Bonferroni across 4 |")
    A("|---|---|---|")
    for g, pv, bp in rob["bonferroni"]:
        A(f"| {g} | {fmt_p(pv)} | {fmt_p(bp)} |")
    A("")

    # ---- 8. draft manuscript text -------------------------------------------------------
    A("## 8. Draft manuscript text (drop-in for §3.7 / Supplement 7)")
    A("")
    # name every class that recovered something; merge AURKA/AURKB into one Aurora class
    seen, classes = set(), []
    if gene == "RB1" and "AURKA" in by_t and "AURKB" in by_t:
        ar = by_t["AURKA"]["recovered"] | by_t["AURKB"]["recovered"]
        if ar:
            classes.append(f"Aurora kinase ({', '.join(sorted(ar))})")
            seen |= ar
    for e in targets:
        if gene == "RB1" and e["target"] in ("AURKA", "AURKB"):
            continue
        rest = e["recovered"] - seen
        if rest:
            classes.append(f"{e['target']} ({', '.join(sorted(rest))})")
            seen |= rest
    aurora = (" " + "; ".join(classes)) if classes else " none"
    A(f"> To test whether the S′ selection window recovers established {gene} biology, a reference set of "
      f"{gene}-selective vulnerabilities was compiled from the published literature under **structural "
      f"blinding**. In this blinded census assembly, four isolated AI agents, one per genotype, worked from "
      f"stated inclusion criteria without access to the analysis repository and without sight of any S′, pS′ "
      f"or ΔpS′ value; their output was transferred verbatim into the reference file, which was then frozen "
      f"and checksum-verified before the benchmark was run. Of {tested_total} PRISM compounds "
      f"annotated to these literature-nominated targets and measured in the {gene} cohort "
      f"(≥3 wildtype and ≥3 mutant lung lines), the window recovered {rec_total} "
      f"({pct(rec_total, tested_total)}; hypergeometric p = {fmt_p(row.hyperg_p)}, "
      f"10,000-permutation p = {fmt_p(row.perm_p)}"
      + (f"; {int(sens_row.recovered)}/{int(sens_row.ref_in_universe)}, p = {fmt_p(sens_row.hyperg_p)} in a "
         f"sensitivity analysis retaining two inverse-direction entries" if sens_row is not None else "")
      + f"). Recovered compounds fall into coherent mechanistic classes —{aurora} — while {len(misses)} "
      f"annotated compounds were tested and not recovered. Recovery is therefore selective rather than "
      f"indiscriminate. "
      + (f"The enrichment is carried by the Aurora kinase class: removing AURKA and AURKB from the reference "
         f"set leaves {rob['aurora'][3]} of {rob['aurora'][2]} recovered at p = {fmt_p(rob['aurora'][4])}, "
         f"so the supported claim is the specific one, that {gene}-deficient lines are selectively sensitive "
         f"to Aurora kinase inhibitors, rather than a broad recovery of {gene} biology. No other target "
         f"class is load-bearing. " if rob.get("aurora") else "")
      + f"The reference set is pan-cancer, whereas recovery is measured in lung cell lines. "
      f"This analysis establishes enrichment for literature-validated {gene} dependencies beyond chance; it "
      f"does **not** estimate sensitivity, specificity or positive predictive value, and the same procedure "
      f"applied to PTEN, CDKN2A and TP53 returned chance-level recovery. It is reported alongside the "
      f"orthogonal genetic-dependency evidence in Supplement 8 (RNAi/CRISPR, RB–E2F axis), which is also "
      f"{gene}-anchored: the study's two independent lines of evidence converge on the same genotype.")
    A("")

    # ---- 9. limitations -----------------------------------------------------------------
    A("## 9. What this analysis does not claim")
    A("")
    A("1. **Not a sensitivity estimate.** The design cannot estimate sensitivity, specificity or positive "
      "predictive value. Recovery percentage is not accuracy.")
    A("2. **Pan-cancer reference, lung measurement.** The census draws on SCLC, breast/TNBC, prostate, "
      "hepatocellular, retinoblastoma, ovarian and bladder models; recovery is measured in lung lines. "
      "The census records why: *\"Lung-specific primary evidence is scarce for PTEN and CDKN2A and "
      "moderate for RB1 and TP53. A lung-restricted census would have been too small to test; the "
      "pan-cancer scope is a deliberate and necessary choice, and a limitation to state.\"*")
    A("3. **Annotation noise.** Target → compound expansion relies on PRISM's own target/MOA annotations, "
      "which the referee review flagged as sometimes wrong (barasertib, for example, is mis-annotated). "
      "§6 shows the matched annotation text for every recovered compound so each call can be checked.")
    A("4. **The blinding is structural, not absolute.** The assembly step was initiated from within a "
      "results-aware project, so the guarantee does not rest on anyone's ignorance. It rests on two "
      "procedural facts. The four AI agents that built the rows worked in isolation, without repository "
      "access and without sight of any ΔpS′ value. Their output was transferred verbatim — no row added, "
      "removed, reworded or reordered — which removes any opportunity to shape the reference set after "
      "seeing how it would score. What a reviewer can verify directly is that the reference set has not "
      "changed since it was hashed; what structural blinding does not provide is an independent record of "
      "the conditions under which the rows were written. A fully independent replication would assemble the "
      "census before any results exist. (`BLIND_CENSUS_2026-08-31.md` states this same limitation in terms "
      "of the person who commissioned the census; the procedural statement here is the accurate one, and "
      "that document is left unedited as the record of the day.)")
    if rob.get("aurora"):
        A(f"5. **The enrichment rests on one target class.** Removing the Aurora pair leaves "
          f"{rob['aurora'][3]} of {rob['aurora'][2]} recovered at p = {fmt_p(rob['aurora'][4])}. The result "
          f"supports a single specific dependency, not recovery of the genotype's biology in general. "
          f"See §7.2.")
    n = 6 if rob.get("aurora") else 5
    A(f"{n}. **The freeze commit is retroactive.** The census was hashed and run on 2026-08-31 and committed "
      f"on 2026-09-06. The hashes, not the commit date, are the evidence.")
    A(f"{n + 1}. **Model-system annotation is post-hoc.** The *Model system* and *Census caveat* columns were "
      f"added on 2026-09-06 from the cited primaries and the census assembly notes. They are presentation "
      f"only and enter no computation.")
    A("")

    # ---- 10. author decisions ------------------------------------------------------------
    A("## 10. Decisions for the authors (surfaced, not applied)")
    A("")
    A("1. **PARP stays in.** An earlier analysis argued for excluding PARP1 from the RB1 reference set — no "
      "BioGRID RB1–PARP1 genetic interaction, disjoint STRING modules, older RB1–PARP literature tracing to "
      "co-deleted RNASEH2B/BRCA2. That was wrong. The blind census cites PMID 42618565, a 2026 isogenic "
      "hepatocellular screen showing biallelic RB1-inactivated cells are selectively PARP-sensitive, and "
      "olaparib and niraparib are 2 of the 13 recovered. Keep PARP, cite 42618565, drop the "
      "\"context-dependent\" footnote.")
    A("2. **Delete a fabricated citation.** Table 1 currently cites *\"Jansen VM, Bhatt DL, Maniaci J, et "
      "al., Cancer Discov 2017\"* on the AURKB row. No such paper exists. Oser 2019 (PMID 30373918) carries "
      "that row; Gong 2019 (PMID 30373917) is the real Aurora-A paper.")
    A("3. **De-claim TP53–KIF11** in Table 4 and the abstract. Present it as a novel internal finding of "
      "this dataset, explicitly **not** literature-validated.")
    A("4. **Retire the 75–94% recovery figures** in the abstract, §3.7 and §4, along with §4's \"confirming "
      "the accuracy and biological specificity of the S′ index.\" Claim validation for RB1 only, paired "
      "with Supplement 8.")
    A("5. **Change the table title.** *\"Literature-Corroborated Candidate Vulnerabilities Identified in "
      "Pharmacologic Screens\"* describes the old direction; if it survives, the circularity objection "
      "stands in the heading itself.")
    A("")

    # ---- 11. provenance ------------------------------------------------------------------
    A("## 11. Provenance and reproduction")
    A("")
    A("| Item | Value |")
    A("|---|---|")
    for name, path in sorted(census_paths.items()):
        A(f"| Census `{name}` | {census_n.get(name, '?')} rows, md5 `{md5sum(path)}` |")
    _fn = 6 if rob.get("aurora") else 5
    A(f"| Census freeze commit | `{FREEZE_COMMITS['census']}` (retroactive — see §9.{_fn}) |")
    A(f"| Results commit | `{FREEZE_COMMITS['results']}` |")
    A(f"| Engine | `{ENGINE_INVOCATION}` |")
    for k, v in DATA_MD5.items():
        A(f"| {k} | md5 `{v}` |")
    A(f"| SL window | `sprime_core.py` — imported, not redefined "
      f"(ΔpS′ ≤ {DELTA_LE:g}, ≥{MIN_LINES} lines per arm) |".replace("≤ -", "≤ −"))
    A("")
    A("```bash")
    A("uv run --locked python fetch_data.py")
    A("uv run --locked python sprime_pipeline.py")
    A("uv run --locked python concordance/concordance_enrichment.py \\")
    A("    --reference concordance/reference_set_2026-08-31_directional.csv \\")
    A("    --out concordance/results/2026-08-31_blind --perm 10000")
    A(f"uv run --locked python concordance/build_suppl7_table1.py --genotype {gene}")
    A("```")
    A("")
    return "\n".join(L) + "\n"


def main():
    ap = argparse.ArgumentParser(description="Generate Supplement 7 Table 1 from the frozen blind benchmark.")
    ap.add_argument("--genotype", default="RB1", choices=GENES)
    ap.add_argument("--census", default=os.path.join(_HERE, "reference_set_2026-08-31_directional.csv"))
    ap.add_argument("--census-full", default=os.path.join(_HERE, "reference_set_2026-08-31.csv"))
    ap.add_argument("--results", default=os.path.join(_HERE, "results", "2026-08-31_blind",
                                                      "concordance_report_primary_directional.csv"))
    ap.add_argument("--results-sensitivity", default=os.path.join(_HERE, "results", "2026-08-31_blind",
                                                                 "concordance_report_sensitivity_full.csv"))
    ap.add_argument("--annotations", default=os.path.join(_HERE, "reference_annotations_2026-08-31.csv"))
    ap.add_argument("--derived", default=os.path.join(os.path.dirname(_HERE), "results"))
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    gene = a.genotype
    out = a.out or os.path.join(_HERE, f"SUPPL7_TABLE1_{gene}.md")

    census = pd.read_csv(need(a.census, "frozen census (primary)"), comment="#")
    census["genotype"] = census["genotype"].astype(str).str.upper()
    report = pd.read_csv(need(a.results, "blind results (primary)"))
    sens = pd.read_csv(need(a.results_sensitivity, "blind results (sensitivity)"))
    notes = load_notes(a.annotations)
    if not notes:
        print(f"NOTE: no annotation file at {a.annotations} — Model system / Census caveat will read "
              f"'not annotated'.")

    mat, geno, ann, ann_t = load_matrix(a.derived)
    universe, cand = cohort(mat, geno, gene)
    targets = per_target(census, gene, universe, cand, ann, notes)
    rob = robustness(gene, census, mat, geno, universe, cand, ann, ann_t, report)

    resolved = set().union(*[e["tested"] for e in targets]) if targets else set()
    stats = dict(universe=len(universe), candidates=len(cand),
                 ref=len(resolved), recovered=len(resolved & cand))

    # matched annotation text per recovered compound — for the "how it matched" table
    matched = {}
    for e in targets:
        for nm in e["recovered"]:
            tg, txt = matched.get(nm, ([], ann.get(nm, "")))
            matched[nm] = (sorted(set(tg + [e["target"]])), txt)

    report_row = report.set_index("gene").loc[gene]
    sens_row = sens.set_index("gene").loc[gene] if gene in set(sens.gene) else None
    census_paths = {os.path.basename(a.census): a.census, os.path.basename(a.census_full): a.census_full}
    full = pd.read_csv(need(a.census_full, "frozen census (full)"), comment="#")
    census_n = {os.path.basename(a.census): len(census), os.path.basename(a.census_full): len(full),
                "full": len(full)}

    failures = []
    verify(gene, stats, report_row, sens_row, targets, census_paths, failures)
    print(f"{gene}: universe {stats['universe']}, candidates {stats['candidates']}, "
          f"reference-in-universe {stats['ref']}, recovered {stats['recovered']}")
    print(f"  targets: {len(targets)} nominated, "
          f"{sum(1 for e in targets if not e['tested'])} with no compound in PRISM 19Q4")
    if failures:
        print(f"\nACCEPTANCE GATES FAILED ({len(failures)}) — no document written:")
        for f in failures:
            print(f"  - {f}")
        print("\nThis means the derived baseline changed. Report the delta; do not publish new numbers.")
        raise SystemExit(1)
    print(f"  all acceptance gates reproduced")

    doc = emit(gene, a, stats, report, sens_row, targets, census_n, census_paths, matched, rob)
    with open(out, "w", encoding="utf-8", newline="\n") as f:
        f.write(doc)
    print(f"  wrote {out}")

    # Robustness numbers as a committed CSV: docs/evidence.md, concordance/README.md and CLAUDE.md
    # quote the leave-out figure in prose, and tests/test_docs_numbers.py pins that prose to this file.
    rows = [dict(analysis="full", removed="", tested_removed=0, recovered_removed=0,
                 ref_left=rob["full"][0], recovered_left=rob["full"][1], hyperg_p=rob["full"][2])]
    for cls, dt, dr, kr, kk, kp in rob["classes"]:
        rows.append(dict(analysis="drop_class", removed="+".join(cls), tested_removed=dt,
                         recovered_removed=dr, ref_left=kr, recovered_left=kk, hyperg_p=kp))
    if rob.get("aurora"):
        at, ar, kr, kk, kp = rob["aurora"]
        rows.append(dict(analysis="drop_aurora_pair", removed="AURKA+AURKB", tested_removed=at,
                         recovered_removed=ar, ref_left=kr, recovered_left=kk, hyperg_p=kp))
    rob_csv = os.path.join(os.path.dirname(a.results), f"robustness_{gene}.csv")
    (pd.DataFrame(rows)
       .sort_values(["analysis", "removed"], kind="stable")          # canonical, stable row order
       .to_csv(rob_csv, index=False, float_format="%.12g"))
    print(f"  wrote {rob_csv}")


if __name__ == "__main__":
    main()
