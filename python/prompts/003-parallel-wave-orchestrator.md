# Statistical Rethinking Python Companion — Manual Parallel-Wave Orchestrator

You are the **orchestrator and later integrator** for the existing Statistical Rethinking Python companion project.

Repository: `halkypi/stat_rethinking_2026`

Canonical integration branch:

`agent/cortex-python-companion`

The project has completed Session S1 from the remaining-work roadmap.

Your job in this pass is to determine which remaining roadmap sessions can safely run in parallel, prepare the Git branches/worktrees and worker prompts, and then hand control back to Scott.

**You do not run, launch, supervise, or implement the worker sessions. Scott will start each worker manually in a separate agent session.**

After those workers finish, Scott will return to you. You will then review their work, integrate it into the canonical branch, clean up the worktrees, and recommend the next wave.

Do not begin any worker implementation during this setup pass.

## 1. Orient from repository evidence

Before choosing workers, inspect:

- root `README.md`;
- `python/README.md`;
- `python/prompts/001-python-port.md`;
- `python/prompts/002-remaining-work-orchestrator.md`;
- `python/reports/cumulative-report.md`;
- `python/reports/remaining-work-roadmap.md`;
- recent Git history on `agent/cortex-python-companion`;
- current `python/notebooks/`, `python/checks/`, `python/src/`, dependency/runtime files;
- the R/Stan sources relevant to candidate roadmap sessions;
- current Git status, branches, and worktrees.

Treat the cumulative report as the execution spine and Git commits as detailed implementation memory.

Preserve the original R/Stan material.

## 2. Decide what can run in parallel

Select the best **three roadmap sessions** that can run concurrently with minimal dependency and merge risk.

The previous candidate set was:

- S2 — B-spline regression + elemental confounds / WaffleDivorce;
- S4 — MCMC mechanics + ESS/ACF diagnostics;
- S5 — binomial/Poisson GLMs + sensitivity.

These are suggestions only. Re-evaluate them against the actual current repository state.

For every candidate you consider, assess:

- conceptual dependency on earlier roadmap sessions;
- whether another candidate is expected to establish machinery it should reuse;
- overlapping notebooks/checks/helpers;
- likely shared dependency changes;
- likely merge conflicts;
- whether the scope is coherent for one worker context;
- whether delaying it until a later wave would materially simplify the work.

Prefer three workers that are **truly independent enough to be useful in parallel**, not merely three numerically separate roadmap entries.

Do not parallelize known serial chains simply to maximize concurrency.

## 3. Create branches and worktrees

Once you have selected the three workers, prepare them for Scott.

Each worker must have:

- its own branch;
- its own sibling Git worktree;
- its own tailored prompt;
- its own plan path;
- its own final report path.

All worker branches must start from the current tip of:

`agent/cortex-python-companion`

Use descriptive branch names based on the selected roadmap sessions, for example:

- `agent/cortex-s2`
- `agent/cortex-s4`
- `agent/cortex-s5`

Use sibling worktrees, for example:

- `../statrethinking-s2`
- `../statrethinking-s4`
- `../statrethinking-s5`

Before creating anything, inspect existing branches and worktrees and avoid collisions.

Do not reset or repurpose the canonical integration worktree.

Actually create the branches and worktrees during this setup pass. Do not merely recommend commands for creating them unless a local constraint prevents you from doing so.

## 4. Write one worker prompt per worktree

Create a self-contained worker prompt under `python/prompts/parallel/` for each selected worker, for example:

- `python/prompts/parallel/wave-01-s2.md`
- `python/prompts/parallel/wave-01-s4.md`
- `python/prompts/parallel/wave-01-s5.md`

Each prompt must be tailored to its assigned roadmap session and identify:

- the exact R/Stan source files to inspect;
- relevant existing Python artifacts and helpers;
- intended pedagogical scope;
- expected notebook/check/helper artifacts;
- validation and independent-check expectations;
- likely data/dependency needs;
- shared-file restrictions;
- final worker-report path.

The worker prompt must use a two-stage human-in-the-loop protocol.

### Worker Phase 1 — plan only

The worker must:

- orient from repository evidence;
- inspect all relevant R/Stan/Python sources;
- produce an implementation plan;
- identify exact artifacts to create/change;
- state its validation/oracle strategy;
- identify dependency or shared-infrastructure needs;
- identify likely integration conflicts;
- identify any computation expected to take long enough that Scott should run it externally;
- write the plan to its unique plan file;
- commit the plan;
- **STOP and wait for Scott**.

It must not implement during Phase 1.

### Worker Phase 2 — implementation after Scott approves

Once Scott manually approves the plan, the worker must:

- implement only the approved assigned scope;
- preserve upstream R/Stan files;
- follow existing marimo/PyMC/ArviZ/Altair/uv conventions;
- preserve current statistical verification standards;
- make frequent coherent commits;
- avoid unnecessary edits to canonical shared state;
- use the long-running-computation handoff protocol below when appropriate rather than sitting idle waiting for expensive jobs;
- write and commit its final worker report;
- STOP.

The final report must contain:

- scope completed;
- source files accounted for;
- artifacts created/changed;
- statistical results;
- verification performed;
- dependencies added;
- shared infrastructure changed or proposed;
- unresolved issues;
- commit SHAs;
- integration notes;
- any externally run long computations, their commands, outputs, and evidence inspected.

## 5. Long-running computation handoff — project-wide principle

Scott prefers to run and monitor long computations himself rather than have an agent spend its context waiting for them.

Apply this principle throughout this wave and future waves.

When a worker reaches a computation that is expected to be materially long-running—such as heavy sampling, many-replication validation, large exports, expensive GP/phylogenetic/ODE/HMM fits, or other jobs where the agent would mostly wait—it should prepare a **fire-and-forget handoff** instead of polling or blocking unnecessarily.

The worker must:

1. finish and commit all code/configuration needed to launch the job;
2. provide Scott with exact shell command(s) to run from the worker worktree;
3. make the command write durable outputs to ignored or designated artifact paths, including enough of:
   - stdout/stderr log;
   - diagnostics/summary JSON or text;
   - posterior/sample artifact if needed for later inspection;
   - deterministic metadata such as seed/configuration/version where relevant;
4. state how Scott can tell the process is still running and how to tell it completed successfully;
5. state the exact file(s) the worker will inspect when Scott returns;
6. STOP rather than repeatedly polling the process.

Scott will run/monitor the command and tell the worker when it has completed.

When Scott returns, the worker must inspect the persisted artifacts and continue verification from those results. Do not rerun an expensive job merely because the agent session resumed unless the inputs/configuration changed or the artifacts are incomplete/corrupt.

For short computations, normal autonomous execution is fine. Use judgment; this is a principle to avoid wasting agent context on waiting, not a rigid time threshold.

Workers should include any anticipated long-run handoff in Phase 1 so Scott knows in advance where the session may pause.

## 6. Shared-state rules for workers

Parallel workers should avoid editing these unless absolutely required:

- `python/reports/cumulative-report.md`;
- `python/reports/remaining-work-roadmap.md`;
- `python/README.md`;
- shared runtime configuration;
- shared dependency files;
- shared package modules another concurrent worker is also likely to modify.

Prefer worker-owned notebooks, checks, helper modules, plans, and reports.

Workers must not independently update the cumulative report. The integration orchestrator owns canonical project-state updates.

If a worker genuinely needs a shared dependency or common helper change, it may make the smallest justified change, but it must flag that prominently in both its plan and final report.

## 7. Coordination record

Create:

`python/reports/parallel/wave-01/README.md`

For each worker record:

- roadmap session/scope;
- branch;
- worktree path;
- worker prompt path;
- plan path;
- final report path;
- relevant source files;
- dependencies;
- expected shared-file/merge risks;
- likely long-running computations and expected fire-and-forget handoff points;
- recommended eventual integration order.

This document is for durable project coordination. It does not launch anything.

## 8. What Scott should do manually

Scott will open three separate agent sessions himself.

Your final response must make that easy.

For **each worker**, provide exactly:

1. the shell command(s) Scott should run to enter/verify the prepared worktree, for example:

   ```bash
   cd ../statrethinking-s2
   git branch --show-current
   ```

2. the short initial handoff Scott should paste into that worker session, for example:

   ```text
   Read and execute python/prompts/parallel/wave-01-s2.md.
   Phase 1 only: write and commit your plan, then stop for my approval.
   ```

Also provide the short Phase-2 approval message Scott can paste back after reviewing a worker plan:

```text
Approved. Execute Phase 2 from your worker prompt and approved plan. Implement, verify, commit, write your final worker report, and stop. For any materially long-running computation, give me the fire-and-forget command/artifact handoff and stop so I can run and monitor it.
```

Do **not** create or require a terminal-launching script unless Scott separately asks for one.

Do not attempt to launch the workers yourself.

## 9. When Scott returns after all workers finish

The same orchestrator role becomes the integration implementor.

At that point:

1. read all worker plans and final reports;
2. inspect each worker branch and its commits/diffs;
3. review statistical and implementation quality before integrating;
4. identify dependency/shared-helper conflicts;
5. integrate one worker at a time into `agent/cortex-python-companion` using merge or cherry-pick as appropriate;
6. reconcile dependencies and shared infrastructure centrally;
7. run aggregate verification after each integration and again at the end;
8. use the same fire-and-forget handoff principle for any materially long aggregate verification or integration computation;
9. fix integration issues where appropriate;
10. update canonical project state:
   - `python/reports/cumulative-report.md`;
   - `python/reports/remaining-work-roadmap.md` if materially changed;
   - `python/README.md` where appropriate;
11. commit the integrated state;
12. remove completed worker worktrees only after their branches are safely integrated and their reports/commits are preserved;
13. optionally delete local worker branches only when safe and justified;
14. recommend the next set of sessions that can run in parallel;
15. if another wave is appropriate, prepare its worktrees and prompts using the same protocol.

Do not treat a worker as complete merely because it produced code. Review its validation, diagnostics, source coverage, and integration consequences first.

## 10. Deliverables for this setup pass

Before stopping, ensure these exist:

- three selected worker scopes;
- three worker branches;
- three sibling worktrees;
- three tailored worker prompts;
- `python/reports/parallel/wave-01/README.md`;
- any canonical setup commit needed to preserve the prompts/coordination record.

No worker session should have been started by you.

## 11. Final response — keep it operational

Your final output should be concise and action-oriented.

First give one short sentence stating which three sessions were selected and why they are safe enough to parallelize.

Then, for each worker, give:

```text
Worker <name>
Worktree: <path>
Branch: <branch>
Prompt: <prompt path>

Commands:
<exact shell commands Scott should run>

Handoff:
<exact two-line Phase-1 handoff Scott should paste>
```

Then give the single shared Phase-2 approval message.

Finally state:

- where the coordination README lives;
- that Scott should return to this orchestrator after all three workers have completed Phase 2;
- that you will then review, integrate, verify, clean up the worktrees, update canonical reports, and recommend the next wave.

Then **STOP**.