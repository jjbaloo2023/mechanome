# Direct-interpreter process identity: one successful preflight

29 September 2026. The separately registered zero-work probe launched the locally
reported base Python executable directly. It observed PID **18908**, and the
child reported that same PID and parent PID **17360**, matching the supervisor.
The child's executable also matches the requested base path. The parent observed
exit code **0**, from **16:44:00.797655 to 16:44:00.874122 UTC**.

The [result](process_identity_probe_001.json), [raw output](process_identity_probe_001.log),
[reservation](process_identity_probe_reservation.json), [launch record](process_identity_probe_started.json)
and [source](process_identity_probe.py) preserve this sole invocation. Its source
hash, AST and Ruff F were checked; it used no campaign, dummy callback, scientific
calculation or network. The [design](process_identity_design.json) capped it at
one subprocess. [Independent review](PROCESS_IDENTITY_REVIEW.md) records the scope.

This establishes one usable local launch path for the observed normal exit.
It does not prove the cause or process ancestry of the earlier virtual-environment
PID mismatch, validate a crash/reboot path, or retrospectively accept the stopped
[recovery demonstration](WORK_UNIT_RECOVERY_FINDINGS.md).

The next step is a bounded repair/reconciliation design, not an automatic replay.
It must preserve the original failed invocation, one charged dummy unit, one
remaining dummy callback and two remaining phase launches. Any use of later PID
absence and verified marker evidence must be explicit and independently reviewed;
they cannot be relabeled as an original parent-observed child exit. If reconciliation
cannot be justified, leave that campaign unresolved. Do not create a fresh budget
or rerun phase 1 to manufacture a clean demonstration.
