# Python Port — Cumulative Report

## Goal

Build a faithful, executable Python companion to Statistical Rethinking 2026, preserving statistical reasoning and teaching order. The first milestone is achieved. Five executable lessons now cover the distinct statistical concepts in the supplied Week 2 scripts; GIS, animation and incidental drawing variants remain deferred. Week 2 homework has not been ported.

## Environment

Verified 2026-09-26 on macOS arm64:

- Python 3.13.12 (existing Miniforge interpreter); `.python-version` requests 3.13.
- uv 0.11.7; project-local `.venv`, reproducible dependencies in `uv.lock`.
- NumPy 2.5.3, pandas 3.0.6, Altair 6.3.0, marimo 0.25.0.
- SciPy 1.18.1 now supplies Beta, binomial and beta-binomial operations and independent quadrature. PyMC 5.28.5, ArviZ 0.23.4 and PyTensor 2.38.2 now support fitting. The dependency ranges retain the verified PyMC 5 / ArviZ InferenceData API; major-version migration is a separate change.
- From `python/`: `uv sync --locked`; `uv run marimo run notebooks` opens the lesson gallery. Use `uv run marimo edit notebooks/<lesson>.py` to step through code.
- Verify all Week 2 lessons: `uv run marimo check notebooks/02_*.py`; `uv run python checks/check_week02.py`. Individual `check_*.py` files provide focused re-entry checks.
- Export: `mkdir -p outputs`; `uv run marimo export html notebooks/02_garden.py -o outputs/02_garden.html --force`.
- Final Week 2 checkpoint: all five lesson checks and all marimo structural checks pass; `uv sync --locked --offline` succeeds. All five HTML exports exist locally. Browser inspection confirmed predictive panels and Beta density rendering; changing the misclassification report to white updates the posterior to 3/5. Upstream `scripts/`, `homework/`, root README and LICENSE have no changes.
- Exported HTML is a snapshot; use the live marimo app for reactive Python controls. Generated outputs and environments are ignored.
- The Codex sandbox required escalation for dependency downloads and marimo's local kernel/server sockets; installation and export succeeded. No global Python packages changed.

- The companion is now an editable package under `python/src/rethinking_companion`; run `uv sync --locked` after checkout. Plotting and PyTensor caches use ignored `python/.cache`. On this macOS toolchain native PyTensor linking fails with `ld: library d64 not found`; `runtime.py` defaults to supported `cxx=,optimizer_excluding=fusion` execution on macOS (explicit user PYTENSOR_FLAGS override this). Excluding fusion avoids slow Python scalar loops in the compiler-free backend; four-chain fits take roughly 5–30 seconds here. All previously verified Gaussian fits were rerun after this optimizer change and retained their diagnostic results. No compiler/system settings were changed.
- ArviZ 0.23.4 writes an import-warning timestamp under the macOS user cache; sandboxed model checks/export required escalation for this library behavior. Its import cache location is not configurable by the project.

## Session workflow and credit conservation

- Scott explicitly requested more frequent commits at the 2026-09-26 pause. Commit each independently useful, verified increment as soon as it is ready: for example, a tested runtime fix or reusable inference helper can precede the completed lesson. Do not wait for a whole lesson or session when a coherent verified boundary already exists. Describe verification and remaining scope accurately; never label an unfinished lesson complete.
- Some elapsed time in the last session was model fitting and fresh-fit HTML export; some was diagnosing the macOS backend and independently checking results. The compiler-free fusion issue made a synthetic fit take 163 seconds; excluding fusion reduced it to about 27 seconds. The runtime change justified rerunning earlier Gaussian checks, which passed. Ordinary future checks should not repeat successful fits unless relevant code, configuration, data, or unresolved evidence changes.
- For future long computations, a proposed user-run handoff is documented in the README: prepare exact commands that save logs, samples and diagnostic summaries, end the agent turn, then inspect those artifacts when Scott reports completion. Scott asked about this option; the suggested two-minute threshold has not been adopted as a mandatory pause rule. Short runs can remain autonomous under the existing authorization. Preserve full sampling and independent verification either way.
- Local Python computation does not call an OpenAI model. Do not infer credit consumption from wall-clock duration or promise a quantified saving from manual monitoring; no per-operation credit breakdown was available. Reduce unnecessary polling, verbose outputs and repeated reads while retaining statistical checks.
- Pause checkpoint: all statistical implementation is committed through `b746c75`; Week 4 has not been started. No additional model runs were needed for this documentation-only handoff.
- Cortex session on `agent/cortex-python-companion`: completed the full remaining-work roadmap (`python/reports/remaining-work-roadmap.md`) inventorying all 51 source files, then implemented Session S1 — categorical predictors (W\~S, W\~S+H, full SCM) and simulation-based validation. Three model fits on Howell1 adults, one independent integration oracle, 20-replication coverage check, two new marimo notebooks, two check scripts, and a shared `categorical.py` helper.

## Progress

| Source | Python artifact | Status | Verification |
|---|---|---|---|
| Week 2 / `scripts/02_*` inventory | This report | complete | All four scripts inspected |
| `scripts/02_garden_plots_lib.R`: three four-marble bags, B–W–B | `python/notebooks/02_garden.py` | complete | Full marimo execution, HTML export, all four slider states, exact enumeration and Altair schema checks |
| `scripts/02_garden_plots_lib.R`: six-marble example | `python/notebooks/02_garden_sizes.py` | complete | Four controls, 180 exact rational checks, marimo HTML export |
| `scripts/02_garden_plots_lib.R`: final manual misclassification example | `python/notebooks/02_misclassification.py` | complete | Six control states, 18 rational Bayes cases, literal R parent mapping, marimo export |
| `scripts/02_garden_plots_lib.R`: earlier `garden2` drawing draft | — | deferred | Final manual conditional-observation tree is the canonical statistical source |
| `scripts/02_garden_animation.r`: frame animation | — | deferred | Its path-counting concept is covered by the garden lessons and exhaustive binary-sequence checks |
| `scripts/02_predictive_simulation.r`: statistical core | `python/notebooks/02_predictive_simulation.py` | complete | Both modes × four sample sizes; 50,000 seeded draws each, independent quadrature, moments, chart schemas, marimo HTML export |
| `scripts/02_globe_tossing_updating.r`: Beta updating and percentile interval | `python/notebooks/02_beta_updating.py` | complete | Every prefix, likelihood quadrature, three interval levels, reproducible quantiles, marimo HTML export |
| `scripts/02_globe_tossing_updating.r`: GIS and animation | — | deferred | Statistical core is complete without presentation machinery |

| `scripts/03_gaussian_generative_sim.r`: symmetric walk and path counts | `python/notebooks/03_gaussian_sums.py` | complete | All 100 step counts, eight controls, exact enumeration, seeded moments, marimo export |
| `scripts/03_gaussian_generative_sim.r`: growth-model block | — | deferred | Vector-valued growth-factor recycling needs separate interpretation; not assumed equivalent to independent identical increments |

| `scripts/03_prior_pred_OLS.r`: linear prior and updating model | `python/notebooks/03_gaussian_regression.py` and shared Gaussian helper | complete | Four-chain NUTS against exact posterior, 2D quadrature, sequential updates, predictive checks, notebook states and export |

| `scripts/03_prior_pred_OLS.r`: quadratic/cubic mean functions | Existing `03_gaussian_regression.py` | complete | Both NUTS fits, exact covariance/predictions, source outlier edit, prefix controls, default export |

| `scripts/03_howell_new_weight_model.r`: synthetic validation and first adult weight fit | `python/notebooks/03_height_weight.py` | complete | Refined/expanded independent integration, both full fits, diagnostic/support/predictive checks, notebook charts and export |
| `scripts/03_howell_plots.r`: prior-line illustration | Existing prior-function lessons | deferred | Mechanism already represented; reversed response/predictor direction is not claimed to be the same fitted model |
| `scripts/03_ptolemaic_model.R` | — | deferred | Geocentric/heliocentric presentation animation; no fitted statistical model |

| `scripts/04_height_weight_sex_categorical.r`: W\~S indexed group means | `python/notebooks/04_categorical_weight.py` and shared `categorical.py` | complete | Four-chain NUTS, independent numerical integration oracle for (a[1],a[2],sigma), posterior mean contrast M−F, individual prediction contrast, P(male heavier), diagnostic gates |
| `scripts/04_height_weight_sex_categorical.r`: W\~S+H sex-varying slopes | Existing `04_categorical_weight.py` | complete | Four-chain NUTS with LogNormal positive slopes, diagnostic gates, positive slope support |
| `scripts/04_height_weight_sex_categorical.r`: Full SCM (joint H+W model) | Existing `04_categorical_weight.py` | complete | Joint five-parameter model, do(S) causal contrast via simulated intervention, total effect > direct effect verified |
| `scripts/LA04_sim heights validate example.r`: simulation-based validation | `python/notebooks/04_sim_validate.py` | complete | Single 4-chain recovery with 89% CI covering b=0.5; 20-replication coverage check (85%, within sampling error of 89%); notebook with 10-replication UI |

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

### Continuous Beta updating and percentile intervals

- Source: statistical update loop and final interval example in `scripts/02_globe_tossing_updating.r`; artifacts: `python/notebooks/02_beta_updating.py`, `python/checks/check_beta_updating.py`, ignored HTML export.
- Lesson: each water/land observation increments the corresponding Beta shape parameter; compare the previous and current density, then interpret posterior means, tail areas and equal-tailed credible intervals.
- Choices: fixed W L W W W L W L W data connect to the predictive lesson; W L L L reproduces the source's separate Beta(2,4) interval distribution. The R source's ten random GIS-derived outcomes are deliberately replaced, not claimed reproduced. NumPy simulates 10,000 p values with seed 2026; SciPy quantiles provide an exact comparison to the R `PI` operation.
- Verification: every prefix of both sequences (15 states) agrees with independently integrated/normalized Bernoulli likelihoods. Three interval masses (50%, 89%, 99%) integrate to their stated probability, widen monotonically, and default controls execute. Seeded draws reproduce; empirical quantiles satisfy six-standard-error bounds on their exact CDF values. Order invariance, posterior tail areas, Altair schema, clean marimo check and executable HTML export pass.
- Exact 99% intervals: Beta(7,4) [0.26488601, 0.92323183]; Beta(2,4) [0.02288122, 0.81490273]. These are central percentile intervals, not highest-density intervals.
- Keep the Beta plot at 550px with its legend below the plot so the complete [0,1] axis and distribution labels fit the app pane; the exported lesson and aggregate checks were rerun after this adjustment.
- Differences: omit GIS/projection/spinning globe and interpolation frames; include exact quantiles and explicit density-versus-probability explanations. The plotting grid is not an inference approximation. R was not executed; independent likelihood integration verifies its statistical rule.

### Six-marble garden and unequal path totals

- Source: `scripts/02_garden_plots_lib.R`, `n <- 6`, `nblue <- 3` block. Artifacts: `python/notebooks/02_garden_sizes.py`, `python/checks/check_garden_sizes.py`, ignored HTML export.
- Lesson: more compatible physical paths need not mean greater likelihood. Three blue out of six gives 27/216 for B–W–B; two blue out of four gives 8/64. Both are 1/8 under replacement, so these color observations cannot distinguish the bags.
- Translate the six-way radial diagram to an exact count/fraction table and Altair likelihood comparison. The comparison with a four-marble bag makes the normalization lesson explicit; the source's stale comment mentioning ten is superseded by its executable value six.
- Verification: every slider state executes; all 180 combinations of bag sizes 4/6, possible blue counts, and binary sequences of length 0–3 agree with independent rational Bernoulli likelihoods, including zero/one probability boundaries. Altair schema, marimo check and executable HTML export pass. No simulation or dependencies added.
- Difference: static probability comparison replaces radial geometry; it explicitly explains that cross-hypothesis raw-count normalization only works when per-path probability scales are equal.

### Misclassification: latent states and observed reports

- Source: final manual tree after `# try doing it manually` in `scripts/02_garden_plots_lib.R`. Artifacts: `python/notebooks/02_misclassification.py`, `python/checks/check_misclassification.py`, ignored HTML export.
- Statistical lesson: distinguish the known bag composition, latent true color of one draw, and observed report; sum joint path probabilities over latent states, then condition on the report. Both true colors are reported correctly with probability 2/3.
- Source mapping: parents 1–3 are blue and parent 4 white. R's reversed `pts[5-j]` connects j=1's white parent to two white/one blue reports; j>1 blue parents get two blue/one white reports. The twelve equally likely leaves contain joint counts BB=6, BW=3, WB=1, WW=2.
- Exact results: P(report blue)=7/12; P(true blue | report blue)=6/7; P(true blue | report white)=3/5. Conditioning reverses the question, so reporter accuracy is not the posterior probability of true color.
- Translation: exact `Fraction` enumeration, an Altair joint-probability heatmap, a complete path table and prior/posterior bars. A report control and two explicitly labeled teaching extensions (uninformative/perfect reporting) show when data leave the prior unchanged or identify truth exactly.
- Verification: six UI states, normalized joints, chart schemas, 18 base-rate/sensor/report cases against independent rational Bayes calculations, and a literal reconstruction of the R parent-index/report mapping. Clean marimo check and executable HTML export pass. The aggregate `checks/check_week02.py` runs all five lessons' checks in isolated processes.
- Differences: replace radial graphics with joint probabilities; do not reuse the earlier `garden2` draft, which uses parent-independent second-ring possibilities and does not represent this sensor model. This distinction is resolved by following the explicit final manual code; no upstream changes are made.

### Week 3: Gaussian sums from discrete paths

- Source: first football-field block and 50-toss combinatorial example in `scripts/03_gaussian_generative_sim.r`. Artifacts: `03_gaussian_sums.py`, `checks/check_gaussian_sums.py`, reproducible HTML export.
- Concept: many independent ±1 increments produce binomial endpoint masses and approximately Gaussian sums. Keep 1,000 walkers, seed label 384, and the source's 100-frame/99-move distinction; include zero and 50 moves.
- Use NumPy cumulative sums and exact `math.comb(n,k)/2**n`; Altair shows eight trajectories plus simulated, exact and normal-approximate endpoint probabilities. Normal probabilities integrate width-two bins, respecting lattice spacing; do not compare density heights directly to mass or hide out-of-support mass by renormalizing.
- Verified all 100 counts for parity/support, exact normalization/symmetry/mean/variance, independent SciPy binomial agreement, seeded reproducibility and six-standard-error simulation bounds. Independently enumerate every path through eight moves. Eight UI choices and both chart schemas pass; marimo check and full export succeed.
- Difference: no animated field, no R-identical random stream; normal comparison is an explanatory addition. Growth block is deliberately separate because its `runif(..., 1+gf)` recycles 100 bounds across 1,000 individuals.

### First verified PyMC / ArviZ regression pattern

- Source: linear prior/updating blocks of `scripts/03_prior_pred_OLS.r`; artifacts: `03_gaussian_regression.py`, `checks/check_gaussian_regression.py`, reusable `src/rethinking_companion/gaussian_regression.py` and `runtime.py`, locked dependencies; ignored `outputs/03_linear_fit.nc`, diagnostic JSON and HTML export.
- Model: independent a,b ~ Normal(0,1); y ~ Normal(a+b*x,1). The source overwrites its intended n=10 demo with n=0; explicitly activate ten synthetic observations with NumPy seed 2971, clipped Normal x, true slope 0.7 and generating noise 0.5. Fitted sigma stays 1. The changed execution scope and random stream are stated in the lesson.
- Fit: four independent NUTS chains, 1,000 tuning + 1,500 retained draws per chain, target_accept 0.9, cores=1, seed 731. Labels identify coefficients, observations and predictions. Prior simulation uses 1,000 draws. No fit cache silently replaces execution.
- Independent checks: solve the conjugate Gaussian posterior and also integrate prior × likelihood on a 301×301 parameter grid. Sequential rank-one updates match batch solutions at every data prefix. NUTS means and full covariance agree within six Monte Carlo standard errors; prior draws/noise, posterior predictive shapes, and new-data means/quantiles/noise pass. Predictions reproduce each draw's design-matrix multiplication exactly, verifying coefficient conditioning rather than accidental resampling.
- Diagnostics: max rank R-hat 1.001329; min bulk ESS 5707.6; min tail ESS 4021.3; zero divergences; min BFMI 1.092; maximum tree depth 3. Thresholds are R-hat <1.01, both ESS >400, no divergences, BFMI >0.3, depth <10. Clean marimo check, five displayed prefix states, chart schemas and a separate full notebook export (fresh fit) pass.
- Pedagogy: prior coefficient draws imply whole functions; distinguish central 89% uncertainty about the mean from prediction intervals for observations. The slider uses exact prefix updates while MCMC verifies the full-data fit once per execution. Here quap is exact because the posterior is Gaussian; NUTS establishes a reusable pattern for non-Gaussian models.

### Polynomial means in the canonical Gaussian regression lesson

- Source: quadratic/cubic blocks of `scripts/03_prior_pred_OLS.r`; extend `03_gaussian_regression.py` and its shared helper rather than create duplicate lessons. Add `checks/check_polynomial_regression.py`.
- Preserve Normal(0,1) coefficients and fitted noise SD 1. Quadratic generator is 0.7x−x² with noise 0.5, seed label 12 and the deliberately replaced ninth observation x=3,y=−1. Cubic generator is 0.7x−2x²+3x³ with noise 0.5 and seed label 13. Realized NumPy data differ from R.
- Explain linearity in coefficients, covariance-aware uncertainty and extrapolation. Choosing a scenario fits four chains; prefix controls use exact updates. Prior mean-function plots, uncertainty bands and coefficient summaries work for arbitrary included powers. The scenarios are separate illustrative datasets, not a model-selection comparison.
- Verification: both full four-chain fits pass the original exact-posterior mean/covariance, predictive-noise and quantile checks; explicit power-by-power predictions equal joint matrix predictions. UI states 0/8/9/10, chart schemas and marimo export pass. Predictive quantile tolerances now use quantile-specific ESS rather than a fixed tolerance, preserving Monte Carlo error awareness in correlated fits.
- Quadratic diagnostics: R-hat 1.000464, min bulk ESS 3040.8, tail ESS 3316.8, zero divergences, min BFMI 1.075, max depth 4. Cubic: R-hat 1.002193, bulk ESS 2324.1, tail ESS 2947.8, zero divergences, BFMI 1.026, depth 5. Saved fits/JSON reports are ignored, reproducible outputs.

### Centered positive-slope regression with unknown residual scale

- Source: `scripts/03_howell_new_weight_model.r`, initial validation and first adult model through its interval plots, before animation. Artifacts: `03_height_weight.py`, `checks/check_height_weight.py`, shared `height_weight.py`, checksummed `data/Howell1.csv` with attribution, GPL-3 license copy and immutable provenance.
- Preserve a ~ Normal(60,10), b ~ LogNormal(0,1), sigma ~ Uniform(0,10), W ~ Normal(a+b*(H−Hbar),sigma). Adult filter age≥18 gives 352 of 544 rows, Hbar=154.5970926 cm. Keep that training center for all predictions. The notebook displays actual fitted priors, residuals and a replicated-weight-SD check; positive slope does not imply positive Normal outcomes or establish causation.
- Synthetic validation: 100 heights Uniform(130,170), generating a=70,b=.5,sigma=5, local seed 604 (source unseeded). Full posterior means/covariance match independent integration and the realized 99% intervals include all three truths; this is one recovery test, not SBC.
- Independent oracle: integrate the Normal intercept analytically conditional on b,sigma using centered sufficient statistics, then integrate b and sigma on a fine trapezoid grid. Double resolution and expand the b bound from 3 to 6; means agree within 1e-5, covariances within rtol=1e-4/atol=1e-6, boundary mass <1e-10. Compare NUTS means and full covariance with Monte Carlo error bounds; check positive slope, sigma support, training/new-input dimensions, retained centering, standardized prior/posterior predictive noise and notebook charts.
- Adult integrated posterior means (SD): a=44.99822 (0.22700) kg; b=0.628689 (0.029354) kg/cm; sigma=4.256974 (0.161651) kg. NUTS diagnostics: R-hat 1.001052, min bulk ESS 5573.5, tail ESS 4487.5, zero divergences, min BFMI 1.0233, max depth 4. Synthetic diagnostics: R-hat 1.001476, bulk ESS 4653.3, tail ESS 3198.8, zero divergences, BFMI 1.0573, depth 3.
- Full notebook export reruns the adult fit successfully. Its source-matched intervals are 99% equal-tailed mean uncertainty and 89% individual prediction. Forecasts to 190 cm are labeled extrapolation.
- Runtime verification found compiler-free elementwise fusion was unnecessarily slow (163 seconds for a synthetic fit). Excluding this supported optimizer pass reduced full fits to about 27 seconds; all linear/quadratic/cubic exact-oracle checks were repeated successfully. Short performance benchmarks were not treated as accepted inference.
- Differences/deferred scope: NUTS replaces quap. Original R data files are untouched; official rethinking data are vendored only under python/. The source's repeated-fit point-estimate experiment is not presented as calibration and is deferred as a repeated validation demonstration. Adult animation, grouped models and all-age polynomial/log models remain separate/deferred work.

### Week 4: Categorical predictors, causal contrasts and simulation validation

- Source: `scripts/04_height_weight_sex_categorical.r` (all three blocks) and `scripts/LA04_sim heights validate example.r`. Artifacts: `python/notebooks/04_categorical_weight.py`, `python/notebooks/04_sim_validate.py`, `python/checks/check_categorical_weight.py`, `python/checks/check_sim_validate.py`, shared `python/src/rethinking_companion/categorical.py`.
- Three models in one notebook. **W\~S**: indexed group means a[S] ~ Normal(60,10) with shared sigma ~ Uniform(0,10). S=1 Female (187), S=2 Male (165), 352 adults. **W\~S+H**: sex-varying intercepts and positive slopes b[S] ~ LogNormal(0,1) on centered height. **Full SCM**: jointly model height and weight as functions of sex; simulate do(S) to get the total causal effect.
- The **W\~S** model has an independent integration oracle: conditionally on sigma, each a[k] has a Normal posterior. Integrate out both a[k] analytically, then numerically integrate sigma on a 2001-point grid. NUTS means agree within 6 Monte Carlo standard errors. Grid boundary mass < 1e-8.
- W\~S integrated posterior means: a[Female]=41.844, a[Male]=48.611, sigma=5.525. Mean contrast M−F ≈ 6.77 kg. P(individual male heavier than individual female) ≈ 0.61. The mean contrast is tight; the individual contrast is wide because sigma dominates.
- W\~S diagnostics: R-hat 1.0009, min bulk ESS 5301, min tail ESS 3860, zero divergences, BFMI 1.067, max depth 3.
- W\~S+H diagnostics: R-hat 1.0010, min bulk ESS 4219, tail ESS 3928, zero divergences, BFMI 1.075, max depth 6. LogNormal slopes confirmed positive.
- Full SCM: total causal effect do(Male)−do(Female) ≈ 6.81 kg; direct effect (height-adjusted mean contrast) ≈ −0.07 kg. The total effect is larger because sex affects height, and height affects weight. Diagnostics: R-hat 1.0015, min bulk ESS 4459, tail ESS 3889, zero divergences, BFMI 0.995, depth 6.
- **Simulation validation lab** (from `LA04_sim heights validate example.r`): simulate W = b*H + noise from known b=0.5, fit, check 89% interval coverage. Single detailed recovery passes (b=0.4455, CI [0.389, 0.503]). 20-replication coverage: 85% (within sampling error of 89% nominal). Interactive notebook with 10/50/100 replication options.
- Differences: NUTS replaces `quap`. The do(S) contrast simulates through the joint posterior rather than using `sim()`. The simulation validation uses PyMC throughout rather than the R `replicate(100, f())` pattern. Notebook display controls select model stage; each stage fits four chains.

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

- R `PI(draws, mass)` → `np.quantile(draws, [(1-mass)/2, (1+mass)/2])`; use exact distribution quantiles where available and check covered area independently.

- Observation error trees → enumerate joint true-state/report paths, marginalize by summation, then normalize compatible paths; preserve the direction of conditioning.

### Model-fitting pattern

- `quap` / `extract.samples` → explicitly specified PyMC model + four-chain NUTS, retaining labeled `InferenceData.posterior` chain/draw axes for ArviZ. This changes the inference algorithm, not the likelihood/prior; compare with independent references before reuse.
- `extract.prior` → `pm.sample_prior_predictive`; `sim` at training inputs → `sample_posterior_predictive(..., extend_inferencedata=True)`.
- `link` at new predictors → separate prediction model with the same coefficient names/dimensions and deterministic mean; `sample_posterior_predictive(..., predictions=True, var_names=[mean,outcome])` conditions on the joint posterior. Tests must verify those means equal matrix multiplication of the original posterior coefficients.
- `precis` → `az.summary`; also inspect unrounded rank R-hat, bulk/tail ESS, divergences, BFMI and tree depth. A passing sampler is not evidence that the statistical model fits reality.
- Equal-tailed intervals use NumPy quantiles; ArviZ summary's default HDI is not called a percentile interval. Preserve joint draws for contrasts/covariances.
- Independent first-model oracle: Normal-prior, known-noise regression has V=(I+XᵀX/σ²)⁻¹, m=VXᵀy/σ². Use linear solves. Predictive covariance includes observation variance as well as X V Xᵀ.
- API references used: [PyMC posterior predictions](https://www.pymc.io/projects/docs/en/v5.24.0/api/generated/pymc.sample_posterior_predictive.html), [ArviZ diagnostics](https://python.arviz.org/en/v0.21.0/api/diagnostics.html); installed signatures/source were checked for version-specific behavior.

- Positive slope `dlnorm(0,1)` → `pm.LogNormal(mu=0,sigma=1)`; Uniform residual SD → bounded PyMC variable with automatic transform. Independently check support and density implications, not only sampler convergence.
- Preserve the training centering constant as saved fit metadata. A new prediction grid must never redefine the intercept by using its own average.
- Local source data: immutable upstream URL + SHA-256 + schema/row checks, provenance and upstream license; no network dependency during lesson execution.

### Wave 01: Parallel sessions S2 + S4 + S5

Three sessions ran in parallel from the same branch tip using separate worktrees. Integration order: S2 first (WaffleDivorce data), S4 second (trivial WaffleDivorce dedup), S5 third (runtime.py change).

#### S2 — B-spline regression + elemental confounds

- Source: `scripts/04_prior_pred_spline.r` (224 lines), `scripts/05_elemental_confounds.r` (261 lines).
- Artifacts: `04_spline.py`, `05_confounds.py`, `check_spline.py`, `check_confounds.py`, `spline.py` helper, cherry blossom + WaffleDivorce data with provenance.
- B-spline basis via `scipy.interpolate.BSpline.design_matrix`; no new dependencies.
- Cherry blossom spline (20 knots, tau=10): R-hat 1.0014, 0 divergences. Howell1 height~age: R-hat 1.0033, 0 divergences.
- WaffleDivorce D~M+A: bA=−0.607 (strong), bM=−0.058 (near zero). Confound confirmed.
- Fork/pipe/collider/descendant d-separation predictions verified. Happiness collider shows spurious conditional correlation.
- Animation deferred throughout.

| Source | Python artifact | Status | Verification |
|---|---|---|---|
| `04_prior_pred_spline.r`: B-spline basis, prior/posterior predictive | `04_spline.py` | complete | Basis properties, NUTS diagnostic gates, marimo check |
| `04_prior_pred_spline.r`: animation | — | deferred | |
| `05_elemental_confounds.r`: fork/pipe/collider/descendant | `05_confounds.py` | complete | d-separation predictions with n=10,000 |
| `05_elemental_confounds.r`: WaffleDivorce D~A, D~M, D~M+A | `05_confounds.py` | complete | NUTS diagnostic gates, bA strong, bM near zero |
| `05_elemental_confounds.r`: happiness collider | `05_confounds.py` | complete | Marginal independence, conditional negative correlation |
| `05_elemental_confounds.r`: animation | — | deferred | |

#### S4 — MCMC mechanics + ESS/ACF diagnostics

- Source: `scripts/08_MCMC.r` (612 lines), `scripts/08_mHMC.stan` (27 lines), `scripts/LB03_ess acf example.r` (61 lines).
- Artifacts: `08_mcmc.py`, `lab_ess_acf.py`, `check_mcmc.py`, `check_ess_acf.py`, `check_ess_acf_run.py` (fire-and-forget), `mcmc.py` helper, bangladesh data with provenance.
- King Markov: 200,000 steps, max |empirical − target| = 0.002, chi-squared 13.39.
- HMC leapfrog: energy conservation |ΔH| < 0.02 for step=0.01; divergent trajectories demonstrated at step=0.15.
- WaffleDivorce NUTS: bA=−0.610, bM=−0.062. R-hat 1.0020, ESS 4335, 0 divergences.
- Bad chains: pathological priors → R-hat 1.068, 237 divergences; reasonable priors → R-hat 1.005, 0 divergences.
- Bangladesh hierarchical (non-centered, ~50 min on compiler-free backend): R-hat 1.001, ESS 1310, 0 divergences. Partial pooling verified (posterior SD 0.338 vs raw SD 1.195).
- 1000-dim Normal: theta bulk ESS 5683 vs theta² bulk ESS 1890 (ratio 3.0×). ACF ordering correct.
- Animation deferred throughout.

| Source | Python artifact | Status | Verification |
|---|---|---|---|
| `08_MCMC.r`: King Markov | `08_mcmc.py` | complete | Stationary distribution matches target |
| `08_MCMC.r`: HMC leapfrog | `08_mcmc.py` | complete | Energy conservation + divergence demo |
| `08_MCMC.r`: WaffleDivorce workflow | `08_mcmc.py` | complete | NUTS diagnostic gates |
| `08_MCMC.r`: R-hat illustration | `08_mcmc.py` | complete | W/B convergence |
| `08_MCMC.r`: bad chains | `08_mcmc.py` | complete | Diagnostic failure + fix |
| `08_MCMC.r`: animation | — | deferred | |
| `08_mHMC.stan` | Absorbed into PyMC | complete | |
| `LB03_ess acf example.r`: Bangladesh | `lab_ess_acf.py` | complete | Non-centered, shrinkage verified |
| `LB03_ess acf example.r`: 1000-dim ESS | `lab_ess_acf.py` | complete | ESS ratio and ACF ordering |

#### S5 — Binomial/Poisson GLMs + sensitivity analysis

- Source: `scripts/09_binomial_GLMs.r` (323 lines), `scripts/10_confounds_poisson.r` (450 lines), `scripts/A10_sensitivity.R` (110 lines).
- Artifacts: `09_binomial_glm.py`, `10_poisson_sensitivity.py`, `check_binomial_glm.py`, `check_poisson_sensitivity.py`, `glm.py` helper, UCBadmit + Kline data with provenance.
- **First non-Gaussian likelihoods**: Bernoulli, Binomial, and Poisson.
- UCBadmit: Simpson's paradox confirmed — total effect favors men (P(admit|F) − P(admit|M) = −0.141), but 4/6 departments favor women. Marginal causal effect 0.036 (near zero).
- Aggregated binomial ≡ disaggregated Bernoulli: max mean diff 0.003.
- Sensitivity with latent u: u correlation 0.315 (fixed b/g). Proxy model: tau=[0.094, 0.498, 0.254] (true [0.1, 0.5, 0.25]), u correlation 0.958. Proxy model has poor mixing (R-hat 1.21, ESS 15, BFMI 0.019) but excellent estimates — documented as known PyMC limitation.
- Kline tools Poisson: interaction model has high Pareto k for Hawaii. Innovation/loss scientific model fits well.
- Runtime change: removed macOS compiler-free workaround from `runtime.py` after discovering and patching the PyTensor `-ld64` flag on macOS 26. C compilation now works, giving ~5–10× speedup.
- Animation deferred throughout.

| Source | Python artifact | Status | Verification |
|---|---|---|---|
| `09_binomial_GLMs.r`: logit link, priors | `09_binomial_glm.py` | complete | Prior predictive comparison |
| `09_binomial_GLMs.r`: animation | — | deferred | |
| `09_binomial_GLMs.r`: generative UCBadmit sim | `09_binomial_glm.py` | complete | Bernoulli + binomial equivalence |
| `09_binomial_GLMs.r`: UCBadmit real data | `09_binomial_glm.py` | complete | Simpson's paradox, marginal causal effect |
| `10_confounds_poisson.r`: confounded sim | `10_poisson_sensitivity.py` | complete | Spurious contrast + u recovery |
| `10_confounds_poisson.r`: sensitivity | `10_poisson_sensitivity.py` | complete | Latent u, fixed + learned b/g |
| `10_confounds_poisson.r`: real UCBadmit sensitivity | `10_poisson_sensitivity.py` | complete | Dept A contrast 0.061 |
| `10_confounds_poisson.r`: proxy variables | `10_poisson_sensitivity.py` | complete | tau recovery excellent; mixing poor (documented) |
| `10_confounds_poisson.r`: Poisson regression (Kline) | `10_poisson_sensitivity.py` | complete | PSIS comparison, Hawaii influential |
| `10_confounds_poisson.r`: innovation/loss model | `10_poisson_sensitivity.py` | complete | Scientific model verified |
| `A10_sensitivity.R` | Merged into `10_poisson_sensitivity.py` | complete | Learned b/g model |

## Known Issues / Deferred Fidelity

- Distinct Week 2 statistical concepts are complete. Incidental drawing variants use the same verified counting rule; exact radial presentation is not reproduced.
- Week 2 homework is outside this source-script translation checkpoint.
- Exact radial geometry, animation, fonts and slide presentation are deferred across all sessions.
- GIS/globe graphics remain deferred; the globe script's Beta updating and interval computations are complete.
- Live interaction needs a running marimo process; exported HTML does not recompute Python.
- The proxy variable model (`10_poisson_sensitivity.py`) has poor NUTS mixing (R-hat 1.21, ESS 15) but excellent parameter recovery. This is a known PyMC limitation for funnel geometries; Stan handles it better. Documented in the lesson.
- The A10 learned b/g model has marginal convergence (R-hat 1.019, ESS 287). The Uniform(0,1) priors with 2000 latent variables is near PyMC's practical limit.
- PyTensor `-ld64` patch on macOS 26 is applied to the local venv's site-packages and will be lost on `uv sync`. Re-apply after rebuilding the environment (see S5 commit `6055bcf` for instructions).

## Next Chunk

The next roadmap sessions are:

- **S3**: Bad controls (`06_simulations_bad_controls.r` + `06_breen_collider_animation.R`) + overfitting/info criteria/robust regression (`07_overfitting_animations.r`). Completes Weeks 6–7 beginner.
- **S6**: Ordered categorical regression (`11_ordered_categories.r`). Completes Week 10 beginner.
- **S7**: Intro multilevel models (`12_intro_multilevel_models.r`) + Mundlak machine (`12_bonus_mundlak.r` + `B04_bonus_mundlak.r`). First multilevel model.

S3 and S6 are natural Wave 02 parallel candidates (independent weeks, no shared data). S7 (first multilevel model) is the next critical-path risk and could also run in parallel if its infrastructure needs are self-contained.

## Re-entry Instructions

Read this report, inspect Git status and recent commits, and continue from the **Next Chunk** section. The parallel orchestrator protocol is in `python/prompts/003-parallel-wave-orchestrator.md`; wave coordination records are in `python/reports/parallel/`. Do not redo completed chunks unless new evidence identifies a defect. The repository must remain resumable without previous chat history.
