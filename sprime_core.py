"""Core S′ definitions — single source of truth for the metric and the SL window.

S′ = asinh((E_max / EC50) × C_ref),  C_ref = 1 µM,  E_max on the percent (0–100) scale.
The argument is signed (E_max = upper − lower asymptote), so S′ > 0 = inhibition, S′ < 0 = disinhibition.
pS′ = cohort mean of S′;  ΔpS′ = pS′_WT − pS′_mutant  (negative ⇒ mutant-selective inhibition).
SL window: pS′_WT > 0 AND pS′_mutant > 0 AND ΔpS′ ≤ delta_le (default −2), with ≥ min_lines per pool.
"""
import numpy as np

C_REF_UM = 1.0
DELTA_LE = -2.0
MIN_LINES = 3

def sprime(emax_percent, ec50_uM):
    """S′ for one curve. emax_percent = (upper - lower) * 100 (signed); ec50 in µM."""
    return np.arcsinh((np.asarray(emax_percent) / np.asarray(ec50_uM)) * C_REF_UM)

def delta_ps(psprime_wt, psprime_mut):
    """ΔpS′ = pS′_WT − pS′_mutant."""
    return np.asarray(psprime_wt) - np.asarray(psprime_mut)

def passes_window(pwt, pmut, delta_le=DELTA_LE):
    """Boolean SL-window test given pooled pS′ values (activity + selectivity)."""
    pwt = np.asarray(pwt); pmut = np.asarray(pmut)
    return (pwt > 0) & (pmut > 0) & (delta_ps(pwt, pmut) <= delta_le)

def fold_change(delta_ps_units):
    """Interpret a ΔpS′ gap as a fold change in E_max/EC50 (converges to e**|Δ| for pS′≳1)."""
    return float(np.exp(abs(delta_ps_units)))
