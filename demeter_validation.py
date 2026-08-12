#!/usr/bin/env python3
"""DEMETER2 RNAi genetic-dependency validation (Supplement-8 style), parallel to ΔpS′.

For each SL target gene, computes a genotype-contrasted dependency:
    D = −DEMETER2  (DEMETER2 runs negative-for-dependent; D>0 = more dependent)
    pD = cohort mean;  ΔpD = pD_WT − pD_MUT   (ΔpD < 0 ⇒ mutant-selective dependency, mirroring ΔpS′)
with a Mann–Whitney test and Benjamini–Hochberg FDR across the tested genes per genotype.

Needs the DEMETER2 file (data_sources/D2_combined_gene_dep_scores.csv — get it with fetch_data.py) plus the
derived tables from sprime_pipeline.py (results/lung_genotypes.csv, results/sprime_lung_pairs.csv for the
CCLE↔ACH map). Runs only when the DEMETER2 file is present; otherwise prints how to obtain it.

Usage:  python demeter_validation.py [--genes AURKB AURKA PLK1 ...] [--reference concordance/reference_seed_grounded.csv]
"""
import argparse, hashlib, os, re, sys
import numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _common import default_data_dir, safe_stdout
safe_stdout()

# DEMETER2 v6 combined gene dep scores (doi:10.6084/m9.figshare.6025238.v6) — same pin as fetch_data.py.
DEMETER_MD5 = "e82566a48993753c20ea5f480f1867ec"

GENES = ["PTEN", "CDKN2A", "RB1", "TP53"]
DEFAULT_TARGETS = ["AURKB", "AURKA", "PLK1", "CHEK1", "PARP1", "KIF11", "AKT1", "SKP2", "CCNE2", "E2F4", "CDK4", "CDK6"]
try:
    from scipy.stats import mannwhitneyu
except Exception:
    mannwhitneyu = None

def md5sum(path, chunk=1 << 20):
    h = hashlib.md5()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(chunk), b""):
            h.update(b)
    return h.hexdigest()

def bh_fdr(pvals):
    p = np.asarray(pvals, float); n = len(p); order = np.argsort(p)
    q = np.empty(n); prev = 1.0
    for i in range(n - 1, -1, -1):
        idx = order[i]; prev = min(prev, p[idx] * n / (i + 1)); q[idx] = prev
    return q

def main():
    here = os.path.dirname(os.path.abspath(__file__))
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default=default_data_dir(here))
    ap.add_argument("--derived", default=os.path.join(here, "results"))
    ap.add_argument("--out", default=os.path.join(here, "results"))
    ap.add_argument("--demeter", default="D2_combined_gene_dep_scores.csv")
    ap.add_argument("--genes", nargs="*", default=None)
    ap.add_argument("--reference", default=None, help="pull target genes from a concordance reference CSV")
    ap.add_argument("--min-lines", type=int, default=5)
    ap.add_argument("--skip-checksum", action="store_true", help="do not md5-verify the DEMETER2 matrix")
    a = ap.parse_args()

    dfile = os.path.join(a.data, a.demeter)
    if not os.path.exists(dfile):
        print(f"DEMETER2 file not found: {dfile}\n  Get it with:  python fetch_data.py --only demeter2_rnai")
        sys.exit(2)
    if a.skip_checksum:
        print("DEMETER2 checksum verification skipped (--skip-checksum). Input authenticity unverified.")
    else:
        got = md5sum(dfile)
        if got != DEMETER_MD5:
            print(f"DEMETER2 md5 MISMATCH: got {got}, expected {DEMETER_MD5}\n"
                  f"  {dfile} is not the pinned DEMETER2 v6 release — refusing to validate against it.\n"
                  f"  Re-fetch with:  python fetch_data.py --only demeter2_rnai   (or pass --skip-checksum)")
            sys.exit(3)

    targets = a.genes or DEFAULT_TARGETS
    if a.reference:
        if not os.path.exists(a.reference):
            print(f"ERROR: --reference {a.reference} not found."); sys.exit(2)
        ref = pd.read_csv(a.reference, comment="#")
        targets = sorted(set(targets) | set(ref["target"].dropna().astype(str)))
    targets = [t for t in targets if t]

    # CCLE↔ACH map + genotype calls
    pairs = pd.read_csv(os.path.join(a.derived, "sprime_lung_pairs.csv"))
    ccle2ach = dict(zip(pairs.ccle_name, pairs.depmap_id))
    geno = pd.read_csv(os.path.join(a.derived, "lung_genotypes.csv")).set_index("ModelID")

    # read only the target-gene rows from the DEMETER2 matrix (memory-safe)
    want = set(t.upper() for t in targets); keep = []
    for chunk in pd.read_csv(dfile, chunksize=2000, index_col=0):
        sym = chunk.index.to_series().str.extract(r"^([A-Za-z0-9\-]+)")[0].str.upper()
        hit = chunk[sym.isin(want).values]
        if len(hit): keep.append(hit)
    if not keep:
        print("No target genes found in DEMETER2 matrix. Check --genes symbols."); sys.exit(1)
    D = pd.concat(keep)
    D.index = D.index.to_series().str.extract(r"^([A-Za-z0-9\-]+)")[0].str.upper()
    # columns are CCLE names -> map to ACH -> restrict to our lung lines
    ach_cols = {c: ccle2ach.get(c) for c in D.columns}
    D = D.rename(columns=ach_cols)
    D = D.loc[:, [c for c in D.columns if isinstance(c, str) and c in geno.index]]
    Dneg = -D   # D>0 = more dependent

    rows = []
    for gene in GENES:
        v = geno[gene]
        wt = [c for c in Dneg.columns if v.get(c) == 0]
        mu = [c for c in Dneg.columns if v.get(c) == 2]
        pset = []
        for tgt in sorted(want & set(Dneg.index)):
            w = Dneg.loc[tgt, wt].dropna(); m = Dneg.loc[tgt, mu].dropna()
            if len(w) < a.min_lines or len(m) < a.min_lines:
                continue
            dpd = float(w.mean() - m.mean())      # ΔpD; <0 => mutant more dependent
            nan = float("nan")
            if mannwhitneyu is not None and len(w) and len(m):
                p_mut = float(mannwhitneyu(m, w, alternative="greater").pvalue)  # mutant more dependent
                p_wt = float(mannwhitneyu(w, m, alternative="greater").pvalue)   # WT more dependent
                p_two = float(mannwhitneyu(w, m, alternative="two-sided").pvalue)
            else:
                p_mut = p_wt = p_two = nan
            pset.append(dict(target=tgt, n_wt=len(w), n_mut=len(m), delta_pD=dpd,
                             p_mut=p_mut, p_wt=p_wt, p_two=p_two))
        if pset:
            # FDR within genotype, separately per hypothesis — a WT-selective target scores
            # p_mut -> 1, so q_mut alone reads as "nothing here" when the effect is real.
            for src, dst in (("p_mut", "q_mut"), ("p_wt", "q_wt"), ("p_two", "q_two")):
                qs = (bh_fdr([r[src] for r in pset]) if mannwhitneyu is not None
                      else [float("nan")] * len(pset))
                for r, qq in zip(pset, qs):
                    r[dst] = float(qq)
            for r in pset:
                q_mut, q_wt = r["q_mut"], r["q_wt"]
                rows.append(dict(
                    genotype=gene, target=r["target"], n_wt=r["n_wt"], n_mut=r["n_mut"],
                    delta_pD=round(r["delta_pD"], 3),
                    direction=("mutant-selective" if r["delta_pD"] < 0 else "WT-selective"),
                    mw_p=r["p_mut"], bh_q=round(q_mut, 3) if q_mut == q_mut else None,
                    p_wt=r["p_wt"], q_wt=round(q_wt, 4) if q_wt == q_wt else None,
                    p_two=r["p_two"], q_two=round(r["q_two"], 4) if r["q_two"] == r["q_two"] else None,
                    mutant_selective=(r["delta_pD"] < 0 and (q_mut < 0.10 if q_mut == q_mut else False)),
                    wt_selective=(r["delta_pD"] > 0 and (q_wt < 0.10 if q_wt == q_wt else False))))
    res = pd.DataFrame(rows)
    if len(res):
        res = res.sort_values(["genotype", "delta_pD"])
        print(res.to_string(index=False))
        res.to_csv(os.path.join(a.out, "demeter_validation.csv"), index=False)
        print(f"\nwrote {a.out}/demeter_validation.csv")
        print("ΔpD < 0 with q_mut < 0.10 => mutant-selective RNAi dependency (validates the genotype axis, not the target).")
        print("ΔpD > 0 with q_wt  < 0.10 => WT-selective (e.g. CDK4/6 under RB1 loss — a positive control).")
        print("Read `direction` before any q: bh_q/q_mut test ONLY 'mutant more dependent', so a real")
        print("WT-selective effect scores q_mut = 1.0. q_two is the two-sided test, the conservative one.")
    else:
        print("No target survived the min-lines filter; DEMETER2 lung coverage may be too thin for these genes.")

if __name__ == "__main__":
    main()
