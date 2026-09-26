# Remaining Work Roadmap — Statistical Rethinking Python Companion

## 1. Handoff Provenance

- **Predecessor branch**: `project/python-companion`
- **Base commit**: `2e4e36766e33e55a67845da0b8d79b41e4aa9ebc`
  - `plan: require Cortex handoff branch from current project tip` (2026-09-26)
- **Cortex branch**: `agent/cortex-python-companion`
  - Continues exactly from the predecessor tip; zero divergence at planning time.
- **Prior work**: 17 Python-port commits, 81 total commits on the predecessor branch.
- **Predecessor sessions**: approximately 4–6 coding-agent sessions produced 8 verified marimo notebooks (5 Week 2, 3 Week 3), 10 check scripts, a shared `rethinking_companion` package, and the cumulative report.

## 2. Current State

### Completed

- **Week 2** (5 lessons): path counting, garden sizes, misclassification, Beta updating, predictive simulation.
- **Week 3** (3 lessons): Gaussian sums, linear/polynomial regression with exact posterior oracle, centered positive-slope regression with unknown sigma on real + simulated data.
- **Shared infrastructure**: `runtime.py` (PyTensor config), `gaussian_regression.py` (exact posterior, PyMC fitting, diagnostics), `height_weight.py` (centered regression, numerical integration oracle), checksummed Howell1 data with provenance.
- **Established patterns**: four-chain NUTS with diagnostic gates (R-hat < 1.01, ESS > 400, zero divergences, BFMI > 0.3), exact/numerical oracle comparison, marimo check + HTML export, Altair chart schemas, `App.run(defs=...)` for programmatic control verification.

### Not started

Everything from Week 4 onward (Beginner track Weeks 4–10, Experienced track Weeks 1–10, bonus/lab material).

### Deferred from prior work

- GIS/globe animation from `02_globe_tossing_updating.r`
- Garden animation (`02_garden_animation.r`)
- Growth-model block from `03_gaussian_generative_sim.r`
- Prior-line illustration (`03_howell_plots.r`)
- Ptolemaic animation (`03_ptolemaic_model.R`)
- Repeated-fit experiment from `03_howell_new_weight_model.r`
- All-age polynomial/log models and animation from `03_howell_new_weight_model.r`

## 3. Source Inventory

Every file under `scripts/` is accounted for below. Actions: `translate` (new Python lesson needed), `extend-existing-lesson` (add to an existing notebook), `merge-with-related-source` (combine into another script's lesson), `already-covered` (Python equivalent exists), `defer-presentation-only` (animation/decoration with no distinct statistical content), `defer-duplicate` (near-duplicate of another entry).

### Week 2 — Already covered

| Source | Concept | Action | Python artifact |
|---|---|---|---|
| `02_garden_plots_lib.R` | Path counting, Bayes updating, misclassification | already-covered | `02_garden.py`, `02_garden_sizes.py`, `02_misclassification.py` |
| `02_garden_animation.r` | Garden path frame animation | already-covered | Deferred; concept in garden lessons |
| `02_globe_tossing_updating.r` | Beta updating, predictive simulation | already-covered | `02_beta_updating.py`, `02_predictive_simulation.py`; GIS deferred |
| `02_predictive_simulation.r` | Prior/posterior predictive simulation | already-covered | `02_predictive_simulation.py` |

### Week 3 — Already covered

| Source | Concept | Action | Python artifact |
|---|---|---|---|
| `03_gaussian_generative_sim.r` | Random walks → Gaussian sums | already-covered | `03_gaussian_sums.py`; growth block deferred |
| `03_prior_pred_OLS.r` | Linear/polynomial regression | already-covered | `03_gaussian_regression.py` |
| `03_howell_new_weight_model.r` | Centered regression, positive slope | already-covered | `03_height_weight.py`; animation/all-age deferred |
| `03_howell_plots.r` | Prior line illustration | already-covered | Mechanism in prior-function lessons |
| `03_ptolemaic_model.R` | Geocentric epicycle animation | defer-presentation-only | No statistical model |

### Week 4 — Beginner: Categories and Causes

| Source | Concept | Action | Complexity | Dependencies |
|---|---|---|---|---|
| `04_height_weight_sex_categorical.r` | Categorical predictors (index variables), posterior contrasts, causal effects via SCM (W\~S, W\~S+H, full joint) | translate | M–L | Howell1 data (vendored); extends height_weight pattern |
| `04_prior_pred_spline.r` | B-spline regression, prior/posterior predictive, cherry blossom data | translate | M | Cherry blossom data (new); splines package equivalent; animation deferrable |

### Week 5 — Beginner: Estimands and Estiplans

| Source | Concept | Action | Complexity | Dependencies |
|---|---|---|---|---|
| `05_elemental_confounds.r` | Fork, pipe, collider, descendant confounds; WaffleDivorce multiple regression; happiness simulation | translate | M–L | WaffleDivorce data (from rethinking); multiple regression pattern |
| `05_DAG_animations.r` | DAG structure animations (fork, pipe, collider, instrument, m-bias) | defer-presentation-only | — | Pure animation; concepts taught via elemental confounds |

### Week 6 — Beginner: Elemental Confounds

| Source | Concept | Action | Complexity | Dependencies |
|---|---|---|---|---|
| `06_simulations_bad_controls.r` | Post-treatment bias, case-control, precision parasite, bias amplification | translate | M | Monte Carlo `lm()` simulation; no Bayesian fitting |
| `06_breen_collider_animation.R` | Collider bias: grandparent-parent-child education triad | merge-with-related-source | S–M | Statistical content can merge with bad-controls or confounds lesson |
| `06_DAG_animations.r` | DAG animations (table-2 fallacy, smoking) | defer-presentation-only | — | All code inside `if(FALSE)`; pure animation |

### Week 7 — Beginner: Good and Bad Controls / Overfitting

| Source | Concept | Action | Complexity | Dependencies |
|---|---|---|---|---|
| `07_overfitting_animations.r` | Overfitting, LOO-CV, WAIC, PSIS, regularization, model comparison, Student-t robust regression | translate | L | Brain/mass data, WaffleDivorce, plant growth; ArviZ `compare`; most complex beginner file (566 lines) |
| `07_copernican_model.R` | Copernican epicycle geometric animation | defer-presentation-only | — | No statistics; philosophical illustration |

### Week 8 — Beginner: MCMC

| Source | Concept | Action | Complexity | Dependencies |
|---|---|---|---|---|
| `08_MCMC.r` | Metropolis algorithm, HMC mechanics, chain diagnostics, King Markov | translate | M–L | Manual sampler code; `ulam` models; HMC trajectory animation deferrable |
| `08_mHMC.stan` | Minimal Stan regression for MCMC lecture | merge-with-related-source | S | Companion to `08_MCMC.r` |

### Week 9 — Beginner: Modeling Events

| Source | Concept | Action | Complexity | Dependencies |
|---|---|---|---|---|
| `09_binomial_GLMs.r` | Binomial/logistic GLMs, logit link, UCBerkeley admissions, Simpson's paradox, marginal causal effects | translate | L | **First non-Gaussian likelihood**; UCBadmit data; causal contrasts on probability scale |
| `10_confounds_poisson.r` | Unmeasured confounders in GLMs, sensitivity with latent variables, proxy variables, Poisson regression (Kline tools) | translate | L–XL | Latent variable models, custom Stan code, PSIS diagnostics, multiple scientific models |
| `A10_sensitivity.R` | UCBadmit sensitivity analysis with latent u | merge-with-related-source | M | Overlaps with `10_confounds_poisson`; extend that lesson |

### Week 10 — Beginner: Ordered Outcomes / Sensitivity

| Source | Concept | Action | Complexity | Dependencies |
|---|---|---|---|---|
| `11_ordered_categories.r` | Ordered logistic regression, Trolley data, Dirichlet monotonic effects, gender-stratified education | translate | L | Ordered logit link, `dordlogit`, Dirichlet priors, simplex constraints |

### Week 1–2 Experienced: Multilevel Models

| Source | Concept | Action | Complexity | Dependencies |
|---|---|---|---|---|
| `12_intro_multilevel_models.r` | Partial pooling, varying intercepts, adaptive sigma, coffee/Reed-frog/Trolley examples | translate | XL | **First multilevel model**; 496 lines; cmdstanr; WAIC/PSIS comparison; animation |
| `12_bonus_mundlak.r` | Mundlak machine: fixed effects, random effects, group-mean centering, latent Mundlak | translate | L | Five deconfounding strategies; endogenous group confounds |

### Week 2 Experienced: GLMM Expansion

| Source | Concept | Action | Complexity | Dependencies |
|---|---|---|---|---|
| `13_GLMM2.r` | Non-centered parameterization, UCBadmit pooling, chimpanzee block-treatment, devil's funnel | translate | XL | 622 lines; 8+ models; multiple datasets; HMC animation |
| `13_varying_features_bangladesh.R` | Varying intercepts + slopes on Bangladesh contraception data | translate | M–L | Applied varying effects; non-centered parameterization; real data |

### Week 3 Experienced: Correlated Features

| Source | Concept | Action | Complexity | Dependencies |
|---|---|---|---|---|
| `14_GLMM_slopes_.r` | Correlated varying slopes, Cholesky decomposition, LKJ correlation prior, animated Bayesian updating | translate | XL | Learned covariance; inline Stan; 501 lines |
| `14_varying_slopes_bangladesh.R` | Varying slopes ± covariance on Bangladesh data; centered vs non-centered Cholesky | translate | L | Comparison of covariance-aware vs independent models |

### Week 4–5 Experienced: Social Networks

| Source | Concept | Action | Complexity | Dependencies |
|---|---|---|---|---|
| `15_social_networks.r` | Social relations model, dyadic reciprocity, generalized giving/receiving, household effects | translate | XL | Multivariate non-centered, Cholesky, igraph network visualization; 476 lines |

### Week 6 Experienced: Gaussian Processes

| Source | Concept | Action | Complexity | Dependencies |
|---|---|---|---|---|
| `16_gaussian_processes.r` | GP kernels (L2, L1, periodic), spatial GP (Kline), phylogenetic GP/OU (primate data) | translate | XL | ~10 models; Stan sidecars; phylogenetic `ape` package; 680 lines |
| `16_gp_fast_f.stan` | GP with fixed kernel hyperparameters | merge-with-related-source | M | Stan sidecar for GP lesson |
| `16_gp_fast_l.stan` | GP with learned kernel hyperparameters | merge-with-related-source | M | Stan sidecar for GP lesson |

### Week 7 Experienced: Measurement Models

| Source | Concept | Action | Complexity | Dependencies |
|---|---|---|---|---|
| `17_measurement_error.r` | Measurement error (divorce, recall bias), misclassification (Himba paternity), custom likelihoods | translate | L–XL | 8+ models; three error scenarios; Himba.csv; `custom()` likelihood |
| `17_age_estimation.r` | Age estimation from family structure constraints | translate | M | 43 lines; uses Stan sidecar |
| `17_measurement_error.stan` | Age estimation Stan model (draft/incomplete) | merge-with-related-source | S | Sidecar for `17_age_estimation.r` |

### Week 8 Experienced: Missing and Censored Data

| Source | Concept | Action | Complexity | Dependencies |
|---|---|---|---|---|
| `18_missing_data.r` | MCAR/MAR/MNAR simulations, phylogenetic imputation (301 species), censored exponential | translate | XL | 10+ models; `18_BMG_OU.stan`; phylogenetic trees; inline Stan |
| `18_BMG_OU.stan` | Phylogenetic imputation with OU covariance and missing data | merge-with-related-source | L | Stan sidecar for `18_missing_data.r` |
| `18_BMG_OU` (binary) | Compiled Stan executable | defer-duplicate | — | Pre-compiled binary; not source code |

### Week 9 Experienced: Generalized Linear Madness

| Source | Concept | Action | Complexity | Dependencies |
|---|---|---|---|---|
| `19_gen_lin_madness.r` | Scientific non-linear models: geometric weight, cognitive state model, Lotka-Volterra ODE | translate | XL | Custom Stan code; ODE integration; 391 lines |

### Bonus / Lab Scripts

| Source | Concept | Action | Complexity | Dependencies |
|---|---|---|---|---|
| `B04_bonus_mundlak.r` | Extended Mundlak with estimand evaluation (acc_doX) | extend-existing-lesson | L | Extends `12_bonus_mundlak`; adds causal estimand accuracy |
| `B04_social_networks.r` | Social relations model (experienced track duplicate) | defer-duplicate | — | Near-identical to `15_social_networks.r` |
| `B08 black cats new script.r` | Survival analysis: geometric survival, censoring, AustinCats data | translate | L | Unique survival/event-history content; custom likelihood |
| `B09_new_lynx.R` | Lotka-Volterra ODE (cleaner standalone) | merge-with-related-source | M | Cleaner version of lynx-hare from `19_gen_lin_madness.r` |
| `B10_HMMs_basic.R` | Hidden Markov Models, capture-recapture | translate | L–XL | Stan `hmm_marginal`; unique content |
| `LA04_histograms height weight sex Howell1.r` | Histogram visualization of sex differences | defer-presentation-only | — | Pure visualization; no models |
| `LA04_sim heights validate example.r` | Simulation-based model validation, 100-replication coverage | translate | S–M | Core pedagogical technique |
| `LB03_ess acf example.r` | ESS and autocorrelation diagnostics | translate | M | Hierarchical logistic + 1000-dim ESS demo |

### Presentation-Only / Decorative

| Source | Concept | Action |
|---|---|---|
| `00_title_twinkle.R` | Title slide animation (light) | defer-presentation-only |
| `00_title_twinkle_dark.R` | Title slide animation (dark) | defer-presentation-only |
| `00_random_igraph.R` | Random network decoration | defer-presentation-only |

### Data Files (not work units)

| Source | Purpose |
|---|---|
| `scripts/Himba.csv` | Data for `17_measurement_error.r` |
| `scripts/UCBadmit_long.csv` | Data for GLM scripts |
| `scripts/week08_Monks.csv` | Data for `15_social_networks.r` |
| `scripts/README.md` | Scripts directory documentation |

## 4. Scope Tiers

### Tier 1 — Core Remaining Pedagogical Companion (Beginner track, Weeks 4–10)

Everything required for a coherent Python path through the main beginner course material.

| Work unit | Source(s) | Complexity |
|---|---|---|
| Categorical means and posterior contrasts | `04_height_weight_sex_categorical.r` | M–L |
| B-spline regression | `04_prior_pred_spline.r` | M |
| Elemental confounds and WaffleDivorce | `05_elemental_confounds.r` | M–L |
| Bad controls simulation study | `06_simulations_bad_controls.r` + `06_breen_collider_animation.R` | M |
| Overfitting, information criteria, robust regression | `07_overfitting_animations.r` | L |
| MCMC mechanics and diagnostics | `08_MCMC.r` + `08_mHMC.stan` | M–L |
| Binomial GLMs and Simpson's paradox | `09_binomial_GLMs.r` | L |
| Poisson GLMs, latent confounders, sensitivity | `10_confounds_poisson.r` + `A10_sensitivity.R` | L–XL |
| Ordered categorical regression | `11_ordered_categories.r` | L |

**9 work units** spanning 12 source files.

### Tier 2 — Experienced / Advanced Course Material

Multilevel models, varying effects, networks, GPs, measurement error, missing data, HMMs, and advanced non-linear models.

| Work unit | Source(s) | Complexity |
|---|---|---|
| Intro multilevel models (partial pooling, varying intercepts) | `12_intro_multilevel_models.r` | XL |
| Mundlak machine (group confounds) | `12_bonus_mundlak.r` | L |
| GLMM expansion (non-centered, devil's funnel) | `13_GLMM2.r` | XL |
| Varying features on Bangladesh data | `13_varying_features_bangladesh.R` | M–L |
| Correlated varying slopes (Cholesky, LKJ) | `14_GLMM_slopes_.r` | XL |
| Varying slopes on Bangladesh data | `14_varying_slopes_bangladesh.R` | L |
| Social relations model for networks | `15_social_networks.r` | XL |
| Gaussian processes (spatial + phylogenetic) | `16_gaussian_processes.r` + Stan sidecars | XL |
| Measurement error and misclassification | `17_measurement_error.r` + `17_age_estimation.r` + Stan | L–XL |
| Missing data mechanisms and imputation | `18_missing_data.r` + `18_BMG_OU.stan` | XL |
| Generalized linear madness (geometric, cognitive, ODE) | `19_gen_lin_madness.r` | XL |

**11 work units** spanning 17 source files.

### Tier 3 — Optional Fidelity / Bonus Material

Material that adds depth but is not required for a pedagogically complete path.

| Work unit | Source(s) | Complexity | Why lower priority |
|---|---|---|---|
| Extended Mundlak with estimand evaluation | `B04_bonus_mundlak.r` | L | Extends Tier 2 Mundlak; adds causal accuracy metric |
| Survival analysis (black cats) | `B08 black cats new script.r` | L | Unique but supplementary; not in main lecture sequence |
| Hidden Markov Models | `B10_HMMs_basic.R` | L–XL | Experienced Week 10 bonus; Stan HMM functions |
| Simulation-based validation | `LA04_sim heights validate example.r` | S–M | Pedagogically useful workflow technique |
| ESS and autocorrelation diagnostics | `LB03_ess acf example.r` | M | Diagnostic-focused lab; supplements MCMC lesson |
| Sensitivity analysis extension | `A10_sensitivity.R` | M | Overlaps `10_confounds_poisson`; listed as merge target |
| Collider bias demo | `06_breen_collider_animation.R` | S–M | Animation-heavy; statistical content in bad controls |

**7 work units** (5 unique, 2 merge targets already counted in Tier 1).

**Deferred with no planned work**: 8 presentation-only files (animations, title slides, decorative plots), 1 compiled binary, 1 near-duplicate (`B04_social_networks.r` ≈ `15_social_networks.r`).

## 5. Complexity Assessment

### Size definitions (calibrated from repository history)

| Size | Description | Examples from prior work |
|---|---|---|
| **S** | Deterministic simulation, visualization, algebra, or extension of established pattern | Single check script; histogram overlay |
| **M** | One new model or concept using known translation/verification patterns | `03_gaussian_sums` (discrete walk + exact enumeration); `02_predictive_simulation` (beta-binomial draws) |
| **L** | Several related fitted models, new likelihood family, causal simulation, or substantial independent validation | `03_height_weight` (synthetic + real data, unknown sigma, numerical integration oracle) |
| **XL** | Multilevel/GLMM architecture, Gaussian processes, networks, missing-data models, HMMs, unfamiliar Stan logic, or work requiring investigation before implementation | `12_intro_multilevel_models` (partial pooling, cmdstanr, WAIC/PSIS); `16_gaussian_processes` (~10 models, phylogenetic trees) |

### Calibration from prior work

- Week 2 (5 lessons from 4 scripts): ~2–3 sessions. Dominated by environment setup, first marimo pattern, and first verification infrastructure.
- Week 3 (3 lessons from 3 scripts): ~2–3 sessions. Dominated by PyMC/ArviZ fitting infrastructure, exact posterior oracle, numerical integration oracle, runtime debugging (macOS PyTensor), and the first real-data fit.
- **Observed rate**: 1–3 completed lessons per session; fitted-model lessons take roughly 1 session each; simulation-only lessons can share a session.
- The first PyMC fit (`03_gaussian_regression`) was expensive because it established the fitting, diagnostic, and prediction patterns. Subsequent fits (`03_height_weight`) reused that infrastructure but still required model-specific validation.

## 6. Session Estimates

These estimates assume multi-file sessions: each session translates 2–3 source files where they share a week, dataset, or statistical infrastructure. The predecessor sessions already demonstrated this rate (Week 2 produced 5 lessons from 4 scripts in ~2–3 sessions). Future sessions benefit from established fitting patterns, diagnostic gates, and marimo/Altair conventions that no longer need to be built.

Only the largest scripts (GPs at 680 lines, missing data at 512 lines) or first-of-kind technical jumps (first multilevel model, first non-Gaussian likelihood) are expected to consume a full session alone.

### Tier 1 + Tier 2 (Pedagogically complete + source-accounted)

| | Sessions | Lessons/chunks | Assumptions | Dominant work |
|---|---|---|---|---|
| **Optimistic** | 14–16 | ~20 | Established patterns reuse cleanly; 2–3 files per session is the norm; no major runtime surprises; data vendoring smooth | Advanced models (multilevel, GPs, networks) still need new infrastructure but fit 1–2 per session |
| **Expected** | 18–22 | ~20 | Normal debugging; full verification; most sessions handle 2 files; first-of-kind items (multilevel, GP, ODE) take a full session each | GPs (new covariance infrastructure), social networks (igraph replacement), missing data (phylogenetic imputation), ODE models |
| **Conservative** | 26–30 | ~20 | Difficult model translations; phylogenetic/network data dependencies; additional validation or refactoring; some XL items split across sessions; occasional single-file sessions | Phylogenetic GP/OU (new library ecosystem), HMMs (Stan-specific functions), ODE integration in PyMC/Stan |

### Tier 3 (Bonus — additional)

| | Sessions | Lessons/chunks |
|---|---|---|
| **Optimistic** | +2–3 | ~5–7 |
| **Expected** | +3–5 | ~5–7 |
| **Conservative** | +5–7 | ~5–7 |

### Major assumptions

- A "session" means one fresh coding-agent context comparable to the predecessor sessions (which each produced 1–3 verified lessons).
- Sessions handling related M-complexity files (same week, shared dataset) routinely complete 2–3 source files. Sessions dominated by a single XL file or a first-of-kind technical jump complete 1 file.
- The biggest uncertainty is in Tier 2 XL items (multilevel, GPs, networks, missing data, ODE), which collectively account for ~60% of the expected effort.
- Data vendoring for datasets not already in the repository (WaffleDivorce, UCBadmit, cherry blossom, Bangladesh, Kline, AustinCats, primate phylogeny) will add overhead to the first session that needs each dataset.
- PyMC's multilevel and GP capabilities exist but may differ from `ulam`/`cmdstanr` in ways that require investigation.
- Stan-specific features (`hmm_marginal`, custom ODE, `compose_noncentered`) may need PyMC equivalents or direct PyStan/CmdStanPy usage.

## 7. Recommended Session Roadmap

| Session | Proposed scope | Why grouped | Main risk | Exit condition |
|---|---|---|---|---|
| **S1** | Full categorical lesson: `04_height_weight_sex_categorical.r` (all blocks: W\~S, W\~S+H, full SCM) + `LA04_sim heights validate example.r` (simulation validation lab) | Same week and dataset (Howell1, already vendored); cumulative report's declared next chunk; validation lab is S-complexity and reinforces the fit-check workflow | Multi-equation SCM is new; `do`-calculus contrast needs careful joint-model construction | All three model stages (indexed means, height-adjusted, full SCM) verified; total vs direct causal effect comparison; 100-replication simulation validation passes; posterior contrasts and P(individual M > individual F) checked |
| **S2** | B-spline regression (`04_prior_pred_spline.r`) + elemental confounds and WaffleDivorce (`05_elemental_confounds.r`) | Both introduce new regression concepts (basis functions, multiple regression with causal interpretation); completes Weeks 4–5 beginner content | Cherry blossom and WaffleDivorce data vendoring; `patsy`/`scikit-learn` B-spline equivalents; two new datasets in one session | Spline prior/posterior predictive verified; fork/pipe/collider simulations verified; divorce model passes diagnostics; happiness collider demonstrated |
| **S3** | Bad controls (`06_simulations_bad_controls.r` + `06_breen_collider_animation.R`) + overfitting/info criteria/robust regression (`07_overfitting_animations.r`) | Bad controls are simulation-only (no fitting, M-complexity) so pair naturally with the heavier overfitting file; completes Weeks 6–7 | `07_overfitting` is the largest beginner file (566 lines); multiple datasets and model families; ArviZ `compare` API | Four bad-control scenarios verified; brain/mass polynomials, plant growth, WaffleDivorce models verified; WAIC/PSIS comparison demonstrated; Student-t robust fit passes |
| **S4** | MCMC mechanics (`08_MCMC.r` + `08_mHMC.stan`) + ESS/ACF diagnostics lab (`LB03_ess acf example.r`) | MCMC internals and diagnostic assessment are one pedagogical unit; ESS lab directly reinforces | Manual Metropolis/HMC code; hierarchical model for ESS demo requires multilevel-like PyMC patterns | King Markov sampler matches analytical; HMC trajectory demonstrated; ESS/ACF lesson verified; all three source files accounted for |
| **S5** | Binomial GLMs (`09_binomial_GLMs.r`) + Poisson GLMs / sensitivity (`10_confounds_poisson.r` + `A10_sensitivity.R`) | Both are Week 9 GLM content sharing the logit/log link infrastructure and UCBadmit data; sensitivity analysis extends the confounded GLM | **First non-Gaussian likelihood**; `inv_logit` link; custom Stan code for sensitivity; PSIS diagnostics; Kline data; 3 source files | UCBadmit total/direct binomial models verified; Poisson scientific models verified; sensitivity analysis with latent u demonstrated; marginal causal effects on probability scale |
| **S6** | Ordered categorical regression (`11_ordered_categories.r`) | Completes beginner track; Dirichlet priors and ordered logit are distinct new mechanics | Ordered logit link; simplex constraints in PyMC; multi-threaded Stan translation | Trolley models verified; monotonic education effect with Dirichlet demonstrated; cumulative logit demonstrated |
| **S7** | Intro multilevel models (`12_intro_multilevel_models.r`) + Mundlak machine (`12_bonus_mundlak.r` + `B04_bonus_mundlak.r`) | **First multilevel model**; Mundlak directly complements by addressing group confounds in the same partial-pooling framework | New PyMC patterns for varying intercepts; cmdstanr → PyMC; latent Mundlak joint model; 3 source files but shared infrastructure | Coffee/Reed-frog/Trolley varying intercepts verified; adaptive sigma demonstrated; all five Mundlak strategies verified; causal estimand accuracy compared |
| **S8** | GLMM expansion (`13_GLMM2.r`) + varying features Bangladesh (`13_varying_features_bangladesh.R`) | Both extend multilevel models with non-centered parameterization; Bangladesh applies what GLMM2 teaches abstractly | 8+ models in GLMM2; devil's funnel; non-centered parameterization must work in PyMC | UCBadmit pooling, chimpanzee block-treatment, devil's funnel all verified; Bangladesh varying intercepts + slopes verified; shrinkage demonstrated |
| **S9** | Correlated varying slopes (`14_GLMM_slopes_.r`) + varying slopes Bangladesh (`14_varying_slopes_bangladesh.R`) | Both teach learned covariance / Cholesky / LKJ; Bangladesh applies the UCBadmit covariance pattern to real data | Inline Stan code; LKJ Cholesky factorization; `compose_noncentered` translation | UCBadmit correlated slopes verified; all Bangladesh covariance models verified; shrinkage comparison plots demonstrated |
| **S10** | Social networks (`15_social_networks.r`) | Social relations model is a self-contained XL topic; multivariate non-centered dyadic model is unique | igraph replacement (NetworkX); network visualization; Koster-Leckie data vendoring; 476 lines | Dyad model + full SRM verified on simulated and real data; network visualization demonstrated |
| **S11–S12** | Gaussian processes (`16_gaussian_processes.r` + `16_gp_fast_f.stan` + `16_gp_fast_l.stan`) | GP kernels, spatial GP, phylogenetic GP/OU; the single most complex topic (~10 models, 680 lines + 2 Stan sidecars); likely needs 2 sessions | Covariance kernel construction in PyMC; phylogenetic tree data (`ape` → Python); Stan custom GP prediction functions | S11: GP regression with fixed/learned kernels verified; Kline spatial model verified. S12: at least one phylogenetic OU model verified; primate brain/body analysis demonstrated |
| **S13** | Measurement error (`17_measurement_error.r` + `17_age_estimation.r` + `17_measurement_error.stan`) | Three error scenarios share custom-likelihood infrastructure; age estimation is small (43 lines) and uses the same Stan sidecar | `custom()` likelihood → PyMC potential; Himba data vendoring; draft Stan model may need completion | Divorce measurement error, paternity misclassification, age estimation all verified |
| **S14–S15** | Missing data (`18_missing_data.r` + `18_BMG_OU.stan`) | MCAR/MAR/MNAR sims, phylogenetic imputation (301 species), censored exponential; likely needs 2 sessions due to 10+ models and phylogenetic complexity | Phylogenetic imputation reuses GP covariance infrastructure from S11–S12; `merge_missing` Stan function; inline Stan for censored model | S14: dog-homework MCAR/MAR/MNAR simulations verified; censored exponential (naive + imputation + marginalization) verified. S15: phylogenetic imputation models verified; complete-case comparisons demonstrated |
| **S16** | Generalized linear madness (`19_gen_lin_madness.r`) + Lotka-Volterra standalone (`B09_new_lynx.R`) | All three scientific non-linear models (geometric, cognitive, ODE) from one script; `B09` is a cleaner ODE standalone that merges naturally | Custom Stan for cognitive Boxes model; ODE integration in Stan/PyMC; lynx-hare data | Geometric weight model, cognitive state model, and Lotka-Volterra ODE all verified; posterior population trajectories demonstrated |
| **S17** | Survival analysis (`B08 black cats new script.r`) + Hidden Markov Models (`B10_HMMs_basic.R`) | Both are bonus experienced-track material with custom likelihoods; pairing keeps the bonus content in one session | Custom censoring likelihoods; `hmm_marginal` equivalent in Python; may need CmdStanPy for HMMs; AustinCats data | Geometric survival ± censoring verified; single-individual and capture-recapture HMMs verified |

**Total: 17–19 sessions** (expected estimate for all tiers, including Tier 3 bonus material).

Sessions S11–S12 (GPs) and S14–S15 (missing data) are split because those scripts are the largest and most complex in the corpus. S3 and S5 are the most ambitious multi-file sessions; if either proves too large in practice, the second file can spill into the next session without disrupting the rest of the roadmap.

## 8. Critical-Path Risks

These are the remaining concepts that represent the largest technical jumps, ordered roughly by when they appear in the roadmap.

### First non-Gaussian likelihood (S5: binomial + Poisson GLMs)

- **Why hard**: All prior work uses Gaussian likelihoods. The logit link, aggregated vs disaggregated data, and probability-scale contrasts are new patterns.
- **Mitigation**: PyMC handles logistic regression natively; the UCBadmit dataset is standard.

### First multilevel model (S7: intro multilevel + Mundlak)

- **Why hard**: Varying intercepts with adaptive regularization (sigma estimated from data) require new PyMC patterns. The predecessor `ulam` → PyMC mapping for hierarchical models has not been established.
- **Mitigation**: PyMC is designed for hierarchical models; ArviZ diagnostics transfer directly. The key risk is translating `compose_noncentered` and getting efficient NUTS sampling.

### Non-centered parameterization and devil's funnel (S8)

- **Why hard**: The centered → non-centered transform is critical for HMC efficiency on hierarchical models. PyMC has some automatic reparameterization but may need manual intervention.
- **Mitigation**: Well-documented in PyMC; the funnel example is pedagogically clear.

### Correlated varying effects / Cholesky / LKJ (S9)

- **Why hard**: Multivariate varying effects with learned covariance matrices and LKJ priors are the most complex hierarchical structure before GPs.
- **Mitigation**: PyMC supports `LKJCholeskyCov` and `MvNormal`; the difficulty is matching the `compose_noncentered` Cholesky factorization.

### Social networks / igraph (S10)

- **Why hard**: Network data requires a Python graph library (NetworkX or igraph-python), network visualization, and the multivariate dyadic reciprocity model.
- **Mitigation**: NetworkX is mature; the statistical model is an extension of correlated varying effects.

### Gaussian processes (S11–S12)

- **Why hard**: Covariance kernel construction, GP regression, spatial distance matrices, and phylogenetic Ornstein-Uhlenbeck processes. The Stan sidecars define custom GP prediction functions. Phylogenetic data requires a Python tree library.
- **Mitigation**: PyMC has `gp.Latent` and `gp.Marginal`; `ete3` or `dendropy` for phylogenetics. This is likely the single most investigation-heavy topic.

### Missing data imputation (S14–S15)

- **Why hard**: Bayesian imputation of phylogenetic data for 301 species with OU covariance; the `merge_missing` Stan function splices imputed values into observed vectors. Censored data requires custom likelihoods.
- **Mitigation**: PyMC supports masked data and potential functions. Phylogenetic covariance can reuse GP infrastructure from S11–S12.

### ODE models (S16)

- **Why hard**: Lotka-Volterra requires ODE integration within the sampler. Stan uses `integrate_ode_rk45`; PyMC has `pytensor.tensor.ode` or `sunode`, but the integration may be fragile.
- **Mitigation**: The lynx-hare model is well-studied; a manual Euler integrator could serve as fallback.

### HMMs (S17)

- **Why hard**: Stan's built-in `hmm_marginal` and `hmm_hidden_state_prob` do not have direct PyMC equivalents. May require CmdStanPy or a manual forward algorithm.
- **Mitigation**: `hmmlearn` or manual forward/Viterbi in PyMC. The model structure is well-defined.

## 9. Reuse Opportunities

### Existing infrastructure that reduces future effort

| Component | Location | Reuse scope |
|---|---|---|
| PyMC four-chain NUTS fitting | `gaussian_regression.fit_gaussian()` | Pattern (not the function directly) reusable for all future models |
| Diagnostic gates | `gaussian_regression.diagnostics()`, `assert_diagnostics()` | Directly reusable for every fitted model |
| Exact Normal posterior oracle | `gaussian_regression.exact_posterior()` | Reusable for any known-noise Gaussian model; basis for new oracles |
| Numerical integration oracle | `height_weight.integrated_weight_posterior()` | Pattern reusable for any low-dimensional posterior |
| Runtime configuration | `runtime.configure_runtime()` | All future lessons import this |
| Howell1 data with checksum | `height_weight.load_howell()` | Reusable for all Howell1-based lessons (Week 4 categorical, splines) |
| Marimo `App.run(defs=...)` verification | All check scripts | Pattern reusable for every marimo lesson |
| Altair chart schema checks | All check scripts | Pattern reusable |
| `uv` lock + `marimo check` | Project-wide | CI/verification pattern |

### Recommended new shared infrastructure

| Component | When needed | Benefit |
|---|---|---|
| Data vendoring helper (URL + SHA-256 + schema check) | S4 (WaffleDivorce) | Standardizes data acquisition for ~6 new datasets |
| `inv_logit` / logit link utilities | S8 (binomial GLMs) | Used in every GLM lesson after Week 9 |
| Hierarchical model fitting helper (non-centered option) | S11 (intro multilevel) | Reduces boilerplate for all multilevel models |
| ArviZ `compare` wrapper for WAIC/PSIS | S6 (overfitting) or S11 | Standardizes model comparison display |
| Phylogenetic distance/covariance helper | S17 (GPs) | Shared by GP and missing-data phylogenetic lessons |

No speculative architecture work is recommended during this planning pass. Build shared helpers when the second consumer appears.

## 10. Completion Criteria

### Pedagogically complete (primary target)

Every distinct statistical concept in the upstream material has an executable, verified Python representation. This covers all Tier 1 + Tier 2 work units (20 distinct concepts across 29 source files).

### Source-accounted (primary target)

Every R/Stan source file under `scripts/` appears in this inventory with an explicit disposition: translated, merged, already covered, deferred as presentation-only, or deferred as duplicate. This is already satisfied by the inventory in §3.

### Fully faithful (optional stretch)

All presentation, animation, and secondary variants are also reproduced. This would add Tier 3 and all deferred items. Not recommended as a primary target unless Scott explicitly requests cosmetic fidelity.

**The project should target pedagogically complete + source-accounted.** All 51 R/Stan source files and 4 data/documentation files are accounted for in the inventory above.

## 11. Recommended Next Implementation Session

**Session S1**: Full categorical lesson from `scripts/04_height_weight_sex_categorical.r` (all three blocks: W\~S, W\~S+H, full joint SCM) plus the simulation-based validation lab from `scripts/LA04_sim heights validate example.r`.

This is the cumulative report's declared next chunk, extended to include the complete script and a small complementary lab. It:

- directly extends the existing `03_height_weight.py` pattern;
- uses the already-vendored Howell1 data;
- introduces index-variable categorical predictors (a[S]);
- demonstrates posterior group-mean contrasts (M−F) vs individual-prediction contrasts;
- progresses through height-adjusted models and the full multi-equation SCM for total vs direct causal effects;
- adds simulation-based model validation (100-replication coverage check) as a reusable pedagogical technique;
- establishes the causal-interpretation vocabulary for everything after Week 4.

**Exit condition**: All three model stages (indexed means, height-adjusted, full SCM) verified; total vs direct causal effect comparison demonstrated; 100-replication simulation validation passes; posterior contrasts and P(individual M > individual F) checked; diagnostic gates pass; marimo notebooks execute and export.
