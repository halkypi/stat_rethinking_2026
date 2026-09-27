"""B-spline regression on cherry blossom phenology and Howell1 height-age data."""
import marimo

__generated_with = "0.25.0"
app = marimo.App(width="medium")


@app.cell
def _():
    from rethinking_companion.spline import (
        bspline_basis, fit_cherry_spline, fit_howell_spline,
        load_cherry_blossoms,
    )
    from rethinking_companion.height_weight import load_howell
    from rethinking_companion.gaussian_regression import assert_diagnostics, diagnostics
    import altair as alt
    import marimo as mo
    import numpy as np
    import pandas as pd
    return (alt, assert_diagnostics, bspline_basis, diagnostics,
            fit_cherry_spline, fit_howell_spline, load_cherry_blossoms,
            load_howell, mo, np, pd)


@app.cell
def _(mo):
    mo.md(r"""
    # B-spline regression

    Source: `scripts/04_prior_pred_spline.r`. B-spline basis functions
    turn a wiggly predictor–outcome relationship into a linear regression
    on locally supported basis functions. The weight on each basis function
    controls the local contribution to the mean; a prior on those weights
    controls smoothness.

    Two datasets:
    1. **Cherry blossom phenology** — day of first bloom at Kyoto, 812–2015.
       A spline captures century-scale temperature trends.
    2. **Howell1 height vs age** — all ages (not just adults). A spline
       captures the non-linear growth curve: rapid increase in childhood,
       plateau in adulthood, slight decline in old age.
    """)
    return


@app.cell
def _(mo):
    dataset_choice = mo.ui.dropdown(
        ["Cherry blossoms", "Howell1 height ~ age"],
        value="Cherry blossoms",
        label="Dataset",
    )
    num_knots_slider = mo.ui.slider(
        3, 30, value=20, step=1, label="Number of knots",
    )
    tau_slider = mo.ui.slider(
        1, 50, value=10, step=1, label="tau (prior SD on basis weights)",
    )
    mo.hstack([dataset_choice, num_knots_slider, tau_slider])
    return dataset_choice, num_knots_slider, tau_slider


@app.cell
def _(load_cherry_blossoms, load_howell, dataset_choice, np):
    if dataset_choice.value == "Cherry blossoms":
        _cb = load_cherry_blossoms()
        _d = _cb[_cb["doy"].notna()].sort_values("year")
        x_data = _d["year"].values
        y_data = _d["doy"].values
        x_label = "Year"
        y_label = "Day of first bloom"
    else:
        _hw = load_howell()
        _order = np.argsort(_hw["age"].values)
        x_data = _hw["age"].values[_order]
        y_data = _hw["height"].values[_order]
        x_label = "Age (years)"
        y_label = "Height (cm)"
    return x_data, y_data, x_label, y_label


@app.cell
def _(bspline_basis, dataset_choice, num_knots_slider, x_data):
    _degree = 3
    if dataset_choice.value == "Cherry blossoms" and num_knots_slider.value <= 5:
        _degree = 2
    B, knots = bspline_basis(x_data, num_knots_slider.value, degree=_degree)
    n_basis = B.shape[0]
    return B, knots, n_basis


@app.cell
def _(mo, n_basis):
    mo.md(f"**Basis functions**: {n_basis} B-spline basis functions "
           f"(intercept excluded; a separate `a0` absorbs the baseline).")
    return


@app.cell
def _(B, alt, n_basis, np, pd, x_data, x_label):
    _rows = []
    for _j in range(n_basis):
        for _i in range(0, len(x_data), max(1, len(x_data) // 200)):
            _rows.append({"x": float(x_data[_i]), "basis": int(_j),
                          "value": float(B[_j, _i])})
    _bdf = pd.DataFrame(_rows)
    basis_chart = alt.Chart(_bdf).mark_line(strokeWidth=2).encode(
        x=alt.X("x:Q", title=x_label),
        y=alt.Y("value:Q", title="Basis value"),
        color=alt.Color("basis:N", legend=None),
    ).properties(title="B-spline basis functions", width=550, height=250)
    basis_chart
    return (basis_chart,)


@app.cell
def _(mo):
    mo.md(r"""
    ## Prior predictive draws

    Each curve below is `a0 + a * B` where `a` is drawn from Normal(0, tau).
    Larger tau → more flexibility; smaller tau → closer to the flat intercept.
    """)
    return


@app.cell
def _(B, alt, dataset_choice, np, pd, tau_slider, x_data, x_label, y_data, y_label):
    rng_prior = np.random.default_rng(42)
    n_prior_draws = 10
    _a0_prior = 100.0 if dataset_choice.value == "Cherry blossoms" else 120.0
    _rows = []
    for _i in range(n_prior_draws):
        _a = rng_prior.normal(0, tau_slider.value, B.shape[0])
        _mu = _a0_prior + _a @ B
        for _j in range(0, len(x_data), max(1, len(x_data) // 200)):
            _rows.append({"x": float(x_data[_j]), "y": float(_mu[_j]),
                          "draw": int(_i)})
    _pdf = pd.DataFrame(_rows)
    _data_df = pd.DataFrame({"x": x_data, "y": y_data})
    _data_pts = alt.Chart(_data_df).mark_circle(size=8, opacity=0.2, color="gray").encode(
        x=alt.X("x:Q", title=x_label), y=alt.Y("y:Q", title=y_label))
    _prior_lines = alt.Chart(_pdf).mark_line(strokeWidth=1.5, opacity=0.6).encode(
        x="x:Q", y="y:Q", color=alt.Color("draw:N", legend=None))
    prior_chart = (_data_pts + _prior_lines).properties(
        title=f"Prior predictive (tau={tau_slider.value})", width=550, height=300)
    prior_chart
    return (prior_chart,)


@app.cell
def _(mo):
    mo.md(r"""
    ## Posterior fit

    Four-chain NUTS. The model: Y ~ Normal(a0 + a * B, exp(log_sigma)),
    with a0 ~ Normal(100, 1) [or 120 for height], a ~ Normal(0, tau),
    log_sigma ~ Normal(0, 0.5). This matches the R source's `quap` model.
    """)
    return


@app.cell
def _(B, dataset_choice, fit_cherry_spline, fit_howell_spline,
      tau_slider, x_data, y_data):
    if dataset_choice.value == "Cherry blossoms":
        fit = fit_cherry_spline(x_data, y_data, B, tau=tau_slider.value)
    else:
        fit = fit_howell_spline(x_data, y_data, B, tau=tau_slider.value)
    return (fit,)


@app.cell
def _(assert_diagnostics, diagnostics, fit, mo, n_basis):
    _var_names = ["a0", "a", "log_sigma"]
    summary, diag = diagnostics(fit, _var_names)
    assert_diagnostics(diag)
    mo.md(f"""**Diagnostics**: R-hat {diag['max_rhat']:.4f},
    bulk ESS {diag['min_ess_bulk']:.0f},
    tail ESS {diag['min_ess_tail']:.0f},
    divergences {diag['divergences']},
    BFMI {diag['min_bfmi']:.3f},
    tree depth {diag['max_tree_depth']}.
    Parameters: a0 + {n_basis} basis weights + log_sigma = {n_basis + 2} total.""")
    return diag, summary


@app.cell
def _(alt, fit, np, pd, x_data, x_label, y_data, y_label):
    _mu_post = fit.posterior["mu"].values.reshape(-1, len(x_data))
    _mu_mean = _mu_post.mean(axis=0)
    _mu_lo = np.percentile(_mu_post, 5.5, axis=0)
    _mu_hi = np.percentile(_mu_post, 94.5, axis=0)

    _fit_df = pd.DataFrame({
        "x": x_data, "mean": _mu_mean, "lo": _mu_lo, "hi": _mu_hi,
    })
    _data_df = pd.DataFrame({"x": x_data, "y": y_data})

    _pts = alt.Chart(_data_df).mark_circle(size=10, opacity=0.25, color="coral").encode(
        x=alt.X("x:Q", title=x_label), y=alt.Y("y:Q", title=y_label))
    _band = alt.Chart(_fit_df).mark_area(opacity=0.3, color="steelblue").encode(
        x="x:Q", y="lo:Q", y2="hi:Q")
    _line = alt.Chart(_fit_df).mark_line(color="steelblue", strokeWidth=2).encode(
        x="x:Q", y="mean:Q")
    posterior_chart = (_pts + _band + _line).properties(
        title="Posterior mean and 89% interval", width=550, height=300)
    posterior_chart
    return (posterior_chart,)


@app.cell
def _(mo):
    mo.md(r"""
    The posterior curve captures the long-term pattern in the data.
    For cherry blossoms, blooming has shifted earlier over the last
    two centuries (lower day of year). For Howell1, the spline traces
    rapid height growth in childhood, a plateau through adulthood, and
    slight decline in old age.

    The 89% interval around the mean function shows posterior uncertainty
    — wider where data are sparse, narrower where dense. This is a
    regression on basis functions, not a smoothing spline; the model
    trades off data fit against the prior on basis weights.
    """)
    return


if __name__ == "__main__":
    app.run()
