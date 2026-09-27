"""Categorical predictors, posterior contrasts, and the causal effect of sex on weight."""
import marimo

__generated_with = "0.25.0"
app = marimo.App(width="medium")


@app.cell
def _():
    from rethinking_companion.categorical import (
        adult_sex_data, causal_contrast_scm, fit_full_scm,
        fit_weight_by_sex, fit_weight_height_sex,
    )
    from rethinking_companion.gaussian_regression import assert_diagnostics, diagnostics
    import altair as alt
    import marimo as mo
    import numpy as np
    import pandas as pd
    return (alt, assert_diagnostics, causal_contrast_scm, adult_sex_data,
            diagnostics, fit_full_scm, fit_weight_by_sex,
            fit_weight_height_sex, mo, np, pd)


@app.cell
def _(mo):
    mo.md(r"""
    # Categories, contrasts and causes

    Source: `scripts/04_height_weight_sex_categorical.r`. Three progressively
    richer models of adult weight from the Howell1 data, all using sex as a
    categorical predictor via index variables (S = 1 Female, 2 Male).

    1. **W ~ S** — indexed group means, shared sigma.
    2. **W ~ S + H** — sex-varying intercepts and slopes on centered height.
    3. **Full SCM** — jointly model height and weight as functions of sex,
       then simulate `do(S)` to get the **total causal effect**.

    A posterior contrast of group means is not the same as contrasting two
    individual predictions. And a statistical group difference does not by
    itself identify a causal effect — the full SCM makes the causal question
    explicit.
    """)
    return


@app.cell
def _(mo):
    stage = mo.ui.dropdown(
        ["W ~ S", "W ~ S + H", "Full SCM"],
        value="W ~ S",
        label="Model stage (each fits four chains)",
    )
    stage
    return (stage,)


@app.cell
def _(adult_sex_data):
    dat = adult_sex_data()
    return (dat,)


@app.cell
def _(dat, fit_full_scm, fit_weight_by_sex, fit_weight_height_sex, stage):
    if stage.value == "W ~ S":
        fit = fit_weight_by_sex(dat)
    elif stage.value == "W ~ S + H":
        fit = fit_weight_height_sex(dat)
    else:
        fit = fit_full_scm(dat)
    return (fit,)


@app.cell
def _(assert_diagnostics, dat, diagnostics, fit, mo, stage):
    var_names = ["a", "sigma"]
    if stage.value == "W ~ S + H":
        var_names = ["a", "b", "sigma"]
    elif stage.value == "Full SCM":
        var_names = ["h", "tau", "a", "b", "sigma"]
    summary, diag = diagnostics(fit, var_names)
    assert_diagnostics(diag)
    n_female = int((dat["S"] == 1).sum())
    n_male = int((dat["S"] == 2).sum())
    mo.vstack([
        mo.md(f"**{len(dat['W'])} adults** ({n_female} female, {n_male} male), "
              f"Hbar = {dat['Hbar']:.4f} cm. "
              f"R-hat {diag['max_rhat']:.4f}, min bulk ESS {diag['min_ess_bulk']:.0f}, "
              f"divergences {diag['divergences']}."),
        mo.ui.table(summary[["mean", "sd", "ess_bulk", "ess_tail", "r_hat"]]
                     .reset_index(names="Parameter"), selection=None, show_data_types=False),
    ])
    return diag, summary


@app.cell
def _(alt, fit, np, pd, stage):
    a_post = fit.posterior["a"].values.reshape(-1, 2)
    mean_contrast = a_post[:, 1] - a_post[:, 0]
    contrast_df = pd.DataFrame({"Contrast (kg)": mean_contrast})
    mean_chart = alt.Chart(contrast_df).mark_bar(opacity=0.7).encode(
        x=alt.X("Contrast (kg):Q", bin=alt.Bin(maxbins=60),
                 title="Male − Female mean weight (kg)"),
        y=alt.Y("count():Q", title="Draws"),
    ).properties(width=500, height=180)

    sigma_post = fit.posterior["sigma"].values.ravel()
    W1 = np.random.default_rng(42).normal(a_post[:, 0], sigma_post)
    W2 = np.random.default_rng(43).normal(a_post[:, 1], sigma_post)
    individual_contrast = W2 - W1
    p_male_heavier = float((individual_contrast > 0).mean())
    ind_df = pd.DataFrame({"Contrast (kg)": individual_contrast})
    ind_chart = (
        alt.Chart(ind_df).mark_bar(opacity=0.7, color="steelblue").encode(
            x=alt.X("Contrast (kg):Q", bin=alt.Bin(maxbins=80),
                     title="Individual Male − Female weight (kg)"),
            y=alt.Y("count():Q", title="Draws"),
        ).properties(width=500, height=180)
        + alt.Chart(pd.DataFrame({"x": [0]})).mark_rule(color="black", strokeDash=[4, 4]).encode(x="x:Q")
    )
    _ = stage  # read for label
    return mean_chart, mean_contrast, ind_chart, p_male_heavier


@app.cell
def _(mean_chart, mean_contrast, ind_chart, mo, p_male_heavier, stage):
    label = "W ~ S" if stage.value == "W ~ S" else "direct effect (height-adjusted)"
    mo.vstack([
        mo.md(f"## Posterior contrasts ({label})\n"
              f"Mean contrast M−F: **{float(mean_contrast.mean()):.2f} ± "
              f"{float(mean_contrast.std()):.2f} kg**. "
              f"But two randomly chosen individuals: P(male heavier) = **{p_male_heavier:.3f}**. "
              "The mean contrast is tight; the individual contrast is wide because sigma "
              "dominates individual variation."),
        mean_chart, ind_chart,
    ])
    return


@app.cell
def _(causal_contrast_scm, dat, fit, mean_contrast, mo, np, pd, alt, stage):
    if stage.value != "Full SCM":
        scm_output = mo.md(
            f"Select **Full SCM** to see the total causal effect via `do(S)`. "
            f"The current {stage.value} model gives a "
            + ("statistical group contrast, not a causal estimate."
               if stage.value == "W ~ S"
               else "direct effect holding height constant."))
    else:
        W_do_S = causal_contrast_scm(fit, dat["Hbar"])
        do_df = pd.DataFrame({"Contrast (kg)": W_do_S})
        do_chart = alt.Chart(do_df).mark_bar(opacity=0.7, color="darkorange").encode(
            x=alt.X("Contrast (kg):Q", bin=alt.Bin(maxbins=80),
                     title="Total causal effect do(Male) − do(Female) (kg)"),
            y=alt.Y("count():Q", title="Draws"),
        ).properties(width=500, height=180)
        direct = float(mean_contrast.mean())
        total = float(W_do_S.mean())
        scm_output = mo.vstack([
            mo.md(f"## Total causal effect via the SCM\n"
                  f"Direct effect (W~S+H mean contrast): **{direct:.2f} kg**. "
                  f"Total causal effect do(Male)−do(Female): **{total:.2f} kg**.\n\n"
                  "The total effect is larger because sex affects height, and height "
                  "affects weight. The direct effect conditions on height and removes "
                  "the indirect path S → H → W. Neither is wrong; they answer "
                  "different causal questions."),
            do_chart,
        ])
    scm_output
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## What has been verified?

    The **W ~ S** model is checked against an independent numerical integration:
    conditionally on sigma, each group mean a[k] has a Normal posterior (Normal
    prior × Normal likelihood). Integrate out both a[k] analytically, then
    numerically integrate sigma on a grid. NUTS means and covariance are compared
    within Monte Carlo standard errors.

    The **W ~ S + H** model adds sex-varying positive slopes b[S] ~ LogNormal(0,1).
    The posterior is not conjugate; verification relies on diagnostics and
    consistency with the simpler model's intercept estimates.

    The **full SCM** jointly fits height and weight. The total causal effect
    simulates through the joint posterior: draw sex-specific heights, then
    sex-specific weights conditional on those heights. This matches the R
    source's `sim(m_SHW_full, data=list(S=c(1,2)), vars=c("H","W"))`.

    NUTS replaces `quap` throughout. The Gaussian likelihood makes `quap`
    exact for the first model, but NUTS generalizes to later non-Gaussian
    models.
    """)
    return


if __name__ == "__main__":
    app.run()
