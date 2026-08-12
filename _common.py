"""Small shared helpers for every entry point: input location and console encoding.

Stdlib-only on purpose: run_all.py and fetch_data.py must stay importable without
numpy/pandas, so this cannot live in sprime_core.py.
"""
import os
import sys


def _dir_has_files(d):
    """True if `d` exists and contains at least one entry. A plain os.path.isdir check
    would treat an interrupted fetch_data.py's empty mkdir (or a stray manual mkdir) the
    same as a directory that actually holds the 560 MB of inputs."""
    try:
        return any(os.scandir(d))
    except OSError:
        return False


def default_data_dir(here):
    """data_sources/ inside the repo (where fetch_data.py writes) — the layout a fresh
    clone gets. Falls back to a sibling ../data_sources/ if that one actually has files
    and the inside one does not, so an interrupted fetch or an empty directory does not
    shadow a populated sibling. When neither has files, return the inside path — that is
    where fetch_data.py writes, so first-run behaviour is unchanged. Override with --data."""
    inside = os.path.join(here, "data_sources")
    sibling = os.path.join(here, "..", "data_sources")
    return sibling if not _dir_has_files(inside) and _dir_has_files(sibling) else inside


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
