"""Elemental confounds, WaffleDivorce multiple regression, and the happiness collider."""
import marimo

__generated_with = "0.25.0"
app = marimo.App(width="medium")


@app.cell
def _():
    from rethinking_companion.runtime import configure_runtime
    configure_runtime()
    from rethinking_companion.gaussian_regression import assert_diagnostics, diagnostics
    import altair as alt
    import arviz as az
    import hashlib
    import json
    import marimo as mo
    import numpy as np
    import pandas as pd
    import pymc as pm
    from pathlib import Path
    from scipy.special import expit
    return (alt, assert_diagnostics, az, diagnostics, expit, hashlib, json,
            mo, np, Path, pd, pm)


@app.cell
def _(mo):
    mo.md(r"""
    # Elemental confounds and multiple regression

    Source: `scripts/05_elemental_confounds.r`. Four structural patterns
    (fork, pipe, collider, descendant) create or block statistical
    associations. Understanding these is essential before adding controls
    to a regression.

    Then: the WaffleDivorce dataset illustrates how a confound (median
    age at marriage) creates a spurious association between marriage rate
    and divorce rate. And the happiness collider simulation shows how
    conditioning on a collider (marriage status) creates a spurious
    association between age and happiness.
    """)
    return


@app.cell
def _(mo):
    section = mo.ui.dropdown(
        ["Elemental confounds", "d-separation (continuous)",
         "WaffleDivorce regression", "Happiness collider",
         "Publication collider"],
        value="Elemental confounds",
        label="Section",
    )
    section
    return (section,)


# --- Elemental confounds (binary simulations) ---

@app.cell
def _(mo, section):
    mo.stop(section.value != "Elemental confounds")
    mo.md(r"""
    ## Elemental confounds

    Four structural patterns with binary variables. In each case,
    we check whether X and Y are correlated marginally and conditionally
    on Z, matching the d-separation predictions.

    - **Fork** (X ← Z → Y): X ⊥ Y | Z (conditioning blocks the path)
    - **Pipe** (X → Z → Y): X ⊥ Y | Z (conditioning blocks the path)
    - **Collider** (X → Z ← Y): X ⊥ Y marginally; X ⊥̸ Y | Z (conditioning opens the path)
    - **Descendant** (X → Z → Y, Z → A): conditioning on A partially opens/blocks like Z
    """)
    return


@app.cell
def _(mo, np, pd, section):
    mo.stop(section.value != "Elemental confounds")
    n = 1000
    rng_ec = np.random.default_rng(2026)

    def rbern(n, p, rng):
        return rng.binomial(1, p, n)

    results = {}

    # FORK: X <- Z -> Y
    Z_fork = rbern(n, 0.5, rng_ec)
    X_fork = rbern(n, np.where(Z_fork == 0, 0.1, 0.9), rng_ec)
    Y_fork = rbern(n, np.where(Z_fork == 0, 0.1, 0.9), rng_ec)
    results["Fork"] = {
        "cor_XY": float(np.corrcoef(X_fork, Y_fork)[0, 1]),
        "cor_XY_Z0": float(np.corrcoef(X_fork[Z_fork == 0], Y_fork[Z_fork == 0])[0, 1]),
        "cor_XY_Z1": float(np.corrcoef(X_fork[Z_fork == 1], Y_fork[Z_fork == 1])[0, 1]),
        "pattern": "X ← Z → Y",
        "prediction": "X ⊥ Y | Z",
    }

    # PIPE: X -> Z -> Y
    X_pipe = rbern(n, 0.5, rng_ec)
    Z_pipe = rbern(n, np.where(X_pipe == 0, 0.1, 0.9), rng_ec)
    Y_pipe = rbern(n, np.where(Z_pipe == 0, 0.1, 0.9), rng_ec)
    results["Pipe"] = {
        "cor_XY": float(np.corrcoef(X_pipe, Y_pipe)[0, 1]),
        "cor_XY_Z0": float(np.corrcoef(X_pipe[Z_pipe == 0], Y_pipe[Z_pipe == 0])[0, 1]),
        "cor_XY_Z1": float(np.corrcoef(X_pipe[Z_pipe == 1], Y_pipe[Z_pipe == 1])[0, 1]),
        "pattern": "X → Z → Y",
        "prediction": "X ⊥ Y | Z",
    }

    # COLLIDER: X -> Z <- Y
    X_coll = rbern(n, 0.5, rng_ec)
    Y_coll = rbern(n, 0.5, rng_ec)
    Z_coll = rbern(n, np.where(X_coll + Y_coll > 0, 0.9, 0.2), rng_ec)
    results["Collider"] = {
        "cor_XY": float(np.corrcoef(X_coll, Y_coll)[0, 1]),
        "cor_XY_Z0": float(np.corrcoef(X_coll[Z_coll == 0], Y_coll[Z_coll == 0])[0, 1]),
        "cor_XY_Z1": float(np.corrcoef(X_coll[Z_coll == 1], Y_coll[Z_coll == 1])[0, 1]),
        "pattern": "X → Z ← Y",
        "prediction": "X ⊥̸ Y | Z",
    }

    # DESCENDANT: X -> Z -> Y, Z -> A
    X_desc = rbern(n, 0.5, rng_ec)
    Z_desc = rbern(n, np.where(X_desc == 0, 0.1, 0.9), rng_ec)
    Y_desc = rbern(n, np.where(Z_desc == 0, 0.1, 0.9), rng_ec)
    A_desc = rbern(n, np.where(Z_desc == 0, 0.1, 0.9), rng_ec)
    results["Descendant"] = {
        "cor_XY": float(np.corrcoef(X_desc, Y_desc)[0, 1]),
        "cor_XY_A0": float(np.corrcoef(X_desc[A_desc == 0], Y_desc[A_desc == 0])[0, 1]),
        "cor_XY_A1": float(np.corrcoef(X_desc[A_desc == 1], Y_desc[A_desc == 1])[0, 1]),
        "pattern": "X → Z → Y, Z → A",
        "prediction": "X ⊥ Y | A (partial)",
    }

    _rows = []
    for _name, _r in results.items():
        _rows.append({"Structure": _name, "Pattern": _r["pattern"],
                     "cor(X,Y)": f"{_r['cor_XY']:.3f}",
                     "cor(X,Y|Z=0)": f"{_r.get('cor_XY_Z0', _r.get('cor_XY_A0', '')):.3f}",
                     "cor(X,Y|Z=1)": f"{_r.get('cor_XY_Z1', _r.get('cor_XY_A1', '')):.3f}",
                     "Prediction": _r["prediction"]})
    confound_table = pd.DataFrame(_rows)
    mo.ui.table(confound_table)
    return confound_table, results


# --- d-separation scatter plots (continuous) ---

@app.cell
def _(mo, section):
    mo.stop(section.value != "d-separation (continuous)")
    mo.md(r"""
    ## d-separation with continuous variables

    Three structural patterns with continuous X, Y and binary Z.
    Colored by Z, with regression lines showing the marginal and
    conditional associations.
    """)
    return


@app.cell
def _(alt, expit, mo, np, pd, section):
    mo.stop(section.value != "d-separation (continuous)")
    N_dsep = 300
    rng_ds = np.random.default_rng(314)

    charts = []
    for pattern_name, sim_fn in [
        ("Pipe: X → Z → Y", lambda rng: _sim_pipe(rng, N_dsep)),
        ("Fork: X ← Z → Y", lambda rng: _sim_fork(rng, N_dsep)),
        ("Collider: X → Z ← Y", lambda rng: _sim_collider(rng, N_dsep)),
    ]:
        X, Y, Z = sim_fn(rng_ds)
        _df = pd.DataFrame({"X": X, "Y": Y, "Z": Z.astype(str)})
        _pts = alt.Chart(_df).mark_circle(size=40, opacity=0.5).encode(
            x=alt.X("X:Q"), y=alt.Y("Y:Q"),
            color=alt.Color("Z:N", scale=alt.Scale(domain=["0", "1"],
                            range=["steelblue", "coral"])))
        _marginal = alt.Chart(_df).transform_regression(
            "X", "Y", method="linear"
        ).mark_line(color="black", strokeWidth=2).encode(x="X:Q", y="Y:Q")
        _cond = alt.Chart(_df).transform_regression(
            "X", "Y", method="linear", groupby=["Z"]
        ).mark_line(strokeWidth=2, strokeDash=[4, 2]).encode(
            x="X:Q", y="Y:Q",
            color=alt.Color("Z:N", scale=alt.Scale(domain=["0", "1"],
                            range=["steelblue", "coral"])))
        charts.append((_pts + _marginal + _cond).properties(
            title=pattern_name, width=250, height=250))

    dsep_chart = alt.hconcat(*charts)
    dsep_chart
    return (dsep_chart,)


@app.cell
def _(expit, np):
    def _sim_pipe(rng, N):
        X = rng.normal(size=N)
        Z = rng.binomial(1, expit(X), N)
        Y = rng.normal(2 * Z - 1, size=N)
        return X, Y, Z

    def _sim_fork(rng, N):
        Z = rng.binomial(1, 0.5, N)
        X = rng.normal(2 * Z - 1, size=N)
        Y = rng.normal(2 * Z - 1, size=N)
        return X, Y, Z

    def _sim_collider(rng, N):
        X = rng.normal(size=N)
        Y = rng.normal(size=N)
        Z = rng.binomial(1, expit(2 * X + 2 * Y - 2), N)
        return X, Y, Z
    return _sim_collider, _sim_fork, _sim_pipe


# --- WaffleDivorce ---

@app.cell
def _(mo, section):
    mo.stop(section.value != "WaffleDivorce regression")
    mo.md(r"""
    ## WaffleDivorce: confounded multiple regression

    Waffle Houses per capita correlate with divorce rate across US states.
    But both are confounded by Southern US culture, mediated through
    median age at marriage.

    Standardize D (divorce), M (marriage rate), and A (median age at
    marriage). Fit three models: D ~ A, D ~ M, and D ~ M + A. In the
    multiple regression, A remains a strong negative predictor while M
    shrinks toward zero — the marriage rate association is confounded
    by age at marriage.

    Priors: a ~ Normal(0, 0.2), bM/bA ~ Normal(0, 0.5), sigma ~ Exp(1).
    """)
    return


@app.cell
def _(hashlib, json, np, Path, pd, section, mo):
    mo.stop(section.value != "WaffleDivorce regression")
    _folder = Path(__file__).parent.parent / "data"
    _payload = (_folder / "WaffleDivorce.csv").read_bytes()
    _prov = json.loads((_folder / "WaffleDivorce.provenance.json").read_text())
    assert hashlib.sha256(_payload).hexdigest() == _prov["sha256"]
    wd = pd.read_csv(_folder / "WaffleDivorce.csv", sep=";")
    assert len(wd) == 50

    def standardize(x):
        return (x - x.mean()) / x.std()

    dat_wd = {
        "D": standardize(wd["Divorce"].values),
        "M": standardize(wd["Marriage"].values),
        "A": standardize(wd["MedianAgeMarriage"].values),
        "South": wd["South"].values,
        "Loc": wd["Loc"].values,
    }
    return dat_wd, standardize, wd


@app.cell
def _(dat_wd, np, pm, section, mo):
    mo.stop(section.value != "WaffleDivorce regression")
    D, M, A = dat_wd["D"], dat_wd["M"], dat_wd["A"]

    # D ~ A
    with pm.Model():
        a = pm.Normal("a", 0, 0.2)
        bA = pm.Normal("bA", 0, 0.5)
        sigma = pm.Exponential("sigma", 1)
        mu = a + bA * A
        pm.Normal("D", mu, sigma, observed=D)
        fit_DA = pm.sample(draws=1500, tune=1000, chains=4, cores=1,
                           random_seed=901, target_accept=0.9,
                           progressbar=False, return_inferencedata=True)

    # D ~ M
    with pm.Model():
        a = pm.Normal("a", 0, 0.2)
        bM = pm.Normal("bM", 0, 0.5)
        sigma = pm.Exponential("sigma", 1)
        mu = a + bM * M
        pm.Normal("D", mu, sigma, observed=D)
        fit_DM = pm.sample(draws=1500, tune=1000, chains=4, cores=1,
                           random_seed=902, target_accept=0.9,
                           progressbar=False, return_inferencedata=True)

    # D ~ M + A
    with pm.Model():
        a = pm.Normal("a", 0, 0.2)
        bM = pm.Normal("bM", 0, 0.5)
        bA = pm.Normal("bA", 0, 0.5)
        sigma = pm.Exponential("sigma", 1)
        mu = a + bM * M + bA * A
        pm.Normal("D", mu, sigma, observed=D)
        fit_DMA = pm.sample(draws=1500, tune=1000, chains=4, cores=1,
                            random_seed=903, target_accept=0.9,
                            progressbar=False, return_inferencedata=True)
    return fit_DA, fit_DM, fit_DMA


@app.cell
def _(assert_diagnostics, diagnostics, fit_DA, fit_DM, fit_DMA, mo, section):
    mo.stop(section.value != "WaffleDivorce regression")
    _results = {}
    for _name, _fit, _vnames in [
        ("D ~ A", fit_DA, ["a", "bA", "sigma"]),
        ("D ~ M", fit_DM, ["a", "bM", "sigma"]),
        ("D ~ M + A", fit_DMA, ["a", "bM", "bA", "sigma"]),
    ]:
        _s, _d = diagnostics(_fit, _vnames)
        assert_diagnostics(_d)
        _results[_name] = _d
    diag_wd = _results

    mo.md(f"""**All three models pass diagnostic gates.**

| Model | R-hat | Bulk ESS | Tail ESS | Divergences |
|---|---|---|---|---|
| D ~ A | {diag_wd['D ~ A']['max_rhat']:.4f} | {diag_wd['D ~ A']['min_ess_bulk']:.0f} | {diag_wd['D ~ A']['min_ess_tail']:.0f} | {diag_wd['D ~ A']['divergences']} |
| D ~ M | {diag_wd['D ~ M']['max_rhat']:.4f} | {diag_wd['D ~ M']['min_ess_bulk']:.0f} | {diag_wd['D ~ M']['min_ess_tail']:.0f} | {diag_wd['D ~ M']['divergences']} |
| D ~ M + A | {diag_wd['D ~ M + A']['max_rhat']:.4f} | {diag_wd['D ~ M + A']['min_ess_bulk']:.0f} | {diag_wd['D ~ M + A']['min_ess_tail']:.0f} | {diag_wd['D ~ M + A']['divergences']} |
""")
    return (diag_wd,)


@app.cell
def _(alt, fit_DA, fit_DM, fit_DMA, mo, np, pd, section):
    mo.stop(section.value != "WaffleDivorce regression")
    _rows = []
    for _model_name, _fit, _params in [
        ("D ~ A", fit_DA, {"bA": "bA"}),
        ("D ~ M", fit_DM, {"bM": "bM"}),
        ("D ~ M + A", fit_DMA, {"bM": "bM", "bA": "bA"}),
    ]:
        for _label, _var in _params.items():
            _vals = _fit.posterior[_var].values.ravel()
            _rows.append({
                "model": _model_name, "parameter": _label,
                "mean": float(_vals.mean()),
                "lo": float(np.percentile(_vals, 5.5)),
                "hi": float(np.percentile(_vals, 94.5)),
            })
    coef_df = pd.DataFrame(_rows)
    coef_chart = alt.Chart(coef_df).mark_point(size=80).encode(
        x=alt.X("mean:Q", title="Coefficient (standardized)"),
        y=alt.Y("parameter:N", title=""),
        color=alt.Color("model:N"),
    ) + alt.Chart(coef_df).mark_rule(strokeWidth=2).encode(
        x="lo:Q", x2="hi:Q", y="parameter:N", color="model:N",
    )
    coef_chart = coef_chart.properties(
        title="Posterior coefficients (89% interval)", width=400, height=200)
    coef_chart
    return coef_chart, coef_df


@app.cell
def _(coef_df, mo, section):
    mo.stop(section.value != "WaffleDivorce regression")
    _dma = coef_df[coef_df["model"] == "D ~ M + A"]
    _bA = _dma[_dma["parameter"] == "bA"]["mean"].values[0]
    _bM = _dma[_dma["parameter"] == "bM"]["mean"].values[0]
    mo.md(f"""In the multiple regression D ~ M + A:
- **bA = {_bA:.3f}** — age at marriage remains a strong negative predictor.
- **bM = {_bM:.3f}** — marriage rate shrinks toward zero after conditioning on A.

This is the fork confound: A → M and A → D, so the marginal M–D
association is confounded by A. Once we condition on A, M carries
little additional information about D.""")
    return


# --- Publication collider ---

@app.cell
def _(mo, section):
    mo.stop(section.value != "Publication collider")
    mo.md(r"""
    ## Publication bias as a collider

    Newsworthiness and trustworthiness are independent traits of a study.
    But selection (publication) depends on both: only the top-scoring
    studies get published. Among published studies, the two traits become
    negatively correlated — conditioning on the collider opens the path.
    """)
    return


@app.cell
def _(alt, mo, np, pd, section):
    mo.stop(section.value != "Publication collider")
    rng_pub = np.random.default_rng(1914)
    N_pub = 200
    p_select = 0.1
    nw = rng_pub.normal(size=N_pub)
    tw = rng_pub.normal(size=N_pub)
    s = nw + tw
    q = np.quantile(s, 1 - p_select)
    selected = s >= q

    _df = pd.DataFrame({"Newsworthiness": nw, "Trustworthiness": tw,
                         "Selected": np.where(selected, "Selected", "Not selected")})
    _pts = alt.Chart(_df).mark_circle(size=40).encode(
        x=alt.X("Newsworthiness:Q"), y=alt.Y("Trustworthiness:Q"),
        color=alt.Color("Selected:N", scale=alt.Scale(
            domain=["Selected", "Not selected"], range=["coral", "lightgray"])))
    _sel_df = _df[_df["Selected"] == "Selected"]
    _line = alt.Chart(_sel_df).transform_regression(
        "Newsworthiness", "Trustworthiness", method="linear"
    ).mark_line(color="black", strokeWidth=2).encode(
        x="Newsworthiness:Q", y="Trustworthiness:Q")

    cor_sel = float(np.corrcoef(nw[selected], tw[selected])[0, 1])
    pub_chart = (_pts + _line).properties(
        title=f"Publication collider (r among selected = {cor_sel:.3f})",
        width=400, height=300)
    pub_chart
    return (pub_chart,)


# --- Happiness collider ---

@app.cell
def _(mo, section):
    mo.stop(section.value != "Happiness collider")
    mo.md(r"""
    ## Happiness collider simulation

    Happiness is a fixed trait (assigned at birth, never changes). Marriage
    probability depends on happiness via `inv_logit(happiness - 4)` — happier
    people are more likely to marry. Age simply accumulates.

    Age and happiness are marginally independent. But conditioning on
    marriage status (a collider: happiness → married ← age) creates a
    spurious negative correlation: among married people, older individuals
    tend to be less happy (because unhappy people needed more years of
    exposure to eventually marry).

    This is the `sim_happiness()` function from the rethinking package.
    """)
    return


@app.cell
def _(alt, expit, mo, np, pd, section):
    mo.stop(section.value != "Happiness collider")

    def sim_happiness(seed=1977, N_years=1000, max_age=65, N_births=20, aom=18):
        rng = np.random.default_rng(seed)
        A = np.array([], dtype=float)
        H = np.array([], dtype=float)
        M = np.array([], dtype=int)
        for _t in range(N_years):
            A = A + 1
            newborn_H = np.linspace(-2, 2, N_births)
            A = np.concatenate([A, np.ones(N_births)])
            H = np.concatenate([H, newborn_H])
            M = np.concatenate([M, np.zeros(N_births, dtype=int)])
            eligible = (A >= aom) & (M == 0)
            marry_prob = expit(H - 4) * eligible
            M = np.where(rng.random(len(A)) < marry_prob, 1, M).astype(int)
            alive = A <= max_age
            A, H, M = A[alive], H[alive], M[alive]
        return pd.DataFrame({"age": A, "married": M, "happiness": H})

    hap = sim_happiness(seed=1977, N_years=1000)

    cor_marginal = float(np.corrcoef(hap["age"], hap["happiness"])[0, 1])
    _married = hap[hap["married"] == 1]
    cor_married = float(np.corrcoef(_married["age"], _married["happiness"])[0, 1])
    _single = hap[hap["married"] == 0]
    cor_single = float(np.corrcoef(_single["age"], _single["happiness"])[0, 1])

    _df = hap.copy()
    _df["status"] = np.where(_df["married"] == 1, "Married", "Single")
    _pts = alt.Chart(_df).mark_circle(size=20, opacity=0.4).encode(
        x=alt.X("age:Q", title="Age (years)"),
        y=alt.Y("happiness:Q", title="Happiness"),
        color=alt.Color("status:N", scale=alt.Scale(
            domain=["Married", "Single"], range=["coral", "lightgray"])))
    _cond = alt.Chart(_df).transform_regression(
        "age", "happiness", method="linear", groupby=["status"]
    ).mark_line(strokeWidth=2).encode(
        x="age:Q", y="happiness:Q",
        color=alt.Color("status:N", scale=alt.Scale(
            domain=["Married", "Single"], range=["coral", "lightgray"])))

    hap_chart = (_pts + _cond).properties(
        title="Happiness collider: conditioning on marriage", width=500, height=300)
    hap_chart
    return cor_marginal, cor_married, cor_single, hap, hap_chart, sim_happiness


@app.cell
def _(cor_marginal, cor_married, cor_single, mo, section):
    mo.stop(section.value != "Happiness collider")
    mo.md(f"""**Correlations**:
- Marginal cor(age, happiness) = **{cor_marginal:.4f}** (near zero)
- Among married: cor(age, happiness) = **{cor_married:.4f}** (negative — collider bias)
- Among single: cor(age, happiness) = **{cor_single:.4f}**

The negative slope among married people is entirely spurious. Happiness
does not decline with age in this simulation — it is fixed at birth.
The pattern appears because conditioning on the collider (marriage)
opens the path Age → Married ← Happiness.""")
    return


if __name__ == "__main__":
    app.run()
