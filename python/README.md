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

The distinct statistical concepts in the supplied Week 2 scripts are complete
as five executable lessons. Suggested learning order:

| Lesson | Concept |
|---|---|
| [Finite garden](notebooks/02_garden.py) | Path counting, likelihood and Bayesian updating |
| [Garden sizes](notebooks/02_garden_sizes.py) | Different path totals can give the same likelihood |
| [Misclassification](notebooks/02_misclassification.py) | True states, imperfect reports and conditioning |
| [Beta updating](notebooks/02_beta_updating.py) | Continuous parameter uncertainty and credible intervals |
| [Predictive simulation](notebooks/02_predictive_simulation.py) | Prior/posterior predictive counts and exact beta-binomial checks |

Animation, GIS and incidental drawing variants are deferred. Week 2 homework
has not been translated. The cumulative report names the next source-backed
chunk: Week 3's symmetric random walk and combinatorial path counts.

## Run the lessons

From the repository root:

```sh
cd python
uv sync --locked
uv run marimo run notebooks
```

The gallery opens the lessons in a reading view. To inspect and edit individual
cells, use `uv run marimo edit notebooks/02_beta_updating.py` (or another lesson).
Controls choose observation prefixes, interval coverage, report accuracy, or
predictive simulation size. Each lesson states its source and assumptions.

## Verify and export

From `python/`:

```sh
uv run marimo check notebooks/02_*.py
uv run python checks/check_week02.py
mkdir -p outputs
uv run marimo export html notebooks/02_predictive_simulation.py -o outputs/02_predictive_simulation.html --force
```

The aggregate check executes all five lessons in isolated processes, tests their
controls, and compares calculations with independent exact probabilities,
numerical integration or sampling-error bounds. Focused `checks/check_*.py`
scripts are also available. Replace the filename in the export command to save
another lesson; generated snapshots are ignored by Git.

HTML exports save rendered outputs; reactive controls require the live app.
Original R files remain unchanged. Detailed fidelity decisions and verification
results are in [the cumulative report](reports/cumulative-report.md).

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