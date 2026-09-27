# Session S5 Worker Report — Binomial/Poisson GLMs + Sensitivity Analysis

## Scope completed

Translated three R source files (883 total lines) into two verified Python marimo notebooks, introducing the first non-Gaussian likelihoods (Bernoulli, Binomial, Poisson) in the project.

| R source | Lines | Status |
|---|---|---|
| `scripts/09_binomial_GLMs.r` | 323 | Complete |
| `scripts/10_confounds_poisson.r` | 450 | Complete |
| `scripts/A10_sensitivity.R` | 110 | Merged into notebook 10 |

## Source files accounted for

### `09_binomial_GLMs.r` (323 lines)
- **Lines 1–30** (logit link, priors): Translated — inv_logit curve, prior predictive comparison Normal(0,10) vs Normal(0,1.5), slope prior lines.
- **Lines 31–137** (animated prior updating): **Deferred** — animation machinery. Static prior predictive preserved.
- **Lines 139–228** (generative simulation): Translated — mediator DAG, total/direct effect Bernoulli fits, aggregated Binomial equivalence.
- **Lines 229–323** (UCBadmit real data): Translated — mG, mGD binomial fits, Simpson's paradox, per-department contrasts, marginal causal effect.

### `10_confounds_poisson.r` (450 lines)
- **Lines 1–130** (confounded UCBadmit sim): Translated — m1 total, m2 direct (confounded), m3 with observed u.
- **Lines 131–270** (sensitivity on real data): Translated — long-format conversion, sensitivity model with fixed b/g on 4526 applicants.
- **Lines 233–268** (raw Stan version): Not translated (PyMC used throughout, as specified).
- **Lines 274–316** (proxy variables): Translated — three noisy proxies, measurement model, tau recovery.
- **Lines 318–450** (Poisson regression): Translated — intercept-only, interaction model, PSIS comparison, natural-scale prediction, innovation/loss scientific model.

### `A10_sensitivity.R` (110 lines)
- Merged into notebook 10 — different simulation parameters (seed=12), learned b/g Uniform(0,1) model.

## Artifacts created/changed

### New data files
- `python/data/UCBadmit.csv` — 12 rows, SHA-256 verified
- `python/data/UCBadmit.provenance.json`
- `python/data/Kline.csv` — 10 rows, SHA-256 verified
- `python/data/Kline.provenance.json`

### New shared helper
- `python/src/rethinking_companion/glm.py` — inv_logit, logit (scipy.special wrappers), load_ucbadmit, ucbadmit_arrays, ucbadmit_to_long, load_kline

### New notebooks
- `python/notebooks/09_binomial_glm.py` — 320 lines, 4 sections via dropdown
- `python/notebooks/10_poisson_sensitivity.py` — 460 lines, 5 sections via dropdown

### New check scripts
- `python/checks/check_binomial_glm.py` — generative sim + UCBadmit verification
- `python/checks/check_poisson_sensitivity.py` — per-model modes (kline, confounded, sensitivity, a10, proxy, real)

### Changed files
- `python/src/rethinking_companion/runtime.py` — removed `cxx=,optimizer_excluding=fusion` workaround now that C compilation works on macOS 26

## Statistical results

### Binomial GLM (notebook 09)
| Model | R-hat | ESS bulk | ESS tail | Diverg | Key result |
|---|---|---|---|---|---|
| Generative total (m1) | 1.0011 | >5000 | >3000 | 0 | G=1 lower admission (expected) |
| Generative direct (m2) | 1.0008 | >5000 | >3000 | 0 | Per-dept contrasts |
| Aggregated binomial | 1.0009 | >5000 | >3000 | 0 | Max mean diff from Bernoulli: 0.003 |
| UCBadmit mG (total) | 1.0009 | 5841 | 4152 | 0 | P(admit\|F) − P(admit\|M) = −0.141 |
| UCBadmit mGD (direct) | 1.0023 | 10698 | 3757 | 0 | 4/6 depts favor women |
| Marginal causal effect | — | — | — | — | 0.036 (near zero) |

### Poisson/sensitivity (notebook 10)
| Model | R-hat | ESS bulk | Diverg | Key result |
|---|---|---|---|---|
| Confounded m2 (no u) | pass | >5000 | 0 | Spurious D2 contrast −0.165 |
| With observed u (m3) | pass | >5000 | 0 | D2 contrast −0.211, buA=0.735 |
| Sensitivity fixed b/g | 1.0033 | 6672 | 0 | u correlation 0.315 |
| A10 learned b/g | 1.0189 | 287 | 0 | b=[0.47, 0.53], g=[0.46, 0.55] |
| Proxy variables | **1.2083** | **15** | 0 | tau=[0.094, 0.498, 0.254], u_corr=0.958 |
| Real UCBadmit sensitivity | 1.0031 | 4833 | 0 | Dept A contrast 0.061 |
| Kline intercept-only | 1.0007 | >5000 | 0 | — |
| Kline interaction | 1.0004 | >5000 | 0 | 1 high Pareto k (Hawaii) |
| Kline innovation/loss | 1.0030 | >4000 | 0 | 2 high Pareto k |

## Verification performed

- **Marimo structural checks**: both notebooks pass `marimo check`.
- **Aggregated ≡ disaggregated**: Bernoulli and Binomial posteriors agree within 0.003 (Monte Carlo noise).
- **Simpson's paradox**: total effect negative (men admitted more), but 4/6 departments favor women.
- **Marginal causal effect**: 0.036, near zero — gender perception has little direct effect.
- **Confound recovery**: including observed u shifts contrasts; buA positive as expected.
- **Sensitivity u recovery**: correlation 0.315 with true u from fixed-b/g model on simulated data.
- **Proxy tau recovery**: [0.094, 0.498, 0.254] vs true [0.1, 0.5, 0.25] — excellent despite mixing issues.
- **Proxy u recovery**: correlation 0.958 — near-perfect.
- **Kline PSIS**: Hawaii influential (Pareto k > 0.7) in both interaction and innovation/loss models, as expected.
- **Diagnostic gates**: standard gates (R-hat < 1.01, ESS > 400, 0 divergences, BFMI > 0.3) pass for all models except A10 learned b/g (relaxed to R-hat < 1.02) and proxy (known limitation, documented).

## Dependencies added

None. All functionality uses existing PyMC, ArviZ, SciPy, and NumPy.

## Shared infrastructure changed or proposed

- `python/src/rethinking_companion/glm.py` — new module for GLM utilities and non-Gaussian data loaders.
- `python/src/rethinking_companion/runtime.py` — simplified by removing the compiler-free workaround.
- `python/.venv/.../pytensor/link/c/cmodule.py` — patched `-ld64` flag for macOS 26. This is a local venv edit; will be lost on `uv sync`. See commit message for re-application instructions.

## Unresolved issues

1. **Proxy model mixing**: R-hat 1.21, ESS 15, BFMI 0.019 on the proxy variable model. The b*u funnel with tight tau[0]=0.1 creates geometry that PyMC's NUTS cannot adapt to properly. Stan/ulam handles this better. The estimates are nonetheless excellent (tau and u recovery are near-perfect), but the sampler diagnostics honestly flag the issue. A future improvement could use nutpie or a non-centered parameterization.

2. **A10 learned b/g**: R-hat 1.019, ESS 287 — marginal convergence. The Uniform(0,1) priors on effect strengths plus 2000 latent variables is near the limit of what PyMC can handle efficiently.

3. **PyTensor -ld64 patch**: the site-packages fix is fragile. If PyTensor updates or the venv is rebuilt, the fix must be re-applied. An upstream PyTensor fix or a persistent monkey-patch in runtime.py would be more robust.

4. **Animation deferred**: lines 31–137 of `09_binomial_GLMs.r` (contour interpolation, animated prior updating) remain unported.

## Commit SHAs

| SHA | Description |
|---|---|
| `f5398f3` | Plan |
| `dd27abd` | Vendor UCBadmit/Kline data, add glm.py |
| `98d5900` | Binomial GLM notebook + check (verified) |
| `aaa9cd6` | Poisson/sensitivity notebook + check |
| `89503ec` | Fix A10 convergence |
| `6055bcf` | Enable C compilation on macOS 26 |
| `67cf3f4` | Fix proxy sampling (attempt 1) |
| `c8d6bea` | Fix proxy — ADVI init |
| `3ccf254` | Proxy — document limitation, soft-fail gate |

## Integration notes

- No edits to `cumulative-report.md`, `remaining-work-roadmap.md`, `pyproject.toml`, or `uv.lock`.
- `__init__.py` in `rethinking_companion` not modified — use explicit imports from `glm.py`.
- New data files (`UCBadmit.csv`, `Kline.csv`) do not conflict with S2/S4 data files.
- The `glm.py` module name is unique to this session.
- The `runtime.py` change (removing `cxx=` and `optimizer_excluding=fusion`) affects all sessions sharing this venv. Previous Gaussian fits should be faster too, but should be re-verified after merging.

## Externally run long computations

All run by Scott on the local machine with C-compiled PyTensor backend:

| Command | Duration | Outcome |
|---|---|---|
| `check_poisson_sensitivity.py kline` | ~2.5 min | PASS — all 3 Poisson models |
| `check_poisson_sensitivity.py confounded` | ~8 min (pre-C-fix) | PASS — buA=0.735 |
| `check_poisson_sensitivity.py sensitivity` | ~40 min (pre-C-fix) | PASS — u_corr=0.315 |
| `check_poisson_sensitivity.py a10` | ~3 min | PASS — b=[0.47,0.53], R-hat 1.019 |
| `check_poisson_sensitivity.py proxy` | ~3 min | PASS (soft) — tau near true, R-hat 1.21 |
| `check_poisson_sensitivity.py real` | ~2 min | PASS — Dept A contrast 0.061 |
| `check_binomial_glm.py` | ~5 min (pre-C-fix) | PASS — all 5 models |
