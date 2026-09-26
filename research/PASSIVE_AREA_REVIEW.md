# Independent review: bounded passive area-sign result

Task `passive-area-review-001`, parent task `passive-area-sign-001`, attempt 1.
This is a saved-result review only; no boundary-value problem was rerun. The
tool clock observed after the independent geometry record became available was
2026-09-25 02:13:37 UTC.

## Disposition

**Accept a sampled negative apex-curvature area ordering at all four shared
amplitudes, limited to the computed mild-to-moderate solutions and stated
controls.** All 12 base cases and the one joint mesh/cutoff sensitivity pass
the frozen numerical gates. At each common amplitude,

\[
{H_{\rm apex}(x=0.5)\over C_{\rm source}}>
{H_{\rm apex}(x=1)\over C_{\rm source}}>
{H_{\rm apex}(x=2)\over C_{\rm source}}.
\]

The accepted statement concerns these three material coat labels on solutions
reached by the saved continuation. It is not a proof of continuous or global
monotonicity, branch uniqueness, stability, a force mechanism, or reproduction
of the source authors' computation.

The shapes remain below the preregistered scope boundary: the largest
\(\max|\psi|\) is 0.26785 radians (15.3 degrees), well below 0.6 radians. They
should be described as mild-to-moderate deformations rather than deep buds.

## Frozen model and implementation

The source imports the accepted frozen rho-coordinate passive equations. It
keeps total material area 98, material edge width 0.01, outer tension 0.5,
homogeneous rigidity, and zero pressure and force fixed. The coat labels are
\(x=0.5,1,2\), corresponding to half-height material labels
\(\alpha_c=0.125,0.5,2\). The four amplitudes are
\(c_{\rm repo}\ell=0.02,0.1,0.3,0.6\).

The imported equations use the energy-consistent positive spontaneous-
curvature contribution to the tension gradient. That is the supplement-S40
model reviewed previously. The opposite sign printed in arXiv v1 main Eq. 3
remains an unresolved source-version discrepancy, so this result is not an
author-code reproduction.

The current source and design exactly match their frozen copies and the hashes
stored in the result. All 13 NPZ hashes match their records. The first case in
each area sequence uses the declared shallow seed; every later case names the
immediately preceding accepted state and its recorded seed hash matches that
file. The sensitivity uses the strongest accepted base state, \(x=2,c=0.6\),
selected by largest recorded \(\max|\psi|\).

The implementation stops a sequence on solver, residual, boundary,
force-balance, finite-state, positive-radius, or geometry failure. It does not
implement the theory note's prose-only large-jump gate. That gate cannot be
claimed retroactively. The saved predecessor seeding establishes how the
solutions were reached, but simple parameter stepping does not prove continuous
branch tracking or exclude missed solutions.

Three targeted mocked-control-flow tests pass. They confirm that a stopped
sequence does not retry higher amplitudes, an accepted case seeds the next
amplitude in its own area sequence, and mocked orchestration does not change the
saved result artifact. These tests verify control flow and preservation only;
they do not add physical validation.

## Registered gates and saved-state checks

The stricter frozen design limits govern this review: outer boundary error
\(\le10^{-9}\) and normalized-observable sensitivity \(\le2\times10^{-6}\).
All 12 base records and the sensitivity report solver status zero and every
implemented gate true. Across them:

- maximum native rho RMS residual is \(9.998\times10^{-9}\), below the
  \(1.01\times10^{-8}\) limit;
- maximum outer boundary error is \(6.28\times10^{-30}\);
- maximum normalized axial-force residual is \(5.41\times10^{-11}\);
- all states are finite with positive radius away from the pole;
- the joint sensitivity changes any normalized observable by at most
  \(8.25\times10^{-9}\), below \(2\times10^{-6}\).

The frozen result omitted an explicit pole-residual field and gate. The lead
reconstructed every saved state with cubic Hermite interpolation and frozen-RHS
derivatives, without solving a BVP. The explicit finite-cutoff pole residual is
at most \(2.78\times10^{-17}\), below the \(10^{-9}\) boundary standard.
Eight-point Gauss integration on every mesh interval reproduces the stored coat
means within \(2.081\times10^{-6}\), below the independently registered
\(2\times10^{-4}\) quadrature check. The projected-area identity agrees to
relative error \(1.67\times10^{-11}\); apex and both depth observables reproduce
exactly at stored precision.

These are valuable implementation checks on the same saved solutions, not
independent physical evidence. The native rho residual is coordinate dependent,
and the mesh/cutoff sensitivity changes two numerical controls together, so it
cannot assign their separate effects or serve as a global error bound.

## Sampled sign result

The sensitivity gives a normalized-apex change of about
\(4.0\times10^{-10}\), so the preregistered decision margin remains
\(\epsilon=10^{-5}\). The normalized apex values and adjacent decreases are:

| \(c_{\rm repo}\ell\) | \(x=0.5\) | \(x=1\) | \(x=2\) | decreases |
| ---: | ---: | ---: | ---: | ---: |
| 0.02 | 0.828358 | 0.601935 | 0.279737 | 0.226423, 0.322198 |
| 0.10 | 0.828383 | 0.602008 | 0.279790 | 0.226375, 0.322217 |
| 0.30 | 0.828587 | 0.602615 | 0.280240 | 0.225973, 0.322374 |
| 0.60 | 0.829280 | 0.604698 | 0.281811 | 0.224582, 0.322888 |

Every adjacent decrease exceeds the decision margin by more than four orders of
magnitude. The sampled ordering is therefore preserved at every shared accepted
amplitude. The conclusion is intentionally discrete: three area labels do not
establish the derivative sign between them, and the missing jump gate prevents
a stronger continuation claim.

The nonlinear change in normalized apex curvature over the tested amplitude
range is modest. For example, at \(x=0.5\) it rises only about 0.11% from 0.02
to 0.6; even the largest relative shift among the three areas is about 0.74%.
The calculation mainly confirms persistence of the shallow ordering over a
mild-to-moderate range, rather than revealing a new nonlinear transition.

## Measurement distinctions and practical meaning

The strongest case makes the measurement-functional issue concrete. At
\(x=2,c_{\rm repo}\ell=0.6\), normalized apex curvature is 0.281811 while the
nominal material-region coat mean is 0.445126, about 58% larger than the apex
value. Reservoir depth and coat-edge-referenced depth likewise remain distinct.
Projected coat area falls below its fixed material label as slope grows; in the
strongest case it is 1.97267 versus material label 2.0. These quantities must
not be substituted for one another.

The result does not store the smooth weighted coat area
\(\int(C/C_*)\,d\alpha\) requested in the theory note. It stores the tanh
half-height material label \(\alpha_c\), which is the actual controlled area
coordinate used for this sampled comparison. The omission prevents reporting
the weighted area as a separate measured output, but it does not change the
ordering of the declared labels under the common fixed profile and width.

The primary result uses pointwise mathematical apex curvature. Existing public
LocMoFit records instead fit spherical-cap area and closing angle and derive
curvature with shared fit errors. The present result therefore does not yet
define a directly measured sign or an experimental force estimate.

## Reliability limits and next decision

The completed artifacts are internally consistent, but the frozen runner allows
state NPZ overwrite, lacks a cycle-wide UTC deadline, and relied only on local
45-second subprocess timeouts. The earlier outer tool-cell termination did not
stop descendant work. These are future execution-durability requirements; they
do not alter the verified hashes of this completed result.

Do not expand the area/amplitude solver sweep next. The useful next bounded
question is a synthetic observation surrogate: fit accepted profiles over
declared finite tip windows while varying window size and nuisance weighting,
then test whether the area ordering survives the measurement functional and
plausible resolution/noise. Keep pointwise apex, cap-fitted curvature, and coat
mean separate. Unless the actual experimental likelihood is implemented, this
must not be described as a biological fit or empirical mechanism test.
