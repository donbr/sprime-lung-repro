"""Figures quoted in docs/ must match the committed results CSVs.

Runs in CI: every CSV read here is committed, so no gated DepMap/PRISM input is
needed. If a results table is regenerated, the formatted string changes and the
assertion fails until the prose is updated. This is the documentation analogue
of test_sprime_worked_example freezing the 6.704 anchor.
"""
import os
import sys
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)


def _read(rel_path):
    """Read a committed results CSV by repo-relative path."""
    return pd.read_csv(os.path.join(ROOT, rel_path))


def _doc(name):
    """Read a file from docs/ as text."""
    with open(os.path.join(ROOT, "docs", name), encoding="utf-8") as f:
        return f.read()


def _assert_in(text, needle, doc_name, source):
    assert needle in text, (
        f"docs/{doc_name} does not contain {needle!r}, which is derived from "
        f"{source}. The committed results changed, or the prose drifted — "
        f"update the document to match."
    )


def test_method_states_computed_cohort_sizes():
    """method.md must quote the cohorts the code actually produces."""
    g = _read("results/lung_genotypes.csv").set_index("ModelID")
    doc = _doc("method.md")
    for gene in ("PTEN", "CDKN2A", "RB1", "TP53"):
        v = g[gene]
        n_wt = int((v == 0).sum())
        n_mut = int((v == 2).sum())
        _assert_in(doc, f"| {gene} | {n_wt} | {n_mut} |", "method.md",
                   "results/lung_genotypes.csv")


def test_method_states_line_count():
    """The analyzed line count is a headline figure and must be current."""
    g = _read("results/lung_genotypes.csv")
    _assert_in(_doc("method.md"), f"{len(g)} lung", "method.md",
               "results/lung_genotypes.csv row count")


def test_evidence_permutation_null_table():
    """The permutation-null row for each genotype must match candidate_null.csv."""
    df = _read("results/candidate_null.csv")
    doc = _doc("evidence.md")
    for r in df.itertuples():
        row = (f"| {r.gene} | {int(r.candidates)} | {r.null_mean:.1f} | "
               f"{r.emp_p:.3f} | {r.perm_fdr:.2f} |")
        _assert_in(doc, row, "evidence.md", "results/candidate_null.csv")


def test_evidence_line_centring_table():
    """The line-centring row for each genotype must match line_centring.csv."""
    df = _read("results/line_centring.csv")
    doc = _doc("evidence.md")
    for r in df.itertuples():
        row = (f"| {r.gene} | {r.offset_mut_minus_wt:+.2f} | {int(r.raw)} | "
               f"{int(r.centred)} | {r.corr_dps:.3f} |")
        _assert_in(doc, row, "evidence.md", "results/line_centring.csv")


def test_evidence_bootstrap_table():
    """The bootstrap survivor row for each genotype must match the summary CSV."""
    df = _read("results/bootstrap_ci_summary.csv")
    doc = _doc("evidence.md")
    for r in df.itertuples():
        row = (f"| {r.gene} | {int(r.point)} | {int(r.ci_excl0)} | "
               f"{int(r.ci_le_minus2)} |")
        _assert_in(doc, row, "evidence.md", "results/bootstrap_ci_summary.csv")


def test_evidence_concordance_table():
    """Concordance rows must match; genotypes with an empty reference are skipped."""
    df = _read("concordance/results/concordance_report.csv")
    doc = _doc("evidence.md")
    for r in df.itertuples():
        if int(r.ref_in_universe) == 0:
            continue
        row = (f"| {r.gene} | {int(r.ref_in_universe)} | {int(r.recovered)} | "
               f"{r.hyperg_p:.2g} |")
        _assert_in(doc, row, "evidence.md",
                   "concordance/results/concordance_report.csv")


if __name__ == "__main__":
    failures = 0
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
                print("ok", name)
            except AssertionError as e:
                failures += 1
                print("FAIL", name, "\n ", e)
    if failures:
        sys.exit(1)
    print("ALL PASSED")
