# Passive axisymmetric numerical benchmark

`axisymmetric-passive-numerical-001`, attempt 1, is a bounded, research-only
test of the passive homogeneous axisymmetric equations. It has no pressure,
traction, stiffness contrast, inverse fit, continuation branch claim, or
biological interpretation.

## Implemented convention

The material coordinate is `alpha=a/(2*pi*ell^2)`, with
`ell=sqrt(kappa_repo/sigma)`. The mapping is `k_source=2*kappa_repo` and
`C_source=c_repo/2`; the outer tension is therefore
`lambda_outer*ell^2/k_source=0.5`. The code uses the supplement S40 equations
with `p=f=0` and the **positive** `lambda_dot=2*(H-C)*C_dot` convention.
That sign follows from `lambda_dot=-partial W/partial alpha` at fixed shape and
`W=k(H-C)^2`: its explicit curvature derivative is negative. The source main
Eq. 3 discrepancy remains documented rather than silently treated as a
published-solver reproduction.

At a finite pole cutoff `alpha0`, the solver uses the independently derived
regular expansion in `AXISYMMETRIC_THEORY.md`, including `r=rho+O(rho^3)`,
`psi=H0*rho+O(rho^3)`, `L=2*H0*(lambda_p-C0*(H0-C0))*alpha+O(alpha^2)`, and
the corresponding `H`, `z`, and `lambda` terms. The three free pole values
`H0,z0,lambda_p` complete the nine BVP conditions. The stored pole quantity is
the imposed finite-cutoff BC residual; cutoff sensitivity of observables is the
independent pole check.

The coat is `C=0.5*C0*(1-tanh((alpha-x^2/2)/width_alpha))`. Baseline areas
`x=R/ell={0.5,1,2}` use the same outer radius 14, rather than changing the
total material domain with coat area. Bessel comparisons are the sharp-edge
reference. A separate Green-function apex reference uses the actual smooth
coat profile, so smoothing bias is not mislabeled as a nonlinear error.

## Records and validation status

The registered ten-case record is [axisymmetric_results_001.json](axisymmetric_results_001.json).
All ten reported `solve_bvp` status 0. The largest RMS ODE residual was
`9.997e-6`; outer `z`, `psi`, and `lambda` errors were below `1e-30`, `1e-29`,
and exactly zero in the shown baseline case. The baseline normalized apexes
decrease from 0.828, to 0.602, to 0.280 over `x=0.5,1,2`, matching the
small-slope passive trend. At `x=1`, the baseline sharp-reference relative
errors were `4.71e-5` (apex), `5.82e-5` (reservoir depth), and `8.30e-5`
(edge-referenced depth); the coat mean differs by `1.01e-2`, as expected for a
finite smooth edge rather than a pointwise sharp interface.

Mesh/tolerance, cutoff, smoothing, and domain cases are records, not pooled as
one error bar. The narrower `width_alpha=0.005` apex sharp error (`1.35e-5`)
is smaller than the wider `0.02` case (`1.81e-4`). The cutoff change
`1e-6 -> 2.5e-7` changes the apex by `1.21e-7`. The force-balance first
integral `Q=r*((H-C)*(H+C-sin(psi)/r)-lambda)*sin(psi)+L*cos(psi)` is stored
with both raw and relative scales; its baseline `x=1` relative residual is
`2.69e-7`.

The initial baseline tolerance floored the amplitude comparison. A registered
separate refinement, [axisymmetric_amplitude_refinement.json](axisymmetric_amplitude_refinement.json),
uses `x=1`, width 0.01, outer radius 14, cutoff `1e-6`, 801 initial nodes, and
`tol=1e-8`. It succeeded for `c_repo*ell=0.005` and `0.01`, with smooth-apex
relative errors `3.14e-7` and `1.26e-6`, respectively: a factor 4.00, consistent
with the expected normalized `O((c_repo*ell)^2)` nonlinear correction. The
`0.02` refinement failed (`status=1`, RMS residual `0.397`) and is retained as
a failed record. It is not evidence about a physical branch.

`per_solver_seconds=45` in the registered design was a target, not an enforced
wall-clock interrupt. The recorded successful solves took at most 9.16 seconds;
the failed high-amplitude refinement took 4.14 seconds before `max_nodes`.

## Reproducibility note

The original record retains its execution-time source hashes. Its recorded
`axisymmetric_passive.py` hash (`9ced1728...`) and design hash
(`1ae285cb...`) differ from the final files because, after that run, this code
received only the separate refinement entrypoint (the BVP equations and
`solve_case` physics were unchanged) and the design received its refinement
amendment. The original JSON was not rewritten. An exact immutable
`axisymmetric_passive_initial_snapshot.py` was recovered afterward; its SHA-256
matches the original recorded solver hash, confirming that only the refinement
entrypoint was appended. The refinement record has its own current source hashes (`axisymmetric_passive.py`
`09d0d38c...`, design `89dc6d6a...`), and the final files are now frozen for
review. This evidence validates a small, shallow numerical benchmark only; it
does not reproduce the source paper or establish snap-through, stability, or a
finite-amplitude area-response law.

## Lead provenance addendum

After the review, the lead also recovered `axisymmetric_design_initial_snapshot.json` by removing only the later refinement amendment and verified its exact SHA-256 against the original result. Both historical source and design are now available as hash-matching snapshots. This supersedes the earlier statement that the historical design text was unavailable. Current refinement source/design hashes were verified again at checkpoint. No numerical values or original result hashes were changed.
