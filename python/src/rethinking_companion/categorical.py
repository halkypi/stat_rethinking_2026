"""Categorical weight models and the full height-weight SCM from 04_height_weight_sex_categorical.r."""
from .runtime import configure_runtime
configure_runtime()

import numpy as np
import pymc as pm
from .height_weight import load_howell


def adult_sex_data():
    data = load_howell().query("age >= 18")
    return {
        "W": data.weight.to_numpy(),
        "H": data.height.to_numpy(),
        "S": data.male.to_numpy() + 1,  # 1=Female, 2=Male (matches R)
        "Hbar": float(data.height.mean()),
        "sex_labels": ["Female", "Male"],
    }


def fit_weight_by_sex(dat, *, seed=501, draws=1500, tune=1000):
    """W ~ Normal(a[S], sigma) with indexed intercepts."""
    W, S = dat["W"], dat["S"]
    with pm.Model(coords={"sex": dat["sex_labels"], "obs": np.arange(len(W))}):
        a = pm.Normal("a", 60, 10, dims="sex")
        sigma = pm.Uniform("sigma", 0, 10)
        mu = pm.Deterministic("mu", a[S - 1], dims="obs")
        pm.Normal("W", mu, sigma, observed=W, dims="obs")
        idata = pm.sample(draws=draws, tune=tune, chains=4, cores=1,
                          random_seed=seed, target_accept=0.9,
                          progressbar=False, return_inferencedata=True)
        pm.sample_posterior_predictive(idata, var_names=["W"], random_seed=seed + 2,
                                       extend_inferencedata=True, progressbar=False)
    return idata


def fit_weight_height_sex(dat, *, seed=502, draws=1500, tune=1000):
    """W ~ Normal(a[S] + b[S]*(H - Hbar), sigma) with sex-varying slopes."""
    W, H, S, Hbar = dat["W"], dat["H"], dat["S"], dat["Hbar"]
    with pm.Model(coords={"sex": dat["sex_labels"], "obs": np.arange(len(W))}):
        a = pm.Normal("a", 60, 10, dims="sex")
        b = pm.LogNormal("b", 0, 1, dims="sex")
        sigma = pm.Uniform("sigma", 0, 10)
        mu = pm.Deterministic("mu", a[S - 1] + b[S - 1] * (H - Hbar), dims="obs")
        pm.Normal("W", mu, sigma, observed=W, dims="obs")
        idata = pm.sample(draws=draws, tune=tune, chains=4, cores=1,
                          random_seed=seed, target_accept=0.9,
                          progressbar=False, return_inferencedata=True)
    return idata


def fit_full_scm(dat, *, seed=503, draws=1500, tune=1000):
    """Joint SCM: height and weight both depend on sex."""
    W, H, S, Hbar = dat["W"], dat["H"], dat["S"], dat["Hbar"]
    with pm.Model(coords={"sex": dat["sex_labels"], "obs": np.arange(len(W))}):
        h = pm.Normal("h", 160, 10, dims="sex")
        tau = pm.Uniform("tau", 0, 10)
        nu = pm.Deterministic("nu", h[S - 1], dims="obs")
        pm.Normal("H", nu, tau, observed=H, dims="obs")
        a = pm.Normal("a", 60, 10, dims="sex")
        b = pm.LogNormal("b", 0, 1, dims="sex")
        sigma = pm.Uniform("sigma", 0, 10)
        mu = pm.Deterministic("mu", a[S - 1] + b[S - 1] * (H - Hbar), dims="obs")
        pm.Normal("W", mu, sigma, observed=W, dims="obs")
        idata = pm.sample(draws=draws, tune=tune, chains=4, cores=1,
                          random_seed=seed, target_accept=0.9,
                          progressbar=False, return_inferencedata=True)
    return idata


def causal_contrast_scm(idata, Hbar, *, n=10_000, seed=504):
    """Simulate do(S=1) vs do(S=2) through the full SCM to get total causal effect."""
    rng = np.random.default_rng(seed)
    post = {name: idata.posterior[name].values.reshape(-1, 2)
            for name in ("h", "a", "b")}
    tau = idata.posterior["tau"].values.ravel()
    sigma = idata.posterior["sigma"].values.ravel()
    idx = rng.integers(0, len(tau), n)
    H_S1 = rng.normal(post["h"][idx, 0], tau[idx])
    W_S1 = rng.normal(post["a"][idx, 0] + post["b"][idx, 0] * (H_S1 - Hbar), sigma[idx])
    H_S2 = rng.normal(post["h"][idx, 1], tau[idx])
    W_S2 = rng.normal(post["a"][idx, 1] + post["b"][idx, 1] * (H_S2 - Hbar), sigma[idx])
    return W_S2 - W_S1


def integrated_categorical_posterior(W, S):
    """Independent integration for indexed-intercept model W ~ Normal(a[S], sigma).

    Analytically integrate out a[1] and a[2] conditional on sigma; numerically
    integrate sigma on a grid. Returns posterior means and covariance for
    (a[1], a[2], sigma).
    """
    s1 = S == 1; s2 = S == 2
    n1, n2 = int(s1.sum()), int(s2.sum())
    w1bar, w2bar = float(W[s1].mean()), float(W[s2].mean())
    ss1 = float(((W[s1] - w1bar) ** 2).sum())
    ss2 = float(((W[s2] - w2bar) ** 2).sum())

    sigma_grid = np.linspace(0.01, 10, 2001)
    ds = sigma_grid[1] - sigma_grid[0]
    S2 = sigma_grid ** 2

    var1 = 1.0 / (n1 / S2 + 1.0 / 100)
    mean1 = var1 * (n1 * w1bar / S2 + 60.0 / 100)
    var2 = 1.0 / (n2 / S2 + 1.0 / 100)
    mean2 = var2 * (n2 * w2bar / S2 + 60.0 / 100)

    log_p = (-(n1 + n2 - 2) * np.log(sigma_grid)
             - 0.5 * np.log(S2 + n1 * 100) - 0.5 * np.log(S2 + n2 * 100)
             - ss1 / (2 * S2) - ss2 / (2 * S2)
             - (w1bar - 60) ** 2 / (2 * (100 + S2 / n1))
             - (w2bar - 60) ** 2 / (2 * (100 + S2 / n2)))
    log_p -= log_p.max()
    weights = np.exp(log_p)
    weights[0] *= 0.5; weights[-1] *= 0.5
    weights /= weights.sum()

    means = np.array([(weights * mean1).sum(),
                      (weights * mean2).sum(),
                      (weights * sigma_grid).sum()])
    values = [mean1, mean2, sigma_grid]
    cov = np.zeros((3, 3))
    for i in range(3):
        for j in range(3):
            cov[i, j] = (weights * (values[i] - means[i]) * (values[j] - means[j])).sum()
    cov[0, 0] += (weights * var1).sum()
    cov[1, 1] += (weights * var2).sum()

    boundary = float(weights[:2].sum() + weights[-2:].sum())
    return means, cov, boundary
