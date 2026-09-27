# Wave 01 Worker — Session S5: Binomial/Poisson GLMs + Sensitivity Analysis

You are a worker in a parallel wave. Your scope is **Session S5** from `python/reports/remaining-work-roadmap.md`.

- **Branch**: `agent/cortex-s5`
- **Worktree**: `../statrethinking-s5`
- **Plan path**: `python/reports/parallel/wave-01/plan-s5.md`
- **Final report path**: `python/reports/parallel/wave-01/report-s5.md`

## Scope

Translate three R source files into verified Python marimo notebooks. This session introduces the **first non-Gaussian likelihoods** (binomial and Poisson) in the project.

1. **Binomial GLMs and Simpson's paradox** from `scripts/09_binomial_GLMs.r` (323 lines)
2. **Poisson GLMs, latent confounders, and sensitivity** from `scripts/10_confounds_poisson.r` (450 lines)
3. **Sensitivity analysis extension** from `scripts/A10_sensitivity.R` (110 lines)

## R source files to inspect

### `scripts/09_binomial_GLMs.r` (323 lines) — Major sections:

1. **Logit link and priors** (lines 1–30): Demonstrate `inv_logit`, prior predictive simulation for logistic models. Show that Normal(0,10) on the logit scale implies extreme probabilities; Normal(0,1.5) is more reasonable.

2. **Animated prior updating** (lines 31–137): Logistic regression with sequential data, contour plots of posterior, animated curves. **Animation deferred.** But the static prior predictive lines and contour concept should be preserved.

3. **UCBadmit generative model** (lines 139–228): Simulate mediator scenario (G → D → A with G → A). Fit total effect (A ~ bernoulli(logit(a[G]))) and direct effect (A ~ bernoulli(logit(a[G,D]))). Gender contrasts on logit and probability scales. Aggregate to binomial format and show equivalence.

4. **UCBadmit real data** (lines 229–323): `data(UCBadmit)`. Total effect model mG and direct effect model mGD (binomial likelihood). Traceplots, trankplots. Per-department gender contrasts on probability scale. **Marginal causal effect**: simulate counterfactual (all perceived as women vs all perceived as men), weighted by department application volumes. This is the key causal inference result.

### `scripts/10_confounds_poisson.r` (450 lines) — Major sections:

1. **UCBadmit with confounders** (lines 1–130): Simulated UCBadmit with latent ability `u`. Three models: without u (confounded), with observed u, and sensitivity model with latent u (declared as `vector[N]:u ~ normal(0,1)` with fixed effect strengths `b` and `g`). Shows confound recovery.

2. **Sensitivity on real UCBadmit** (lines 131–270): Convert UCBadmit to long (logistic) format. Fit total, direct, and sensitivity models on real data. Extract latent u estimates per applicant. Raw Stan version as alternative implementation (use PyMC, not Stan).

3. **Proxy variables** (lines 274–316): Three noisy proxies of latent u. Measurement model T_k ~ Normal(u, tau_k). Joint model recovers u and deconfounds the gender contrast.

4. **Poisson regression** (lines 318–450): Kline tools data. Log-Normal and Normal priors for Poisson GLMs. Intercept-only model and interaction model (tools ~ Poisson with log link, a[C] + b[C]*P). PSIS comparison. Innovation/loss scientific model: lambda = exp(a[C]) * P^b[C] / g. Natural-scale and standardized-scale prediction plots.

### `scripts/A10_sensitivity.R` (110 lines):
- Extended UCBadmit sensitivity with different simulation parameters (seed 12, different acceptance rates). Two sensitivity models: one with fixed b/g vectors, one with b/g as learned Uniform(0,1) parameters. This extends the content from `10_confounds_poisson.r` — merge into the same lesson rather than creating a separate notebook.

## Existing Python artifacts to reuse

- `python/src/rethinking_companion/runtime.py` — PyTensor configuration
- `python/src/rethinking_companion/gaussian_regression.py` — diagnostic gates, fitting patterns
- `python/src/rethinking_companion/height_weight.py` — data loading pattern with checksum
- `python/src/rethinking_companion/categorical.py` — index-variable model pattern
- `python/notebooks/04_categorical_weight.py` — reference for indexed parameter models
- `python/checks/` — reference for check script patterns

## Expected artifacts

### Notebooks
- `python/notebooks/09_binomial_glm.py` — logit link, prior predictive, UCBadmit generative + real data, Simpson's paradox, marginal causal effects
- `python/notebooks/10_poisson_sensitivity.py` — latent confounders, sensitivity analysis, proxy variables, Poisson regression on Kline tools, innovation/loss model. Merges content from both `10_confounds_poisson.r` and `A10_sensitivity.R`.

### Check scripts
- `python/checks/check_binomial_glm.py`
- `python/checks/check_poisson_sensitivity.py`

### Data
- `python/data/UCBadmit.csv` — vendored with SHA-256 checksum, attribution, provenance. 12 rows (6 departments × 2 genders), columns: dept, applicant.gender, admit, reject, applications.
- `python/data/Kline.csv` — vendored with SHA-256 checksum, attribution, provenance. 10 rows (Oceanic societies), columns: culture, population, contact, total_tools, mean_TU.

### Shared helpers
- `python/src/rethinking_companion/glm.py` — `inv_logit` (expit) function, logit function, possibly a generalized link-function fitting helper. Use `scipy.special.expit` / `scipy.special.logit` as the underlying implementation.

## Pedagogical scope

### Binomial GLM lesson (`09_binomial_glm.py`)

- **Logit link**: show `inv_logit` curve, explain logit scale. Prior predictive simulation showing reasonable vs extreme priors for intercepts and slopes on the logit scale.
- **Generative simulation**: simulate the mediator DAG (G → D → A with direct G → A). Fit total effect and direct effect models. Show contrasts on both logit and probability scales.
- **Aggregated vs disaggregated**: demonstrate that binomial(N,p) with aggregated counts gives the same posterior as bernoulli with individual rows.
- **UCBadmit real data**: fit mG (total effect) and mGD (direct effect with department). Traceplots, rank plots. Per-department gender contrasts on probability scale. Show Simpson's paradox: total effect favors men, but within-department effects are mixed.
- **Marginal causal effect**: the most important pedagogical result. Simulate counterfactual predictions: all applicants perceived as women vs all as men, weighted by actual department application volumes. This gives the direct causal effect of gender perception on admission probability.
- **Animation deferred** throughout.

### Poisson/sensitivity lesson (`10_poisson_sensitivity.py`)

- **Confounded UCBadmit simulation**: simulate with latent ability u. Demonstrate that the direct-effect model (conditioning on department) is confounded when ability affects both department choice and admission. Show that including u (if observed) recovers the true effect.
- **Sensitivity analysis**: declare u as a latent Normal(0,1) variable with fixed or learned effect strengths. Show partial recovery of the true gender effect even without observing u. Apply to both simulated and real UCBadmit data. Merge the extended sensitivity from `A10_sensitivity.R` (learned b/g parameters).
- **Proxy variables**: three noisy measurements of latent u. Joint model with measurement model T_k ~ Normal(u, tau_k). Show that proxies partially identify the latent variable and improve the gender contrast estimate.
- **Poisson regression**: Kline tools data. Log link, log-Normal priors. Intercept-only and interaction models (a[C] + b[C]*P). PSIS model comparison via ArviZ. Prediction curves on both standardized and natural population scales.
- **Innovation/loss model**: scientific non-linear model lambda = exp(a[C]) * P^b[C] / g. Show that this scientifically motivated model fits better than the log-linear model.

## Validation and oracle strategy

### Binomial GLM
- **Generative simulation**: verify that the true causal effect is recovered by the total-effect model and that the direct-effect model correctly stratifies by department.
- **UCBadmit real data**: diagnostic gates on all fits. Verify Simpson's paradox pattern: total P(admit|female) < P(admit|male), but within most departments female admission rate ≥ male.
- **Marginal causal effect**: verify that the marginal direct effect is small and centered near zero (gender perception has little direct effect once department is accounted for).
- **Aggregated vs disaggregated equivalence**: posterior means and covariances should agree within Monte Carlo error.

### Poisson/sensitivity
- **Confounded simulation**: verify that the naive direct-effect model shows spurious gender differences, and that including u (observed or latent) moves the contrast toward the true value.
- **Sensitivity with learned b/g**: verify that the model explores reasonable effect sizes and provides wider but more honest uncertainty.
- **Proxy model**: verify that tau estimates are close to the generating noise levels (0.1, 0.5, 0.25).
- **Kline tools**: diagnostic gates. PSIS comparison should show the interaction model has some high Pareto k values (influential observations, especially Hawaii). The innovation/loss model should have better PSIS diagnostics.
- **All models**: diagnostic gates (R-hat < 1.01, ESS > 400, zero divergences, BFMI > 0.3).

## Data and dependency needs

- **UCBadmit data**: from the `rethinking` R package. 12 rows. Also need `UCBadmit_long.csv` or generate the long format programmatically (the source shows the transformation).
- **Kline tools data**: from the `rethinking` R package (`data(Kline)`). 10 rows. Columns: culture, population, contact, total_tools, mean_TU.
- **No new Python package dependencies expected.** PyMC handles binomial and Poisson likelihoods natively. `scipy.special.expit` for inv_logit.

## Shared-file restrictions

Do **not** edit these files:
- `python/reports/cumulative-report.md`
- `python/reports/remaining-work-roadmap.md`
- `python/README.md`
- `pyproject.toml` / `uv.lock` (unless a new dependency is absolutely required — flag prominently)

## Long-running computation expectations

- Binomial fits (UCBadmit, 12 rows or ~4500 long-format rows): fast, < 30 seconds each.
- Poisson fits (Kline, 10 rows): very fast.
- **Sensitivity models with latent u**: N=2000 simulated individuals, each with a latent u parameter = 2000+ parameters. These will likely take 2–10 minutes. Prepare fire-and-forget handoffs for:
  - Simulated sensitivity model (m3s in the source, ~2000 latent parameters)
  - Real UCBadmit sensitivity model (mGDu, ~4500 latent parameters)
  - Proxy variable model (m4, ~2000 latent u + measurement model)
- **A10 sensitivity extension**: additional sensitivity models, also with latent u vectors. Similar timing.

For each long computation, commit the code first, provide the exact shell command, and STOP.

## Two-phase protocol

### Phase 1 — Plan only

1. Orient from repository evidence: read this prompt, the cumulative report, recent Git history, and all R source files listed above.
2. Inspect existing Python artifacts for patterns to reuse.
3. Produce an implementation plan covering:
   - exact artifacts to create/change
   - data vendoring approach for UCBadmit and Kline
   - model specifications for each fit (especially the first non-Gaussian likelihoods)
   - how to handle long-format conversion for UCBadmit
   - sensitivity model approach (latent u in PyMC)
   - how to merge A10_sensitivity.R content
   - validation/oracle strategy
   - anticipated long-running computations (sensitivity models with latent u) and fire-and-forget handoff plan
   - dependency or shared-infrastructure needs (inv_logit helper, GLM patterns)
   - likely integration conflicts
4. Write the plan to `python/reports/parallel/wave-01/plan-s5.md`.
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
8. Write and commit your final worker report to `python/reports/parallel/wave-01/report-s5.md`.
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
