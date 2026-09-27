# Wave 01 Worker — Session S2: B-Spline Regression + Elemental Confounds

You are a worker in a parallel wave. Your scope is **Session S2** from `python/reports/remaining-work-roadmap.md`.

- **Branch**: `agent/cortex-s2`
- **Worktree**: `../statrethinking-s2`
- **Plan path**: `python/reports/parallel/wave-01/plan-s2.md`
- **Final report path**: `python/reports/parallel/wave-01/report-s2.md`

## Scope

Translate two R source scripts into verified Python marimo notebooks:

1. **B-spline regression** from `scripts/04_prior_pred_spline.r` (224 lines)
2. **Elemental confounds and WaffleDivorce multiple regression** from `scripts/05_elemental_confounds.r` (261 lines)

## R source files to inspect

- `scripts/04_prior_pred_spline.r` — cherry blossom spline (3 knots, 20 knots), prior/posterior predictive, Howell1 height~age spline. Uses `library(splines)`, `bs()` for B-spline basis, `quap` for fitting. Heavy animation portions are deferrable.
- `scripts/05_elemental_confounds.r` — fork/pipe/collider/descendant simulations with `rbern`; WaffleDivorce data (`data(WaffleDivorce)`) with standardized multiple regression (D~M+A); happiness collider simulation (`sim_happiness`); d-separation scatter plots. Uses `quap` for the divorce model.

## Existing Python artifacts to reuse

- `python/src/rethinking_companion/runtime.py` — PyTensor configuration
- `python/src/rethinking_companion/gaussian_regression.py` — exact posterior, diagnostics, fitting patterns
- `python/src/rethinking_companion/height_weight.py` — Howell1 data loading with checksum
- `python/notebooks/03_gaussian_regression.py` — reference for PyMC fitting notebook pattern
- `python/notebooks/04_categorical_weight.py` — reference for index-variable models
- `python/checks/` — reference for check script patterns

## Expected artifacts

### Notebooks
- `python/notebooks/04_spline.py` — B-spline regression on cherry blossom and Howell1 data
- `python/notebooks/05_confounds.py` — elemental confounds + WaffleDivorce multiple regression

### Check scripts
- `python/checks/check_spline.py`
- `python/checks/check_confounds.py`

### Data
- `python/data/cherry_blossoms.csv` — vendored cherry blossom data with SHA-256 checksum, attribution, and provenance
- `python/data/WaffleDivorce.csv` — vendored WaffleDivorce data with SHA-256 checksum, attribution, and provenance

### Shared helpers (if needed)
- `python/src/rethinking_companion/spline.py` — B-spline basis construction (use `scipy.interpolate.BSpline` or `scipy.interpolate.splev`; do not add new package dependencies)

## Pedagogical scope

### B-spline lesson (`04_spline.py`)
- Construct B-spline basis functions from `scipy.interpolate.BSpline` (the R `bs()` equivalent); do **not** add `patsy` or `scikit-learn` as dependencies.
- Cherry blossom data: filter complete cases on `doy`, fit a spline regression Y ~ Normal(a0 + a*B, sigma) with `quap` → four-chain NUTS.
- Show prior predictive draws (with different tau values) and posterior predictive fits.
- Howell1 height~age spline: use the already-vendored Howell1 data, fit spline regression of height on age (all ages, not just adults).
- Animation frames are **deferred**. Translate the statistical content (basis functions, prior/posterior predictive, fitted curves) into static Altair visualizations with marimo controls.
- Marimo controls: number of knots, tau (prior scale), and/or data subset size.

### Elemental confounds lesson (`05_confounds.py`)
- Fork, pipe, collider, descendant: simulation demonstrations with `numpy` random generators. Show correlation tables and d-separation logic. Altair scatter plots colored by conditioning variable.
- WaffleDivorce multiple regression: vendor the data, standardize D/M/A, fit D~A, D~M, D~M+A using four-chain NUTS. Compare coefficients (bA strong, bM weak after conditioning). Prior predictive simulation with Normal(0,0.2) intercept and Normal(0,0.5) slopes.
- Happiness collider simulation: simulate age/happiness/marriage, show that conditioning on marriage creates a spurious negative correlation. This uses the `sim_happiness` function from the rethinking package — you will need to implement the simulation logic directly.
- d-separation scatter plots showing fork/pipe/collider patterns with continuous variables.
- Animation is **deferred**.

## Validation and oracle strategy

### Spline lesson
- B-spline basis: verify basis matrix properties (partition of unity, non-negativity, support).
- Cherry blossom fit: four-chain NUTS with diagnostic gates (R-hat < 1.01, bulk/tail ESS > 400, zero divergences, BFMI > 0.3). Compare posterior mean curve against data. Prior predictive draws should span the data range for reasonable tau.
- Howell1 spline: same diagnostic gates. Posterior curve should capture the growth pattern (rapid increase in childhood, plateau in adulthood).

### Confounds lesson
- Fork/pipe/collider simulations: verify that unconditional correlations and conditional correlations match the expected d-separation predictions (fork: X⊥Y|Z; pipe: X⊥Y|Z; collider: X⊥̸Y|Z).
- WaffleDivorce model: diagnostic gates on all fits. Verify that bA is negative and bM is near zero in the multiple regression, matching the source's conclusion.
- Happiness collider: verify that the marginal correlation between age and happiness is near zero, but conditioning on married status creates a negative slope.

## Data and dependency needs

- **Cherry blossom data**: obtain from the `rethinking` R package's `cherry_blossoms` dataset. Vendor as CSV with checksum. Columns: year, doy (day of year of first bloom), temp, temp_upper, temp_lower. Many NA values — filter to complete cases on `doy` for the spline fit.
- **WaffleDivorce data**: obtain from the `rethinking` R package. Vendor as CSV with checksum. Key columns: Location, Loc, Population, MedianAgeMarriage, Marriage, Divorce, WaffleHouses, South. 50 rows (US states).
- **No new Python package dependencies expected.** SciPy's `interpolate.BSpline` covers B-spline basis construction. If you genuinely need a new package, flag it prominently in both your plan and final report.

## Shared-file restrictions

Do **not** edit these files:
- `python/reports/cumulative-report.md`
- `python/reports/remaining-work-roadmap.md`
- `python/README.md`
- `pyproject.toml` / `uv.lock` (unless a new dependency is absolutely required — flag prominently)

Prefer worker-owned notebooks, checks, helpers, plans, and reports. If you must change a shared file, document it in your plan and final report.

**Note**: Worker S4 (MCMC mechanics) also uses WaffleDivorce data. Both workers should vendor the data independently in their branches. The integration orchestrator will deduplicate at merge time. Do not coordinate with S4.

## Long-running computation expectations

Cherry blossom and WaffleDivorce fits should complete in under 60 seconds each on this machine (four-chain NUTS, compiler-free PyTensor backend). The Howell1 height~age spline fit with 20+ knots may take longer due to more parameters.

If any fit exceeds roughly two minutes, prepare a fire-and-forget handoff: commit the code, provide the exact shell command to run it, describe the output artifacts, and STOP.

## Two-phase protocol

### Phase 1 — Plan only

1. Orient from repository evidence: read this prompt, the cumulative report, recent Git history, and all R source files listed above.
2. Inspect existing Python artifacts for patterns to reuse.
3. Produce an implementation plan covering:
   - exact artifacts to create/change
   - data vendoring approach and checksum strategy
   - B-spline basis construction approach
   - model specifications for each fit
   - validation/oracle strategy
   - dependency or shared-infrastructure needs
   - likely integration conflicts
   - anticipated long-running computations (with fire-and-forget handoff if needed)
4. Write the plan to `python/reports/parallel/wave-01/plan-s2.md`.
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
8. Write and commit your final worker report to `python/reports/parallel/wave-01/report-s2.md`.
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
