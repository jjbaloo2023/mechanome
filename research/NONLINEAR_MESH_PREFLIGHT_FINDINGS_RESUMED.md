# Final mesh preparation accepted after interrupted work resumed

The lead accepts the independently reviewed 003 source for a separately
registered final numerical attempt. This is code readiness and synthetic-test
evidence. No BVP or physical diagnostic was computed in this preparation stage.
The previous interrupted draft and its non-acceptance record remain frozen.

The corrected source retains the readable 002 structure, model equations,
linear controls, 26-case schedule, tolerances, domains, 20000-node cap and every
scientific threshold. Its registered changes are a fixed 5761-node initial mesh,
fresh 003 paths and identity, exact pole regularity, and an augmented residual
grid. The existing finite-R K3 comparison is retained. The grid contains the
original points, 17 interior points per final polynomial interval, and both
floating-point sides of every interior knot. Physical flux still differentiates
the actual v interpolant twice; no equation substitution hides derivative error.

Independent review resolved all earlier objections:

- Actual v'(0)=w(0)=0 is required before the finite pole limit. A synthetic
  v'(0)=1e-12 is rejected rather than masked by a tolerance.
- A C1 physical v bump placed between original grid points produces zero Q/r
  on the old grid and 48.9795928364 on the augmented grid. This tests the actual
  physical derivative calculation, not merely mismatch with stored w.
- Nonconstant PPoly values and first/second derivatives retain their axis and
  roundtrip correctly. Linear and nonlinear control paths remain distinct.
- Injected postprocessing failure leaves solver status and x/c/axis arrays on
  disk. Any failed gate suppresses K; matching finite-R K3 is preserved.

The successful synthetic run was observed at 2026-09-28
20:34:37.118720--20:34:37.207605 UTC, with zero real solve_bvp calls. Two earlier
harness-only failures are retained: a missing gate helper and Windows cleanup
of an open NPZ reader. Both were corrected before the successful run. They are
not numerical attempts or evidence about equilibria.

The lead checked final source/harness hashes and AST, compared the unchanged
model/control/serialization functions to frozen 002, and inspected the
independent review. Source SHA-256:
`f9a25845c3cca2dd8dbb88d5d1de0641ce45a3ffd5dc865cb822fc22c26ebbc3`.
Harness SHA-256:
`fc7915894b9a2e203da5f8256062ad319b6751305e46f49bae85270be7bee374`.

Attempt 3 is queued and remains unconsumed. Acceptance arrived near 20:35 UTC;
a complete run plus independent physical-result review did not reliably fit
before the 20:37:55 evidence cutoff. A fresh cycle must register the actual
start, confirm no existing execution/results, and run this frozen source once.
The unchanged 26-call ceiling and final-attempt stopping rule apply. A failed
physical gate closes this numerical branch; a pass permits only the registered
model-conditional K diagnostic. There is no numerical, stability, empirical
mechanism or practical-precision claim from preflight alone.

Evidence: [resumed registration](nonlinear_mesh_preflight_resume_001.json),
[source](nonlinear_graph_numerical_003.py), [harness](check_nonlinear_harness_003.py),
[checks and retained failures](nonlinear_mesh_preflight_checks.json),
[implementation](NONLINEAR_MESH_IMPLEMENTATION_RESUMED.md),
[independent review](NONLINEAR_MESH_PREFLIGHT_REVIEW_RESUMED.md),
[manifest](nonlinear_mesh_preflight_manifest.json),
[earlier interruption](NONLINEAR_MESH_PREFLIGHT_FINDINGS.md).
