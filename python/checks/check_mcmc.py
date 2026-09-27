"""Validate MCMC mechanics notebook: King Markov, HMC leapfrog, WaffleDivorce, bad chains."""
import json
from pathlib import Path
import numpy as np
from rethinking_companion.mcmc import (
    fit_bad_chains, fit_waffle_divorce, hmc_leapfrog, hmc_sample,
    king_markov, load_waffle_divorce, make_2d_target,
    make_correlated_target, rhat_over_time,
)
from rethinking_companion.gaussian_regression import assert_diagnostics, diagnostics


def verify_king_markov():
    print("King Markov...")
    positions = king_markov(n_steps=200_000, seed=42)
    post_burn = positions[10_000:]
    empirical = np.bincount(post_burn, minlength=10) / len(post_burn)
    target = np.arange(1, 11) / 55.0
    max_err = np.max(np.abs(empirical - target))
    print(f"  Max |empirical - target|: {max_err:.4f}")
    assert max_err < 0.01, f"King Markov frequency error too large: {max_err}"
    # chi-squared goodness of fit
    expected_counts = target * len(post_burn)
    observed_counts = np.bincount(post_burn, minlength=10).astype(float)
    chi2 = np.sum((observed_counts - expected_counts) ** 2 / expected_counts)
    print(f"  Chi-squared (9 df): {chi2:.2f}")
    assert chi2 < 30, f"Chi-squared too large: {chi2}"  # p < 0.001 threshold
    print("  PASS")


def verify_hmc_leapfrog():
    print("HMC leapfrog...")
    rng = np.random.default_rng(7)
    y = np.abs(rng.normal(size=50))
    y = np.concatenate([y, -y])

    # Small step size: energy conserved
    U, grad_U = make_2d_target(y, a=0, b=1, k=0, d=0.3)
    _, trajs = hmc_sample(U, grad_U, step_size=0.01, n_leapfrog=12,
                          q_init=np.array([-0.4, 0.2]), n_samples=10, seed=12)
    for i, t in enumerate(trajs):
        print(f"  Trajectory {i}: |ΔH| = {abs(t['dH']):.6f}, accepted={t['accepted']}")
        assert abs(t["dH"]) < 0.5, f"Energy error too large for small step: {t['dH']}"
    print("  Small step size: all |ΔH| < 0.5 — PASS")

    # Large step size on correlated target: energy errors
    rng2 = np.random.default_rng(7)
    y2 = np.abs(rng2.normal(size=20))
    y2 = np.concatenate([y2, -y2])
    U_corr, grad_U_corr = make_correlated_target(y2, a=0, b=0.5)
    _, trajs_div = hmc_sample(U_corr, grad_U_corr, step_size=0.15, n_leapfrog=15,
                              q_init=np.array([-0.4, -0.4]), n_samples=3, seed=42)
    max_dH = max(abs(t["dH"]) for t in trajs_div)
    print(f"  Large step size max |ΔH|: {max_dH:.2f}")
    assert max_dH > 1.0, f"Expected large energy error, got {max_dH}"
    print("  Large step size: energy error > 1.0 — PASS")


def verify_waffle_divorce():
    print("WaffleDivorce NUTS...")
    wd = load_waffle_divorce()
    assert len(wd) == 50
    def standardize(x):
        return (x - x.mean()) / x.std()
    dat = {
        "D": standardize(wd["Divorce"].values).astype(np.float64),
        "M": standardize(wd["Marriage"].values).astype(np.float64),
        "A": standardize(wd["MedianAgeMarriage"].values).astype(np.float64),
    }
    fit = fit_waffle_divorce(dat)
    summary, diag = diagnostics(fit, ("a", "bM", "bA", "sigma"))
    print(f"  R-hat: {diag['max_rhat']:.4f}")
    print(f"  Min bulk ESS: {diag['min_ess_bulk']:.0f}")
    print(f"  Min tail ESS: {diag['min_ess_tail']:.0f}")
    print(f"  Divergences: {diag['divergences']}")
    print(f"  Min BFMI: {diag['min_bfmi']:.3f}")
    assert_diagnostics(diag)

    bA_mean = float(fit.posterior["bA"].mean())
    bM_mean = float(fit.posterior["bM"].mean())
    print(f"  bA mean: {bA_mean:.3f} (expected ~-0.6)")
    print(f"  bM mean: {bM_mean:.3f} (expected ~0)")
    assert bA_mean < -0.3, f"bA should be negative: {bA_mean}"
    assert abs(bM_mean) < 0.3, f"bM should be near zero: {bM_mean}"
    print("  PASS")
    return fit, diag


def verify_rhat_over_time(fit):
    print("R-hat over time...")
    chains_a = fit.posterior["a"].values.T  # (draws, chains)
    W, B = rhat_over_time(chains_a)
    assert len(W) == chains_a.shape[0]
    # At convergence, B should be small relative to W
    assert B[-1] < W[-1], f"B ({B[-1]}) should be < W ({W[-1]}) at convergence"
    print(f"  Final W: {W[-1]:.6f}, B: {B[-1]:.6f}")
    print("  PASS")


def verify_bad_chains():
    print("Bad chains...")
    y = np.array([-1.0, 1.0])

    # Pathological
    fit_bad = fit_bad_chains(y, alpha_prior_sd=1000, sigma_prior_rate=0.0001, seed=811)
    _, diag_bad = diagnostics(fit_bad, ("alpha", "sigma"))
    print(f"  Pathological: R-hat={diag_bad['max_rhat']:.3f}, "
          f"min_ess_bulk={diag_bad['min_ess_bulk']:.0f}, "
          f"divergences={diag_bad['divergences']}")
    bad_failed = (diag_bad["max_rhat"] > 1.1 or diag_bad["min_ess_bulk"] < 100
                  or diag_bad["divergences"] > 0)
    assert bad_failed, "Pathological model should fail at least one diagnostic"
    print("  Pathological model fails diagnostics — PASS")

    # Fixed
    fit_good = fit_bad_chains(y, alpha_prior_sd=10, sigma_prior_rate=1, seed=812)
    _, diag_good = diagnostics(fit_good, ("alpha", "sigma"))
    print(f"  Fixed: R-hat={diag_good['max_rhat']:.4f}, "
          f"min_ess_bulk={diag_good['min_ess_bulk']:.0f}, "
          f"divergences={diag_good['divergences']}")
    assert_diagnostics(diag_good)
    print("  Fixed model passes diagnostics — PASS")


def main():
    verify_king_markov()
    verify_hmc_leapfrog()
    fit, diag = verify_waffle_divorce()
    verify_rhat_over_time(fit)
    verify_bad_chains()
    print("\nAll MCMC checks passed.")


if __name__ == "__main__":
    main()
