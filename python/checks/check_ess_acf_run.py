"""Fire-and-forget: run Bangladesh + 1000-dim fits, save artifacts for inspection.

Usage (from python/ directory):
    uv run python checks/check_ess_acf_run.py 2>&1 | tee checks/check_ess_acf_run.log

Artifacts saved:
    checks/ess_acf_bangladesh.nc   — ArviZ InferenceData
    checks/ess_acf_1000dim.nc      — ArviZ InferenceData
    checks/check_ess_acf_run.log   — stdout log
"""
import json
import sys
import time
from pathlib import Path
import arviz as az
import numpy as np

from rethinking_companion.mcmc import fit_bangladesh, fit_1000dim_normal, load_bangladesh
from rethinking_companion.gaussian_regression import assert_diagnostics, diagnostics

OUT = Path(__file__).resolve().parent


def run_bangladesh():
    print("=" * 60)
    print("Bangladesh hierarchical model (126 parameters, 4 chains)")
    print("=" * 60)
    bd = load_bangladesh()
    dat = {
        "C": bd["use.contraception"].values.astype(np.int64),
        "D": (bd["district"].values - 1).astype(np.int64),
        "U": bd["urban"].values.astype(np.float64),
    }
    t0 = time.time()
    fit = fit_bangladesh(dat)
    elapsed = time.time() - t0
    print(f"Sampling completed in {elapsed:.0f} seconds.")

    fit.to_netcdf(str(OUT / "ess_acf_bangladesh.nc"))
    print(f"Saved: {OUT / 'ess_acf_bangladesh.nc'}")

    summary, diag = diagnostics(fit, ("abar", "bbar", "sigma", "tau"))
    print(f"Hyperparameter diagnostics:")
    for k, v in diag.items():
        print(f"  {k}: {v}")
    try:
        assert_diagnostics(diag)
        print("  All hyperparameter diagnostic gates PASS")
    except AssertionError as e:
        print(f"  DIAGNOSTIC FAILURE: {e}")

    a_means = fit.posterior["a"].mean(dim=("chain", "draw")).values
    sd_posterior = float(np.std(a_means))
    districts = dat["D"]
    contraception = dat["C"]
    raw_props = []
    for d in range(61):
        mask = districts == d
        if mask.sum() > 0:
            p = contraception[mask].mean()
            p = np.clip(p, 0.01, 0.99)
            raw_props.append(np.log(p / (1 - p)))
    sd_raw = float(np.std(raw_props))
    print(f"Shrinkage: posterior SD = {sd_posterior:.3f}, raw SD = {sd_raw:.3f}")
    if sd_posterior < sd_raw:
        print("  Partial pooling verified — PASS")
    else:
        print("  WARNING: no shrinkage detected")
    return fit


def run_1000dim():
    print("\n" + "=" * 60)
    print("1000-dim Normal ESS demonstration")
    print("=" * 60)
    t0 = time.time()
    fit = fit_1000dim_normal()
    elapsed = time.time() - t0
    print(f"Sampling completed in {elapsed:.0f} seconds.")

    fit.to_netcdf(str(OUT / "ess_acf_1000dim.nc"))
    print(f"Saved: {OUT / 'ess_acf_1000dim.nc'}")

    ess_theta_bulk = az.ess(fit, var_names=["theta"], method="bulk")["theta"].values
    ess_sq_bulk = az.ess(fit, var_names=["theta_sq"], method="bulk")["theta_sq"].values
    median_theta = float(np.median(ess_theta_bulk))
    median_sq = float(np.median(ess_sq_bulk))
    print(f"Median theta bulk ESS: {median_theta:.0f}")
    print(f"Median theta² bulk ESS: {median_sq:.0f}")
    print(f"Ratio: {median_theta / median_sq:.1f}×")
    if median_theta > 2 * median_sq:
        print("  theta ESS > 2× theta² ESS — PASS")
    else:
        print("  WARNING: ESS ratio too small")

    # ACF check
    chain0_theta = fit.posterior["theta"].values[0, :, 0]
    chain0_sq = fit.posterior["theta_sq"].values[0, :, 0]
    def acf_at_lag(x, k):
        n = len(x)
        m = x.mean()
        v = np.var(x)
        return float(np.mean((x[:n - k] - m) * (x[k:] - m)) / v)
    acf_t5 = acf_at_lag(chain0_theta, 5)
    acf_s5 = acf_at_lag(chain0_sq, 5)
    print(f"ACF at lag 5: theta[0]={acf_t5:.4f}, theta²[0]={acf_s5:.4f}")
    if abs(acf_t5) < abs(acf_s5):
        print("  ACF decays faster for theta — PASS")
    else:
        print("  WARNING: ACF not decaying faster for theta")
    return fit


if __name__ == "__main__":
    run_bangladesh()
    run_1000dim()
    print("\n" + "=" * 60)
    print("Fire-and-forget run complete.")
    print("Inspect artifacts: ess_acf_bangladesh.nc, ess_acf_1000dim.nc")
    print("=" * 60)
