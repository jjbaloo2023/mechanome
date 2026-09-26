# Passive nonlinear membrane solver: first validation

Task `axisymmetric-passive-001`, attempt 1. Scheduled delivery was
2026-09-24T21:31:55.561Z; the first observed tool clock was 21:32:06 UTC.
The cycle target is 21:52:06 UTC. This is a research-only implementation;
the production cap solver is unchanged.

## Mathematical convention

The implemented candidate follows the stated energy and supplement equations
of [Hassinger arXiv v1](https://arxiv.org/html/1604.08629v1), with no pressure or
applied force, uniform bending stiffness and a prescribed smooth coat profile.
The main-text/supplement sign conflict remains a source-version discrepancy.
We select the supplement's positive tension-gradient term because
`lambda'=-partial W/partial s|explicit=2k(H-C)C'` for `W=k(H-C)^2`
under its multiplier convention. This is not a claim about unobtained author code.

The source's bending modulus equals twice the repository modulus, and its
preferred mean curvature equals half the repository's preferred total curvature.
Lengths use `ell=sqrt(kappa_repo/sigma)`; the dimensionless reservoir tension
is therefore 1/2. The independent coordinate is accumulated material area,
`alpha=a/(2*pi*ell^2)`, not projected area.

The six variables are radius, height, tangent angle, local mean curvature,
curvature-gradient moment L and tension. Regular expansions start the calculation
at a small positive area cutoff. Three unknown pole values, together with the
outer flat-height, flat-angle and reservoir-tension conditions, determine the
boundary-value solution. See [AXISYMMETRIC_THEORY.md](AXISYMMETRIC_THEORY.md).

## Independent check of internal force balance

For source modulus scaled to one, define

`Q=r*((H-C)*(H+C-sin(psi)/r)-lambda)*sin(psi)+L*cos(psi)`.

Direct differentiation using the passive equations gives `dQ/ds=0`; regular
pole data require Q=0. The lead derived this independently and the theory
specialist verified it. A complex-step directional check at 1,000 declared
regular states gives maximum `|dQ/ds|=3.51e-16` with the positive tension term.
Switching only that term's sign gives the nonzero residual
`4*r*(H-C)*C'*sin(psi)`, matching to 3.52e-16. This checks consistency of the
equation system; it is not evidence that a biological membrane obeys it.
The inspectable record is [axisymmetric_lead_checks.json](axisymmetric_lead_checks.json).

## Numerical evidence and disposition

The independent implementation review accepts a **limited shallow passive
benchmark**. Ten registered baseline/sensitivity cases converged, with maximum
RMS ODE residual 1.00e-5, tiny boundary residuals, and maximum relative axial-force
imbalance 9.65e-7. Three focused tests passed in 5.69 seconds. These are numerical
checks within the chosen equations, not a validation of a biological mechanism.

At nominal coat radius x=1 and c_repo*ell=0.01, the normalized apex curvature
is 0.60193559; the independently integrated smooth-profile linear reference
is 0.60193199 (relative difference 5.98e-6). The sharp-edge reference is
0.60190723; its extra discrepancy includes the deliberately smoothed coat edge.
The mean curvature over the coat is more sensitive to that edge: its discrepancy
from the sharp reference falls from 2.02% to 0.509% as width falls 0.02 to 0.005.

| Check at x=1 | Observed change or outcome |
| --- | --- |
| Axis cutoff 1e-6 to 2.5e-7 | Apex changes about 2.0e-7 relative |
| Finer mesh and tighter tolerance | Apex changes about 4.6e-6 relative |
| Outer domain radius 14 to 20 | Apex changes about 1.5e-5 relative |
| Tighter solve, amplitude 0.005 | Smooth-reference apex error 3.14e-7; converged |
| Tighter solve, amplitude 0.01 | Error 1.26e-6; converged |
| Tighter solve, amplitude 0.02 | Node limit reached; RMS residual 0.397; rejected |

The two successful tight cases show a fourfold discrepancy reduction when
amplitude is halved, consistent with the expected quadratic normalized correction.
The unsuccessful high-amplitude refinement is retained and its output values are
excluded from physical interpretation. It neither demonstrates a new branch nor
refutes a membrane mechanism. Stringent validation at that point remains open.

The preserved records are [axisymmetric_results_001.json](axisymmetric_results_001.json)
and [axisymmetric_amplitude_refinement.json](axisymmetric_amplitude_refinement.json).
Current source/design hashes match the refinement. After adding the refinement
entry point, the lead reconstructed exact original solver and design snapshots
and verified both against the original result hashes. Those snapshots preserve
reproducibility without rewriting the original JSON. An initial write-denied
execution was rerun; its unsaved values are not evidence. The declared 45-second
per-solve target was not enforced by the code; recorded accepted solves took at
most 9.16 seconds. See [AXISYMMETRIC_REVIEW.md](AXISYMMETRIC_REVIEW.md).

The next step is numerical conditioning, not a larger-deformation study. Use
rho=sqrt(2*alpha) as an alternative material-area coordinate, verify equivalence
with S40, enforce an actual bounded subprocess runtime, and retest the failed
case while preserving these results. This coordinate is a material-area label,
not the membrane's physical radius. The proposed repair is not implemented yet.

## Collaboration and limits

Two specialists ran: mathematical derivation and numerical implementation.
Starting a third reviewer and restarting a previous reviewer both failed with
`agent thread limit reached`. The theory specialist consequently reviews the
numerical implementation, while the lead independently checks the theory.
This is independent implementation review, not three separate specialists or
an independent reviewer of every mathematical assumption.

The calculation is restricted to shallow passive solutions and supplies no
claim about force scaling, unstable branches, snap-through, published-figure
reproduction, biological parameter estimates or literature novelty.
