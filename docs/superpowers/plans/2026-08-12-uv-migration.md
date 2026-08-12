# Enforced reproducibility: loud failures, one window definition, and uv

**Goal:** Make the guarantees this repository documents actually enforced. Three strands, in one pass
because they touch the same files and share a single regeneration: stop the pipeline failing silently,
make the declared single source of truth actually govern the analysis, and lock the environment.

**Why one pass:** a high-effort code review verified ten defects, and several land in files the uv
migration already had to touch. The `%.12g` reformat regenerates every cited CSV, which is precisely the
trigger for the README-drift defect — fixing them separately would mean regenerating twice.

## Ordering constraint

Analysis-code changes must all land **before** the single regeneration, and the drift-gate extension
**after** it. Tasks are ordered accordingly. Only Task 5 regenerates; every earlier task must leave the
committed CSVs untouched, which is itself the check that those changes are behaviour-preserving.

## Verified facts this plan rests on

- `uv 0.11.7` resolves the pinned set across `>=3.10,<3.14`: **13 packages** with hashes, against the 4
  in `requirements.txt`. The 9 additions include `certifi`, the CA bundle `fetch_data.py` uses for figshare.
- `%.12g` absorbs **all five** observed float divergences (both `corr_dps`, all three `hyperg_p`) and
  changes **no** figure the docs or tests assert on — verified column by column at each display precision.
- Reported outputs may be reformatted; `results/sprime_lung_pairs.csv` may **not**. It is an intermediate
  re-read at full precision by four downstream scripts, so rounding it would shift every downstream number.

---

### Task 1 — Stop failing silently

Six defects share one shape: a guard that disables itself, or a verdict that never reaches the exit code.
For a repository whose value is that its numbers can be trusted, a failure that looks like success is the
worst available outcome. Each fix is small; the point is that none of them may print nothing.

- **`sprime_pipeline.py:106`** — the cohort-size check prints `ok`/`CHECK` and never feeds `val_ok`.
  Wire it in, so a genotype-call regression produces the same non-zero exit the doxorubicin anchor does.
  `run_all.py` already treats exit 1 as a warning and ≥2 as fatal; a cohort mismatch belongs at 1.
- **`demeter_validation.py:62`** — the md5 pin silently disables whenever `--demeter` names a non-default
  filename. Either verify whatever file is named, or print an explicit unverified-input notice mirroring
  `sprime_pipeline.py`'s `--skip-checksum` message. Silence is the defect.
- **`demeter_validation.py:71`** — an unresolvable `--reference` falls through to `DEFAULT_TARGETS` with
  no message. An explicitly-passed path that does not exist is a user error: report it and exit non-zero.
  Do not silently substitute a different target set.
- **`run_all.py:45`** — the printed concordance follow-up hardcodes repo-relative paths and drops the
  user's `--out`. Interpolate the actual `--out`, or drop the suggestion rather than print a command that
  reads a different derived table than the run just produced.
- **`_common.py:16`** — `default_data_dir` prefers a repo-inside `data_sources/` on mere existence, so an
  empty directory shadows a populated sibling. Prefer the directory that actually contains inputs; fall
  back to the inside path when neither does, so first-run behaviour is unchanged.
- **`tests/test_docs_numbers.py`** — add the `safe_stdout()` call every other entry point makes. Its
  assertion messages embed ΔpD and prime glyphs, so on a cp1252 console the drift report dies with an
  encoding error instead of naming the drift.

**Gate:** `git diff --quiet results/ concordance/results/` after this task. None of these may change a number.

### Task 2 — Make `sprime_core` actually the single source of truth

`sprime_core.DELTA_LE`, `MIN_LINES` and `passes_window` are imported by nothing but the synthetic test.
The window that produces every cited figure is re-implemented inline in `blocking_analyses.py:24,58`,
`bootstrap_ci_gate.py:54` and `concordance/concordance_enrichment.py:38`, each with a literal `-2` and its
own module-level `MINN = 3`. Change the constants and the docs describe one window while the code applies
another, with nothing detecting it.

Import the constants from `sprime_core` in all three consumers and delete the local duplicates. Keep the
vectorised expressions as they are — this is about where the *numbers* come from, not restructuring the
maths. Where a script needs the window elementwise over arrays, use `sprime_core.passes_window`; where it
needs it inside a permutation loop over NumPy arrays, importing `DELTA_LE` and `MIN_LINES` is sufficient
and avoids changing the hot path.

Also fix **`blocking_analyses.py:61`**: `rate = nobs / ntest` has no zero guard though the adjacent `fdr`
does. With `ntest == 0` STEP 2 dies mid-loop, leaving STEP 3's outputs freshly written beside STEP 2's
stale ones. Guard it the same way `fdr` is guarded, and make the printed row render sensibly at zero.

**Gate:** `git diff --quiet results/ concordance/results/`. Sourcing the same values from one place must
be a no-op numerically. If any CSV changes, the duplicates had already drifted — stop and report that.

### Task 3 — scipy becomes a declared, enforced dependency

- `concordance/concordance_enrichment.py`: remove the `try/except ImportError` around
  `from scipy.stats import hypergeom` and delete the `_logC`/`hyper_sf` pure-python fallback. Measured,
  the fallback produces p-values differing from scipy's in the 12th significant digit, so it is a second
  numerically distinct path that can activate silently.
- `demeter_validation.py`: remove the `mannwhitneyu = None` degradation. On `ImportError`, print the
  install command and exit non-zero. A statistics module emitting `nan` for every p-value with exit 0 is
  worse than one that refuses to run.

**Gate:** `git diff --quiet results/ concordance/results/` — scipy is present here, so behaviour is unchanged.

### Task 4 — Uniform float formatting

Add `float_format="%.12g"` to exactly these six writers, and no others:
`blocking_analyses.py:64,82`, `bootstrap_ci_gate.py:75,76`,
`concordance/concordance_enrichment.py:105`, `demeter_validation.py:140`.

Do **not** touch `sprime_pipeline.py:115` (`sprime_lung_pairs.csv`, the intermediate) or `:117`
(`lung_genotypes.csv`, already byte-stable 0/1/2 values).

### Task 5 — One regeneration, under a hard verification gate

Inputs are already fetched and md5-verified in `data_sources/`. Run:
`python3 run_all.py`, then
`python3 concordance/concordance_enrichment.py --reference concordance/reference_seed_grounded.csv`, then
`python3 demeter_validation.py`.

**The gate, which is the whole point of this task.** For every regenerated file, parse the committed and
regenerated versions and assert every numeric value agrees to within `1e-9` relative. Anything moving more
than that is a real change from Tasks 1–4, not a reformat: stop and report it rather than commit it.

Then confirm `tests/test_docs_numbers.py` passes **without being edited**. It builds needles from the CSVs
at display precision, so a purely representational change must leave it green.

### Task 6 — `pyproject.toml`, `uv.lock`, generated `requirements.txt`

`requires-python = ">=3.10,<3.14"`; the four pins as dependencies with scipy among them rather than
annotated optional; `uv lock` for a hashed lockfile; regenerate `requirements.txt` via `uv export` with a
header naming the lock as the source of truth. Do not delete `requirements.txt` — the audience includes
reviewers on pip and conda.

### Task 7 — CI: prove reproduction and portability separately, and stop hardcoding the file list

Rework `.github/workflows/smoke.yml` into two jobs:

- **locked** — `uv sync --locked`, then the compile check and both test scripts. Proves a reproducer's env.
- **portability** — the existing 3.10/3.12 matrix, installing from the generated `requirements.txt`
  rather than an unpinned `pip install numpy pandas`, and now including scipy so the real paths run.

Replace the hardcoded nine-file `py_compile` list with discovery over tracked Python files, so the repo's
only universal check cannot be outgrown by adding a file. The same list is duplicated in three documents;
update or remove those copies so there is one description of what CI compiles.

### Task 8 — Extend the drift gate beyond `docs/`

`tests/test_docs_numbers.py::_doc()` opens files only under `docs/`, so `README.md`'s headline table and
`concordance/README.md`'s results table quote committed CSVs with no protection — and the README table is
the first thing a referee reads. Generalise the helper to take a repo-relative path, and add assertions
pinning both tables. Task 5's regeneration must land first so the numbers are current.

### Task 9 — Documentation

- `docs/verifying.md`: reported outputs are now written at fixed precision and are stable across BLAS
  builds; CI enforces the lock. Keep the note that `sprime_lung_pairs.csv` is an unrounded intermediate.
- `README.md`, `DOWNLOAD_CHECKLIST.md`: add the `uv sync` path alongside pip.
- `docs/scope.md`: scipy is no longer optional.
- `CLAUDE.md`: `requirements.txt` is generated; reported CSVs use `%.12g`; the drift gate now covers
  `README.md` and `concordance/README.md`; the exit-code contract now includes the cohort check.

## Out of scope

Moving scripts into `src/` or a package. The review returned no finding recommending it, and treats a
package move as a *risk* to the CI compile check rather than a fix. The flat root is defensible for nine
scripts whose audience types `python3 run_all.py`; what was wrong was that the declared abstractions did
not hold, which Tasks 1, 2 and 7 address directly. Revisit only if a concrete need appears.

Also out of scope: rounding `sprime_lung_pairs.csv`; changing any statistical method; expanding the
concordance reference set.
