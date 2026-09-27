"""Verify elemental confounds simulations and WaffleDivorce regression fits."""
import hashlib
import json
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.special import expit
from rethinking_companion.runtime import configure_runtime
configure_runtime()
import pymc as pm
from rethinking_companion.gaussian_regression import assert_diagnostics, diagnostics


def verify_elemental_confounds():
    """Check d-separation predictions on binary simulations."""
    n = 10_000
    rng = np.random.default_rng(42)

    def rbern(n, p):
        return rng.binomial(1, p, n)

    # Fork: X <- Z -> Y; cor(X,Y) > 0, cor(X,Y|Z) ~ 0
    Z = rbern(n, 0.5)
    X = rbern(n, np.where(Z == 0, 0.1, 0.9))
    Y = rbern(n, np.where(Z == 0, 0.1, 0.9))
    assert abs(np.corrcoef(X, Y)[0, 1]) > 0.3, "Fork: marginal X-Y should be correlated"
    for z in [0, 1]:
        c = abs(np.corrcoef(X[Z == z], Y[Z == z])[0, 1])
        assert c < 0.1, f"Fork: cor(X,Y|Z={z}) = {c:.3f}, expected near 0"

    # Pipe: X -> Z -> Y; cor(X,Y) > 0, cor(X,Y|Z) ~ 0
    X = rbern(n, 0.5)
    Z = rbern(n, np.where(X == 0, 0.1, 0.9))
    Y = rbern(n, np.where(Z == 0, 0.1, 0.9))
    assert abs(np.corrcoef(X, Y)[0, 1]) > 0.3, "Pipe: marginal X-Y should be correlated"
    for z in [0, 1]:
        c = abs(np.corrcoef(X[Z == z], Y[Z == z])[0, 1])
        assert c < 0.1, f"Pipe: cor(X,Y|Z={z}) = {c:.3f}, expected near 0"

    # Collider: X -> Z <- Y; cor(X,Y) ~ 0, cor(X,Y|Z) != 0
    X = rbern(n, 0.5)
    Y = rbern(n, 0.5)
    Z = rbern(n, np.where(X + Y > 0, 0.9, 0.2))
    assert abs(np.corrcoef(X, Y)[0, 1]) < 0.05, "Collider: marginal X-Y should be ~0"
    for z in [0, 1]:
        c = abs(np.corrcoef(X[Z == z], Y[Z == z])[0, 1])
        assert c > 0.05, f"Collider: cor(X,Y|Z={z}) = {c:.3f}, expected nonzero"

    print("  elemental confounds: PASS")


def verify_happiness_collider():
    """Happiness simulation: marginal independence, conditional correlation."""
    rng = np.random.default_rng(1977)
    A = np.array([], dtype=float)
    H = np.array([], dtype=float)
    M = np.array([], dtype=int)
    for _t in range(1000):
        A = A + 1
        newborn_H = np.linspace(-2, 2, 20)
        A = np.concatenate([A, np.ones(20)])
        H = np.concatenate([H, newborn_H])
        M = np.concatenate([M, np.zeros(20, dtype=int)])
        eligible = (A >= 18) & (M == 0)
        marry_prob = expit(H - 4) * eligible
        M = np.where(rng.random(len(A)) < marry_prob, 1, M).astype(int)
        alive = A <= 65
        A, H, M = A[alive], H[alive], M[alive]

    cor_marginal = abs(np.corrcoef(A, H)[0, 1])
    assert cor_marginal < 0.05, f"Marginal cor(age,happiness) = {cor_marginal:.4f}, expected ~0"

    married = M == 1
    cor_married = np.corrcoef(A[married], H[married])[0, 1]
    assert cor_married < -0.05, f"cor(age,happiness|married) = {cor_married:.4f}, expected negative"

    print(f"  happiness collider: PASS (marginal r={cor_marginal:.4f}, "
          f"married r={cor_married:.4f})")


def verify_waffle_divorce():
    """WaffleDivorce: three models with diagnostic gates and coefficient checks."""
    folder = Path(__file__).resolve().parents[1] / "data"
    payload = (folder / "WaffleDivorce.csv").read_bytes()
    prov = json.loads((folder / "WaffleDivorce.provenance.json").read_text())
    assert hashlib.sha256(payload).hexdigest() == prov["sha256"]
    wd = pd.read_csv(folder / "WaffleDivorce.csv", sep=";")
    assert len(wd) == 50

    def std(x):
        return (x - x.mean()) / x.std()

    D = std(wd["Divorce"].values)
    M = std(wd["Marriage"].values)
    A = std(wd["MedianAgeMarriage"].values)

    # D ~ A
    with pm.Model():
        a = pm.Normal("a", 0, 0.2)
        bA = pm.Normal("bA", 0, 0.5)
        sigma = pm.Exponential("sigma", 1)
        pm.Normal("D", a + bA * A, sigma, observed=D)
        fit_DA = pm.sample(draws=1500, tune=1000, chains=4, cores=1,
                           random_seed=901, target_accept=0.9,
                           progressbar=False, return_inferencedata=True)
    _, diag_DA = diagnostics(fit_DA, ["a", "bA", "sigma"])
    assert_diagnostics(diag_DA)
    bA_alone = fit_DA.posterior["bA"].values.ravel().mean()
    assert bA_alone < -0.3, f"D~A: bA={bA_alone:.3f}, expected strongly negative"

    # D ~ M
    with pm.Model():
        a = pm.Normal("a", 0, 0.2)
        bM = pm.Normal("bM", 0, 0.5)
        sigma = pm.Exponential("sigma", 1)
        pm.Normal("D", a + bM * M, sigma, observed=D)
        fit_DM = pm.sample(draws=1500, tune=1000, chains=4, cores=1,
                           random_seed=902, target_accept=0.9,
                           progressbar=False, return_inferencedata=True)
    _, diag_DM = diagnostics(fit_DM, ["a", "bM", "sigma"])
    assert_diagnostics(diag_DM)

    # D ~ M + A
    with pm.Model():
        a = pm.Normal("a", 0, 0.2)
        bM = pm.Normal("bM", 0, 0.5)
        bA = pm.Normal("bA", 0, 0.5)
        sigma = pm.Exponential("sigma", 1)
        pm.Normal("D", a + bM * M + bA * A, sigma, observed=D)
        fit_DMA = pm.sample(draws=1500, tune=1000, chains=4, cores=1,
                            random_seed=903, target_accept=0.9,
                            progressbar=False, return_inferencedata=True)
    _, diag_DMA = diagnostics(fit_DMA, ["a", "bM", "bA", "sigma"])
    assert_diagnostics(diag_DMA)

    bA_multi = fit_DMA.posterior["bA"].values.ravel().mean()
    bM_multi = fit_DMA.posterior["bM"].values.ravel().mean()
    assert bA_multi < -0.3, f"D~M+A: bA={bA_multi:.3f}, expected strongly negative"
    assert abs(bM_multi) < 0.3, f"D~M+A: bM={bM_multi:.3f}, expected near zero"

    print(f"  WaffleDivorce: PASS")
    print(f"    D~A: bA={bA_alone:.3f} (R-hat {diag_DA['max_rhat']:.4f})")
    print(f"    D~M+A: bA={bA_multi:.3f}, bM={bM_multi:.3f} "
          f"(R-hat {diag_DMA['max_rhat']:.4f})")
    return diag_DA, diag_DM, diag_DMA


def main():
    print("check_confounds.py")
    verify_elemental_confounds()
    verify_happiness_collider()
    diags = verify_waffle_divorce()
    print("ALL CONFOUND CHECKS PASSED")
    return diags


if __name__ == "__main__":
    main()
