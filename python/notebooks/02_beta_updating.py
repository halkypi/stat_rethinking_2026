"""Statistical core and percentile interval from 02_globe_tossing_updating.r."""
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
    # Learning a continuous water probability

    A finite garden compares a few bags. Now let the unknown water probability
    $p$ take **any value from 0 to 1**. Assume independent Bernoulli outcomes
    conditional on p, an unchanged p across tosses, and correctly recorded
    water/land labels. Start with a uniform Beta(1,1) prior.

    A water outcome multiplies the density by p; a land outcome multiplies it
    by 1−p. Normalize after each observation. After W water and L land outcomes,
    the result is $p\mid D\sim\mathrm{Beta}(1+W,1+L)$.

    This is the updating rule in `scripts/02_globe_tossing_updating.r`.
    We replace the source's ten random GIS-derived outcomes with the fixed
    nine-outcome sequence from the predictive lesson. A second sequence
    produces the source's separate **Beta(2,4)** interval example.
    """)
    return


@app.cell
def _(mo):
    sequence_choice = mo.ui.dropdown(
        ["Six water, three land", "Interval example: one water, three land"],
        value="Six water, three land", label="Observed sequence")
    interval_mass = mo.ui.dropdown([0.5, 0.89, 0.99], value=0.99, label="Posterior interval mass")
    mo.vstack([sequence_choice, interval_mass])
    return interval_mass, sequence_choice


@app.cell
def _(mo, sequence_choice):
    sequence = (1, 0, 1, 1, 1, 0, 1, 0, 1) if sequence_choice.value == "Six water, three land" else (1, 0, 0, 0)
    step = mo.ui.slider(0, len(sequence), value=len(sequence), step=1,
                        label="Outcomes observed", show_value=True)
    step
    return sequence, step


@app.cell
def _(np):
    def posterior_parameters(data):
        a_now, b_now = 1, 1
        history = [(a_now, b_now)]
        for water in data:
            a_now += water
            b_now += 1 - water
            history.append((a_now, b_now))
        return np.array(history)
    return (posterior_parameters,)


@app.cell
def _(np, posterior_parameters, sequence, stats, step):
    n_seen = step.value
    parameter_history = posterior_parameters(sequence)
    a, b = parameter_history[n_seen]
    previous_a, previous_b = parameter_history[max(0, n_seen - 1)]
    draws = np.random.default_rng(2026).beta(a, b, size=10000)
    mean_p = float(a / (a + b))
    water_majority = float(stats.beta.sf(0.5, a, b))
    observed_text = " ".join("W" if x else "L" for x in sequence[:n_seen]) or "none (prior)"
    return a, b, draws, mean_p, n_seen, observed_text, parameter_history, previous_a, previous_b, water_majority


@app.cell
def _(a, b, draws, interval_mass, np, pd, stats):
    mass = interval_mass.value
    tail = (1 - mass) / 2
    exact_interval = stats.beta.ppf([tail, 1 - tail], a, b)
    sample_interval = np.quantile(draws, [tail, 1 - tail])
    interval_table = pd.DataFrame({
        "Method": ["Exact Beta quantiles", "10,000 simulated p values"],
        "Lower": [exact_interval[0], sample_interval[0]],
        "Upper": [exact_interval[1], sample_interval[1]],
    })
    return exact_interval, interval_table, mass, sample_interval, tail


@app.cell
def _(a, alt, b, exact_interval, mo, np, observed_text, pd, previous_a, previous_b, stats):
    grid = np.linspace(0, 1, 501)
    density_data = pd.DataFrame({
        "p": grid, "Current posterior": stats.beta.pdf(grid, a, b),
        "Before latest outcome": stats.beta.pdf(grid, previous_a, previous_b),
    }).melt("p", var_name="Distribution", value_name="Density")
    # Include exact quantile endpoints so the shading covers the intended interval.
    shaded_grid = np.linspace(exact_interval[0], exact_interval[1], 301)
    shaded = pd.DataFrame({"p": shaded_grid, "Density": stats.beta.pdf(shaded_grid, a, b)})
    density_chart = (
        alt.Chart(shaded).mark_area(color="#167c80", opacity=0.2).encode(x="p:Q", y="Density:Q")
        + alt.Chart(density_data).mark_line().encode(
            x=alt.X("p:Q", title="Probability of water, p", scale=alt.Scale(domain=[0, 1])),
            y=alt.Y("Density:Q", title="Probability density"),
            color=alt.Color("Distribution:N", scale=alt.Scale(
                domain=["Current posterior", "Before latest outcome"], range=["#167c80", "#989fa8"]), legend=alt.Legend(orient="bottom")),
            strokeDash=alt.StrokeDash("Distribution:N", legend=alt.Legend(orient="bottom")), tooltip=["p:Q", "Density:Q", "Distribution:N"])
    ).properties(width=550, height=270, title=f"Current distribution: Beta({a}, {b})")
    mo.vstack([mo.md(f"Observed: **{observed_text}**. Compare the density before and after the latest outcome."), density_chart])
    return density_chart, density_data


@app.cell
def _(a, b, interval_table, mass, mean_p, mo, water_majority):
    mo.vstack([
        mo.md(f"""
        ## Areas express uncertainty

        The posterior mean p is **{mean_p:.4f}**. The probability that p exceeds
        one half is **{water_majority:.4f}**. A density's height can exceed 1;
        probabilities are **areas** under the curve.

        The shaded **{mass:.0%} equal-tailed credible interval** leaves
        {(1-mass)/2:.1%} probability in each tail of Beta({a},{b}).
        This is a statement about p under the model and observed data, not
        about the fraction of future tosses that will be water.
        """),
        mo.ui.table(interval_table, selection=None, show_data_types=False,
                    format_mapping={"Lower": lambda x: f"{x:.5f}", "Upper": lambda x: f"{x:.5f}"}),
    ])
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## Connect the calculations

    The R script's final plot samples 10,000 values from Beta(2,4), then calls
    `PI(p, 0.99)`. Here `np.quantile` estimates that central percentile interval;
    SciPy's `beta.ppf` supplies the exact quantiles for comparison. This is
    **not** a highest-density interval. The simulation seed is 2026, so repeated
    execution is reproducible; the R interval snippet did not set a seed.

    **Try it:** start with no observations and advance one outcome at a time.
    Which outcomes move the density toward larger p? Switch to the interval
    example and compare 50%, 89% and 99% intervals. Wider probability coverage
    requires a wider interval. If the same counts arrive in a different order,
    intermediate updates change but the final posterior does not.

    The nine-outcome sequence ends at Beta(7,4), exactly the distribution used
    to generate predictions in `02_predictive_simulation.py`. This lesson is
    conjugate updating, not a numerical grid approximation: the plotting grid
    only draws the density. No GIS, globe projection or animation is needed
    to perform or interpret these calculations.
    """)
    return


if __name__ == "__main__":
    app.run()
