# Numerical harness repaired; attempt 2 remains queued

The first numerical attempt is preserved as an implementation failure after one
solver call returned. No usable physical result was saved. Its source, partial
result, empty NPZ and review remain unchanged under the attempt1 manifest.

The distinct002script corrects solver-wrapper access, interpolation axis storage
and reconstruction, linear-control dispatch, fine linear gates at both reservoir
sizes, post-return checkpointing, and the conditional saved-profile diagnostic.
Its physical residual uses derivatives of the interpolated v component; a separate
p/J reconstruction checks algebra. Nonlinear flux fields on control records are
explicitly labeled diagnostic-only. Scientific parameters and thresholds did not
change.

The independent review accepts code readiness. Synthetic regression checks used
a nonconstant, vector-valued polynomial with the actual SciPy BVP axis convention.
Values and first/second derivatives survived serialization. Stubbed solver returns
and a deliberately broken postprocessor verified saved return/status and traceback;
linear dispatch matched its separate equation. A forbidden-call counter measured
ZERO actual solve_bvp calls during these checks.

This is a software repair checkpoint, not validation of stationary profiles.
The local analytic theorem is unaffected. Attempt2 needs a new recorded execution,
the same frozen contract, at most26 solver calls and independent result review.
It has not started. No scientific tolerance was relaxed to turn failure into success.

- [Corrected candidate](nonlinear_graph_numerical_002.py)
- [Synthetic harness](check_nonlinear_harness_002.py) and [check results](nonlinear_numerical_repair_checks.json)
- [Implementation account](NONLINEAR_NUMERICAL_REPAIR_IMPLEMENTATION.md)
- [Independent review](NONLINEAR_NUMERICAL_REPAIR_REVIEW.md)
- [Stopped attempt1](NONLINEAR_NUMERICAL_FINDINGS.md)
- [Next execution](NEXT_CYCLE.md)
