# Independent review: passive axisymmetric benchmark

Task `axisymmetric-passive-review-001`, attempt 1. The theory specialist
reviewed the numerical design, implementation, and retained results after
completing the equation derivation. The lead independently checked the pole
series and tension-sign invariant. This is independent implementation review,
not a third specialist and not a reproduction audit of unobtained author code.

## Disposition

**Accept the small-amplitude passive solver benchmark, with recorded procedural
and scope limitations.** The retained baseline solves the stated-energy,
supplement-S40 model and agrees with the matching smooth-profile linear apex
reference. Mesh/tolerance, axis-cutoff, outer-domain, edge-width, and force-
balance checks support that conclusion. The accepted result establishes only
this shallow passive benchmark. It does not validate a published nonlinear
area sweep, force protocol, snap-through branch, stability, or biological
interpretation.

## Convention and boundary-condition review

The implementation uses material area
\(\alpha=a/(2\pi\ell^2)\), \(\ell=\sqrt{\kappa_{\rm repo}/\sigma}\),
\(k_{\rm source}=2\kappa_{\rm repo}\), and
\(C_{\rm source}=c_{\rm repo}/2\). With \(k_0=k_{\rm source}\), its imposed
reservoir tension \(\lambda(\alpha_{\max})=1/2\) is correct. The six ODEs,
three finite-cutoff pole-series relations, and three outer conditions provide
nine boundary residuals for six state variables plus the three unknown pole
values \((H_p,z_p,\lambda_p)\).

The code uses the positive curvature-gradient term
\(\dot\lambda=2(H-C)\dot C\). This follows from
\(\lambda_{,\gamma}=-\partial W/\partial x^\gamma|_{\rm exp}\) and
\(W=k(H-C)^2\). arXiv v1 main Eq. 3 displays the opposite sign, whereas S13,
S27, and S40c display the implemented sign. The result is properly described
as the stated-energy/supplement model; the discrepancy is not declared a
published typo.

The regular pole implementation matches the independently derived expansion.
In particular, it does not impose \(r=\psi=L=0\) at a positive cutoff. It also
uses the extrapolated pole parameter \(z_p\), rather than the cutoff value of
\(z\), for both depth observables. The reported `pole_expansion_max_abs_error`
is an imposed boundary residual, not an independent accuracy test; pole
accuracy is instead supported by the separate cutoff sensitivity.

The coat is prescribed as a tanh profile in material area. The code does not
substitute projected area for coat or domain area. Its coat mean includes the
small omitted interval from zero to \(\alpha_0\) using the pole curvature.
Sharp-step comparisons are kept separate from the smooth-profile linear apex
reference.

## Code and residual checks

The reviewed solver callback has the required `solve_bvp` signature when
unknown parameters are present, captures each case's cutoff locally, uses the
current NumPy trapezoidal integrator, preserves failed cases, and does not add
pressure or force. The initial guess has the correct inner/outer Bessel signs.

All 10 retained cases in `axisymmetric_results_001.json` report solver status
zero. Their maximum RMS ODE residual is at most \(1.00\times10^{-5}\); outer
height and angle residuals are below \(8\times10^{-31}\), and the outer tension
residual is zero at stored precision. The independently derived axial-force
integral

\[
Q=r[(H-C)(H+C-\sin\psi/r)-\lambda]\sin\psi+L\cos\psi
\]

has maximum normalized residual \(9.65\times10^{-7}\) over these cases and
improves to about \(10^{-12}\) in the accepted tight-tolerance amplitude
refinement. The lead's separate complex-step check at 1,000 regular states
found maximum \(|dQ/ds|=3.50\times10^{-16}\) for the plus sign. Reversing only
the tension-gradient sign produces the predicted nonzero drift
\(4r(H-C)C'_s\sin\psi\), with formula error \(3.52\times10^{-16}\).

## Numerical comparison

At the baseline \(x=1\), \(c_{\rm repo}\ell=0.01\), width 0.01, cutoff
\(10^{-6}\), and outer radius 14, the computed normalized apex curvature is
0.60193559. The matching smooth-profile linear value is 0.60193199, a relative
difference of \(5.98\times10^{-6}\). The sharp-step value is 0.60190723; its
larger \(4.71\times10^{-5}\) discrepancy includes the deliberately finite
tanh edge and must not be attributed wholly to nonlinear geometry.

The registered sensitivities behave as follows:

- Reducing the cutoff from \(10^{-6}\) to \(2.5\times10^{-7}\) changes the
  normalized apex by about \(2.0\times10^{-7}\) relative.
- Refining from 401 nodes/tolerance \(10^{-5}\) to 801 nodes/tolerance
  \(3\times10^{-6}\) changes it by about \(4.6\times10^{-6}\) relative.
- Enlarging the outer radius from 14 to 20 changes it by about
  \(1.5\times10^{-5}\) relative.
- Narrowing the material-area edge width from 0.02 to 0.01 to 0.005 decreases
  the apex error against the sharp reference from \(1.81\times10^{-4}\) to
  \(4.71\times10^{-5}\) to \(1.35\times10^{-5}\). The coat-mean sharp-reference
  error decreases from 2.02% to 1.01% to 0.509%, consistent with a leading
  finite-width effect. Depth errors decrease in the same direction.

The original absolute tolerance did not resolve the amplitude trend: the
lowest-amplitude case had a larger normalized smooth-reference error because
the signal decreased while the solver tolerance stayed fixed. The preserved
tight-tolerance follow-up resolves the relevant small-amplitude side. At
\(c_{\rm repo}\ell=0.005\) and 0.01, the smooth-apex relative errors are
\(3.14\times10^{-7}\) and \(1.26\times10^{-6}\), respectively, a factor of
four consistent with a quadratic correction in amplitude. Both cases converge
with RMS residual at most \(1.00\times10^{-8}\) and normalized force-balance
residual below \(9.8\times10^{-13}\). The attempted
\(c_{\rm repo}\ell=0.02\) tight solve exceeded the 12,000-node cap and has RMS
residual 0.397; its observables are rejected and the failure is correctly
retained. That failed higher-amplitude point is not needed to accept the
one-sided small-amplitude convergence demonstrated by the other two.

The failed tight solve means stringent validation at the largest tested
amplitude remains unresolved. Before any high-tension or larger-deformation
sweep, the bounded next numerical repair is to solve in
\(\rho=\sqrt{2\alpha}\) as the independent material-area label. This keeps
the prescribed coat as \(C(\rho^2/2)\) while multiplying the S40 derivatives
by \(\rho\), which removes the explicit \(r\sim\sqrt{\alpha}\) conditioning at
the axis. That change is not implemented or tested in this cycle and requires
a new result artifact.

## Provenance and limitations

The first sandbox execution completed numerically but could not create the
result file under the initial write permissions; its unpreserved console-only
values are not used. The retained rerun was created at the recorded tool time
and completed all 10 cases. The command-level runtime was 24.1 seconds and
individual retained solves report 0.84-2.05 seconds. The design declared a
45-second per-solver limit, but the Python implementation does not itself
interrupt an individual solve at that limit. Because every accepted solve
finished far below it, this is a procedural limitation rather than evidence
against the numerical result.

`axisymmetric_results_001.json` preserves hashes of the solver and design at
that run. Afterward, the amplitude-refinement entry point and provenance
amendments changed the current hashes; the original result was not overwritten.
The lead removed only the appended refinement entry point from a copy and
recovered `axisymmetric_passive_initial_snapshot.py`, whose SHA-256
`9ced172841fc7c9c0245609f8ee19a6480ab86794f285998aee002a1beeed01b`
exactly matches the solver hash stored in the original result. This confirms
the original executable source cryptographically. A full historical copy of
the original design JSON was not retained, although every executed case input
is stored in the result and the amended design records the provenance changes.
`axisymmetric_amplitude_refinement.json` records the current hashes for the
follow-up. The linear benchmark and theory hashes agree between the original
result and the current files. Any future physics change requires a new result
artifact rather than relabeling attempt 1.

## Lead provenance addendum

After the review, the lead also recovered `axisymmetric_design_initial_snapshot.json` by removing only the later refinement amendment and verified its exact SHA-256 against the original result. Both historical source and design are now available as hash-matching snapshots. This supersedes the earlier statement that the historical design text was unavailable. Current refinement source/design hashes were verified again at checkpoint. No numerical values or original result hashes were changed.
