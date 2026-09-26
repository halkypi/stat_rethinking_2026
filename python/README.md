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

Environment files such as `pyproject.toml` and `uv.lock` should be added when the first executable lesson establishes the actual dependency set.

## Current state

Project scaffolding established on `project/python-companion`.

The next execution goal is to inventory the Week 2 / Garden of Forking Data scripts and complete the smallest coherent Bayesian-updating lesson as a verified marimo notebook. Avoid beginning with the GIS/animation-heavy globe script.

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