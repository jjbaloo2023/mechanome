# Tracking validation now separates full and eligible cohorts

**Implemented and independently accepted.** The [validator](../validation/tracking.py)
now reports two internally consistent sets of counts and scores. Its previous
recall combined true positives from all ground-truth presence with false
negatives only from detectable ground truth. That mixed populations. The
[independent review](TRACKING_METRIC_REVIEW.md) accepts the repair and its limits.

## What changes for callers

`all_presence` scores every ground-truth event-frame. `detectable` scores the
subset whose observed local image peak reaches the declared floor. Both use the
same one-to-one matches, with ground truth present at the matching frame and a
strictly enforced inclusive spatial radius. A valid match to an ineligible
object is an all-presence true positive and is explicitly ignored by conditional
precision; it is not relabeled a physical false positive. Unmatched predictions
remain false positives in both blocks.

| Constructed case | Previous hybrid recall | New all-presence recall | New detectable recall |
| --- | ---: | ---: | ---: |
| One ineligible frame matched; another ineligible frame missed; one eligible frame missed | 1 / 2 | 1 / 3 | 0 / 1 |

The new denominator includes the entirely missed part of the cohort. Event
recovery also uses actual framewise matches; a nearby prediction outside an
event's time interval cannot make that event count as recovered.

The version tag is `tracking-validation-v2`. Existing top-level P/R/F1 and count
keys now mean **all-presence**. Explicit metric blocks use null for an undefined
rate; the top-level compatibility scalars retain the historical zero fallback.
F1 uses `2TP/(2TP+FP+FN)`, so all-missed nonempty truth yields zero, not undefined.
Sweep output uses explicit all-presence/detectable names, including
`all_presence_gt_event_detected_frac`. The CLI labels its score. Consumers relying
on old hybrid values or old sweep field names must adopt this documented contract;
repository caller inspection found no threshold that needed preservation.

Without a supplied movie, all present truth is eligible and the fallback is
labeled. With a movie, eligibility is based on observed local intensity, not the
noiseless center definition used in the [earlier synthetic demonstration](SYNTHETIC_DIMMING_FINDINGS.md).
The old positional-median `lifetime_pairs` remains a labeled legacy diagnostic.
It can disagree with valid event coverage and must not be interpreted as a
complete biological lifetime estimate.

## Validation and scope

The [targeted test log](tracking_metric_pytest_01.log) records **15 passed**:
hand-constructed regression cases plus the existing orchestration tests. Cases
cover mixed eligibility, missed frames/events, empty denominators, no-movie
fallback, true false positives, duplicates, temporal nonoverlap and radius
boundaries. The [execution ledger](tracking_metric_test_runs.json) records one
pytest invocation and exactly one instrumented tracker-movie call, below both
three-call limits. Workers performed no executions; the [lead-owned runner](tracking_metric_test_runner.py)
reserves cumulative budget before each invocation/call and preserves unique logs.

The final sweep-key rename occurred after pytest. The [label audit](tracking_metric_label_review.json)
proves that reversing only that literal rename exactly recovers the tested full
source hash. Tested validator logic is byte-identical; final Ruff F passes.
[AST checks](tracking_metric_static_checks.json) confirm the detector, linker,
Track and run_tracking are unchanged. No benchmark grid, physical inverse,
source acquisition or biological fit was run. Prior failed and over-budget
research records remain unchanged.

The [implementation note](TRACKING_METRIC_IMPLEMENTATION.md), [registration](tracking_metric_design.json),
[frozen accepted source](tracking_metric_source_001.py), [frozen tests](tracking_metric_tests_001.py)
and [manifest](tracking_metric_manifest.json) preserve this checkpoint. The
repair closes this software task; it is not a new clathrin-mechanism result.

## Next research decision

Return to verified public cap data with a different descriptive prediction
question: does the existing within-cell-line ranking transfer when an entire
cell line is held out? Existing results do not answer that question. Keep the
same three model forms and filtering policies, predeclare training weights and
all folds, and retain missing covariance and population-sampling caveats.
[NEXT_CYCLE.md](NEXT_CYCLE.md) specifies one bounded comparison. It is queued,
not running, and cannot establish a single-pit trajectory or molecular mechanism.
