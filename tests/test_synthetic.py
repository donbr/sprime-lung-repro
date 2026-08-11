"""Synthetic-data smoke test — runs in CI without the gated DepMap/PRISM files.
Verifies the S′ math and the SL-window logic against hand-checked values, and that a small
permutation-null loop executes. Real-data reproduction is a documented local step (see README).
"""
import os, sys, math
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import sprime_core as sc


def test_sprime_worked_example():
    # doxorubicin/A549 inputs: upper=1.0, lower=0.00103, ec50=0.2449 µM, percent E_max
    emax_pct = (1.0 - 0.00103) * 100
    s = float(sc.sprime(emax_pct, 0.2449))
    assert abs(s - 6.70) < 0.05, s


def test_sprime_sign():
    assert sc.sprime(90.0, 0.5) > 0          # inhibition
    assert sc.sprime(-90.0, 0.5) < 0         # disinhibition (signed E_max)


def test_delta_and_window():
    assert sc.delta_ps(2.0, 4.0) == -2.0
    assert bool(sc.passes_window(2.0, 4.0)) is True      # active in both + ΔpS′ = -2
    assert bool(sc.passes_window(-1.0, 4.0)) is False     # fails pS′_WT > 0
    assert bool(sc.passes_window(4.0, 4.0)) is False      # ΔpS′ = 0


def test_fold_change_converges():
    assert abs(sc.fold_change(2.0) - math.e**2) < 1e-9    # ΔpS′ = -2 ⇒ ~7.389-fold


def test_permutation_null_runs():
    rng = np.random.default_rng(0)
    n_comp, n_lines = 200, 20
    S = rng.normal(3, 2, size=(n_comp, n_lines))          # compound × line S′ (no true selectivity)
    labels = np.array([0] * 12 + [2] * 8)
    counts = []
    for _ in range(50):
        perm = rng.permutation(labels)
        wt = S[:, perm == 0].mean(1); mut = S[:, perm == 2].mean(1)
        counts.append(int(np.sum(sc.passes_window(wt, mut))))
    assert len(counts) == 50 and max(counts) >= 0         # executes and produces a null distribution


if __name__ == "__main__":
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn(); print("ok", name)
    print("ALL PASSED")
