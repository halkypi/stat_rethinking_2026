"""Known-noise Gaussian regression, with exact inference as an independent oracle."""
from .runtime import configure_runtime
configure_runtime()

import arviz as az
import numpy as np
import pymc as pm


def linear_data(seed=2971):
    """Activate the R script's intended 10-point demo (it overwrites n with 0)."""
    rng = np.random.default_rng(seed)
    x = np.clip(rng.normal(size=10), -2, 2)
    y = rng.normal(0.7*x, 0.5)
    return x, y


def regression_case(kind="Linear"):
    """Source-backed polynomial scenarios; R and NumPy seed streams differ."""
    if kind == "Linear":
        x,y = linear_data()
        return x,y,1,np.linspace(-2.2,2.2,81)
    if kind not in ("Quadratic", "Cubic"):
        raise ValueError(f"Unknown regression case: {kind}")
    degree = 2 if kind == "Quadratic" else 3
    rng = np.random.default_rng(12 if degree == 2 else 13)
    x = np.clip(rng.normal(size=10), -2, 2)
    mean = .7*x-x*x if degree == 2 else .7*x-2*x*x+3*x**3
    y = rng.normal(mean,.5)
    if degree == 2:
        x[8],y[8] = 3.,-1.  # R x[9], y[9]: deliberately influential observation.
        grid = np.linspace(-4,5,91)
    else:
        grid = np.linspace(x.min()-2,x.max()+2,91)
    return x,y,degree,grid


def design_matrix(x, degree=1):
    return np.vander(np.asarray(x), N=degree+1, increasing=True)


def exact_posterior(X, y, sigma=1.0):
    """For independent Normal(0,1) coefficients and fixed observation sigma."""
    X, y = np.asarray(X), np.asarray(y)
    precision = np.eye(X.shape[1]) + X.T @ X / sigma**2
    covariance = np.linalg.solve(precision, np.eye(X.shape[1]))
    mean = np.linalg.solve(precision, X.T @ y / sigma**2)
    return mean, covariance


def fit_gaussian(X, y, X_grid, *, sigma=1.0, seed=731, draws=1500, tune=1000):
    """Fit four chains and return labeled prior, posterior and predictive groups.

    The training and prediction models share coefficient names and dimensions.
    Separate prediction coordinates avoid changing the training observations.
    No disk fit cache is used: executing this operation actually samples.
    """
    X, y, X_grid = map(np.asarray, (X, y, X_grid))
    labels = ["intercept"] + [f"x^{j}" for j in range(1, X.shape[1])]
    with pm.Model(coords={"coefficient": labels, "observation": np.arange(len(y))}):
        beta = pm.Normal("beta", mu=0, sigma=1, dims="coefficient")
        mu = pm.Deterministic("mu", pm.math.dot(X, beta), dims="observation")
        pm.Normal("y", mu=mu, sigma=sigma, observed=y, dims="observation")
        prior = pm.sample_prior_predictive(draws=1000, random_seed=seed+1)
        idata = pm.sample(draws=draws, tune=tune, chains=4, cores=1,
                          random_seed=seed, target_accept=0.9, progressbar=False,
                          return_inferencedata=True)
        pm.sample_posterior_predictive(idata, var_names=["y"], random_seed=seed+2,
                                      extend_inferencedata=True, progressbar=False)
    idata.extend(prior)
    # Reusing names conditions beta on its joint posterior; only y_new is sampled.
    with pm.Model(coords={"coefficient": labels, "prediction": np.arange(len(X_grid))}):
        beta = pm.Normal("beta", mu=0, sigma=1, dims="coefficient")
        mu_new = pm.Deterministic("mu_new", pm.math.dot(X_grid, beta), dims="prediction")
        pm.Normal("y_new", mu=mu_new, sigma=sigma, dims="prediction")
        pm.sample_posterior_predictive(idata, var_names=["mu_new", "y_new"],
                                      predictions=True, random_seed=seed+3,
                                      extend_inferencedata=True, progressbar=False)
    return idata


def diagnostics(idata, var_names=("beta",)):
    summary = az.summary(idata, var_names=list(var_names), kind="all", round_to=None)
    values = {
        "max_rhat": float(az.rhat(idata, var_names=list(var_names)).to_array().max()),
        "min_ess_bulk": float(az.ess(idata, var_names=list(var_names), method="bulk").to_array().min()),
        "min_ess_tail": float(az.ess(idata, var_names=list(var_names), method="tail").to_array().min()),
        "divergences": int(idata.sample_stats.diverging.sum()),
        "min_bfmi": float(np.min(az.bfmi(idata))),
        "max_tree_depth": int(idata.sample_stats.tree_depth.max()),
    }
    return summary, values


def assert_diagnostics(values):
    assert values["max_rhat"] < 1.01, values
    assert values["min_ess_bulk"] > 400, values
    assert values["min_ess_tail"] > 400, values
    assert values["divergences"] == 0, values
    assert values["min_bfmi"] > 0.3, values
    assert values["max_tree_depth"] < 10, values
