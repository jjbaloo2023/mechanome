# Work-unit recovery phase runner

`work_unit_recovery.py` is a lead-supervised dummy-only phase runner.  Its
interface is `python research/work_unit_recovery.py PHASE RUN_DIR --commit SHA`;
the only accepted commit is the registered metadata commit.  It creates one
campaign and one attempt with campaign/task `dummy=2` limits.

Each phase writes its exclusive `RUN_DIR/phase-N.json` only at normal completion
or a preserved exception.  Marker callbacks write the exact two fixed evidence
files with exclusive creation.  Rejected, replay and over-cap callbacks raise
an assertion if the controller accidentally invokes them, so a silent callback
cannot make a check pass.

The supervisor must write `exit-N.json` only after observing the phase process
exit.  It contains `phase`, `status: completed`, `exit_code: 0`, `pid`, and
`phase_output_sha256`.  The supervisor then terminates the exited phase lead
with receipt evidence and writes required `post-exit-N.json`.  Before phase 2
or 3, this runner validates that receipt, the prior output hash/PID, and the
post-exit audit's terminated lead/token.  The runner never terminates its own
lead.

Phase 1 writes call 1 and intentionally leaves it reserved.  Phase 2 proves
that same-ID and new-ID calls are blocked while unresolved, verifies the exact
marker before reconciliation, replays the terminal call without callback, then
writes/reconciles call 2.  Phase 3 replays both IDs without callback, rejects a
third capped call, verifies both markers, and finishes the shared attempt with
a hashed software artifact.  The script makes no live-agent, exactly-once,
crash/reboot, scientific-work or callback-success claim beyond these supervised
ordinary process exits.
