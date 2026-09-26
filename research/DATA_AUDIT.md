# Public dataset audit — 2026-09-19

The processed S-BIAD566 fit tables are accessible. All 23 files match the MD5
values in the public manifest. SHA-256 hashes, URLs, fields and per-file counts
are retained in [data_audit.json](data_audit.json). Total size: 379,676 bytes.
Raw localization data were not downloaded. These are local audit findings, not
an independent validation of the biological interpretations.

| Cell line | Tables | Deposited rows | Flagged disconnected | Kept by current adapter |
| --- | ---: | ---: | ---: | ---: |
| 3T3 | 7 | 739 | 51 | 680 |
| SKMEL2 | 13 | 1,798 | 153 | 1,631 |
| U2OS | 3 | 294 | 53 | 240 |
| Total | 23 | 2,831 | 257 | 2,551 |

## Findings from downloaded files and code

- Every table contains one file-number group, plus site IDs and cell-line labels.
  No duplicate `(cell_line, file_number, ID)` keys within tables were found.
  Treat file/cell groups as clusters; culture-level independence is unverified.
- All inspected geometry fields are finite. There are 23 negative raw curvature
  values: eight 3T3, fourteen SKMEL2, one U2OS. All have deposited corrected
  curvature zero and corrected angle 0.0001 degrees. The current adapter ignores
  corrected columns and removes these rows. This is a selection difference,
  particularly relevant to early flat structures, not proof of biased conclusions.
- The files contain no per-site standard-error or covariance fields. The adapter
  computes its own `H_sigma_inv_nm`; that must not be described as deposited fit
  uncertainty. Localization precision alone does not establish curvature error.
- Eighteen deposited `disconnected_sites` flags disagree with a direct application
  of the paper's cell-line thresholds to raw curvature. Preserve both the supplied
  flags and the discrepancy; do not silently regenerate labels.
- The existing fetch function reads but does not verify manifest MD5 values.
  The new audit verifies them before accepting cached or downloaded files.

## Methods and access checks

Mund et al.'s [institutional full text](https://research-explorer.ista.ac.at/download/14788/14811/2023_JCB_Mund.pdf),
printed pages 11–12, describes spherical-cap fitting, manual curation, flat-site
corrections and curvature-based population exclusions. Pseudotime sorts static
sites by closing angle. The adapter's description of `disconnected_sites` as
multi-structure fits conflates separate filtering steps. This paper's cooperative
curvature model is also distinct from the chat's adaptor-engagement proposal.

The article identifies a CC BY 4.0 license on page 1; a separate deposit license
has not been verified. Keep public access distinct from redistribution permission.

Scott et al.'s [Data availability section](https://www.nature.com/articles/s41467-018-02818-8)
states that datasets are available from the corresponding author on request.
No request was sent. The paper remains useful literature, but not a verified
downloadable raw-data source under the current public-data scope.

## Decision

Proceed with an exploratory, grouped geometry comparison after preserving the
raw/corrected fields and making filtering explicit. Do not use the current
adapter's heuristic errors for a confirmatory likelihood. No model has been fit
or ranked in this audit. See the frozen initial comparison specification for
scoring, sensitivity checks and stop conditions.
