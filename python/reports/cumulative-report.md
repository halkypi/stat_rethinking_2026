# Python Port — Cumulative Report

## Goal

Build a faithful, executable Python companion to Statistical Rethinking 2026, preserving statistical reasoning and teaching order. The first milestone is achieved: one complete beginner lesson is available for Scott to step through.

## Environment

Verified 2026-09-26 on macOS arm64:

- Python 3.13.12 (existing Miniforge interpreter); `.python-version` requests 3.13.
- uv 0.11.7; project-local `.venv`, reproducible dependencies in `uv.lock`.
- NumPy 2.5.3, pandas 3.0.6, Altair 6.3.0, marimo 0.25.0.
- SciPy, PyMC and ArviZ are not installed yet: exact enumeration needs none of them. Add them when a translated lesson needs their statistical operations.
- From `python/`: `uv sync --locked`, then `uv run marimo edit notebooks/02_garden.py`.
- Verification: `uv run marimo check notebooks/02_garden.py`; `uv run python checks/check_garden.py`.
- Export: `mkdir -p outputs`; `uv run marimo export html notebooks/02_garden.py -o outputs/02_garden.html --force`.
- Exported HTML is a snapshot; use the live marimo app for reactive Python controls. Generated outputs and environments are ignored.
- The Codex sandbox required escalation for dependency downloads and marimo's local kernel/server sockets; installation and export succeeded. No global Python packages changed.

## Progress

| Source | Python artifact | Status | Verification |
|---|---|---|---|
| Week 2 / `scripts/02_*` inventory | This report | complete | All four scripts inspected |
| `scripts/02_garden_plots_lib.R`: three four-marble bags, B–W–B | `python/notebooks/02_garden.py` | complete | Full marimo execution, HTML export, all four slider states, exact enumeration and Altair schema checks |
| `scripts/02_garden_plots_lib.R`: six-marble and misclassification examples | — | not-started | Outside first lesson scope |
| `scripts/02_garden_animation.r` | — | deferred | Static path grid preserves first lesson's path-counting concept |
| `scripts/02_predictive_simulation.r` | — | not-started | Selected next chunk |
| `scripts/02_globe_tossing_updating.r` | — | deferred | GIS/animation-heavy; not first chunk |

## Completed Work

### Project setup

- Established the Python companion alongside the untouched upstream material.
- Chose marimo `.py` notebooks for reviewable executable lessons, Markdown for durable state, and Altair for statistical graphics.
- Established the cumulative report as the project spine and descriptive commits as implementation memory.

### Week 2 inventory and first finite-garden lesson

- Source: `scripts/02_garden_plots_lib.R`, especially the three-option comparison with `dat = c(1,0,1)` and bags containing 1, 2, or 3 blue marbles out of 4.
- Artifacts: `python/notebooks/02_garden.py`, `python/checks/check_garden.py`, environment files, generated `python/outputs/02_garden.html` (ignored, reproducible).
- Inventory: the static library contains a self-contained path-counting example; garden animation adds display machinery; globe updating adds GIS; predictive simulation introduces continuous Beta uncertainty and binomial draws. The static three-bag comparison is the smallest coherent Bayesian-updating slice.
- Concept: enumerate equally likely physical paths, discard those incompatible with data, convert counts into likelihoods, multiply by priors, and normalize. Sequential and batch updating agree.
- Assumptions: sampling with replacement, independent draws conditional on bag, equally likely physical marbles, error-free observed colors, only three candidate bags. Equal prior mass is an explicit teaching assumption added to normalize the R garden's counts.
- Important decisions: enumerate marble IDs with `itertools.product`; use NumPy for sequential Bayes and pandas for chart data. Altair shows compatible-path grids, prior/posterior bars, and probabilities across draws. A slider reveals 0–3 observations.
- Exact results: B–W–B counts `[3,8,9]` out of 64 per bag; posterior `[0.15,0.40,0.45]`; next-blue probability 0.575. After B–W, posterior `[0.3,0.4,0.3]`.
- Verification: `marimo check`, direct script execution, `App.run` at every slider state, valid schemas for all three charts, 15 binary sequences of length 0–3 against analytic Bernoulli likelihoods, equal and unequal priors, normalization, order invariance, and executable HTML export. Browser inspection confirmed charts render and moving the slider to 0 reactively restores the prior.
- Differences: rectangular path grids replace radial trees; there is no frame animation or golden-ratio geometry. Normalized posterior and a one-draw posterior predictive average make the implicit counting argument explicit. No simulation or MCMC is needed. R was inspected but not executed; equivalence is checked against the source's branching rules and independent exact probabilities.

## Shared Translation Patterns

- R recursive garden branches → `itertools.product` over physical-marble IDs; compatibility is the conjunction of observed-color matches.
- Path count / total paths → ordered-sequence likelihood; do not confuse it with a binomial count likelihood.
- Sequential Bayes → multiply the prior vector by the next observation's likelihood, then normalize.
- Keep marimo UI construction and cells reading `.value` separate for reactive dependencies.
- Altair consumes tidy pandas tables; explicit [0,1] probability axes permit comparisons. Label finite hypothesis weights as probability, not density.
- `App.run(defs=...)` executes the whole notebook with a substituted control, enabling deterministic verification of every UI state.
- Validate statistical identities independently from plot schemas; browser inspection checks actual rendering.

## Known Issues / Deferred Fidelity

- Remaining sections of the static R library are not claimed complete.
- Exact radial geometry, animation, fonts and slide presentation are deferred.
- The first lesson is finite inference, not a continuous grid approximation.
- Future sampling translations require statistical agreement rather than R-identical random streams.
- GIS/globe graphics and nontrivial `rethinking` model translations remain deferred.
- Live interaction needs a running marimo process; exported HTML does not recompute Python.

## Next Chunk

Translate the statistical core of `scripts/02_predictive_simulation.r` into one marimo lesson: Beta(7,4) posterior after 6 water and 3 land observations, then draw p and simulate water counts in 9 future tosses. It follows the current lesson's predictive average by representing continuous parameter uncertainty and a full predictive distribution. Prerequisites: add SciPy for an exact beta-binomial reference and use seeded NumPy beta/binomial draws. Preserve the three-panel explanation with Altair; defer frame animation. Verify shapes, reproducibility, probability normalization, and simulation agreement with exact beta-binomial probabilities (and the Beta(1,1) prior predictive case).

## Re-entry Instructions

Read this report, inspect Git status and recent commits, inspect the source named under **Next Chunk**, and continue from there. Do not redo completed chunks unless new evidence identifies a defect. Update this report and make descriptive commits after each verified chunk. The repository must remain resumable without previous chat history.
