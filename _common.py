"""Small shared helpers for every entry point: input location and console encoding.

Stdlib-only on purpose: run_all.py and fetch_data.py must stay importable without
numpy/pandas, so this cannot live in sprime_core.py.
"""
import os
import sys


def default_data_dir(here):
    """data_sources/ inside the repo (where fetch_data.py writes) — the layout a fresh
    clone gets. Falls back to a sibling ../data_sources/ if that is where the inputs
    already are, so an existing checkout keeps working. Override with --data."""
    inside = os.path.join(here, "data_sources")
    sibling = os.path.join(here, "..", "data_sources")
    return sibling if not os.path.isdir(inside) and os.path.isdir(sibling) else inside


def safe_stdout():
    """Let the S-prime notation (ΔpS′, ≤, −) print on a legacy console.

    A Windows console defaults to cp1252, which cannot encode those characters, so an
    ordinary print() raises UnicodeEncodeError and kills the run *after* the CSV is
    written. Prefer real UTF-8; fall back to replacing unencodable characters.
    """
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, OSError, ValueError):
            pass  # not a reconfigurable stream (redirected/wrapped) — leave it alone
