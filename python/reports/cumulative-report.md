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

## Known Issues / Deferred Fidelity

- Distinct Week 2 statistical concepts are complete. Incidental one/two/three-bag drawing variants use the same verified counting rule; exact radial presentation is not reproduced.
- The earlier `garden2` drawing draft remains unported in favor of the explicit final manual misclassification model.
- Week 2 homework is outside this source-script translation checkpoint.
- Exact radial geometry, animation, fonts and slide presentation are deferred.
- The first lesson is finite inference, not a continuous grid approximation.
- Future sampling translations require statistical agreement rather than R-identical random streams.
- GIS/globe graphics remain deferred; the globe script's Beta updating and interval computations are complete. The first Normal-prior regression is verified; constrained/unknown-noise and non-Gaussian models still need their own validation.
- Live interaction needs a running marimo process; exported HTML does not recompute Python.

## Next Chunk

Begin the canonical **group means and posterior contrasts** lesson from the first `W ~ S` block of `scripts/04_height_weight_sex_categorical.r` (stop before `W ~ S + H`). Fit adult weights with indexed a[S] ~ Normal(60,10) and shared sigma ~ Uniform(0,10), using the existing checksummed Howell1 data and source mapping male=0/1 → Female/Male. Compare the posterior mean-weight contrast M−F with the much wider contrast between two independently predicted individuals, and estimate P(individual contrast>0). Preserve paired joint posterior draws. Independently integrate sigma with conditional Normal group means to check posterior/contrast moments and predictive probabilities, plus the established four-chain diagnostic gates. State that a statistical group contrast alone does not identify a causal effect. Existing dependencies suffice; later height-adjusted and full SCM models should extend or follow this lesson without duplicating its basic indexing concept.

## Re-entry Instructions

Read this report, inspect Git status and recent commits, inspect the source named under **Next Chunk**, and continue from there. Do not redo completed chunks unless new evidence identifies a defect. Update this report and make descriptive commits after each verified chunk. The repository must remain resumable without previous chat history.
