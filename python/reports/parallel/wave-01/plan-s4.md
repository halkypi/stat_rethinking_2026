# Plan — Session S4: MCMC Mechanics + ESS/ACF Diagnostics

## 1. Scope

Translate three R/Stan source files into verified Python marimo notebooks:

1. `scripts/08_MCMC.r` (612 lines) — King Markov, HMC leapfrog, WaffleDivorce NUTS workflow, R-hat illustration, autocorrelation, bad chains
2. `scripts/08_mHMC.stan` (27 lines) — translated to PyMC (not CmdStanPy)
3. `scripts/LB03_ess acf example.r` (61 lines) — Bangladesh hierarchical model diagnostics, 1000-dim ESS demonstration

All animation is deferred. Stan model is absorbed into the PyMC WaffleDivorce fit.

## 2. Artifacts

### New files

| Artifact | Purpose |
|---|---|
| `python/notebooks/08_mcmc.py` | Marimo notebook: King Markov, HMC leapfrog mechanics, WaffleDivorce NUTS workflow, R-hat illustration, autocorrelation, bad chains |
| `python/notebooks/lab_ess_acf.py` | Marimo notebook: Bangladesh hierarchical model, 1000-dim ESS demonstration, ACF plots, ESS scatter comparisons |
| `python/checks/check_mcmc.py` | Verification script for 08_mcmc notebook |
| `python/checks/check_ess_acf.py` | Verification script for lab_ess_acf notebook |
| `python/data/WaffleDivorce.csv` | Vendored dataset (50 US states), SHA-256 checksummed |
| `python/data/WaffleDivorce.provenance.json` | Checksum, attribution, provenance |
| `python/data/bangladesh.csv` | Vendored dataset (~1934 rows), SHA-256 checksummed |
| `python/data/bangladesh.provenance.json` | Checksum, attribution, provenance |
| `python/src/rethinking_companion/mcmc.py` | Shared helper: King Markov sampler, leapfrog integrator, R-hat computation |

### Files not modified

All shared-file restrictions from the prompt are respected: `cumulative-report.md`, `remaining-work-roadmap.md`, `python/README.md`, `pyproject.toml`, `uv.lock`.

### Integration conflict

Worker S2 also vendors `WaffleDivorce.csv`. Both workers vendor independently; the integration orchestrator deduplicates at merge time. Identical checksummed data means no semantic conflict.

## 3. Data Vendoring

### WaffleDivorce

- Source: `rethinking` R package, `data(WaffleDivorce)`.
- Extract from the R package's installed data directory or reconstruct from the well-known published dataset. Key columns: Location, Loc, Population, MedianAgeMarriage, Marriage, Divorce, WaffleHouses, South, plus additional columns. 50 rows (US states).
- Standardize D, M, A in the notebook (not in the CSV).
- SHA-256 checksum recorded in provenance JSON.
- Load function validates checksum, schema, and row count on every import.

### Bangladesh

- Source: `rethinking` R package, `data(bangladesh)`.
- Key columns: district, use.contraception, urban, age.centered, children, woman. ~1934 rows.
- Same checksum/provenance pattern as WaffleDivorce and Howell1.

**Data extraction approach**: Use R to write CSV files from the rethinking package, or obtain the canonical CSV from the rethinking package's GitHub repository. Verify column names and row counts against the R source code.

## 4. Implementation Plan

### 4.1 Shared helper: `python/src/rethinking_companion/mcmc.py`

These are pedagogical implementations showing how MCMC works internally — not replacements for PyMC.

**King Markov sampler** (from lines 1–18 of `08_MCMC.r`):
- 10 islands with populations proportional to 1–10.
- Proposal: current ± 1 with wrap-around (island 1 ↔ island 10).
- Acceptance ratio: min(1, population[proposal] / population[current]).
- Return position history array.
- Parameterize: `n_steps` (default 100,000), `seed`.

**Leapfrog integrator** (from lines 167–525 of `08_MCMC.r`):
- Implement a single HMC step: half-step momentum, L full position+momentum leapfrog steps, half-step momentum.
- Target: 2D Gaussian with `U(q)` = negative log posterior and `grad_U(q)` = gradient.
- Return trajectory (all intermediate positions), final position, initial/final Hamiltonian, accept/reject.
- Translate the R source's `myU2` and `myU_grad2` functions: y ~ Normal(mu, exp(log_sigma)), mu ~ Normal(a, b), log_sigma ~ Normal(k, d).
- Test data: `set.seed(7); y <- abs(rnorm(50)); y <- c(y, -y)` — replicate with NumPy for verification (exact stream not required; mean-zero symmetric data is the key property).

**R-hat computation** (from lines 567–580 of `08_MCMC.r`):
- Given raw chain draws (chains × draws), compute within-chain variance W and between-chain variance B as a function of the number of retained draws.
- Return W and B arrays for plotting convergence.

### 4.2 Notebook: `python/notebooks/08_mcmc.py`

Six sections, each a marimo cell group:

#### Section 1: King Markov (R lines 1–18)

- Call the King Markov sampler from the shared helper.
- Marimo slider for number of steps (e.g. 1000, 10000, 100000).
- Altair bar chart: empirical visit frequency after burn-in vs target proportions (1–10 normalized).
- Altair line chart: chain trace (first 2000 steps).

#### Section 2: HMC Leapfrog Mechanics (R lines 167–525)

Translate the core HMC logic, not the animation.

- Define U and grad_U for the 2D target (mu, log_sigma) with the symmetric test data.
- Run several HMC trajectories from a fixed start point.
- **Static trajectory plot**: Altair scatter + lines showing leapfrog steps overlaid on log-posterior contours. Show accepted (open circle) and rejected (filled circle) proposals.
- **Energy conservation**: table or chart showing H_initial and H_final for each trajectory. Non-divergent trajectories should have |ΔH| small.
- **Step-size sensitivity**: demonstrate that a large step size causes energy errors (divergences). Use the source's step=0.15, L=15 on the correlated `a1+a2` target (myU3/myU_grad3, lines 378–525) to show U-turns and divergent trajectories.
- Contour background: evaluate U on a grid, plot as Altair contour lines or heatmap.

#### Section 3: WaffleDivorce NUTS Workflow (R lines 529–563, Stan model)

- Load and standardize WaffleDivorce data (D, M, A).
- Fit D ~ Normal(a + bM*M + bA*A, sigma) with PyMC four-chain NUTS.
  - Priors: a ~ Normal(0, 0.2), bM ~ Normal(0, 0.5), bA ~ Normal(0, 0.5), sigma ~ Exponential(1).
- Display: traceplot (ArviZ `plot_trace` or manual Altair), rank plot (ArviZ `plot_rank` or manual Altair), posterior summary table.
- Expected results: bA ≈ -0.6, bM ≈ 0 (consistent with the confounds lesson).

#### Section 4: R-hat Illustration (R lines 567–580)

- Extract raw chain draws from the WaffleDivorce fit (warmup excluded, but use the first parameter's draws across 4 chains).
- Compute within-chain variance W(t) and between-chain variance B(t) as functions of t = 1..n_draws.
- Altair line chart: W and B converging as sample size increases.

#### Section 5: Autocorrelation (R lines 582–584)

- Compute ACF of one chain's draws for the first parameter.
- Altair bar chart showing autocorrelation by lag.
- Brief pedagogical note connecting ACF decay rate to ESS.

#### Section 6: Bad Chains (R lines 586–612)

- Fit two models on y = [-1, 1]:
  - **Pathological**: alpha ~ Normal(0, 1000), sigma ~ Exponential(0.0001). Three chains.
  - **Fixed**: alpha ~ Normal(1, 10), sigma ~ Exponential(1). Three chains.
- Display traceplots and rank plots for both.
- Verify: pathological model fails diagnostics (high R-hat or low ESS); fixed model passes.

### 4.3 Notebook: `python/notebooks/lab_ess_acf.py`

Two sections:

#### Section 1: Bangladesh Hierarchical Model (R lines 1–19)

- Load Bangladesh data. Prepare: C = use.contraception, D = district (integer 1–61), U = urban indicator.
- PyMC model:
  ```
  C ~ Bernoulli(logit_p)
  logit_p = a[D] + b[D] * U
  a[1:61] ~ Normal(abar, sigma)
  b[1:61] ~ Normal(bbar, tau)
  abar, bbar ~ Normal(0, 1)
  sigma, tau ~ Exponential(1)
  ```
- Four-chain NUTS. This is ~126 parameters — expect 1–5 minutes.
- Display: summary table, varying intercept caterpillar plot showing partial pooling (shrinkage toward grand mean).
- Diagnostic gates on hyperparameters (abar, bbar, sigma, tau).

**Long-running computation note**: If the Bangladesh fit exceeds ~2 minutes, use the fire-and-forget handoff pattern: prepare the exact command, save diagnostics/samples to disk, and inspect artifacts after completion.

#### Section 2: 1000-Dimensional ESS Demonstration (R lines 25–58)

- PyMC model: theta[1:1000] ~ Normal(0, 1). Compute theta_sq = theta^2 as a derived quantity.
- Four-chain NUTS. 1000 parameters but trivial geometry — should be fast.
- Display:
  - Rank plots for theta[1] and theta_sq[1].
  - ACF plots for theta[1] (fast decay) and theta_sq[1] (slow decay).
  - Scatter: theta bulk ESS vs theta tail ESS (high values).
  - Scatter: theta_sq bulk ESS vs theta_sq tail ESS (lower values).
  - Scatter: theta bulk ESS vs theta_sq bulk ESS (theta >> theta_sq).
  - Scatter: theta tail ESS vs theta_sq tail ESS.
- Key pedagogical point: a well-behaved parameter (theta) can produce a poorly-behaved transformation (theta^2) because squaring creates autocorrelation.

### 4.4 Check scripts

#### `python/checks/check_mcmc.py`

1. **King Markov**: run 200,000 steps, discard first 10,000. Compute empirical frequencies for islands 1–10. Compare to target proportions (k/55 for island k). Use chi-squared goodness-of-fit or verify max |empirical - target| < tolerance.
2. **HMC leapfrog**: run trajectories with small step size. Verify |H_final - H_initial| < threshold for non-divergent trajectories. Run one trajectory with large step size, verify energy error is large.
3. **WaffleDivorce**: diagnostic gates (R-hat < 1.01, ESS > 400, zero divergences, BFMI > 0.3). Verify bA < 0 (median), |bM| small.
4. **Bad chains**: verify pathological model has R-hat > 1.1 or ESS < 100 for at least one parameter; fixed model passes all diagnostic gates.

#### `python/checks/check_ess_acf.py`

1. **Bangladesh**: diagnostic gates on hyperparameters. Verify varying intercepts show shrinkage (SD of posterior means < SD of raw district proportions).
2. **1000-dim ESS**: compute bulk ESS for all theta and theta_sq. Verify median theta bulk ESS > 2× median theta_sq bulk ESS. Verify ACF at lag 5 is smaller for theta[1] than for theta_sq[1].

## 5. Model Specifications Summary

| Model | Parameters | Data | Expected fit time |
|---|---|---|---|
| King Markov | None (pure NumPy) | Synthetic | < 1 s |
| HMC leapfrog | None (pure NumPy) | Synthetic (100 points, mean-zero) | < 1 s |
| WaffleDivorce | a, bM, bA, sigma (4) | 50 states | ~10–30 s |
| Bad chains (pathological) | alpha, sigma (2) | y = [-1, 1] | ~5–15 s |
| Bad chains (fixed) | alpha, sigma (2) | y = [-1, 1] | ~5–15 s |
| Bangladesh hierarchical | 61 intercepts + 61 slopes + 4 hyperparams (126) | ~1934 rows | ~1–5 min |
| 1000-dim Normal | 1000 thetas + 1000 theta_sq derived (1000 sampled) | None (prior-only) | ~30 s – 2 min |

## 6. Validation/Oracle Strategy

### King Markov
- The stationary distribution of the Metropolis chain on the 10-island archipelago must match the target: P(island k) = k/55.
- After discarding burn-in (10,000 steps), empirical frequencies from 200,000 steps should satisfy a chi-squared test or have max absolute error < 0.01.

### HMC Leapfrog
- Energy conservation: for step=0.01, L=12, verify |H_final - H_initial| < 0.1 for all trajectories starting near the mode.
- Divergence demonstration: for step=0.15, L=15 on the correlated target, at least one trajectory should have |ΔH| > 1.

### WaffleDivorce
- Diagnostic gates: R-hat < 1.01, ESS_bulk > 400, ESS_tail > 400, zero divergences, BFMI > 0.3.
- Posterior means: bA ≈ -0.6 (negative, significant), bM ≈ 0 (near zero). These are consistent with the S2 worker's confounds lesson.
- No independent integration oracle for this model (4 parameters with Exponential prior on sigma are not analytically tractable in the same way as the Gaussian models). Rely on diagnostic gates and known R reference values.

### Bad Chains
- Pathological model (flat priors): at least one parameter should have R-hat > 1.1 or bulk ESS < 100.
- Fixed model (reasonable priors): all diagnostic gates pass.

### Bangladesh Hierarchical
- Diagnostic gates on hyperparameters (abar, bbar, sigma, tau).
- Varying intercepts should show partial pooling: the SD of posterior intercept means should be less than the SD of raw district-level contraception proportions.

### 1000-dim ESS
- median(theta bulk ESS) > 2 × median(theta_sq bulk ESS).
- ACF of theta[k] at moderate lags should be smaller than ACF of theta_sq[k].

## 7. Dependencies

No new Python package dependencies. All required packages are already in `pyproject.toml`:
- NumPy / SciPy for manual samplers and ACF computation
- PyMC / ArviZ for NUTS fits and diagnostics
- pandas for data handling
- Altair for charts
- marimo for notebook framework

## 8. Reusable Infrastructure

**From existing code** (no changes needed):
- `runtime.configure_runtime()` — PyTensor configuration
- `gaussian_regression.diagnostics()` / `assert_diagnostics()` — diagnostic extraction and gates
- `height_weight.load_howell()` — data loading pattern (template for new loaders)
- Marimo `App.run(defs=...)` verification pattern from all check scripts

**New shared helper** (`mcmc.py`):
- King Markov sampler — pedagogical, reusable for teaching
- Leapfrog integrator — pedagogical, not a replacement for PyMC's sampler
- R-hat computation — pedagogical manual computation complementing ArviZ

**New data loaders** (in notebook or mcmc.py):
- `load_waffle_divorce()` — same checksum/provenance pattern as `load_howell()`
- `load_bangladesh()` — same pattern

## 9. Anticipated Long-Running Computations

| Computation | Expected time | Strategy |
|---|---|---|
| WaffleDivorce NUTS | 10–30 s | Autonomous |
| Bad chains (2 fits) | 5–15 s each | Autonomous |
| Bangladesh hierarchical | 1–5 min | Autonomous if < 2 min; fire-and-forget handoff if longer |
| 1000-dim Normal | 30 s – 2 min | Autonomous if < 2 min; fire-and-forget if longer |

The fire-and-forget handoff (if needed) will: save InferenceData to netCDF, print diagnostic summary to stdout, and exit. The check script then loads and validates the saved artifact.

## 10. Commit Strategy

Planned coherent commit boundaries:
1. Data vendoring (WaffleDivorce + Bangladesh CSVs, provenance JSONs, load functions)
2. Shared `mcmc.py` helper (King Markov, leapfrog, R-hat)
3. `08_mcmc.py` notebook (King Markov + HMC sections)
4. `08_mcmc.py` notebook (WaffleDivorce + R-hat + ACF + bad chains sections)
5. `check_mcmc.py` verification
6. `lab_ess_acf.py` notebook
7. `check_ess_acf.py` verification
8. Final worker report

Each commit is independently useful and verified at its boundary.
