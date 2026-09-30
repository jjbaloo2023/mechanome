# Bounded numerical implementation — `nonlinear-numerical-001`, attempt 1

## Execution disposition

This attempt stopped with an exact code failure after its first permitted BVP
call returned to Python.  It does **not** report a nonlinear profile, a
convergence result, a control result, or an ordering result.  It must not be
restarted: the returned first BVP object was not serialized, so repeating that
case would duplicate a solve whose solver status is unknown.

The immutable execution record is
[`nonlinear_numerical_results_001.json`](nonlinear_numerical_results_001.json).
It records the sole call as `unknown_completion_code_failure_stop`, its exact
timestamps, package versions, frozen-input hashes, and the SHA-256 of the
execution-source bytes.  The empty NPZ file was created by the pre-call
checkpoint; it contains no solution coefficients.

The precise exception was `AttributeError: c` in `ppoly_arrays`: the program
tried to read `sol.c` from SciPy's `solve_bvp` result rather than the PPoly
stored at `sol.sol.c`.  Because this happened between solver return and the
post-call checkpoint, no node count, solver message, PPoly breakpoints, or
coefficients can honestly be reconstructed.  A second defect was identified
during the stopped attempt's review: the `linear` control path would have
called the nonlinear RHS instead of a separate linear RHS.  Neither defect was
corrected in the execution source, because preserving those source bytes and
stopping prevents an accidental restart of this registered attempt.

## Intended fixed contract encoded in the source

The preserved source, [`nonlinear_graph_numerical.py`](nonlinear_graph_numerical.py),
was structured to make at most 26 calls: eighteen nonlinear cases (three
amplitudes, two tensions, and the three fixed R/tolerance configurations), six
linear controls, and two zero-source controls.  It wrote a `started` record and
an NPZ checkpoint before every BVP call.  It used a singular matrix with only
the `-3w/r` contribution and a regular-origin boundary condition.

For a successful future, separately registered attempt, required corrections
are to use `solution.sol.x` and `solution.sol.c` for the stored PPoly, pass the
PPoly to the off-mesh checker, and implement the independent linear system
`w'=c'/r+sigma*v` without the nonlinear denominator or products.  Its
off-mesh flux must differentiate the first spline component (`v'` and `v''`),
not substitute the ODE RHS or assume the stored `w` spline is that derivative.
The NPZ should preserve PPoly breakpoints and coefficients after each known
completion, so later residual and K calculations need no BVP rerun.

No acceptance threshold was relaxed, no amplitude/domain/tolerance case was
changed, and optional K was suppressed.
