# Statistical Rethinking Python Companion — Remaining-Work Orchestrator

You are taking over an existing multi-session project in:

`halkypi/stat_rethinking_2026`

Current working branch:

`project/python-companion`

Your first role is **Orchestrator / Planner**, not implementation agent.

The project already has substantial completed work. Do not restart it, redesign it from scratch, or assume the original R-file count equals the remaining Python lesson count.

Your immediate task is to reconstruct the project from repository evidence, inventory all remaining R → Python work, estimate how many future coding sessions will be required, and leave a durable execution roadmap.

Do **not** begin translating Week 4 until the planning pass is complete.

## Internet access

Internet access is **not required for this planning pass**.

Base the inventory, complexity assessment, and session estimates on repository evidence. Do not browse for external Python ports, solutions, tutorials, or equivalent implementations during this pass.

If you encounter something that genuinely cannot be assessed without external research, flag it explicitly as a planning uncertainty and identify what would need to be researched later. Do not consume the planning session resolving it on the web.

## 1. Reconstruct the project from repository state

Before making any planning judgment, read:

1. repository instructions such as `AGENTS.md`, `CLAUDE.md`, or equivalent, if present;
2. root `README.md`;
3. `python/README.md`;
4. `python/prompts/001-python-port.md`;
5. `python/reports/cumulative-report.md`;
6. the recent commit history on `project/python-companion`;
7. all current tracked material under:
   - `python/notebooks/`
   - `python/checks/`
   - `python/src/`
8. the dependency/runtime files under `python/`;
9. the complete upstream `scripts/` directory.

Inspect Git status first and preserve unrelated or uncommitted work.

The cumulative report is the durable project spine.

The Git commits are the detailed implementation memory. Read enough of their messages and diffs to understand the actual rate and difficulty of previous work.

Do not infer current state from filenames alone.

## 2. Understand what has already been established

Preserve the existing project principles unless repository evidence shows a problem:

- original R material remains untouched;
- marimo `.py` notebooks are the primary executable lesson format;
- Markdown is used for reports and project state;
- Altair is the default visualization tool where appropriate;
- NumPy / pandas / SciPy / PyMC / ArviZ form the statistical stack;
- `uv` owns the environment;
- statistical operations are translated, not R syntax mechanically;
- lessons are organized by distinct pedagogical concepts rather than blindly one Python file per R file;
- every completed lesson must execute and be independently verified;
- frequent descriptive commits preserve implementation context;
- cosmetic animations, slide styling, GIS, and redundant presentation code may be deferred when the statistical lesson is already preserved.

Do not weaken verification merely to increase apparent coverage.

## 3. Inventory the entire remaining source corpus

Inspect **every remaining R file** under `scripts/`.

Also inspect relevant `.stan` sidecars where they materially define the model being taught.

For each source file, determine its actual role.

Create an inventory with at least:

| Source | Course/track | Main concept | Already covered? | Action | Complexity | Dependencies |
|---|---|---|---|---|---|---|

`Action` must be one of:

- `translate`
- `extend-existing-lesson`
- `merge-with-related-source`
- `already-covered`
- `defer-presentation-only`
- `defer-duplicate`
- `needs-human-decision`

Do not treat filenames as independent work units if several scripts teach the same concept.

Likewise, do not declare something redundant without inspecting it.

Explicitly identify:

- duplicate or near-duplicate scripts;
- alternate lecture versions of the same concept;
- animation/presentation-only scripts;
- beginner vs experienced-track material;
- bonus material;
- source files whose statistical content is already represented in Python;
- source files that introduce genuinely new model families or validation requirements.

## 4. Distinguish scope tiers

Produce three scope tiers.

### Tier 1 — Core remaining pedagogical companion

Everything required to give Scott a coherent Python path through the main course material.

### Tier 2 — Experienced / advanced course material

Multilevel models, varying effects/slopes, networks, Gaussian processes, measurement error, missing data, HMMs, and other advanced material that belongs to the experienced track or later advanced sequence.

### Tier 3 — Optional fidelity / bonus material

Animations, duplicated lecture demonstrations, visual-only scripts, bonus examples, alternative implementations, or material that adds relatively little pedagogical value after a verified canonical lesson already exists.

Do not silently exclude Tier 3. Inventory it, explain why it is lower priority, and estimate it separately.

## 5. Estimate work using evidence, not intuition alone

Estimate the number of future coding sessions required.

A **session** means one fresh coding-agent context/credit allocation comparable to the sessions already used on this branch.

Calibrate the estimate from actual repository history:

- what Week 2 required;
- what Week 3 required;
- how many coherent concepts were completed per session;
- which commits involved simple deterministic translations;
- which required PyMC fitting, independent validation, runtime debugging, external data, or lengthy computation.

Do not extrapolate raw file counts linearly.

Classify each remaining work unit approximately as:

### S — small
Deterministic simulation, visualization, algebra, or extension of an established pattern.

### M — medium
One new model or concept using known translation/verification patterns.

### L — large
Several related fitted models, new likelihood/model family, causal simulation, or substantial independent validation.

### XL — research-heavy
Multilevel/GLMM architecture, Gaussian processes, networks, missing-data models, HMMs, measurement-error models, unfamiliar Stan logic, or work where faithful Python translation needs investigation before implementation.

Adjust these categories if inspection shows a better scheme.

## 6. Produce three session estimates

Give:

1. **Optimistic**
   - established patterns reuse cleanly;
   - no major runtime surprises;
   - closely related sources combine well.

2. **Expected**
   - normal debugging;
   - full verification;
   - sensible reuse of existing infrastructure.

3. **Conservative**
   - difficult model translations;
   - data/dependency issues;
   - additional validation or refactoring.

For each estimate, give:

- sessions remaining;
- approximate number of pedagogical lessons/chunks;
- major assumptions;
- the work most likely to dominate the estimate.

Do not pretend precision you do not have.

Use ranges where justified.

## 7. Build a proposed session roadmap

Create a sequence such as:

| Session | Proposed scope | Why grouped together | Main risk | Exit condition |
|---|---|---|---|---|

Each session should have a coherent pedagogical and implementation boundary.

Prefer grouping work where shared machinery reduces cost.

Examples:

- categorical means + contrasts;
- height-adjusted models / causal interpretation;
- DAG/confounding simulation;
- MCMC diagnostics;
- binomial GLMs;
- Poisson / ordered outcomes;
- introductory multilevel models;
- varying intercepts/slopes;
- networks;
- Gaussian processes;
- measurement error / missing data;
- HMM / remaining advanced material.

These are examples only. Derive the actual plan from the repository.

A session should not be overloaded simply to make the session count smaller.

## 8. Identify likely reuse opportunities

Determine which existing Python infrastructure should reduce future effort.

Inspect and report on reusable pieces such as:

- PyMC sampling helpers;
- diagnostic gates;
- posterior predictive helpers;
- exact/numerical validation patterns;
- Altair chart conventions;
- marimo interaction patterns;
- data vendoring/checksum conventions;
- runtime configuration;
- aggregate test runners.

Recommend refactoring only when it will clearly reduce repeated work across multiple future lessons.

Do not perform speculative architecture work during this planning pass.

## 9. Identify the critical path

State which remaining concepts are likely to be the largest technical jumps.

For each, explain why.

Examples may include:

- first non-Gaussian likelihood;
- first multilevel model;
- correlated varying effects;
- Gaussian processes;
- social/network models;
- measurement error;
- missing data;
- hidden Markov models.

Use the actual source code to decide.

## 10. Establish completion criteria for the whole port

Define what “R → Python conversion complete” should mean.

Distinguish:

### Pedagogically complete
Every distinct statistical concept in the upstream material has an executable, verified Python representation.

### Source-accounted
Every R/Stan source file appears in the inventory with an explicit disposition: translated, merged, already covered, or deliberately deferred.

### Fully faithful
Optional presentation, animation, or secondary variants are also reproduced.

The current project should target **pedagogically complete + source-accounted** unless Scott explicitly asks for full cosmetic fidelity.

## 11. Write a durable planning report

Create:

`python/reports/remaining-work-roadmap.md`

It should contain:

1. current state;
2. source inventory;
3. scope tiers;
4. complexity assessment;
5. optimistic / expected / conservative session estimates;
6. recommended session roadmap;
7. critical-path risks;
8. reuse opportunities;
9. completion definition;
10. exactly one recommended next implementation session.

Keep `python/reports/cumulative-report.md` as the execution spine.

Do not duplicate its historical detail into the roadmap.

The roadmap answers:

> How much remains, how should it be grouped, and how many coding sessions are likely required?

The cumulative report answers:

> What has actually been completed and what is the next verified chunk?

## 12. Commit the planning work

Scott has authorized frequent commits for this project.

For this planning pass:

- do not modify upstream R material;
- do not begin implementation;
- commit the roadmap once the inventory and estimate are internally consistent;
- use a descriptive commit message explaining the evidence and assumptions.

Suggested commit:

`plan: inventory remaining R corpus and estimate Python port sessions`

The commit body should summarize:

- files inspected;
- number of remaining distinct concepts;
- expected session range;
- major advanced-risk areas;
- declared next implementation session.

## 13. Final response

When finished, report succinctly:

- how much of the source corpus is already accounted for;
- how many distinct work units remain;
- optimistic / expected / conservative session counts;
- which areas dominate the remaining effort;
- the proposed next session;
- path to `python/reports/remaining-work-roadmap.md`;
- commit SHA.

Do not begin the next implementation session until Scott reviews the roadmap.