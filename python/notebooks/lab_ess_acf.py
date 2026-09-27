"""ESS and autocorrelation diagnostics: Bangladesh hierarchical model + 1000-dim demo."""
import marimo

__generated_with = "0.25.0"
app = marimo.App(width="medium")


@app.cell
def _():
    from rethinking_companion.mcmc import (
        fit_bangladesh, fit_1000dim_normal, load_bangladesh,
    )
    from rethinking_companion.gaussian_regression import assert_diagnostics, diagnostics
    import altair as alt
    import arviz as az
    import marimo as mo
    import numpy as np
    import pandas as pd
    return (alt, assert_diagnostics, az, diagnostics, fit_bangladesh,
            fit_1000dim_normal, load_bangladesh, mo, np, pd)


# ── Section 1: Bangladesh Hierarchical Model ────────────────────────────────

@app.cell
def _(mo):
    mo.md(r"""
    # ESS and Autocorrelation Diagnostics

    Source: `scripts/LB03_ess acf example.r`.

    ## Bangladesh Hierarchical Model

    Contraception use (binary) modeled with 61 varying intercepts and
    61 varying slopes by district, plus hyperpriors. The pedagogical
    focus is on diagnosing ESS and ACF from this complex model.

    $$
    C_i \sim \text{Bernoulli}(\text{logit}^{-1}(a_{D_i} + b_{D_i} \cdot U_i))
    $$

    $a_d \sim \text{Normal}(\bar{a}, \sigma)$, $b_d \sim \text{Normal}(\bar{b}, \tau)$,
    $\bar{a}, \bar{b} \sim \text{Normal}(0, 1)$, $\sigma, \tau \sim \text{Exp}(1)$.
    """)
    return


@app.cell
def _(load_bangladesh, np):
    bd = load_bangladesh()
    dat_bd = {
        "C": bd["use.contraception"].values.astype(np.int64),
        "D": (bd["district"].values - 1).astype(np.int64),  # 0-indexed
        "U": bd["urban"].values.astype(np.float64),
    }
    return (bd, dat_bd)


@app.cell
def _(dat_bd, fit_bangladesh):
    fit_bd = fit_bangladesh(dat_bd)
    return (fit_bd,)


@app.cell
def _(assert_diagnostics, diagnostics, fit_bd, mo):
    summary_bd, diag_bd = diagnostics(fit_bd, ("abar", "bbar", "sigma", "tau"))
    assert_diagnostics(diag_bd)
    mo.md(f"""
    ### Hyperparameter diagnostics

    - R-hat: {diag_bd['max_rhat']:.4f}
    - Min bulk ESS: {diag_bd['min_ess_bulk']:.0f}
    - Min tail ESS: {diag_bd['min_ess_tail']:.0f}
    - Divergences: {diag_bd['divergences']}
    - Min BFMI: {diag_bd['min_bfmi']:.3f}
    """)
    return (diag_bd, summary_bd)


@app.cell
def _(alt, fit_bd, np, pd):
    _a_means = fit_bd.posterior["a"].mean(dim=("chain", "draw")).values
    _abar = float(fit_bd.posterior["abar"].mean())
    _df_a = pd.DataFrame({
        "district": np.arange(61),
        "intercept_mean": _a_means,
    })
    _base = alt.Chart(_df_a).mark_point(size=40).encode(
        x=alt.X("district:O", title="District"),
        y=alt.Y("intercept_mean:Q", title="Posterior mean intercept"),
    )
    _rule = alt.Chart(pd.DataFrame({"y": [_abar]})).mark_rule(
        color="red", strokeDash=[4, 4]).encode(y="y:Q")
    chart_shrinkage = (_base + _rule).properties(
        title="Varying intercepts (red line = grand mean ā)", width=600, height=250)
    chart_shrinkage
    return (chart_shrinkage,)


# ── Section 2: 1000-Dimensional ESS Demonstration ──────────────────────────

@app.cell
def _(mo):
    mo.md(r"""
    ## 1000-Dimensional ESS Demonstration

    Fit $\theta_d \sim \text{Normal}(0, 1)$ for $d = 1, \ldots, 1000$ and
    compute $\theta^2_d = \theta_d^2$ as a derived quantity. Although $\theta$
    has high ESS, $\theta^2$ has much lower ESS because squaring creates
    autocorrelation in the transformed parameter.
    """)
    return


@app.cell
def _(fit_1000dim_normal):
    fit_ess = fit_1000dim_normal()
    return (fit_ess,)


@app.cell
def _(az, fit_ess, np):
    ess_theta_bulk = az.ess(fit_ess, var_names=["theta"], method="bulk")["theta"].values
    ess_theta_tail = az.ess(fit_ess, var_names=["theta"], method="tail")["theta"].values
    ess_sq_bulk = az.ess(fit_ess, var_names=["theta_sq"], method="bulk")["theta_sq"].values
    ess_sq_tail = az.ess(fit_ess, var_names=["theta_sq"], method="tail")["theta_sq"].values
    return ess_sq_bulk, ess_sq_tail, ess_theta_bulk, ess_theta_tail


@app.cell
def _(mo, np, ess_theta_bulk, ess_sq_bulk):
    mo.md(f"""
    ### ESS summary

    - Median theta bulk ESS: {np.median(ess_theta_bulk):.0f}
    - Median theta² bulk ESS: {np.median(ess_sq_bulk):.0f}
    - Ratio (theta / theta²): {np.median(ess_theta_bulk) / np.median(ess_sq_bulk):.1f}×
    """)
    return


@app.cell
def _(alt, fit_ess, np, pd):
    # ACF for theta[0] and theta_sq[0]
    _chain0_theta = fit_ess.posterior["theta"].values[0, :, 0]
    _chain0_sq = fit_ess.posterior["theta_sq"].values[0, :, 0]
    _max_lag = 30

    def _compute_acf(x, max_lag):
        _n = len(x)
        _m = x.mean()
        _v = np.var(x)
        return np.array([np.mean((x[:_n-k] - _m) * (x[k:] - _m)) / _v
                         for k in range(max_lag + 1)])

    _acf_theta = _compute_acf(_chain0_theta, _max_lag)
    _acf_sq = _compute_acf(_chain0_sq, _max_lag)

    _df_acf = pd.DataFrame({
        "lag": np.tile(np.arange(_max_lag + 1), 2),
        "ACF": np.concatenate([_acf_theta, _acf_sq]),
        "parameter": ["theta[0]"] * (_max_lag + 1) + ["theta²[0]"] * (_max_lag + 1),
    })
    chart_acf_compare = alt.Chart(_df_acf).mark_bar(width=6, opacity=0.7).encode(
        x=alt.X("lag:Q", title="Lag"),
        y=alt.Y("ACF:Q"),
        color="parameter:N",
        xOffset="parameter:N",
    ).properties(title="ACF comparison: theta[0] vs theta²[0]", width=500, height=250)
    chart_acf_compare
    return (chart_acf_compare,)


@app.cell
def _(alt, ess_theta_bulk, ess_theta_tail, pd):
    _df_theta = pd.DataFrame({"bulk": ess_theta_bulk, "tail": ess_theta_tail})
    chart_theta_ess = alt.Chart(_df_theta).mark_point(size=10, opacity=0.5).encode(
        x=alt.X("bulk:Q", title="theta bulk ESS"),
        y=alt.Y("tail:Q", title="theta tail ESS"),
        color=alt.value("#e6550d"),
    ).properties(title="theta: bulk vs tail ESS", width=350, height=350)
    chart_theta_ess
    return (chart_theta_ess,)


@app.cell
def _(alt, ess_sq_bulk, ess_sq_tail, pd):
    _df_sq = pd.DataFrame({"bulk": ess_sq_bulk, "tail": ess_sq_tail})
    chart_sq_ess = alt.Chart(_df_sq).mark_point(size=10, opacity=0.5).encode(
        x=alt.X("bulk:Q", title="theta² bulk ESS"),
        y=alt.Y("tail:Q", title="theta² tail ESS"),
        color=alt.value("#e6550d"),
    ).properties(title="theta²: bulk vs tail ESS", width=350, height=350)
    chart_sq_ess
    return (chart_sq_ess,)


@app.cell
def _(alt, ess_theta_bulk, ess_sq_bulk, pd):
    _df_cross_bulk = pd.DataFrame({"theta_bulk": ess_theta_bulk, "sq_bulk": ess_sq_bulk})
    chart_cross_bulk = alt.Chart(_df_cross_bulk).mark_point(size=10, opacity=0.5).encode(
        x=alt.X("theta_bulk:Q", title="theta bulk ESS"),
        y=alt.Y("sq_bulk:Q", title="theta² bulk ESS"),
        color=alt.value("#e6550d"),
    ).properties(title="theta bulk ESS vs theta² bulk ESS", width=350, height=350)
    chart_cross_bulk
    return (chart_cross_bulk,)


@app.cell
def _(alt, ess_theta_tail, ess_sq_tail, pd):
    _df_cross_tail = pd.DataFrame({"theta_tail": ess_theta_tail, "sq_tail": ess_sq_tail})
    chart_cross_tail = alt.Chart(_df_cross_tail).mark_point(size=10, opacity=0.5).encode(
        x=alt.X("theta_tail:Q", title="theta tail ESS"),
        y=alt.Y("sq_tail:Q", title="theta² tail ESS"),
        color=alt.value("#e6550d"),
    ).properties(title="theta tail ESS vs theta² tail ESS", width=350, height=350)
    chart_cross_tail
    return (chart_cross_tail,)


if __name__ == "__main__":
    app.run()
