"""Poisson GLMs, latent confounders, sensitivity analysis, and proxy variables."""
import marimo

__generated_with = "0.25.0"
app = marimo.App(width="medium")


@app.cell
def _():
    from rethinking_companion.glm import (
        inv_logit, load_ucbadmit, ucbadmit_arrays, ucbadmit_to_long, load_kline,
    )
    from rethinking_companion.gaussian_regression import assert_diagnostics, diagnostics
    import altair as alt
    import arviz as az
    import marimo as mo
    import numpy as np
    import pandas as pd
    import pymc as pm
    return (alt, assert_diagnostics, az, diagnostics, inv_logit,
            load_ucbadmit, load_kline, mo, np, pd, pm,
            ucbadmit_arrays, ucbadmit_to_long)


@app.cell
def _(mo):
    mo.md(r"""
    # Poisson GLMs, sensitivity analysis, and proxy variables

    Sources: `scripts/10_confounds_poisson.r` and `scripts/A10_sensitivity.R`.

    This lesson covers:
    1. **Confounded UCBadmit**: latent ability u creates a backdoor path.
       The direct-effect model is confounded when u is unobserved.
    2. **Sensitivity analysis**: declare u as a latent Normal(0,1) variable
       with fixed or learned effect strengths to partially recover the true effect.
    3. **Proxy variables**: noisy measurements of u jointly identify the latent.
    4. **Poisson regression**: Kline tools data with log link. Intercept-only
       and interaction models, PSIS comparison, innovation/loss scientific model.
    """)
    return


@app.cell
def _(mo):
    topic = mo.ui.dropdown(
        ["Confounded simulation",
         "Sensitivity analysis (long-running)",
         "Proxy variables (long-running)",
         "Poisson regression — Kline tools",
         "Innovation/loss model"],
        value="Confounded simulation",
        label="Topic",
    )
    topic
    return (topic,)


# --- Confounded UCBadmit simulation ---

@app.cell
def _(assert_diagnostics, diagnostics, inv_logit, mo, np, pd, pm, topic, alt):
    if topic.value != "Confounded simulation":
        _out = mo.md("Select **Confounded simulation**.")
    else:
        _rng = np.random.default_rng(17)
        _N = 2000
        _G = _rng.choice([1, 2], size=_N)
        _u = _rng.binomial(1, 0.1, _N)
        _D = _rng.binomial(1, np.where(_G == 1, _u * 0.5, 0.8)) + 1
        _ar_u0 = np.array([[0.1, 0.1], [0.1, 0.3]])
        _ar_u1 = np.array([[0.2, 0.3], [0.2, 0.5]])
        _p = np.array([(_ar_u1 if _u[i] else _ar_u0)[_D[i]-1, _G[i]-1]
                        for i in range(_N)])
        _A = _rng.binomial(1, _p)

        # m1: total effect
        with pm.Model(coords={"gender": ["F", "M"]}):
            _a1 = pm.Normal("a", 0, 1, dims="gender")
            pm.Bernoulli("A", logit_p=_a1[_G - 1], observed=_A)
            _fit1 = pm.sample(draws=1500, tune=1000, chains=4, cores=1,
                              random_seed=1001, target_accept=0.9,
                              progressbar=False, return_inferencedata=True)
        _, _d1 = diagnostics(_fit1, ["a"])
        assert_diagnostics(_d1)

        # m2: direct effect (confounded — no u)
        with pm.Model(coords={"gender": ["F", "M"], "dept": ["1", "2"]}):
            _a2 = pm.Normal("a", 0, 1, dims=("gender", "dept"))
            pm.Bernoulli("A", logit_p=_a2[_G - 1, _D - 1], observed=_A)
            _fit2 = pm.sample(draws=1500, tune=1000, chains=4, cores=1,
                              random_seed=1002, target_accept=0.9,
                              progressbar=False, return_inferencedata=True)
        _, _d2 = diagnostics(_fit2, ["a"])
        assert_diagnostics(_d2)

        # m3: with observed u
        with pm.Model(coords={"gender": ["F", "M"], "dept": ["1", "2"]}):
            _a3 = pm.Normal("a", 0, 1, dims=("gender", "dept"))
            _buA = pm.HalfNormal("buA", 1)
            pm.Bernoulli("A", logit_p=_a3[_G - 1, _D - 1] + _buA * _u,
                         observed=_A)
            _fit3 = pm.sample(draws=1500, tune=1000, chains=4, cores=1,
                              random_seed=1003, target_accept=0.9,
                              progressbar=False, return_inferencedata=True)
        _, _d3 = diagnostics(_fit3, ["a", "buA"])
        assert_diagnostics(_d3)

        _post2 = _fit2.posterior["a"].values.reshape(-1, 2, 2)
        _c2_D1 = inv_logit(_post2[:, 0, 0]) - inv_logit(_post2[:, 1, 0])
        _c2_D2 = inv_logit(_post2[:, 0, 1]) - inv_logit(_post2[:, 1, 1])

        _post3 = _fit3.posterior["a"].values.reshape(-1, 2, 2)
        _c3_D1 = inv_logit(_post3[:, 0, 0]) - inv_logit(_post3[:, 1, 0])
        _c3_D2 = inv_logit(_post3[:, 0, 1]) - inv_logit(_post3[:, 1, 1])

        _cdf = pd.concat([
            pd.DataFrame({"contrast": _c2_D1, "Model": "m2 (no u) Dept 1"}),
            pd.DataFrame({"contrast": _c2_D2, "Model": "m2 (no u) Dept 2"}),
            pd.DataFrame({"contrast": _c3_D1, "Model": "m3 (with u) Dept 1"}),
            pd.DataFrame({"contrast": _c3_D2, "Model": "m3 (with u) Dept 2"}),
        ])
        _cchart = alt.Chart(_cdf).mark_bar(opacity=0.5).encode(
            x=alt.X("contrast:Q", bin=alt.Bin(maxbins=50),
                     title="F − M contrast (probability)"),
            y="count():Q", color="Model:N",
        ).properties(width=550, height=250)

        _out = mo.vstack([
            mo.md(f"**Confounded simulation**: N={_N}, latent ability u ~ Bernoulli(0.1).\n\n"
                   f"Without u (m2), the direct effect model shows spurious gender "
                   f"differences — Dept 1 contrast: {_c2_D1.mean():.3f}, "
                   f"Dept 2: {_c2_D2.mean():.3f}.\n\n"
                   f"With observed u (m3), contrasts move toward zero — "
                   f"Dept 1: {_c3_D1.mean():.3f}, Dept 2: {_c3_D2.mean():.3f}.\n\n"
                   f"buA = {_fit3.posterior['buA'].values.mean():.2f} "
                   f"(positive: ability helps admission)."),
            _cchart,
        ])
    _out
    return


# --- Sensitivity analysis (latent u) ---

@app.cell
def _(mo, topic):
    if topic.value != "Sensitivity analysis (long-running)":
        _out = mo.md("Select **Sensitivity analysis** to fit models with latent u.\n\n"
                      "These models have N=2000+ latent parameters and take several "
                      "minutes to fit. Use the check script for automated verification.")
    else:
        _out = mo.md(r"""
        ## Sensitivity analysis

        The sensitivity model declares `u ~ Normal(0,1)` as a latent variable
        for each individual. A joint model links u to both admission and
        department choice:

        - Admission: `logit(p) = a[G,D] + b[G] * u`
        - Department: `logit(q) = delta[G] + g[G] * u`

        With **fixed** effect strengths (b, g passed as data), the model
        partially recovers the true gender effect even without observing u.

        With **learned** b ~ Uniform(0,1) and g ~ Uniform(0,1), the model
        explores reasonable effect sizes, providing wider but more honest
        uncertainty.

        Run `uv run python checks/check_poisson_sensitivity.py` to fit and
        verify these models.
        """)
    _out
    return


# --- Proxy variables ---

@app.cell
def _(mo, topic):
    if topic.value != "Proxy variables (long-running)":
        _out = mo.md("Select **Proxy variables** to see this section.")
    else:
        _out = mo.md(r"""
        ## Proxy variables

        Three noisy proxies of latent ability:
        - T₁ ~ Normal(u, τ₁) with τ₁ = 0.1
        - T₂ ~ Normal(u, τ₂) with τ₂ = 0.5
        - T₃ ~ Normal(u, τ₃) with τ₃ = 0.25

        The joint model recovers u through measurement equations and
        deconfounds the gender contrast. The estimated τ values should
        be close to the generating noise levels.

        Run `uv run python checks/check_poisson_sensitivity.py` to fit and
        verify this model.
        """)
    _out
    return


# --- Poisson regression: Kline tools ---

@app.cell
def _(assert_diagnostics, az, diagnostics, load_kline, mo, np, pd, pm, topic, alt):
    if topic.value != "Poisson regression — Kline tools":
        _out = mo.md("Select **Poisson regression — Kline tools**.")
    else:
        _kline = load_kline()
        _T, _P, _C = _kline["T"], _kline["P"], _kline["C"]

        # intercept-only
        with pm.Model():
            _a0 = pm.Normal("a", 3, 0.5)
            _lam0 = pm.math.exp(_a0)
            pm.Poisson("T", mu=_lam0, observed=_T)
            _fit0 = pm.sample(draws=1500, tune=1000, chains=4, cores=1,
                              random_seed=1101, target_accept=0.9,
                              progressbar=False, return_inferencedata=True,
                              idata_kwargs={"log_likelihood": True})
        _, _d0 = diagnostics(_fit0, ["a"])
        assert_diagnostics(_d0)

        # interaction model
        with pm.Model(coords={"contact": ["low", "high"], "obs": np.arange(len(_T))}):
            _a1 = pm.Normal("a", 3, 0.5, dims="contact")
            _b1 = pm.Normal("b", 0, 0.2, dims="contact")
            _lam1 = pm.Deterministic("lambda",
                                      pm.math.exp(_a1[_C - 1] + _b1[_C - 1] * _P),
                                      dims="obs")
            pm.Poisson("T", mu=_lam1, observed=_T)
            _fit1 = pm.sample(draws=1500, tune=1000, chains=4, cores=1,
                              random_seed=1102, target_accept=0.9,
                              progressbar=False, return_inferencedata=True,
                              idata_kwargs={"log_likelihood": True})
        _, _d1 = diagnostics(_fit1, ["a", "b"])
        assert_diagnostics(_d1)

        # PSIS comparison
        _loo0 = az.loo(_fit0, pointwise=True)
        _loo1 = az.loo(_fit1, pointwise=True)
        _comp = az.compare({"intercept": _fit0, "interaction": _fit1})

        # Pareto k values for interaction model
        _k_vals = _loo1.pareto_k.values
        _high_k = (_k_vals > 0.7).sum()

        # prediction curves on standardized scale
        _P_seq = np.linspace(-1.4, 3, 100)
        _post1 = _fit1.posterior
        _a_post = _post1["a"].values.reshape(-1, 2)
        _b_post = _post1["b"].values.reshape(-1, 2)
        _pred_rows = []
        for _ci, _clabel in enumerate(["low", "high"]):
            _lam_pred = np.exp(_a_post[:, _ci, None] + _b_post[:, _ci, None] * _P_seq)
            _mean = _lam_pred.mean(axis=0)
            _lo = np.quantile(_lam_pred, 0.055, axis=0)
            _hi = np.quantile(_lam_pred, 0.945, axis=0)
            for _j in range(len(_P_seq)):
                _pred_rows.append({"P": float(_P_seq[_j]), "mean": float(_mean[_j]),
                                   "lo": float(_lo[_j]), "hi": float(_hi[_j]),
                                   "contact": _clabel})
        _pred_df = pd.DataFrame(_pred_rows)

        _data_df = pd.DataFrame({
            "P": _P, "T": _T,
            "contact": ["low" if c == 1 else "high" for c in _C],
            "culture": _kline["culture"],
            "pareto_k": _k_vals,
        })

        _points = alt.Chart(_data_df).mark_circle(size=100).encode(
            x=alt.X("P:Q", title="log population (standardized)"),
            y=alt.Y("T:Q", title="total tools"),
            color=alt.Color("contact:N"),
            size=alt.Size("pareto_k:Q", scale=alt.Scale(range=[50, 300]),
                          title="Pareto k"),
            tooltip=["culture:N", "T:Q", "pareto_k:Q"],
        )
        _lines = alt.Chart(_pred_df).mark_line().encode(
            x="P:Q", y="mean:Q", color="contact:N",
        )
        _band = alt.Chart(_pred_df).mark_area(opacity=0.2).encode(
            x="P:Q", y="lo:Q", y2="hi:Q", color="contact:N",
        )
        _std_chart = (_band + _lines + _points).properties(
            width=500, height=300,
            title="Kline tools: interaction model (standardized log pop)")

        # natural scale
        _pop_seq = np.exp(_P_seq * _kline["log_pop_std"] + _kline["log_pop_mean"])
        _nat_rows = []
        for _ci, _clabel in enumerate(["low", "high"]):
            _lam_pred = np.exp(_a_post[:, _ci, None] + _b_post[:, _ci, None] * _P_seq)
            _mean = _lam_pred.mean(axis=0)
            _lo = np.quantile(_lam_pred, 0.055, axis=0)
            _hi = np.quantile(_lam_pred, 0.945, axis=0)
            for _j in range(len(_P_seq)):
                _nat_rows.append({"population": float(_pop_seq[_j]),
                                  "mean": float(_mean[_j]),
                                  "lo": float(_lo[_j]), "hi": float(_hi[_j]),
                                  "contact": _clabel})
        _nat_df = pd.DataFrame(_nat_rows)
        _ndata = pd.DataFrame({
            "population": _kline["population"], "T": _T,
            "contact": ["low" if c == 1 else "high" for c in _C],
            "culture": _kline["culture"],
        })
        _npoints = alt.Chart(_ndata).mark_circle(size=100).encode(
            x=alt.X("population:Q", title="population"),
            y=alt.Y("T:Q", title="total tools"),
            color="contact:N", tooltip=["culture:N", "T:Q"],
        )
        _nlines = alt.Chart(_nat_df).mark_line().encode(
            x="population:Q", y="mean:Q", color="contact:N",
        )
        _nband = alt.Chart(_nat_df).mark_area(opacity=0.2).encode(
            x="population:Q", y="lo:Q", y2="hi:Q", color="contact:N",
        )
        _nat_chart = (_nband + _nlines + _npoints).properties(
            width=500, height=300, title="Kline tools: natural population scale")

        _out = mo.vstack([
            mo.md(f"**Kline tools**: intercept-only R-hat {_d0['max_rhat']:.4f}, "
                   f"interaction R-hat {_d1['max_rhat']:.4f}.\n\n"
                   f"PSIS comparison (top model first):\n\n"),
            mo.ui.table(_comp.reset_index(names="Model")[
                ["Model", "elpd_loo", "se", "p_loo", "weight"]],
                selection=None, show_data_types=False),
            mo.md(f"\nHigh Pareto k (>0.7): **{_high_k}** observations. "
                   f"Hawaii (pop 275,000) is influential."),
            _std_chart, _nat_chart,
        ])
    _out
    return


# --- Innovation/loss model ---

@app.cell
def _(assert_diagnostics, az, diagnostics, load_kline, mo, np, pd, pm, topic, alt):
    if topic.value != "Innovation/loss model":
        _out = mo.md("Select **Innovation/loss model**.")
    else:
        _kline = load_kline()
        _T = _kline["T"]
        _pop = _kline["population"]
        _C = _kline["C"]

        with pm.Model(coords={"contact": ["low", "high"], "obs": np.arange(len(_T))}):
            _a = pm.Normal("a", 1, 1, dims="contact")
            _b = pm.Exponential("b", 1, dims="contact")
            _g = pm.Exponential("g", 1)
            _lam = pm.Deterministic(
                "lambda",
                pm.math.exp(_a[_C - 1]) * _pop ** _b[_C - 1] / _g,
                dims="obs")
            pm.Poisson("T", mu=_lam, observed=_T)
            _fit_il = pm.sample(draws=1500, tune=1000, chains=4, cores=1,
                                random_seed=1103, target_accept=0.95,
                                progressbar=False, return_inferencedata=True,
                                idata_kwargs={"log_likelihood": True})
        _, _d_il = diagnostics(_fit_il, ["a", "b", "g"])
        assert_diagnostics(_d_il)

        _loo_il = az.loo(_fit_il, pointwise=True)
        _k_il = _loo_il.pareto_k.values
        _high_k_il = (_k_il > 0.7).sum()

        # Also fit interaction for comparison
        _P = _kline["P"]
        with pm.Model(coords={"contact": ["low", "high"], "obs": np.arange(len(_T))}):
            _a_int = pm.Normal("a", 3, 0.5, dims="contact")
            _b_int = pm.Normal("b", 0, 0.2, dims="contact")
            pm.Poisson("T", mu=pm.math.exp(_a_int[_C - 1] + _b_int[_C - 1] * _P),
                       observed=_T)
            _fit_int = pm.sample(draws=1500, tune=1000, chains=4, cores=1,
                                 random_seed=1102, target_accept=0.9,
                                 progressbar=False, return_inferencedata=True,
                                 idata_kwargs={"log_likelihood": True})

        _comp = az.compare({"interaction": _fit_int, "innovation_loss": _fit_il})

        # prediction on natural scale
        _pop_seq = np.linspace(0, 300000, 200)
        _a_post = _fit_il.posterior["a"].values.reshape(-1, 2)
        _b_post = _fit_il.posterior["b"].values.reshape(-1, 2)
        _g_post = _fit_il.posterior["g"].values.ravel()
        _pred_rows = []
        for _ci, _clabel in enumerate(["low", "high"]):
            _lam_pred = (np.exp(_a_post[:, _ci, None])
                         * _pop_seq[None, :] ** _b_post[:, _ci, None]
                         / _g_post[:, None])
            _mean = _lam_pred.mean(axis=0)
            _lo = np.quantile(_lam_pred, 0.055, axis=0)
            _hi = np.quantile(_lam_pred, 0.945, axis=0)
            for _j in range(len(_pop_seq)):
                _pred_rows.append({"population": float(_pop_seq[_j]),
                                   "mean": float(_mean[_j]),
                                   "lo": float(_lo[_j]), "hi": float(_hi[_j]),
                                   "contact": _clabel})
        _pred_df = pd.DataFrame(_pred_rows)

        _data_df = pd.DataFrame({
            "population": _pop, "T": _T,
            "contact": ["low" if c == 1 else "high" for c in _C],
            "culture": _kline["culture"],
        })
        _points = alt.Chart(_data_df).mark_circle(size=100).encode(
            x=alt.X("population:Q"), y=alt.Y("T:Q", title="total tools"),
            color="contact:N", tooltip=["culture:N", "T:Q"],
        )
        _lines = alt.Chart(_pred_df).mark_line().encode(
            x="population:Q", y="mean:Q", color="contact:N",
        )
        _band = alt.Chart(_pred_df).mark_area(opacity=0.2).encode(
            x="population:Q", y="lo:Q", y2="hi:Q", color="contact:N",
        )
        _chart = (_band + _lines + _points).properties(
            width=500, height=300,
            title="Innovation/loss: λ = exp(a[C]) · P^b[C] / g")

        _out = mo.vstack([
            mo.md(f"**Innovation/loss model**: R-hat {_d_il['max_rhat']:.4f}, "
                   f"high Pareto k (>0.7): {_high_k_il}.\n\n"
                   f"This scientifically motivated model uses raw population: "
                   f"`λ = exp(a[C]) · P^b[C] / g`. PSIS comparison:"),
            mo.ui.table(_comp.reset_index(names="Model")[
                ["Model", "elpd_loo", "se", "p_loo", "weight"]],
                selection=None, show_data_types=False),
            _chart,
        ])
    _out
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## What has been verified?

    - **Confounded simulation**: without u, direct-effect model shows spurious
      gender differences. With observed u, contrasts move toward zero.
    - **Sensitivity models**: latent u partially recovers the true effect even
      without observation. Extended A10 models with learned b/g provide wider
      but more honest uncertainty. (Long-running — use check script.)
    - **Proxy variables**: three noisy measurements jointly identify latent u.
      Estimated τ values near generating levels. (Long-running — use check script.)
    - **Kline tools**: Poisson regression with log link. PSIS comparison shows
      the interaction model has influential observations (Hawaii). The
      innovation/loss model fits better with fewer Pareto k warnings.
    - All fast fits: R-hat < 1.01, ESS > 400, zero divergences, BFMI > 0.3.
    """)
    return


if __name__ == "__main__":
    app.run()
