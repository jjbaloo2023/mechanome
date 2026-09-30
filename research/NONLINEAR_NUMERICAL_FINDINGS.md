# Numerical attempt 1: implementation failure, physics unassessed

The first registered attempt stopped after one boundary-value solver call
returned. An output-handling bug requested polynomial coefficients from the
solver result wrapper instead of its interpolation object. The process exited
with code 1 before the solver status and profile arrays were saved. The exact
executed script and empty checkpoint are retained; no solver rerun occurred.

This is an implementation failure. It does not establish nonconvergence,
contradict the local existence theorem, or supply numerical evidence about the
model. No equilibrium gate, linear/zero control comparison, ordering margin or
optional compatibility diagnostic was evaluated.

Independent inspection also found a mislabeled linear-control code path,
an incorrect interpolation-object argument in residual checking, an incomplete
fine-linear gate, and an omitted conditional diagnostic. These must be corrected
before a new registered execution. Parameters and acceptance thresholds remain
unchanged; code failure is not a reason to loosen the experiment.

See [implementation record](NONLINEAR_NUMERICAL_IMPLEMENTATION.md),
[independent review](NONLINEAR_NUMERICAL_REVIEW.md),
[partial result](nonlinear_numerical_results_001.json), and
[executed source](nonlinear_graph_numerical.py). The
[asymptotic note](NONLINEAR_NUMERICAL_ASYMPTOTIC.md) is a separate analytic
prediction: the fixed-source compatibility diagnostic scales cubically at
leading order. It remains untested numerically here.

A separate code-repair stage is preparing attempt 2. No additional BVP calls
are authorized within stopped attempt 1; the next execution must retain this
failure record, use new output paths, and pass independent preflight review.
