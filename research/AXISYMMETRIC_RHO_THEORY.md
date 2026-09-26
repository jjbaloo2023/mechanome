# Regular material-area coordinate for the passive axisymmetric system

Task `axisymmetric-rho-theory-001`, parent task `axisymmetric-passive-001`
attempt 2. The first tool clock observed
for this derivation was 2026-09-24 23:03:33 UTC. This note transforms the frozen
attempt-1 stated-energy/supplement-S40 model. It does not change the physical
equations, coat definition, boundary conditions, or source-version disposition.

The arXiv v1 main Eq. 3 versus supplement S13/S27/S40c sign discrepancy remains
unresolved as an author-code or publication-history question. As in attempt 1,
the implemented mathematical model uses the supplement's positive term because
it follows from the stated energy and multiplier convention:

\[
\lambda_{,\gamma}=-{\partial W\over\partial x^\gamma}\bigg|_{\rm exp}
=2k(H-C)C_{,\gamma},\qquad W=k(H-C)^2.
\]

This remains a stated-energy model, not a claimed reproduction of the authors'
unobtained numerical code.

## Coordinate transformation

Retain the dimensionless material area and variables from attempt 1,

\[
\alpha={a\over2\pi\ell^2},\qquad
\ell=\sqrt{\kappa_{\rm repo}/\sigma},\qquad
k_{\rm source}=2\kappa_{\rm repo},\qquad
C={c_{\rm repo}\ell\over2},
\]

and define a new independent coordinate

\[
\boxed{\rho=\sqrt{2\alpha}},\qquad
\alpha={\rho^2\over2},\qquad
{dY\over d\rho}=\rho {dY\over d\alpha}. \tag{1}
\]

The symbol \(\rho\) is a material-area label. It is not the physical radial
state \(r\). They agree at leading order near a regular pole and for an exactly
flat disk, but at finite slope

\[
{d\over d\rho}{r^2\over2}=\rho\cos\psi,\qquad
{r^2\over2}=\int_0^\rho u\cos\psi(u)\,du, \tag{2}
\]

so generally \(r(\rho)\ne\rho\). In particular, an outer label
\(\rho_{\max}=14\) means \(\alpha_{\max}=98\); it does not assert that the
deformed physical boundary radius equals 14.

Let a subscript \(\rho\) denote differentiation and define

\[
F=2H[(H-C)^2+\lambda]
-2(H-C)\left[H^2+\left(H-{\sin\psi\over r}\right)^2\right]. \tag{3}
\]

For homogeneous dimensionless rigidity one, pressure zero, and force zero,
the transformed six-state system is

\[
\begin{aligned}
r_\rho&={\rho\over r}\cos\psi,\\
z_\rho&={\rho\over r}\sin\psi,\\
\psi_\rho&={\rho\over r^2}(2rH-\sin\psi),\\
H_\rho&={\rho L\over r^2}+C_\rho,\\
L_\rho&=\rho F,\\
\lambda_\rho&=2(H-C)C_\rho.
\end{aligned} \tag{4}
\]

Equation (4) is exactly Eq. S40 multiplied by \(d\alpha/d\rho=\rho\).
It is a reparameterization, not a new membrane model. The exact boundary
conditions remain

\[
r(0)=\psi(0)=L(0)=0,\qquad
z(\rho_{\max})=\psi(\rho_{\max})=0,qquad
\lambda(\rho_{\max})={1\over2}. \tag{5}
\]

The factor \(1/2\) again follows from
\(\sigma\ell^2/k_{\rm source}=1/2\).

## Material-area coat profile

The coat remains prescribed in \(\alpha\), including its width. For the frozen
tanh profile,

\[
C(\rho)={C_*\over2}\left[1-
\tanh\left({\rho^2/2-\alpha_c\over w}\right)\right], \tag{6}
\]

and

\[
C_\rho=-{C_*\rho\over2w}\operatorname{sech}^2
\left({\rho^2/2-\alpha_c\over w}\right). \tag{7}
\]

Here \(\alpha_c=x^2/2\) and \(w\) retains its material-area units. Replacing
Eq. (6) by a tanh in \(\rho-\rho_c\), or treating \(w\) as a rho width, changes
the physical coat profile and is not a coordinate transformation.

## Regular pole expansion

Let

\[
C(\rho)=C_0+{\dot C_0\over2}\rho^2+O(\rho^4),
\]

where \(\dot C_0=dC/d\alpha|_0\), and let the unknown pole data be
\(z_p,H_p,\lambda_p\). Define

\[
d_p=H_p-C_0,\qquad Q_p=\lambda_p-C_0d_p,\qquad
h_2={\dot C_0+H_pQ_p\over2}. \tag{8}
\]

The attempt-1 expansion is already a series in \(\rho=\sqrt{2\alpha}\), so it
is unchanged:

\[
\begin{aligned}
r&=\rho-{H_p^2\over8}\rho^3+O(\rho^5),\\
\psi&=H_p\rho+
\left({h_2\over2}+{H_p^3\over24}\right)\rho^3+O(\rho^5),\\
z&=z_p+{H_p\over2}\rho^2+{h_2\over8}\rho^4+O(\rho^6),\\
H&=H_p+h_2\rho^2+O(\rho^4),\\
L&=H_pQ_p\rho^2+O(\rho^4),\\
\lambda&=\lambda_p+d_p\dot C_0\rho^2+O(\rho^4).
\end{aligned} \tag{9}
\]

A computation may still start at \(\rho_0=\sqrt{2\alpha_0}>0\) to avoid
evaluating removable zero-over-zero expressions exactly at the pole. Keeping
the displayed terms gives absolute cutoff errors

\[
\delta r,\delta\psi=O(\rho_0^5),\quad
\delta z=O(\rho_0^6),\quad
\delta H,\delta L,\delta\lambda=O(\rho_0^4). \tag{10}
\]

Thus the physical cutoff and asymptotic data are unchanged when the same
\(\alpha_0\) is used. The practical benefit is that a mesh uniform or adaptive
in \(\rho\) no longer compresses the regular square-root variation into an
\(\alpha\)-coordinate endpoint. Whether that actually removes the previous
node bottleneck is a numerical question for attempt 2, not a consequence of
the algebra alone.

## Equivalence and residual diagnostics

The axial-force first integral is a scalar property of the physical solution
and is unchanged by reparameterization:

\[
\mathcal Q=r\left[(H-C)\left(H+C-{\sin\psi\over r}\right)-\lambda\right]
\sin\psi+L\cos\psi=0. \tag{11}
\]

A valid coordinate repair should satisfy all of the following at identical
material-domain, coat, amplitude, cutoff, and tolerance controls:

1. Match the accepted attempt-1 pole observables and geometric outputs within
   declared tolerances.
2. Match state profiles after evaluating both solutions on a common material
   grid, using \(\alpha=\rho^2/2\). Comparing arrays at equal indices is not an
   equivalence check because the meshes use different coordinates.
3. Preserve the outer conditions, finite-cutoff series, coat integral, and
   algebraic force balance \(\mathcal Q\).
4. Demonstrate any claimed conditioning improvement through convergence of the
   previously failed case, or fewer nodes/runtime at comparable physical error,
   while retaining every failure.

Solver-reported ODE residuals need special care. If the alpha-form absolute
defect is \(R_\alpha=Y_\alpha-F_\alpha\), the transformed absolute defect is

\[
R_\rho=Y_\rho-\rho F_\alpha=\rho R_\alpha,
\qquad R_\alpha={R_\rho\over\rho}. \tag{12}
\]

Moreover, `solve_bvp` normalizes its residual by the coordinate-specific right
hand side and integrates it over coordinate-specific mesh intervals. Its native
RMS residual is therefore not invariant under Eq. (1). A smaller rho-coordinate
RMS or a shared tolerance label cannot by itself establish greater physical
accuracy. Report the native rho residual, a reconstructed alpha-form defect on
the finite domain, boundary residuals, \(\mathcal Q\), and observable/profile
equivalence. Near \(\rho_0\), division by \(\rho\) magnifies numerical noise;
the cutoff study and regular series remain the appropriate axis checks.

## Decision after this repair gate

If attempt 2 establishes equivalence and resolves the node bottleneck, the next
smallest falsifiable physics calculation is one bounded passive material-area
sign test at moderate deformation. Continue the validated shallow branch in
amplitude, then compare apex mean curvature at three fixed coat material areas
while holding reservoir tension, total material area, edge width, rigidity,
pressure, and force fixed. Predeclare a moderate-slope stop and stop before a
fold or narrow neck. The transferred area-curvature signature is supported only
if apex curvature decreases across the declared area points; a reversed or
multivalued response falsifies a simple continuation of the passive cap/linear
sign. Report material and projected areas, depth measures, and a declared apex
fit observable separately.

This is preferable to beginning a full published area/tension map: it directly
tests the research question beyond the linear limit with one controlled branch,
while avoiding premature claims about unstable branches, stability, force, or
author-code reproduction.
