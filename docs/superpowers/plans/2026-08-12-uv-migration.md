# uv migration and enforced reproducibility — implementation plan

**Goal:** Make the reproducibility guarantees this repository documents actually enforced — by declaring
and locking dependencies, by failing loudly when an analysis dependency is absent instead of degrading
silently, and by making written results independent of BLAS-level floating-point variation.

**Why now:** the first full Tier 1 reproduction (2026-08-12) found three gaps. `requirements.txt` pins four
packages but nothing enforces the pins, and CI installs `numpy pandas` unpinned with no scipy at all — so
the green badge has never tested the pinned environment. scipy's absence silently changes concordance
p-values and reduces `demeter_validation.py` to a table of `nan` with exit code 0. And `np.corrcoef` varies
in the last ULP between BLAS builds, so one committed artifact did not reproduce byte-identically.

## Decisions (settled)

| Decision | Choice |
|---|---|
| scipy | Hard dependency. Drop the pure-python hypergeometric fallback — it silently produces different digits than the committed baseline. |
| CI shape | A locked job proving exact reproduction, plus the existing 3.10/3.12 matrix on loose deps proving the code is not version-brittle. |
| Float stability | Round stored diagnostics via a uniform `float_format`, accepting that committed CSVs are rewritten. |

## Verified facts this plan rests on

- `uv 0.11.7` resolves the pinned set across `>=3.10,<3.14`: **13 packages** with hashes, against the 4
  that `requirements.txt` pins. The 9 unpinned transitive packages are `certifi`, `charset-normalizer`,
  `idna`, `urllib3` (via requests) and `python-dateutil`, `pytz`, `six`, `tzdata` (via pandas).
  `certifi` is the CA bundle `fetch_data.py` uses to reach figshare.
- `%.12g` absorbs **all five** observed divergences: both `corr_dps` values and all three
  `hyperg_p` values that differed between the scipy and pure-python paths.
- `%.12g` changes **no** figure the docs or tests assert on. Verified column by column against
  `candidate_null.csv` (`.1f`/`.3f`/`.2f`), `line_centring.csv` (`+.2f`/`.3f`) and
  `concordance_report.csv` (`.2g`) — every displayed value is identical before and after.

## Critical constraint: which files may be reformatted

`results/sprime_lung_pairs.csv` is an **intermediate**, re-read at full precision by
`blocking_analyses.py`, `bootstrap_ci_gate.py`, `concordance_enrichment.py` and `demeter_validation.py`.
Applying a float format to it would truncate the S′ values those scripts consume and shift every
downstream number. **Do not reformat it.**

Apply `float_format="%.12g"` only to reported outputs:

| File | Writer |
|---|---|
| `results/candidate_null.csv` | `blocking_analyses.py:64` |
| `results/line_centring.csv` | `blocking_analyses.py:82` |
| `results/bootstrap_ci_gate.csv` | `bootstrap_ci_gate.py:75` |
| `results/bootstrap_ci_summary.csv` | `bootstrap_ci_gate.py:76` |
| `concordance/results/concordance_report.csv` | `concordance/concordance_enrichment.py:105` |
| `results/demeter_validation.csv` | `demeter_validation.py:140` |

`results/lung_genotypes.csv` (`sprime_pipeline.py:117`) holds only 0/1/2 values and is already
byte-stable; leave it unchanged to keep the diff minimal.

## Tasks

### Task 1 — scipy becomes a declared, enforced dependency

- `concordance/concordance_enrichment.py`: remove the `try/except ImportError` around
  `from scipy.stats import hypergeom` and delete the `_logC`/`hyper_sf` pure-python fallback. It is the
  source of the divergent digits and would become dead code that can still silently activate.
- `demeter_validation.py`: remove the `mannwhitneyu = None` degradation. Import directly; on
  `ImportError`, print an actionable message naming the install command and exit non-zero. A statistics
  module that emits `nan` for every p-value with a success exit code is worse than one that refuses to run.
- Keep every numerical path otherwise untouched — with scipy present, behaviour is unchanged, which the
  regeneration in Task 2 must confirm.

### Task 2 — uniform float formatting, then regenerate and verify

- Add `float_format="%.12g"` to the six writers listed above, and only those.
- Regenerate from the inputs already fetched in `data_sources/` (all three md5-verified):
  `python3 run_all.py`, then `python3 concordance/concordance_enrichment.py --reference
  concordance/reference_seed_grounded.csv`, then `python3 demeter_validation.py`.
- **Verification gate.** For every regenerated file, confirm the change is representational only: parse
  old and new, and assert every value agrees to within `1e-9` relative. Any value that moves by more than
  that is a real change and must stop the task for investigation, not be committed.
- Confirm `tests/test_docs_numbers.py` still passes without editing it. It builds its needles from the
  CSVs at display precision, so a purely representational change must leave it green. If it fails, the
  formatting is too aggressive.

### Task 3 — `pyproject.toml`, `uv.lock`, and a generated `requirements.txt`

- `pyproject.toml` with `requires-python = ">=3.10,<3.14"` and the four pins as dependencies, scipy now
  among them rather than annotated optional.
- `uv lock` to produce `uv.lock` with hashes.
- Regenerate `requirements.txt` from the lock (`uv export`) so pip users keep working, with a header
  comment saying it is generated and naming the source of truth.
- Do not delete `requirements.txt`. The audience includes reviewers on pip and conda workflows.

### Task 4 — CI: prove reproduction and portability separately

Rework `.github/workflows/smoke.yml` into two jobs:

- **locked** — `uv sync --locked`, then `py_compile`, `tests/test_synthetic.py`,
  `tests/test_docs_numbers.py`. This is the job that proves a reproducer's environment.
- **portability** — the existing 3.10/3.12 matrix, but installing from the generated
  `requirements.txt` rather than an unpinned `pip install numpy pandas`, and now including scipy so the
  real code paths are exercised.

Both must run the doc-figure test; it is the drift gate.

### Task 5 — documentation

- `docs/verifying.md`: the byte-identical guarantee is now stronger. State that reported outputs are
  written at a fixed precision and are therefore stable across BLAS builds, and that CI enforces the lock.
  Keep the honest note that `sprime_lung_pairs.csv` is an unrounded intermediate.
- `README.md` and `DOWNLOAD_CHECKLIST.md`: add the `uv sync` path alongside the existing pip instructions.
- `docs/scope.md`: scipy is no longer optional; correct any wording that says otherwise.
- `CLAUDE.md`: record that `requirements.txt` is generated and that reported CSVs use `%.12g`.

## Out of scope

Rounding `sprime_lung_pairs.csv`; changing any statistical method; touching the reference set; and
anything about the companion manuscript.
