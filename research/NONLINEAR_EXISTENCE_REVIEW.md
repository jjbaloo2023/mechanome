# Independent review: a small-curvature exact stationary branch

**Assessment.** The proposed source does admit a defensible local existence and strict slope-ordering proof in the registered exact graph model, provided the nonlinear implicit-function step is carried out in a weighted **radial-vector** space, rather than asserted from a pointwise slope expansion. The proof is local in sufficiently small positive `epsilon`; it gives stationary profiles, not stability, global branch selection, or an empirical identification claim.

For `kappa=1`, put `q(x)=p(r)e_r=grad h`, `J=(1+|q|^2)^(1/2)`, and `C=div(q/J)`. The exact first-variation flux is

`Q(q,c) = -grad[(C-c)J]/J^3 + [((C-c)^2)/2+sigma] q/J`.

For a radial field this is the scalar flux of the frozen energy times `e_r`. Stationarity with `f=0` gives `(r Q_r)'=0`; regularity at the origin makes the constant zero. Thus the equation to solve is **`Q(q,c)=0`**, not merely its differentiated version, which could admit an unphysical `constant/r` flux.

At `(q,c)=(0,0)`, `D_q Q[v]=-grad div v+sigma v`. On a pure radial vector field (equivariant under all of `O(2)`, including reflections), `curl v=0`, so `grad div v=Delta v` and the derivative is `-Delta+sigma`. The source derivative is `D_c Q[phi]=grad phi`. Hence `q_sigma(epsilon)=epsilon v_sigma+o(epsilon)` solves

`(-Delta+sigma)v_sigma=-grad phi`,

or, with `v_sigma=v_sigma(r)e_r`,

`L_sigma v_sigma=-phi'(r)`, `L_sigma=-d^2/dr^2-(1/r)d/dr+1/r^2+sigma`.

Here `phi'(r)<0` for `0<r<1` and `phi` is smooth with zero extension. The regular-decaying order-one Green kernel is positive: it is proportional to `I_1(sqrt(sigma) r_<) K_1(sqrt(sigma) r_>)`. It follows that `v_2(r)>0` for every `r>0`. The resolvent identity gives `L_1(v_1-v_2)=v_2>0`, so `v_1-v_2>0` for every `r>0`. Near the origin the Green representation gives strictly positive limits of `v_2(r)/r` and `(v_1-v_2)(r)/r`; these ratios are continuous on `[0,1]`, and each has a positive minimum. This origin-normalized margin is needed: positivity at fixed `r>0` alone would not justify uniform nonlinear ordering arbitrarily close to zero.

A suitable continuation setup is `X_mu={O(2)-equivariant q: exp(mu*sqrt(1+|x|^2))q in C^(2,alpha)(R^2)}` and corresponding `Y_mu` with `C^(0,alpha)`, for `0<mu<1`, `0<alpha<1`. The curvature bump is smooth radial compact support. `Q:X_mu x R -> Y_mu` is smooth near zero: `C=div(q/J)` costs one derivative and the flux gradient costs one more, while all denominators stay positive. The linear inverse `(-Delta+sigma)^-1:Y_mu -> X_mu` is bounded for `sigma=1,2`; this follows from the positive massive Green kernel, whose exponential decay beats the selected weight, together with standard local Schauder estimates. The inverse preserves `O(2)` equivariance, so solutions have no azimuthal component and are gradients of radial heights. An implicit-function theorem therefore supplies unique small `q_sigma(epsilon)` in this local space, with `q_sigma=epsilon v_sigma+O(epsilon^2)` in `X_mu` (in fact parity allows a higher-order remainder). Define `h_sigma(r)=-integral_r^infinity p_sigma(s)ds`; exponential decay makes its flat-reservoir height and slope well defined, and vector-field regularity gives `p_sigma(0)=0` and a continuous `p_sigma/r` at the origin.

The `X_mu` remainder controls `p_sigma/r` uniformly on `[0,1]`: an `O(2)`-equivariant `C^1` vector field vanishing at zero obeys `|q(r)|/r <= ||Dq||_infinity`. Hence, for sufficiently small positive `epsilon`, the strictly positive linear margins imply `p_1(r)>p_2(r)>0` for all `0<r<=1`, including the flat source endpoint. Because `p/sqrt(1+p^2)` is strictly increasing, the exact two-profile uniqueness coefficients satisfy `D>0` and `S>0` there. The previously reviewed compact-source theorem consequently applies to these **actual** stationary profiles for support `R0=1`.

This argument requires the weighted resolvent and smooth-map claims to be stated and justified explicitly in the companion proof. It establishes one small stationary branch at each tension with the same `c=epsilon phi` and `f=0`; it does not select a stable branch, determine `epsilon` numerically, or remove the unrestricted-source flat-family counterexample outside this conditional setting.



## Cross-check of the strict comparison

[The separate ordering derivation](NONLINEAR_EXISTENCE_ORDERING.md) gives an especially transparent endpoint check. Set `z_sigma=v_sigma/r` and extend it as a radial scalar in `R^4`. Direct substitution in the order-one radial operator gives `(-Delta_R4+sigma)z_sigma=-phi'/r`, where `-phi'/r=2*phi/(1-r^2)^2` inside the disk, has value `2` at the origin, and extends smoothly by zero at `r=1`. The massive heat kernel is strictly positive, hence `z_2>0` and `z_1-z_2=(-Delta_R4+1)^-1 z_2>0` at every finite radius. Their minima on `[0,1]` are strictly positive. This independently verifies the origin and support-edge margins used above; no comparison at arbitrarily large radius is needed for the compact-source theorem.

## Review of the companion existence proof

[The existence derivation](NONLINEAR_EXISTENCE_THEORY.md) now states all three exact flux formulas with the required positive tension/square term. Its normalized-slope variable `U=(p/J)e_r` gives `t=div U-c` and the exact polynomial flux `F=-(1-|U|^2)grad t-t(DU)U+(t^2/2+sigma)U`; expanding `J=(1-|U|^2)^(-1/2)` reproduces the original graph flux because `grad J/J^3=(DU)U` for a pure radial field. The derivative is `-grad div+sigma`, equal to `-Delta+sigma` on the full `O(2)`-equivariant radial-vector space. The stated Yukawa-convolution bound for `0<mu<1` plus local Schauder estimates supplies the weighted inverse needed by the implicit-function theorem. Its odd branch remainder in `X_mu` is stronger than the uniform `o(epsilon)` control of normalized slope divided by radius needed for ordering. The height reconstruction is integrable at infinity and regular at the origin. I find no remaining analytic prerequisite within the declared local stationary and compact-support claim.

The conclusion is deliberately local: one small branch for each specified tension and a strict normalized-slope gap through `R0=1`. This proves that the earlier compact-source uniqueness criterion is attained by actual stationary profiles in this model. It says nothing about stability, larger branches, arbitrary supports, load or coordinate uncertainty, or measurable precision.
