# Wave 01 — Parallel Worker Coordination Record

## Overview

Three workers run concurrently from the tip of `agent/cortex-python-companion` (`aaa459f`). Each has its own branch, worktree, prompt, plan path, and report path. Workers do not coordinate with each other. The integration orchestrator merges their work after all three complete.

## Workers

### Worker S2 — B-Spline Regression + Elemental Confounds

| Field | Value |
|---|---|
| Roadmap session | S2 (Weeks 4–5 beginner) |
| Scope | B-spline regression on cherry blossom and Howell1; fork/pipe/collider/descendant simulations; WaffleDivorce multiple regression; happiness collider |
| Branch | `agent/cortex-s2` |
| Worktree | `../statrethinking-s2` |
| Worker prompt | `python/prompts/parallel/wave-01-s2.md` |
| Plan path | `python/reports/parallel/wave-01/plan-s2.md` |
| Final report path | `python/reports/parallel/wave-01/report-s2.md` |
| R source files | `scripts/04_prior_pred_spline.r` (224 lines), `scripts/05_elemental_confounds.r` (261 lines) |
| Data to vendor | cherry_blossoms (from rethinking), WaffleDivorce (from rethinking) |
| Expected notebooks | `04_spline.py`, `05_confounds.py` |
| Expected checks | `check_spline.py`, `check_confounds.py` |
| Expected helpers | `spline.py` (B-spline basis via scipy) |
| New dependencies | None expected (scipy covers B-spline basis) |
| Shared-file risks | WaffleDivorce data overlap with S4 (trivial merge — identical files) |
| Likely long computations | Cherry blossom and Howell1 spline fits (moderate, < 60s each expected) |
| Recommended integration order | **First** — vendors WaffleDivorce data used by S4; introduces confounds vocabulary |

### Worker S4 — MCMC Mechanics + ESS/ACF Diagnostics

| Field | Value |
|---|---|
| Roadmap session | S4 (Week 8 beginner) + ESS lab (bonus) |
| Scope | King Markov sampler, HMC leapfrog mechanics, WaffleDivorce NUTS workflow, R-hat/ACF illustration, bad chains, Bangladesh hierarchical diagnostics, 1000-dim ESS |
| Branch | `agent/cortex-s4` |
| Worktree | `../statrethinking-s4` |
| Worker prompt | `python/prompts/parallel/wave-01-s4.md` |
| Plan path | `python/reports/parallel/wave-01/plan-s4.md` |
| Final report path | `python/reports/parallel/wave-01/report-s4.md` |
| R source files | `scripts/08_MCMC.r` (612 lines), `scripts/08_mHMC.stan` (27 lines), `scripts/LB03_ess acf example.r` (61 lines) |
| Data to vendor | WaffleDivorce (from rethinking), bangladesh (from rethinking) |
| Expected notebooks | `08_mcmc.py`, `lab_ess_acf.py` |
| Expected checks | `check_mcmc.py`, `check_ess_acf.py` |
| Expected helpers | `mcmc.py` (pedagogical King Markov, leapfrog implementations) |
| New dependencies | None expected |
| Shared-file risks | WaffleDivorce data overlap with S2 (trivial merge — identical files) |
| Likely long computations | Bangladesh hierarchical model (61 varying intercepts + slopes, 1–5 min); 1000-dim Normal (likely fast but monitor) |
| Recommended integration order | **Second** — independent of S2 content but WaffleDivorce data deduplicates after S2 merge |

### Worker S5 — Binomial/Poisson GLMs + Sensitivity Analysis

| Field | Value |
|---|---|
| Roadmap session | S5 (Week 9 beginner) |
| Scope | First non-Gaussian likelihoods; logit link; UCBadmit total/direct binomial models; Simpson's paradox; marginal causal effects; latent confounders; sensitivity analysis with latent u; proxy variables; Poisson regression on Kline tools; innovation/loss scientific model; PSIS comparison |
| Branch | `agent/cortex-s5` |
| Worktree | `../statrethinking-s5` |
| Worker prompt | `python/prompts/parallel/wave-01-s5.md` |
| Plan path | `python/reports/parallel/wave-01/plan-s5.md` |
| Final report path | `python/reports/parallel/wave-01/report-s5.md` |
| R source files | `scripts/09_binomial_GLMs.r` (323 lines), `scripts/10_confounds_poisson.r` (450 lines), `scripts/A10_sensitivity.R` (110 lines) |
| Data to vendor | UCBadmit (from rethinking), Kline (from rethinking) |
| Expected notebooks | `09_binomial_glm.py`, `10_poisson_sensitivity.py` |
| Expected checks | `check_binomial_glm.py`, `check_poisson_sensitivity.py` |
| Expected helpers | `glm.py` (inv_logit/logit wrappers via scipy.special) |
| New dependencies | None expected (PyMC handles binomial/Poisson natively) |
| Shared-file risks | None (UCBadmit and Kline data are unique to this worker; no notebook overlaps) |
| Likely long computations | **Sensitivity models with latent u** (2000–4500 latent parameters each, 2–10 min) — fire-and-forget handoffs expected for: simulated sensitivity (m3s), real UCBadmit sensitivity (mGDu), proxy model (m4), A10 extended sensitivity |
| Recommended integration order | **Third** — introduces non-Gaussian likelihoods; largest scope; most fire-and-forget handoffs |

## Cross-worker dependency analysis

| Pair | Overlap | Risk | Mitigation |
|---|---|---|---|
| S2 ↔ S4 | WaffleDivorce data | Low | Both vendor independently; integrator keeps one copy |
| S2 ↔ S5 | None | None | Fully independent |
| S4 ↔ S5 | None | None | Fully independent |
| All | pyproject.toml/uv.lock | Low | No new deps expected; flag prominently if needed |
| All | Notebook filenames | None | Different week prefixes (04/05, 08/lab, 09/10) |
| All | Helper modules | None | Different files (spline.py, mcmc.py, glm.py) |

## Integration order rationale

1. **S2 first**: smallest scope, establishes WaffleDivorce data and confounds vocabulary
2. **S4 second**: WaffleDivorce deduplication is trivial; MCMC content is independent
3. **S5 third**: largest scope, most likely to have unresolved issues; integrating last allows most review time

## Post-integration actions

After all three workers are merged into `agent/cortex-python-companion`:

1. Deduplicate WaffleDivorce data (keep one copy with checksum)
2. Reconcile any shared helper changes
3. Run aggregate verification across all new lessons
4. Update `python/reports/cumulative-report.md`
5. Update `python/reports/remaining-work-roadmap.md` if materially changed
6. Update `python/README.md` with new lesson entries
7. Remove completed worker worktrees
8. Recommend next wave
