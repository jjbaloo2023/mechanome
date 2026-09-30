# Independent review: full-membrane curvature and balanced-load identifiability

**Task:** `load-identifiability-review-001`, attempt 1.

**Cycle first observed:** 2026-09-26 14:48:17 UTC.

**Reviewer first observed:** 14:50:56 UTC; **review checkpoint:** 14:55:23 UTC.

**Registered lead cutoff/checkpoint:** 15:03:17 / 15:08:17 UTC.

**Scope:** independently derive the frozen linear operator, assess the preregistered templates, and review the theory and single-configuration integral check. No solver, sweep, empirical fit, source download, or biological inference.

## Disposition

**Accept the conditional structural result.** The unrestricted curvature/load fields have an exact balanced-load nullspace even with complete ideal shape and known-tension repeats. For the independently prescribed Gaussian curvature and difference-of-Gaussians load templates, the two full-profile responses are linearly independent when widths, rigidity and tension are known. The preregistered two-summary response matrix has nonzero rank at the one checked configuration, but its columns are nearly parallel on the declared dimensionless axes. These are separate statements; no calibrated precision, absolute force, empirical or biological conclusion follows.

## Independent signs, balance and unrestricted nullspace

For the frozen energy `E=integral [kappa/2 (Delta h-c)^2+sigma/2 |grad h|^2-fh] d^2x`, preferred total curvature is `c`, small-slope mean curvature is `H=Delta h/2`, and positive `f` does work for positive height. Two integrations by parts give

`kappa Delta(Delta h-c)-sigma Delta h-f=0`,
or `(kappa Delta^2-sigma Delta)h=kappa Delta c+f`.

The Fourier response for nonzero `k` is

`h_hat=[-kappa k^2 c_hat+f_hat]/[k^2(kappa k^2+sigma)]`.

Thus, for any smooth localized axisymmetric `g`, the pair `delta c=epsilon g`, `delta f=-kappa epsilon Delta g` produces exactly the same shape. The added load is balanced because `integral Delta g d^2x=0`. For a Gaussian `g`, it has a positive center and negative surround. Because the combined source `kappa Delta c+f` stays the same, changing only `sigma` with the same `kappa,c,f` leaves this unrestricted ambiguity intact. Integrating the field equation over the infinite reservoir also requires zero net `f` when boundary fluxes vanish. An unbalanced load needs an explicit reaction or finite boundary; tension alone does not remove the `k=0` obstruction.

## Registered templates and complete-profile rank

The registered `g_w=exp[-r^2/(2w^2)]` and `p_w=g_w/(2 pi w^2)` obey `integral p_w d^2x=1`. Consequently `f=F(p_a-p_b)`, `b=2a`, is a smooth, decaying, zero-net-load traction with components `F` and `-F`. Here `F` is an opposite-component amplitude, **not** a net force or automatically the positive-lobe integral. The curvature source `c=Cg_a` also has a balanced Laplacian. Both source transforms vanish as `k^2` at zero, permitting regular origin and flat far-field response.

For the prescribed amplitudes, `c_hat/C=2 pi a^2 exp(-a^2k^2/2)` and `f_hat/F=exp(-a^2k^2/2)-exp(-b^2k^2/2)`. Proportional complete-profile responses would require `[1-exp(-(b^2-a^2)k^2/2)]/k^2` to be constant at all positive `k`; it is not for `b=2a`. The full profile therefore has rank two for `C,F` conditional on the templates and known `a,kappa,sigma`. A positive `C` gives negative central height, positive apex `H` and positive `h(a)-h(0)`; positive `F` gives the opposite signs. Those signs alone do not certify the scalar-summary rank.

## Two-summary check and normalization

I checked the theory draft's four Fourier-Bessel integrals for `H_apex=Delta h(0)/2` and `d_a=h(a)-h(0)`. With `t=sigma a^2/kappa`, `G=exp(-s^2/2)`, `D=G-exp(-2s^2)`, and `J=J0(s)`, the draft correctly writes `M11=A/2`, `M12=-B/(4 pi kappa)`, `M21=a^2P`, `M22=-a^2Q/(2 pi kappa)`, where `A=integral s^3G/(s^2+t)`, `B=integral sD/(s^2+t)`, `P=integral sG(1-J)/(s^2+t)`, and `Q=integral D(1-J)/[s(s^2+t)]`. Their determinant is `a^2(BP-AQ)/(4 pi kappa)`. This is a criterion, not a claim of global rank across controls.

The predeclared single configuration `a=kappa=sigma=1, b=2` was checked in `load_identifiability_results_001.json` using `check_load_identifiability.py`. I inspected the script's transform and scale factors: rows `(a H_apex,d_a/a)`, columns `(Ca,Fa/kappa)` require a factor of `kappa` on the force response and `1/a^2` on both depth response derivatives, as implemented. The analytic exponential-integral apex formulas agree with the direct integrals. The saved matrix is

```
[ 0.2692723418790674  -0.022344638433383735 ]
[ 0.11437934283585115 -0.010096040328866029 ]
```

Its determinant is `-1.6281936314413106e-4`, versus a first-order propagated quadrature diagnostic of `4.74000360856511e-14`; baseline and tighter quadrature matrices differ by at most `3.47e-18`. The script also checks the signed plane integral of the unit load near zero. This resolves structural rank for the two chosen summaries at this one configuration. The column-angle sine is `0.0226976` and the matrix 2-norm condition number is `529.37` on those axes: the columns are nearly parallel and the result offers no measured noise precision. Quadrature error estimates are diagnostics, not rigorous interval certificates. No widths, tensions, summaries or amplitudes were selected after inspecting this result.

## Nuisances, protocol and limit

The theory draft correctly separates height-reference, center/pose, lateral and vertical scales, template widths, tension/rigidity ratio and their common mechanical scale. `H_apex` and `d_a` remove a constant vertical offset but need a registered center and calibrated spatial/height scales. Static shape depends on `sigma/kappa`, `C` and `F/kappa`; the transformation `(kappa,sigma,F)->lambda(kappa,sigma,F)` leaves it unchanged. Two scalar summaries cannot by themselves identify `C,F` plus an unknown `sigma/kappa`. An unmeasured fitted cap area cannot stand in for externally prescribed `a`.

The theory's proposed independent, calibrated spatial traction map is a mathematically valid way to break the unrestricted source nullspace: with known full shape, `kappa,sigma`, center and scale, the map fixes `Delta c=(L_sigma h-f)/kappa`, and localized decay removes harmonic freedom. Measuring net force alone would fail because both candidate loads integrate to zero. A separate possible controlled design is two known distinct rigidity values with identical `c,f`: `S_j=(kappa_j Delta^2-sigma_j Delta)h_j=kappa_j Delta c+f`, so subtracting identifies `Delta c` if all coefficients and template invariance are calibrated. This is a mathematical prospect, not a claim that either measurement is currently feasible.

The result is distinct from the completed spherical-cap two-area algebra because it treats spatial sources and the balanced-load/boundary condition in the full linear membrane operator. It does not validate a nonlinear solver, identify an active cellular mechanism, recover force from the LocMoFit tables, or establish novelty.


## Final synthesis check (14:57:27 UTC)

I reviewed `LOAD_IDENTIFIABILITY_FINDINGS.md` against the frozen energy, theory and saved one-configuration result. Its two-rigidity protocol is mathematically sufficient **under the stated controls**: for complete calibrated profiles with known distinct `kappa_1,kappa_2`, known `sigma_1,sigma_2`, invariant spatial `c,f`, and identical boundary/reaction conventions, each reconstructed source is `S_j=(kappa_j Delta^2-sigma_j Delta)h_j=kappa_j Delta c+f`. Subtraction gives `Delta c=(S_2-S_1)/(kappa_2-kappa_1)`, then `f=S_1-kappa_1 Delta c`. Localized decay fixes the harmonic ambiguity in `c`. Full registered geometry and a derivative observation model are essential; the public cap tables do not provide them. The synthesis states these conditions and confines the result to a prospective mathematical design. Its matrix, determinant, conditioning and no-calibration wording agree with the independent review. I find no synthesis error requiring correction.
