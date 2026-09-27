"""MCMC mechanics helpers: data loaders, King Markov, leapfrog, R-hat.

Pedagogical implementations from 08_MCMC.r and LB03_ess acf example.r.
These illustrate how MCMC works internally — they do not replace PyMC.
"""
from .runtime import configure_runtime
configure_runtime()

import hashlib
import json
from pathlib import Path
import numpy as np
import pandas as pd
import pymc as pm


# ---------------------------------------------------------------------------
# Data loaders
# ---------------------------------------------------------------------------

def load_waffle_divorce():
    folder = Path(__file__).resolve().parents[2] / "data"
    payload = (folder / "WaffleDivorce.csv").read_bytes()
    provenance = json.loads((folder / "WaffleDivorce.provenance.json").read_text())
    if hashlib.sha256(payload).hexdigest() != provenance["sha256"]:
        raise ValueError("WaffleDivorce checksum mismatch")
    data = pd.read_csv(folder / "WaffleDivorce.csv", sep=";")
    if len(data) != 50 or data.isna().any().any():
        raise ValueError("Unexpected WaffleDivorce schema")
    for col in ("Divorce", "Marriage", "MedianAgeMarriage"):
        if col not in data.columns:
            raise ValueError(f"Missing column: {col}")
    return data


def load_bangladesh():
    folder = Path(__file__).resolve().parents[2] / "data"
    payload = (folder / "bangladesh.csv").read_bytes()
    provenance = json.loads((folder / "bangladesh.provenance.json").read_text())
    if hashlib.sha256(payload).hexdigest() != provenance["sha256"]:
        raise ValueError("Bangladesh checksum mismatch")
    data = pd.read_csv(folder / "bangladesh.csv", sep=";")
    if len(data) != 1934:
        raise ValueError(f"Expected 1934 rows, got {len(data)}")
    for col in ("district", "use.contraception", "urban"):
        if col not in data.columns:
            raise ValueError(f"Missing column: {col}")
    return data


# ---------------------------------------------------------------------------
# King Markov sampler (08_MCMC.r lines 1-18)
# ---------------------------------------------------------------------------

def king_markov(n_steps=100_000, seed=None):
    """Metropolis sampler on a discrete 10-island archipelago.

    Island populations are proportional to 1..10. Proposal: current ± 1
    with wrap-around. Acceptance ratio: population[proposal] / population[current].
    """
    rng = np.random.default_rng(seed)
    populations = np.arange(1, 11, dtype=float)
    positions = np.empty(n_steps, dtype=int)
    current = 9  # 0-indexed island 10
    for i in range(n_steps):
        positions[i] = current
        step = rng.choice([-1, 1])
        proposal = (current + step) % 10
        prob_move = populations[proposal] / populations[current]
        if rng.random() < prob_move:
            current = proposal
    return positions


# ---------------------------------------------------------------------------
# Leapfrog integrator (08_MCMC.r lines 167-525)
# ---------------------------------------------------------------------------

def hmc_leapfrog(U, grad_U, step_size, n_leapfrog, q_init, *, seed=None):
    """One HMC proposal: leapfrog integration with Metropolis accept/reject.

    Returns dict with keys: q_final, trajectory (L+1 x d), H_init, H_final,
    accepted (bool), dH.
    """
    rng = np.random.default_rng(seed)
    q = np.array(q_init, dtype=float)
    d = len(q)
    p = rng.normal(size=d)

    trajectory = np.empty((n_leapfrog + 1, d))
    trajectory[0] = q.copy()

    H_init = U(q) + 0.5 * np.dot(p, p)

    # half step for momentum
    p = p - 0.5 * step_size * grad_U(q)

    for l in range(n_leapfrog):
        q = q + step_size * p
        trajectory[l + 1] = q.copy()
        if l < n_leapfrog - 1:
            p = p - step_size * grad_U(q)

    # final half step for momentum
    p = p - 0.5 * step_size * grad_U(q)
    p = -p  # negate for reversibility

    H_final = U(q) + 0.5 * np.dot(p, p)
    dH = H_final - H_init

    accepted = rng.random() < np.exp(-dH)
    q_final = q if accepted else np.array(q_init, dtype=float)

    return {
        "q_final": q_final,
        "trajectory": trajectory,
        "H_init": float(H_init),
        "H_final": float(H_final),
        "dH": float(dH),
        "accepted": bool(accepted),
    }


def hmc_sample(U, grad_U, step_size, n_leapfrog, q_init, n_samples, *, seed=None):
    """Run multiple HMC steps, returning samples and trajectory metadata."""
    rng = np.random.default_rng(seed)
    samples = []
    trajectories = []
    q = np.array(q_init, dtype=float)
    for _ in range(n_samples):
        result = hmc_leapfrog(U, grad_U, step_size, n_leapfrog, q, seed=rng)
        q = result["q_final"]
        samples.append(q.copy())
        trajectories.append(result)
    return np.array(samples), trajectories


def make_2d_target(y, a=0, b=1, k=0, d=0.5):
    """Return (U, grad_U) for the 2D (mu, log_sigma) target from 08_MCMC.r."""
    y = np.asarray(y)
    n = len(y)

    def U(q):
        mu, log_s = q
        s = np.exp(log_s)
        ll = -0.5 * n * np.log(2 * np.pi) - n * log_s - 0.5 * np.sum((y - mu) ** 2) / s ** 2
        lp_mu = -0.5 * (mu - a) ** 2 / b ** 2
        lp_logs = -0.5 * (log_s - k) ** 2 / d ** 2
        return -(ll + lp_mu + lp_logs)

    def grad_U(q):
        mu, log_s = q
        s = np.exp(log_s)
        G1 = np.sum(y - mu) / s ** 2 + (a - mu) / b ** 2
        G2 = np.sum((y - mu) ** 2) / s ** 2 - n + (k - log_s) / d ** 2
        return np.array([-G1, -G2])

    return U, grad_U


def make_correlated_target(y, a=0, b=0.5):
    """Return (U, grad_U) for the correlated a1+a2 target from 08_MCMC.r."""
    y = np.asarray(y)
    n = len(y)

    def U(q):
        mu = q[0] + q[1]
        ll = -0.5 * np.sum((y - mu) ** 2)
        lp = -0.5 * (q[0] - a) ** 2 / b ** 2 - 0.5 * (q[1] - a) ** 2 / b ** 2
        return -(ll + lp)

    def grad_U(q):
        mu = q[0] + q[1]
        G1 = np.sum(y - mu) + (a - q[0]) / b ** 2
        G2 = np.sum(y - mu) + (a - q[1]) / b ** 2
        return np.array([-G1, -G2])

    return U, grad_U


# ---------------------------------------------------------------------------
# R-hat computation (08_MCMC.r lines 567-580)
# ---------------------------------------------------------------------------

def rhat_over_time(chains):
    """Compute within-chain variance W and between-chain variance B vs sample size.

    chains: array of shape (n_draws, n_chains).
    Returns W_array, B_array of length n_draws.
    """
    chains = np.asarray(chains)
    n_draws, n_chains = chains.shape
    W = np.empty(n_draws)
    B = np.empty(n_draws)
    for t in range(1, n_draws + 1):
        segment = chains[:t, :]
        chain_vars = np.var(segment, axis=0, ddof=1) if t > 1 else np.zeros(n_chains)
        chain_means = np.mean(segment, axis=0)
        W[t - 1] = np.mean(chain_vars)
        B[t - 1] = np.var(chain_means, ddof=1) if t > 1 else 0.0
    return W, B


# ---------------------------------------------------------------------------
# PyMC model builders
# ---------------------------------------------------------------------------

def fit_waffle_divorce(dat, *, seed=801, draws=1500, tune=1000):
    """D ~ Normal(a + bM*M + bA*A, sigma) on standardized WaffleDivorce data."""
    D, M, A = dat["D"], dat["M"], dat["A"]
    with pm.Model(coords={"obs": np.arange(len(D))}):
        a = pm.Normal("a", 0, 0.2)
        bM = pm.Normal("bM", 0, 0.5)
        bA = pm.Normal("bA", 0, 0.5)
        sigma = pm.Exponential("sigma", 1)
        mu = pm.Deterministic("mu", a + bM * M + bA * A, dims="obs")
        pm.Normal("D", mu, sigma, observed=D, dims="obs")
        idata = pm.sample(draws=draws, tune=tune, chains=4, cores=1,
                          random_seed=seed, target_accept=0.9,
                          progressbar=False, return_inferencedata=True)
    return idata


def fit_bad_chains(y, alpha_prior_sd, sigma_prior_rate, *, n_chains=3, seed=811,
                   draws=1000, tune=1000):
    """y ~ Normal(alpha, sigma) with specified priors. For bad/good chain comparison."""
    with pm.Model():
        alpha = pm.Normal("alpha", 0 if sigma_prior_rate < 0.01 else 1, alpha_prior_sd)
        sigma = pm.Exponential("sigma", sigma_prior_rate)
        pm.Normal("y", alpha, sigma, observed=y)
        idata = pm.sample(draws=draws, tune=tune, chains=n_chains, cores=1,
                          random_seed=seed, target_accept=0.9,
                          progressbar=False, return_inferencedata=True)
    return idata


def fit_bangladesh(dat, *, seed=821, draws=1500, tune=2000):
    """Hierarchical contraception model with 61 varying intercepts and slopes.

    Uses non-centered parameterization to avoid the funnel geometry that
    makes centered hierarchical models difficult for HMC.
    """
    C, D, U = dat["C"], dat["D"], dat["U"]
    n_districts = 61
    coords = {"district": np.arange(n_districts), "obs": np.arange(len(C))}
    with pm.Model(coords=coords):
        abar = pm.Normal("abar", 0, 1)
        bbar = pm.Normal("bbar", 0, 1)
        sigma = pm.Exponential("sigma", 1)
        tau = pm.Exponential("tau", 1)
        # non-centered: a = abar + sigma * a_offset
        a_offset = pm.Normal("a_offset", 0, 1, dims="district")
        b_offset = pm.Normal("b_offset", 0, 1, dims="district")
        a = pm.Deterministic("a", abar + sigma * a_offset, dims="district")
        b = pm.Deterministic("b", bbar + tau * b_offset, dims="district")
        logit_p = a[D] + b[D] * U
        pm.Bernoulli("C", logit_p=logit_p, observed=C, dims="obs")
        idata = pm.sample(draws=draws, tune=tune, chains=4, cores=1,
                          random_seed=seed, target_accept=0.99,
                          progressbar=False, return_inferencedata=True)
    return idata


def fit_1000dim_normal(*, seed=831, draws=1000, tune=1000):
    """1000-dim Normal(0,1) with theta^2 derived quantity for ESS demonstration."""
    D = 1000
    coords = {"dim": np.arange(D)}
    with pm.Model(coords=coords):
        theta = pm.Normal("theta", 0, 1, dims="dim")
        pm.Deterministic("theta_sq", theta ** 2, dims="dim")
        idata = pm.sample(draws=draws, tune=tune, chains=4, cores=1,
                          random_seed=seed, target_accept=0.9,
                          progressbar=False, return_inferencedata=True)
    return idata
