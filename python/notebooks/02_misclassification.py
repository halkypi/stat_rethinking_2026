"""Condition on an imperfect report using the final manual R garden tree."""
import marimo

__generated_with = "0.25.0"
app = marimo.App(width="medium")


@app.cell
def _():
    from fractions import Fraction
    import altair as alt
    import marimo as mo
    import pandas as pd
    return Fraction, alt, mo, pd


@app.cell
def _(mo):
    mo.md(r"""
    # When the observed color can be wrong

    A known bag has **three blue marbles and one white marble**. Draw one
    marble uniformly, but see only an imperfect color report. In the source
    example, a blue marble is reported blue with probability 2/3, and a white
    marble is reported white with probability 2/3.

    **Question:** if the report says blue, what is the probability that the
    marble really is blue? We are learning the **latent color of one draw**,
    not estimating the composition of the bag.

    This follows the final manual tree in `scripts/02_garden_plots_lib.R`:
    four true-state branches, each with three equally likely report branches.
    Keep true states and observations separate; multiply along paths, then
    add paths that lead to the same report.
    """)
    return


@app.cell
def _(mo):
    sensor = mo.ui.dropdown(
        ["2 of 3 correct (source)", "1 of 2 correct (uninformative)", "Always correct"],
        value="2 of 3 correct (source)", label="Report accuracy for either true color")
    report = mo.ui.dropdown(["Blue", "White"], value="Blue", label="Observed report")
    mo.vstack([sensor, report])
    return report, sensor


@app.cell
def _(Fraction):
    def enumerate_reports(blue_count, correct, tickets):
        # Each marble and each report ticket is uniformly selected.
        paths = []
        for marble in range(4):
            truth = int(marble < blue_count)
            for ticket in range(tickets):
                observed = truth if ticket < correct else 1 - truth
                paths.append({"Marble": marble + 1, "Report ticket": ticket + 1,
                              "True color": "Blue" if truth else "White",
                              "Reported color": "Blue" if observed else "White"})
        return paths

    def infer_true_blue(paths, observation):
        compatible = [path for path in paths if path["Reported color"] == observation]
        true_blue = sum(path["True color"] == "Blue" for path in compatible)
        return Fraction(len(compatible), len(paths)), Fraction(true_blue, len(compatible))
    return enumerate_reports, infer_true_blue


@app.cell
def _(Fraction, enumerate_reports, infer_true_blue, pd, report, sensor):
    correct, tickets = {
        "2 of 3 correct (source)": (2, 3),
        "1 of 2 correct (uninformative)": (1, 2),
        "Always correct": (1, 1),
    }[sensor.value]
    accuracy = Fraction(correct, tickets)
    paths = enumerate_reports(3, correct, tickets)
    report_probability, posterior_blue = infer_true_blue(paths, report.value)
    path_table = pd.DataFrame(paths)
    path_table["Compatible with report"] = path_table["Reported color"] == report.value
    joint_table = pd.DataFrame([
        {"True color": truth, "Reported color": observed,
         "Joint probability": sum(p["True color"] == truth and p["Reported color"] == observed for p in paths) / len(paths)}
        for truth in ("Blue", "White") for observed in ("Blue", "White")
    ])
    comparison = pd.DataFrame([
        {"True color": "Blue", "Distribution": "Prior", "Probability": 0.75},
        {"True color": "White", "Distribution": "Prior", "Probability": 0.25},
        {"True color": "Blue", "Distribution": "Posterior", "Probability": float(posterior_blue)},
        {"True color": "White", "Distribution": "Posterior", "Probability": float(1-posterior_blue)},
    ])
    return accuracy, comparison, correct, joint_table, path_table, paths, posterior_blue, report_probability, tickets


@app.cell
def _(alt, joint_table, mo, path_table, paths):
    joint_base = alt.Chart(joint_table).encode(
        x=alt.X("Reported color:N", sort=["Blue", "White"]),
        y=alt.Y("True color:N", sort=["Blue", "White"]),
    )
    joint_chart = (
        joint_base.mark_rect().encode(color=alt.Color("Joint probability:Q", scale=alt.Scale(domain=[0, 1], scheme="blues")))
        + joint_base.mark_text(color="black", fontSize=16).encode(text=alt.Text("Joint probability:Q", format=".3f"))
    ).properties(width=330, height=180, title="Joint probabilities: P(true color, report)")
    mo.vstack([
        mo.md(f"## 1. Keep all paths\nThere are **{len(paths)}** equally likely paths in this setting, each with probability **1/{len(paths)}**. "
              "The four cells below sum to one. To find the probability of a report, sum its column over both true colors."),
        joint_chart,
        mo.ui.table(path_table, selection=None, show_data_types=False, pagination=False),
    ])
    return (joint_chart,)


@app.cell
def _(alt, comparison, mo, posterior_blue, report, report_probability):
    posterior_chart = alt.Chart(comparison).mark_bar().encode(
        x=alt.X("True color:N", axis=alt.Axis(labelAngle=0)), xOffset="Distribution:N",
        y=alt.Y("Probability:Q", scale=alt.Scale(domain=[0, 1])),
        color=alt.Color("Distribution:N", scale=alt.Scale(domain=["Prior", "Posterior"], range=["#aebfca", "#167c80"])),
        tooltip=["True color:N", "Distribution:N", alt.Tooltip("Probability:Q", format=".4f")],
    ).properties(width=500, height=220)
    mo.vstack([
        mo.md(f"""
        ## 2. Condition on the report

        The probability of a **{report.value.lower()}** report is **{report_probability}**
        ({float(report_probability):.4f}). Keep only paths matching that report and
        normalize their probabilities. The posterior probability of true blue is
        **{posterior_blue}** ({float(posterior_blue):.4f}).
        """),
        posterior_chart,
    ])
    return (posterior_chart,)


@app.cell
def _(mo):
    mo.md(r"""
    ## 3. Check the source example by hand

    For source accuracy 2/3, there are **12** paths: six true-blue/report-blue,
    three true-blue/report-white, one true-white/report-blue, and two
    true-white/report-white. Seven paths report blue, so

    $P(\text{true blue}\mid\text{report blue})=
    \frac{(3/4)(2/3)}{(3/4)(2/3)+(1/4)(1/3)}=6/7$.

    The accuracy 2/3 is $P(\text{report blue}\mid\text{true blue})$;
    reversing the conditioning does **not** give the same probability.
    When the report is white, three of five compatible paths still have a
    blue true state, giving **3/5**. Blue marbles started out three times as common.

    **Try it:** switch the reported color. Then compare an uninformative
    reporter with a perfect reporter. At accuracy 1/2, either report leaves
    the prior probability 3/4 unchanged; at accuracy 1, the report identifies
    the true color. These two settings are teaching extensions of the source.

    **Source correspondence:** the final manual R block connects `pts[5-j]`
    to report branches. Its white parent has one blue and two white reports;
    each blue parent has two blue and one white report. The earlier `garden2`
    draft supplies the same report possibilities at every parent and therefore
    does not encode this conditional sensor model. We follow the final manual
    tree, using exact path enumeration rather than reproducing that draft's
    plotting recursion. Joint-probability squares replace radial drawing.
    """)
    return


if __name__ == "__main__":
    app.run()
