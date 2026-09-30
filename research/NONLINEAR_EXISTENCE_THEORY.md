# Local exact graph profiles for a compact curvature source

Task nonlinear-existence-theory-001, attempt 1, 2026-09-26. This note addresses the separately registered [existence design](nonlinear_existence_design.json) under the [fixed graph energy](nonlinear_source_design.json). It proves a small-source stationary branch for each of the two specified tensions and verifies the slope condition in the [compact-source theorem](NONLINEAR_UNIQUENESS_THEORY.md). The statement is local in the source amplitude and does not select a stable or global branch.

Set \(\kappa=1\), \(f=0\), \(\sigma\in\{1,2\}\), and

\[
c_\varepsilon(r)=\varepsilon\phi(r),\qquad
\phi(r)=
\begin{cases}
\exp\!\left(1-\dfrac{1}{1-r^2}\right),&0\le r<1,\\
0,&r\ge1 .
\end{cases} \tag{1}
\]

The bump is a smooth function of \(r^2\) at the origin and has smooth zero extension at \(r=1\). Sources are prescribed in projected radius and the load is vertical dead load per projected area. The origin is regular, and height and slope decay to the flat reservoir.

## Exact stationary flux

For a graph \(h(r)\), let \(p=h'\), \(J=\sqrt{1+p^2}\), \(C=(rp/J)'/r\), and \(t=C-c\). Varying the full-square energy with \(f=0\), using \(\delta J=(p/J)\delta p\) and \(\delta C=r^{-1}(r\delta p/J^3)'\), gives

\[
\delta E=2\pi\int_0^\infty r Q_\sigma\,\delta p\,dr,\qquad
Q_\sigma=-\frac{(tJ)'}{J^3}
       +\left(\frac{t^2}{2}+\sigma\right)\frac pJ . \tag{2}
\]

The Euler equation is \((rQ_\sigma)'=0\). A smooth radial graph and smooth radial \(c\) have \(p=O(r)\), \(C'=O(r)\), and \(Q_\sigma=O(r)\) at the origin, so the integration constant is zero: **every regular radial stationary profile with \(f=0\) obeys \(Q_\sigma=0\)**. Conversely \(Q_\sigma=0\) makes the first variation vanish for all compact height variations, including nonradial ones when expressed in the vector form below. No point force or boundary reaction is introduced.

Use the normalized slope \(u=p/J\), so \(J=(1-u^2)^{-1/2}\), \(C=u'+u/r\), and \(t=u'+u/r-c\). Equation (2) becomes exactly

\[
Q_\sigma=-(1-u^2)t'-tuu'
              +\left(\frac{t^2}{2}+\sigma\right)u. \tag{3}
\]

This retains the \(c^2J\) part of the energy. In particular, its linearization at \(u=c=0\) is

\[
(-\Delta_1+\sigma)u=-c',\qquad
\Delta_1u=u''+\frac{u'}r-\frac{u}{r^2}. \tag{4}
\]

The order-one radial operator is regular when regarded as the ordinary vector Laplacian of \(U(x)=u(|x|)x/|x|\) on \(\mathbb R^2\).

## A weighted-space local branch

Fix \(0<\alpha<1\) and \(0<\mu<1\). Let \(X_\mu\) be the closed space of \(O(2)\)-equivariant vector fields \(U:\mathbb R^2\to\mathbb R^2\) with \(e^{\mu\langle x\rangle}U\in C^{2,\alpha}(\mathbb R^2)\), and \(Y_\mu\) the analogous \(C^{0,\alpha}\) space. Here \(\langle x\rangle=\sqrt{1+|x|^2}\); full \(O(2)\) equivariance means \(U(Rx)=RU(x)\), excluding a swirl component. Such fields have \(U=u(r)e_r\), \(U(0)=0\), and \(u(r)=O(r)\).

For \(U=u e_r\) define \(t=\operatorname{div}U-c_\varepsilon\) and

\[
\mathcal F_\sigma(U,\varepsilon)
=-(1-|U|^2)\nabla t-t(DU)U
 +\left(\frac{t^2}{2}+\sigma\right)U. \tag{5}
\]

The radial component of (5) is exactly (3). It maps \(X_\mu\times\mathbb R\) smoothly, indeed analytically near zero, into \(Y_\mu\): \(t\) uses one derivative of \(U\), \(\nabla t\) two, and all remaining terms are products of weighted Holder functions. Radial \(\nabla\operatorname{div}U=\Delta U\), so

\[
D_U\mathcal F_\sigma(0,0)V=(-\Delta+\sigma)V,\qquad
D_\varepsilon\mathcal F_\sigma(0,0)=\nabla\phi. \tag{6}
\]

For each \(\sigma\ge1\), \(-\Delta+\sigma:X_\mu\to Y_\mu\) is an isomorphism. Its inverse is the two-dimensional Yukawa Green convolution \(G_\sigma*F\), which preserves \(O(2)\) equivariance. The kernel decays at rate \(\sqrt{\sigma}\). Since \(\langle x\rangle-\langle x-z\rangle\le |z|\), the weighted supremum estimate is bounded by \(\|F\|_{Y_\mu}\int_{\mathbb R^2}G_\sigma(z)e^{\mu|z|}\,dz<\infty\) for \(\mu<1\le\sqrt{\sigma}\); local Schauder estimates give the weighted \(C^{2,\alpha}\) bound. A decaying homogeneous solution vanishes by the positive energy identity, so the inverse is unique.

The Banach implicit-function theorem therefore gives, for each \(\sigma=1,2\), a unique small \(U_\sigma(\varepsilon)\in X_\mu\) satisfying \(\mathcal F_\sigma=0\) for \(|\varepsilon|<\varepsilon_\sigma\). This is uniqueness only **within a small weighted-space neighborhood of the flat graph**. The flux is odd under \((U,\varepsilon)\mapsto(-U,-\varepsilon)\); uniqueness makes the branch odd and analytic. If \(V_\sigma=\partial_\varepsilon U_\sigma(0)\), then

\[
U_\sigma(\varepsilon)=\varepsilon V_\sigma+O_{X_\mu}(\varepsilon^3),
\qquad (-\Delta+\sigma)V_\sigma=-\nabla\phi. \tag{7}
\]

For sufficiently small amplitude \(\|U_\sigma\|_\infty<1\). Recover \(p_\sigma=u_\sigma/\sqrt{1-u_\sigma^2}\) and fix the height reference by

\[
h_\sigma(r)=-\int_r^\infty p_\sigma(s)\,ds. \tag{8}
\]

The exponential weight makes the slope integrable, so \(h_\sigma(\infty)=p_\sigma(\infty)=0\). Equivariance gives \(p_\sigma(0)=0\), and smooth compact \(\phi\) with elliptic bootstrapping gives a smooth radially regular graph. Since (5) vanishes as a vector field, its full first variation vanishes. The energy is finite; \(f=0\) is balanced. These are actual stationary graphs of the registered nonlinear model.

## Strict ordering on the declared source disk

Write \(V_\sigma=v_\sigma(r)e_r\) and \(v_\sigma(r)=r z_\sigma(r)\). The identity

\[
\Delta_1(rz)=r\left(z''+\frac{3}{r}z'\right)=r\Delta_4 z
\]

turns (7) into a scalar screened problem in \(\mathbb R^4\):

\[
(-\Delta_4+\sigma)z_\sigma=q(r),\qquad
q(r)=-\frac{\phi'(r)}r=
\begin{cases}
\dfrac{2\phi(r)}{(1-r^2)^2},&r<1,\\
0,&r\ge1 .
\end{cases} \tag{9}
\]

The value at the origin is \(q(0)=2\). Thus \(q\) is smooth, nonnegative, compactly supported, and strictly positive for \(0\le r<1\). The positive heat-kernel representation

\[
z_\sigma=\int_0^\infty e^{-\sigma t}
       (e^{t\Delta_4}q)\,dt \tag{10}
\]

implies \(z_2(r)>0\) for every \(r\ge0\), including \(r=1\) and the origin. Moreover,

\[
z_1-z_2=\int_0^\infty (e^{-t}-e^{-2t})
       (e^{t\Delta_4}q)\,dt>0 \quad(r\ge0). \tag{11}
\]

Continuity gives positive minima \(m_2=\min_{[0,1]}z_2>0\) and \(m_d=\min_{[0,1]}(z_1-z_2)>0\). No numerical value is needed.

The \(X_\mu\) remainder in (7) controls first derivatives. Because every equivariant remainder vanishes at \(x=0\), the mean-value inequality gives

\[
\sup_{0<r\le1}
\left|\frac{u_\sigma(r;\varepsilon)}r-\varepsilon z_\sigma(r)\right|
\le C_\sigma\varepsilon^3. \tag{12}
\]

Choose a sufficiently small positive \(\varepsilon\) so that the two remainders are below \(\varepsilon m_2\) and \(\varepsilon m_d\), respectively. Then on the **whole** \(0<r\le1\),

\[
u_1(r;\varepsilon)>u_2(r;\varepsilon)>0. \tag{13}
\]

Both normalized-slope sum \(S=u_1+u_2\) and difference \(D=u_1-u_2\) are strictly positive there, including the outer endpoint \(r=1\); their ratios to \(r\) have positive limits at the origin. The prior compact-source uniqueness theorem therefore applies to these two actual common-\(c_\varepsilon\), common-\(f=0\), common-\(\kappa=1\) profiles for smooth \(g\) supported in \(0\le r\le1\). It rules out a nonzero shared compact curvature change with one compensating balanced load **for this local pair**.

This is an existence and exact structural statement within the specified graph model. It does not establish nonlinear stability, uniqueness among large-amplitude branches, practical conditioning, observational precision, or a biological source interpretation. The strict margins shrink with \(\varepsilon\), so the proof itself supplies no noise tolerance.
