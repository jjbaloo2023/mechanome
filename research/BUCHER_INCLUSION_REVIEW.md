# Independent review: Bucher EM inclusion reconciliation

**Task:** `bucher-inclusion-review-001`, attempt 1 (2026-09-26). I checked the preregistered [design](bucher_inclusion_design.json), the preserved [package audit](bucher_inclusion_package_001.json) and its [reader](check_bucher_inclusion.py), the bounded [source note](BUCHER_INCLUSION_SOURCE.md), and the earlier [EM contract](BUCHER_EM_CONTRACT.md). This review concerns deposited-area inclusion and sampling provenance only. It makes no morphology effect estimate or mechanical inference.

## Disposition

**Accept an unresolved count discrepancy and stop Fig. 1/Fig. 7 reproduction.** A reconciliation would require an explicit source rule linking the visually counted caption structures to the workbook area entries, or a demonstrated package-reading error whose correction restores the counts. Neither was found within the frozen two-workbook and named-supplement scope. A plausible reason for fewer entries is not an identified reason.

The package worker rechecked exact registered byte length, publisher MD5 and prior SHA-256 for both cached XLSX files. Its ZIP/XML parser separately classifies numeric, text, blank, boolean and error cells; it requires each counted area to be finite and positive. It records first/last numeric rows, internal gaps and trailing padding, plus hidden rows/columns, formulas, comments and defined names. I inspected the code path and group summaries: all counted values satisfy the numeric gate, no group has an internal missing row, and zero formulas are present. Shorter morphology columns have trailing padding, which cannot be converted into omitted structures. No inspected package metadata supplies an inclusion rule.

| Source block | Deposited positive-area entries | Published caption structures | Difference |
| --- | --- | --- | --- |
| Fig. 1, three baseline membranes | 735, 857, 726 | 746, 869, 739 | 11, 12, 13 |
| Fig. 7, four normal membranes | 257, 299, 226, 321 | 267, 308, 229, 323 | 10, 9, 3, 2 |
| Fig. 7, four shock membranes | 390, 95, 347, 200 | 395, 99, 351, 201 | 5, 4, 4, 1 |

The source worker retrieved only the named 18-page [supplement](https://static-content.springer.com/esm/art%3A10.1038%2Fs41467-018-03533-0/MediaObjects/41467_2018_3533_MOESM1_ESM.pdf), 972,260 bytes under the registered limit, and recorded its SHA-256 in [BUCHER_INCLUSION_SOURCE.md](BUCHER_INCLUSION_SOURCE.md). The [primary article](https://www.nature.com/articles/s41467-018-03533-0) Fig. 1/7 captions provide the published totals. The supplement does not identify the workbook entries or map them to those totals. Its pp. 10–13 thresholds/exclusions concern fluorescence-derived model histograms and tracks; p. 16 discusses a fluorescence-track calculation. Neither establishes an EM area-entry inclusion rule. The main-text CLEM multiple-structure exclusion also cannot be assigned to the EM workbooks without explicit linkage. Thus an unmeasured-area, different-subset or omitted-category explanation remains a hypothesis, not a reconciliation.

Cell/membrane blocks are the available grouping labels; individual area rows are structures within them. The repeated Control and shock `Cell 1–4` labels do not prove matched pre/post membranes, and destructive unroofed EM cannot follow one membrane through both conditions. Distinct labeled membranes also do not establish independent cultures or experimental days. No figure-level percentages, p-values or model fits should be computed as a claimed reproduction. Any future description of deposited entries must use deposited denominators and state that selection relative to caption counts is unknown.

## Separate next-direction advice

A partial-identification bound for omitted morphology categories would be informative only if evidence first established that deposited entries are a subset of the caption population, with known mutually exclusive category definitions and exactly the caption-minus-entry omissions in each membrane. That containment link is absent. Using caption totals as denominators now would assume the answer to this audit, so I do **not** recommend that follow-up on current evidence.

A separate bounded theory task could test whether the exact curvature/traction nullspace from the **linear shallow** operator survives a nonlinear Helfrich model under two known tensions. It should freeze material versus projected source coordinates, load direction/work and balancing reaction, membrane boundary, known rigidity and invariant source fields, then derive an explicit surviving symmetry or first order at which the gauge splits on one regular branch. No nonlinear solver, Gaussian sweep or empirical promotion is warranted by this suggestion. The present Bucher/Saleem records do not enable a calibrated finite-dimensional curvature-versus-load comparison.
