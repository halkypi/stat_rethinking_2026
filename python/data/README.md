# Howell1 source data

`Howell1.csv` is copied unchanged from Richard McElreath's **rethinking** package.
[Immutable source](https://raw.githubusercontent.com/rmcelreath/rethinking/4b523cc4e75ab2aacd4c989b89f73b2f2e63da84/data/Howell1.csv).
`Howell1.provenance.json` records the source revision, retrieval date and SHA-256.
The loader checks the digest before use; lessons never download data at runtime.

The package documentation credits **Nancy Howell**, describes demographic data
from Kalahari !Kung San people, and cites the
[University of Toronto data source](https://tspace.library.utoronto.ca/handle/1807/10395).
The four CSV columns are height (cm), weight (kg), age (years) and the source's
binary `male` indicator. Adult analyses retain age >= 18: 352 of 544 rows.

The upstream package DESCRIPTION specifies **GPL (>= 3)**. This vendored file
retains upstream terms; the repository's CC0 dedication does not relicense it.
A copy of GPL version 3 is included in `COPYING-GPL-3.txt`.
