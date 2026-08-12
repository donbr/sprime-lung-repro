#!/usr/bin/env python3
"""Bootstrap confidence-interval gate for the S′ candidate lists.

For every compound with valid WT/mutant pools, resample cell lines WITH replacement (stratified within each
pool) B times, recompute ΔpS′ = pS′_WT − pS′_mut, and take the 2.5/97.5 percentile CI. Then report how many
raw candidates (pS′_WT>0, pS′_mut>0, ΔpS′≤−2) survive successively stricter gates:
  point   : ΔpS′ point estimate ≤ −2                    (current manuscript rule)
  excl0   : + bootstrap 95% CI upper bound < 0          (selectivity is non-zero)
  ci<=-2  : + bootstrap 95% CI upper bound ≤ −2         (interval fully past the threshold)

Reads ../results/{sprime_lung_pairs,lung_genotypes}.csv. Writes ../results/bootstrap_ci_gate.csv (per
candidate: ΔpS′, CI, which gates it passes) and prints a per-genotype survival table.

Usage:  python bootstrap_ci_gate.py [--B 2000] [--seed 20260811]
"""
import argparse, os
import numpy as np, pandas as pd
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _common import safe_stdout
from sprime_core import DELTA_LE, MIN_LINES, passes_window
safe_stdout()

GENES = ["PTEN", "CDKN2A", "RB1", "TP53"]

def main():
    here = os.path.dirname(os.path.abspath(__file__))
    ap = argparse.ArgumentParser()
    ap.add_argument("--derived", default=os.path.join(here, "results"))
    ap.add_argument("--out", default=os.path.join(here, "results"))
    ap.add_argument("--B", type=int, default=2000)
    ap.add_argument("--seed", type=int, default=20260811)
    a = ap.parse_args()
    rng = np.random.default_rng(a.seed)

    pairs = pd.read_csv(os.path.join(a.derived, "sprime_lung_pairs.csv")).dropna(subset=["name"])
    geno = pd.read_csv(os.path.join(a.derived, "lung_genotypes.csv")).set_index("ModelID")
    M = pairs.pivot_table(index="name", columns="depmap_id", values="sprime", aggfunc="mean")
    comps = M.index.to_numpy()

    rows = []
    print(f"Bootstrap CI gate (B={a.B}); resampling cell lines within each pool.\n")
    print(f"{'gene':7}{'point ≤ -2':>12}{'+ CI<0':>10}{'+ CI≤-2':>10}{'  (survival of the point-estimate candidate list)'}")
    summary = []
    for g in GENES:
        v = geno[g]
        wt = [c for c in M.columns if v.get(c) == 0]
        mu = [c for c in M.columns if v.get(c) == 2]
        WT = M.reindex(columns=wt).to_numpy()      # compounds x nWT
        MU = M.reindex(columns=mu).to_numpy()      # compounds x nMUT
        nwt = np.sum(~np.isnan(WT), 1); nmut = np.sum(~np.isnan(MU), 1)
        pwt = np.nanmean(WT, 1); pmut = np.nanmean(MU, 1); dps = pwt - pmut
        ok = (nwt >= MIN_LINES) & (nmut >= MIN_LINES)
        cand = ok & passes_window(pwt, pmut)     # point-estimate candidates
        idx = np.where(cand)[0]
        n_excl0 = n_ci2 = 0
        for i in idx:
            wcol = WT[i][~np.isnan(WT[i])]; mcol = MU[i][~np.isnan(MU[i])]
            nb, mb = len(wcol), len(mcol)
            bw = wcol[rng.integers(0, nb, size=(a.B, nb))].mean(1)      # bootstrap pS'_WT
            bm = mcol[rng.integers(0, mb, size=(a.B, mb))].mean(1)      # bootstrap pS'_MUT
            bd = bw - bm
            lo, hi = np.percentile(bd, [2.5, 97.5])
            passes_excl0 = hi < 0
            passes_ci2 = hi <= DELTA_LE
            n_excl0 += passes_excl0; n_ci2 += passes_ci2
            rows.append(dict(gene=g, compound=comps[i], dpS=round(float(dps[i]), 3),
                             ci_lo=round(float(lo), 3), ci_hi=round(float(hi), 3),
                             n_wt=int(nwt[i]), n_mut=int(nmut[i]),
                             pass_point=True, pass_excl0=bool(passes_excl0), pass_ci_le2=bool(passes_ci2)))
        npt = len(idx)
        print(f"{g:7}{npt:>12}{n_excl0:>10}{n_ci2:>10}")
        summary.append(dict(gene=g, point=npt, ci_excl0=n_excl0, ci_le_minus2=n_ci2))

    pd.DataFrame(rows).to_csv(os.path.join(a.out, "bootstrap_ci_gate.csv"), index=False,
                              float_format="%.12g")
    pd.DataFrame(summary).to_csv(os.path.join(a.out, "bootstrap_ci_summary.csv"), index=False,
                                 float_format="%.12g")
    print("\n  point   = current rule (ΔpS′ point estimate ≤ −2)")
    print("  + CI<0  = also require bootstrap 95% CI upper bound < 0  (selectivity distinguishable from zero)")
    print("  + CI≤-2 = also require the whole 95% CI at/below the −2 threshold")
    print(f"\nwrote {a.out}/bootstrap_ci_gate.csv (per-candidate CIs) and bootstrap_ci_summary.csv")

if __name__ == "__main__":
    main()
