# Statistical Rethinking Python Companion — Parallel Wave Orchestrator

You are the orchestrator and integration implementor for the existing Statistical Rethinking Python companion project.

Repository: `halkypi/stat_rethinking_2026`

Canonical integration branch:

`agent/cortex-python-companion`

The project has already completed Session S1 from the remaining-work roadmap. Your job is now to organize the next parallel wave of work without weakening the project's existing statistical, verification, provenance, or Git standards.

Do **not** begin the three workers' implementation during this setup pass.

## 1. Orient from repository evidence

Before making recommendations, inspect:

- root `README.md`;
- `python/README.md`;
- `python/prompts/001-python-port.md`;
- `python/prompts/002-remaining-work-orchestrator.md`;
- `python/reports/cumulative-report.md`;
- `python/reports/remaining-work-roadmap.md`;
- recent Git history on `agent/cortex-python-companion`;
- current `python/notebooks/`, `python/checks/`, `python/src/`, dependency/runtime files;
- the R/Stan sources relevant to candidate roadmap sessions;
- current Git status and existing worktrees.

Treat the cumulative report as the execution spine and the Git commits as detailed implementation memory.

Preserve the original R/Stan material.

## 2. Recommend the first parallel wave

Choose the best **three roadmap sessions** to run concurrently.

The current expected candidates are:

- S2 — B-spline regression + elemental confounds / WaffleDivorce;
- S4 — MCMC mechanics + ESS/ACF diagnostics;
- S5 — binomial/Poisson GLMs + sensitivity.

These are candidates, not an instruction to ignore repository evidence. Confirm that they remain sufficiently independent from the current tip. If a different set of three gives cleaner dependency separation or materially lower integration risk, explain and use that instead.

For each candidate, evaluate:

- conceptual dependencies on previous sessions;
- shared helper/runtime/dependency needs;
- likely overlapping files;
- expected branch merge risk;
- whether another worker is likely to establish infrastructure it should reuse;
- whether the session is small enough to remain coherent within one worker context.

Do not parallelize strongly serial chains merely to maximize concurrency.

## 3. Branch and worktree model

Each worker must have:

- its own branch;
- its own sibling Git worktree;
- its own prompt;
- its own plan file;
- its own final worker report.

All worker branches must start from the current tip of:

`agent/cortex-python-companion`

Use descriptive names such as:

- `agent/cortex-s2`
- `agent/cortex-s4`
- `agent/cortex-s5`

Use sibling worktrees such as:

- `../statrethinking-s2`
- `../statrethinking-s4`
- `../statrethinking-s5`

Do not reset, repurpose, or alter the canonical integration worktree while creating the workers.

Before creating anything, inspect existing branches/worktrees and avoid collisions. If names already exist, resolve them conservatively and document what you did.

## 4. Worker prompt protocol

Write one self-contained worker prompt per worktree under:

`python/prompts/parallel/`

For example:

- `python/prompts/parallel/wave-01-s2.md`
- `python/prompts/parallel/wave-01-s4.md`
- `python/prompts/parallel/wave-01-s5.md`

Each prompt must be tailored to its assigned roadmap session and must point the worker at the exact relevant R/Stan sources, current Python infrastructure, expected outputs, and validation responsibilities.

Every worker prompt must require two phases.

### Phase 1 — plan only

The worker must:

- orient from repository evidence;
- inspect every R/Stan/Python source relevant to its assigned session;
- inspect reusable helpers and existing tests;
- identify exact implementation artifacts;
- identify its validation/oracle strategy;
- identify required data/dependencies;
- identify any proposed shared infrastructure;
- identify likely conflicts with the other workers;
- write a plan to a unique file such as:

  `python/reports/parallel/wave-01/s2-plan.md`

- commit the plan;
- **STOP**.

It must not implement the lesson during Phase 1.

Scott will review the plan and explicitly authorize Phase 2.

### Phase 2 — implementation

After Scott approves the plan, the worker must:

- implement only its assigned scope;
- preserve upstream R/Stan files;
- follow existing marimo/PyMC/ArviZ/Altair/uv conventions;
- preserve existing verification standards;
- create focused checks and independent validation appropriate to the model;
- commit coherent verified increments frequently;
- avoid editing canonical shared state unless genuinely required;
- write a final report to a unique file such as:

  `python/reports/parallel/wave-01/s2-report.md`

The report must include:

- scope completed;
- source files accounted for;
- artifacts created/changed;
- statistical results;
- verification performed;
- dependencies added;
- shared infrastructure changed or proposed;
- unresolved issues;
- commit SHAs;
- integration notes.

The worker must commit its report and stop.

## 5. Shared-file rules

Parallel workers should avoid editing these unless absolutely necessary:

- `python/reports/cumulative-report.md`;
- `python/reports/remaining-work-roadmap.md`;
- `python/README.md`;
- common runtime configuration;
- shared dependency files;
- shared package modules owned by another concurrent worker.

Prefer worker-owned notebooks, checks, helper modules, plans, and reports.

If a dependency or common helper must change, the worker should make the smallest justified change and call it out prominently in its plan/report.

Workers must **not independently update the cumulative report**. The integration orchestrator owns canonical project-state updates.

## 6. Coordination summary

Create:

`python/reports/parallel/wave-01/README.md`

It should show, for each worker:

- worker/session name;
- roadmap session;
- branch;
- worktree path;
- prompt path;
- plan path;
- final report path;
- relevant source files;
- dependencies on prior work;
- expected conflict/shared-file risks;
- recommended integration order.

Also include the exact two short messages Scott should paste into each worker:

### Initial worker handoff

`Read and execute <prompt path>. Phase 1 only. Write and commit your plan, then stop for my approval.`

### Implementation approval

`Approved. Execute Phase 2 exactly as defined in your plan and worker prompt. Implement, verify, commit the work, write your final worker report, and stop.`

## 7. Terminal helper script

Create a shell script such as:

`scripts/open-parallel-wave-01.sh`

Its job is to make launching the three workers easy on macOS.

The script should open one terminal window per worker worktree and, in each window:

- `cd` to the correct worktree;
- show `git branch --show-current`;
- print the worker prompt path;
- print the short Phase-1 handoff text Scott should give the agent.

Do **not** automatically launch or authorize an AI coding agent unless an existing local command and workflow are clearly documented and safe to use.

If the terminal application is not known with confidence, make the terminal choice configurable or document the expected default. If iTerm2 is clearly available, AppleScript support for iTerm2 is acceptable.

The script should fail clearly if a worktree is missing.

## 8. Integration role after workers finish

After the three workers complete Phase 2, Scott will return to this orchestrator/integrator.

At that point you must:

1. read all three worker reports;
2. inspect every worker branch and its commits;
3. review statistical and implementation quality before merging;
4. identify shared/dependency conflicts;
5. merge or cherry-pick one worker branch at a time into `agent/cortex-python-companion`;
6. reconcile dependencies and shared infrastructure centrally;
7. run aggregate verification after each integration;
8. fix integration issues where appropriate;
9. update canonical project state:
   - `python/reports/cumulative-report.md`;
   - `python/reports/remaining-work-roadmap.md` if materially changed;
   - `python/README.md` when appropriate;
10. commit the integrated state;
11. recommend the next parallel wave.

Do not mark a worker complete merely because it produced code. Review its statistical validation, diagnostics, and tests first.

## 9. Deliverables for this setup pass

Before stopping, ensure all of these exist:

- three worker branches;
- three sibling worktrees;
- three tailored worker prompts;
- `python/reports/parallel/wave-01/README.md`;
- `scripts/open-parallel-wave-01.sh`;
- a descriptive setup commit on the canonical integration branch where appropriate.

Do not start Phase 1 for the workers yourself.

## 10. Final response and stop condition

When setup is complete, report succinctly:

- the three chosen roadmap sessions;
- branch and worktree for each;
- prompt path for each;
- coordination summary path;
- terminal helper path;
- any important dependency/conflict notes;
- commit SHA(s).

Then **STOP** so Scott can launch the three workers and review their plans before implementation begins.