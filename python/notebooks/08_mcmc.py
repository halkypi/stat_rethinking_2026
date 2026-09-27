"""MCMC mechanics: King Markov, HMC leapfrog, WaffleDivorce workflow, diagnostics."""
import marimo

__generated_with = "0.25.0"
app = marimo.App(width="medium")


@app.cell
def _():
    from rethinking_companion.mcmc import (
        fit_bad_chains, fit_waffle_divorce, hmc_leapfrog, hmc_sample,
        king_markov, load_waffle_divorce, make_2d_target,
        make_correlated_target, rhat_over_time,
    )
    from rethinking_companion.gaussian_regression import assert_diagnostics, diagnostics
    import altair as alt
    import arviz as az
    import marimo as mo
    import numpy as np
    import pandas as pd
    return (alt, assert_diagnostics, az, diagnostics, fit_bad_chains,
            fit_waffle_divorce, hmc_leapfrog, hmc_sample, king_markov,
            load_waffle_divorce, make_2d_target, make_correlated_target,
            mo, np, pd, rhat_over_time)


# ── Section 1: King Markov ──────────────────────────────────────────────────

@app.cell
def _(mo):
    mo.md(r"""
    # MCMC Mechanics

    Source: `scripts/08_MCMC.r`, `scripts/08_mHMC.stan`, `scripts/LB03_ess acf example.r`.

    ## King Markov — Metropolis on a discrete archipelago

    Ten islands with populations proportional to 1, 2, …, 10. The king
    proposes moving ±1 (wrapping around) and accepts with probability
    equal to the ratio of the proposed island's population to the current
    island's population. The stationary distribution matches the target:
    island *k* is visited with frequency *k* / 55.
    """)
    return


@app.cell
def _(mo):
    n_steps_slider = mo.ui.slider(
        start=1000, stop=200000, step=1000, value=100000,
        label="Number of steps",
    )
    n_steps_slider
    return (n_steps_slider,)


@app.cell
def _(king_markov, n_steps_slider, np):
    positions = king_markov(n_steps=n_steps_slider.value, seed=42)
    burn_in = min(10000, n_steps_slider.value // 10)
    post_burn = positions[burn_in:]
    empirical = np.bincount(post_burn, minlength=10) / len(post_burn)
    target = np.arange(1, 11) / 55.0
    return burn_in, empirical, positions, post_burn, target


@app.cell
def _(alt, empirical, np, pd, target):
    df_freq = pd.DataFrame({
        "Island": np.tile(np.arange(1, 11), 2),
        "Frequency": np.concatenate([empirical, target]),
        "Source": ["Empirical"] * 10 + ["Target (k/55)"] * 10,
    })
    chart_freq = alt.Chart(df_freq).mark_bar(opacity=0.7).encode(
        x=alt.X("Island:O"),
        y=alt.Y("Frequency:Q"),
        color=alt.Color("Source:N"),
        xOffset="Source:N",
    ).properties(title="Stationary distribution vs target", width=500)
    chart_freq
    return (chart_freq,)


@app.cell
def _(alt, np, pd, positions):
    n_trace = min(2000, len(positions))
    df_trace = pd.DataFrame({"step": np.arange(n_trace), "island": positions[:n_trace] + 1})
    chart_trace = alt.Chart(df_trace).mark_line(strokeWidth=1).encode(
        x=alt.X("step:Q", title="Step"),
        y=alt.Y("island:Q", scale=alt.Scale(domain=[1, 10]), title="Island"),
    ).properties(title="King Markov chain trace (first 2000 steps)", width=600, height=200)
    chart_trace
    return (chart_trace,)


# ── Section 2: HMC Leapfrog Mechanics ───────────────────────────────────────

@app.cell
def _(mo):
    mo.md(r"""
    ## HMC Leapfrog Mechanics

    Hamiltonian Monte Carlo uses a leapfrog integrator to propose new
    positions in parameter space. The Hamiltonian $H = U(q) + K(p)$ is
    conserved along exact trajectories; the leapfrog approximation
    introduces small errors that grow with step size.

    **Target**: 100 synthetic observations $y \sim \text{Normal}(\mu, \sigma)$
    with mean zero. Parameters: $\mu$ and $\log\sigma$.
    """)
    return


@app.cell
def _(make_2d_target, np):
    rng_hmc = np.random.default_rng(7)
    y_hmc = np.abs(rng_hmc.normal(size=50))
    y_hmc = np.concatenate([y_hmc, -y_hmc])
    U_2d, grad_U_2d = make_2d_target(y_hmc, a=0, b=1, k=0, d=0.3)
    return U_2d, grad_U_2d, y_hmc


@app.cell
def _(U_2d, grad_U_2d, hmc_sample, np):
    samples_hmc, trajs_hmc = hmc_sample(
        U_2d, grad_U_2d, step_size=0.01, n_leapfrog=12,
        q_init=np.array([-0.4, 0.2]), n_samples=10, seed=12,
    )
    return samples_hmc, trajs_hmc


@app.cell
def _(U_2d, alt, np, pd, trajs_hmc):
    _mu_grid = np.linspace(-0.5, 0.5, 60)
    _ls_grid = np.linspace(-0.3, 0.4, 60)
    _MU, _LS = np.meshgrid(_mu_grid, _ls_grid)
    _Z = np.array([[U_2d(np.array([m, l])) for m in _mu_grid] for l in _ls_grid])
    _df_contour = pd.DataFrame({"mu": _MU.ravel(), "log_sigma": _LS.ravel(), "U": _Z.ravel()})

    _contour = alt.Chart(_df_contour).mark_rect().encode(
        x=alt.X("mu:Q", bin=alt.Bin(maxbins=60)),
        y=alt.Y("log_sigma:Q", bin=alt.Bin(maxbins=60)),
        color=alt.Color("U:Q", scale=alt.Scale(scheme="blues"), legend=None),
    ).properties(width=450, height=350)

    _traj_rows = []
    for _i, _t in enumerate(trajs_hmc):
        for _j, _pt in enumerate(_t["trajectory"]):
            _traj_rows.append({"mu": _pt[0], "log_sigma": _pt[1], "traj": _i, "step": _j})
    _df_traj = pd.DataFrame(_traj_rows)

    _lines = alt.Chart(_df_traj).mark_line(strokeWidth=2).encode(
        x="mu:Q", y="log_sigma:Q",
        detail="traj:N", color=alt.value("#3182bd"),
    )

    _ep_rows = []
    for _i2, _t2 in enumerate(trajs_hmc):
        _ep = _t2["trajectory"][-1]
        _ep_rows.append({"mu": _ep[0], "log_sigma": _ep[1],
                         "accepted": _t2["accepted"], "traj": _i2})
    _df_ep = pd.DataFrame(_ep_rows)
    _points = alt.Chart(_df_ep).mark_point(size=80, strokeWidth=2).encode(
        x="mu:Q", y="log_sigma:Q",
        shape=alt.Shape("accepted:N", scale=alt.Scale(
            domain=[True, False], range=["circle", "cross"])),
        color=alt.condition(
            alt.datum.accepted, alt.value("#3182bd"), alt.value("#e6550d")),
    )

    chart_hmc = (_contour + _lines + _points).properties(
        title="HMC trajectories on 2D target (step=0.01, L=12)")
    chart_hmc
    return (chart_hmc,)


@app.cell
def _(mo, pd, trajs_hmc):
    _energy_rows = [{"Trajectory": _i, "H_init": _t["H_init"],
                     "H_final": _t["H_final"], "|ΔH|": abs(_t["dH"]),
                     "Accepted": _t["accepted"]}
                    for _i, _t in enumerate(trajs_hmc)]
    df_energy = pd.DataFrame(_energy_rows)
    mo.md("### Energy conservation along trajectories")
    return (df_energy,)


@app.cell
def _(df_energy, mo):
    mo.ui.table(df_energy)
    return


# ── Divergent trajectory demonstration ──────────────────────────────────────

@app.cell
def _(mo):
    mo.md(r"""
    ### Step-size sensitivity: U-turns and divergences

    With a large step size on a correlated target ($\mu = a_1 + a_2$),
    the leapfrog integrator overshoots, producing U-turns and large energy
    errors (divergences).
    """)
    return


@app.cell
def _(hmc_sample, make_correlated_target, np):
    rng_div = np.random.default_rng(7)
    y_div = np.abs(rng_div.normal(size=20))
    y_div = np.concatenate([y_div, -y_div])
    U_corr, grad_U_corr = make_correlated_target(y_div, a=0, b=0.5)
    samples_div, trajs_div = hmc_sample(
        U_corr, grad_U_corr, step_size=0.15, n_leapfrog=15,
        q_init=np.array([-0.4, -0.4]), n_samples=3, seed=42,
    )
    return samples_div, trajs_div, U_corr


@app.cell
def _(U_corr, alt, np, pd, trajs_div):
    _a_grid = np.linspace(-1.5, 1.5, 60)
    _A1, _A2 = np.meshgrid(_a_grid, _a_grid)
    _Z_corr = np.array([[U_corr(np.array([a1, a2])) for a1 in _a_grid] for a2 in _a_grid])
    _df_bg = pd.DataFrame({"a1": _A1.ravel(), "a2": _A2.ravel(), "U": _Z_corr.ravel()})

    _bg = alt.Chart(_df_bg).mark_rect().encode(
        x=alt.X("a1:Q", bin=alt.Bin(maxbins=60)),
        y=alt.Y("a2:Q", bin=alt.Bin(maxbins=60)),
        color=alt.Color("U:Q", scale=alt.Scale(scheme="blues"), legend=None),
    ).properties(width=400, height=400)

    _traj_rows_d = []
    for _i, _t in enumerate(trajs_div):
        for _j, _pt in enumerate(_t["trajectory"]):
            _traj_rows_d.append({"a1": _pt[0], "a2": _pt[1], "traj": _i, "step": _j})
    _df_td = pd.DataFrame(_traj_rows_d)
    _lines_d = alt.Chart(_df_td).mark_line(strokeWidth=2).encode(
        x="a1:Q", y="a2:Q", detail="traj:N", color=alt.value("#e6550d"),
    )

    chart_div = (_bg + _lines_d).properties(
        title="Large step size on correlated target (step=0.15, L=15)")
    chart_div
    return (chart_div,)


@app.cell
def _(mo, pd, trajs_div):
    _energy_div = [{"Trajectory": _i, "|ΔH|": abs(_t["dH"]),
                    "Accepted": _t["accepted"]}
                   for _i, _t in enumerate(trajs_div)]
    df_energy_div = pd.DataFrame(_energy_div)
    mo.md("Energy errors with large step size:")
    return (df_energy_div,)


@app.cell
def _(df_energy_div, mo):
    mo.ui.table(df_energy_div)
    return


# ── Section 3: WaffleDivorce NUTS Workflow ──────────────────────────────────

@app.cell
def _(mo):
    mo.md(r"""
    ## WaffleDivorce: NUTS Workflow

    Source: `scripts/08_MCMC.r` lines 529–563 and `scripts/08_mHMC.stan`.

    Standardize Divorce (D), Marriage rate (M), and Median Age at Marriage (A),
    then fit $D \sim \text{Normal}(a + b_M \cdot M + b_A \cdot A, \sigma)$
    with four-chain NUTS.

    Priors: $a \sim \text{Normal}(0, 0.2)$, $b_M \sim \text{Normal}(0, 0.5)$,
    $b_A \sim \text{Normal}(0, 0.5)$, $\sigma \sim \text{Exponential}(1)$.
    """)
    return


@app.cell
def _(load_waffle_divorce, np):
    wd = load_waffle_divorce()
    def _standardize(x):
        return (x - x.mean()) / x.std()
    dat_wd = {
        "D": _standardize(wd["Divorce"].values).astype(np.float64),
        "M": _standardize(wd["Marriage"].values).astype(np.float64),
        "A": _standardize(wd["MedianAgeMarriage"].values).astype(np.float64),
    }
    return (dat_wd, wd)


@app.cell
def _(dat_wd, fit_waffle_divorce):
    fit_wd = fit_waffle_divorce(dat_wd)
    return (fit_wd,)


@app.cell
def _(assert_diagnostics, diagnostics, fit_wd, mo):
    summary_wd, diag_wd = diagnostics(fit_wd, ("a", "bM", "bA", "sigma"))
    assert_diagnostics(diag_wd)
    mo.md(f"""
    ### Diagnostics

    - R-hat: {diag_wd['max_rhat']:.4f}
    - Min bulk ESS: {diag_wd['min_ess_bulk']:.0f}
    - Min tail ESS: {diag_wd['min_ess_tail']:.0f}
    - Divergences: {diag_wd['divergences']}
    - Min BFMI: {diag_wd['min_bfmi']:.3f}
    """)
    return (diag_wd, summary_wd)


@app.cell
def _(mo, summary_wd):
    mo.ui.table(summary_wd.reset_index())
    return


@app.cell
def _(alt, fit_wd, np, pd):
    _trace_rows = []
    for _var in ("a", "bM", "bA", "sigma"):
        _vals = fit_wd.posterior[_var].values
        for _c in range(_vals.shape[0]):
            for _d in range(_vals.shape[1]):
                _trace_rows.append({"parameter": _var, "chain": _c,
                                    "draw": _d, "value": float(_vals[_c, _d])})
    _df_trace_wd = pd.DataFrame(_trace_rows)
    chart_trace_wd = alt.Chart(_df_trace_wd).mark_line(strokeWidth=0.5, opacity=0.6).encode(
        x="draw:Q", y="value:Q",
        color=alt.Color("chain:N", legend=None),
    ).facet(facet="parameter:N", columns=2).properties(title="Traceplots")
    chart_trace_wd
    return (chart_trace_wd,)


@app.cell
def _(alt, fit_wd, np, pd):
    _rank_rows = []
    for _var in ("a", "bM", "bA", "sigma"):
        _vals = fit_wd.posterior[_var].values
        _flat = _vals.ravel()
        _ranks = np.argsort(np.argsort(_flat)).reshape(_vals.shape)
        for _c in range(_vals.shape[0]):
            _hist, _edges = np.histogram(_ranks[_c], bins=20)
            for _j in range(len(_hist)):
                _rank_rows.append({"parameter": _var, "chain": _c,
                                   "rank_bin": (_edges[_j] + _edges[_j+1]) / 2,
                                   "count": int(_hist[_j])})
    _df_rank = pd.DataFrame(_rank_rows)
    chart_rank = alt.Chart(_df_rank).mark_bar(opacity=0.6).encode(
        x=alt.X("rank_bin:Q", title="Rank"),
        y=alt.Y("count:Q", title="Count"),
        color=alt.Color("chain:N", legend=None),
    ).facet(facet="parameter:N", columns=2).properties(title="Rank plots (trankplots)")
    chart_rank
    return (chart_rank,)


# ── Section 4: R-hat Illustration ───────────────────────────────────────────

@app.cell
def _(mo):
    mo.md(r"""
    ## R-hat: Within-chain vs Between-chain Variance

    As chains converge, within-chain variance (W) rises to match the true
    posterior variance, while between-chain variance (B) falls to zero.
    R-hat ≈ √((W + B) / W) → 1.
    """)
    return


@app.cell
def _(alt, fit_wd, np, pd, rhat_over_time):
    chains_a = fit_wd.posterior["a"].values.T  # (draws, chains)
    W_arr, B_arr = rhat_over_time(chains_a)
    _n_show = len(W_arr)
    df_rhat = pd.DataFrame({
        "sample": np.tile(np.arange(1, _n_show + 1), 2),
        "variance": np.concatenate([W_arr, B_arr]),
        "type": ["Within-chain (W)"] * _n_show + ["Between-chain (B)"] * _n_show,
    })
    chart_rhat = alt.Chart(df_rhat).mark_line(strokeWidth=2).encode(
        x=alt.X("sample:Q", title="Number of draws"),
        y=alt.Y("variance:Q", title="Variance"),
        color="type:N",
    ).properties(title="R-hat convergence: W and B over draws", width=500)
    chart_rhat
    return (chart_rhat,)


# ── Section 5: Autocorrelation ──────────────────────────────────────────────

@app.cell
def _(mo):
    mo.md(r"""
    ## Autocorrelation

    Low autocorrelation means each draw is nearly independent, giving
    high effective sample size (ESS). The faster the ACF decays to zero,
    the more efficient the sampler.
    """)
    return


@app.cell
def _(alt, fit_wd, np, pd):
    _chain0_a = fit_wd.posterior["a"].values[0, :]
    _max_lag = 30
    _n_c = len(_chain0_a)
    _mean_c = _chain0_a.mean()
    _var_c = np.var(_chain0_a)
    acf_vals = np.array([np.mean((_chain0_a[:_n_c-k] - _mean_c) * (_chain0_a[k:] - _mean_c)) / _var_c
                         for k in range(_max_lag + 1)])
    df_acf = pd.DataFrame({"lag": np.arange(_max_lag + 1), "ACF": acf_vals})
    chart_acf = alt.Chart(df_acf).mark_bar(width=8).encode(
        x=alt.X("lag:Q", title="Lag"),
        y=alt.Y("ACF:Q"),
    ).properties(title="Autocorrelation of parameter 'a' (chain 1)", width=500, height=200)
    chart_acf
    return (chart_acf,)


# ── Section 6: Bad Chains ───────────────────────────────────────────────────

@app.cell
def _(mo):
    mo.md(r"""
    ## Bad Chains vs Good Chains

    Pathological priors (alpha ~ Normal(0, 1000), sigma ~ Exp(0.0001)) on
    just two data points produce chains that fail to converge. Tighter
    priors (alpha ~ Normal(1, 10), sigma ~ Exp(1)) fix the problem.
    """)
    return


@app.cell
def _(fit_bad_chains, np):
    y_bad = np.array([-1.0, 1.0])
    fit_pathological = fit_bad_chains(y_bad, alpha_prior_sd=1000,
                                      sigma_prior_rate=0.0001, seed=811)
    fit_fixed = fit_bad_chains(y_bad, alpha_prior_sd=10,
                               sigma_prior_rate=1, seed=812)
    return fit_fixed, fit_pathological, y_bad


@app.cell
def _(diagnostics, fit_fixed, fit_pathological, mo):
    _, diag_bad = diagnostics(fit_pathological, ("alpha", "sigma"))
    _, diag_good = diagnostics(fit_fixed, ("alpha", "sigma"))
    mo.md(f"""
    ### Pathological priors
    - R-hat: {diag_bad['max_rhat']:.3f}
    - Min bulk ESS: {diag_bad['min_ess_bulk']:.0f}
    - Divergences: {diag_bad['divergences']}

    ### Reasonable priors
    - R-hat: {diag_good['max_rhat']:.4f}
    - Min bulk ESS: {diag_good['min_ess_bulk']:.0f}
    - Divergences: {diag_good['divergences']}
    """)
    return diag_bad, diag_good


@app.cell
def _(alt, fit_pathological, pd):
    _trace_bad = []
    for _var in ("alpha", "sigma"):
        _vals = fit_pathological.posterior[_var].values
        for _c in range(_vals.shape[0]):
            for _d in range(_vals.shape[1]):
                _trace_bad.append({"parameter": _var, "chain": _c,
                                   "draw": _d, "value": float(_vals[_c, _d])})
    _df_tb = pd.DataFrame(_trace_bad)
    chart_bad = alt.Chart(_df_tb).mark_line(strokeWidth=0.5, opacity=0.6).encode(
        x="draw:Q", y="value:Q", color=alt.Color("chain:N", legend=None),
    ).facet(facet="parameter:N", columns=2).properties(title="Pathological priors — traceplots")
    chart_bad
    return (chart_bad,)


@app.cell
def _(alt, fit_fixed, pd):
    _trace_good = []
    for _var in ("alpha", "sigma"):
        _vals = fit_fixed.posterior[_var].values
        for _c in range(_vals.shape[0]):
            for _d in range(_vals.shape[1]):
                _trace_good.append({"parameter": _var, "chain": _c,
                                    "draw": _d, "value": float(_vals[_c, _d])})
    _df_tg = pd.DataFrame(_trace_good)
    chart_good = alt.Chart(_df_tg).mark_line(strokeWidth=0.5, opacity=0.6).encode(
        x="draw:Q", y="value:Q", color=alt.Color("chain:N", legend=None),
    ).facet(facet="parameter:N", columns=2).properties(title="Reasonable priors — traceplots")
    chart_good
    return (chart_good,)


if __name__ == "__main__":
    app.run()
