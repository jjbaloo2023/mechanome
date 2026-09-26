# Regular-rho passive axisymmetric result

Attempt 2 reparameterizes the accepted passive S40 material-area model with
`rho=sqrt(2*alpha)`, so `dY/drho=rho*dY/dalpha`. It keeps the same six states,
material-area tanh coat, `p=f=0`, homogeneous rigidity, and the supplement
positive tension-gradient sign. `rho` is an area label, not physical radius.

The registered design is [axisymmetric_rho_design.json](axisymmetric_rho_design.json).
Before execution, exact byte copies were frozen as
`axisymmetric_rho_frozen_002.py` and `axisymmetric_rho_design_frozen_002.json`.
Earlier named snapshots are retained as superseded pre-run provenance drafts;
the result hashes every imported and frozen artifact. Runtime source/design
were not changed after the exact copies were made.

Each of four cases ran in a separate subprocess with an actual 45-second
timeout, and the parent opened
[axisymmetric_rho_results_002.json](axisymmetric_rho_results_002.json) for exclusive
creation before collecting records, then wrote the completed JSON. An empty
file during the run was not completion evidence. No case timed out or failed. The `c_repo*ell=0.02`
case that previously hit the 12,000-node cap now converged in 0.40 seconds and
1,363 final nodes; its joint mesh/cutoff sensitivity converged in 0.42 seconds
and 2,161 nodes. This is a conditioning observation, not a new physical result.

| `c_repo*ell` | apex / `C_source` | smooth-reference relative error | final nodes | native rho RMS |
| --- | ---: | ---: | ---: | ---: |
| 0.005 | 0.6019321864 | 3.24e-7 | 1,195 | 9.90e-9 |
| 0.01 | 0.6019327498 | 1.26e-6 | 1,277 | 9.99e-9 |
| 0.02 | 0.6019350158 | 5.03e-6 | 1,363 | 9.96e-9 |

All cases pass preregistered status, native RMS, outer-BC, and axial
force-balance gates. The largest normalized Q residual is `9.55e-13`. The
`.005` and `.01` apex values differ from accepted attempt-1 tight records by
`6.38e-9` and `3.22e-9`, below the `2e-6` gate. The joint `.02` mesh/cutoff
apex difference is `1.84e-9`. Smooth-reference errors rise about fourfold when
amplitude doubles, consistent with the shallow quadratic correction.

Native `solve_bvp` residual norms cannot be compared directly between alpha and
rho coordinates. As an additional check, `(r/rho)*Y_rho - r*Y_alpha` is
evaluated at fraction 0.37 of selected final mesh intervals, avoiding endpoints
and midpoint collocation points. The largest six-component arc-length defect
is `1.23e-8`; all components and the sampling definition are stored per case.

This validates a bounded coordinate-conditioning repair in the stated passive
model. It does not reproduce author code or establish high-tension, force,
biological, branch-stability, or snap-through conclusions.
