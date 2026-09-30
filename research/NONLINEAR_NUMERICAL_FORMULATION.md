# Regular boundary value formulation for the exact graph branch

Task nonlinear-numerical-design-theory-001, attempt 1, 2026-09-26. This is an analytic formulation check for the [registered numerical design](nonlinear_numerical_design_review.json) following the accepted [local existence proof](NONLINEAR_EXISTENCE_THEORY.md). No boundary value solver, numerical amplitude, mesh, tolerance experiment, or fit was run here.

Keep \(\kappa=1\), \(\sigma\in\{1,2\}\), \(f=0\), and \(c(r)=\varepsilon\phi(r)\), where \(\phi=\exp(1-1/(1-r^2))\) for \(r<1\) and is zero for \(r\ge1\). Let \(u=p/\sqrt{1+p^2}\) be normalized graph slope, \(u=rv\), and \(w=v'\). Set \(t=C-c\), where \(C=u'+u/r=2v+rw\). The exact regular-origin zero-load flux from the full-square energy is

\[
Q=-(1-u^2)t'-tuu'+\left(\frac{t^2}{2}+\sigma\right)u=0. \tag{1}
\]

Substitution of \(u=rv\), \(u'=v+rw\), \(t=2v+rw-c\), and \(t'=3w+rw'-c'\) gives

\[
(1-r^2v^2)(3w+rw'-c')
=rv\left[\sigma-\frac12(2v+rw-c)(rw+c)\right].
\]

Hence the proposed first-order system is **algebraically correct** for \(r>0\):

\[
\boxed{\begin{aligned}
v'&=w,\\
w'&=-\frac{3w}{r}+\frac{c'}r
  +\frac{\sigma v-\frac12v(2v+rw-c)(rw+c)}{1-r^2v^2}.
\end{aligned}} \tag{2}
\]

The denominator encodes the graph domain \(|u|=|rv|<1\). A computed branch must remain strictly inside it on the entire interval; reaching \(|rv|=1\) invalidates recovery of \(p=u/\sqrt{1-u^2}\).

## Pole and reservoir conditions

Radial smoothness requires \(v'(0)=w(0)=0\). Writing \(v=v_0+\tfrac12v''(0)r^2+O(r^4)\) and \(c=c_0+\tfrac12c''(0)r^2+O(r^4)\), the finite pole value is constrained by

\[
\boxed{4v''(0)=c''(0)+\sigma v_0
-\frac12v_0(2v_0-c_0)c_0.} \tag{3}
\]

This follows by taking the limit of (2), rather than evaluating \(-3w/r\) and \(c'/r\) separately at zero. For the registered bump,

\[
\frac{c'(r)}r=
\begin{cases}
-\dfrac{2\varepsilon\phi(r)}{(1-r^2)^2},&0\le r<1,\\
0,&r\ge1,
\end{cases}
\quad
c_0=\varepsilon,\quad c''(0)=-2\varepsilon,\quad
\left.\frac{c'}r\right|_{r=0}=-2\varepsilon . \tag{4}
\]

The apparent expression at \(r=1\) has smooth zero extension because the bump is flat there. One may formulate the \(-3w/r\) term with a solver's singular-matrix mechanism and the regularity condition \(w(0)=0\), or use the pole relation (3) to start away from zero; neither approach is implemented here.

For a finite outer radius \(R>1\), \(v(R)=0\) is a **truncated-reservoir approximation** to the true decay \(v(r)\to0\) as \(r\to\infty\). It is not an exact boundary condition of the infinite-domain stationary branch. Reconstructing a finite-domain height with \(h(R)=0\) likewise changes its reference relative to \(h(\infty)=0\). A finite-amplitude calculation must compare increasing \(R\) and mesh/tolerance refinements before interpreting the support-disk profile. A decaying Robin condition informed by the linear exterior tail is another possible approximation, but it would also require a boundary-error check.

## Independent linear reference and validation contract

At first order in \(\varepsilon\), \(u_\sigma=\varepsilon u_\sigma^{(1)}+O(\varepsilon^3)\) and

\[
(-\Delta_1+\sigma)u_\sigma^{(1)}=-\phi',\qquad
\Delta_1u=u''+\frac{u'}r-\frac{u}{r^2}.
\]

An independent infinite-domain Bessel Green formula is

\[
u_\sigma^{(1)}(r)=\int_0^1 s\,
I_1(\sqrt{\sigma}\min\{r,s\})
K_1(\sqrt{\sigma}\max\{r,s\})
[-\phi'(s)]\,ds. \tag{5}
\]

The kernel is positive. For \(r\ge1\), this becomes \(K_1(\sqrt{\sigma}r)\int_0^1sI_1(\sqrt{\sigma}s)[-\phi'(s)]\,ds>0\), so \(v_\sigma^{(1)}(R)=u_\sigma^{(1)}(R)/R>0\) for every finite \(R\). Formula (5) is a benchmark for the small-amplitude slope, not a claim that finite-\(R\) Dirichlet data reproduce the infinite reservoir exactly. The 4D screened scalar Green or heat-kernel formula for \(v^{(1)}=u^{(1)}/r\) provides a second equivalent analytic representation.

A later **separately registered numerical run** should, for each reported finite \(\varepsilon\), record: the zero-source solution \(v=w=0\); the maximum \(|rv|\); the pole relation (3); the exact undivided flux (1) evaluated away from collocation nodes; changes under mesh/tolerance refinement and increasing \(R\); and comparison of \(rv/\varepsilon\) with (5), or \(v/\varepsilon\) with (5) divided by \(r\), as amplitudes decrease. On the full source disk it should inspect \(v_2>0\) and \(v_1-v_2>0\), including their finite origin limits and the endpoint \(r=1\). Values only at solver nodes cannot certify continuous strict ordering without an error enclosure. No tested finite amplitude would identify the unspecified threshold in the local existence theorem or prove stability or global branch selection.

Optionally, for one fixed smooth nonzero test \(g\) supported in \([0,1]\), one may inspect the **undivided** exact compatibility residual \(D[-S(rg)'+r(cg+g^2/2)]\), where \(D=u_1-u_2\) and \(S=u_1+u_2\). It is a formulation check only; dividing by small \(D\) or \(S\), or treating this residual as a noise-based identifiability estimate, would exceed this design.
