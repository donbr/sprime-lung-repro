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
import argparse, os, re, sys
import numpy as np, pandas as pd

GENES = ["PTEN", "CDKN2A", "RB1", "TP53"]
DEFAULT_TARGETS = ["AURKB", "AURKA", "PLK1", "CHEK1", "PARP1", "KIF11", "AKT1", "SKP2", "CCNE2", "E2F4", "CDK4", "CDK6"]
try:
    from scipy.stats import mannwhitneyu
except Exception:
    mannwhitneyu = None

def bh_fdr(pvals):
    p = np.asarray(pvals, float); n = len(p); order = np.argsort(p)
    q = np.empty(n); prev = 1.0
    for i in range(n - 1, -1, -1):
        idx = order[i]; prev = min(prev, p[idx] * n / (i + 1)); q[idx] = prev
    return q

def main():
    here = os.path.dirname(os.path.abspath(__file__))
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default=os.path.join(here, "data_sources"))
    ap.add_argument("--derived", default=os.path.join(here, "results"))
    ap.add_argument("--out", default=os.path.join(here, "results"))
    ap.add_argument("--demeter", default="D2_combined_gene_dep_scores.csv")
    ap.add_argument("--genes", nargs="*", default=None)
    ap.add_argument("--reference", default=None, help="pull target genes from a concordance reference CSV")
    ap.add_argument("--min-lines", type=int, default=5)
    a = ap.parse_args()

    dfile = os.path.join(a.data, a.demeter)
    if not os.path.exists(dfile):
        print(f"DEMETER2 file not found: {dfile}\n  Get it with:  python fetch_data.py --only demeter2_rnai")
        sys.exit(2)

    targets = a.genes or DEFAULT_TARGETS
    if a.reference and os.path.exists(a.reference):
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
            if mannwhitneyu is not None and len(w) and len(m):
                p = float(mannwhitneyu(m, w, alternative="greater").pvalue)  # mutant more dependent
            else:
                p = float("nan")
            pset.append((tgt, len(w), len(m), dpd, p))
        if pset:
            q = bh_fdr([x[4] for x in pset]) if mannwhitneyu is not None else [float("nan")] * len(pset)
            for (tgt, nw, nm, dpd, p), qq in zip(pset, q):
                rows.append(dict(genotype=gene, target=tgt, n_wt=nw, n_mut=nm,
                                 delta_pD=round(dpd, 3), mw_p=p, bh_q=round(float(qq), 3) if qq == qq else None,
                                 mutant_selective=(dpd < 0 and (qq < 0.10 if qq == qq else False))))
    res = pd.DataFrame(rows)
    if len(res):
        res = res.sort_values(["genotype", "delta_pD"])
        print(res.to_string(index=False))
        res.to_csv(os.path.join(a.out, "demeter_validation.csv"), index=False)
        print(f"\nwrote {a.out}/demeter_validation.csv")
        print("ΔpD < 0 with q < 0.10 => mutant-selective RNAi dependency (validates the genotype axis, not the target).")
    else:
        print("No target survived the min-lines filter; DEMETER2 lung coverage may be too thin for these genes.")

if __name__ == "__main__":
    main()
