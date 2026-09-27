# Statistical Rethinking 2026 — Python Companion

Status: active

## Problem

The upstream 2026 course is taught with R/rethinking examples. The goal is to make the course directly usable while learning modern Python Bayesian workflow, without replacing or modifying McElreath's original material.

## Desired outcome

Build an executable Python companion, in course order, that preserves the statistical ideas and important visualizations while using idiomatic Python.

The first milestone is deliberately concrete: **complete at least one beginner lesson that Scott can step through end-to-end.**

## Approach

- Preserve `scripts/` and `homework/` as upstream reference material.
- Use marimo `.py` notebooks for executable lessons; Markdown for project state and reports.
- Prefer Python 3.13 where dependencies permit and `uv` for environment management.
- Core stack: NumPy, pandas, SciPy, PyMC, ArviZ, **Altair**, and marimo.
- Translate statistical operations and pedagogy, not R syntax mechanically.
- Work in small verified chunks.
- Treat `reports/cumulative-report.md` as the project spine.
- Put detailed implementation rationale and context in frequent, descriptive Git commits.

## Project layout

```text
python/
  README.md
  notebooks/
  prompts/
    001-python-port.md
  reports/
    cumulative-report.md
```

The Python 3.13 environment is defined by `pyproject.toml` and `uv.lock`. Only dependencies used by completed lessons are installed.

## Current state

Sixteen verified marimo notebooks cover Weeks 2–9 of the beginner track plus
MCMC diagnostics. Suggested learning order:

| Lesson | Concept |
|---|---|
| [Finite garden](notebooks/02_garden.py) | Path counting, likelihood and Bayesian updating |
| [Garden sizes](notebooks/02_garden_sizes.py) | Different path totals can give the same likelihood |
| [Misclassification](notebooks/02_misclassification.py) | True states, imperfect reports and conditioning |
| [Beta updating](notebooks/02_beta_updating.py) | Continuous parameter uncertainty and credible intervals |
| [Predictive simulation](notebooks/02_predictive_simulation.py) | Prior/posterior predictive counts and exact beta-binomial checks |
| [Gaussian sums](notebooks/03_gaussian_sums.py) | Exact random-walk probabilities and normal approximation |
| [Gaussian regression](notebooks/03_gaussian_regression.py) | First PyMC/ArviZ fit; exact posterior; polynomial extensions |
| [Height–weight](notebooks/03_height_weight.py) | Centering, positive slope, unknown sigma, real data |
| [Categorical weight](notebooks/04_categorical_weight.py) | Index variables, posterior contrasts, causal SCM |
| [Simulation validation](notebooks/04_sim_validate.py) | Coverage check via repeated recovery |
| [B-spline regression](notebooks/04_spline.py) | Basis functions, cherry blossom and Howell1 spline fits |
| [Elemental confounds](notebooks/05_confounds.py) | Fork/pipe/collider, WaffleDivorce multiple regression |
| [MCMC mechanics](notebooks/08_mcmc.py) | King Markov, HMC leapfrog, diagnostics, bad chains |
| [Binomial GLM](notebooks/09_binomial_glm.py) | Logit link, UCBadmit, Simpson's paradox, marginal causal effects |
| [Poisson and sensitivity](notebooks/10_poisson_sensitivity.py) | Latent confounders, proxy variables, Kline tools |
| [ESS/ACF lab](notebooks/lab_ess_acf.py) | Bangladesh hierarchical diagnostics, 1000-dim ESS |

Animation, GIS and incidental drawing variants are deferred. Homework has
not been translated.

## Run the lessons

From the repository root:

```sh
cd python
uv sync --locked
uv run marimo run notebooks
```

The gallery opens the lessons in a reading view. To inspect and edit individual
cells, use `uv run marimo edit notebooks/02_beta_updating.py` (or another lesson).
Controls choose observation prefixes, interval coverage, report accuracy, or
predictive simulation size. Each lesson states its source and assumptions.

## Verify and export

From `python/`:

```sh
uv run marimo check notebooks/02_*.py
uv run python checks/check_week02.py
mkdir -p outputs
uv run marimo export html notebooks/02_predictive_simulation.py -o outputs/02_predictive_simulation.html --force
```

The aggregate check executes all five lessons in isolated processes, tests their
controls, and compares calculations with independent exact probabilities,
numerical integration or sampling-error bounds. Focused `checks/check_*.py`
scripts are also available. Replace the filename in the export command to save
another lesson; generated snapshots are ignored by Git.

Model-fitting lessons run four chains. Simple models take 5–30 seconds;
hierarchical and latent-variable models (Bangladesh, sensitivity) can take
minutes. On macOS 26, C compilation is enabled after patching PyTensor's
`-ld64` flag (see cumulative report). Without the patch, the compiler-free
fallback still works but is slower.

HTML exports save rendered outputs; reactive controls require the live app.
Original R files remain unchanged. Detailed fidelity decisions and verification
results are in [the cumulative report](reports/cumulative-report.md).

### Optional Terminal handoff for long checks

Long checks can run directly in Terminal while the agent turn is finished. These
commands use local Python and do not call an OpenAI model. For example:

```sh
cd /Users/shalkyard/GitHub/stat_rethinking_2026/python
uv sync --locked
mkdir -p outputs
set -o pipefail
uv run python -u checks/check_height_weight.py 2>&1 | tee outputs/check_height_weight.log
echo "Exit status: $?"
```

Run the exit-status command immediately after the check; zero indicates success.
The check fits both synthetic and adult data, verifies them independently, and
saves NetCDF samples and diagnostic JSON under `outputs/`. Give the agent the log
path and exit status when finished so it can review the evidence before marking
the work complete. A failed check remains incomplete even if some artifacts exist.

A separate export executes another fresh fit:

```sh
uv run marimo export html notebooks/03_height_weight.py -o outputs/03_height_weight.html --force > outputs/export_height_weight.log 2>&1
echo "Exit status: $?"
```

The current checks and export already passed; rerun only when relevant changes
or unresolved concerns justify it. For a future chunk, use its specific check
and notebook filenames. User-run execution changes who monitors the process,
not the required sampling or verification standards.

## Definition of done for a lesson

A lesson is complete when:

1. its source R material and statistical purpose are identified;
2. the Python translation is pedagogically faithful and idiomatic;
3. the marimo notebook executes successfully;
4. key numerical/statistical behavior is verified;
5. important visualizations use Altair where appropriate;
6. meaningful differences from R are documented; and
7. the cumulative report identifies exactly one next chunk.

## Re-entry

Start with `reports/cumulative-report.md`. It is the canonical handoff across Codex sessions. Read recent commits for implementation detail and rationale.
