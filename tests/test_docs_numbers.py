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
