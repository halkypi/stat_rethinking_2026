# Python Port — Cumulative Report

## Goal

Build a faithful, executable Python companion to Statistical Rethinking 2026, preserving statistical reasoning and teaching order. The first milestone is achieved: one complete beginner lesson is available for Scott to step through.

## Environment

Verified 2026-09-26 on macOS arm64:

- Python 3.13.12 (existing Miniforge interpreter); `.python-version` requests 3.13.
- uv 0.11.7; project-local `.venv`, reproducible dependencies in `uv.lock`.
- NumPy 2.5.3, pandas 3.0.6, Altair 6.3.0, marimo 0.25.0.
- SciPy 1.18.1 now supplies Beta, binomial and beta-binomial operations and independent quadrature. PyMC and ArviZ are not installed: completed lessons use direct simulation and exact inference, not MCMC.
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
| `scripts/02_predictive_simulation.r`: statistical core | `python/notebooks/02_predictive_simulation.py` | complete | Both modes × four sample sizes; 50,000 seeded draws each, independent quadrature, moments, chart schemas, marimo HTML export |
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

### Prior and posterior predictive simulation

- Source: `scripts/02_predictive_simulation.r`; artifacts: `python/notebooks/02_predictive_simulation.py`, `python/checks/check_predictive_simulation.py`, ignored HTML export of the same stem.
- Statistical lesson: draw p from Beta(7,4), then a count from Binomial(9,p); repeat to marginalize parameter uncertainty. The prior mode uses Beta(1,1). Conditional tosses share one p per group.
- Preserve the three-panel explanation: parameter density and selected p, conditional count distribution and selected count, accumulated predictive frequencies. Default 500 groups and seed label 8675 match the R source. A fixed 50,000-draw pool makes displayed prefixes stable when changing sample count.
- Add the exact beta-binomial overlay, predictive moments and a warning about plug-in means losing parameter uncertainty. Prior predictive counts are uniform over 0–9. Posterior predictive mean is 63/11 ≈ 5.7273 and variance ≈ 3.4711, versus plug-in variance ≈ 2.0826.
- Verification: clean marimo check and executable HTML export; whole app at both modes × four sample sizes; support, shapes, reproducibility, stable prefixes, conditional normalization and valid chart schemas. Independently integrate binomial × Beta for every count; compare exact moments and 50,000-draw frequencies using six-standard-error bounds. Maximum absolute frequency errors: posterior 0.00301, prior 0.00212.
- Differences: vectorized NumPy draws replace R's interleaved stream (not bit-identical); relative frequencies replace raw counts; exact reference and prior-mode control are explicit additions. Frame animation and platform-specific output code are deferred. No MCMC diagnostics apply.

## Shared Translation Patterns

- R recursive garden branches → `itertools.product` over physical-marble IDs; compatibility is the conjunction of observed-color matches.
- Path count / total paths → ordered-sequence likelihood; do not confuse it with a binomial count likelihood.
- Sequential Bayes → multiply the prior vector by the next observation's likelihood, then normalize.
- Keep marimo UI construction and cells reading `.value` separate for reactive dependencies.
- Altair consumes tidy pandas tables; explicit [0,1] probability axes permit comparisons. Label finite hypothesis weights as probability, not density.
- `App.run(defs=...)` executes the whole notebook with a substituted control, enabling deterministic verification of every UI state.
- Validate statistical identities independently from plot schemas; browser inspection checks actual rendering.

- R `rbeta` / `rbinom` → a local NumPy `Generator.beta` / `Generator.binomial`; use one parameter draw per replicated group. SciPy distribution functions provide exact reference probabilities.
- Compare Monte Carlo frequencies against sampling-error bounds, and verify exact mixture formulas by independent numerical integration.

## Known Issues / Deferred Fidelity

- Remaining sections of the static R library are not claimed complete.
- Exact radial geometry, animation, fonts and slide presentation are deferred.
- The first lesson is finite inference, not a continuous grid approximation.
- Future sampling translations require statistical agreement rather than R-identical random streams.
- GIS/globe graphics and nontrivial `rethinking` model translations remain deferred.
- Live interaction needs a running marimo process; exported HTML does not recompute Python.

## Next Chunk

Translate the statistical core of `scripts/02_globe_tossing_updating.r`: sequential Beta(1+W,1+L) updating and the final Beta(2,4) 99% percentile-interval example, without GIS or animation. This supplies the parameter-learning step behind the predictive lesson. Reuse the fixed nine-outcome sequence from the predictive source (explicitly replacing random GIS outcomes) and include a Beta(2,4) example. Use SciPy quantiles and seeded draws for the interval, with Altair density/interval plots. Verify every observation prefix against normalized Bernoulli likelihoods, order invariance, exact interval probability and empirical quantile accuracy. Existing dependencies suffice.

## Re-entry Instructions

Read this report, inspect Git status and recent commits, inspect the source named under **Next Chunk**, and continue from there. Do not redo completed chunks unless new evidence identifies a defect. Update this report and make descriptive commits after each verified chunk. The repository must remain resumable without previous chat history.
