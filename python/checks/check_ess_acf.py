"""Validate ESS/ACF lab: Bangladesh hierarchical model + 1000-dim ESS demonstration."""
import numpy as np
from rethinking_companion.mcmc import (
    fit_bangladesh, fit_1000dim_normal, load_bangladesh,
)
from rethinking_companion.gaussian_regression import az, assert_diagnostics, diagnostics


def verify_bangladesh():
    print("Bangladesh hierarchical model...")
    bd = load_bangladesh()
    assert len(bd) == 1934
    dat = {
        "C": bd["use.contraception"].values.astype(np.int64),
        "D": (bd["district"].values - 1).astype(np.int64),
        "U": bd["urban"].values.astype(np.float64),
    }
    fit = fit_bangladesh(dat)

    # hyperparameter diagnostics
    summary, diag = diagnostics(fit, ("abar", "bbar", "sigma", "tau"))
    print(f"  R-hat: {diag['max_rhat']:.4f}")
    print(f"  Min bulk ESS: {diag['min_ess_bulk']:.0f}")
    print(f"  Min tail ESS: {diag['min_ess_tail']:.0f}")
    print(f"  Divergences: {diag['divergences']}")
    print(f"  Min BFMI: {diag['min_bfmi']:.3f}")
    assert_diagnostics(diag)

    # partial pooling: SD of posterior intercept means < SD of raw district proportions
    a_means = fit.posterior["a"].mean(dim=("chain", "draw")).values
    sd_posterior = float(np.std(a_means))

    # raw district proportions (on logit scale for fair comparison)
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
    print(f"  SD of posterior intercept means: {sd_posterior:.3f}")
    print(f"  SD of raw district logit proportions: {sd_raw:.3f}")
    assert sd_posterior < sd_raw, (
        f"Partial pooling: posterior SD ({sd_posterior}) should be < raw SD ({sd_raw})")
    print("  Partial pooling verified (shrinkage toward grand mean) — PASS")
    return fit


def verify_1000dim_ess():
    print("1000-dim ESS demonstration...")
    fit = fit_1000dim_normal()

    ess_theta_bulk = az.ess(fit, var_names=["theta"], method="bulk")["theta"].values
    ess_sq_bulk = az.ess(fit, var_names=["theta_sq"], method="bulk")["theta_sq"].values

    median_theta = float(np.median(ess_theta_bulk))
    median_sq = float(np.median(ess_sq_bulk))
    print(f"  Median theta bulk ESS: {median_theta:.0f}")
    print(f"  Median theta² bulk ESS: {median_sq:.0f}")
    print(f"  Ratio: {median_theta / median_sq:.1f}×")
    assert median_theta > 2 * median_sq, (
        f"theta ESS ({median_theta}) should be > 2× theta² ESS ({median_sq})")
    print("  theta ESS > 2× theta² ESS — PASS")

    # ACF check: theta[0] ACF at lag 5 < theta_sq[0] ACF at lag 5
    chain0_theta = fit.posterior["theta"].values[0, :, 0]
    chain0_sq = fit.posterior["theta_sq"].values[0, :, 0]
    lag = 5
    def acf_at_lag(x, k):
        n = len(x)
        m = x.mean()
        v = np.var(x)
        return float(np.mean((x[:n-k] - m) * (x[k:] - m)) / v)
    acf_theta_5 = acf_at_lag(chain0_theta, lag)
    acf_sq_5 = acf_at_lag(chain0_sq, lag)
    print(f"  ACF at lag {lag}: theta[0]={acf_theta_5:.4f}, theta²[0]={acf_sq_5:.4f}")
    assert abs(acf_theta_5) < abs(acf_sq_5), (
        f"theta ACF ({acf_theta_5}) should decay faster than theta² ACF ({acf_sq_5})")
    print("  ACF decays faster for theta than theta² — PASS")


def main():
    verify_bangladesh()
    verify_1000dim_ess()
    print("\nAll ESS/ACF checks passed.")


if __name__ == "__main__":
    main()
