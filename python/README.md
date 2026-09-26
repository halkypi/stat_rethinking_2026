# Statistical Rethinking 2026 — Python Companion

Status: active

## Problem

The upstream 2026 course is taught with R/rethinking examples. The goal is to make the course directly usable while learning modern Python Bayesian workflow, without replacing or modifying McElreath's original material.

## Desired outcome

Build an executable Python companion, in course order, that preserves the statistical ideas and important visualizations while using idiomatic Python.

The first milestone is deliberately concrete: **complete at least one beginner lesson that Scott can step through end-to-end.**

## Approach

- Preserve `scripts/` and `homework/` as upstream reference material.
- Use marimo `.py` notebooks for executable lessons; Markdown for project state and reports.
- Prefer Python 3.13 where dependencies permit and `uv` for environment management.
- Core stack: NumPy, pandas, SciPy, PyMC, ArviZ, **Altair**, and marimo.
- Translate statistical operations and pedagogy, not R syntax mechanically.
- Work in small verified chunks.
- Treat `reports/cumulative-report.md` as the project spine.
- Put detailed implementation rationale and context in frequent, descriptive Git commits.

## Project layout

```text
python/
  README.md
  notebooks/
  prompts/
    001-python-port.md
  reports/
    cumulative-report.md
```

The Python 3.13 environment is defined by `pyproject.toml` and `uv.lock`. Only dependencies used by completed lessons are installed.

## Current state

The first Garden of Forking Data lesson is complete: [02_garden.py](notebooks/02_garden.py).
It teaches exact Bayesian updating for three candidate bags with an observation slider,
compatible-path grids, prior/posterior bars, and sequential updating. The [predictive simulation lesson](notebooks/02_predictive_simulation.py) adds prior and
posterior predictive counts, seeded simulation and an exact beta-binomial comparison.
The [Beta-updating lesson](notebooks/02_beta_updating.py) connects observations to
continuous posterior densities and credible intervals. The [six-marble comparison](notebooks/02_garden_sizes.py) explains normalization
when path totals differ. The misclassification example remains to be translated; the cumulative report identifies the next chunk.

## Run the lesson

From the repository root:

```sh
cd python
uv sync --locked
uv run marimo edit notebooks/02_garden.py
```

Use `marimo run` instead of `marimo edit` for a reading view. Set the slider to 0
and advance through blue, white, blue. The final bag probabilities are 15%, 40%, 45%.

## Verify and export

From `python/`:

```sh
uv run marimo check notebooks/02_garden.py
uv run python checks/check_garden.py
mkdir -p outputs
uv run marimo export html notebooks/02_garden.py -o outputs/02_garden.html --force
```

The HTML export is a saved snapshot; reactive controls require the live app.
Checks execute all four observation states and compare path enumeration with
independent analytical probabilities. Original R files are unchanged.

## Definition of done for a lesson

A lesson is complete when:

1. its source R material and statistical purpose are identified;
2. the Python translation is pedagogically faithful and idiomatic;
3. the marimo notebook executes successfully;
4. key numerical/statistical behavior is verified;
5. important visualizations use Altair where appropriate;
6. meaningful differences from R are documented; and
7. the cumulative report identifies exactly one next chunk.

## Re-entry

Start with `reports/cumulative-report.md`. It is the canonical handoff across Codex sessions. Read recent commits for implementation detail and rationale.