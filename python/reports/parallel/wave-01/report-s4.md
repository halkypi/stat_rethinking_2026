# Worker Report — Session S4: MCMC Mechanics + ESS/ACF Diagnostics

## Scope Completed

Translated three R/Stan source files into verified Python marimo notebooks covering MCMC mechanics, chain diagnostics, and ESS/ACF analysis. All models are verified.

## Source Files Accounted For

| Source | Disposition |
|---|---|
| `scripts/08_MCMC.r` (612 lines) | Translated: King Markov (lines 1–18), HMC leapfrog mechanics (lines 167–525, animation deferred), WaffleDivorce workflow (lines 529–563), R-hat illustration (lines 567–580), autocorrelation (lines 582–584), bad chains (lines 586–612). Animation sections (lines 22–165, HMC animation loops) deferred. |
| `scripts/08_mHMC.stan` (27 lines) | Absorbed into PyMC WaffleDivorce model in `08_mcmc.py`. Not using CmdStanPy. |
| `scripts/LB03_ess acf example.r` (61 lines) | Translated: Bangladesh hierarchical model (lines 1–19), 1000-dim ESS demonstration (lines 25–58). |

## Artifacts Created

| Artifact | Purpose |
|---|---|
| `python/data/WaffleDivorce.csv` | Vendored dataset (50 US states) from rethinking R package |
| `python/data/WaffleDivorce.provenance.json` | SHA-256 checksum and provenance |
| `python/data/bangladesh.csv` | Vendored dataset (1934 rows) from rethinking R package |
| `python/data/bangladesh.provenance.json` | SHA-256 checksum and provenance |
| `python/src/rethinking_companion/mcmc.py` | Shared helper: data loaders, King Markov sampler, leapfrog integrator, R-hat computation, PyMC model builders |
| `python/notebooks/08_mcmc.py` | Marimo notebook: 6 sections covering all non-animation MCMC content |
| `python/notebooks/lab_ess_acf.py` | Marimo notebook: Bangladesh hierarchical + 1000-dim ESS |
| `python/checks/check_mcmc.py` | Verification script (all checks pass) |
| `python/checks/check_ess_acf.py` | Verification script |
| `python/checks/check_ess_acf_run.py` | Fire-and-forget script saving InferenceData to netCDF |

## Statistical Results

### MCMC Mechanics (fully verified)

- **King Markov**: 200,000 steps, max |empirical − target| = 0.002, chi-squared = 13.39 (9 df). Stationary distribution matches target proportions k/55.
- **HMC leapfrog**: step=0.01, L=12 — all 10 trajectories have |ΔH| < 0.02. Step=0.15, L=15 on correlated target — max |ΔH| = 2.87, demonstrating divergence.
- **WaffleDivorce NUTS**: bA = −0.610, bM = −0.062. R-hat 1.0020, min bulk ESS 4335, min tail ESS 3527, 0 divergences, BFMI 0.885. All diagnostic gates pass.
- **R-hat illustration**: W and B converge over draws; final B << W.
- **Bad chains**: pathological priors (σ ~ Exp(0.0001)) produce R-hat 1.068, 237 divergences, min bulk ESS 69. Reasonable priors produce R-hat 1.0052, 0 divergences, ESS 910. Both as expected.

### ESS/ACF Lab (fully verified via fire-and-forget)

- **Bangladesh hierarchical** (non-centered parameterization, 3027 seconds): R-hat 1.001, min bulk ESS 1310, min tail ESS 1805, 0 divergences, BFMI 0.575. All hyperparameter diagnostic gates pass. Shrinkage: posterior intercept SD 0.338 vs raw district-proportion SD 1.195 — partial pooling verified.
  - The initial centered parameterization failed diagnostics (R-hat 1.022, 2 divergences, BFMI 0.15). Switching to non-centered parameterization (`a = abar + sigma * a_offset`) with target_accept=0.99 and tune=2000 resolved all issues.
- **1000-dim Normal** (8 seconds): median theta bulk ESS = 5683, median theta² bulk ESS = 1890, ratio = 3.0×. ACF at lag 5: theta[0] = −0.033, theta²[0] = 0.045. All checks pass.

## Verification Performed

- `marimo check` passes for both notebooks.
- `check_mcmc.py` passes all 5 verification blocks (King Markov, HMC energy conservation, WaffleDivorce diagnostics, R-hat convergence, bad chains).
- `check_ess_acf_run.py` fire-and-forget: all checks pass (Bangladesh diagnostics, shrinkage, 1000-dim ESS ratio, ACF ordering).

## Dependencies Added

None. All required packages (NumPy, SciPy, PyMC, ArviZ, pandas, Altair, marimo) were already in `pyproject.toml`.

## Shared Infrastructure Changed or Proposed

**Added**: `python/src/rethinking_companion/mcmc.py` with:
- `load_waffle_divorce()` and `load_bangladesh()` data loaders (same checksum/provenance pattern as `load_howell()`)
- `king_markov()` pedagogical Metropolis sampler
- `hmc_leapfrog()`, `hmc_sample()` pedagogical HMC implementations
- `make_2d_target()`, `make_correlated_target()` target distribution factories
- `rhat_over_time()` pedagogical R-hat computation
- `fit_waffle_divorce()`, `fit_bad_chains()`, `fit_bangladesh()`, `fit_1000dim_normal()` model builders

**No existing shared files were modified.**

## Unresolved Issues

1. **WaffleDivorce data overlap with S2**: both workers vendor `WaffleDivorce.csv` independently. The integration orchestrator should deduplicate at merge — the files are identical (same SHA-256 checksum from the same rethinking package source).

2. **Bangladesh fit duration**: 3027 seconds (~50 minutes) for 4 sequential chains with the non-centered parameterization on the compiler-free macOS backend. This is inherent to the model size (126 parameters) and the lack of C compilation. Future sessions with multilevel models will face similar timescales.

## Commit SHAs

| SHA | Description |
|---|---|
| `366732b` | Plan |
| `eee28ec` | Vendor data + shared helper |
| `cbcc559` | MCMC notebook + verification (all pass) |
| `13698dc` | ESS/ACF notebook + check (pre-verification) |
| `b08cd44` | Fire-and-forget script |
| `4463f61` | Non-centered Bangladesh parameterization fix |

## Integration Notes

- `WaffleDivorce.csv` and `WaffleDivorce.provenance.json` will conflict with S2 worker at merge. Both are identical vendored copies — resolve by keeping either.
- No other shared files modified. No `pyproject.toml` or `uv.lock` changes.
- The `mcmc.py` shared helper is new and does not conflict with any existing module.
- The non-centered parameterization for the Bangladesh model is a lesson preview: the MCMC lecture teaches why centered hierarchical models can fail, and Session S8 (GLMM expansion) covers non-centered parameterization in depth. The pedagogical note in the notebook should mention this connection.

## Externally Run Long Computations

### Bangladesh hierarchical model (fire-and-forget)

**Command**: `uv run python checks/check_ess_acf_run.py 2>&1 | tee checks/check_ess_acf_run.log`

**Duration**: 3027 seconds (centered run: 1086 seconds, failed diagnostics; non-centered run: 3027 seconds, all pass).

**Output inspected**:
- `NUTS: [abar, bbar, sigma, tau, a_offset, b_offset]` — confirms non-centered parameters sampled
- `Sampling 4 chains for 2_000 tune and 1_500 draw iterations (8_000 + 6_000 draws total) took 3026 seconds` — no warnings
- R-hat 1.001, min bulk ESS 1310, min tail ESS 1805, 0 divergences, BFMI 0.575
- "All hyperparameter diagnostic gates PASS"
- Shrinkage: posterior SD 0.338 < raw SD 1.195 — "Partial pooling verified — PASS"
- 1000-dim: ratio 3.0×, ACF ordering correct — both PASS
- "Fire-and-forget run complete."

**Artifacts**: `ess_acf_bangladesh.nc`, `ess_acf_1000dim.nc` (regenerable, .gitignored).
