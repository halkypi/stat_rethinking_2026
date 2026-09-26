"""Prior and posterior predictive simulation: scripts/02_predictive_simulation.r."""
import marimo

__generated_with = "0.25.0"
app = marimo.App(width="medium")


@app.cell
def _():
    import altair as alt
    import marimo as mo
    import numpy as np
    import pandas as pd
    from scipy import stats
    return alt, mo, np, pd, stats


@app.cell
def _(mo):
    mo.md(r"""
    # From uncertainty about p to predictions

    The R example observes **W L W W W L W L W**: six water and three land
    outcomes. Assume independent tosses with a common probability $p$ of
    water, and a uniform prior $p\sim\mathrm{Beta}(1,1)$.
    Updating gives $p\mid D\sim\mathrm{Beta}(7,4)$.

    To predict water counts in **nine new tosses**, repeat:

    1. Draw one $p$ from the prior or posterior.
    2. Draw $\widetilde W\sim\mathrm{Binomial}(9,p)$ using that same $p$
       for the entire group of nine tosses.
    3. Accumulate the water count; then draw a new $p$ for the next group.

    The left panel describes uncertainty about a parameter. The middle panel
    describes outcomes conditional on one parameter draw. The right panel
    averages over both sources of uncertainty.
    """)
    return


@app.cell
def _(mo):
    mode = mo.ui.dropdown(["Posterior", "Prior"], value="Posterior", label="Predict from")
    sample_count = mo.ui.dropdown([50, 500, 5000, 50000], value=500, label="Simulated groups")
    mo.hstack([mode, sample_count], justify="start")
    return mode, sample_count


@app.cell
def _(np):
    def simulate_predictive(a, b, size=50000, seed=8675):
        rng = np.random.default_rng(seed)
        probabilities = rng.beta(a, b, size=size)
        water_counts = rng.binomial(9, probabilities)
        return probabilities, water_counts
    return (simulate_predictive,)


@app.cell
def _(mode, simulate_predictive):
    a, b = (7, 4) if mode.value == "Posterior" else (1, 1)
    # A fixed pool means increasing the display count extends the same sequence.
    p_draws, water_draws = simulate_predictive(a, b)
    return a, b, p_draws, water_draws


@app.cell
def _(a, b, np, p_draws, pd, sample_count, stats, water_draws):
    n_sim = sample_count.value
    selected_p = float(p_draws[n_sim - 1])
    selected_water = int(water_draws[n_sim - 1])
    support = np.arange(10)
    observed_counts = np.bincount(water_draws[:n_sim], minlength=10)
    exact = stats.betabinom.pmf(support, 9, a, b)
    p_grid = np.linspace(0, 1, 401)
    density_data = pd.DataFrame({"p": p_grid, "Density": stats.beta.pdf(p_grid, a, b)})
    conditional_data = pd.DataFrame({
        "Water": support, "Probability": stats.binom.pmf(support, 9, selected_p),
        "Selected": support == selected_water,
    })
    predictive_data = pd.DataFrame({
        "Water": support, "Simulated frequency": observed_counts / n_sim,
        "Exact probability": exact,
    })
    return conditional_data, density_data, exact, n_sim, observed_counts, predictive_data, selected_p, selected_water, support


@app.cell
def _(a, alt, b, conditional_data, density_data, mode, mo, n_sim, pd, predictive_data, selected_p, selected_water):
    density_chart = (
        alt.Chart(density_data).mark_line(color="#167c80").encode(
            x=alt.X("p:Q", scale=alt.Scale(domain=[0, 1])), y="Density:Q")
        + alt.Chart(pd.DataFrame({"p": [selected_p]})).mark_rule(color="#b34e28").encode(x="p:Q")
    ).properties(width=230, height=220, title=f"1. {mode.value}: Beta({a}, {b})")
    conditional_chart = alt.Chart(conditional_data).mark_bar().encode(
        x=alt.X("Water:O", title="Water in nine tosses"),
        y=alt.Y("Probability:Q", scale=alt.Scale(domain=[0, 1])),
        color=alt.condition(alt.datum.Selected, alt.value("#b34e28"), alt.value("#aebfca")),
        tooltip=["Water:O", alt.Tooltip("Probability:Q", format=".4f")],
    ).properties(width=230, height=220, title=f"2. Binomial(9, {selected_p:.3f})")
    predictive_chart = (
        alt.Chart(predictive_data).mark_bar(color="#167c80", opacity=0.65).encode(
            x=alt.X("Water:O", title="Water in nine new tosses"),
            y=alt.Y("Simulated frequency:Q", title="Probability / frequency", scale=alt.Scale(domain=[0, 0.5])),
            tooltip=["Water:O", alt.Tooltip("Simulated frequency:Q", format=".4f"), alt.Tooltip("Exact probability:Q", format=".4f")])
        + alt.Chart(predictive_data).mark_point(color="#222222", filled=True, size=45).encode(
            x="Water:O", y="Exact probability:Q")
    ).properties(width=230, height=220, title=f"3. {mode.value} predictive")
    three_panel = alt.hconcat(density_chart, conditional_chart, predictive_chart)
    mo.vstack([
        three_panel,
        mo.md(f"Group **{n_sim:,}** draws **p = {selected_p:.3f}**, then **{selected_water} water** outcomes. "
              "Orange marks this group's parameter and outcome. Teal bars are accumulated relative frequencies; "
              "black dots are the exact predictive probabilities. Try increasing the number of groups."),
    ])
    return conditional_chart, density_chart, predictive_chart, three_panel


@app.cell
def _(a, b, exact, mo, np, support):
    predictive_mean = 9 * a / (a + b)
    predictive_variance = 9 * a * b * (a + b + 9) / ((a + b) ** 2 * (a + b + 1))
    plugin_variance = 9 * (a / (a + b)) * (b / (a + b))
    assert np.isclose(exact.sum(), 1)
    assert np.isclose(exact @ support, predictive_mean)
    mo.md(r"""
    ## An exact target for the simulation

    Averaging a binomial likelihood over a Beta distribution yields
    $P(\widetilde W=k)=\binom{9}{k} B(k+a,9-k+b)/B(a,b)$,
    a **beta-binomial** distribution. It is a distribution of future counts,
    not a distribution of $p$.
    """ + f"""
    In this mode, the predictive mean is **{predictive_mean:.3f}** water outcomes,
    and its variance is **{predictive_variance:.3f}**. Fixing p at its mean would
    give variance **{plugin_variance:.3f}**. That shortcut loses parameter
    uncertainty. Drawing a fresh p for each individual toss also changes the model.

    **Try the prior:** Beta(1,1) makes all ten future water counts equally likely
    (0.1 each). It does not give Binomial(9, 0.5): a uniform distribution over p
    is different from fixing p at 0.5.

    **Predictive checking:** six observed water outcomes can be compared with
    replicated groups of nine; agreement in this count alone cannot check the
    independence assumption or ordering of the original outcomes.

    This is direct independent simulation, not MCMC. The seed is 8675, matching
    the R example's seed label, but NumPy and R produce different random streams.
    The default 500 groups match the R loop. Static panels replace animation;
    frequencies and exact probabilities replace raw accumulated counts.
    """)
    return plugin_variance, predictive_mean, predictive_variance


if __name__ == "__main__":
    app.run()
