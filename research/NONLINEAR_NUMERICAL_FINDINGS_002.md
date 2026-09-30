# Exact graph numerical attempt 2: physical residual gate failed

All 26 registered boundary-value solves returned status 0 and were saved, but
**the numerical realization is not accepted**. Independent reconstruction from
saved polynomial coefficients reproduces the failed physical equation check.
The downstream fixed-source compatibility diagnostic K was not computed.

| Check | Result |
| --- | --- |
| Calls and termination | 18 nonlinear, 6 separate linear, 2 zero; process exit 0 |
| Fine nonlinear physical max absolute Q/r divided by epsilon | 1.45767e-4 to 1.53030e-4; required below 1e-5 |
| Solver status, graph safety, prescribed boundaries | Passed |
| Sampled profile tolerance/reservoir changes and ordering margins | Passed, but insufficient to override the physical residual failure |
| Independent fine linear Green comparison, R8 and R12 | Passed; largest relative error 1.21436e-7 versus 1e-6 limit |
| Zero-source controls | Exactly zero sampled profile |
| Conditional K calculation | Suppressed |

The failed residual applies to all 12 fine nonlinear cases. The original grid's
maxima lie inside the source disk, around radius 0.93324 or 0.84137, not solely
at the pole. Agreement of profile values under refinement does not establish
accuracy of the second derivatives used by the equation.

Execution was observed from 2026-09-27 00:54:03.636845 to 00:54:33.897736 UTC;
terminal return was observed at 00:55:08.114849. Python 3.12.14, NumPy 2.5.2 and
SciPy 1.18.1 are recorded in the result. This is a bounded completed run, not
continuous operation. Attempt 1 remains a separate implementation failure;
attempt 2 is a completed calculation with a failed scientific acceptance gate.
Neither failure contradicts the local existence theorem or refutes a biological
mechanism. No finite-amplitude equilibrium or practical precision is promoted.

The lead accepts the execution provenance and independent review, rejects the
numerical realization at its unchanged gate, and retains every saved profile.
After that stop condition, a separate [saved-coefficient diagnosis](NONLINEAR_RESIDUAL_POSTMORTEM.md)
examines why the physical residual fails, with no additional solver calls.
One final logical attempt remains; any new implementation needs a reviewed
plan and preflight before execution.

Evidence: [frozen contract](nonlinear_numerical_design.json),
[execution](nonlinear_numerical_execution_002.json), [executed source](nonlinear_graph_numerical_002.py),
[results](nonlinear_numerical_results_002.json), [profiles](nonlinear_numerical_profiles_002.npz),
[implementation record](NONLINEAR_NUMERICAL_IMPLEMENTATION_002.md),
[independent review](NONLINEAR_NUMERICAL_REVIEW_002.md),
[reanalysis](nonlinear_numerical_reanalysis_002.json),
[manifest](nonlinear_numerical_manifest_002.json).
