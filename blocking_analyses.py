#!/usr/bin/env python3
"""The two blocking controls, reading the derived tables from sprime_pipeline.py.

 (1) candidate-list sizes per genotype + label-permutation null (empirical FDR at ΔpS′ ≤ −2)
 (2) line-centred S′ general-sensitivity control (+ ΔpS′-invariance diagnostic)

Writes results/candidate_null.csv, results/line_centring.csv, results/blocking_summary.txt.
Usage:  python blocking_analyses.py [--out DIR] [--perm 2000] [--seed 20260811]
"""
import argparse, os, sys
import numpy as np, pandas as pd

GENES = ["PTEN", "CDKN2A", "RB1", "TP53"]
MINN = 3

def candidates(mat, wt_ids, mut_ids):
    wt = mat.reindex(columns=wt_ids); mut = mat.reindex(columns=mut_ids)
    ok = (wt.notna().sum(1) >= MINN) & (mut.notna().sum(1) >= MINN)
    pwt = wt.mean(1); pmut = mut.mean(1); d = pwt - pmut
    return ok, ok & (pwt > 0) & (pmut > 0) & (d <= -2), d

def main():
    ap = argparse.ArgumentParser()
    here = os.path.dirname(os.path.abspath(__file__))
    ap.add_argument("--out", default=os.path.join(here, "results"))
    ap.add_argument("--perm", type=int, default=2000)
    ap.add_argument("--seed", type=int, default=20260811)
    a = ap.parse_args()
    rng = np.random.default_rng(a.seed)
    lines = []
    def log(*s):
        msg = " ".join(str(x) for x in s); print(msg, flush=True); lines.append(msg)

    pairs = pd.read_csv(os.path.join(a.out, "sprime_lung_pairs.csv")).dropna(subset=["name"])
    geno = pd.read_csv(os.path.join(a.out, "lung_genotypes.csv")).set_index("ModelID")
    M = pairs.pivot_table(index="name", columns="depmap_id", values="sprime", aggfunc="mean")
    log(f"S' matrix: {M.shape[0]} compounds x {M.shape[1]} lung lines\n")

    # ---------- Analysis 1 ----------
    log("ANALYSIS 1 — candidate sizes + label-permutation null (%d perms)" % a.perm)
    log(f"{'gene':7}{'tested':>8}{'candidates':>12}{'rate':>8}{'null_mean':>11}{'emp_p':>8}{'perm_FDR':>10}")
    rows = []
    for g in GENES:
        v = geno[g]
        wt = [c for c in M.columns if v.get(c) == 0]; mu = [c for c in M.columns if v.get(c) == 2]
        ok, cand, _ = candidates(M, wt, mu)
        ntest, nobs = int(ok.sum()), int(cand.sum())
        pool = wt + mu; nmut = len(mu); sub = M.reindex(columns=pool).values
        null = np.empty(a.perm)
        for i in range(a.perm):
            perm = rng.permutation(len(pool)); mi, wi = perm[:nmut], perm[nmut:]
            pm = np.nanmean(sub[:, mi], 1); pw = np.nanmean(sub[:, wi], 1)
            cm = np.sum(~np.isnan(sub[:, mi]), 1); cw = np.sum(~np.isnan(sub[:, wi]), 1)
            null[i] = np.nansum((cw >= MINN) & (cm >= MINN) & (pw > 0) & (pm > 0) & ((pw - pm) <= -2))
        emp_p = (np.sum(null >= nobs) + 1) / (a.perm + 1)
        fdr = null.mean() / nobs if nobs else float("nan")
        rows.append(dict(gene=g, tested=ntest, candidates=nobs, rate=nobs / ntest,
                         null_mean=null.mean(), emp_p=emp_p, perm_fdr=fdr))
        log(f"{g:7}{ntest:>8}{nobs:>12}{100*nobs/ntest:>7.1f}%{null.mean():>11.1f}{emp_p:>8.3f}{fdr:>10.2f}")
    pd.DataFrame(rows).to_csv(os.path.join(a.out, "candidate_null.csv"), index=False)
    log("  Only genotypes with perm_FDR well below ~0.5 carry signal beyond chance.\n")

    # ---------- Analysis 2 ----------
    log("ANALYSIS 2 — line-centred S' (general-sensitivity control)")
    line_med = M.median(axis=0); Mc = M.subtract(line_med, axis=1)
    log(f"{'gene':7}{'off(MUT-WT)':>13}{'raw':>6}{'centred':>9}{'survived':>10}{'corr_dpS':>10}")
    rows2 = []
    for g in GENES:
        v = geno[g]
        wt = [c for c in M.columns if v.get(c) == 0]; mu = [c for c in M.columns if v.get(c) == 2]
        wtm = np.median([line_med[c] for c in wt]); mum = np.median([line_med[c] for c in mu])
        ok_r, raw, d_r = candidates(M, wt, mu); ok_c, cen, d_c = candidates(Mc, wt, mu)
        rs, cs = set(raw[raw].index), set(cen[cen].index); both = ok_r & ok_c
        corr = float(np.corrcoef(d_r[both], d_c[both])[0, 1])
        rows2.append(dict(gene=g, offset_mut_minus_wt=mum - wtm, raw=len(rs), centred=len(cs),
                          survived=len(rs & cs), corr_dps=corr))
        log(f"{g:7}{mum-wtm:>+13.2f}{len(rs):>6}{len(cs):>9}{len(rs&cs):>10}{corr:>10.3f}")
    pd.DataFrame(rows2).to_csv(os.path.join(a.out, "line_centring.csv"), index=False)
    log("  Small offset + corr≈1 => no gross sensitivity confound; large raw→centred drop reflects the")
    log("  absolute pS'>0 gate (1uM / percent-Emax anchoring), not differential sensitivity.")

    with open(os.path.join(a.out, "blocking_summary.txt"), "w") as f:
        f.write("\n".join(lines) + "\n")
    log(f"\nwrote {a.out}/candidate_null.csv, line_centring.csv, blocking_summary.txt")

if __name__ == "__main__":
    main()
