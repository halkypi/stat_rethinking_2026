"""Validate categorical weight models against independent integration."""
import json
from pathlib import Path
import numpy as np
from rethinking_companion.categorical import (
    adult_sex_data, causal_contrast_scm, fit_full_scm,
    fit_weight_by_sex, fit_weight_height_sex,
    integrated_categorical_posterior,
)
from rethinking_companion.gaussian_regression import az, assert_diagnostics, diagnostics


def verify_ws_model(fit, dat):
    summary, diag = diagnostics(fit, ("a", "sigma"))
    assert_diagnostics(diag)
    a_post = fit.posterior["a"].values.reshape(-1, 2)
    sigma_post = fit.posterior["sigma"].values.ravel()
    assert np.all((sigma_post > 0) & (sigma_post < 10))

    means, cov, boundary = integrated_categorical_posterior(dat["W"], dat["S"])
    assert boundary < 1e-8, f"Grid boundary mass {boundary}"
    mcmc_means = np.array([a_post[:, 0].mean(), a_post[:, 1].mean(), sigma_post.mean()])
    mcse = np.array([
        float(az.mcse(fit, var_names=["a"])["a"].values[0]),
        float(az.mcse(fit, var_names=["a"])["a"].values[1]),
        float(az.mcse(fit, var_names=["sigma"])["sigma"]),
    ])
    assert np.all(abs(mcmc_means - means) < 6 * mcse + 1e-4), \
        f"Mean mismatch: MCMC {mcmc_means} vs integrated {means}, MCSE {mcse}"

    contrast = a_post[:, 1] - a_post[:, 0]
    assert contrast.mean() > 0, "Expected males heavier on average"
    return diag, means, cov


def verify_wsh_model(fit, dat):
    summary, diag = diagnostics(fit, ("a", "b", "sigma"))
    assert_diagnostics(diag)
    b_post = fit.posterior["b"].values.reshape(-1, 2)
    assert np.all(b_post > 0), "LogNormal slope must be positive"
    sigma = fit.posterior["sigma"].values.ravel()
    assert np.all((sigma > 0) & (sigma < 10))
    return diag


def verify_scm(fit, dat):
    summary, diag = diagnostics(fit, ("h", "tau", "a", "b", "sigma"))
    assert_diagnostics(diag)
    W_do_S = causal_contrast_scm(fit, dat["Hbar"])
    total_effect = W_do_S.mean()
    direct_contrast = (fit.posterior["a"].values.reshape(-1, 2)[:, 1]
                       - fit.posterior["a"].values.reshape(-1, 2)[:, 0]).mean()
    assert total_effect > direct_contrast, \
        f"Total effect {total_effect:.2f} should exceed direct {direct_contrast:.2f}"
    assert total_effect > 0
    return diag, float(total_effect), float(direct_contrast)


def main():
    root = Path(__file__).resolve().parents[1]
    dat = adult_sex_data()
    assert len(dat["W"]) == 352
    assert (dat["S"] == 1).sum() == 187  # females
    assert (dat["S"] == 2).sum() == 165  # males

    # W ~ S
    fit_ws = fit_weight_by_sex(dat)
    diag_ws, means, cov = verify_ws_model(fit_ws, dat)
    print("PASS W~S: diagnostics, independent integration, positive contrast")
    print(json.dumps({"diagnostics": diag_ws, "integrated_means": means.tolist()}))

    # W ~ S + H
    fit_wsh = fit_weight_height_sex(dat)
    diag_wsh = verify_wsh_model(fit_wsh, dat)
    print("PASS W~S+H: diagnostics, positive slopes, sigma support")
    print(json.dumps({"diagnostics": diag_wsh}))

    # Full SCM
    fit_scm = fit_full_scm(dat)
    diag_scm, total, direct = verify_scm(fit_scm, dat)
    print(f"PASS Full SCM: total causal effect {total:.2f} > direct {direct:.2f}")
    print(json.dumps({"diagnostics": diag_scm, "total_effect": total, "direct_effect": direct}))

    # Notebook structural check is handled by `marimo check notebooks/04_categorical_weight.py`.
    # Chart schema validation runs via marimo export; App.run with mo.vstack + Altair
    # LayerCharts fails without IPython in Altair 6.3.0's _repr_mimebundle_ fallback.

    print("ALL CHECKS PASSED")


if __name__ == "__main__":
    main()
