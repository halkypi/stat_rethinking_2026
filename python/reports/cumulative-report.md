# Python Port — Cumulative Report

## Goal

Build a faithful, executable Python companion to Statistical Rethinking 2026. Preserve McElreath's statistical reasoning and teaching sequence while using idiomatic modern Python, marimo for executable lessons, and Altair for visualization where appropriate.

The first milestone is one complete beginner lesson that Scott can step through and validate.

## Environment

Not established yet. The first implementation chunk should create the smallest `uv` environment needed for the selected lesson and record exact versions here.

Preferred stack:

- Python 3.13 where dependencies permit
- uv
- NumPy
- pandas
- SciPy
- PyMC
- ArviZ
- Altair
- marimo

## Progress

| Source | Python artifact | Status | Verification |
|---|---|---|---|
| Week 2 / `scripts/02_*` inventory | — | next | — |
| First Garden of Forking Data lesson | — | not-started | — |
| `scripts/02_globe_tossing_updating.r` | — | deferred | GIS/animation-heavy; not suitable as first chunk |

## Completed Work

### Project setup

- Established a Python companion project alongside, rather than replacing, the upstream R material.
- Chose marimo `.py` notebooks to keep executable lessons reviewable in Git.
- Chose Markdown for project state and cumulative reporting.
- Chose Altair as the default visualization grammar for translated teaching plots where it is a good semantic fit.
- Established this report as the durable project spine across sessions; detailed implementation context belongs in frequent descriptive commits.

## Shared Translation Patterns

None established yet. Add mappings only after they have been exercised in real translations.

## Known Issues / Deferred Fidelity

- `rethinking` abstractions will not always have one-to-one Python equivalents; translate the statistical operation rather than mimicking API names.
- Sampling results need statistical/qualitative equivalence, not bit-for-bit equality with R.
- Exact reproduction of incidental slide styling, animation, fonts, or colors is not a priority.
- The globe-tossing animation combines Bayesian updating with GIS, custom globe projection, animation, and platform-specific graphics. Preserve its statistical lesson later without requiring exact presentation parity.

## Next Chunk

Complete one beginner lesson from Week 2 / Garden of Forking Data.

1. Inventory the `scripts/02_*` R scripts.
2. Identify the smallest self-contained example that teaches Bayesian updating without GIS or animation.
3. Record why it was selected.
4. Establish the minimal `uv` environment.
5. Implement the lesson as a marimo `.py` notebook.
6. Use Altair for appropriate explanatory plots.
7. Execute the notebook and verify its numerical/statistical behavior.
8. Update this report with exact artifacts, versions, verification, translation decisions, and the next single chunk.

Do **not** begin with `02_globe_tossing_updating.r`.

## Re-entry Instructions

Read this report, inspect Git status and recent commits, inspect the source files named under **Next Chunk**, and continue from there. Do not redo completed chunks unless verification failed or new evidence shows the translation is incorrect.

At the end of every completed chunk, update this report before stopping. The repository must remain resumable without access to the previous chat session.