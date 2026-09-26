# Passive solver coordinate repair: attempt 2

The material-area coordinate repair resolves the previously preserved shallow
node-limit failure without changing the membrane equations. This is a numerical
capability result, not a biological discovery or a stability result.

Four cases passed the registered gates. At c_repo*ell=.02, the solver now
converges with 1,363 nodes in 0.404 seconds; the old area-coordinate attempt
failed at the 12,000-node cap and remains preserved. A joint mesh/cutoff
sensitivity also converges, with maximum normalized observable difference
1.84e-9. This combined check does not separate mesh and cutoff contributions.
The two previously accepted amplitudes reproduce all four normalized observables
within 6.38e-9. Their smooth-linear apex errors, together with the repaired case,
remain consistent with a quadratic normalized correction in amplitude.

The independent axial-force residual stays below 9.56e-13 relative; sampled
arc-length defects are at most 1.23e-8. Native solver residual norms change with
the coordinate and do not establish equal physical accuracy just because both
runs requested tolerance1e-8. The independent lead comparison of the new and
frozen old alpha right-hand sides was exact at1,000 arbitrary regular states;
40 pole comparisons agreed within3.31e-24. All original artifacts are unchanged.

The numerical worker reports three focused tests passed in1.44seconds, including
preservation of a subprocess timeout record. Each case has a real45second
subprocess limit. The timeout test mocks expiry; no forced45second wait was
needed. Complete solution-profile equivalence was not assessed; only stored
observables were compared between coordinates.

Before execution, review caught a residual diagnostic that sampled collocation
midpoints; it was moved to fraction0.37 of selected intervals. Earlier attempted
snapshots were a hash-only manifest or text copies with extra newlines. They
remain superseded pre-execution drafts. The actual executed source and design
have exact byte copies in axisymmetric_rho_frozen_002.py and
axisymmetric_rho_design_frozen_002.json; all recorded hashes match. The result's
historical task_id axisymmetric-passive-rho-002 is an alias for registered
axisymmetric-rho-numerical-001 under parent axisymmetric-passive-001 attempt2.

The theory specialist derives and independently reviews the numerical work;
the lead checks the theory and stored results. The review disposition is retained
in AXISYMMETRIC_RHO_REVIEW.md when completed. No second lead or scheduler exists.
The next physics stage stays gated on that disposition.

Artifacts: [numerical report](AXISYMMETRIC_RHO_NUMERICAL.md),
[theory](AXISYMMETRIC_RHO_THEORY.md),
[results](axisymmetric_rho_results_002.json),
[independent lead checks](axisymmetric_rho_lead_checks.json).

The scheduled delivery was22:58:15.217UTC; first observed clock22:58:28UTC,
target checkpoint23:18:28UTC. The lead checker completed at23:11:57UTC. The next
routine read stalled with runner spawn_ready failure; next observed clock was
23:23:04UTC, beyond target. This is an overrun, not20minute compliance or evidence
of continuous computation. Only checkpoint work followed the observed overrun.

## Final disposition

Independent implementation review completed and was accepted by the lead.
All workers are completed; no outstanding execution remains. The next bounded
moderate-deformation area-sign test is queued, not running. See
[review](AXISYMMETRIC_RHO_REVIEW.md) and [next cycle](NEXT_CYCLE.md).

Final checkpoint: 2026-09-25T00:00:21.264304+00:00. After the observed23:23:04 clock,
the next successful checkpoint-script clock was23:59:02; that further gap has
no verified cause and is not attributed to active computation. The20minute
target was exceeded. No new research computation followed the observed overrun.
