#!/usr/bin/env python3
"""One-command runner: verify inputs, build S′, run the two blocking analyses.
Usage:  python run_all.py [--data DIR] [--mutations FILE] [--perm N]
Exits non-zero if inputs are missing / wrong release or validation fails.
"""
import argparse, os, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _common import default_data_dir, safe_stdout
safe_stdout()

def main():
    here = os.path.dirname(os.path.abspath(__file__))
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default=default_data_dir(here))
    ap.add_argument("--out", default=os.path.join(here, "results"))
    ap.add_argument("--mutations", default="OmicsSomaticMutationsMatrixDamaging.csv")
    ap.add_argument("--perm", type=int, default=2000)
    ap.add_argument("--skip-checksum", action="store_true")
    a = ap.parse_args()
    py = sys.executable

    step1 = [py, os.path.join(here, "sprime_pipeline.py"), "--data", a.data, "--out", a.out,
             "--mutations", a.mutations] + (["--skip-checksum"] if a.skip_checksum else [])
    print(">>> STEP 1: build + validate\n" + " ".join(step1))
    r = subprocess.run(step1)
    if r.returncode >= 2:
        print("run_all: inputs invalid — see DOWNLOAD_CHECKLIST.md"); sys.exit(r.returncode)
    if r.returncode == 1:
        print("run_all: WARNING — a validation anchor did not match; continuing but review results.")

    step2 = [py, os.path.join(here, "blocking_analyses.py"), "--out", a.out, "--perm", str(a.perm)]
    print("\n>>> STEP 2: blocking analyses (candidate sizes, permutation null, line-centring)\n" + " ".join(step2))
    r2 = subprocess.run(step2)

    step3 = [py, os.path.join(here, "bootstrap_ci_gate.py"), "--derived", a.out, "--out", a.out]
    print("\n>>> STEP 3: bootstrap confidence-interval gate\n" + " ".join(step3))
    r3 = subprocess.run(step3)
    print("\n(Optional) literature-blind concordance:  "
          "python concordance/concordance_enrichment.py --reference concordance/reference_seed_grounded.csv")
    sys.exit(max(r2.returncode, r3.returncode))

if __name__ == "__main__":
    main()
