# Independent review: regular-rho coordinate repair

Task `axisymmetric-rho-review-001`, parent task `axisymmetric-passive-001`
attempt 2. The review used the frozen attempt-2 source, design, result, numerical
note, and the lead's independent formula and preservation checks. The tool clock
observed at final review was 2026-09-24 23:22:54 UTC.

## Disposition

**Accept the rho reparameterization as a coordinate-equivalent conditioning
repair for the bounded passive benchmark.** All four registered attempt-2 cases
converged, including the \(c_{\rm repo}\ell=0.02\) case that previously exceeded
the 12,000-node limit. The two previously accepted tight solutions agree in all
four stored observables to at most \(6.38\times10^{-9}\), far below the
predeclared \(2\times10^{-6}\) gate. The repair changes neither the passive
physics nor the material-area coat.

This disposition does not validate larger deformation, a high-tension area
sweep, unstable branches, stability, force, a biological interpretation, or a
reproduction of the authors' code. The arXiv v1 main-equation/supplement
tension-gradient sign conflict remains unresolved as a source-version matter.

## Equation and implementation review

The implementation correctly applies

\[
\rho=\sqrt{2\alpha},\qquad {dY\over d\rho}=\rho{dY\over d\alpha}
\]

to all six S40 equations. It evaluates the unchanged coat at
\(\alpha=\rho^2/2\), retains the edge width in material-area units, and uses
the unchanged finite-cutoff pole series. The half-height coat edge is evaluated
at \(\rho=x\) because \(\alpha_c=x^2/2\). The code does not equate the material
label \(\rho\) with the physical radial state \(r\).

The lead compared the new `alpha_rhs` with the frozen attempt-1 right-hand side
at 1,000 arbitrary regular states and found zero maximum absolute difference.
Forty pole-series comparisons at both registered cutoffs agree to
\(3.31\times10^{-24}\). These checks establish algebraic equivalence more
directly than comparing solver tolerance labels.

Each case executes in a separate subprocess with an enforced 45-second timeout.
The parent preserves timeout, process, exception, and solver failures as records
and creates the result exclusively after collecting them. No attempt-2 case
failed or timed out. The exact execution source and design are preserved as
`axisymmetric_rho_frozen_002.py` and
`axisymmetric_rho_design_frozen_002.json`; both byte hashes match the runtime
files and the hashes stored in the result. The independent preservation check
also confirms that every frozen attempt-1 artifact is unchanged. Earlier
attempt-2 draft snapshots remain present as superseded edit history.

## Numerical evidence

The native rho-coordinate maximum RMS residual is at most
\(9.99\times10^{-9}\), outer boundary errors are below
\(3.1\times10^{-32}\) for angle and effectively zero for height and tension,
and finite-cutoff boundary residuals are below \(1.7\times10^{-21}\). The
largest normalized axial-force residual is \(9.55\times10^{-13}\).

At \(c_{\rm repo}\ell=0.005\), the new solution uses 1,195 nodes and 0.275 s,
versus 11,277 nodes and 8.91 s in the accepted tight alpha-coordinate result.
At 0.01 it uses 1,277 nodes and 0.391 s, versus 11,941 nodes and 9.16 s. The
rho computation therefore uses about one-tenth as many nodes for the matched
solutions. Runtime is also substantially lower, though wall-time ratios are
secondary to solution equivalence.

The formerly failed \(c_{\rm repo}\ell=0.02\) case now converges in 1,363 nodes
and 0.404 s. Its joint finer-mesh/smaller-cutoff case converges in 2,161 nodes
and 0.421 s. Their four observables differ by at most
\(1.84\times10^{-9}\), passing the registered sensitivity gate. Because mesh
and cutoff changed together, this case demonstrates joint robustness and cannot
attribute the difference separately to either control.

The smooth-linear apex errors are \(3.24\times10^{-7}\),
\(1.26\times10^{-6}\), and \(5.03\times10^{-6}\) as amplitude doubles from
0.005 to 0.01 to 0.02. The approximately fourfold increments retain the
expected quadratic normalized correction on this shallow branch.

## Residual and equivalence caveats

Native `solve_bvp` RMS residuals are coordinate dependent. Under the change of
variable, the absolute defects obey \(R_\rho=\rho R_\alpha\), while solver
normalization and interval quadrature also change. The smaller node count and
successful status support a conditioning improvement only because boundary
conditions, invariants, formulas, and physical observables also agree. A lower
rho residual cannot be compared numerically with the old alpha residual as if
the norms were identical.

The stored off-mesh diagnostic compares the invariant arc-length forms
\((r/\rho)Y_\rho\) and \(rY_\alpha\) at fraction 0.37 of selected final mesh
intervals. Its largest component defect is \(1.23\times10^{-8}\). These points
avoid the midpoint collocation locations, but the diagnostic still evaluates
the same numerical spline and is supporting evidence rather than an independent
solution. Full attempt-1 profiles were not retained, only sparse profile values;
the review therefore requires observable equivalence and the independent
right-hand-side/pole checks rather than claiming full stored-profile identity.

## Next bounded decision

The next calculation should test the actual passive area-curvature question
rather than continue solver polishing. A suitable one-cycle design is an
ascending passive continuation at fixed material coat labels corresponding to
\(x=0.5,1,2\), using \(c_{\rm repo}\ell=0.02,0.1,0.3,0.6\), followed by one
independent mesh/cutoff check at the strongest accepted state. Hold reservoir
tension, total material area, material edge width, rigidity, pressure, and
force fixed. Stop at solver failure, nonpositive \(r\), suspicious tangent or
neck growth, or \(\max|\psi|\ge0.6\) radians.

Report apex and coat-mean curvature, both depth references, and material and
projected areas separately. The falsifiable question is whether apex mean
curvature still decreases with coat material area along the accepted moderate
branch. Simple parameter stepping does not robustly detect a fold and must not
be used to claim stability or absence of additional branches. After this one
bounded sign test, reassess whether a full published area/tension map would add
enough information to justify its larger scope.

## Lead checkpoint clarification

The result file is opened for exclusive creation before subprocess collection;
JSON content is written after collection. An empty in-progress file is not a
completed result. This corrects the creation-order wording above and changes
no numerical result or review disposition. The review document task ID is an
alias within the registered theory-and-review assignment, not a third worker.
