# Passive axisymmetric membrane: equations and regular pole data

Task `axisymmetric-passive-theory-001`, attempt 1. This note fixes the
mathematical model for the first passive nonlinear benchmark. It does not
implement a solver, reproduce the authors' code, or support a force, stability,
inverse-fitting, or biological claim.

The tool clock observed while deriving this note was 2026-09-24 21:35:46 UTC.
The primary source is Hassinger et al., arXiv:1604.08629v1, especially Eqs.
S10-S14, S18-S27, and S35-S41. Existing repository context was taken from
`NEXT_CYCLE.md`, `FULL_SHAPE_MAPPING.md`, `FULL_SHAPE_REVIEW.md`, and
`FULL_SHAPE_SOURCE.md`.

## Energy convention and the tension-gradient sign

The source uses

\[
W=k(H-C)^2+\bar kK,
\]

with its normal and curvature convention defined by S17-S21 and its area
constraint multiplier defined by \(\lambda=-(\gamma+W)\) in S8. The tangential
balance in S10 is

\[
\left({\partial W\over\partial x^\gamma}\bigg|_{\rm exp}
      +\lambda_{,\gamma}\right)a^{\beta\gamma}=0
\]

when no applied tangential force is present. At fixed shape, only the prescribed
field \(C(x)\) contributes to the explicit coordinate derivative:

\[
{\partial W\over\partial x^\gamma}\bigg|_{\rm exp}
=2k(H-C)(-C_{,\gamma})=-2k(H-C)C_{,\gamma}.
\]

Therefore, with the source's normal and multiplier conventions,

\[
\boxed{\lambda_{,\gamma}=+2k(H-C)C_{,\gamma}}. \tag{1}
\]

This is the sign in supplement Eqs. S13, S14, S27, S32c, and S40c. Main-text
Eq. 3 of arXiv v1 instead prints a minus sign on this curvature-gradient term.
The two displayed equations are mathematically inconsistent. This note selects
the plus sign because it follows from the stated energy and S10; it does not
label the main-text equation a publication typo and does not resolve what any
unobtained source-code version implemented. The present solver is consequently
an implementation of the stated-energy/supplement model, not yet a reproduction
of the published computation.

For comparison with repository notation,

\[
k_{\rm source}=2\kappa_{\rm repo},\qquad
C_{\rm source}={c_{\rm repo}\over2}. \tag{2}
\]

## Dimensionless material-area system

Choose

\[
\ell=\sqrt{\kappa_{\rm repo}/\sigma},\qquad k_0=k_{\rm source},
\qquad \alpha={a\over2\pi\ell^2}.
\]

Here \(a\) is accumulated **surface/material area**, not projected area. Define
dimensionless variables, and then omit hats below,

\[
r={r_{\rm phys}\over\ell},\quad z={z_{\rm phys}\over\ell},\quad
H=H_{\rm phys}\ell,\quad C=C_{\rm source}\ell
={c_{\rm repo}\ell\over2},\quad L=L_{\rm phys}\ell,
\quad \lambda={\lambda_{\rm phys}\ell^2\over k_{\rm source}}.
\]

The homogeneous modulus is then \(\widetilde k=1\). With pressure \(p=0\)
and force density \(\mathbf f=0\), source Eq. S40 becomes, with a dot denoting
\(d/d\alpha\),

\[
\begin{aligned}
r\dot r&=\cos\psi,\\
r\dot z&=\sin\psi,\\
r^2\dot\psi&=2rH-\sin\psi,\\
r^2\dot H&=L+r^2\dot C,\\
\dot L&=2H\left[(H-C)^2+\lambda\right]
-2(H-C)\left[H^2+\left(H-{\sin\psi\over r}\right)^2\right],\\
\dot\lambda&=2(H-C)\dot C.
\end{aligned} \tag{3}
\]

The exact pole and outer conditions corresponding to S41 are

\[
r(0)=\psi(0)=L(0)=0,\qquad
z(\alpha_{\max})=\psi(\alpha_{\max})=0,\qquad
\lambda(\alpha_{\max})={1\over2}. \tag{4}
\]

The last value follows exactly from Eq. (2) and the chosen length:

\[
{\sigma\ell^2\over k_{\rm source}}
={\kappa_{\rm repo}\over2\kappa_{\rm repo}}={1\over2}.
\]

No pole value of \(z\), \(H\), or \(\lambda\) is prescribed in this passive
problem; those values are determined by the two-point boundary-value solution.

## Regular expansion at the pole

The area equations contain divisions by \(r\) and \(r^2\), so a computation
should begin at a finite \(\alpha_0>0\) using regular asymptotic data. Put

\[
\rho=\sqrt{2\alpha},\qquad
C(\alpha)=C_0+\dot C_0\alpha+O(\alpha^2),
\]

and denote the unknown regular pole values by

\[
z_p=z(0),\quad H_p=H(0),\quad\lambda_p=\lambda(0),\quad
d_p=H_p-C_0,
\]

with

\[
Q_p=\lambda_p-C_0d_p,\qquad
h_2={\dot C_0+H_pQ_p\over2}. \tag{5}
\]

Substitution of power series into Eq. (3) gives

\[
\begin{aligned}
r(\alpha)&=\rho-{H_p^2\over8}\rho^3+O(\rho^5),\\
\psi(\alpha)&=H_p\rho+
 \left({h_2\over2}+{H_p^3\over24}\right)\rho^3+O(\rho^5),\\
z(\alpha)&=z_p+{H_p\over2}\rho^2+{h_2\over8}\rho^4+O(\rho^6),\\
H(\alpha)&=H_p+h_2\rho^2+O(\rho^4),\\
L(\alpha)&=2H_pQ_p\alpha+O(\alpha^2),\\
\lambda(\alpha)&=\lambda_p+2d_p\dot C_0\alpha+O(\alpha^2).
\end{aligned} \tag{6}
\]

For reference, the curvature line can equivalently be written

\[
H(\alpha)=H_p+[\dot C_0+H_pQ_p]\alpha+O(\alpha^2). \tag{7}
\]

The derivation uses the geometric leading limits
\(r\sim\rho\), \(\psi\sim H_p\rho\), and
\(\sin\psi/r\to H_p\). Equation (3e) then gives

\[
\dot L(0)=2H_p\{(H_p-C_0)^2+\lambda_p\}
-2(H_p-C_0)H_p^2=2H_pQ_p,
\]

which fixes both the linear term of \(L\) and the coefficient \(h_2\).
Equation (3f) fixes the first tension correction. Thus \(L=0\) at the exact
axis, but generally \(L(\alpha_0)\ne0\) at a finite cutoff.

At \(\alpha_0\), use Eq. (6) as the three regular left boundary relations,
with \(z_p,H_p,\lambda_p\) treated as unknown pole data (or eliminated
consistently). Keeping the displayed terms gives absolute truncation errors

\[
\delta r=O(\alpha_0^{5/2}),\quad
\delta\psi=O(\alpha_0^{5/2}),\quad
\delta z=O(\alpha_0^3),\quad
\delta H=O(\alpha_0^2),\quad
\delta L=O(\alpha_0^2),\quad
\delta\lambda=O(\alpha_0^2). \tag{8}
\]

If only the leading terms \(r=\rho\), \(\psi=H_p\rho\), \(z=z_p+H_p\alpha\),
\(H=H_p\), \(L=0\), and \(\lambda=\lambda_p\) are retained, their respective
errors are \(O(\alpha_0^{3/2})\), \(O(\alpha_0^{3/2})\), \(O(\alpha_0^2)\),
\(O(\alpha_0)\), \(O(\alpha_0)\), and \(O(\alpha_0)\). A cutoff study must
therefore reduce \(\alpha_0\) and check the observables, not just the collocation
residual. An implementation that sets \(r=\psi=L=0\) at finite \(\alpha_0\)
does not approximate the regular branch.

## Smooth coat and the meaning of area

A centered coat with a smooth outer edge can be prescribed directly in material
area, for example

\[
C(\alpha)={C_*\over2}
\left[1-\tanh\left({\alpha-\alpha_c\over w}\right)\right],\qquad
\dot C(\alpha)=-{C_*\over2w}\operatorname{sech}^2
\left({\alpha-\alpha_c\over w}\right). \tag{9}
\]

Here \(2\pi\ell^2\alpha_c\) is the half-height coat surface area and
\(2\pi\ell^2w\) is its edge-width scale in material-area units. The finite
value of \(\dot C(0)\) is compatible with pole smoothness because
\(d\alpha/ds\propto r\to0\). In a sweep, keep \(w\) and
\(\alpha_{\max}\) fixed while varying \(\alpha_c\), unless a separate
edge-convergence check deliberately changes \(w\).

The projected disk area inside a material label \(\alpha\) is

\[
{A_{\rm proj}(\alpha)\over2\pi\ell^2}={r(\alpha)^2\over2},
\qquad {d\over d\alpha}{r^2\over2}=\cos\psi. \tag{10}
\]

Consequently

\[
{r^2\over2}=\int_0^\alpha\cos\psi(\beta)\,d\beta,
\]

which equals \(\alpha\) only for a flat patch (and to leading order for small
slopes). The prescribed coat area and total domain area in Eq. (9) are material
surface areas. Neither may be replaced by \(\pi r^2\) in the nonlinear model.

## Checks required of the first benchmark

The first calculation should remain on the shallow passive branch and compare
against the existing small-slope analytic patch. In addition to BVP convergence,
report the maximum ODE and boundary residuals, mesh dependence, sensitivity to
\(\alpha_0\), sensitivity to \(\alpha_{\max}\), and the effect of reducing
\(w\) and curvature amplitude. Compare apex mean curvature, coat-mean mean
curvature, reservoir-referenced depth, and coat-edge-referenced depth separately.
The sharp analytic patch uses projected radius/area; agreement with the material
area formulation is expected only in the small-slope limit, with the discrepancy
entering at quadratic order in slope.

For the same smooth coat used by the solver, the linearized apex value can be
checked without introducing a sharp-edge error. On the flat reference geometry
let \(C(r)=C_*g(r^2/2)\). The dimensionless linear equation is
\((\Delta-1)H=\Delta C\), hence the axisymmetric Green function gives

\[
{H(0)\over C_*}=g(0)-\int_0^\infty rK_0(r)g(r^2/2)\,dr. \tag{11}
\]

For a step \(g=1\) on \(r<x\), the identity
\(\int_0^x rK_0(r)\,dr=1-xK_1(x)\) recovers \(H(0)/C_*=xK_1(x)\).
The smooth reference in Eq. (11) separates edge smoothing from nonlinear and
discretization errors. A coat-mean comparison must use a separately declared
material-area weighting and generally has a leading edge-width correction.

This bounded validation does not establish a high-tension published area sweep,
snap-through, branch stability, or reproduction of the authors' numerical code.

## Independent axial-force first integral

For the same passive, pressure-free system there is a useful check that is not
merely another evaluation of the collocation equations. Define

\[
\mathcal Q=r\left[(H-C)\left(H+C-{\sin\psi\over r}\right)-\lambda\right]
\sin\psi+L\cos\psi. \tag{12}
\]

Differentiate Eq. (11) with respect to dimensionless arc length and substitute
S32. The derivative of the bracket uses
\(H'=L/r+C'\),
\(\lambda'=2(H-C)C'\), and
\((\sin\psi/r)'=2\cos\psi(H-\sin\psi/r)/r\); every term cancels, giving

\[
{d\mathcal Q\over ds}=0. \tag{13}
\]

Regular pole data give \(\mathcal Q(0)=0\), so the target solution has
\(\mathcal Q\equiv0\). At a flat outer boundary, Eq. (11) also reduces to
\(\mathcal Q=L\), providing an independent check that the computed outer
\(L\) tends to zero even though it is not one of the six imposed boundary
conditions. A nonzero drift in \(\mathcal Q\) can expose a sign or internal-force
inconsistency that small solver-reported residuals need not reveal. Report both
the raw maximum \(|\mathcal Q|\) and any normalized version with its scale
defined explicitly.
