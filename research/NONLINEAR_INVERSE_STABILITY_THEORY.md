# No uniform inverse Lipschitz bound near the flat graph

Task nonlinear-inverse-stability-theory-001, attempt 1, 2026-09-29. This is a separate analytic consequence of the accepted [exact source correction](NONLINEAR_SOURCE_THEORY.md), [local branch](NONLINEAR_EXISTENCE_THEORY.md), and [two-profile uniqueness criterion](NONLINEAR_UNIQUENESS_THEORY.md), under the [registered design](nonlinear_inverse_stability_design.json). The closed numerical branch and its failed profiles play no role.

**Claim.** In the registered axisymmetric projected-source model, when smooth compact balanced vertical loads are unknown, no inverse estimate recovering the curvature source from the two complete normalized-slope profiles can have a Lipschitz constant uniform as the nonflat source amplitude \(\varepsilon\downarrow0\). Along the construction below every such constant is at least of order \(\varepsilon^{-2}\). This is a lower bound on conditioning, not a sharp exponent or a noise-precision estimate.

## Spaces and exact load change

Fix \(0<\alpha<1\) and \(0<\mu<1\). Let \(X=C^{3,\alpha}_\mu(\mathbb R^2;\mathbb R^2)\) and \(Y=C^{1,\alpha}_\mu(\mathbb R^2;\mathbb R^2)\), restricted to \(O(2)\)-equivariant radial vector fields; the norm means multiplication by \(e^{\mu\langle x\rangle}\) before the ordinary Holder norm. Scalar curvature fields use \(C^{2,\alpha}_\mu\). The screened inverse \((-\Delta+\sigma)^{-1}:Y\to X\) is bounded for \(\sigma=1,2\), by the weighted Yukawa estimate and Schauder regularity used in the existence proof. Smooth compact data bootstrap the resulting profiles and loads.

Let \(\phi\) be the registered smooth bump supported in \(r\le1\), \(c_\varepsilon=\varepsilon\phi\), \(f_\varepsilon=0\), and \(U_j=u_j(r)e_r\) the accepted exact decaying stationary profiles at \(\sigma_j=j\). Their local branch obeys \(\|U_j\|_X\le C\varepsilon\) for all sufficiently small positive \(\varepsilon\). Write \(\mathcal F_\sigma(U,c)\) for the vector stationary flux in the existence note, so \(\mathcal F_{\sigma_j}(U_j,c_\varepsilon)=0\).

Set \(g=c_\varepsilon\). Direct subtraction of the **full-square** flux, with the radial sources fixed in projected coordinates, gives the origin-safe vector identity

\[
\Delta\mathcal F(U;c,g)
:=\mathcal F_\sigma(U,c+g)-\mathcal F_\sigma(U,c)
=(1-|U|^2)\nabla g
+g(DU)U-g(\operatorname{div}U)U
+(cg+\tfrac12g^2)U. \tag{1}
\]

Its radial component is
\[
\Delta Q(u;c,g)=(1-u^2)g'-\frac{g u^2}{r}
 +(cg+\tfrac12g^2)u. \tag{2}
\]
The quotient is regular: \(u=O(r)\) and \(g'=O(r)\). Define \(M_\varepsilon e_r=\Delta\mathcal F(U_1;c_\varepsilon,g)\), and prescribe the common changed load
\[
\widetilde f_\varepsilon(r)
=-\frac1r(rM_\varepsilon)' . \tag{3}
\]
Equation (1) makes \(M_\varepsilon e_r\) smooth and compactly supported, with \(M_\varepsilon=O(r)\) at the origin. Hence \(\widetilde f_\varepsilon\) is a smooth compact projected-area vertical dead load, and \(2\pi\int_0^\infty r\widetilde f_\varepsilon\,dr=-2\pi[rM_\varepsilon]_0^\infty=0\). Its sign matches the Euler equation \((rQ)'=-rf\). Under the changed common sources \((\widetilde c,\widetilde f)=(2c_\varepsilon,\widetilde f_\varepsilon)\), **the first profile \(U_1\) remains exactly stationary**.

## An actual second profile and the inverse bound

The vector \(M_\varepsilon e_r\) is \(O_Y(\varepsilon)\). More decisively, the leading \(\nabla g\) in (1) is independent of \(U\); every other term has three factors of size \(O(\varepsilon)\). Thus
\[
\|\Delta\mathcal F(U_2;c_\varepsilon,g)
-\Delta\mathcal F(U_1;c_\varepsilon,g)\|_Y
\le C\varepsilon^3 . \tag{4}
\]
This is an equilibrium *residual*, and by itself would not be a second stationary profile. Define
\[
\mathcal G_\varepsilon(U)
=\mathcal F_{2}(U,2c_\varepsilon)-M_\varepsilon e_r .
\]
Then \(\mathcal G_\varepsilon(U_2)\) equals the difference in (4). At \(\varepsilon=0,U=0\), \(D_U\mathcal G_0=-\Delta+2:X\to Y\) is an isomorphism. In an \(X\)-ball of radius \(C\varepsilon\) containing the nearby profiles, \(D_U\mathcal G_\varepsilon\) differs from this operator by \(O(\varepsilon)\), so its inverse is uniformly bounded by a Neumann-series argument. The implicit-function theorem with parameters \((c,M)\) supplies an actual nearby solution \(\widetilde U_2\) of \(\mathcal G_\varepsilon(\widetilde U_2)=0\). The mean derivative along the segment from \(U_2\) to \(\widetilde U_2\) is itself \(O(\varepsilon)\)-close to \(-\Delta+2\), hence uniformly invertible, giving
\[
\|\widetilde U_2-U_2\|_X\le C'\varepsilon^3. \tag{5}
\]
The solution remains a small single-valued graph: \(\|U\|_\infty<1\), and \(p=u/\sqrt{1-u^2}\) is integrable by exponential decay. It is regular at the origin and has height fixed by \(h(\infty)=0\). It is stationary under the **same changed** \(2c_\varepsilon,\widetilde f_\varepsilon\) as \(U_1\). This proves actual source-pair/profile-pair proximity, not merely a small equation residual.

Use the complete normalized slopes as data, with norm \(\|(U_1,U_2)\|_{X\times X}=\|U_1\|_X+\|U_2\|_X\), and measure curvature source difference in \(C^{2,\alpha}_\mu\) (or source-pair norm including the load, which is at least this curvature difference). The two admissible source pairs are \((c_\varepsilon,0)\) and \((2c_\varepsilon,\widetilde f_\varepsilon)\). They produce \((U_1,U_2)\) and \((U_1,\widetilde U_2)\), respectively, while
\[
\|\widetilde c-c_\varepsilon\|_{C^{2,\alpha}_\mu}
=\varepsilon\|\phi\|_{C^{2,\alpha}_\mu}>0,\qquad
\|(U_1,\widetilde U_2)-(U_1,U_2)\|_{X\times X}
\le C'\varepsilon^3 . \tag{6}
\]
Therefore any inverse Lipschitz constant \(L_\varepsilon\) valid on a neighborhood containing these two admissible pairs must obey \(L_\varepsilon\ge \|\phi\|_{C^{2,\alpha}_\mu}(C')^{-1}\varepsilon^{-2}\). If the profile difference is smaller or zero, the inverse estimate fails still more strongly. This lower bound concerns the class with unknown balanced load. It does **not** construct a second known-zero-load explanation, assert global uniqueness or stability, or turn a mathematical norm into calibrated imaging noise.
