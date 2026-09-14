#!/usr/bin/env python3
"""Assemble a frozen census from per-genotype agent output — verbatim.

The verbatim-assembly rule is what makes structural blinding work: no row may be added, removed,
reworded or reordered on the basis of anything known about the results. Doing the assembly in a
script rather than by hand is what makes that rule auditable — this file is the complete list of
transformations applied between what the agents produced and what gets frozen.

The ONLY transformations are:

  1. concatenation of the per-genotype files in a fixed genotype order (never a results-dependent one);
  2. the directional split — rows whose inclusion_rationale begins with the token INVERSE-DIRECTION
     are dropped from the primary census and kept in the full one. That flag is written by the agent
     at authoring time, before any result exists, so the exclusion is not a post-hoc choice.

No filtering on target, compound, journal, year or plausibility. No de-duplication. No reordering
within a genotype. If a row looks wrong, it stays and the objection goes in the notes.

Usage:
    uv run --locked python concordance/assemble_census.py --raw concordance/census_2026-09-06_raw \
        --out-full concordance/reference_set_2026-09-06.csv \
        --out-directional concordance/reference_set_2026-09-06_directional.csv

Exit codes: 0 = ok | 2 = missing or malformed input.
"""
import argparse, csv, hashlib, os, sys

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(_HERE))
from _common import safe_stdout          # noqa: E402

safe_stdout()

GENES = ["PTEN", "CDKN2A", "RB1", "TP53"]      # fixed order, chosen before any census existed
COLUMNS = ["genotype", "target", "compound", "pmid", "doi",
           "source_db", "search_terms", "date_frozen", "inclusion_rationale"]
INVERSE = "INVERSE-DIRECTION"


def md5_of(path, chunk=1 << 20):
    h = hashlib.md5()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(chunk), b""):
            h.update(b)
    return h.hexdigest()


def read_one(path, gene):
    if not os.path.exists(path):
        print(f"ERROR: missing per-genotype census file: {path}")
        sys.exit(2)
    # utf-8-sig: a BOM on an agent-produced file would otherwise turn the first header into
    # "\ufeffgenotype" and surface as a baffling column mismatch.
    # restkey/restval: a row with MORE fields than the header would otherwise smuggle the extra value
    # through validation under the None key and explode inside the writer, after a partial write.
    with open(path, encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f, restkey="__extra__", restval=None))
    if not rows:
        print(f"ERROR: {path} has no data rows")
        sys.exit(2)
    for i, r in enumerate(rows, start=2):
        if "__extra__" in r:
            print(f"ERROR: {path} line {i}: more fields than the header ({r['__extra__']!r} left over)")
            sys.exit(2)
        if sorted(r) != sorted(COLUMNS):
            print(f"ERROR: {path} line {i}: columns {sorted(r)} != {sorted(COLUMNS)}")
            sys.exit(2)
        missing = [c for c in COLUMNS if r[c] is None]
        if missing:
            print(f"ERROR: {path} line {i}: fewer fields than the header (missing {missing})")
            sys.exit(2)
        if r["genotype"].strip().upper() != gene:
            print(f"ERROR: {path} line {i}: genotype {r['genotype']!r} != {gene}")
            sys.exit(2)
        if not r["pmid"].strip() and not r["doi"].strip():
            print(f"ERROR: {path} line {i}: neither PMID nor DOI — the protocol makes one mandatory")
            sys.exit(2)
        if not r["search_terms"].strip():
            print(f"ERROR: {path} line {i}: empty search_terms — mandatory on every row")
            sys.exit(2)
        if not r["inclusion_rationale"].strip():
            print(f"ERROR: {path} line {i}: empty inclusion_rationale — mandatory on every row")
            sys.exit(2)
    return rows


def write_census(path, rows):
    # newline="" for the csv module; LF endings so the md5 is platform-independent (.gitattributes
    # also marks these files -text, so git never rewrites them either)
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLUMNS, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)


def main():
    ap = argparse.ArgumentParser(description="Assemble a frozen census from per-genotype agent output.")
    ap.add_argument("--raw", default=os.path.join(_HERE, "census_2026-09-06_raw"))
    ap.add_argument("--out-full", default=os.path.join(_HERE, "reference_set_2026-09-06.csv"))
    ap.add_argument("--out-directional",
                    default=os.path.join(_HERE, "reference_set_2026-09-06_directional.csv"))
    a = ap.parse_args()

    full, directional = [], []
    print(f"{'gene':9}{'rows':>6}{'inverse':>9}{'primary':>9}")
    for g in GENES:
        rows = read_one(os.path.join(a.raw, f"{g}.csv"), g)
        inv = [r for r in rows if r["inclusion_rationale"].lstrip().startswith(INVERSE)]
        keep = [r for r in rows if not r["inclusion_rationale"].lstrip().startswith(INVERSE)]
        full.extend(rows)          # order within a genotype is the agent's own, untouched
        directional.extend(keep)
        print(f"{g:9}{len(rows):>6}{len(inv):>9}{len(keep):>9}")

    # Both censuses are validated and fully built before ANYTHING is written, and each is written to a
    # temporary file and then os.replace()d into position — the same discipline fetch_data.py uses. A
    # half-written frozen census is the worst artifact this script could produce, since its whole purpose
    # is an auditable, hashed file.
    for path, rows_out in ((a.out_full, full), (a.out_directional, directional)):
        tmp = path + ".part"
        write_census(tmp, rows_out)
        os.replace(tmp, path)
    print(f"\n{'':9}{len(full):>6}{len(full) - len(directional):>9}{len(directional):>9}   TOTAL")
    for p in (a.out_full, a.out_directional):
        print(f"  {md5_of(p)}  {os.path.basename(p)}  ({sum(1 for _ in open(p, encoding='utf-8')) - 1} rows)")
    print("\nFreeze these hashes in the commit message, then commit BEFORE running the enrichment engine.")


if __name__ == "__main__":
    main()
