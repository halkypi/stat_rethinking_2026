# Session S5 Implementation Plan — Binomial/Poisson GLMs + Sensitivity Analysis

## Scope

Translate three R source files into two verified Python marimo notebooks:

| R source | Lines | Python target |
|---|---|---|
| `scripts/09_binomial_GLMs.r` | 323 | `python/notebooks/09_binomial_glm.py` |
| `scripts/10_confounds_poisson.r` | 450 | `python/notebooks/10_poisson_sensitivity.py` |
| `scripts/A10_sensitivity.R` | 110 | Merged into `10_poisson_sensitivity.py` |

These introduce the **first non-Gaussian likelihoods** (binomial, Bernoulli, Poisson) in the project.

## Artifacts to create

### Data files
- `python/data/UCBadmit.csv` — 12 rows (6 depts × 2 genders). Columns: dept, applicant.gender, admit, reject, applications. Vendored with SHA-256 checksum.
- `python/data/UCBadmit.provenance.json` — SHA-256, attribution to the `rethinking` R package (originally Bickel et al. 1975), schema description.
- `python/data/Kline.csv` — 10 rows (Oceanic societies). Columns: culture, population, contact, total_tools, mean_TU. Vendored with SHA-256 checksum.
- `python/data/Kline.provenance.json` — SHA-256, attribution to Kline & Boyd 2010 via `rethinking`.

### Shared helper
- `python/src/rethinking_companion/glm.py` — GLM utilities:
  - `inv_logit(x)` → `scipy.special.expit(x)`
  - `logit(p)` → `scipy.special.logit(p)`
  - `load_ucbadmit()` — load + checksum verify + return dict with G, D, A, N arrays
  - `ucbadmit_to_long(d)` — expand aggregated UCBadmit to individual rows (replicating the R tidyverse `uncount` pattern)
  - `load_kline()` — load + checksum verify + return dict with T, P (standardized log population), C (contact index), raw population, culture names

### Notebooks
- `python/notebooks/09_binomial_glm.py` — Binomial GLMs lesson
- `python/notebooks/10_poisson_sensitivity.py` — Poisson/sensitivity lesson

### Check scripts
- `python/checks/check_binomial_glm.py`
- `python/checks/check_poisson_sensitivity.py`

## Data vendoring approach

Extract UCBadmit and Kline data from the `rethinking` R package. Since we can't run R, I'll create the CSV files from the well-known published data:

**UCBadmit** (Bickel, Hammel & O'Connell 1975, Science 187:398-404): 12 rows exactly matching the `rethinking` package. The data is a standard textbook dataset.

**Kline** (Kline & Boyd 2010): 10 Oceanic societies with tool counts. Standard dataset from the `rethinking` package.

Both will follow the established pattern: CSV file + provenance JSON with SHA-256 checksum, attribution, and schema. The loader functions will verify checksums at load time, matching the `height_weight.py` pattern.

## Model specifications

### Notebook 09: Binomial GLMs

**1. Logit link and priors** (R lines 1–30)
- Show `inv_logit` curve
- Prior predictive: Normal(0,10) vs Normal(0,1.5) on logit scale
- Prior predictive lines: a ~ Normal(0,1.5), b ~ Normal(0,0.5)

**2. Prior updating animation** (R lines 31–137)
- **Animation deferred.** Preserve static prior predictive lines on the logit-probability curve as a pedagogical element.

**3. Generative simulation — mediator DAG** (R lines 139–228)
- Simulate N=1000: G → D → A with G → A
- `accept_rate = matrix(c(0.05,0.2,0.1,0.3), nrow=2)` (R's final version)
- **m1 (total effect)**: `A ~ Bernoulli(inv_logit(a[G]))`, a[G] ~ Normal(0,1)
  - PyMC: `pm.Bernoulli("A", logit_p=a[G-1], observed=A)`
- **m2 (direct effect)**: `A ~ Bernoulli(inv_logit(a[G,D]))`, a[G,D] ~ Normal(0,1)
  - PyMC: 2×2 indexed parameter matrix
- Contrasts on logit and probability scales
- **m2_bin (aggregated)**: `A ~ Binomial(N, inv_logit(a[G,D]))` on aggregated data
  - Show equivalence to the disaggregated Bernoulli fit

**4. UCBadmit real data** (R lines 229–323)
- **mG (total effect)**: `A ~ Binomial(N, inv_logit(a[G]))`, a[G] ~ Normal(0,1)
- **mGD (direct effect)**: `A ~ Binomial(N, inv_logit(a[G,D]))`, a[G,D] ~ Normal(0,1)
  - 2×6 parameter matrix (2 genders × 6 departments)
- Traceplots, rank plots via ArviZ
- Per-department gender contrasts on probability scale
- **Marginal causal effect**: simulate counterfactual — all applicants perceived as women vs men, weighted by department application volumes. This is the key result.

### Notebook 10: Poisson/Sensitivity

**1. Confounded UCBadmit simulation** (R lines 1–130 of `10_confounds_poisson.r`)
- N=2000, seed=17, latent binary ability u ~ Bernoulli(0.1)
- **m1 (total)**: same as above
- **m2 (direct, confounded)**: a[G,D] without u — shows spurious gender effects
- **m3 (with observed u)**: `logit(p) = a[G,D] + buA*u`, buA constrained positive
  - PyMC: `pm.HalfNormal` or `pm.TruncatedNormal(lower=0)` for buA
- Show that including u recovers true (near-zero) gender contrasts

**2. Sensitivity model on simulated data** (R lines 94–128)
- Latent u as `vector[N]:u ~ Normal(0,1)` — N=2000 latent parameters
- Joint model: admission model + department-choice model sharing u
- Fixed effect strengths b=[1,1], g=[1,0]
- PyMC: `u = pm.Normal("u", 0, 1, dims="applicant")` with N=2000
- **This is a long-running computation (~2–10 min)**

**3. Sensitivity on real UCBadmit** (R lines 131–270)
- Convert to long format (~4526 rows)
- **mGD (direct)**: Binomial on aggregated, for comparison
- **mGDu (sensitivity)**: Bernoulli on long-format with ~4526 latent u parameters
- Fixed b=[1,1], g=[1,0]
- **Very long-running (~5–15 min)**

**4. Extended sensitivity from A10** (R `A10_sensitivity.R`)
- Different simulation parameters: seed=12, different acceptance rates
- **mGDu (fixed b/g)**: same structure, different data
- **mGDu2 (learned b/g)**: b[G] ~ Uniform(0,1), g[G] ~ Uniform(0,1)
- Wider but more honest uncertainty
- Also long-running

**5. Proxy variables** (R lines 274–316)
- Three noisy proxies: T_k ~ Normal(u, tau_k), tau = [0.1, 0.5, 0.25]
- Joint model: admission + measurement model for proxies
- b constrained positive, tau ~ Exponential(1)
- N=2000 latent u + 3 measurement equations
- **Long-running computation**

**6. Poisson regression — Kline tools** (R lines 318–450)
- Standardize: `P = scale(log(population))`
- **Intercept-only**: `T ~ Poisson(exp(a))`, a ~ Normal(3, 0.5)
- **Interaction model**: `T ~ Poisson(exp(a[C] + b[C]*P))`, a[C] ~ Normal(3,0.5), b[C] ~ Normal(0,0.2)
- PSIS comparison via ArviZ (`az.loo`)
- Pareto k diagnostics — expect high-k for Hawaii
- Prediction plots on standardized and natural population scales
- **Innovation/loss model**: `lambda = exp(a[C]) * P^b[C] / g`
  - a[C] ~ Normal(1,1), b[C] ~ Exponential(1), g ~ Exponential(1)
  - Uses raw (unstandardized) population
  - Better PSIS diagnostics expected

## Long-format conversion for UCBadmit

Replicate the R tidyverse `uncount` pattern programmatically:
```python
def ucbadmit_to_long(d):
    """Expand aggregated UCBadmit to individual Bernoulli rows."""
    rows = []
    for _, row in d.iterrows():
        rows.extend([{...admit=1...}] * row["admit"])
        rows.extend([{...admit=0...}] * row["reject"])
    return pd.DataFrame(rows)
```
This produces ~4526 rows (sum of admit+reject across all 12 rows).

## Sensitivity model approach — latent u in PyMC

The key PyMC pattern for the sensitivity model:
```python
with pm.Model(coords={"applicant": np.arange(N), "gender": [1,2], "dept": [1,2]}):
    a = pm.Normal("a", 0, 1, dims=("gender", "dept"))
    delta = pm.Normal("delta", 0, 1, dims="gender")
    u = pm.Normal("u", 0, 1, dims="applicant")  # latent ability
    
    # Admission model
    logit_p = a[G-1, D-1] + b[G-1] * u
    pm.Bernoulli("A", logit_p=logit_p, observed=A)
    
    # Department choice model
    logit_q = delta[G-1] + g[G-1] * u
    pm.Bernoulli("D2", logit_p=logit_q, observed=D2)
```

Where `b` and `g` are either fixed data or learned Uniform(0,1) parameters.

This creates N latent parameters (2000 for simulated, ~4526 for real data), making these models substantially more expensive than previous fits.

## Merging A10_sensitivity.R

The A10 content extends the sensitivity analysis with:
1. Different simulation parameters (seed=12 instead of 17, different acceptance rates)
2. A model where b and g are learned rather than fixed

This fits naturally into notebook 10 as additional sections after the base sensitivity analysis. The notebook will present:
- Base sensitivity with fixed b/g on seed-17 simulation
- Extended sensitivity with fixed b/g on seed-12 simulation (showing robustness to simulation parameters)
- Learned b/g model showing wider but more honest uncertainty

## Validation/oracle strategy

### Binomial GLM (notebook 09)
- **Generative simulation**: true acceptance rates are known. Total-effect model should recover overall gender gap. Direct-effect model should show department-specific rates.
- **Aggregated ≡ disaggregated**: posterior means for a[G,D] should agree within Monte Carlo error between Bernoulli (individual) and Binomial (aggregated) fits.
- **UCBadmit real data**: Simpson's paradox pattern — total P(admit|female) < P(admit|male), but within most departments female rate ≥ male rate.
- **Marginal causal effect**: should be small, centered near zero.
- **All fits**: diagnostic gates (R-hat < 1.01, ESS > 400, zero divergences, BFMI > 0.3).

### Poisson/sensitivity (notebook 10)
- **Confounded simulation**: naive direct-effect model shows spurious gender differences; including u moves contrast toward zero.
- **Sensitivity (fixed b/g)**: contrast shifts relative to the confounded model.
- **Sensitivity (learned b/g)**: wider uncertainty, contrast still shifts.
- **Proxy model**: tau estimates near generating values (0.1, 0.5, 0.25).
- **Kline intercept-only**: diagnostic gates.
- **Kline interaction**: diagnostic gates. PSIS should show some high Pareto k (Hawaii). 
- **Innovation/loss**: better PSIS diagnostics than log-linear model.
- **All models**: standard diagnostic gates.

## Fire-and-forget handoff plan

These models have N latent parameters and will take minutes, not seconds:

| Model | N latent | Estimated time | Phase |
|---|---|---|---|
| m3s (simulated sensitivity, fixed b/g) | 2000 | 2–10 min | Sim sensitivity |
| mGDu (real UCBadmit sensitivity) | ~4526 | 5–15 min | Real sensitivity |
| mGDu_A10 (A10 fixed b/g) | 2000 | 2–10 min | Extended sensitivity |
| mGDu2_A10 (A10 learned b/g) | 2000 | 2–10 min | Extended sensitivity |
| m4 (proxy model) | 2000 + measurement | 2–10 min | Proxy variables |

**Protocol**: For each long computation:
1. Commit all code first
2. Provide the exact `uv run python checks/check_*.py` command
3. STOP and wait for Scott to run it and report results
4. Inspect artifacts when Scott reports completion

Short fits (generative simulation Bernoulli/Binomial, UCBadmit binomial, Kline Poisson) should complete in < 30 seconds and can run autonomously.

## Dependency and shared-infrastructure needs

### New shared helper: `python/src/rethinking_companion/glm.py`
- `inv_logit`, `logit` (thin wrappers around scipy.special)
- Data loaders for UCBadmit and Kline with checksum verification
- Long-format conversion utility

### Reused from existing infrastructure
- `runtime.py` — PyTensor configuration
- `gaussian_regression.py` — `diagnostics()`, `assert_diagnostics()` (reused as-is for all non-Gaussian fits too — they only inspect ArviZ InferenceData)
- Data vendoring pattern from `height_weight.py`

### No new Python package dependencies expected
- PyMC handles Bernoulli, Binomial, Poisson natively
- `scipy.special.expit`/`logit` already available
- ArviZ `az.loo` for PSIS comparison already available

## Likely integration conflicts

### With S2 (B-splines + confounds)
- Both may create new data files in `python/data/`. No filename overlap expected (UCBadmit/Kline vs cherry blossom/WaffleDivorce).
- Both may add shared helpers. S5 creates `glm.py`; S2 may add spline utilities. No overlap.
- S2's confounds lesson uses `quap`-equivalent fits on WaffleDivorce. S5's confounds are entirely different (UCBadmit sensitivity). No model overlap.

### With S4 (whatever that session covers)
- Unknown scope. Likely different source scripts. Conflict risk is low if both follow the convention of separate notebook/helper/data files.

### Shared files
- Neither `cumulative-report.md` nor `remaining-work-roadmap.md` nor `pyproject.toml` will be edited by this session.
- `__init__.py` in `rethinking_companion` may need updating if other sessions also add modules. Current `__init__.py` is empty, so adding imports there would conflict. **Plan: do not modify `__init__.py`**; use explicit imports from submodules.

## Implementation order

1. Vendor UCBadmit and Kline data (CSV + provenance JSON)
2. Create `glm.py` shared helper (inv_logit, logit, data loaders)
3. Build notebook 09 incrementally:
   a. Logit link + prior predictive
   b. Generative simulation (Bernoulli fits — fast)
   c. Aggregated vs disaggregated equivalence
   d. UCBadmit real data (Binomial fits — fast)
   e. Marginal causal effect
4. Create `check_binomial_glm.py` and verify
5. Build notebook 10 incrementally:
   a. Confounded simulation (fast Bernoulli fits)
   b. Observed-u model (fast)
   c. Sensitivity models (long — fire-and-forget)
   d. Proxy variables (long — fire-and-forget)
   e. Poisson regression on Kline (fast)
   f. Innovation/loss model (fast)
6. Create `check_poisson_sensitivity.py` and verify
7. Final commit with all verified artifacts
