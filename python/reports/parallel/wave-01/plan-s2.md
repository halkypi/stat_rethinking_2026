# Session S2 Implementation Plan — B-Spline Regression + Elemental Confounds

## Scope

Translate two R source scripts into verified Python marimo notebooks:

1. `scripts/04_prior_pred_spline.r` (224 lines) → `python/notebooks/04_spline.py`
2. `scripts/05_elemental_confounds.r` (261 lines) → `python/notebooks/05_confounds.py`

## Artifacts

### Data
- `python/data/cherry_blossoms.csv` — vendored from rethinking package (1215 rows, semicolon-delimited)
- `python/data/cherry_blossoms.provenance.json` — SHA-256 checksum and attribution
- `python/data/WaffleDivorce.csv` — vendored from rethinking package (50 rows, semicolon-delimited)
- `python/data/WaffleDivorce.provenance.json` — SHA-256 checksum and attribution

### Shared helpers
- `python/src/rethinking_companion/spline.py` — B-spline basis construction via `scipy.interpolate.BSpline`, cherry blossom and Howell1 data loading, spline model fitting functions

### Notebooks
- `python/notebooks/04_spline.py` — B-spline basis visualization, prior predictive draws, cherry blossom and Howell1 height~age posterior fits
- `python/notebooks/05_confounds.py` — fork/pipe/collider/descendant simulations, d-separation scatter plots, WaffleDivorce multiple regression, publication collider, happiness collider

### Check scripts
- `python/checks/check_spline.py` — basis properties, cherry blossom fit, Howell1 height~age fit
- `python/checks/check_confounds.py` — d-separation predictions, happiness collider, WaffleDivorce three-model comparison

## B-spline basis construction

Use `scipy.interpolate.BSpline.design_matrix()` with a clamped knot vector matching R's `bs()`. Internal knots from `np.linspace(min, max, num_knots)`; boundary knots extended by epsilon to avoid scipy's half-open interval zeroing the last observation. Drop the first column for `intercept=False`.

## Model specifications

### Cherry blossom spline
- Y ~ Normal(a0 + a*B, exp(log_sigma))
- a0 ~ Normal(100, 1), a ~ Normal(0, tau), log_sigma ~ Normal(0, 0.5)
- 20 knots, degree 3, tau=10

### Howell1 height~age spline
- Same structure with a0 ~ Normal(120, 1), tau=25

### WaffleDivorce
- D ~ Normal(a + bA*A, sigma) and variants
- a ~ Normal(0, 0.2), bM/bA ~ Normal(0, 0.5), sigma ~ Exp(1)
- Standardized predictors

## Validation strategy

- Basis: non-negativity, partition of unity (with intercept), correct dimension count
- All fits: R-hat < 1.01, bulk/tail ESS > 400, zero divergences, BFMI > 0.3
- Cherry blossom: mean residual < 2 days, a0 in [90, 120]
- Howell1: child heights < adult heights, positive growth slope in childhood
- Confounds: fork/pipe conditional correlations near zero, collider marginal near zero
- WaffleDivorce: bA strongly negative, bM near zero in multiple regression
- Happiness: marginal cor(age, happiness) near zero, conditional negative

## Dependencies

No new Python package dependencies. SciPy's `BSpline` covers B-spline basis construction.
