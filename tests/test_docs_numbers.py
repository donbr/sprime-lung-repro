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
sys.path.insert(0, ROOT)
from _common import safe_stdout
safe_stdout()

GENES = ["PTEN", "CDKN2A", "RB1", "TP53"]


def _read(rel_path):
    """Read a committed results CSV by repo-relative path."""
    return pd.read_csv(os.path.join(ROOT, rel_path))


def _doc(rel_path):
    """Read a file by repo-relative path (e.g. 'docs/method.md', 'README.md')."""
    with open(os.path.join(ROOT, rel_path), encoding="utf-8") as f:
        return f.read()


def _assert_in(text, needle, doc_path, source):
    assert needle in text, (
        f"{doc_path} does not contain {needle!r}, which is derived from "
        f"{source}. The committed results changed, or the prose drifted — "
        f"update the document to match."
    )


def _assert_one_row_per_gene(df, source):
    """Guard the converse direction: a shrunken CSV must not pass vacuously.

    Every row-by-row check below iterates the CSV, so a CSV that lost rows (or
    is empty) would assert nothing at all and leave a stale phantom row in the
    prose forever. Pin the shape first.
    """
    assert list(df.gene) == GENES, (
        f"{source} holds gene rows {list(df.gene)}, expected exactly {GENES}. "
        f"The committed results changed shape, so the row-by-row checks below "
        f"can no longer prove the document is current — regenerate or fix "
        f"{source} before trusting the docs."
    )


def _table_rows_after(text, heading, doc_path):
    """Data rows of the first markdown table following `heading`."""
    assert heading in text, f"{doc_path} has no {heading!r} section."
    lines, started = [], False
    for line in text.split(heading, 1)[1].splitlines():
        if line.startswith("|"):
            started = True
            lines.append(line)
        elif started:
            break
    assert len(lines) >= 2, (
        f"{doc_path} has no markdown table under {heading!r}."
    )
    return lines[2:]  # drop the header row and the |---|---| separator


def test_method_states_computed_cohort_sizes():
    """method.md must quote the cohorts the code actually produces."""
    g = _read("results/lung_genotypes.csv").set_index("ModelID")
    doc = _doc("docs/method.md")
    for gene in ("PTEN", "CDKN2A", "RB1", "TP53"):
        v = g[gene]
        n_wt = int((v == 0).sum())
        n_mut = int((v == 2).sum())
        _assert_in(doc, f"| {gene} | {n_wt} | {n_mut} |", "docs/method.md",
                   "results/lung_genotypes.csv")


def test_method_states_line_count():
    """The analyzed line count is a headline figure and must be current."""
    g = _read("results/lung_genotypes.csv")
    _assert_in(_doc("docs/method.md"), f"{len(g)} lung", "docs/method.md",
               "results/lung_genotypes.csv row count")


def test_evidence_permutation_null_table():
    """The permutation-null row for each genotype must match candidate_null.csv."""
    df = _read("results/candidate_null.csv")
    _assert_one_row_per_gene(df, "results/candidate_null.csv")
    doc = _doc("docs/evidence.md")
    for r in df.itertuples():
        row = (f"| {r.gene} | {int(r.candidates)} | {r.null_mean:.1f} | "
               f"{r.emp_p:.3f} | {r.perm_fdr:.2f} |")
        _assert_in(doc, row, "docs/evidence.md", "results/candidate_null.csv")


def test_evidence_line_centring_table():
    """The line-centring row for each genotype must match line_centring.csv."""
    df = _read("results/line_centring.csv")
    _assert_one_row_per_gene(df, "results/line_centring.csv")
    doc = _doc("docs/evidence.md")
    for r in df.itertuples():
        row = (f"| {r.gene} | {r.offset_mut_minus_wt:+.2f} | {int(r.raw)} | "
               f"{int(r.centred)} | {r.corr_dps:.3f} |")
        _assert_in(doc, row, "docs/evidence.md", "results/line_centring.csv")


def test_evidence_bootstrap_table():
    """The bootstrap survivor row for each genotype must match the summary CSV."""
    df = _read("results/bootstrap_ci_summary.csv")
    _assert_one_row_per_gene(df, "results/bootstrap_ci_summary.csv")
    doc = _doc("docs/evidence.md")
    for r in df.itertuples():
        row = (f"| {r.gene} | {int(r.point)} | {int(r.ci_excl0)} | "
               f"{int(r.ci_le_minus2)} |")
        _assert_in(doc, row, "docs/evidence.md", "results/bootstrap_ci_summary.csv")


BLIND = "concordance/results/2026-08-31_blind/concordance_report_primary_directional.csv"
SEED = "concordance/results/concordance_report.csv"


def test_evidence_concordance_table():
    """The Control 4 headline table must be the benchmark of record, not the superseded seed run.

    `_table_rows_after` takes the FIRST table under the heading, so this also pins the ordering:
    if the superseded seed table is ever moved above the census table, this fails.
    """
    df = _read(BLIND)
    _assert_one_row_per_gene(df, BLIND)
    doc = _doc("docs/evidence.md")
    n_benchmarkable = int((df.ref_in_universe > 0).sum())
    n_in_doc = len(_table_rows_after(doc, "## Control 4", "docs/evidence.md"))
    assert n_in_doc == n_benchmarkable, (
        f"the first Control 4 table in docs/evidence.md has {n_in_doc} data rows but "
        f"{BLIND} has {n_benchmarkable} genotypes with a non-empty reference set. A genotype "
        f"was added or lost, or the superseded seed table drifted above the census table."
    )
    for r in df.itertuples():
        if int(r.ref_in_universe) == 0:
            continue
        row = (f"| {r.gene} | {int(r.ref_in_universe)} | {int(r.recovered)} | "
               f"{r.hyperg_p:.2g} |")
        _assert_in(doc, row, "docs/evidence.md", BLIND)


def test_evidence_superseded_seed_table():
    """The superseded seed run stays quoted accurately, under a heading that labels it superseded."""
    df = _read(SEED)
    _assert_one_row_per_gene(df, SEED)
    doc = _doc("docs/evidence.md")
    _assert_in(doc, "### The superseded first pass", "docs/evidence.md", SEED)
    for r in df.itertuples():
        if int(r.ref_in_universe) == 0:
            continue
        row = (f"| {r.gene} | {int(r.ref_in_universe)} | {int(r.recovered)} | "
               f"{r.hyperg_p:.2g} |")
        _assert_in(doc, row, "docs/evidence.md", SEED)


def test_claude_md_b1_row():
    """CLAUDE.md's B1 row must quote the benchmark of record, not the superseded run."""
    df = _read(BLIND)
    _assert_one_row_per_gene(df, BLIND)
    doc = _doc("CLAUDE.md")
    for r in df.itertuples():
        _assert_in(doc, f"{r.gene} p={r.hyperg_p:.2g}", "CLAUDE.md", BLIND)


def test_verifying_claim_table():
    """verifying.md's claim-to-evidence rows must quote the benchmark of record."""
    df = _read(BLIND).set_index("gene")
    doc = _doc("docs/verifying.md")
    for gene in ("RB1", "TP53"):
        _assert_in(doc, f"p = {df.loc[gene].hyperg_p:.2g}", "docs/verifying.md", BLIND)


def test_aurora_leave_out_quoted_everywhere():
    """The Aurora leave-out figure is quoted in three documents; pin all three to the CSV.

    Without this the most consequential sentence in the supplement — that the RB1 enrichment
    is carried by one target class — would be prose no committed result backs.
    """
    rob = _read("concordance/results/2026-08-31_blind/robustness_RB1.csv")
    row = rob[rob.analysis == "drop_aurora_pair"]
    assert len(row) == 1, (
        "robustness_RB1.csv has no drop_aurora_pair row; regenerate it with "
        "concordance/build_suppl7_table1.py before trusting the prose."
    )
    r = row.iloc[0]
    needle = (f"{int(r.recovered_left)} of {int(r.ref_left)} recovered at "
              f"p = {r.hyperg_p:.2g}")
    for path in ("docs/evidence.md", "concordance/README.md", "CLAUDE.md"):
        _assert_in(_doc(path), needle, path,
                   "concordance/results/2026-08-31_blind/robustness_RB1.csv")


def test_evidence_demeter_validation_table():
    """The DEMETER2 RNAi cross-check figures quoted in evidence.md must match demeter_validation.csv."""
    df = _read("results/demeter_validation.csv")
    demeter_genotypes = sorted(df.genotype.unique())
    assert demeter_genotypes == ["CDKN2A", "RB1", "TP53"], (
        f"results/demeter_validation.csv holds genotypes {demeter_genotypes}, expected exactly "
        f"['CDKN2A', 'RB1', 'TP53']. The committed CSV changed shape, so the checks below can no "
        f"longer prove the document is current — regenerate or fix the CSV before trusting the docs."
    )
    assert len(df) == 36, (
        f"results/demeter_validation.csv has {len(df)} rows, expected 36. The committed CSV changed "
        f"shape, so the checks below can no longer prove the document is current — regenerate or fix "
        f"the CSV before trusting the docs."
    )
    doc = _doc("docs/evidence.md")

    def _fmt_q(q):
        return "<0.0001" if q == 0 else f"{q:.4f}"

    rb1 = df[df.genotype == "RB1"].set_index("target")
    for target in ("SKP2", "CCNE2", "E2F4", "AKT1", "CDK4", "CDK6", "AURKB", "AURKA"):
        r = rb1.loc[target]
        needle = f"{target} (ΔpD {r.delta_pD:+.3f}, q_two {_fmt_q(r.q_two)})"
        _assert_in(doc, needle, "docs/evidence.md", "results/demeter_validation.csv")

    rb1_cohort = rb1.iloc[0]
    cohort_needle = f"{int(rb1_cohort.n_mut)} mutant / {int(rb1_cohort.n_wt)} WT"
    _assert_in(doc, cohort_needle, "docs/evidence.md", "results/demeter_validation.csv")

    tp53_kif11 = df[(df.genotype == "TP53") & (df.target == "KIF11")].iloc[0]
    needle = f"KIF11 (ΔpD {tp53_kif11.delta_pD:+.3f}, q_two {_fmt_q(tp53_kif11.q_two)})"
    _assert_in(doc, needle, "docs/evidence.md", "results/demeter_validation.csv")

    assert "PTEN" not in demeter_genotypes, (
        "results/demeter_validation.csv now has PTEN rows, but evidence.md's Cross-check section "
        "states PTEN is entirely absent below the --min-lines floor — update the prose if PTEN "
        "coverage has changed."
    )


def test_readme_headline_table():
    """README.md's headline results table must match candidate_null.csv and bootstrap_ci_summary.csv."""
    null = _read("results/candidate_null.csv")
    boot = _read("results/bootstrap_ci_summary.csv")
    _assert_one_row_per_gene(null, "results/candidate_null.csv")
    _assert_one_row_per_gene(boot, "results/bootstrap_ci_summary.csv")
    doc = _doc("README.md")
    boot_by_gene = boot.set_index("gene")
    for r in null.itertuples():
        ci_le_minus2 = int(boot_by_gene.loc[r.gene, "ci_le_minus2"])
        row = f"| {r.gene} | {int(r.candidates)} | {r.perm_fdr:.2f} | {ci_le_minus2}"
        _assert_in(doc, row, "README.md",
                   "results/candidate_null.csv, results/bootstrap_ci_summary.csv")


def test_concordance_readme_blind_table():
    """concordance/README.md's benchmark-of-record table must match the blind census results."""
    df = _read(BLIND)
    _assert_one_row_per_gene(df, BLIND)
    doc = _doc("concordance/README.md")
    _assert_in(doc, "## The benchmark of record", "concordance/README.md", BLIND)
    for r in df.itertuples():
        row = (f"| {r.gene} | {int(r.ref_in_universe)} | {int(r.candidates)} | "
               f"{int(r.universe)} | {int(r.recovered)} | {r.recovery:.0%} |")
        _assert_in(doc, row, "concordance/README.md", BLIND)
        _assert_in(doc, f"{r.hyperg_p:.2g}", "concordance/README.md", f"{BLIND} (hyperg_p)")


def test_concordance_readme_seed_table():
    """concordance/README.md's superseded table must still match concordance_report.csv.

    Mirrors test_evidence_concordance_table's pattern: the hyperg_p / perm_p cells carry
    illustrative bold markers on only some rows, so — as evidence.md's own concordance test
    already does — only the structurally uniform columns (through recovery %) are pinned by
    exact row match; hyperg_p is checked separately as a bare substring.
    """
    df = _read(SEED)
    _assert_one_row_per_gene(df, SEED)
    doc = _doc("concordance/README.md")
    _assert_in(doc, "## Superseded first pass", "concordance/README.md", SEED)
    for r in df.itertuples():
        if int(r.ref_in_universe) == 0:
            row = f"| {r.gene} | {int(r.ref_in_universe)} | {int(r.candidates)} | " \
                  f"{int(r.universe)} | {int(r.recovered)} | n/a |"
            _assert_in(doc, row, "concordance/README.md",
                       "concordance/results/concordance_report.csv")
            continue
        row = (f"| {r.gene} | {int(r.ref_in_universe)} | {int(r.candidates)} | "
               f"{int(r.universe)} | {int(r.recovered)} | {r.recovery:.0%} |")
        _assert_in(doc, row, "concordance/README.md",
                   "concordance/results/concordance_report.csv")
        _assert_in(doc, f"{r.hyperg_p:.2g}", "concordance/README.md",
                   "concordance/results/concordance_report.csv (hyperg_p)")


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
