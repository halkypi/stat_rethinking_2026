"""Six-marble garden: compare probabilities when path totals differ."""
import marimo

__generated_with = "0.25.0"
app = marimo.App(width="medium")


@app.cell
def _():
    import itertools
    from fractions import Fraction
    import altair as alt
    import marimo as mo
    import pandas as pd
    return Fraction, alt, itertools, mo, pd


@app.cell
def _(mo):
    mo.md(r"""
    # More paths, same probability

    The next ordinary garden in `scripts/02_garden_plots_lib.R` uses **six
    marbles, three blue**, and the sequence **blue–white–blue**. The comment
    mentions ten, but the executable R values are `n = 6`, `nblue = 3`.

    Compare this with the **four-marble, two-blue** bag from our first lesson.
    Both bags have p(blue) = 1/2. With replacement and equally likely physical
    marbles, should either make the observed color sequence more probable?

    Every physical path is equally likely **within** each garden, but paths
    in the six-marble garden have smaller individual probabilities.
    """)
    return


@app.cell
def _(mo):
    step = mo.ui.slider(0, 3, value=3, step=1, label="B–W–B draws observed", show_value=True)
    step
    return (step,)


@app.cell
def _(Fraction, itertools):
    def garden_probability(total_marbles, blue_marbles, data):
        total_paths = total_marbles ** len(data)
        compatible = sum(
            all(int(m < blue_marbles) == color for m, color in zip(path, data))
            for path in itertools.product(range(total_marbles), repeat=len(data))
        )
        return compatible, total_paths, Fraction(compatible, total_paths)
    return (garden_probability,)


@app.cell
def _(garden_probability, pd, step):
    data = (1, 0, 1)[:step.value]
    results = [garden_probability(n, n // 2, data) for n in (4, 6)]
    comparison = pd.DataFrame([
        {"Bag": f"{n//2} blue / {n} marbles", "Compatible paths": good,
         "All paths": total, "Exact likelihood": str(probability), "Likelihood": float(probability)}
        for n, (good, total, probability) in zip((4, 6), results)
    ])
    return comparison, data, results


@app.cell
def _(alt, comparison, mo):
    likelihood_chart = alt.Chart(comparison).mark_bar(color="#167c80").encode(
        x=alt.X("Bag:N", axis=alt.Axis(labelAngle=0)),
        y=alt.Y("Likelihood:Q", title="Probability of this ordered color sequence", scale=alt.Scale(domain=[0, 1])),
        tooltip=["Bag:N", "Compatible paths:Q", "All paths:Q", "Exact likelihood:N"],
    ).properties(width=550, height=240)
    mo.vstack([mo.ui.table(comparison, selection=None, show_data_types=False), likelihood_chart])
    return (likelihood_chart,)


@app.cell
def _(mo, results):
    assert results[0][2] == results[1][2]
    mo.md(r"""
    With all three draws, the four-marble garden has **8 / 64** compatible
    paths, and the six-marble garden has **27 / 216**. Both equal **1/8**.
    The Bernoulli calculation is $(1/2)(1/2)(1/2)=1/8$.

    **Why this matters for Bayes:** normalizing just 8 and 27 across the two
    bags would incorrectly favor the larger bag. First divide each count by
    its own total; then multiply each likelihood by its prior and normalize.
    Equal prior probabilities remain equal here. These color data cannot
    distinguish the two bags because they imply the same p.

    **Try it:** move from zero to three observations. The path counts change,
    but the likelihoods stay equal. This equivalence relies on replacement;
    removing marbles would change the probabilities and the model.

    The source's radial six-way garden becomes an exact count table and
    probability comparison. We enumerate paths rather than simulate, so
    no random seed or sampling diagnostics are needed.
    """)
    return


if __name__ == "__main__":
    app.run()
