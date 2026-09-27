"""Simulation-based model validation: fit, recover, repeat."""
import marimo

__generated_with = "0.25.0"
app = marimo.App(width="medium")


@app.cell
def _():
    from rethinking_companion.runtime import configure_runtime
    configure_runtime()
    import altair as alt
    import marimo as mo
    import numpy as np
    import pandas as pd
    import pymc as pm
    return alt, mo, np, pd, pm


@app.cell
def _(mo):
    mo.md(r"""
    # Simulation-based model validation

    Source: `scripts/LA04_sim heights validate example.r`. The core idea:
    simulate data from known parameters, fit the model, check whether the
    posterior recovers the truth. Repeat many times to assess coverage.

    This is not full simulation-based calibration (SBC), but it demonstrates
    the essential workflow: **if you cannot recover parameters you chose,
    your model or fitting procedure has a problem.**

    Model: $W_i \sim \mathrm{Normal}(a + bH_i, \sigma)$ with $a \sim
    \mathrm{Normal}(0,10)$, $b \sim \mathrm{Uniform}(0,1)$, $\sigma \sim
    \mathrm{Uniform}(0,10)$.
    """)
    return


@app.cell
def _(mo):
    n_reps = mo.ui.dropdown(
        ["10", "50", "100"],
        value="100",
        label="Number of replications",
    )
    n_reps
    return (n_reps,)


@app.cell
def _(n_reps, np, pm):
    b_true = 0.5
    n_obs = 100
    reps = int(n_reps.value)

    results = []
    for i in range(reps):
        rng = np.random.default_rng(93 + i)
        H = rng.uniform(130, 170, n_obs)
        W = rng.normal(b_true * H, 5)
        with pm.Model():
            a = pm.Normal("a", 0, 10)
            b = pm.Uniform("b", 0, 1)
            sigma = pm.Uniform("sigma", 0, 10)
            mu = a + b * H
            pm.Normal("W", mu, sigma, observed=W)
            idata = pm.sample(draws=500, tune=500, chains=2, cores=1,
                              random_seed=i, target_accept=0.9,
                              progressbar=False, return_inferencedata=True)
        b_draws = idata.posterior["b"].values.ravel()
        b_mean = float(b_draws.mean())
        b_lo = float(np.quantile(b_draws, 0.055))
        b_hi = float(np.quantile(b_draws, 0.945))
        results.append({"rep": i, "b_mean": b_mean, "b_lo": b_lo, "b_hi": b_hi,
                         "covers": b_lo <= b_true <= b_hi})
    return b_true, results, reps


@app.cell
def _(alt, b_true, mo, np, pd, results, reps):
    df = pd.DataFrame(results)
    coverage = float(df["covers"].mean())

    base = alt.Chart(df).encode(y=alt.Y("rep:O", axis=None))
    interval_chart = (
        base.mark_rule(strokeWidth=2).encode(
            x=alt.X("b_lo:Q", title="b", scale=alt.Scale(domain=[0.3, 0.7])),
            x2="b_hi:Q",
            color=alt.condition(alt.datum.covers, alt.value("steelblue"), alt.value("firebrick")),
        )
        + base.mark_point(size=30, filled=True).encode(
            x="b_mean:Q",
            color=alt.condition(alt.datum.covers, alt.value("steelblue"), alt.value("firebrick")),
        )
        + alt.Chart(pd.DataFrame({"x": [b_true]})).mark_rule(
            color="black", strokeDash=[4, 4], strokeWidth=2
        ).encode(x="x:Q")
    ).properties(width=500, height=max(200, reps * 4))

    n_miss = int((~df["covers"]).sum())
    mo.vstack([
        mo.md(f"## Recovery of b = {b_true}\n"
              f"**{reps} replications**, n = 100 each, 89% intervals. "
              f"Coverage: **{coverage:.0%}** ({n_miss} misses). "
              f"Expected coverage is 89%; a single run's coverage is a random "
              f"variable with SD ≈ {np.sqrt(0.89 * 0.11 / reps):.2f}. "
              "Red intervals miss the true value."),
        interval_chart,
    ])
    return coverage, df


@app.cell
def _(mo):
    mo.md(r"""
    ## What this teaches

    - If many intervals miss the truth, something is wrong with the model or
      the fitting procedure.
    - If coverage is close to the nominal level, that is **necessary but not
      sufficient** — the model could still be wrong for real data.
    - Each replication uses a fresh dataset drawn from the generative model.
      The posterior is specific to that dataset; the coverage rate summarizes
      the procedure's reliability across datasets.
    - This uses 2 chains × 500 draws per replication to keep runtime
      practical. The full check script uses 4 chains × 1500 draws for one
      representative fit.

    The R source uses `quap` (Gaussian approximation); here NUTS is used
    throughout. For this linear Normal model the posteriors are equivalent.
    """)
    return


if __name__ == "__main__":
    app.run()
