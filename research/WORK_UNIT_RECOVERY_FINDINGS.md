# Recovery demonstration stopped at process identity verification

29 September 2026. Independent [review](WORK_UNIT_RECOVERY_REVIEW.md) rejects a
completed three-process recovery claim. The supervisor stopped after the first
phase, before admitting a replacement process or refunding any work units.

## What happened

The sole phase invocation started at **16:38:37.249233 UTC**. The supervisor
launched the virtual-environment Python executable as PID **12896** and observed
exit code **0** at **16:38:37.489082 UTC**. The phase output reported PID **6280**.
The supervisor required those identities to agree and therefore failed closed.
It did not create an accepted exit receipt, retire the lead, or run phases 2/3.

The phase itself wrote one exclusive deterministic dummy marker. Read-only
SQLite inspection found one reserved unit, one running attempt and lead token 1
still marked active. Those saved statuses describe unfinished protocol state;
they are not proof of a currently running process. No work was reconciled,
refunded, repeated or replaced. The [execution ledger](work_unit_recovery_execution.json)
retains **one of three phase invocations** and the [failure audit](work_unit_recovery_failure_audit.json)
retains **one of two permitted dummy callbacks**.

At 16:40:05 UTC, a `Get-Process` lookup explicitly found neither PID. That later
absence does not attest their original ancestry or supply the target Python
process's observed exit code. Earlier CIM access was denied, and a .NET lookup
was blocked by constrained PowerShell; its empty array is explicitly rejected as
absence evidence. The [actual lookup](work_unit_recovery_001/process_lookup_cmdlet.json)
and failed diagnostic are preserved.

Windows virtual-environment redirection is a plausible explanation. The local
interpreter reports a different base executable, but no original process-tree
record establishes that explanation. This is a supervision/identity failure,
not evidence that SQLite lost its reservation or that a biological model failed.

## Scope and next decision

The accepted controller source and its 17-test checkpoint remain unchanged.
Review improved exact rejection-reason checks, persisted state checks, marker
counting and parent-only retirement before execution. Those static corrections
did not prevent the platform identity mismatch. No new pytest invocation,
scientific calculation, source request or paid API call ran.

Stop this demonstration at its failed phase; do not reset phase or callback
counters. A separately registered zero-work direct-interpreter identity probe
is permitted to clarify the launch path. It cannot retrospectively turn this
failed run into a valid recovery result, authorize a new callback, or reconcile
the preserved work. Any later repair needs a distinct reviewed plan retaining
this expenditure and uncertainty. No live-agent or host-crash/reboot capability
is demonstrated here.

[Registered design](work_unit_recovery_design.json), [execution input hashes](work_unit_recovery_execution_inputs.json),
[phase implementation](WORK_UNIT_RECOVERY_IMPLEMENTATION.md), [failure snapshot](work_unit_recovery_attempt_001.zip),
[manifest](work_unit_recovery_manifest.json).
