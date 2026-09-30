# Bucher 2018 inclusion-source reconciliation

**Task:** `bucher-inclusion-source-001`, attempt 1. Scope: the named primary article and its linked Supplementary Information PDF only; prior workbook-count records are cited only to state the unresolved comparison. No EM workbook payload was read by this source task.

## Bounded source provenance

- Supplement URL: `https://static-content.springer.com/esm/art%3A10.1038%2Fs41467-018-03533-0/MediaObjects/41467_2018_3533_MOESM1_ESM.pdf`
- Retrieved once at `2026-09-26T15:50:53.2758954Z`; 972,260 bytes (below the 1,100,000-byte bound); SHA-256 `f3b87301b3da66a5a7a5307cec79e43cd9f932065ef3865e82fd673dac43037d`; 18 pages. Cached only in ignored `research/.cache-bucher-reconcile-001/`. Text was extracted locally with bundled Python 3.12.14 and pypdf 6.10.0.

## Source-derived finding (134 words)

The main article's Fig. 1 caption reports three membrane counts of 746, 869, and 739 structures; Fig. 7 caption reports normal-condition counts of 267, 308, 229, and 323 and osmotic-shock counts of 395, 99, 351, and 201. The supplement does not name either set of EM workbook entries, reproduce those caption totals, or state an entry-level inclusion/exclusion mapping. Its explicit threshold/filter material applies to fluorescence-model analyses: a TEM detection threshold is used to restrict calculated FM-derived histogram points, and short-lived or multiple-intensity-maximum FM tracks are excluded (Supplement pp. 10-13, “Relate EM and FM datasets” and “Data filtering”). Supplement p. 16 calculates Fig. 7 morphology ratios from 1,356 FM tracks of one cell, which is separate from the destructive EM counts. Supplement pp. 2-5 describe live imaging from individual cells and a separate intact/unroofed STED comparison; they do not establish that labelled membranes are independent cultures, experimental days, or matched pre/post samples.

## Count reconciliation

| Published figure | Caption counts | Deposited-entry comparison already recorded | Explicit source mapping found here |
|---|---|---|---|
| Fig. 1 | 746, 869, 739 structures from three membranes | 735, 857, 726 apparent entries in the three baseline blocks | None in main text or supplement |
| Fig. 7 normal | 267, 308, 229, 323 | 257, 299, 226, 321 entries | None in main text or supplement |
| Fig. 7 osmotic shock | 395, 99, 351, 201 | 390, 95, 347, 200 entries | None in main text or supplement |

The cited entry counts are the prior structural records, not a new analysis. The primary Fig. 1/7 captions are the exact published locators. The supplement’s CLEM/FM filters cannot be assigned to EM tables without an explicit source link.

## Decision

**Unresolved discrepancy; stop published-figure reproduction.** The bounded supplement establishes no inclusion rule, missing-area convention, membrane-to-workbook mapping, or independence/culture mapping that reconciles the registered deposited totals with Fig. 1 or Fig. 7. A later descriptive analysis would need its own denominators and an unknown-selection caveat; it cannot be described as reproducing the figure or as a matched biological comparison.

## Exact source locators

- Primary article, Fig. 1 caption: three membrane counts; Results “EM analyses of CCSs do not support existing growth models.”
- Primary article, Fig. 7 caption: normal and osmotic-shock membrane counts; Results “Membrane tension influences the flat-to-curved transition.”
- Supplement PDF p. 2-5, Supplementary Figs. 1-2: cell/movie and intact/unroofed sampling descriptions.
- Supplement PDF pp. 10-13, “Relate EM and FM datasets” and “Data filtering”: model-track thresholds and exclusions, not an EM entry mapping.
- Supplement PDF p. 16, “Calculation of the ratio histogram during the osmotic shock”: 1,356 FM tracks from one cell for calculated Fig. 7 ratios.
