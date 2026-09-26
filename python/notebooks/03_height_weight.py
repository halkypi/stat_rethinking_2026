"""Centered adult weight regression with constrained parameters and unknown noise."""
import marimo

__generated_with = "0.25.0"
app = marimo.App(width="medium")


@app.cell
def _():
    from rethinking_companion.gaussian_regression import assert_diagnostics, diagnostics
    from rethinking_companion.height_weight import fit_weight, load_howell, simulated_weight
    import altair as alt
    import marimo as mo
    import numpy as np
    import pandas as pd
    return alt, assert_diagnostics, diagnostics, fit_weight, load_howell, mo, np, pd, simulated_weight


@app.cell
def _(mo):
    mo.md(r"""
    # Predict adult weight from height

    Follow the first fitted model in `scripts/03_howell_new_weight_model.r`:

    $W_i\sim\mathrm{Normal}(\mu_i,\sigma)$,
    $\mu_i=a+b(H_i-\bar H)$,
    $a\sim\mathrm{Normal}(60,10)$,
    $b\sim\mathrm{LogNormal}(0,1)$,
    $\sigma\sim\mathrm{Uniform}(0,10)$.

    Weight is in **kg**, height in **cm**. Centering height makes a the expected
    weight at the training sample's average height. The positive-slope prior
    encodes an increasing association; it does not establish a causal effect.
    LogNormal(0,1) means log(b) has Normal mean 0 and SD 1.

    Start with the source's simulated truth a=70, b=0.5, sigma=5; then fit
    Howell1 adults (age ≥18). The real data were collected by Nancy Howell
    and are vendored unchanged from the official rethinking package with a
    checksum and attribution in `data/README.md`. The lesson runs offline.
    """)
    return


@app.cell
def _(mo):
    dataset = mo.ui.dropdown(["Synthetic validation", "Howell adults"], value="Howell adults", label="Data (changing this runs four chains)")
    dataset
    return (dataset,)


@app.cell
def _(dataset, load_howell, np, simulated_weight):
    if dataset.value == "Synthetic validation":
        height,weight = simulated_weight()
    else:
        adults = load_howell().query("age >= 18")
        height,weight = adults.height.to_numpy(),adults.weight.to_numpy()
    height_grid=np.linspace(130,190,50)
    return height, height_grid, weight


@app.cell
def _(fit_weight, height, height_grid, weight):
    fit=fit_weight(height,weight,height_grid)
    return (fit,)


@app.cell
def _(assert_diagnostics, diagnostics, fit, height, mo):
    summary,diagnostic_values=diagnostics(fit,("a","b","sigma"))
    assert_diagnostics(diagnostic_values)
    mo.vstack([
        mo.md(f"**{len(height)} observations**, centered at **{height.mean():.3f} cm**. "
              f"Maximum R-hat **{diagnostic_values['max_rhat']:.4f}**, minimum bulk ESS **{diagnostic_values['min_ess_bulk']:.0f}**, "
              f"divergences **{diagnostic_values['divergences']}**. The full verification also gates tail ESS, BFMI and tree depth."),
        mo.ui.table(summary[["mean","sd","ess_bulk","ess_tail","r_hat"]].reset_index(names="Parameter"),
                    selection=None,show_data_types=False),
    ])
    return diagnostic_values, summary


@app.cell
def _(fit, height_grid, np, pd):
    mu=fit.predictions.mu_new.values.reshape(-1,len(height_grid))
    predictions=fit.predictions.weight_new.values.reshape(-1,len(height_grid))
    mean_interval=np.quantile(mu,[.005,.995],axis=0)
    prediction_interval=np.quantile(predictions,[.055,.945],axis=0)
    bands=pd.DataFrame({"Height":height_grid,"Mean weight":mu.mean(axis=0),
        "Mean lower":mean_interval[0],"Mean upper":mean_interval[1],
        "Prediction lower":prediction_interval[0],"Prediction upper":prediction_interval[1]})
    return bands, mu, predictions


@app.cell
def _(alt, bands, height, mo, pd, weight):
    base=alt.Chart(bands).encode(x=alt.X("Height:Q",title="Height (cm)"))
    weight_chart=(
        base.mark_area(color="#aebfca",opacity=.45).encode(y=alt.Y("Prediction lower:Q",title="Weight (kg)"),y2="Prediction upper:Q")
        +base.mark_area(color="#167c80",opacity=.5).encode(y="Mean lower:Q",y2="Mean upper:Q")
        +base.mark_line(color="#167c80").encode(y="Mean weight:Q")
        +alt.Chart(pd.DataFrame({"Height":height,"Weight":weight})).mark_point(opacity=.4,size=20).encode(x="Height:Q",y="Weight:Q")
    ).properties(width=550,height=270)
    mo.vstack([mo.md("## Mean uncertainty and individual variation\nTeal is a **99% equal-tailed interval for mean weight**; gray is an **89% prediction interval for individual weight**, matching the source's two coverage levels. "
                    "Predictions retain the training mean height even on a different grid. The plot extends to 190 cm to match the source; beyond observed heights, it is extrapolation."),weight_chart])
    return (weight_chart,)


@app.cell
def _(alt, fit, height, height_grid, mo, np, pd):
    prior_a=fit.prior.a.values.ravel()[:30]
    prior_b=fit.prior.b.values.ravel()[:30]
    prior_means=prior_a[:,None]+prior_b[:,None]*(height_grid-height.mean())
    prior_lines=pd.DataFrame({"Height":np.tile(height_grid,30),"Mean weight":prior_means.ravel(),"Draw":np.repeat(np.arange(30),len(height_grid))})
    prior_chart=alt.Chart(prior_lines).mark_line(opacity=.3).encode(
        x=alt.X("Height:Q",title="Height (cm)"),y=alt.Y("Mean weight:Q",title="Prior mean weight (kg)"),detail="Draw:N",
    ).properties(width=550,height=210)
    negative_fraction=float((fit.prior_predictive.weight.values<0).mean())
    mo.vstack([mo.md(f"## Inspect what the prior permits\nThese 30 mean functions use the actual fitted priors. About **{negative_fraction:.1%}** of prior predictive weights at the training heights are negative. "
                    "A positive slope does not guarantee positive outcomes under a Normal likelihood. Prior prediction reveals implications; do not discard inconvenient draws from the graph."),prior_chart])
    return (prior_chart,)


@app.cell
def _(alt, fit, height, mo, np, pd, weight):
    fitted_mean=fit.posterior.mu.mean(("chain","draw")).values
    residuals=pd.DataFrame({"Height":height,"Residual":weight-fitted_mean})
    residual_chart=(
        alt.Chart(residuals).mark_point(opacity=.5).encode(x="Height:Q",y=alt.Y("Residual:Q",title="Observed − posterior mean (kg)"))
        +alt.Chart(pd.DataFrame({"Residual":[0]})).mark_rule(color="gray").encode(y="Residual:Q")
    ).properties(width=550,height=190)
    replicated=fit.posterior_predictive.weight.values.reshape(-1,len(weight))
    replicated_sd=np.std(replicated,axis=1,ddof=1)
    observed_sd=float(np.std(weight,ddof=1))
    mo.vstack([
        mo.md(f"## Check the model against outcomes\nObserved weight SD: **{observed_sd:.2f} kg**. "
              f"The central 89% interval of replicated weight SDs is **{np.quantile(replicated_sd,.055):.2f}–{np.quantile(replicated_sd,.945):.2f} kg**. "
              "This checks one summary; also look for residual trends, changing spread or outliers."),
        residual_chart,
        mo.md(r"""
        ## What has been verified?

        NUTS is compared with an independent posterior integration: conditionally
        on b and sigma, a has an analytic Normal posterior. Integrate a out,
        then numerically integrate b and sigma using centered sufficient
        statistics. Refine and expand that grid before trusting the comparison.
        The checks compare all means and covariances, parameter support,
        predictive noise and unchanged training centering.

        The synthetic example uses 100 independent heights Uniform(130,170)
        and seed 604 (the source does not fix its seed). Its 99% intervals
        contain the generating values for this realized dataset; that single
        recovery test is **not** a claim of simulation-based calibration.
        The source's repeated-fit experiment, grouped models and adult/child
        polynomial models are separate work. Here NUTS replaces `quap`'s
        Gaussian approximation while retaining the specified priors/likelihood.
        """),
    ])
    return (residual_chart,)


if __name__=="__main__":
    app.run()
