# Bounded passive area-curvature sign test

Task `passive-area-theory-001`, parent task `passive-area-sign-001`, attempt 1.
The first tool clock observed for this task was 2026-09-25 00:47:30 UTC. This
note defines one bounded nonlinear comparison on the passive branch connected
to the validated shallow solution. It does not begin a tension map, locate
folds, establish stability, infer force, or reproduce unobtained author code.

## Fixed model and controls

Use the accepted rho-coordinate form of the homogeneous passive supplement-S40
model,

\[
\rho=\sqrt{2\alpha},\qquad \alpha={a\over2\pi\ell^2},\qquad
\ell=\sqrt{\kappa_{\rm repo}/\sigma},
\]

with \(k_{\rm source}=2\kappa_{\rm repo}\),
\(C_{\rm source}=c_{\rm repo}/2\), \(p=0\), \(f=0\), dimensionless rigidity
one, and outer tension \(\lambda(\alpha_{\max})=1/2\). The energy-consistent
positive tension-gradient sign remains the implemented mathematical convention.
The arXiv v1 main-equation/supplement discrepancy remains unresolved as a
source-version question.

The comparison fixes

\[
\alpha_{\max}=98,\qquad w_\alpha=0.01,
\]

and uses three half-height material coat labels

\[
x\in\{0.5,1,2\},\qquad \alpha_c={x^2\over2}
\in\{0.125,0.5,2\}. \tag{1}
\]

At every point the prescribed source spontaneous curvature is

\[
C(\alpha)={C_*\over2}
\left[1-\tanh\left({\alpha-\alpha_c\over w_\alpha}\right)\right],
\qquad C_*={c_{\rm repo}\ell\over2}. \tag{2}
\]

The labels in Eq. (1) are material-area controls and the tanh half-height
locations. They are not physical radii and not exact binary coat areas. The
smooth weighted area is \(\int g(\alpha)d\alpha\), where
\(g=C/C_*\); for the present well-separated center and edge it is close to
\(\alpha_c\), but the calculation should retain the distinction.

## Continuation and stopping rules

For each \(x\), solve the ascending amplitude sequence

\[
c_{\rm repo}\ell\in\{0.02,0.1,0.3,0.6\}. \tag{3}
\]

The first case uses the declared shallow seed. Each later case uses only the
immediately preceding accepted solution for the same \(x\). The three area
sequences remain separate. This local parameter continuation identifies only a
computed branch connected to the shallow seed; it is not a branch-enumeration
or stability method.

Preserve a case and stop that area sequence if any of the following occurs:

1. timeout, exception, nonzero solver status, or a failed residual/boundary/
   force-balance gate;
2. any nonfinite state or nonpositive physical radius away from the pole
   cutoff;
3. \(\max|\psi|\ge0.6\) radians, equivalently reaching the declared
   moderate-slope boundary before a neck is approached;
4. a large discontinuous state/observable jump that makes simple continuation
   tracking doubtful.

The \(0.6\)-radian threshold is a scope boundary, not a stability criterion.
A failed solve or abrupt jump is not evidence of a physical fold. Do not retry
through it with alternative seeds in this task, and do not attempt higher
amplitudes in that sequence.

Use at most 12 base solves plus one joint mesh/cutoff sensitivity at the
strongest accepted base state, selected by largest \(\max|\psi|\) with a
predeclared tie rule. Require finite states, solver success, native rho RMS no
larger than 1.01 times the frozen tolerance, outer and finite-cutoff boundary
errors no larger than \(10^{-8}\), and normalized axial-force residual no
larger than \(10^{-6}\). The sensitivity changes only the declared mesh and
cutoff and requires every normalized observable to change by at most
\(2\times10^{-5}\). Because both controls change together, it is a joint
robustness check and cannot apportion their effects.

Native rho-coordinate residual norms remain coordinate dependent. Acceptance
rests on the complete set of status, boundary, pole, axial-force, finite-state,
sensitivity, and continuation checks, not on comparing the rho RMS numerically
with an alpha-coordinate RMS.

## Fair area comparison

At a given amplitude, compare areas only when all three sequences have an
accepted case at that same amplitude. The primary observable is the extrapolated
pole mean curvature normalized by the shared source amplitude,

\[
y(x;c)={H_{\rm apex}(x;c)\over C_{\rm source}(c)}. \tag{4}
\]

Because \(C_{\rm source}\) is identical across the three areas at fixed \(c\),
ordering \(y\) is exactly equivalent to ordering dimensional apex mean
curvature. Normalization only permits comparison across amplitudes.

Let \(\delta_{\rm sens}\) be the absolute normalized-apex change in the
strongest-state sensitivity and define

\[
\epsilon=\max(10^{-5},2\delta_{\rm sens}). \tag{5}
\]

At a shared accepted amplitude, classify the sampled ordering as

\[
\begin{array}{ll}
\text{preserved:}&y(0.5)-y(1)>\epsilon
\ \text{and}\ y(1)-y(2)>\epsilon,\\
\text{reversed:}&\text{either adjacent difference}< -\epsilon,\\
\text{unresolved:}&\text{otherwise.}
\end{array} \tag{6}
\]

A preserved result supports the passive negative area ordering only at these
sampled material labels, amplitudes, and on the tracked branch. Three samples
do not prove continuous monotonicity, uniqueness, or a global area sign. A
reversal falsifies the simple transfer of the cap/linear ordering at those
controls, but by itself does not identify its cause or imply active force. An
unresolved or incomplete shared set supports no sign conclusion at that
amplitude.

## Measurement and area distinctions

Report the following separately for every retained case:

- \(H_{\rm apex}=H(0)\), the local mathematical tip mean curvature;
- \(\langle H\rangle_{\rm coat}=\alpha_c^{-1}
  \int_0^{\alpha_c}H\,d\alpha\), the unweighted nominal material-region mean;
- reservoir depth \(-z(0)\) and edge-referenced depth
  \(z(\alpha_c)-z(0)\);
- nominal material label \(\alpha_c\), smooth weighted coat area
  \(\int g\,d\alpha\), projected edge area \(r(\alpha_c)^2/2\), fixed total
  material area 98, and total projected area \(r(\alpha_{\max})^2/2\).

These quantities are not interchangeable at finite slope. In particular,
projected area changes with geometry even though the material labels are fixed.
The solver's pointwise apex curvature is also not automatically an experimental
observable; microscopy requires a declared finite-window tip fit, applied in
the same way to simulated and measured shapes.

## Decision after the bounded result

If the ordering is preserved through informative moderate states, stop expanding
the mechanical sweep and next test observational usefulness: apply a declared
tip-fit window and plausible spatial resolution/noise to the accepted forward
shapes, then ask whether the sampled area differences remain distinguishable.
That directly addresses whether the theoretical sign can constrain data.
Existing repository audits note that public LocMoFit outputs fit spherical-cap
area and closing angle and derive curvature algebraically, with shared fit
errors. The observation bridge should therefore vary the finite profile window
and nuisance weighting jointly and keep pointwise apex curvature distinct from
cap-fitted curvature. Unless the actual experimental likelihood is implemented,
describe this only as a synthetic observation surrogate.

If a reversal appears, first perform one targeted numerical confirmation around
the first reversed pair with an independent mesh/cutoff check; do not launch a
full area/tension map or infer a mechanism. If the sequences stop before an
informative shared amplitude, report the concrete limitation and reassess
whether repairing it would materially improve the biological question. This
decision rule prevents an open-ended progression of solver studies.

## Registered-design correction (2026-09-25 02:11:11 UTC)

The prose above was written before the completed frozen numerical design was
available. The registered design is authoritative where it is stricter: outer
boundary errors must be no larger than \(10^{-9}\), and the joint mesh/cutoff
sensitivity requires every normalized observable to change by no more than
\(2\times10^{-6}\). These replace the historical \(10^{-8}\) and
\(2\times10^{-5}\) values above for review of this attempt.

The frozen implementation enforces solver, finite-state, positive-radius,
\(\max|\psi|\), \(\min\cos\psi\), residual, boundary, and axial-force stops.
It does not implement the prose-only large-jump continuation stop. Therefore
the saved results cannot be said to have passed such a gate retroactively.
Adjacent changes may be reported descriptively, but branch continuity rests
only on accepted preceding-state seeding and the implemented checks. This
limits the inference to sampled solutions reached by that continuation; it
does not establish stability, uniqueness, or absence of missed branches.
