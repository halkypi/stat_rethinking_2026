"""Finite hypotheses and Bayesian updating from the static R garden example."""
import marimo

__generated_with = "0.25.0"
app = marimo.App(width="medium")


@app.cell
def _():
    import itertools
    import altair as alt
    import marimo as mo
    import numpy as np
    import pandas as pd
    return alt, itertools, mo, np, pd


@app.cell
def _(mo):
    mo.md(r"""
    # The garden of forking data

    **Question:** A bag contains four marbles. Does it contain one, two, or
    three blue marbles? We observe **blue, white, blue** (B–W–B).

    This lesson follows the three-bag comparison in
    `scripts/02_garden_plots_lib.R`, where `dat = c(1, 0, 1)`.
    Each draw selects one of four physical marbles with equal probability.
    **Replace the marble and mix the bag after each draw.** Conditional on
    the bag, draws are independent; colors are observed without error.

    Start by giving each of the three bags prior probability 1/3.
    These are the only hypotheses in this example. Counting compatible
    paths will turn this prior into a posterior.
    """)
    return


@app.cell
def _(np):
    blue_counts = np.array([1, 2, 3])
    p_blue = blue_counts / 4
    observations = (1, 0, 1)
    prior = np.full(3, 1 / 3)
    return blue_counts, observations, p_blue, prior


@app.cell
def _(mo):
    step = mo.ui.slider(0, 3, value=3, step=1, label="Number of observed draws", show_value=True)
    step
    return (step,)


@app.cell
def _(blue_counts, itertools, np, observations, p_blue, pd, prior):
    # Enumerate physical-marble paths, just as each R garden forks four ways.
    # IDs 0,...,k-1 are blue in the bag with k blue marbles.
    def count_paths(data):
        return np.array([
            sum(all(int(marble < k) == color for marble, color in zip(path, data))
                for path in itertools.product(range(4), repeat=len(data)))
            for k in blue_counts
        ])

    def update(data, initial):
        weights = np.asarray(initial, dtype=float).copy()
        history = [weights / weights.sum()]
        for color in data:
            weights = history[-1] * (p_blue if color == 1 else 1 - p_blue)
            history.append(weights / weights.sum())
        return np.array(history)

    posterior_history = update(observations, prior)
    history_table = pd.DataFrame([
        {"Draws": n, "Bag": f"{k} blue / 4", "Probability": posterior_history[n, j]}
        for n in range(4) for j, k in enumerate(blue_counts)
    ])
    return count_paths, history_table, posterior_history, update


@app.cell
def _(blue_counts, count_paths, mo, observations, pd, posterior_history, prior, step):
    observed = observations[:step.value]
    counts = count_paths(observed)
    likelihood = counts / (4 ** len(observed))
    comparison = pd.DataFrame({
        "Bag": [f"{k} blue / 4" for k in blue_counts],
        "Compatible paths": counts,
        "All paths per bag": 4 ** len(observed),
        "Likelihood of observed sequence": likelihood,
        "Prior": prior,
        "Posterior": posterior_history[len(observed)],
    })
    mo.vstack([
        mo.md(f"## 1. Count the paths\nObserved so far: **{''.join('B' if x else 'W' for x in observed) or 'no draws'}**. "
              "Each complete physical path is equally likely within a bag. "
              "The likelihood is compatible paths divided by all paths."),
        mo.ui.table(comparison, selection=None, show_data_types=False,
                    format_mapping={"Prior": lambda x: f"{x:.3f}",
                                    "Posterior": lambda x: f"{x:.3f}"}),
    ])
    return comparison, counts, likelihood, observed


@app.cell
def _(alt, blue_counts, itertools, mo, observed, pd):
    # One square per physical path, instead of the R figure's radial branches.
    path_table = pd.DataFrame([
        {"Bag": f"{k} blue / 4", "Column": index % 8, "Row": index // 8,
         "Marble IDs": '-'.join(str(m + 1) for m in path) or 'root',
         "Colors": ''.join('B' if m < k else 'W' for m in path) or 'none',
         "Status": 'Compatible' if all(int(m < k) == c for m, c in zip(path, observed)) else 'Ruled out'}
        for k in blue_counts
        for index, path in enumerate(itertools.product(range(4), repeat=len(observed)))
    ])
    path_chart = alt.Chart(path_table).mark_rect(stroke="white", strokeWidth=2).encode(
        x=alt.X("Column:O", axis=None), y=alt.Y("Row:O", axis=None),
        color=alt.Color("Status:N", scale=alt.Scale(domain=["Compatible", "Ruled out"], range=["#167c80", "#e4e7eb"])),
        tooltip=["Bag:N", "Marble IDs:N", "Colors:N", "Status:N"],
    ).properties(width=185, height=185).facet(column=alt.Column("Bag:N", title=None))
    mo.vstack([mo.md("Each square is one equally likely path through a bag's garden. Hover to inspect its marble IDs and colors."), path_chart])
    return path_chart, path_table


@app.cell
def _(mo):
    mo.md(r"""
    ## 2. Reweight and normalize

    For bag $H$ and observed data $D$,
    $P(H\mid D)=P(D\mid H)P(H)/\sum_h P(D\mid h)P(h)$.

    With B–W–B, compatible path counts are **3, 8, 9**, out of 64
    paths per bag. Under equal priors, divide by 3 + 8 + 9 = 20:
    posterior probabilities are **0.15, 0.40, 0.45**.
    Likelihoods need not sum to one over hypotheses; posterior probabilities do.

    A likelihood here concerns this **ordered sequence**, not all sequences
    containing two blue draws. Using a binomial count would multiply all
    three likelihoods by the same factor of 3, leaving this posterior unchanged.
    """)
    return


@app.cell
def _(alt, comparison, mo):
    probability_table = comparison.melt(id_vars="Bag", value_vars=["Prior", "Posterior"], var_name="Distribution", value_name="Probability")
    probability_chart = alt.Chart(probability_table).mark_bar().encode(
        x=alt.X("Bag:N", axis=alt.Axis(labelAngle=0)),
        xOffset="Distribution:N",
        y=alt.Y("Probability:Q", scale=alt.Scale(domain=[0, 1])),
        color=alt.Color("Distribution:N", scale=alt.Scale(domain=["Prior", "Posterior"], range=["#b8c3cf", "#167c80"])),
        tooltip=["Bag:N", "Distribution:N", alt.Tooltip("Probability:Q", format=".3f")],
    ).properties(width=580, height=250)
    mo.vstack([mo.md("Prior and posterior for the selected number of observations:"), probability_chart])
    return (probability_chart,)


@app.cell
def _(alt, history_table, mo):
    history_chart = alt.Chart(history_table).mark_line(point=True).encode(
        x=alt.X("Draws:Q", axis=alt.Axis(values=[0, 1, 2, 3]), title="Draws observed (0 = prior; then B, W, B)"),
        y=alt.Y("Probability:Q", scale=alt.Scale(domain=[0, 1])),
        color="Bag:N", tooltip=["Draws:Q", "Bag:N", "Probability:Q"],
    ).properties(width=580, height=250)
    mo.vstack([mo.md("## 3. Yesterday's posterior is today's prior\nMultiply by the next draw's probability and normalize again. The full sequence is shown below."), history_chart])
    return (history_chart,)


@app.cell
def _(count_paths, mo, np, observations, p_blue, posterior_history, prior, update):
    # Exact finite enumeration provides an independent check of sequential Bayes.
    assert np.array_equal(count_paths(observations), [3, 8, 9])
    assert np.allclose(posterior_history[-1], [0.15, 0.40, 0.45])
    assert np.allclose(posterior_history.sum(axis=1), 1)
    assert np.allclose(update((1, 1, 0), prior)[-1], posterior_history[-1])
    next_blue = float(posterior_history[-1] @ p_blue)
    mo.md(f"""
    ## 4. Interpret the result

    The three-blue bag is most probable, but its probability is only 45%.
    We have uncertainty about **which bag** generated the data.
    Averaging each bag's chance of blue over the posterior gives a
    **{next_blue:.1%}** chance that the next draw is blue.

    **Try it:** move the slider to 0 and advance one draw at a time.
    Why does observing white reduce support for the three-blue bag?
    Why do the one-blue and three-blue bags tie after B–W?
    Before moving to the final draw, predict which bag it will favor.
    The equal-prior assumption matters: unequal priors would require weighting
    compatible-path counts by each bag's prior before normalization.

    **Verification passed:** path counts, posterior normalization, the exact
    final posterior, and invariance to rearranging these observations.

    **Scope:** this is exact inference over three hypotheses, so no MCMC or
    sampling diagnostics are needed. The original radial layout is replaced
    by a path grid; animation and the later misclassification example are
    deferred. The normalized posterior and next-draw calculation make the
    reasoning implicit in the R garden explicit.
    """)
    return (next_blue,)


if __name__ == "__main__":
    app.run()
