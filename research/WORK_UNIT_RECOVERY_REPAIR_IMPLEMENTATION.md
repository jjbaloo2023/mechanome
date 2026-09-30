# Evidence-preserving recovery continuation

The lead implemented this script after the assigned worker returned without an
artifact before the actual deadline. No worker executed code. The source reuses
frozen dummy marker helpers and the original phase-3 verification; production
controller sources remain unchanged.

`prepare` validates the accepted input hashes, restores only fixed named files
from the preserved ZIP into a new directory, and verifies the original task,
attempt, reserved unit and lead identities. It writes a distinct reconciliation
record only after those checks. It retires the old token using independently
reviewed later local evidence, leaving the original call reserved for phase 2.
There is no fabricated phase-1 exit receipt and no edit to the failed run.

`run 2` and `run 3` each reserve their single-use invocation before launching the
direct interpreter established by the prior probe. The cumulative ledger retains
the failed first invocation and its callback. Every new child must match both
PID and parent PID and return exit 0 before its lead is retired. Timeout leaves
unknown status and blocks continuation; it does not trigger kill or replay.

Phase 2 checks both unresolved-ID guards before verifying and reconciling the
original marker, then skips duplicate work and uses only the one remaining
callback. Phase 3 replays terminal IDs without callbacks, rejects work at the cap,
and finishes the original attempt. The original failed supervision remains part
of the record even if this controlled-local continuation succeeds. This is not
a general external-side-effect, crash/reboot or live-agent recovery guarantee.
