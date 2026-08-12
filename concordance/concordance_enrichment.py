#!/usr/bin/env python3
"""Literature-blind concordance benchmark: recovery + misses + enrichment (hypergeometric + permutation).

Uses the already-computed S′ tables in ../results/ to build the per-genotype candidate lists and tested
universe, resolves a FROZEN literature reference set to PRISM compounds (by name and/or target/MOA), then
measures recovery and whether it beats chance. This does NOT build the reference set — that is done by hand,
blind to ΔpS′ (see PROTOCOL_literature_blind_concordance.md).

Usage:  python concordance_enrichment.py --reference reference_seed_grounded.csv [--perm 10000]
"""
import argparse, os, re, sys, math
import numpy as np, pandas as pd
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from _common import safe_stdout
from sprime_core import DELTA_LE, MIN_LINES, passes_window
safe_stdout()

GENES = ["PTEN", "CDKN2A", "RB1", "TP53"]
try:
    from scipy.stats import hypergeom
    def hyper_sf(k, N, K, n): return float(hypergeom.sf(k - 1, N, K, n))
except Exception:
    def _logC(n, r):
        if r < 0 or r > n: return -math.inf
        return math.lgamma(n + 1) - math.lgamma(r + 1) - math.lgamma(n - r + 1)
    def hyper_sf(k, N, K, n):
        # P(X>=k), X~Hypergeom(pop=N, successes=K, draws=n)
        lo, hi = max(0, n + K - N), min(K, n); tot = 0.0
        for x in range(k, hi + 1):
            tot += math.exp(_logC(K, x) + _logC(N - K, n - x) - _logC(N, n))
        return min(1.0, tot)

def candidates(mat, wt, mu):
    w = mat.reindex(columns=wt); m = mat.reindex(columns=mu)
    ok = (w.notna().sum(1) >= MIN_LINES) & (m.notna().sum(1) >= MIN_LINES)
    d = w.mean(1) - m.mean(1)
    return set(ok[ok].index), set((ok & passes_window(w.mean(1), m.mean(1))).pipe(lambda s: s[s]).index)

def token_match(target, text):
    if not isinstance(text, str) or not target: return False
    return re.search(rf"\b{re.escape(target)}\b", text, re.I) is not None

def main():
    here = os.path.dirname(os.path.abspath(__file__))
    ap = argparse.ArgumentParser()
    ap.add_argument("--reference", required=True)
    ap.add_argument("--derived", default=os.path.join(here, "..", "results"))
    ap.add_argument("--out", default=os.path.join(here, "results"))
    ap.add_argument("--perm", type=int, default=10000)
    ap.add_argument("--seed", type=int, default=20260811)
    a = ap.parse_args(); os.makedirs(a.out, exist_ok=True)
    rng = np.random.default_rng(a.seed)

    pairs = pd.read_csv(os.path.join(a.derived, "sprime_lung_pairs.csv")).dropna(subset=["name"])
    geno = pd.read_csv(os.path.join(a.derived, "lung_genotypes.csv")).set_index("ModelID")
    M = pairs.pivot_table(index="name", columns="depmap_id", values="sprime", aggfunc="mean")
    # compound -> annotation text (target + moa) for target-based resolution
    ann = (pairs.assign(txt=(pairs.get("target", "").fillna("") + " ; " + pairs.get("moa", "").fillna("")))
                .groupby("name").txt.apply(lambda s: " ; ".join(sorted(set(s)))).to_dict())

    ref = pd.read_csv(a.reference, comment="#")
    ref["genotype"] = ref["genotype"].astype(str).str.upper()

    print(f"Reference rows: {len(ref)} | PRISM lung compounds: {M.shape[0]}\n")
    print(f"{'gene':7}{'ref→univ':>10}{'candidates':>12}{'universe':>10}{'recovered':>11}{'recovery':>10}{'hyperg p':>11}{'perm p':>9}")
    rows = []; misses_all = {}
    for g in GENES:
        v = geno[g]
        wt = [c for c in M.columns if v.get(c) == 0]; mu = [c for c in M.columns if v.get(c) == 2]
        universe, cand = candidates(M, wt, mu)
        # resolve reference -> PRISM compounds in this genotype's universe
        resolved = set()
        for _, r in ref[ref.genotype == g].iterrows():
            comp = str(r.get("compound", "") or "").strip().lower()
            tgt = str(r.get("target", "") or "").strip()
            if comp:
                for nm in universe:
                    if nm.lower() == comp: resolved.add(nm)
            if tgt:
                for nm in universe:
                    if token_match(tgt, ann.get(nm, "")): resolved.add(nm)
        R = resolved & universe
        k = len(R & cand); nR = len(R); N = len(universe); K = len(cand)
        rec = k / nR if nR else float("nan")
        hp = hyper_sf(k, N, K, nR) if nR else float("nan")
        # permutation: draw K random 'candidates' from universe, overlap with R
        if nR and K:
            # sorted(), not list(): `universe` is a set of compound-name strings, and Python
            # randomizes str hashing per process, so list() order — and therefore which
            # compounds the seeded index draw maps to — changed on every run.
            uni = sorted(universe); overlaps = np.empty(a.perm)
            for i in range(a.perm):
                draw = set(rng.choice(len(uni), size=K, replace=False))
                overlaps[i] = len(R & {uni[j] for j in draw})
            pp = (np.sum(overlaps >= k) + 1) / (a.perm + 1)
        else:
            pp = float("nan")
        misses_all[g] = sorted(R - cand)
        rows.append(dict(gene=g, ref_in_universe=nR, candidates=K, universe=N, recovered=k,
                         recovery=rec, hyperg_p=hp, perm_p=pp, misses=";".join(sorted(R - cand))))
        rp = f"{rec:.0%}" if nR else "n/a"
        print(f"{g:7}{nR:>10}{K:>12}{N:>10}{k:>11}{rp:>10}{hp:>11.3g}{pp:>9.3g}")

    pd.DataFrame(rows).to_csv(os.path.join(a.out, "concordance_report.csv"), index=False)
    print("\nMISSES (reference compounds tested but NOT recovered — the informative rows):")
    for g in GENES:
        print(f"  {g:7}: {', '.join(misses_all[g]) if misses_all[g] else '(none)'}")
    print(f"\nwrote {a.out}/concordance_report.csv")
    print("NOTE: run on the reference set provided; expand/freeze the reference per the protocol before")
    print("      treating these numbers as a validation benchmark.")

if __name__ == "__main__":
    main()
