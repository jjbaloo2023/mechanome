# Independent review disposition — 2026-09-19

The independently briefed Sol/high reviewer completed
`geometry-independent-review-001`, attempt 1. The lead accepts the narrow
descriptive scope and all three actionable findings. The original objections
remain in [INDEPENDENT_REVIEW.md](INDEPENDENT_REVIEW.md).

1. **Integrity corrected.** An explicit `geometry_inputs.lock.json` pins the
   implementation, protocol and data audit, separately from generated outputs.
   Each table must also match SHA-256 and retained published MD5. Tests reject
   joint table/audit modification and a wrong MD5 after explicit audit re-locking.
   This protects against drift, not an actor who rewrites code, lock and data.
2. **Observation wording corrected.** Cap area and angle are fitted; curvature is
   algebraically derived within that geometry. The corrected-flat primary filter
   is repository policy, not a claim of uniquely reproducing the paper's filter.
3. **Boundary corrected.** A zero constant-area coefficient (infinite area) or
   nonfinite implied area stops as unresolved. The zero-data case has a test.

Version-1 script and protocol are archived in `baselines/geometry_v1/`, with bytes
matching the hashes in the original `geometry_results.json`. Original results and
`geometry_review.json` were preserved. New results are `geometry_results_v2.json`:
every run payload, fold, coefficient, error and filter count is exactly equal to
version 1. The command rejects overwriting the existing version-2 output.

Validation: 26 focused tests passed. These corrections were implemented/tested by
the lead, not independently re-reviewed. Forms, filters and scoring did not change.

**Permitted scope:** conditional cross-cell prediction of deposited cap geometry.
Joint measurement uncertainty, culture/preprocessing independence, individual-pit
dynamics and molecular mechanisms remain unresolved. Do not escalate this static
ranking into those claims.

The source specialist identified three public dynamic-data candidates in
`PUBLIC_DYNAMIC_DATA.md`. This is discovery, not file validation. The next task
is a small metadata/access check, specified in `NEXT_CYCLE.md`.
