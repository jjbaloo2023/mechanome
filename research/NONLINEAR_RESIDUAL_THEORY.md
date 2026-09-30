# Why the first-order BVP residual did not certify the physical graph flux

Task nonlinear-residual-theory-001, 2026-09-27. This is a postmortem of the frozen attempt-2 [BVP implementation](nonlinear_graph_numerical_002.py) and the lead's saved-coefficient [diagnostic](nonlinear_residual_postmortem.json). It uses only the retained piecewise-polynomial profiles; no new boundary-value solve or source change is part of this note. The attempt-2 physical \(Q/r\varepsilon\) gate failed, and the optional curvature-source compatibility calculation \(K\) remains suppressed.

## Exact decomposition

At \(r>0\), let \(v(r)\) and \(w(r)\) be the two independently interpolated components of a saved cubic BVP solution. Set

\[
u=rv,\quad A=1-u^2,\quad b=v+rw,\quad
T=2v+rw-c,\quad
\delta=v'-w,\quad \delta'=v''-w'. \tag{1}
\]

The true graph reconstructed from \(v\) has \(u'=v+rv'=b+r\delta\), curvature difference \(t_v=2v+rv'-c=T+r\delta\), and \(t_v'=3v'+rv''-c'\). The exact physical flux divided by \(r\), from the registered full-square energy, is

\[
\frac{Q_{\rm phys}}r
=-A\left(\frac{3v'}r+v''-\frac{c'}r\right)
-t_vv(v+rv')+\left(\frac{t_v^2}{2}+\sigma\right)v. \tag{2}
\]

For comparison define a **formal system flux**, using the stored auxiliary \(w\) consistently in the first-order equations:

\[
\frac{Q_{\rm sys}}r
=-A\left(\frac{3w}r+w'-\frac{c'}r\right)
-T v b+\left(\frac{T^2}{2}+\sigma\right)v. \tag{3}
\]

Let \(F(r,v,w)\) denote the full registered right-hand side for \(w'\), including its singular \(-3w/r\) term, and let \(\eta=w'-F(r,v,w)\). Direct substitution of the BVP equation shows \(Q_{\rm sys}/r=-A\eta\). This is a **system diagnostic**, not the physical acceptance metric. Expanding (2) around (3) gives the exact algebraic identity

\[
\boxed{\displaystyle
\frac{Q_{\rm phys}}r
=-A\eta
-A\left(\frac{3\delta}{r}+\delta'\right)
-rvb\,\delta-\frac12vr^2\delta^2 .} \tag{4}
\]

The identity holds within every smooth polynomial interval wherever \(r>0\). It reveals the lost derivative: a small \(v'-w\) does not by itself control \(v''-w'\), and the \(3\delta/r\) term amplifies regularity errors near the pole. A successful first-order collocation status or a tight solver tolerance controls its own first-order residual in the solver's norm; it does not directly impose the frozen, independent supremum bound on \(Q_{\rm phys}/(r\varepsilon)\), which differentiates the \(v\) interpolant twice. Checking only \(\eta\), or substituting the ODE right-hand side for \(v''\), would replace the physical gate rather than satisfy it.

## The pole and saved-profile evidence

For a smooth radial graph \(v'(0)=0\), \(w(0)=0\), and \(c'(0)=0\). With \(T_0=2v_0-c_0\), the finite limits are

\[
\left.\frac{Q_{\rm phys}}r\right|_0
=-4v''(0)+c''(0)-T_0v_0^2
+\left(\frac{T_0^2}{2}+\sigma\right)v_0,
\qquad
\left.\frac{Q_{\rm sys}}r\right|_0
=-4w'(0)+c''(0)-T_0v_0^2
+\left(\frac{T_0^2}{2}+\sigma\right)v_0. \tag{5}
\]

Their difference is \(-4[v''(0)-w'(0)]\). These formulas assume the **actual** interpolated \(v'(0)\) and \(w(0)\) vanish; assigning a pole value from (5) without checking that fact could conceal a \(1/r\) singularity. The saved-profile postmortem explicitly asserts \(v'(0)=w(0)=0\) for every one of the 12 fine nonlinear profiles, so its pole evaluation is valid for these interpolants.

The lead's no-solve script reconstructs the canonical stored PPoly coefficients, reproduces every frozen-grid physical maximum, then samples 17 points per mesh interval and both sides of interior knots. For all 12 fine cases, the augmented grid finds normalized physical maxima about \(2.41885\times10^{-4}\) to \(2.42247\times10^{-4}\), around \(r=0.8416667\) in the interval \([0.8375,0.8416667]\). This exceeds the frozen \(10^{-5}\) gate more strongly than the original fixed-grid maxima \(1.4577\times10^{-4}\) to \(1.5303\times10^{-4}\). The formal system residual maxima are only about \(1.46\times10^{-7}\) to \(5.58\times10^{-7}\). At each augmented-grid physical maximum, the defect terms in (4) account for the physical value to roundoff; the recorded decomposition discrepancies are below \(10^{-12}\) after normalization. The saved \(v'-w\) differences reach only order \(10^{-9}\), while \(v''-w'\) reaches order \(10^{-6}\) to \(10^{-5}\). Pole physical residuals are themselves about \(5.1\times10^{-5}\) to \(5.4\times10^{-5}\) after division by \(\varepsilon\), also above the gate.

This is a localization and representation diagnosis, not a convergence proof. The augmented grid still samples a finite set and supplies no rigorous continuous supremum enclosure. Cubic interpolation is differentiable inside each interval, but its second derivative may change across knots; sampling both knot sides is appropriate for a flux involving \(v''\). The identity does not show that the underlying exact graph solution is absent, that the BVP equation is wrong, or that another mesh will satisfy the gate. It shows precisely why these saved interpolants fail the registered **physical** test despite all solver statuses being zero.

## One possible final-attempt remedy, subject to a new registration

A defensible single preparation for review is to retain the same cubic representation, all 26 cases, \(R\), tolerances, node cap, and physical/linear/zero/ordering gates, but begin from a declared source mesh with 1,921 points and 3,840 outer points (5,761 total, below the 20,000-node cap). Preserve the original off-mesh check and add the interval-and-knot-side grid plus an explicit \(v'(0)=0\) check. This targets the identified derivative defect, including the pole, without redefining physical \(Q\) or relaxing any acceptance threshold. It is a proposal for independent code preflight and a separately registered attempt, **not** an instruction to execute attempt 3 now.

The failing source interval has width about \(4.17\times10^{-3}\); a 1,921-point source mesh would start with spacing about \(5.21\times10^{-4}\), a factor of eight smaller. If the second-derivative defect happened to scale quadratically with that spacing, the observed \(2.42\times10^{-4}\) peak would project to roughly \(3.8\times10^{-6}\). That is a heuristic only. The adaptive solver may distribute nodes differently, the pole or another interval may dominate, and no measured refinement series establishes this rate. The gate stays failed until a fresh, independently checked physical residual passes. A small formal system residual must never substitute for that result; \(K\) remains uncomputed under the frozen attempt-2 contract.
