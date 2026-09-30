# Offline cumulative work-unit limits

Accepted 29 September 2026 after [independent review](WORK_UNITS_REVIEW.md).
The existing SQLite controller now reserves declared units before a guarded
local callback. Task and campaign limits accumulate across attempts and database
reopens. This is an offline software result; no biological result changed.

## What is enforced

- Each task has stable call IDs. Terminal duplicates skip the callback; changed
  kind or unit count conflicts with the original reservation.
- Reservations are atomic and require the current lead token. Every reserved
  unit counts permanently, including failed or cancelled work; there is no refund.
- Reserved or unknown work blocks another call ID, attempt finish and retry.
  Explicit terminal reconciliation requires evidence. Even a successful callback
  remains unresolved until its caller records that evidence.
- Optional limits preserve old serialized charter/task redelivery. Existing
  money, review reserve, attempt and artifact checks remain in place.

The first implementation allowed a new call ID to bypass an unresolved call.
Review caught and corrected that before execution. Review also corrected legacy
JSON redelivery fixtures and separated task/campaign cap tests. Lead bounded the
concurrent test's barrier and joins before running it.

## Evidence and limits

One lead-owned pytest invocation ran at **16:09:54.630006–16:09:55.948859 UTC**:
**17 tests passed** (11 existing, six new), exit 0. The [log](work_units_pytest_01.log)
and [execution ledger](work_units_test_runs.json) retain exact tested hashes and
one invocation against a cap of three. No scientific callback, tracker movie,
fit, BVP or network request ran. Workers read and edited only.

The new checks exercise rejected reservations before callbacks, exception
reconciliation, duplicates across retries, lifetime task/campaign caps, legacy
redelivery, stale lead tokens, database reopens and two fresh connections racing
for one campaign unit. Exactly one racing reservation succeeds. Final
[static checks](work_units_static_checks.json) verify AST, Ruff F and tested hashes.
[Source snapshot](work_units_source_001.zip), [before snapshot](work_units_before_001.zip),
[design](work_units_design.json) and [manifest](work_units_manifest.json) preserve
this attempt without replacing earlier evidence.

Reopened connections are not a separate-process crash or reboot demonstration.
The new work transitions are fenced; existing attempt `finish` and `uncertain`
were not newly fenced. Reservation counts are not independent observations of
side effects. No exactly-once external execution guarantee follows. The caller
must route real work through this API before any live enforcement claim.

## Decision

Accept this bounded extension and stop implementation. The earlier dimming
**282-call/150-cap overrun remains a protocol failure**; this change does not
retroactively repair it. A further scientific rerun would not test this guard.
A separately registered, short, dummy-only process-exit/recovery demonstration
is the next informative check. It must preserve unresolved reservations, show
observed process exit before replacement and validate evidence before replay.
There was insufficient evidence-window time to implement and review that new
stage this cycle. It is queued, not running. Full live-agent integration and a
new scheduler are outside this task.
