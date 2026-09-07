#!/usr/bin/env python3
"""Apply the pre-specified both-must-clear rule to two blinded censuses.

Implements §5 of `PRESPEC_second_census_2026-09-06.md`, which was committed before the second census
existed. Nothing here is a choice made after seeing a result; this file only executes the written rule.

    A genotype's claim stands only if it clears chance against BOTH censuses independently,
    hypergeometric p < alpha AND permutation p < alpha, in each census's primary directional
    analysis. No pooling. Symmetric: a genotype clearing only one census is a discordance, not a
    claim. For a genotype that clears both, the leave-one-class-out is repeated on each census and
    the claim is narrowed to the class or classes carrying it in BOTH; if the carrying class differs
    between censuses the claim is reported as unstable and is not made.

The window, the target resolution and the class construction are all imported, never re-implemented.

Usage:
    uv run --locked python concordance/compare_censuses.py

Exit codes: 0 = ok | 2 = missing input | 4 = scipy missing (raised by the engine import).
"""
import argparse, os, sys
import pandas as pd

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)
sys.path.insert(0, os.path.dirname(_HERE))
from build_suppl7_table1 import (robustness, load_matrix, cohort, need, GENES)   # noqa: E402
from _common import safe_stdout                                                  # noqa: E402

safe_stdout()


def load_census(path):
    df = pd.read_csv(need(path, "census"), comment="#")
    df["genotype"] = df["genotype"].astype(str).str.upper()
    return df


def carrying_classes(rob, alpha):
    """Classes whose removal pushes the enrichment to or above alpha — i.e. the ones carrying it."""
    out = {}
    for cls, dt, dr, kr, kk, kp in rob["classes"]:
        if kp >= alpha:
            out["+".join(cls)] = (dt, dr, kr, kk, kp)
    if rob.get("aurora") and rob["aurora"][4] >= alpha:
        at, ar, kr, kk, kp = rob["aurora"]
        out["AURKA+AURKB"] = (at, ar, kr, kk, kp)
    return out


def main():
    ap = argparse.ArgumentParser(description="Apply the pre-specified both-must-clear rule.")
    ap.add_argument("--census-a", default=os.path.join(_HERE, "reference_set_2026-08-31_directional.csv"))
    ap.add_argument("--census-b", default=os.path.join(_HERE, "reference_set_2026-09-06_directional.csv"))
    ap.add_argument("--results-a", default=os.path.join(_HERE, "results", "2026-08-31_blind",
                                                        "concordance_report_primary_directional.csv"))
    ap.add_argument("--results-b", default=os.path.join(_HERE, "results", "2026-09-06_census2",
                                                        "concordance_report_primary_directional.csv"))
    ap.add_argument("--label-a", default="2026-08-31")
    ap.add_argument("--label-b", default="2026-09-06")
    ap.add_argument("--alpha", type=float, default=0.05)
    ap.add_argument("--derived", default=os.path.join(os.path.dirname(_HERE), "results"))
    ap.add_argument("--out", default=os.path.join(_HERE, "results", "census_comparison.csv"))
    a = ap.parse_args()

    A, B = load_census(a.census_a), load_census(a.census_b)
    RA = pd.read_csv(need(a.results_a, "results A")).set_index("gene")
    RB = pd.read_csv(need(a.results_b, "results B")).set_index("gene")
    mat, geno, ann, ann_t = load_matrix(a.derived)

    print(f"Pre-specified rule: clears chance in BOTH censuses, hypergeometric AND permutation "
          f"p < {a.alpha:g}, no pooling.\n")
    print(f"{'gene':9}{'A ref':>7}{'A rec':>7}{'A hyp':>10}{'A perm':>9}"
          f"{'B ref':>7}{'B rec':>7}{'B hyp':>10}{'B perm':>9}  verdict")
    rows, claimable = [], []
    for g in GENES:
        ra, rb = RA.loc[g], RB.loc[g]
        ca = float(ra.hyperg_p) < a.alpha and float(ra.perm_p) < a.alpha
        cb = float(rb.hyperg_p) < a.alpha and float(rb.perm_p) < a.alpha
        verdict = ("CLAIMABLE" if ca and cb else
                   "discordant (A only)" if ca else
                   "discordant (B only)" if cb else
                   "concordant negative")
        if ca and cb:
            claimable.append(g)
        rows.append(dict(gene=g,
                         ref_a=int(ra.ref_in_universe), recovered_a=int(ra.recovered),
                         hyperg_p_a=float(ra.hyperg_p), perm_p_a=float(ra.perm_p), clears_a=ca,
                         ref_b=int(rb.ref_in_universe), recovered_b=int(rb.recovered),
                         hyperg_p_b=float(rb.hyperg_p), perm_p_b=float(rb.perm_p), clears_b=cb,
                         verdict=verdict))
        print(f"{g:9}{int(ra.ref_in_universe):>7}{int(ra.recovered):>7}{float(ra.hyperg_p):>10.3g}"
              f"{float(ra.perm_p):>9.3g}{int(rb.ref_in_universe):>7}{int(rb.recovered):>7}"
              f"{float(rb.hyperg_p):>10.3g}{float(rb.perm_p):>9.3g}  {verdict}")

    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    # canonical row order is GENES, matching every other reported CSV in the repo — not alphabetical
    out_df = pd.DataFrame(rows)
    out_df["gene"] = pd.Categorical(out_df["gene"], categories=GENES, ordered=True)
    out_df.sort_values("gene", kind="stable").to_csv(a.out, index=False, float_format="%.12g")
    print(f"\nwrote {a.out}")

    # ---- the narrowing step, for every genotype that cleared both ----
    for g in claimable:
        print(f"\n=== {g}: narrowing — which class carries the enrichment in each census? ===")
        universe, cand = cohort(mat, geno, g)
        rob_a = robustness(g, A, mat, geno, universe, cand, ann, ann_t, RA.reset_index())
        rob_b = robustness(g, B, mat, geno, universe, cand, ann, ann_t, RB.reset_index())
        ka, kb = carrying_classes(rob_a, a.alpha), carrying_classes(rob_b, a.alpha)
        for lab, k, rob in ((a.label_a, ka, rob_a), (a.label_b, kb, rob_b)):
            print(f"  {lab}: full {rob['full'][1]}/{rob['full'][0]} at p = {rob['full'][2]:.3g}")
            if not k:
                print("    no single class carries it — removing any one class leaves it significant")
            for name, (dt, dr, kr, kk, kp) in sorted(k.items(), key=lambda kv: -kv[1][4]):
                print(f"    removing {name:24} ({dt:3} tested, {dr} recovered) -> "
                      f"{kk}/{kr} at p = {kp:.3g}")
        shared = sorted(set(ka) & set(kb))
        print(f"  carrying in A: {sorted(ka) or 'none'}")
        print(f"  carrying in B: {sorted(kb) or 'none'}")
        if shared:
            print(f"  --> STABLE across both censuses: {shared}. Per the pre-specification the claim is "
                  f"narrowed to this class.")
        elif not ka and not kb:
            print("  --> no single class is load-bearing in either census; the claim need not be narrowed.")
        else:
            print("  --> UNSTABLE: the carrying class differs between censuses. Per the "
                  "pre-specification the claim is reported as unstable and is NOT made.")


if __name__ == "__main__":
    main()
