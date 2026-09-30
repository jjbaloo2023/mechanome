# Bounded numerical realization — `nonlinear-numerical-001`, attempt 2

The registered attempt-2 process completed exactly once with terminal exit code
0 and no terminal output.  It made the full registered 26 calls: 18 nonlinear
cases, six independent linear controls, and two zero-source controls.  Every
record has `solver_status=0` and `outcome=completed`; the largest adaptive mesh
has 1,166 nodes, below the fixed 20,000-node limit.  No additional BVP call was
made.

The runner started at `2026-09-27T00:54:03.636845+00:00`, completed
finalization at `2026-09-27T00:54:33.897736+00:00`, and its clean terminal
return was observed at `2026-09-27T00:55:08.114849+00:00`.  Exact timestamps,
per-solve starts/finishes, solver messages, and environment/source provenance
are in [`nonlinear_numerical_results_002.json`](nonlinear_numerical_results_002.json).

The profile archive [`nonlinear_numerical_profiles_002.npz`](nonlinear_numerical_profiles_002.npz)
has 26 PPoly coefficient arrays, 26 breakpoint arrays, and 26 stored axes.
This allows off-mesh values and derivatives to be recomputed without another
BVP solve.  It also stores the two Bessel-reference profiles used by the
linear-control comparison.

## Gate disposition

The terminal status is `completed_gate_failed_optional_K_suppressed`.  Solver
status, graph safety, boundary compliance, tolerance and R refinement, both
fine R=8/R=12 linear-reference controls, zero controls, and sampled ordering
gates passed.  The required nonlinear flux gate did not: the six fine-case
values of `max_abs_Q_over_r_div_epsilon` range from
`1.4576741903985e-4` to `1.5303034211854217e-4`, above the frozen `1e-5`
threshold.  The result is therefore an inconclusive/failed computational gate,
not a finite-case equilibrium acceptance.

The original-graph flux reconstruction agrees with the normalized flux away
from the pole to at most `1.6653345369377348e-16`, so that crosscheck does not
identify a transcription mismatch.  The retained pole-limit and interpolation
residual data remain available for independent review.  Because a required
gate failed, the optional fixed-source K diagnostic was not run and no K arrays
were written.  No thresholds, amplitudes, tolerances, domains, or cases were
changed after observing these results.
