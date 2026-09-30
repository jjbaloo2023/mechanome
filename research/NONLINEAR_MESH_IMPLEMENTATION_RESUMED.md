# Resumed mesh-preflight implementation — `nonlinear-mesh-preflight-001`

This resumed preflight completed without calling a real BVP solver or the
attempt-3 `main()` function.  It restores the readable attempt-2 structure in
the mutable 003 candidate and changes only the registered mesh/output/residual
contract: fresh 003 paths, 1,921 source nodes plus 3,840 exterior nodes, exact
origin regularity, and the stronger residual evaluation grid.

The source uses the unchanged model, cases, tolerances, 20,000-node cap, and
scientific gate thresholds.  Its physical residual grid consists of the
original 12,002 points, **17 interior points per final spline interval**, and
both `nextafter` sides of every interior knot.  It evaluates derivatives from
the first PPoly component.  The finite pole residual is used only when both
actual `v'(0)` and stored `w(0)` equal floating-point zero exactly; otherwise
the normalized pole residual is infinite and the new pole gate fails.  The
optional K path remains conditional on every gate and retains the matching
finite-R=12 K3 arrays.

The successful harness run began at `2026-09-28T20:34:37.118720+00:00` and
finished at `2026-09-28T20:34:37.207605+00:00`.  It measured zero real BVP
calls, captured the 5,761-node mesh and singular matrix from a stub, checked
linear dispatch, nonconstant axis-1 PPoly values plus first/second derivatives,
exact rejection of a `1e-12` pole slope, failed-gate K suppression, and an
on-disk postprocessing-failure checkpoint containing coefficients, breakpoints,
and axis data.  A C1 cubic bump placed strictly between adjacent original-grid
points has zero physical Q/r on that original grid but a 48.98 augmented-grid
Q/r residual, demonstrating that the stricter physical grid observes a defect
without ODE-RHS substitution.

Two harness-only failures preceded the final run: a missing extracted K-gate
helper after restoring the 002 base, and Windows cleanup of an open synthetic
NPZ reader.  Both made zero real BVP calls and are retained in the machine
readable check history.  No attempt-3 execution is authorized by this
preflight.

Final tested hashes and all numeric checks are in
[`nonlinear_mesh_preflight_checks.json`](nonlinear_mesh_preflight_checks.json).
