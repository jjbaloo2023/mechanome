# Independent review: Bucher EM workbook contract

**Task:** `bucher-em-contract-review-001`, attempt 1, 2026-09-26. I reviewed the preregistered [design](bucher_em_contract_design.json), [inventory](bucher_em_contract_001.json), and [reader](inspect_bucher_em_contract.py) against Bucher et al. 2018 [Fig. 1 and Fig. 7 captions](https://www.nature.com/articles/s41467-018-03533-0). This is a schema and sampling-unit review only. I did not run an effect estimate, statistical test, trajectory fit or membrane model.

## Disposition

**Accept the byte-verified inventory as a public processed-data contract; defer descriptive reproduction.** Both Figshare Excel files have the registered exact byte lengths and publisher MD5s, and local SHA-256s are saved. The reader opens ZIP/XML content, inventories sheets/labels/nonempty cells, and records zero formulas; it does not execute workbook logic. The two files are **not** two condition arms. `EM BSC-1.xlsx` has three `Cell` blocks under a projected-area `(nm²)` header. `EM BSC-1 osmotic shock.xlsx` contains **both** `Control` and `osmotic shock`, each with four `Cell` blocks and Flat/Dome/Pit columns. Grouping by filename would be wrong.

For the shock workbook, subtracting header text cells from each morphology column's nonempty count gives the following **apparent data-entry inventory**, not a verified biological count:

| Condition | Cell 1 | Cell 2 | Cell 3 | Cell 4 |
| --- | ---: | ---: | ---: | ---: |
| Control entries | 257 | 299 | 226 | 321 |
| Shock entries | 390 | 95 | 347 | 200 |
| Fig. 7 caption, normal | 267 | 308 | 229 | 323 |
| Fig. 7 caption, shock | 395 | 99 | 351 | 201 |

The Fig. 7 caption counts are systematically above the simple workbook-entry counts. The separate baseline workbook likewise has 735, 857 and 726 apparent data entries in its three blocks, versus 746, 869 and 739 structures stated in the Fig. 1 caption. These discrepancies could reflect exclusions, absent projected-area values, a different figure subset, or another mapping; none is established by the inventory or independent [count record](bucher_em_contract_counts_001.json). The multiple-structure exclusion in the primary article concerns CLEM and cannot explain the EM deficit without explicit linkage. Source provenance is needed before assigning a reason or reproducing published percentages.

The `Cell 1` labels on the two sides of the shock workbook do not prove that the same membrane was imaged twice. TEM follows destructive unroofing, and the primary figure describes four membranes per condition without a pair key in this inventory. Each cell/membrane block is a candidate sampling unit, while rows within a block are structures, not independent biological replicates. Condition/date/culture linkage and exclusion rules remain unverified. Empty cells after the last value in shorter morphology columns are ordinary column padding; the inventory alone cannot tell whether internal blanks or other missing values matter. The independent read has not validated units row by row, numeric finiteness, or biological labels against original images.

The next permitted step is a bounded provenance check of package metadata and the linked 949-kB supplement for an explicit Fig. 1/Fig. 7 inclusion rule. If unresolved, retain the count discrepancy and stop figure reproduction; any deposited-entry description must use its own denominators and unknown-selection label. Only after reconciliation could one decide whether a descriptive morphology/area comparison is reproducible. No tension or rigidity calibration, registered membrane height profile, preferred-curvature source or spatial pit traction/reaction is supplied here. This contract therefore does not change the stopped curvature-versus-balanced-load inference decision in [INDEPENDENT_CONTROLS_REVIEW.md](INDEPENDENT_CONTROLS_REVIEW.md).
