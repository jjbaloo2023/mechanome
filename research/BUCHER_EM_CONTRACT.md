# Bucher EM workbook contract: partial and unresolved

Both registered files passed their exact publisher byte lengths and MD5 checks. SHA-256, UTC access times, resolved URLs, workbook labels and column populations are saved in the [inventory](bucher_em_contract_001.json). Retrieval used 150,878 bytes total; cached payloads are ignored by Git. No formulas were present or executed. The [design](bucher_em_contract_design.json) preceded retrieval; the [inspector](inspect_bucher_em_contract.py) reads ZIP/XML without running spreadsheet content.

**The osmotic-shock workbook contains both experimental arms.** Its Sheet1 labels Control Cells 1-4 and osmotic shock Cells 1-4, each with Flat/Dome/Pit projected areas in nm^2. Repeated cell numbers do not establish paired samples. Columns are separate lists, not matched pits. The separate EM BSC-1 workbook contains three cell blocks and must not silently supply Fig. 7's control arm.

| Arm | Deposited entry totals, Cells 1-4 | Fig. 7 caption totals | Difference |
| --- | --- | --- | --- |
| Control | 257, 299, 226, 321 | 267, 308, 229, 323 | 10, 9, 3, 2 |
| Osmotic shock | 390, 95, 347, 200 | 395, 99, 351, 201 | 5, 4, 4, 1 |

The [count record](bucher_em_contract_counts_001.json) derives totals by subtracting header text cells from nonempty column entries. Caption counts were checked against the [primary Fig. 7](https://www.nature.com/articles/s41467-018-03533-0#Fig7). **The counts do not exactly reproduce the figure's stated sample sizes.** This is an unresolved inclusion/mapping discrepancy, not evidence of an error in the paper or a biological effect. The main-text multiple-structure exclusion belongs to CLEM; it does not establish why these EM area totals differ. Workbook labels do not identify exclusions, independent experimental days or unique cross-file membrane identities.

Stop this stage at the reviewed sampling contract. Do not calculate morphology effects, p-values, trajectories or mechanical fits from it. Next: one bounded provenance reconciliation of package metadata and the paper's linked 949-kB supplement for an explicit inclusion/count explanation. If unresolved, retain the discrepancy and stop figure reproduction; any later deposited-entry description must use its actual denominators and explicitly unknown selection. Do not combine files or assume biological independence from repeated cell labels.

[Independent review](BUCHER_EM_CONTRACT_REVIEW.md) records the acceptance boundary. The broader [controls assessment](INDEPENDENT_CONTROLS_FINDINGS.md) remains unchanged.
