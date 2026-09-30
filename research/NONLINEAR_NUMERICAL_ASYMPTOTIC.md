# Leading fixed-source compatibility residual

Task nonlinear-numerical-asymptotic-001, attempt 1, 2026-09-27. This is an analytic check within the [registered numerical execution](nonlinear_numerical_execution_001.json) and [frozen design](nonlinear_numerical_design.json). It derives a conditional reference for the **fixed** test change \(g=c=\varepsilon\phi\), where \(\phi(r)=\exp(1-1/(1-r^2))\) for \(0\le r<1\) and zero for \(r\ge1\). No BVP solve or numerical comparison was run here. The diagnostic remains suppressed if the design's equilibrium validation gates fail.

Let \(u_\sigma(r;\varepsilon)=p_\sigma/\sqrt{1+p_\sigma^2}\) be the two actual local-branch normalized slopes at \(\sigma=1,2\), with common \(\kappa=1\), \(f=0\), \(c=\varepsilon\phi\). Put \(D=u_1-u_2\) and \(S=u_1+u_2\). The exact **undivided** source-compatibility residual is

\[
K_\varepsilon(r)
=D\left[-S(rg)'+r\left(cg+\frac{g^2}{2}\right)\right].
\tag{1}
\]

For \(g=c=\varepsilon\phi\), \((rg)'=\varepsilon(r\phi)'\) and \(cg+g^2/2=\tfrac32\varepsilon^2\phi^2\). The existence proof gives an odd analytic branch

\[
u_\sigma(r;\varepsilon)=\varepsilon V_\sigma(r)+O(\varepsilon^3)
\quad\text{in a weighted }C^1\text{ radial-vector norm}, \tag{2}
\]

where \(V_\sigma\) is the order-one screened linear response to \(-\phi'\). Substitution into (1) gives, uniformly on \(0\le r\le1\),

\[
\boxed{\displaystyle
K_\varepsilon(r)=\varepsilon^3 K_3(r)+O(\varepsilon^5),\qquad
K_3=(V_1-V_2)
\left[-(V_1+V_2)(r\phi)'+\frac32r\phi^2\right].} \tag{3}
\]

The fifth-order remainder follows from the \(O(\varepsilon^3)\) correction to each odd slope: \(D,S=O(\varepsilon)+O(\varepsilon^3)\), while the bracket in (1) is \(O(\varepsilon^2)+O(\varepsilon^4)\). This is a fixed-test-source asymptotic, not an arbitrary-\(g\) compatibility theorem.

## Origin, support edge, and nonzero coefficient

Write \(V_\sigma=r z_\sigma\). The screened radial linear problem becomes \((-\Delta_4+\sigma)z_\sigma=-\phi'/r\); its positive heat-kernel or Bessel Green representation gives \(z_1>z_2>0\) through the support disk. The local branch estimate is stronger than a plain uniform slope estimate:

\[
\sup_{0\le r\le1}
\left|\frac{u_\sigma(r;\varepsilon)}r-\varepsilon z_\sigma(r)\right|
=O(\varepsilon^3), \tag{4}
\]

where each ratio at \(r=0\) means its smooth limit. Therefore (3) holds even in the \(r^{-2}\)-weighted form \(K_\varepsilon/r^2=\varepsilon^3(K_3/r^2)+O(\varepsilon^5)\), uniformly on \([0,1]\), with

\[
\frac{K_3(r)}{r^2}
=(z_1-z_2)\left[-(z_1+z_2)(r\phi)'+\frac32\phi^2\right],
\qquad
\lim_{r\downarrow0}\frac{K_3(r)}{r^2}
=(z_1(0)-z_2(0))
\left[\frac32-z_1(0)-z_2(0)\right]. \tag{5}
\]

Thus \(K_\varepsilon(0)=K_3(0)=0\) by radial regularity, with no hidden point force. The bump and all its derivatives vanish at \(r=1\), so \(K_\varepsilon(1)=K_3(1)=0\), and both vanish outside the support. These zeros make pointwise relative error near the endpoints inappropriate.

The leading coefficient is not identically zero. For \(r<1\) sufficiently close to \(1\), \((r\phi)'=\phi[1-2r^2/(1-r^2)^2]<0\), whereas \(z_1-z_2>0\), \(z_1+z_2>0\), and \(\phi>0\). Both terms in the bracket of (5) are then positive, so \(K_3(r)>0\) on an interior collar near the edge. Its norm is a mathematical reference, not an observation-noise scale.

## An independently checkable comparison

The infinite-reservoir \(V_\sigma\) can be formed without the nonlinear BVP from the positive order-one Green formula

\[
V_\sigma(r)=\int_0^1s\,
I_1(\sqrt{\sigma}\min\{r,s\})
K_1(\sqrt{\sigma}\max\{r,s\})[-\phi'(s)]\,ds. \tag{6}
\]

The finite origin value of \(z_\sigma=V_\sigma/r\) is obtained by the \(I_1(x)\sim x/2\) limit:
\[
z_\sigma(0)=\frac{\sqrt{\sigma}}{2}
\int_0^1 sK_1(\sqrt{\sigma}s)[-\phi'(s)]\,ds.
\]
Inserting these two independently computed linear profiles into (3) or (5) gives a fixed, checkable infinite-domain function \(K_3\); no fitted coefficient is needed.

The registered solver uses \(v(R)=0\) at finite \(R\), while (6) has a positive tail at every finite \(R\). Its **matching finite-\(R\) linear controls** therefore give the first comparison: form \(K_3^{(R)}\) by replacing \(V_\sigma\) in (3) with the corresponding finite-\(R\) linear \(u_\sigma^{(R)}\), then compare the validated nonlinear \(K_\varepsilon^{(R)}/\varepsilon^3\) with \(K_3^{(R)}\) in an absolute support-disk norm across the three registered amplitudes. Algebraically, for any sampled profiles with \(v_\sigma=u_\sigma/r\),

\[
\frac{K_\varepsilon(r)}{\varepsilon^3r^2}
=\left(\frac{v_1}{\varepsilon}-\frac{v_2}{\varepsilon}\right)
\left[-\left(\frac{v_1}{\varepsilon}+\frac{v_2}{\varepsilon}\right)(r\phi)'
+\frac32\phi^2\right], \tag{7}
\]

with the continuous pole limit. Equation (7) permits a direct check of the cubic normalization; it does not replace the independent equilibrium residual tests. As a second comparison, check \(K_3^{(R)}\) against the infinite Green \(K_3\) under the **already registered** \(R=8\) to \(R=12\) reservoir refinement. At fixed \(R\), a nonlinear-to-infinite-Green mismatch includes boundary truncation and must not be assigned wholly to the \(O(\varepsilon^5)\) term. Use absolute rather than pointwise relative error because \(K\) vanishes at \(r=0,1\).

Only after the solver status, graph-domain, boundary, off-mesh flux, profile-refinement, linear-control, zero-source, and sampled-ordering gates pass may the fixed-\(g\) diagnostic be reported under the execution contract. If any gate fails, this note remains a conditional analytic prediction and does not authorize computing or interpreting \(K\). The residual measures a proposed source change's failure to preserve both exact profiles. It is not microscopy error, calibrated force uncertainty, practical conditioning, or a biological identifiability estimate.
