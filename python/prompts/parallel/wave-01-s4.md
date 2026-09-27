# Wave 01 Worker — Session S4: MCMC Mechanics + ESS/ACF Diagnostics

You are a worker in a parallel wave. Your scope is **Session S4** from `python/reports/remaining-work-roadmap.md`.

- **Branch**: `agent/cortex-s4`
- **Worktree**: `../statrethinking-s4`
- **Plan path**: `python/reports/parallel/wave-01/plan-s4.md`
- **Final report path**: `python/reports/parallel/wave-01/report-s4.md`

## Scope

Translate three R/Stan source files into verified Python marimo notebooks:

1. **MCMC mechanics and diagnostics** from `scripts/08_MCMC.r` (612 lines)
2. **Minimal Stan regression** from `scripts/08_mHMC.stan` (27 lines)
3. **ESS and autocorrelation diagnostics lab** from `scripts/LB03_ess acf example.r` (61 lines)

## R source files to inspect

### `scripts/08_MCMC.r` (612 lines) — Major sections:

1. **King Markov** (lines 1–18): Metropolis algorithm on a discrete 10-island archipelago. 100,000 steps, proposal = current ± 1 with wrap-around, acceptance ratio = proposal/current population. Shows that stationary distribution matches island populations.

2. **Animation** (lines 22–165): Animated visualization of King Markov, circle layouts, arrow heads. **Defer all animation.**

3. **HMC mechanics** (lines 167–525): Manual HMC implementation. Leapfrog integrator on a 2D Gaussian target. Demonstrates momentum, trajectory, energy conservation, U-turns, and divergences. Includes step-size sensitivity and divergent trajectory examples. Animation portions are **deferrable**, but the leapfrog integrator and trajectory logic are core statistical content.

4. **Workflow examples** (lines 529–563): WaffleDivorce data — `quap` vs `ulam` comparison, traceplot, trankplot, R-hat illustration, autocorrelation. Uses `08_mHMC.stan` for a direct Stan fit of D ~ Normal(a + bM*M + bA*A, sigma).

5. **R-hat illustration** (lines 567–580): Manual computation of within-chain and between-chain variance across samples, showing convergence.

6. **Bad chains** (lines 586–612): Two models with poor priors (flat/vague) showing pathological chains, then fixed with tighter priors. Traceplot and trankplot comparison.

### `scripts/08_mHMC.stan` (27 lines)
- Stan model for D ~ Normal(a + bM*M + bA*A, sigma) on WaffleDivorce data.
- Priors: a ~ Normal(0,0.2), bM ~ Normal(0,0.5), bA ~ Normal(0,0.5), sigma ~ Exponential(1).

### `scripts/LB03_ess acf example.r` (61 lines)
- **Bangladesh hierarchical model** (lines 1–19): `ulam` fit of contraception ~ bernoulli with logit link, 61 varying intercepts and 61 varying slopes by district, adaptive hyperpriors (abar, bbar, sigma, tau).
- **1000-dim ESS demonstration** (lines 25–58): 1000-dimensional Normal(0,1) with saved theta^2 transformed quantities. Shows that theta has high ESS but theta^2 has low ESS. ACF plots, bulk vs tail ESS scatter, and theta ESS vs theta^2 ESS comparisons.

## Existing Python artifacts to reuse

- `python/src/rethinking_companion/runtime.py` — PyTensor configuration
- `python/src/rethinking_companion/gaussian_regression.py` — diagnostic gates, fitting patterns
- `python/src/rethinking_companion/height_weight.py` — data loading pattern with checksum
- `python/notebooks/03_gaussian_regression.py` — reference for NUTS fitting notebook pattern
- `python/checks/` — reference for check script patterns

## Expected artifacts

### Notebooks
- `python/notebooks/08_mcmc.py` — King Markov, HMC leapfrog mechanics, WaffleDivorce NUTS workflow, R-hat illustration, bad chains diagnostic comparison
- `python/notebooks/lab_ess_acf.py` — Bangladesh hierarchical model diagnostics, 1000-dim ESS demonstration, ACF plots, ESS scatter comparisons

### Check scripts
- `python/checks/check_mcmc.py`
- `python/checks/check_ess_acf.py`

### Data
- `python/data/WaffleDivorce.csv` — vendored with SHA-256 checksum, attribution, provenance (50 US states)
- `python/data/bangladesh.csv` — vendored with SHA-256 checksum, attribution, provenance

### Shared helpers (if needed)
- `python/src/rethinking_companion/mcmc.py` — King Markov sampler, leapfrog integrator, R-hat computation (these are pedagogical implementations, not replacements for PyMC)

## Pedagogical scope

### MCMC mechanics lesson (`08_mcmc.py`)

- **King Markov**: implement the discrete Metropolis sampler. 10 islands with populations 1–10. Show that stationary distribution (after burn-in) matches the target. Marimo control for number of steps.
- **HMC leapfrog**: implement a manual leapfrog integrator on a 2D Gaussian target (the source's `U` and `grad_U` functions). Show momentum proposals, energy conservation along trajectories, and the effect of step size on divergences. Static Altair trajectory plots replace animation.
- **WaffleDivorce workflow**: vendor the data, standardize D/M/A, fit the multiple regression D ~ Normal(a + bM*M + bA*A, sigma) with four-chain NUTS. Show traceplots, rank plots (trankplots), posterior summaries. The Stan model (`08_mHMC.stan`) is translated to PyMC — do not use CmdStanPy.
- **R-hat illustration**: compute within-chain and between-chain variance as a function of sample size, showing convergence. Use the WaffleDivorce fit's raw chain draws.
- **Autocorrelation**: show ACF of chain draws, explain ESS relationship.
- **Bad chains**: fit two models with pathological priors (alpha ~ Normal(0,1000), sigma ~ Exp(0.0001)) and then with reasonable priors (alpha ~ Normal(1,10), sigma ~ Exp(1)) on y = c(-1, 1). Show traceplot/trankplot comparison demonstrating diagnostic failure and success.
- **Animation is deferred** throughout.

### ESS/ACF diagnostics lab (`lab_ess_acf.py`)

- **Bangladesh hierarchical model**: fit the contraception model with 61 varying intercepts and 61 varying slopes. This is a hierarchical/multilevel model — use PyMC's standard varying-effects pattern. The pedagogical focus is on diagnosing ESS and ACF from this complex model, not on teaching multilevel model construction.
- **1000-dim ESS**: fit theta[1:1000] ~ Normal(0,1) with theta_sq = theta^2 as a derived quantity. Show that theta has high bulk/tail ESS but theta_sq has much lower ESS (because squaring creates autocorrelation in the transformed parameter). ACF plots, bulk vs tail ESS scatter, theta ESS vs theta^2 ESS comparisons.

## Validation and oracle strategy

### MCMC lesson
- **King Markov**: verify that the empirical frequency distribution (after burn-in) approximates the target proportional to island populations. Use a chi-squared or KL-divergence check.
- **HMC leapfrog**: verify energy conservation (H_initial ≈ H_final) for non-divergent trajectories. Verify that divergent trajectories have large energy errors.
- **WaffleDivorce**: diagnostic gates (R-hat < 1.01, ESS > 400, zero divergences, BFMI > 0.3). The posterior should show bA ≈ -0.6, bM ≈ 0, consistent with the confounds lesson (S2 worker).
- **Bad chains**: verify that the pathological model fails diagnostics (high R-hat, low ESS) and the fixed model passes.

### ESS lab
- **Bangladesh**: diagnostic gates. Verify varying intercepts show partial pooling (shrinkage toward grand mean).
- **1000-dim ESS**: verify theta bulk ESS >> theta_sq bulk ESS. Verify ACF decays faster for theta than for theta_sq.

## Data and dependency needs

- **WaffleDivorce data**: vendor from the `rethinking` R package. Key columns: Location, Loc, Population, MedianAgeMarriage, Marriage, Divorce, WaffleHouses, South. 50 rows.
- **Bangladesh data**: vendor from the `rethinking` R package (`data(bangladesh)`). Key columns: district, use.contraception, urban, age.centered, children, woman. ~1934 rows.
- **No new Python package dependencies expected.** NumPy/SciPy for manual samplers; PyMC/ArviZ for NUTS fits and diagnostics.

**Note**: Worker S2 (splines + confounds) also vendors WaffleDivorce data. Both workers vendor independently; the integration orchestrator deduplicates at merge time.

## Shared-file restrictions

Do **not** edit these files:
- `python/reports/cumulative-report.md`
- `python/reports/remaining-work-roadmap.md`
- `python/README.md`
- `pyproject.toml` / `uv.lock` (unless a new dependency is absolutely required — flag prominently)

## Long-running computation expectations

- King Markov and manual HMC: pure NumPy, very fast (< 1 second).
- WaffleDivorce NUTS fit: ~10–30 seconds (small data, 4 parameters).
- Bad chains models: fast (2 data points).
- **Bangladesh hierarchical model**: 61 varying intercepts + 61 varying slopes + 4 hyperparameters = 126+ parameters. This will likely take 1–5 minutes on the compiler-free backend. If it exceeds ~2 minutes, prepare a fire-and-forget handoff.
- **1000-dim Normal**: 1000 parameters. Very simple model but high-dimensional. Likely fast (Normal is easy to sample) but monitor.

## Two-phase protocol

### Phase 1 — Plan only

1. Orient from repository evidence: read this prompt, the cumulative report, recent Git history, and all R/Stan source files listed above.
2. Inspect existing Python artifacts for patterns to reuse.
3. Produce an implementation plan covering:
   - exact artifacts to create/change
   - data vendoring approach for WaffleDivorce and Bangladesh
   - manual sampler implementation approach (King Markov, leapfrog)
   - model specifications for each fit
   - validation/oracle strategy
   - anticipated long-running computations (Bangladesh hierarchical, 1000-dim)
   - dependency or shared-infrastructure needs
   - likely integration conflicts (WaffleDivorce data overlap with S2)
4. Write the plan to `python/reports/parallel/wave-01/plan-s4.md`.
5. Commit the plan.
6. **STOP and wait for Scott.**

Do not implement during Phase 1.

### Phase 2 — Implementation (after Scott approves)

1. Implement only the approved scope.
2. Preserve upstream R/Stan files.
3. Follow existing marimo/PyMC/ArviZ/Altair/uv conventions.
4. Preserve current statistical verification standards.
5. Make frequent coherent commits.
6. Avoid unnecessary edits to shared state.
7. Use the fire-and-forget handoff for materially long computations.
8. Write and commit your final worker report to `python/reports/parallel/wave-01/report-s4.md`.
9. **STOP.**

### Final report must contain

- Scope completed
- Source files accounted for
- Artifacts created/changed
- Statistical results
- Verification performed
- Dependencies added
- Shared infrastructure changed or proposed
- Unresolved issues
- Commit SHAs
- Integration notes
- Any externally run long computations, their commands, outputs, and evidence inspected
