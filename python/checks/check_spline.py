"""Verify B-spline basis properties and cherry blossom / Howell1 spline fits."""
import numpy as np
from rethinking_companion.spline import (
    bspline_basis, fit_cherry_spline, fit_howell_spline,
    load_cherry_blossoms,
)
from rethinking_companion.height_weight import load_howell
from rethinking_companion.gaussian_regression import assert_diagnostics, diagnostics


def verify_basis_properties():
    """B-spline basis: non-negativity, support, partition of unity."""
    x = np.linspace(0, 100, 500)
    for nk, deg in [(5, 2), (10, 3), (20, 3), (30, 3)]:
        B, knots = bspline_basis(x, nk, degree=deg, intercept=True)
        assert (B >= -1e-10).all(), f"Negative basis values for nk={nk}, deg={deg}"
        row_sums = B.sum(axis=0)
        assert np.allclose(row_sums, 1.0, atol=1e-6), \
            f"Partition of unity violated: max deviation {abs(row_sums - 1).max()}"

        B_no_int, _ = bspline_basis(x, nk, degree=deg, intercept=False)
        assert B_no_int.shape[0] == B.shape[0] - 1
        assert (B_no_int >= -1e-10).all()
        expected_n_basis = nk + deg  # intercept=False drops one
        assert B_no_int.shape[0] == expected_n_basis, \
            f"Expected {expected_n_basis} basis funcs, got {B_no_int.shape[0]}"

    print("  basis properties: PASS")


def verify_cherry_fit():
    """Cherry blossom spline: 20-knot cubic, four-chain NUTS."""
    cb = load_cherry_blossoms()
    d = cb[cb["doy"].notna()].sort_values("year")
    year, doy = d["year"].values, d["doy"].values

    B, knots = bspline_basis(year, 20, degree=3)
    assert B.shape == (23, len(year))

    fit = fit_cherry_spline(year, doy, B, tau=10)
    _, diag = diagnostics(fit, ["a0", "a", "log_sigma"])
    assert_diagnostics(diag)

    mu_post = fit.posterior["mu"].values.reshape(-1, len(year))
    mu_mean = mu_post.mean(axis=0)
    residuals = doy - mu_mean
    assert abs(residuals.mean()) < 2.0, f"Mean residual {residuals.mean():.3f} too large"

    a0_post = fit.posterior["a0"].values.ravel()
    assert 90 < a0_post.mean() < 120, f"a0 mean {a0_post.mean():.1f} outside expected range"

    print(f"  cherry blossom fit: PASS (R-hat {diag['max_rhat']:.4f}, "
          f"bulk ESS {diag['min_ess_bulk']:.0f}, "
          f"divergences {diag['divergences']})")
    return diag


def verify_howell_fit():
    """Howell1 height~age spline: 20-knot cubic, four-chain NUTS."""
    hw = load_howell()
    order = np.argsort(hw["age"].values)
    age, height = hw["age"].values[order], hw["height"].values[order]

    B, knots = bspline_basis(age, 20, degree=3)
    assert B.shape[0] == 23

    fit = fit_howell_spline(age, height, B, tau=25)
    _, diag = diagnostics(fit, ["a0", "a", "log_sigma"])
    assert_diagnostics(diag)

    mu_post = fit.posterior["mu"].values.reshape(-1, len(age))
    mu_mean = mu_post.mean(axis=0)

    # Children (age < 5) should have lower predicted height than adults (age 25-50)
    child_mask = age < 5
    adult_mask = (age >= 25) & (age <= 50)
    child_mean = mu_mean[child_mask].mean()
    adult_mean = mu_mean[adult_mask].mean()
    assert child_mean < adult_mean, \
        f"Child mean {child_mean:.1f} not less than adult mean {adult_mean:.1f}"

    # Growth pattern: derivative should be positive in childhood
    young = (age >= 2) & (age <= 12)
    young_x = age[young]
    young_mu = mu_mean[young]
    slope = np.polyfit(young_x, young_mu, 1)[0]
    assert slope > 0, f"Expected positive slope in childhood, got {slope:.3f}"

    print(f"  Howell1 height~age fit: PASS (R-hat {diag['max_rhat']:.4f}, "
          f"bulk ESS {diag['min_ess_bulk']:.0f}, "
          f"divergences {diag['divergences']})")
    return diag


def main():
    print("check_spline.py")
    verify_basis_properties()
    cherry_diag = verify_cherry_fit()
    howell_diag = verify_howell_fit()
    print("ALL SPLINE CHECKS PASSED")
    return cherry_diag, howell_diag


if __name__ == "__main__":
    main()
