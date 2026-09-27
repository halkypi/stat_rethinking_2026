"""Binomial GLMs: logit link, Simpson's paradox, and marginal causal effects."""
import marimo

__generated_with = "0.25.0"
app = marimo.App(width="medium")


@app.cell
def _():
    from rethinking_companion.glm import (
        inv_logit, load_ucbadmit, ucbadmit_arrays,
    )
    from rethinking_companion.gaussian_regression import assert_diagnostics, diagnostics
    import altair as alt
    import marimo as mo
    import numpy as np
    import pandas as pd
    import pymc as pm
    return (alt, assert_diagnostics, diagnostics, inv_logit,
            load_ucbadmit, mo, np, pd, pm, ucbadmit_arrays)


@app.cell
def _(mo):
    mo.md(r"""
    # Binomial GLMs and Simpson's paradox

    Source: `scripts/09_binomial_GLMs.r`. This lesson introduces the first
    non-Gaussian likelihoods — Bernoulli and Binomial — with a logit link.
    The UC Berkeley admissions data illustrates Simpson's paradox: the total
    effect of gender favors men, but within most departments the effect
    reverses or vanishes.

    The key result is the **marginal causal effect**: simulate counterfactual
    admissions as if all applicants were perceived as women vs men, weighted
    by actual department application volumes.
    """)
    return


@app.cell
def _(mo):
    section = mo.ui.dropdown(
        ["Logit link and priors",
         "Generative simulation",
         "UCBadmit real data",
         "Marginal causal effect"],
        value="Logit link and priors",
        label="Section",
    )
    section
    return (section,)


@app.cell
def _(alt, inv_logit, mo, np, pd, section):
    if section.value != "Logit link and priors":
        _out = mo.md("Select **Logit link and priors** to see this section.")
    else:
        _x = np.linspace(-6, 6, 200)
        _logit_df = pd.DataFrame({"logit(p)": _x, "p": inv_logit(_x)})
        _logit_curve = alt.Chart(_logit_df).mark_line(
            color="firebrick", strokeWidth=3
        ).encode(
            x=alt.X("logit(p):Q"), y=alt.Y("p:Q", scale=alt.Scale(domain=[0, 1])),
        ).properties(width=450, height=250, title="The logit link: logit(p) ↔ p")

        _rng = np.random.default_rng(42)
        _wide = inv_logit(_rng.normal(0, 10, 10000))
        _narrow = inv_logit(_rng.normal(0, 1.5, 10000))
        _prior_df = pd.concat([
            pd.DataFrame({"p": _wide, "Prior": "Normal(0, 10)"}),
            pd.DataFrame({"p": _narrow, "Prior": "Normal(0, 1.5)"}),
        ])
        _prior_chart = alt.Chart(_prior_df).mark_bar(opacity=0.6).encode(
            x=alt.X("p:Q", bin=alt.Bin(maxbins=50), title="probability"),
            y=alt.Y("count():Q"), color="Prior:N",
        ).properties(width=450, height=200,
                     title="Prior predictive: intercept on probability scale")

        _a = _rng.normal(0, 1.5, 10)
        _b = _rng.normal(0, 0.5, 10)
        _xseq = np.linspace(-3, 3, 100)
        _lines = []
        for _i in range(10):
            _lines.extend([{"x": float(_xi), "p": float(inv_logit(_a[_i] + _b[_i] * _xi)),
                            "draw": _i} for _xi in _xseq])
        _lines_df = pd.DataFrame(_lines)
        _slope_chart = alt.Chart(_lines_df).mark_line(opacity=0.7).encode(
            x=alt.X("x:Q", title="x value"),
            y=alt.Y("p:Q", title="probability", scale=alt.Scale(domain=[0, 1])),
            color=alt.Color("draw:N", legend=None),
        ).properties(width=450, height=250,
                     title="Prior predictive lines: a ~ N(0,1.5), b ~ N(0,0.5)")

        _out = mo.vstack([
            mo.md("Normal(0, 10) on the logit scale implies extreme probabilities "
                   "near 0 or 1. Normal(0, 1.5) is a weakly informative prior that "
                   "permits the full range without concentrating at extremes."),
            _logit_curve, _prior_chart, _slope_chart,
        ])
    _out
    return


@app.cell
def _(assert_diagnostics, diagnostics, inv_logit, mo, np, pd, pm, section, alt):
    if section.value != "Generative simulation":
        _out = mo.md("Select **Generative simulation** to see this section.")
    else:
        _rng = np.random.default_rng(1999)
        _N = 1000
        _G = _rng.choice([1, 2], size=_N)
        _D = _rng.binomial(1, np.where(_G == 1, 0.3, 0.8)) + 1
        _accept = np.array([[0.05, 0.1], [0.2, 0.3]])
        _p = np.array([_accept[_D[i]-1, _G[i]-1] for i in range(_N)])
        _A = _rng.binomial(1, _p)

        with pm.Model(coords={"gender": ["F", "M"]}):
            _a1 = pm.Normal("a", 0, 1, dims="gender")
            pm.Bernoulli("A", logit_p=_a1[_G - 1], observed=_A)
            _fit1 = pm.sample(draws=1500, tune=1000, chains=4, cores=1,
                              random_seed=901, target_accept=0.9,
                              progressbar=False, return_inferencedata=True)
        _, _d1 = diagnostics(_fit1, ["a"])
        assert_diagnostics(_d1)

        with pm.Model(coords={"gender": ["F", "M"], "dept": ["1", "2"]}):
            _a2 = pm.Normal("a", 0, 1, dims=("gender", "dept"))
            pm.Bernoulli("A", logit_p=_a2[_G - 1, _D - 1], observed=_A)
            _fit2 = pm.sample(draws=1500, tune=1000, chains=4, cores=1,
                              random_seed=902, target_accept=0.9,
                              progressbar=False, return_inferencedata=True)
        _, _d2 = diagnostics(_fit2, ["a"])
        assert_diagnostics(_d2)

        _post1 = _fit1.posterior["a"].values.reshape(-1, 2)
        _total_c = inv_logit(_post1[:, 0]) - inv_logit(_post1[:, 1])
        _post2 = _fit2.posterior["a"].values.reshape(-1, 2, 2)
        _dir_D1 = inv_logit(_post2[:, 0, 0]) - inv_logit(_post2[:, 1, 0])
        _dir_D2 = inv_logit(_post2[:, 0, 1]) - inv_logit(_post2[:, 1, 1])

        _cdf = pd.concat([
            pd.DataFrame({"contrast": _total_c, "Model": "Total (m1)"}),
            pd.DataFrame({"contrast": _dir_D1, "Model": "Direct Dept 1"}),
            pd.DataFrame({"contrast": _dir_D2, "Model": "Direct Dept 2"}),
        ])
        _cchart = alt.Chart(_cdf).mark_bar(opacity=0.6).encode(
            x=alt.X("contrast:Q", bin=alt.Bin(maxbins=60),
                     title="F − M contrast (probability scale)"),
            y="count():Q", color="Model:N",
        ).properties(width=500, height=200)

        # aggregated binomial equivalence
        _simdf = pd.DataFrame({"A": _A, "G": _G, "D": _D})
        _agg = _simdf.groupby(["G", "D"]).agg(
            admit=("A", "sum"), n=("A", "count")).reset_index()
        with pm.Model(coords={"gender": ["F", "M"], "dept": ["1", "2"]}):
            _ab = pm.Normal("a", 0, 1, dims=("gender", "dept"))
            pm.Binomial("A", n=_agg["n"].values,
                        logit_p=_ab[_agg["G"].values - 1, _agg["D"].values - 1],
                        observed=_agg["admit"].values)
            _fitb = pm.sample(draws=1500, tune=1000, chains=4, cores=1,
                              random_seed=903, target_accept=0.9,
                              progressbar=False, return_inferencedata=True)
        _, _db = diagnostics(_fitb, ["a"])
        assert_diagnostics(_db)

        _pb = _fit2.posterior["a"].values.reshape(-1, 4)
        _pbin = _fitb.posterior["a"].values.reshape(-1, 4)
        _mdiff = np.abs(_pb.mean(0) - _pbin.mean(0)).max()

        _out = mo.vstack([
            mo.md(f"**Generative simulation**: N={_N}, mediator DAG G → D → A "
                   f"with direct G → A.\n\n"
                   f"Total effect R-hat {_d1['max_rhat']:.4f}, "
                   f"direct effect R-hat {_d2['max_rhat']:.4f}.\n\n"
                   f"Aggregated binomial vs Bernoulli max mean difference: "
                   f"**{_mdiff:.4f}** (should be small — Monte Carlo noise)."),
            _cchart,
        ])
    _out
    return


@app.cell
def _(assert_diagnostics, diagnostics, inv_logit, load_ucbadmit, mo, np, pd, pm,
      section, ucbadmit_arrays, alt):
    if section.value not in ("UCBadmit real data", "Marginal causal effect"):
        _out = mo.md("Select **UCBadmit real data** or **Marginal causal effect**.")
    else:
        _d = load_ucbadmit()
        _dat = ucbadmit_arrays(_d)
        _dlabels = _dat["dept_labels"]

        with pm.Model(coords={"gender": ["F", "M"]}):
            _aG = pm.Normal("a", 0, 1, dims="gender")
            pm.Binomial("A", n=_dat["N"], logit_p=_aG[_dat["G"] - 1],
                        observed=_dat["A"])
            fit_mG = pm.sample(draws=1500, tune=1000, chains=4, cores=1,
                               random_seed=911, target_accept=0.9,
                               progressbar=False, return_inferencedata=True)
        _, _dmG = diagnostics(fit_mG, ["a"])
        assert_diagnostics(_dmG)

        with pm.Model(coords={"gender": ["F", "M"], "dept": _dlabels}):
            _aGD = pm.Normal("a", 0, 1, dims=("gender", "dept"))
            pm.Binomial("A", n=_dat["N"], logit_p=_aGD[_dat["G"] - 1, _dat["D"] - 1],
                        observed=_dat["A"])
            fit_mGD = pm.sample(draws=1500, tune=1000, chains=4, cores=1,
                                random_seed=912, target_accept=0.9,
                                progressbar=False, return_inferencedata=True)
        _, _dmGD = diagnostics(fit_mGD, ["a"])
        assert_diagnostics(_dmGD)

        # total contrast
        _postG = fit_mG.posterior["a"].values.reshape(-1, 2)
        total_diff = inv_logit(_postG[:, 0]) - inv_logit(_postG[:, 1])

        # per-department contrasts
        _postGD = fit_mGD.posterior["a"].values.reshape(-1, 2, 6)
        dept_contrasts = np.column_stack([
            inv_logit(_postGD[:, 0, i]) - inv_logit(_postGD[:, 1, i])
            for i in range(6)])

        if section.value == "UCBadmit real data":
            _rows = []
            for _i in range(6):
                _rows.extend([{"contrast": float(_v), "dept": _dlabels[_i]}
                              for _v in dept_contrasts[::6, _i]])
            _rows.extend([{"contrast": float(_v), "dept": "Total"}
                          for _v in total_diff[::6]])
            _chart = alt.Chart(pd.DataFrame(_rows)).mark_boxplot(extent=1.5).encode(
                x=alt.X("dept:N", title="Department"),
                y=alt.Y("contrast:Q", title="F − M admission probability"),
            ).properties(width=500, height=250,
                         title="Simpson's paradox: total vs per-department gender contrast")

            _out = mo.vstack([
                mo.md(f"**UCBadmit**: total effect R-hat {_dmG['max_rhat']:.4f}, "
                       f"direct effect R-hat {_dmGD['max_rhat']:.4f}.\n\n"
                       f"Total: P(admit|F) − P(admit|M) ≈ "
                       f"**{float(total_diff.mean()):.3f}** "
                       f"(negative = men admitted more overall).\n\n"
                       "But within most departments, the female admission rate "
                       "equals or exceeds the male rate — Simpson's paradox."),
                _chart,
            ])
        else:
            # Marginal causal effect section
            _apps = np.array([_dat["N"][_dat["D"] == i + 1].sum() for i in range(6)])
            _D_exp = np.repeat(np.arange(6), _apps)
            _pF = inv_logit(_postGD[:, 0, :][:, _D_exp])
            _pM = inv_logit(_postGD[:, 1, :][:, _D_exp])
            marginal_effect = _pF.mean(axis=1) - _pM.mean(axis=1)

            _edf = pd.DataFrame({"effect": marginal_effect})
            _echart = (
                alt.Chart(_edf).mark_bar(opacity=0.7, color="firebrick").encode(
                    x=alt.X("effect:Q", bin=alt.Bin(maxbins=60),
                             title="Marginal causal effect of gender perception (F − M)"),
                    y="count():Q",
                ).properties(width=500, height=200)
                + alt.Chart(pd.DataFrame({"x": [0]})).mark_rule(
                    color="black", strokeDash=[4, 4]).encode(x="x:Q")
            )

            _w = _apps / _apps.max()
            _wrows = []
            for _i in range(6):
                _wrows.extend([{"contrast": float(_v), "dept": _dlabels[_i],
                                "weight": float(_w[_i])}
                               for _v in dept_contrasts[::6, _i]])
            _wchart = alt.Chart(pd.DataFrame(_wrows)).mark_boxplot(extent=1.5).encode(
                x=alt.X("dept:N", title="Department"),
                y=alt.Y("contrast:Q", title="F − M admission probability"),
            ).properties(width=500, height=200,
                         title="Per-department contrasts (larger depts dominate the marginal effect)")

            _out = mo.vstack([
                mo.md(f"**Marginal causal effect** of gender perception: "
                       f"**{float(marginal_effect.mean()):.4f}** "
                       f"(89% CI: [{float(np.quantile(marginal_effect, 0.055)):.4f}, "
                       f"{float(np.quantile(marginal_effect, 0.945)):.4f}]).\n\n"
                       "This is the direct causal effect of being perceived as female "
                       "vs male on admission probability, averaged over the actual "
                       "department mix. It is small and centered near zero."),
                _echart, _wchart,
            ])
    _out
    return (dept_contrasts, fit_mG, fit_mGD, marginal_effect, total_diff)


@app.cell
def _(mo):
    mo.md(r"""
    ## What has been verified?

    - **Logit link**: `inv_logit` is `scipy.special.expit`; roundtrip with `logit`
      confirms numerical identity.
    - **Generative simulation**: total and direct effect models both pass diagnostic
      gates. The aggregated binomial fit matches the Bernoulli fit within Monte
      Carlo noise.
    - **UCBadmit**: total effect shows men admitted at higher rates overall. Within
      departments, the female rate generally equals or exceeds the male rate —
      Simpson's paradox. Both models pass diagnostic gates.
    - **Marginal causal effect**: small, centered near zero. The gender contrast in
      overall admissions is explained by differential department application patterns,
      not by direct discrimination.
    - All fits: R-hat < 1.01, ESS > 400, zero divergences, BFMI > 0.3.

    NUTS replaces `quap`/`ulam` from the R source. The animation and contour
    interpolation from lines 31–137 are deferred.
    """)
    return


if __name__ == "__main__":
    app.run()
