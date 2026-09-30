# Linear slope ordering and its nonlinear transfer requirement

Task `nonlinear-existence-ordering-001`, attempt 1. Observed start: 2026-09-26 23:22 UTC. This note uses the frozen [existence design](nonlinear_existence_design.json): `kappa=1`, `f=0`, `c=epsilon*phi`, tensions `sigma=1,2`, and `phi(r)=exp(1-1/(1-r^2))` for `r<1`, zero for `r>=1`. It proves the *linear response ordering* and states the precise remainder needed to transfer it to actual nonlinear stationary branches. Existence of those branches is a separate analytic prerequisite.

## Exact flux and order-one equation

For a radially regular graph, put `p=h'`, `J=sqrt(1+p^2)`, and `C=(rp/J)'/r`. The exact stationary flux in the registered projected-radius, vertical-dead-load model is

\[
 Q_\sigma[p,\epsilon]=-
 \frac{[(C-\epsilon\phi)J]'}{J^3}
 +\left[\frac12(C-\epsilon\phi)^2+\sigma\right]\frac pJ . \tag{1}
\]

The Euler equation is `(r Q_sigma)'=-rf=0`. Radial regularity gives a finite `Q_sigma` at the origin, so its global integration constant vanishes: **`Q_sigma=0` for all `r>0`**.

If an exact branch has `p_sigma(epsilon,r)=epsilon*u_sigma(r)+o(epsilon)` in a topology strong enough to linearize (1), then `J=1+O(epsilon^2)` and `C=epsilon*(u_sigma'+u_sigma/r)+o(epsilon)`. The order-one equation is

\[
 A_\sigma u_\sigma:=-u_\sigma''-\frac{u_\sigma'}r
 +\frac{u_\sigma}{r^2}+\sigma u_\sigma=-\phi'(r). \tag{2}
\]

The regular and reservoir conditions are `u_sigma(0)=0`, finite `u_sigma/r` at the origin, and decay at infinity. For the declared bump,

\[
 -\phi'(r)=\frac{2r\phi(r)}{(1-r^2)^2}>0
 \quad(0<r<1), \tag{3}
\]

and this source vanishes smoothly outside the unit disk.

## Uniform strict ordering through the origin and support edge

Set `z_sigma(r)=u_sigma(r)/r` and extend it radially to `R^4`. Equation (2) becomes

\[
 (-\Delta_{\mathbb R^4}+\sigma)z_\sigma=q,
 \qquad q(r)=-\frac{\phi'(r)}r
 =\begin{cases}2\phi(r)/(1-r^2)^2,&r<1,\\0,&r\ge1.\end{cases} \tag{4}
\]

The apparent quotient at the origin is smooth with `q(0)=2`; the exponential cutoff makes `q` smooth at `r=1`. Thus `q` is smooth, compactly supported, nonnegative, and positive for `0<=r<1`. The decaying solution is unique and has the positive heat-kernel representation

\[
 z_\sigma(x)=\int_0^\infty e^{-\sigma t}
 \int_{\mathbb R^4}(4\pi t)^{-2}
 e^{-|x-y|^2/(4t)}q(y)\,dy\,dt. \tag{5}
\]

In particular `z_2(r)>0` at every finite `r`, including `r=0` and `r=1`. Let `d=z_1-z_2`. Subtracting the screened equations gives

\[
 (-\Delta_{\mathbb R^4}+1)d=(2-1)z_2=z_2>0. \tag{6}
\]

The same positive inverse shows `d(r)>0` at every finite `r`. Continuity on the compact interval `[0,1]` therefore yields the two genuine gaps

\[
 m_2:=\min_{0\le r\le1}z_2(r)>0,
 \qquad m_d:=\min_{0\le r\le1}d(r)>0. \tag{7}
\]

Consequently `u_1(r)>u_2(r)>0` for all `r>0`, with `u_1/r-u_2/r=d>0` even at the origin and the support edge. The positive value at `r=1` is a nonlocal response to the interior source; `phi(1)=0` does not make the slope vanish there. At `r=0` the slopes themselves vanish by radial regularity, so the meaningful strict comparison is of `p/r`, or equivalently their origin derivatives.

## What actual nonlinear branches must supply

For each tension, one needs an exact stationary branch satisfying (1), origin regularity, flat-reservoir decay, and

\[
 \left\|\frac{p_\sigma(\epsilon,\cdot)}r
 -\epsilon z_\sigma\right\|_{C^0([0,1])}
 =o(\epsilon),\qquad \epsilon\downarrow0, \tag{8}
\]

where the quotient at `r=0` means `p_sigma'(epsilon,0)`. This is the precise uniform remainder for the sign transfer. For sufficiently small *unspecified* positive `epsilon`, (7)-(8) imply `p_2/r>0` and `(p_1-p_2)/r>0` throughout `[0,1]`; in particular both actual slopes are positive and strictly ordered on `0<r<=1`, with nonzero slope at `r=1`. Since `p -> p/sqrt(1+p^2)` is strictly increasing, this also gives the uniqueness theorem's `D=u_1-u_2>0` and `S=u_1+u_2>0` at every `0<r<=1`, including its outer endpoint. For example, it is sufficient that the combined difference remainder be less than `epsilon*m_d` and the tension-2 remainder less than `epsilon*m_2`. No numerical threshold is inferred.

A branch differentiable at `epsilon=0` into a radial-vector-field `C^1_b(R^2)` norm, with derivative `u_sigma(r)e_r`, would imply (8): if `V(x)=p(|x|)e_r` and `V(0)=0`, then `|p(r)|/r<=||DV||_infty`. An appropriately weighted slope space controlling `sup_[0,1]|p/r|` also suffices. Pointwise `p_sigma/epsilon -> u_sigma`, ordinary unweighted `C^0` convergence of slopes, or the formal expansion of (1) alone does **not** provide the uniform gap near `r=0`. The separate nonlinear existence proof must establish a branch and an estimate at least as strong as (8); this note makes no global branch, stability, or selection claim.

The normalized-slope field gives a direct way to check the transfer from a branch theorem. Let `U=(p/J)e_r`, so `|U|<1`, `C=div U`, and put `a=div U-epsilon*phi`. Algebraically, (1) is the radial component of the exact vector flux

\[
 \mathcal F_\sigma(U,\epsilon)=
 -(1-|U|^2)\nabla a-a(DU)U
 +\left(\frac{a^2}{2}+\sigma\right)U. \tag{9}
\]

Indeed `J=(1-|U|^2)^(-1/2)` and `J'/J^3=(DU)U` in the radial direction. On radial curl-free fields the derivative of (9) at `(U,epsilon)=(0,0)` is `-Delta U+sigma U`, with source derivative `grad phi`. Thus a radial-vector implicit-function result in a space embedded in `C^1_b`, with `U_sigma(epsilon)=epsilon*u_sigma e_r+o(epsilon)` in that norm, supplies the needed estimate. More explicitly, the mean-value bound from `U(0)=0` gives `sup_[0,1]|U(r)|/r<=||DU||_infty`; recovery `p=U/sqrt(1-|U|^2)` changes `p/r` by `O(epsilon^3)` whenever `||U||_{C^1}=O(epsilon)`. The nonlinear theory worker reports a weighted radial-vector IFT with an `O(epsilon^3)` remainder; this paragraph independently checks its exact flux algebra and ordering transfer, while the function-space inverse and branch construction remain the separate theory/review gate.
