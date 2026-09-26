"""First PyMC fitting pattern: a regression with an independently known posterior."""
import marimo

__generated_with = "0.25.0"
app = marimo.App(width="medium")


@app.cell
def _():
    from rethinking_companion.gaussian_regression import (
        assert_diagnostics, design_matrix, diagnostics, exact_posterior,
        fit_gaussian, linear_data,
    )
    import altair as alt
    import marimo as mo
    import numpy as np
    import pandas as pd
    from scipy import stats
    return alt, assert_diagnostics, design_matrix, diagnostics, exact_posterior, fit_gaussian, linear_data, mo, np, pd, stats


@app.cell
def _(mo):
    mo.md(r"""
    # Learn a regression, then check the computation

    In `scripts/03_prior_pred_OLS.r`, the first model is
    $a,b\sim\mathrm{Normal}(0,1)$ independently and
    $y_i\sim\mathrm{Normal}(a+bx_i,1)$.
    The second argument is a standard deviation. A line is the **conditional
    mean**, not an assertion that every observation lies on that line.

    We activate the source's intended ten-point learning example; its current
    script overwrites `n_points = 10` with zero. Our fixed synthetic data use
    clipped Normal x values, true intercept 0, slope 0.7 and noise SD 0.5.
    The **fitted** noise SD stays at 1, as in R. This intentional discrepancy
    makes the fitted predictive distribution more dispersed than the generator.

    The reusable helper in `src/rethinking_companion/gaussian_regression.py`
    uses a labeled PyMC coefficient vector, four NUTS chains, prior simulation,
    in-sample predictive replication and a separate new-x prediction model.
    Executing this notebook fits the model; no saved fit is silently substituted.
    Changing the observation slider below uses the exact Gaussian solution,
    so it does not restart MCMC.
    """)
    return


@app.cell
def _(design_matrix, linear_data, np):
    x, y = linear_data()
    X = design_matrix(x)
    x_grid = np.linspace(-2.2, 2.2, 81)
    X_grid = design_matrix(x_grid)
    return X, X_grid, x, x_grid, y


@app.cell
def _(X, X_grid, fit_gaussian, y):
    fit = fit_gaussian(X, y, X_grid)
    return (fit,)


@app.cell
def _(assert_diagnostics, diagnostics, fit, mo):
    diagnostic_table, diagnostic_values = diagnostics(fit)
    assert_diagnostics(diagnostic_values)
    mo.vstack([
        mo.md("## Check the sampler\nFour chains must agree. We require R-hat < 1.01, bulk and tail ESS > 400, "
              "zero divergences, BFMI > 0.3 and no maximum-depth saturation. These are computational checks, not proof of model adequacy."),
        mo.ui.table(diagnostic_table.reset_index(names="Parameter"), selection=None, show_data_types=False),
        mo.md(f"Divergences: **{diagnostic_values['divergences']}**; minimum BFMI: **{diagnostic_values['min_bfmi']:.3f}**."),
    ])
    return diagnostic_table, diagnostic_values


@app.cell
def _(mo):
    prefix = mo.ui.slider(0, 10, value=10, step=1, label="Observed data points (exact update)", show_value=True)
    prefix
    return (prefix,)


@app.cell
def _(X, X_grid, exact_posterior, np, pd, prefix, stats, x_grid, y):
    exact_mean, exact_covariance = exact_posterior(X[:prefix.value], y[:prefix.value])
    mu_mean = X_grid @ exact_mean
    mu_sd = np.sqrt(np.einsum("ij,jk,ik->i", X_grid, exact_covariance, X_grid))
    predictive_sd = np.sqrt(mu_sd**2 + 1)
    z = stats.norm.ppf(0.945)  # central 89% interval
    bands = pd.DataFrame({"x": x_grid, "Mean": mu_mean,
        "Mean lower": mu_mean-z*mu_sd, "Mean upper": mu_mean+z*mu_sd,
        "Prediction lower": mu_mean-z*predictive_sd, "Prediction upper": mu_mean+z*predictive_sd})
    return bands, exact_covariance, exact_mean, mu_mean, mu_sd, predictive_sd


@app.cell
def _(alt, bands, mo, pd, prefix, x, y):
    band_base = alt.Chart(bands).encode(x="x:Q")
    regression_chart = (
        band_base.mark_area(color="#aebfca", opacity=.35).encode(y=alt.Y("Prediction lower:Q", title="Outcome y"), y2="Prediction upper:Q")
        + band_base.mark_area(color="#167c80", opacity=.35).encode(y="Mean lower:Q", y2="Mean upper:Q")
        + band_base.mark_line(color="#167c80").encode(y="Mean:Q")
        + alt.Chart(pd.DataFrame({"x":x[:prefix.value], "y":y[:prefix.value]})).mark_point(filled=True,color="black").encode(x="x:Q",y="y:Q")
    ).properties(width=550,height=260)
    mo.vstack([mo.md(f"## Learning from {prefix.value} observations\nTeal: central 89% uncertainty about the mean line. "
                     "Gray: central 89% prediction interval for a new outcome. At zero observations these are prior distributions."), regression_chart])
    return (regression_chart,)


@app.cell
def _(X_grid, alt, fit, mo, pd, x_grid):
    prior_beta = fit.prior.beta.values.reshape(-1, 2)[:20]
    prior_means = X_grid @ prior_beta.T
    prior_lines = pd.DataFrame([
        {"x":float(value), "Mean":float(prior_means[i,j]), "Draw":str(j)}
        for i,value in enumerate(x_grid) for j in range(20)
    ])
    prior_chart = alt.Chart(prior_lines).mark_line(opacity=.35).encode(
        x="x:Q", y=alt.Y("Mean:Q", title="Prior conditional mean"), detail="Draw:N",
    ).properties(width=550,height=200)
    mo.vstack([mo.md("## The prior implies whole functions\nThese are 20 mean lines from PyMC prior coefficient draws. "
                     "A prior predictive **outcome** adds Normal noise around each line; it is not the same as a mean line."), prior_chart])
    return (prior_chart,)


@app.cell
def _(X, exact_posterior, fit, mo, np, pd, y):
    final_mean, final_cov = exact_posterior(X,y)
    sampled = fit.posterior.beta.values.reshape(-1,2)
    comparison = pd.DataFrame({"Parameter":["intercept", "slope"],
        "Exact mean":final_mean, "NUTS mean":sampled.mean(axis=0),
        "Exact SD":np.sqrt(np.diag(final_cov)), "NUTS SD":sampled.std(axis=0,ddof=1)})
    mo.vstack([
        mo.md(r"""
        ## An independent answer

        With design matrix X (columns 1 and x), unit noise and standard Normal
        priors, $V=(I+X^TX)^{-1}$ and $m=VX^Ty$. The posterior coefficients are
        jointly Normal(m,V). The code solves linear systems instead of explicitly
        inverting matrices. Here `quap`'s quadratic approximation is exact;
        using NUTS provides a thoroughly checkable foundation for later models
        where the posterior is not Gaussian.
        """),
        mo.ui.table(comparison, selection=None, show_data_types=False,
                    format_mapping={c:lambda v:f"{v:.4f}" for c in comparison.columns if c != "Parameter"}),
        mo.md("The verification script checks the full covariance, not just marginal means; it also checks independent numerical quadrature, every sequential update, and predictive moments. "
              "Posterior samples keep chain/draw dimensions for diagnostics; flatten them only when constructing plotting summaries."),
    ])
    return (comparison,)


if __name__ == "__main__":
    app.run()
