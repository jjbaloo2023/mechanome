# Final mesh-refined numerical realization — `nonlinear-numerical-001`, attempt 3

The registered attempt-3 runner was launched exactly once with
`.venv\\Scripts\\python.exe research\\nonlinear_graph_numerical_003.py` from
the repository root.  Its runner state began at
`2026-09-29T00:59:13.605340+00:00` and completed finalization at
`2026-09-29T01:00:11.802081+00:00`.  All 26 registered calls completed with
`solver_status=0`; the largest mesh contains 5,764 nodes, below the 20,000
cap.  No further BVP call was made.

The execution tool initially returned a running cell (`74`) and later a
completion notification, but did not provide `exec_command` process metadata.
The terminal exit code is therefore recorded as `null`, rather than inferred
from the completed computational artifact.  The complete per-call timestamps,
statuses, source/design/mesh-plan hashes, and this telemetry limitation are in
[`nonlinear_numerical_results_003.json`](nonlinear_numerical_results_003.json).

The terminal scientific status is `completed_gate_failed_optional_K_suppressed`.
All gates except the physical Q/r gate passed: fine nonlinear normalized
residuals range from `1.2744489648950401e-05` to
`1.7663050515115233e-05`, exceeding the frozen `1e-5` threshold.  Exact pole
regularity passed for all fine nonlinear profiles, as did the graph-safety,
boundary, tolerance/refinement, reservoir, linear-reference, zero-source, and
sampled ordering gates.  The optional K/K3 diagnostic was suppressed and no K
arrays were saved.

The strengthened physical residual union used 12,002 original points, 17
interior points per final interval, and both sides of every interior knot.  The
original-graph flux reconstruction agrees with the normalized expression away
from the pole to at most `2.7755575615628914e-16`.

[`nonlinear_numerical_profiles_003.npz`](nonlinear_numerical_profiles_003.npz)
contains 26 PPoly coefficient arrays, 26 breakpoint arrays, and 26 axis arrays,
plus the saved Bessel references.  It permits independent off-mesh reanalysis
without any additional BVP solve.  No source, design, registration, or prior
attempt artifact was changed during execution.
