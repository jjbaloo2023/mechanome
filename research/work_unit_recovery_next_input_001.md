# Next cycle: demonstrate work-unit recovery across processes

Checkpoint: 29 September 2026 UTC. The [offline work-unit extension](WORK_UNITS_FINDINGS.md)
is independently accepted with 17 targeted tests passing in one invocation.
Current workers are terminal. The work below is queued, not running.

## Next executable decision

1. Reconcile current workers and latest user steering. Verify the accepted
   [manifest](work_units_manifest.json) and tested source. Register a distinct
   dummy-only demo with input hashes, unique outputs and a persistent phase ledger.
2. Reuse the existing SQLite controller. Use at most three lead-owned sequential
   phase subprocesses, one invocation per phase, and at most two dummy callbacks
   total. No extra pytest invocation is planned unless a separately documented
   concrete defect justifies a new bounded repair task. Do not rerun old studies.
3. In phase 1, reserve and execute one deterministic dummy action, save its
   evidence under an exclusive path, and leave its call unresolved to simulate
   a lost acknowledgment. Exit normally. The lead records actual process exit.
4. In phase 2, reopen in another process. Check persisted budget and the unresolved
   call before any replacement. Demonstrate same-ID and different-ID rejection.
   Reconcile only after verifying the exact saved evidence. Replay of the terminal
   call must skip its callback. If using a second callback, reserve it explicitly,
   save distinct evidence and reconcile; the registered total must stay at two.
5. In phase 3, verify terminal replay and cumulative cap rejection after another
   observed process exit, export the final audit and finish cleanly. Register
   exact phase transitions/lead fencing before execution. Unknown process status
   blocks replacement; timeout alone is never evidence of termination.
6. Use one bounded independent reviewer for the design, phase records and final
   claims. Lead owns execution; a specialist may own the small script if useful.
   Stop at one reviewed recovery result or exact blocker. Preserve every phase
   output; a failed phase does not authorize resetting its invocation count.

This demonstrates simulated acknowledgment loss across ordinary process exits,
not an injected crash, host reboot, live agent control or exactly-once external
side effects. It closes a specific gap in the current same-process reopen tests.
No live scheduler integration, framework expansion or historical-ledger migration
is included. After this finite demonstration, reassess the broad research goal
before adding more operational work.

## Preserved research stops

The biological evidence map remains [FINDINGS.md](FINDINGS.md). No mechanism is
selected. No endpoint-paper access rescue, repeated actin inventory, geometry
grid, dimming grid, solver repair or closed yeast/Myo1E/Bucher/Akamatsu branch is
queued. DASC/AP2 remains parked as a mechanism test. The historical 282/150-call
overrun remains a failure despite the new offline software guard.

Target 20 minutes from actual observed start, reserving checkpoint time. No
source requests, fit/tracking/BVP/author-code calls, installs, direct API spending,
external messages, purchases, commits, Git pushes or publishing. Record scheduled
delivery, observed activity, queued work and dated checkpoint separately.
