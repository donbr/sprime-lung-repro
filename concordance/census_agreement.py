#!/usr/bin/env python3
"""Agreement between two blinded census assemblies.

Implements §6 of `PRESPEC_second_census_2026-09-06.md`, which requires these measures to be
reported whatever the enrichment results show. Two censuses built by the same procedure from the
same criteria should agree; how much they actually agree says whether the census or the S′ window
is the noisy component of the benchmark.

Reported per genotype, at two levels:

  target level    — the unit a curator actually decides on. Jaccard over the set of HGNC targets.
  compound level  — the unit the enrichment actually scores, after each target is expanded to the
                    PRISM compounds annotated to it and restricted to the tested universe. Two
                    censuses can name different targets and still resolve to overlapping compounds
                    (or name the same target and resolve to different ones), so neither level
                    substitutes for the other.

The window and the target→compound resolution are imported from the engine, never re-implemented.

Usage:
    uv run --locked python concordance/census_agreement.py \
        --census-a concordance/reference_set_2026-08-31_directional.csv \
        --census-b concordance/reference_set_2026-09-06_directional.csv

Exit codes: 0 = ok | 2 = missing input | 4 = scipy missing (raised by the engine import).
"""
import argparse, os, sys
import pandas as pd

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)
sys.path.insert(0, os.path.dirname(_HERE))
from concordance_enrichment import candidates, token_match     # noqa: E402
from _common import safe_stdout                                # noqa: E402

safe_stdout()

GENES = ["PTEN", "CDKN2A", "RB1", "TP53"]


def need(path, what):
    if not os.path.exists(path):
        print(f"ERROR: missing {what}: {path}")
        if path.endswith("sprime_lung_pairs.csv"):
            print("  Gitignored (~18 MB). Regenerate with:\n"
                  "    uv run --locked python fetch_data.py\n"
                  "    uv run --locked python sprime_pipeline.py")
        sys.exit(2)
    return path


def jaccard(a, b):
    return len(a & b) / len(a | b) if (a or b) else float("nan")


def load_census(path):
    df = pd.read_csv(need(path, "census"), comment="#")
    df["genotype"] = df["genotype"].astype(str).str.upper()
    return df


def targets_of(df, gene):
    """Set of HGNC targets a census names for one genotype, ignoring the citation behind them."""
    sub = df[df.genotype == gene]
    return {str(t).strip() for t in sub.get("target", pd.Series(dtype=str)).fillna("") if str(t).strip()}


def resolve(df, gene, universe, ann):
    """PRISM compounds the census resolves to — the engine's own rule, name match or target token."""
    hits = set()
    for _, r in df[df.genotype == gene].iterrows():
        comp = str(r.get("compound", "") or "").strip().lower()
        tgt = str(r.get("target", "") or "").strip()
        hits |= {n for n in universe
                 if (comp and n.lower() == comp) or (tgt and token_match(tgt, ann.get(n, "")))}
    return hits


def main():
    ap = argparse.ArgumentParser(description="Agreement between two blinded census assemblies.")
    ap.add_argument("--census-a", default=os.path.join(_HERE, "reference_set_2026-08-31_directional.csv"))
    ap.add_argument("--census-b", default=os.path.join(_HERE, "reference_set_2026-09-06_directional.csv"))
    ap.add_argument("--label-a", default="2026-08-31")
    ap.add_argument("--label-b", default="2026-09-06")
    ap.add_argument("--derived", default=os.path.join(os.path.dirname(_HERE), "results"))
    ap.add_argument("--out", default=os.path.join(_HERE, "results", "census_agreement.csv"))
    a = ap.parse_args()

    A, B = load_census(a.census_a), load_census(a.census_b)

    pairs = pd.read_csv(need(os.path.join(a.derived, "sprime_lung_pairs.csv"), "derived pairs table")
                        ).dropna(subset=["name"])
    geno = pd.read_csv(need(os.path.join(a.derived, "lung_genotypes.csv"), "derived genotype table")
                       ).set_index("ModelID")
    mat = pairs.pivot_table(index="name", columns="depmap_id", values="sprime", aggfunc="mean")
    ann = (pairs.assign(txt=(pairs.get("target", "").fillna("") + " ; " + pairs.get("moa", "").fillna("")))
                .groupby("name").txt.apply(lambda s: " ; ".join(sorted(set(s)))).to_dict())

    print(f"census A ({a.label_a}): {len(A)} rows | census B ({a.label_b}): {len(B)} rows\n")
    print(f"{'gene':8}{'tgtA':>6}{'tgtB':>6}{'both':>6}{'J_tgt':>8}"
          f"{'cmpA':>7}{'cmpB':>7}{'both':>6}{'J_cmp':>8}")
    rows = []
    for g in GENES:
        ta, tb = targets_of(A, g), targets_of(B, g)
        v = geno[g]
        wt = [c for c in mat.columns if v.get(c) == 0]
        mu = [c for c in mat.columns if v.get(c) == 2]
        universe, _ = candidates(mat, wt, mu)
        ca, cb = resolve(A, g, universe, ann), resolve(B, g, universe, ann)
        rows.append(dict(
            gene=g,
            rows_a=int((A.genotype == g).sum()), rows_b=int((B.genotype == g).sum()),
            targets_a=len(ta), targets_b=len(tb), targets_shared=len(ta & tb),
            targets_only_a=";".join(sorted(ta - tb)), targets_only_b=";".join(sorted(tb - ta)),
            jaccard_targets=jaccard(ta, tb),
            compounds_a=len(ca), compounds_b=len(cb), compounds_shared=len(ca & cb),
            jaccard_compounds=jaccard(ca, cb),
        ))
        print(f"{g:8}{len(ta):>6}{len(tb):>6}{len(ta & tb):>6}{jaccard(ta, tb):>8.3f}"
              f"{len(ca):>7}{len(cb):>7}{len(ca & cb):>6}{jaccard(ca, cb):>8.3f}")

    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    (pd.DataFrame(rows)
       .sort_values("gene", kind="stable")
       .to_csv(a.out, index=False, float_format="%.12g"))
    print(f"\nwrote {a.out}")
    print("\nRead low agreement as a finding about the census, not about the window: it would mean a\n"
          "single census is too thin an instrument to validate against.")


if __name__ == "__main__":
    main()
