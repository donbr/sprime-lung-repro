#!/usr/bin/env python3
"""S′ pipeline (build + validate) on PRISM 19Q4 SSDRC + DepMap damaging mutations.

Verifies inputs by md5, computes S′ per compound-cell-line pair for lung lines, genotype-calls
PTEN/CDKN2A/RB1/TP53 from the damaging-mutation matrix, validates against the worked example and the
reported cohort sizes, and writes derived tables to results/. Configurable, portable, checksum-guarded.

Usage:  python sprime_pipeline.py [--data DIR] [--out DIR] [--mutations FILENAME]
Default --data is ./data_sources, falling back to ../data_sources (see DOWNLOAD_CHECKLIST.md).
"""
import argparse, hashlib, os, sys
import numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sprime_core

GENES = {"PTEN": "PTEN (5728)", "CDKN2A": "CDKN2A (1029)", "RB1": "RB1 (5925)", "TP53": "TP53 (7157)"}
PRISM_FILE = "secondary-screen-dose-response-curve-parameters.csv"
MD5 = {
    "prism":      "e629b9d505ad3d6bf65fde96f1c54bee",   # PRISM 19Q4 secondary screen
    "mut_24q2":   "02f3568b71af0ca3e8d10e681eefac86",   # DepMap 24Q2 damaging mutations
    "mut_24q4":   "cb20fdbe1cf3b9b0d8ed4f53e1f399b6",   # DepMap 24Q4 (identical calls on analyzed genes)
}
EXPECTED_COHORTS = {"PTEN": (90, 3), "CDKN2A": (80, 13), "RB1": (84, 8), "TP53": (18, 72)}  # Suppl 9 (WT, mut)
MIN_LINES = 3

def md5(path, chunk=1 << 20):
    h = hashlib.md5()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(chunk), b""):
            h.update(b)
    return h.hexdigest()

def log(*a): print(*a, flush=True)

def default_data_dir(here):
    """data_sources/ inside the repo (where fetch_data.py writes); else the sibling layout."""
    inside = os.path.join(here, "data_sources")
    sibling = os.path.join(here, "..", "data_sources")
    return sibling if not os.path.isdir(inside) and os.path.isdir(sibling) else inside

def main():
    ap = argparse.ArgumentParser()
    here = os.path.dirname(os.path.abspath(__file__))
    ap.add_argument("--data", default=default_data_dir(here))
    ap.add_argument("--out", default=os.path.join(here, "results"))
    ap.add_argument("--mutations", default="OmicsSomaticMutationsMatrixDamaging.csv")
    ap.add_argument("--skip-checksum", action="store_true")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    prism = os.path.join(a.data, PRISM_FILE)
    mutf = os.path.join(a.data, a.mutations)

    # ---- guard: files present + correct release ----
    for f in (prism, mutf):
        if not os.path.exists(f):
            log(f"ERROR: missing input {f}\n  See DOWNLOAD_CHECKLIST.md."); sys.exit(2)
    if not a.skip_checksum:
        pm = md5(prism)
        if pm != MD5["prism"]:
            log(f"ERROR: PRISM md5 {pm} != expected {MD5['prism']} (wrong file/release)."); sys.exit(3)
        mm = md5(mutf)
        release = {MD5["mut_24q2"]: "24Q2", MD5["mut_24q4"]: "24Q4"}.get(mm)
        if release is None:
            log(f"ERROR: mutation matrix md5 {mm} matches neither 24Q2 nor 24Q4."); sys.exit(3)
        log(f"Inputs verified. Mutation release detected: DepMap Public {release}"
            + ("  (NOTE: manuscript should cite this release)" if release == "24Q4" else ""))
    else:
        log("Checksum verification skipped (--skip-checksum).")

    # ---- load PRISM, preprocess ----
    log("Loading PRISM SSDRC ...")
    cols = ["depmap_id", "ccle_name", "screen_id", "upper_limit", "lower_limit",
            "ec50", "ic50", "auc", "name", "moa", "target", "passed_str_profiling"]
    p = pd.read_csv(prism, usecols=cols, low_memory=False)
    p["tissue"] = p.ccle_name.str.split("_", n=1).str[1]
    lung = p[p.tissue == "LUNG"].copy()
    lung = lung[lung.passed_str_profiling.astype(str).str.upper().isin(["TRUE", "1", "1.0"])]
    lung = lung[lung.screen_id.isin(["HTS002", "MTS010"])].copy()
    lung["rk"] = (lung.screen_id == "MTS010").astype(int)     # prefer MTS010 in the overlay
    lung = lung.sort_values("rk").drop_duplicates(["depmap_id", "name"], keep="last")
    emax_pct = (lung.upper_limit - lung.lower_limit) * 100.0   # signed; inhibition>0
    lung["sprime"] = sprime_core.sprime(emax_pct.to_numpy(), lung.ec50.to_numpy())   # canonical S′ definition
    log(f"  {lung.depmap_id.nunique()} lung lines, {len(lung)} compound-line pairs (HTS002+MTS010 overlay)")

    # ---- validation anchor: doxorubicin / A549 ~ 6.70 ----
    dox = lung[(lung.name.str.lower() == "doxorubicin") & (lung.ccle_name.str.startswith("A549"))]
    val_ok = True
    if len(dox):
        sv = float(dox.iloc[0].sprime)
        ok = abs(sv - 6.70) < 0.1
        val_ok &= ok
        log(f"  VALIDATION doxorubicin/A549 S' = {sv:.4f}  (expect ~6.70)  {'PASS' if ok else 'FAIL'}")
    else:
        log("  WARN: doxorubicin/A549 not found for validation")

    # ---- genotype calls ----
    idc = pd.read_csv(mutf, nrows=0).columns[0]
    mut = pd.read_csv(mutf, usecols=[idc] + list(GENES.values()))
    mut = mut.rename(columns={idc: "ModelID", **{v: k for k, v in GENES.items()}})
    lines = lung[["depmap_id"]].drop_duplicates().rename(columns={"depmap_id": "ModelID"})
    g = lines.merge(mut, on="ModelID", how="left")
    log("  Cohort sizes (value2=mutant, value0=WT, value1=excluded):")
    for gene in GENES:
        v = g[gene]; nWT = int((v == 0).sum()); nMUT = int((v == 2).sum())
        ew, em = EXPECTED_COHORTS[gene]
        near = abs(nWT - ew) <= 3 and abs(nMUT - em) <= 2
        log(f"    {gene:7} WT={nWT:3d} mut={nMUT:3d}  [Suppl9 {ew}/{em}]  {'ok' if near else 'CHECK'}")

    # ---- write derived tables ----
    keepcols = ["depmap_id", "ccle_name", "name", "moa", "target",
                "upper_limit", "lower_limit", "ec50", "auc", "sprime"]
    lung[[c for c in keepcols if c in lung.columns]] \
        .to_csv(os.path.join(a.out, "sprime_lung_pairs.csv"), index=False)
    g.to_csv(os.path.join(a.out, "lung_genotypes.csv"), index=False)
    log(f"  wrote {a.out}/sprime_lung_pairs.csv and lung_genotypes.csv")
    sys.exit(0 if val_ok else 1)

if __name__ == "__main__":
    main()
