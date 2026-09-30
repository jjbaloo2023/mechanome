# Repair-only numerical implementation — `nonlinear-numerical-repair-001`

This artifact repairs the known attempt-1 implementation defects for a future,
separately registered attempt 2.  It makes no numerical acceptance claim and
does not run `solve_bvp`.  Attempt-1 files remain frozen and are not imported
as mutable state.

[`nonlinear_graph_numerical_002.py`](nonlinear_graph_numerical_002.py) writes
only `nonlinear_numerical_results_002.json` and
`nonlinear_numerical_profiles_002.npz` when its guarded `main()` is eventually
authorized.  It records a `started` record before a call, then records solver
return/status/nodes and checkpoints that state before PPoly serialization or
residual work.  A later serialization/check exception retains both that known
solver return and its traceback.  A solver-call exception has a separate
checkpoint disposition.

The repair accesses the BVP wrapper's PPoly as `result.sol`, storing its
canonical coefficient array, breakpoints, and `axis`.  Reconstruction uses
`PPoly.construct_fast(..., axis=saved_axis)`, preserving the vector-valued
axis-1 output shape.  Off-mesh derivatives use the first spline component
directly.  The normalized flux and a separate `p`, `J`, `C-c` reconstruction
are compared away from the pole; the analytic pole limit is retained.

The linear control is now its own system, `w'=c'/r+sigma*v`, with the
`-3w/r` singular term placed once in `S`.  The nonlinear RHS remains separate.
Fine linear-reference gating evaluates both R=8 and R=12 at tolerance `1e-8`.
Only if every required gate passes, the program reconstructs fixed-source
`K` from saved PPolys and records (K/\varepsilon^3), together with the
matching finite-R=12 linear leading coefficient

\[
 r^2(v_1-v_2)\{- (v_1+v_2)(r\phi)' + 1.5\phi^2\}.
\]

## Synthetic preflight evidence

The command

```
.venv\Scripts\python.exe research\check_nonlinear_harness_002.py
```

passed.  The harness replaces the module's `solve_bvp` with a counter that
raises if reached; the recorded count is zero.  Its stubbed result has a real
solver-shaped axis-1 PPoly.  The checks confirm wrapper access through
`result.sol`, lossless coefficients/breakpoints/axis storage, and value plus
first/second derivative roundtrips at (r=0.25,2,3).  It also confirms the
linear RHS against its exact expression, distinguishes it from nonlinear
dispatch, and forces a post-return PPoly failure to verify the saved
`solver_returned`, solver-status, and traceback checkpoint.

The machine-readable evidence is
[`nonlinear_numerical_repair_checks.json`](nonlinear_numerical_repair_checks.json).
Importing the repair module was separately checked and performed no BVP call;
the static source inspection confirms the `if __name__ == "__main__"` guard
and that the singular matrix is confined to the BVP wrapper.  This stops at
code-review-ready; actual BVP execution is queued for the later attempt-2
registration.
