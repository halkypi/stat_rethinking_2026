# Statistical Rethinking 2026 — Python Companion Execution Prompt

You are working in Scott Halkyard's fork of Richard McElreath's `stat_rethinking_2026` repository.

Your task is to build a faithful, executable **Python companion** to the original R course materials.

This is a multi-session project. Assume that your context or execution credits may disappear at any time. Optimize for safe incremental progress and extremely cheap re-entry.

## First: orient yourself

Before changing anything:

1. Read any repository `AGENTS.md` or equivalent instructions if present.
2. Read the repository `README.md`.
3. Read `python/README.md`.
4. Read `python/reports/cumulative-report.md`.
5. Inspect recent commits on the current project branch. The cumulative report is the spine; commits contain detailed implementation memory and rationale.
6. Inspect the original R scripts relevant to the next incomplete section.
7. Inspect Git status/diff and preserve unrelated work.

Treat the original `scripts/` and `homework/` material as upstream reference material. **Do not modify McElreath's original R files merely to make the Python port easier.**

## Objective

Translate the pedagogically useful R material into idiomatic modern Python while preserving:

- the statistical meaning;
- McElreath's teaching sequence;
- model assumptions;
- simulations;
- important plots;
- prior and posterior predictive checks;
- causal/statistical reasoning;
- enough correspondence to the R source that a learner can compare them.

This is **not** a mechanical R-to-Python transliteration.

Prefer Python that teaches the same statistical idea naturally.

The immediate milestone is to **finish at least one beginner lesson end-to-end so Scott can step through and validate it**. Do not broaden scope until that vertical slice works.

## Python stack

Prefer:

- Python 3.13 where dependencies permit;
- `uv` for environment/dependency management;
- NumPy;
- pandas;
- SciPy;
- PyMC;
- ArviZ;
- **Altair**;
- marimo.

Use Altair as the default plotting library for explanatory/statistical visualizations where its declarative grammar is a good fit. Use another plotting mechanism only when Altair materially impairs fidelity or clarity, and document why.

Add another dependency only when it materially improves fidelity or clarity.

Do not introduce Jupyter `.ipynb` notebooks unless Scott explicitly requests them. Their nested JSON makes review and Git diffs unnecessarily difficult.

## Executable artifact format

Use **marimo `.py` notebooks** for interactive lessons and executable walkthroughs.

Use ordinary `.py` modules when code is better represented as reusable library/helper code.

Use Markdown for documentation and reports.

A translated notebook is not complete merely because it looks plausible. Execute it.

## Work in chunks

Never attempt to port the entire repository in one pass.

At the start of each session, determine the **smallest coherent next chunk** from the cumulative report.

A chunk should normally be one of:

- one small R script;
- a tightly related group of small scripts;
- one pedagogical concept within a lecture/week;
- one shared helper required by the next translations.

Prefer completing and verifying a small chunk over partially translating a large one.

Work broadly in the course's pedagogical order unless dependencies make a different order clearly better.

## For each source script

Before translating it, identify:

1. What statistical concept is being taught?
2. Which parts are pedagogically essential?
3. Which R/rethinking features are implementation details?
4. What is the idiomatic Python equivalent?
5. What numerical or graphical behavior can be used to verify fidelity?

Then implement the Python version.

Where `rethinking` abstractions such as `quap`, `ulam`, `PI`, posterior simulation, or helper plotting functions do not have exact Python equivalents, translate the **statistical operation**, not the function name.

Document meaningful differences.

## Verification

Every completed chunk must be executed.

At minimum verify, as applicable:

- the file imports/runs successfully;
- marimo can execute the lesson without hidden notebook state;
- simulations have the expected qualitative behavior;
- dimensions/shapes are correct;
- model sampling completes;
- diagnostics are acceptable for the teaching example;
- posterior summaries are sensible;
- important plots are produced;
- seeded computations are reproducible where appropriate;
- results are statistically consistent with the R example where direct comparison is meaningful.

Do not require floating-point or sampling output to exactly equal R.

When equivalence cannot be verified, mark the chunk incomplete and explain why.

## Fidelity over cosmetic parity

Do not spend disproportionate effort reproducing incidental slide graphics, fonts, colors, animation effects, or R-specific presentation machinery.

For unusual material such as GIS, animation, or custom graphics:

1. preserve the statistical lesson first;
2. implement a simpler Python visualization if that communicates the same idea;
3. record the fidelity difference;
4. defer exact visual parity unless it is pedagogically important.

## Cumulative report — mandatory checkpoint

After **every completed chunk**, update:

`python/reports/cumulative-report.md`

This file is the canonical machine/human handoff for the port. It is the project spine, not a verbose implementation diary. Put detailed implementation reasoning, discoveries, and context in descriptive Git commits.

The report must be cumulative, not merely a report of the latest session.

Maintain at least these sections:

### Goal
Short statement of the project goal.

### Environment
Python version, uv/PyMC/ArviZ/Altair/marimo versions and important setup information.

### Progress

Use a table:

| Source | Python artifact | Status | Verification |
|---|---|---|---|

Use explicit statuses: `not-started`, `in-progress`, `complete`, `blocked`, `deferred`.

### Completed Work

For every completed chunk, cumulatively record:

- source R file(s);
- Python artifact(s);
- statistical concept;
- important translation decisions;
- verification performed;
- known differences from R.

Do not delete earlier completed-work entries when adding a new one.

### Shared Translation Patterns

Record reusable mappings discovered during real work, for example:

- R/rethinking idiom → Python/PyMC/ArviZ idiom;
- Altair plotting conventions;
- posterior extraction;
- predictive simulation;
- interval calculation;
- data-loading conventions.

### Known Issues / Deferred Fidelity

Maintain a cumulative list of unresolved issues, deliberate simplifications, expensive graphics, dependency problems, or questionable translations.

### Next Chunk

Name exactly one recommended next chunk, including source file(s), concept, why it is next, prerequisites, and expected verification.

### Re-entry Instructions

Keep a short stable instruction telling a fresh session to read the report, recent commits, Git status, and the source named under Next Chunk before continuing.

## README state

After completing a meaningful course section/week, update `python/README.md` with high-level progress.

Do not turn the README into a session log. Detailed history belongs in commits; durable cumulative state belongs in the report.

## Commits are project memory

**Commit frequently after coherent, verified increments.** Scott has explicitly authorized commits for this project.

Use descriptive commit messages that preserve why the change was made, not just what files changed. A future agent should be able to inspect the commit history to recover implementation context that does not belong in the cumulative report.

Good examples:

- `project: establish Python companion workflow and re-entry contract`
- `week02: port grid approximation as executable marimo lesson`
- `week02: verify posterior normalization and Altair probability plot`
- `report: record Week 2 translation decisions and next chunk`

Prefer several coherent commits over one giant end-of-session commit. Do not commit broken intermediate states merely to increase commit count.

Scott reiterated a preference for more frequent commits on 2026-09-26. Commit independently useful, verified helpers, runtime fixes, and lesson extensions promptly instead of waiting for an entire lesson or session. Each commit should explain its verification and remaining scope; keep incomplete lessons explicitly incomplete in the report. A documentation-only checkpoint does not require rerunning unchanged statistical fits.

Never mix unrelated cleanup into a translation commit.

## Stop conditions

Stop the current chunk if:

- the R source's statistical intent is unclear;
- a required dependency creates substantial environment risk;
- faithful translation requires a major design decision;
- verification materially disagrees with the R behavior;
- completing the chunk would require unexpectedly broad changes.

Record the blocker in the cumulative report and stop rather than guessing.

## End of every run

Before ending—even if you have time remaining:

1. execute the newly translated code;
2. update the cumulative report;
3. ensure `Next Chunk` names exactly one resumption point;
4. make coherent descriptive commits for verified work;
5. summarize changed files, commits, and verification;
6. show Scott the result for validation.

The project should always be resumable from the repository alone without requiring the previous chat session.

## First execution target

For the first implementation session:

1. inventory `scripts/02_*`;
2. choose the smallest self-contained Garden of Forking Data example that demonstrates Bayesian updating without GIS or animation;
3. explain the choice in the cumulative report or commit context;
4. establish the minimal `uv` environment;
5. build a complete marimo lesson around it;
6. use Altair for the explanatory probability/posterior visualization where appropriate;
7. execute and verify the entire lesson;
8. commit coherent increments frequently;
9. update the cumulative report;
10. stop with a lesson Scott can actually step through.

Do **not** start with `scripts/02_globe_tossing_updating.r`.
