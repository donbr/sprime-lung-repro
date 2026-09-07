#!/usr/bin/env python3
"""Apply the pre-specified both-must-clear rule to two blinded censuses, and diagnose what it means.

Implements §5 of `PRESPEC_second_census_2026-09-06.md`, committed before the second census existed.
The gate itself is only what the pre-specification says:

    A genotype's claim stands only if it clears chance against BOTH censuses separately,
    hypergeometric p < alpha AND permutation p < alpha, in each census's primary directional
    analysis. No pooling. Symmetric.

Everything else this script computes exists because the gate alone is easy to over-read. In
particular:

  * **Reference nesting.** If census B's resolved reference set is a subset of census A's, then B's
    recovered set is forced to be a subset of A's, because both are intersected with the SAME fixed
    candidate set from the SAME drug-response data. Under nesting, "the two censuses recovered the
    same compounds" is arithmetic, not corroboration, and a smaller p in B may come entirely from a
    smaller denominator. This script measures the nesting so the reader is not left to assume
    independence that does not exist.

  * **Carrying class, two ways.** The leave-one-out heuristic asks whether removing a class pushes p
    above alpha. That conflates losing the effect with losing sample size. A class-versus-remainder
    Fisher test asks the better-posed question — is the class's recovery RATE higher than the rest of
    the reference set's — and is reported next to it.

  * **Bonferroni** across the four genotypes, for each census, which §5 of the pre-specification asks
    for and which the first version of this script did not emit.

The window, the target resolution and the class construction are all imported, never re-implemented.

Usage:
    uv run --locked python concordance/compare_censuses.py

Exit codes: 0 = ok | 2 = missing input | 4 = scipy missing (raised by the engine import).
"""
import argparse, os, sys
import pandas as pd
from scipy.stats import fisher_exact

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)
sys.path.insert(0, os.path.dirname(_HERE))
from build_suppl7_table1 import (robustness, resolve_by_target, load_matrix, cohort,
                                 need, GENES)                                     # noqa: E402
from _common import safe_stdout                                                   # noqa: E402

safe_stdout()


def load_census(path):
    df = pd.read_csv(need(path, "census"), comment="#")
    df["genotype"] = df["genotype"].astype(str).str.upper()
    return df


def carrying_classes(rob, alpha):
    """Classes whose removal pushes the enrichment to or above alpha.

    NOTE this mixes two different units. `rob["classes"]` is the COMPUTED overlap-closed partition;
    `rob["aurora"]` is a single CURATED pair named explicitly in the pre-specification. They are
    reported separately by the caller precisely because they can disagree, and did.
    """
    computed = {}
    for cls, dt, dr, kr, kk, kp in rob["classes"]:
        if kp >= alpha:
            computed["+".join(cls)] = (dt, dr, kr, kk, kp)
    curated = {}
    if rob.get("aurora") and rob["aurora"][4] >= alpha:
        at, ar, kr, kk, kp = rob["aurora"]
        curated["AURKA+AURKB"] = (at, ar, kr, kk, kp)
    return computed, curated


def rate_test(class_set, ref_set, cand):
    """Class-versus-remainder recovery rate, one-sided Fisher.

    Asks whether the class recovers at a HIGHER RATE than the rest of the reference set, which is
    the question 'does this class carry the enrichment' actually poses. The leave-one-out p-value
    cannot separate that from the power lost by shrinking the reference set.
    """
    rest = ref_set - class_set
    a, b = len(class_set & cand), len(class_set) - len(class_set & cand)
    c, d = len(rest & cand), len(rest) - len(rest & cand)
    p = float(fisher_exact([[a, b], [c, d]], alternative="greater")[1]) if (a + b and c + d) else float("nan")
    return a, len(class_set), c, len(rest), p


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
    ap.add_argument("--out-robustness-b", default=os.path.join(_HERE, "results", "2026-09-06_census2",
                                                               "robustness_RB1.csv"))
    a = ap.parse_args()

    A, B = load_census(a.census_a), load_census(a.census_b)
    RA = pd.read_csv(need(a.results_a, "results A")).set_index("gene")
    RB = pd.read_csv(need(a.results_b, "results B")).set_index("gene")
    mat, geno, ann, ann_t = load_matrix(a.derived)
    nG = len(GENES)

    print(f"Pre-specified rule: clears chance in BOTH censuses (separately, no pooling), "
          f"hypergeometric AND permutation p < {a.alpha:g}.\n")
    print(f"{'gene':9}{'A rec/ref':>12}{'A hyp':>10}{'B rec/ref':>12}{'B hyp':>11}"
          f"{'B ref ⊆ A':>11}  verdict")
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

        # reference nesting — the diagnostic that says how much B adds over A
        universe, cand = cohort(mat, geno, g)
        pa = resolve_by_target(A, g, universe, ann)
        pb = resolve_by_target(B, g, universe, ann)
        refA = set().union(*pa.values()) if pa else set()
        refB = set().union(*pb.values()) if pb else set()
        nested = refB <= refA
        a_only, b_only = refA - refB, refB - refA

        rows.append(dict(gene=g,
                         ref_a=int(ra.ref_in_universe), recovered_a=int(ra.recovered),
                         hyperg_p_a=float(ra.hyperg_p), perm_p_a=float(ra.perm_p),
                         bonferroni_p_a=min(1.0, float(ra.hyperg_p) * nG), clears_a=ca,
                         ref_b=int(rb.ref_in_universe), recovered_b=int(rb.recovered),
                         hyperg_p_b=float(rb.hyperg_p), perm_p_b=float(rb.perm_p),
                         bonferroni_p_b=min(1.0, float(rb.hyperg_p) * nG), clears_b=cb,
                         ref_shared=len(refA & refB),
                         ref_only_a=len(a_only), ref_only_a_recovered=len(a_only & cand),
                         ref_only_b=len(b_only), ref_only_b_recovered=len(b_only & cand),
                         ref_b_subset_of_a=nested,
                         recovered_sets_identical=(refA & cand) == (refB & cand),
                         verdict=verdict, narrowed_to="", narrowing_stable=""))
        print(f"{g:9}{f'{int(ra.recovered)}/{int(ra.ref_in_universe)}':>12}{float(ra.hyperg_p):>10.3g}"
              f"{f'{int(rb.recovered)}/{int(rb.ref_in_universe)}':>12}{float(rb.hyperg_p):>11.3g}"
              f"{str(nested):>11}  {verdict}")

    by_gene = {r["gene"]: r for r in rows}

    # ---- narrowing, for every genotype that cleared both ----
    for g in claimable:
        print(f"\n=== {g}: narrowing — which class carries the enrichment, and does that replicate? ===")
        universe, cand = cohort(mat, geno, g)
        rob_a = robustness(g, A, mat, geno, universe, cand, ann, ann_t, RA.reset_index())
        rob_b = robustness(g, B, mat, geno, universe, cand, ann, ann_t, RB.reset_index())
        pa = resolve_by_target(A, g, universe, ann)
        pb = resolve_by_target(B, g, universe, ann)
        refA = set().union(*pa.values()); refB = set().union(*pb.values())

        comp_a, cur_a = carrying_classes(rob_a, a.alpha)
        comp_b, cur_b = carrying_classes(rob_b, a.alpha)
        print(f"  computed overlap-closed classes carrying it — {a.label_a}: {sorted(comp_a) or 'none'}")
        print(f"                                                {a.label_b}: {sorted(comp_b) or 'none'}")
        shared_computed = sorted(set(comp_a) & set(comp_b))
        print(f"  intersection of COMPUTED classes: {shared_computed or 'EMPTY'}")
        shared_curated = sorted(set(cur_a) & set(cur_b))
        print(f"  pre-named curated pair carrying it in both: {shared_curated or 'none'}")

        # the better-posed question: does the class recover at a higher RATE than the remainder?
        if {"AURKA", "AURKB"} <= set(pa) and {"AURKA", "AURKB"} <= set(pb):
            for lab, per, ref in ((a.label_a, pa, refA), (a.label_b, pb, refB)):
                cls = per["AURKA"] | per["AURKB"]
                k, n, kr, nr, p = rate_test(cls, ref, cand)
                flag = "" if p < a.alpha else "   <-- does NOT clear alpha"
                print(f"  {lab}: Aurora {k}/{n} vs remainder {kr}/{nr}, one-sided Fisher p = {p:.3g}{flag}")

        if shared_computed:
            by_gene[g]["narrowed_to"] = ";".join(shared_computed)
            by_gene[g]["narrowing_stable"] = "computed"
        elif shared_curated:
            by_gene[g]["narrowed_to"] = ";".join(shared_curated)
            by_gene[g]["narrowing_stable"] = "curated-pair-only"
            print("  NOTE: the COMPUTED classes differ between censuses; stability holds only for the "
                  "pre-named AURKA+AURKB pair. Report this, do not present it as computed stability.")
        else:
            by_gene[g]["narrowing_stable"] = "unstable"
            print("  UNSTABLE: no class carries it in both. Per the pre-specification the claim is "
                  "reported as unstable and is NOT made.")

        if g == "RB1":
            recs = [dict(analysis="full", removed="", tested_removed=0, recovered_removed=0,
                         ref_left=rob_b["full"][0], recovered_left=rob_b["full"][1],
                         hyperg_p=rob_b["full"][2])]
            for cls, dt, dr, kr, kk, kp in rob_b["classes"]:
                recs.append(dict(analysis="drop_class", removed="+".join(cls), tested_removed=dt,
                                 recovered_removed=dr, ref_left=kr, recovered_left=kk, hyperg_p=kp))
            if rob_b.get("aurora"):
                at, ar, kr, kk, kp = rob_b["aurora"]
                recs.append(dict(analysis="drop_aurora_pair", removed="AURKA+AURKB", tested_removed=at,
                                 recovered_removed=ar, ref_left=kr, recovered_left=kk, hyperg_p=kp))
            os.makedirs(os.path.dirname(a.out_robustness_b), exist_ok=True)
            (pd.DataFrame(recs).sort_values(["analysis", "removed"], kind="stable")
               .to_csv(a.out_robustness_b, index=False, float_format="%.12g", lineterminator="\n"))
            print(f"  wrote {a.out_robustness_b}")

    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    # canonical row order is GENES, matching every other reported CSV in the repo — not alphabetical
    out_df = pd.DataFrame(rows)
    out_df["gene"] = pd.Categorical(out_df["gene"], categories=GENES, ordered=True)
    out_df.sort_values("gene", kind="stable").to_csv(a.out, index=False, float_format="%.12g", lineterminator="\n")
    print(f"\nwrote {a.out}")


if __name__ == "__main__":
    main()
