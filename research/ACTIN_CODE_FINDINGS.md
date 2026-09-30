# Actin load-adaptation code inventory: reviewed partial contract

Accepted on 29 September 2026 after [independent review](ACTIN_CODE_REVIEW.md). The [source inventory](ACTIN_CODE_INVENTORY.md) establishes a pinned simulation configuration and analysis contract. It does not establish the Figure 7 run mapping or a matched deposited output table. Figure 7 reproduction eligibility stops here; this is not a claim that the full repository lacks relevant files.

## What was inspected

The article-linked [Akamatsu manuscript repository](https://github.com/DrubinBarnes/Akamatsu_CME_manuscript/tree/e0d5426515abaa37fdc9cd3151e108480a0337eb) was pinned to current main commit `e0d5426515abaa37fdc9cd3151e108480a0337eb`. Its date does not prove the publication's working revision. The [request ledger](metadata/actin-inventory-001/REQUEST_LEDGER.md) records 13 successful responses, 261,830 response-body bytes and five inert text files including README, within the [registered limits](actin_code_inventory_design.json). No author code was executed. The walk was selective, not a recursive repository audit.

| Checked item | Accepted observation | Remaining boundary |
| --- | --- | --- |
| Two spring-sweep configurations | Endpoints differ only in `first_surface` stiffness, 1 versus 50,000 pN/um | Neither exact Figure 7 run identity nor membrane-tension-to-spring calibration verified |
| Separate endocytosis configuration | 150 pN/um, 200 Arp2/3 couples, 15 seconds and 150 frames | A separate configuration is not evidence of Figure 7 controls |
| Retained multiple-sweep notebook | Helpers select absolute times 10 through 15, then calculate configuration means and standard deviations over run-time rows | Not per-run-first aggregation or a relative final-five-second window; exact Figure 7 use unverified |
| Saved output availability | The inspected spring-sweep subtree contains nine configurations and no output files | Other named output subtrees were not inspected; embedded notebook displays and external pickle paths are not matched deposited time series |

The notebook also contains a separate 12-second internalization estimator. It must not replace the Figure 7 summary by assumption. The larger 4,436,919-byte analysis notebook exceeded the entire retrieval budget and was not fetched. Neither a membrane-tension-to-spring mapping nor a constant-work-reference calculation was verified in the retained notebook. The earlier [primary-source assessment](ACTIN_ADAPTATION_FINDINGS.md) remains the authority for the published simulation prediction.

## Corrections and decision

Review corrected two wording errors: source/configuration texts were retrieved but never executed; `set simul internalize.cym` names a simulation declaration and is not a verified import. The lead and reviewer checked the distinction between pooled time rows and independent runs. Local response SHA-256 and all five Git blob identities were verified. No software tests, Cytosim runs, BVP solves or empirical mechanism tests were needed or performed.

The source note proposes another availability check as an unaccepted option. The lead instead follows the registered stop condition: preserve this partial contract and move to one separately registered experimental-observable feasibility question. Repeating metadata discovery without a new distinguishing question would not resolve the present inference gap.

The next candidate is an unassessed 2026 Myo1E primary paper, specified in [NEXT_CYCLE.md](NEXT_CYCLE.md). It is queued, not running. That assessment will ask what observable comparison is possible; it will not require full spatial force calibration merely to study observable changes, nor equate fluorescence intensity with a count of barbed ends.

## Preservation

The [manifest](actin_code_inventory_manifest.json) separates shareable notes/API metadata from local author-source and HTTP-header cache hashes. The cache remains on disk but is excluded from Git. Exact request identities and hashes permit later retrieval if specifically justified. No files were moved, and no Git push, installation or paid API call occurred.
