"""Symmetric random walks and Gaussian sums from 03_gaussian_generative_sim.r."""
import marimo

__generated_with = "0.25.0"
app = marimo.App(width="medium")


@app.cell
def _():
    import math
    import altair as alt
    import marimo as mo
    import numpy as np
    import pandas as pd
    from scipy import stats
    return alt, math, mo, np, pd, stats


@app.cell
def _(mo):
    mo.md(r"""
    # Why sums become bell-shaped

    Put 1,000 independent walkers at zero. Each step independently moves a
    walker left or right by one, with equal probability. Many more paths end
    near the center than far away. A bell-shaped distribution of endpoints
    emerges even though a **single step is not Gaussian**.

    This translates the first block of `scripts/03_gaussian_generative_sim.r`.
    Its 100 animation frames include the starting state, hence **99 moves**.
    The separate combinatorial example uses 50 moves. We keep both and omit
    the animation. Seed 384 is reproducible in NumPy, not identical to R.
    """)
    return


@app.cell
def _(mo):
    steps = mo.ui.dropdown([0, 1, 2, 5, 10, 25, 50, 99], value=99, label="Actual moves")
    steps
    return (steps,)


@app.cell
def _(math, np, stats):
    def simulate_walks(seed=384):
        increments = np.random.default_rng(seed).choice([-1, 1], size=(1000, 99))
        return np.column_stack([np.zeros(1000, dtype=int), increments.cumsum(axis=1)])

    def endpoint_distribution(n):
        k = np.arange(n + 1)
        positions = 2*k - n
        exact = np.array([math.comb(n, int(j)) / 2**n for j in k])
        if n == 0:
            normal = np.ones(1)
        else:
            # Each allowed lattice point is two units apart. Compare probability
            # masses with normal areas over [x-1, x+1], not density heights.
            normal = stats.norm.cdf((positions+1)/np.sqrt(n)) - stats.norm.cdf((positions-1)/np.sqrt(n))
        return positions, exact, normal

    walks = simulate_walks()
    return endpoint_distribution, simulate_walks, walks


@app.cell
def _(endpoint_distribution, np, pd, steps, walks):
    n = steps.value
    endpoints = walks[:, n]
    support, exact, normal = endpoint_distribution(n)
    empirical = np.array([(endpoints == x).mean() for x in support])
    distribution = pd.DataFrame({"Position": support, "Simulation": empirical,
                                  "Exact binomial": exact, "Normal approximation": normal})
    trajectories = pd.DataFrame([
        {"Move": t, "Position": int(walks[j,t]), "Walker": str(j+1)}
        for j in range(8) for t in range(n+1)
    ])
    return distribution, empirical, endpoints, exact, n, normal, support, trajectories


@app.cell
def _(alt, distribution, mo, n, trajectories):
    base = alt.Chart(distribution).encode(x=alt.X("Position:Q", title="Endpoint after selected moves"))
    endpoint_chart = (
        base.mark_bar(color="#167c80", opacity=0.5, size=5).encode(y=alt.Y("Simulation:Q", title="Probability / relative frequency"))
        + alt.Chart(distribution.melt("Position", value_vars=["Exact binomial", "Normal approximation"],
                                      var_name="Distribution", value_name="Probability")).mark_line(point=True).encode(
            x="Position:Q", y="Probability:Q", color=alt.Color("Distribution:N", legend=alt.Legend(orient="bottom")),
            tooltip=["Position:Q", "Distribution:N", alt.Tooltip("Probability:Q", format=".4f")])
    ).properties(width=550, height=240)
    path_chart = alt.Chart(trajectories).mark_line(point=n < 3).encode(
        x="Move:Q", y="Position:Q", color=alt.Color("Walker:N", legend=None), detail="Walker:N",
    ).properties(width=550, height=180, title="Eight of the 1,000 walkers")
    mo.vstack([path_chart, endpoint_chart])
    return endpoint_chart, path_chart


@app.cell
def _(endpoints, exact, mo, n, normal, np):
    assert np.isclose(exact.sum(), 1)
    mo.md(r"""
    ## Count paths, then approximate

    If K moves are to the right, $X_n=2K-n$ and
    $K\sim\mathrm{Binomial}(n,1/2)$. Thus
    $P(X_n=2k-n)=\binom{n}{k}/2^n$. All $2^n$ paths are equally likely,
    but their endpoints are not. In particular, endpoint parity must match n.

    Independence makes the mean of the sum zero and its variance n.
    The central limit theorem motivates $X_n\approx\mathrm{Normal}(0,\sqrt n)$,
    where the second argument is the **standard deviation**.
    """ + f"""
    At **{n} moves**, the simulated mean is **{endpoints.mean():.3f}**
    (target 0), and variance is **{endpoints.var():.3f}** (target {n}).

    Teal bars show simulated frequencies. The exact line is obtained by
    counting paths. The normal line uses areas over width-two bins around
    allowed endpoints, so it is comparable to discrete probability masses.
    The normal approximation assigns **{max(0., 1-normal.sum()):.5f}** probability
    outside those bins; we do not silently renormalize it. At zero moves the
    distribution is a point mass, not a normal with a positive scale.

    **Try it:** compare 1, 5, 50 and 99 moves. More steps make the normal shape
    a better approximation. More walkers would reduce Monte Carlo noise,
    but would not improve a poor normal approximation for too few steps.
    This generative argument is not evidence that every real outcome is Gaussian.
    """)
    return


if __name__ == "__main__":
    app.run()
