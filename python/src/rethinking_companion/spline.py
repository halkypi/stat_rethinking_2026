"""B-spline basis construction matching R's bs() via scipy.interpolate.BSpline."""
from .runtime import configure_runtime
configure_runtime()

import hashlib
import json
from pathlib import Path
import numpy as np
import pandas as pd
import pymc as pm
from scipy.interpolate import BSpline


def bspline_basis(x, num_knots, degree=3, intercept=False):
    """Construct a B-spline basis matrix matching R's bs().

    Parameters
    ----------
    x : array-like
        Predictor values.
    num_knots : int
        Number of equally spaced knots spanning [min(x), max(x)].
        These are passed as internal knots (R's ``knots`` argument);
        boundary knots are placed at min(x) and max(x) automatically.
    degree : int
        Polynomial degree of the B-spline (default 3 = cubic).
    intercept : bool
        If False (default), drop the first basis column to match
        R's ``bs(..., intercept=FALSE)``.

    Returns
    -------
    B : ndarray, shape (n_basis, n_obs)
        Basis matrix transposed to match the R source convention
        ``B <- t(bs(...))``.
    knots : ndarray
        The internal knot positions used.
    """
    x = np.asarray(x, dtype=float)
    lo, hi = float(x.min()), float(x.max())
    internal_knots = np.linspace(lo, hi, num_knots)
    # Extend boundary knots slightly beyond data range so scipy's half-open
    # interval convention does not zero out the last observation.
    eps = (hi - lo) * 1e-6
    t = np.concatenate([
        np.repeat(lo - eps, degree + 1),
        internal_knots,
        np.repeat(hi + eps, degree + 1),
    ])
    B = BSpline.design_matrix(x, t, degree).toarray()
    if not intercept:
        B = B[:, 1:]
    return B.T, internal_knots


def load_cherry_blossoms():
    """Load cherry blossoms data with checksum verification."""
    folder = Path(__file__).resolve().parents[2] / "data"
    payload = (folder / "cherry_blossoms.csv").read_bytes()
    provenance = json.loads((folder / "cherry_blossoms.provenance.json").read_text())
    if hashlib.sha256(payload).hexdigest() != provenance["sha256"]:
        raise ValueError("cherry_blossoms checksum differs from recorded upstream file")
    data = pd.read_csv(folder / "cherry_blossoms.csv", sep=";")
    expected_cols = ["year", "doy", "temp", "temp_upper", "temp_lower"]
    if list(data.columns) != expected_cols or len(data) != 1215:
        raise ValueError("Unexpected cherry_blossoms schema")
    return data


def fit_cherry_spline(year, doy, B, *, tau=10, seed=801, draws=1500, tune=1000):
    """Fit Y ~ Normal(a0 + a*B, exp(log_sigma)) with four-chain NUTS.

    Matches the R source model:
        Y ~ dnorm(mu, exp(log_sigma))
        mu <- a0 + as.vector(a %*% B)
        a0 ~ dnorm(100, 1)
        a ~ dnorm(0, tau)
        log_sigma ~ dnorm(0, 0.5)
    """
    n_basis = B.shape[0]
    n_obs = B.shape[1]
    with pm.Model(coords={"basis": np.arange(n_basis), "obs": np.arange(n_obs)}):
        a0 = pm.Normal("a0", 100, 1)
        a = pm.Normal("a", 0, tau, dims="basis")
        log_sigma = pm.Normal("log_sigma", 0, 0.5)
        mu = pm.Deterministic("mu", a0 + pm.math.dot(a, B), dims="obs")
        pm.Normal("Y", mu, pm.math.exp(log_sigma), observed=doy, dims="obs")
        prior = pm.sample_prior_predictive(draws=500, random_seed=seed + 1)
        idata = pm.sample(draws=draws, tune=tune, chains=4, cores=1,
                          random_seed=seed, target_accept=0.9,
                          progressbar=False, return_inferencedata=True)
        pm.sample_posterior_predictive(idata, var_names=["Y"], random_seed=seed + 2,
                                       extend_inferencedata=True, progressbar=False)
    idata.extend(prior)
    idata.attrs["tau"] = tau
    idata.attrs["random_seed"] = seed
    return idata


def fit_howell_spline(age, height, B, *, tau=25, seed=802, draws=1500, tune=1000):
    """Fit height ~ Normal(a0 + a*B, exp(log_sigma)) on all-age Howell1 data.

    Matches the R source model:
        Y ~ dnorm(mu, exp(log_sigma))
        mu <- a0 + as.vector(a %*% B)
        a0 ~ dnorm(120, 1)
        a ~ dnorm(0, tau)
        log_sigma ~ dnorm(0, 0.5)
    """
    n_basis = B.shape[0]
    n_obs = B.shape[1]
    with pm.Model(coords={"basis": np.arange(n_basis), "obs": np.arange(n_obs)}):
        a0 = pm.Normal("a0", 120, 1)
        a = pm.Normal("a", 0, tau, dims="basis")
        log_sigma = pm.Normal("log_sigma", 0, 0.5)
        mu = pm.Deterministic("mu", a0 + pm.math.dot(a, B), dims="obs")
        pm.Normal("Y", mu, pm.math.exp(log_sigma), observed=height, dims="obs")
        idata = pm.sample(draws=draws, tune=tune, chains=4, cores=1,
                          random_seed=seed, target_accept=0.9,
                          progressbar=False, return_inferencedata=True)
    idata.attrs["tau"] = tau
    idata.attrs["random_seed"] = seed
    return idata
