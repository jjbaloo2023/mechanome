# Offline work-unit reservation implementation

The offline controller now has immutable normalized `work_unit_limits` on both
the campaign charter and each task.  Limits are canonical kind/nonnegative-unit
pairs, stored as frozen tuples; a guarded call must declare its kind in both
limits and reserve a positive number of units.

`reserve_work(token, attempt, call_id, kind, units)` runs under `BEGIN
IMMEDIATE`, fences the lead, and writes a task-scoped call identity before any
dummy callback can run.  It sums every reservation for the task and campaign,
across attempts and restarts, so failed, cancelled and reconciled calls still
consume units.  This conservative no-refund policy prevents a retry from
silently recreating budget.  A same kind/unit terminal duplicate returns the
explicit non-executing `terminal_duplicate` result; changed kind/units conflict,
and reserved/unknown identities block replacement.

`mark_work_unknown` and `reconcile_work` are new fenced work transitions.
Reconciliation needs evidence and a terminal `completed`, `cancelled` or
`failed` state.
`run_guarded_work` deliberately leaves a successful callback reserved: its caller
must make the separate evidence-bearing terminal reconciliation, and a raised
callback remains reserved for crash-safe inspection.
Existing `uncertain` and `finish` APIs remain compatible and are not newly
fenced; `finish` now refuses an attempt with unresolved work, while `start`
also refuses a task with any reserved/unknown work.  Export includes individual
work rows and lifetime campaign totals.

Old charter/task JSON lacking the optional field constructs with an empty limit
tuple and is returned without rewriting its stored body.  Existing-charter and
task-redelivery comparisons use normalized contract semantics, so adding the
default does not reject legacy records.

The new tests use only callbacks that append to a local list.  They cover cap
rejection before callback execution, a raised callback that remains reserved
until failed reconciliation, terminal duplicates across retries, unknown/restart
reconciliation, a two-thread fresh-connection campaign-cap race, stale fencing,
and legacy reload.  The separate reopen test verifies persisted accounting; it
does not claim uninterrupted process operation.
This is an offline bookkeeping guard.  It neither provides exactly-once external
side effects nor connects to a live agent, provider, scheduler, or scientific
workload.
