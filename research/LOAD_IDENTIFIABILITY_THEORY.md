# Full-membrane curvature versus balanced load: theory note

Task `load-identifiability-theory-001`, attempt 1, 2026-09-26. This is a conditional calculation for the frozen small-slope [design](load_identifiability_design.json). It concerns spatial sources in the full membrane operator, rather than the spherical-cap rank result in [TWO_AREA_FINDINGS.md](TWO_AREA_FINDINGS.md). It does not fit empirical data.

## Operator and source nullspace

Use `E[h]=∫{κ/2(Δh-c)²+σ/2|∇h|²-fh}d²x` on the infinite plane. Here `κ,σ>0` are uniform; `c` is preferred **total** curvature, small-slope mean curvature is `H=Δh/2`, and positive signed `f` does positive work for positive `h`. Axisymmetric fields are regular at the origin; height and slope vanish at infinity; `∫f d²x=0` avoids an unspecified net-load reaction. For compactly supported variations, integration by parts gives

`δE=∫[κΔ(Δh-c)-σΔh-f]δh d²x`, hence

`L_σ h ≡ (κΔ²-σΔ)h = κΔc+f`.                         (1)

This matches the force-free equation in [FULL_SHAPE_MAPPING.md](FULL_SHAPE_MAPPING.md). The positive quadratic energy yields a unique decaying height with its vertical reference fixed.

Complete shape observes the **sum** on the right of (1). For any smooth localized axisymmetric `g` and amplitude `ε`,

`δc=εg`, `δf=-κεΔg`                                      (2)

leaves all shape data unchanged. The added load is balanced since `∫Δg d²x=0`. Explicitly, `g=exp[-r²/(2a²)]` gives `δf=κε(2/a²-r²/a⁴)g`, a positive center and negative surround with zero integral. If the same unknown source fields persist across known-tension repeats, (2) cancels at every `σ`; changing tension alone cannot remove this unrestricted nullspace. Allowing sources to change across repeats introduces more unknowns.

## Prescribed Gaussian pair and full-profile rank

The frozen templates, chosen before inspecting rank, are `c=Cg_a`, `g_w=exp[-r²/(2w²)]`, `f=F(p_a-p_b)`, `p_w=g_w/(2πw²)`, and `b=2a`. The two load components integrate to `F` and `-F`; they decay without compact support. `a` is an externally prescribed Gaussian width, not a fitted cap area or material coat boundary. With `q=|k|` and `ĥ(k)=∫h(x)e^{-ik·x}d²x`, (1) becomes

`(κq⁴+σq²)ĥ = -κq²(2πa²C)e^{-a²q²/2}+F[e^{-a²q²/2}-e^{-b²q²/2}]`.     (3)

Both source terms vanish as `q²` near zero, consistent with a decaying flat-reservoir solution. After removing the common Gaussian, the load-to-curvature source ratio is proportional to `[1-e^{-3a²q²/2}]/q²`; it tends to a nonzero constant at small `q` and to zero at large `q`. Thus the source templates are not proportional. The denominator in (3) is positive for `q>0`, so their full height-response fields are independent. Ideal registered full-profile shape has rank two for `(C,F)` **conditional on known** `a,κ,σ` and the prescribed templates. Template independence is an assumption of the design, not evidence that these forms occur biologically.

## Declared two-summary rank

Let `t=σa²/κ>0`, `s=aq`, `G=e^{-s²/2}`, `D=G-e^{-2s²}`, and `J=J₀(s)`. Fourier-Bessel inversion gives `[H_apex,d_a]^T=M[C,F]^T`, where `H_apex=Δh(0)/2` and `d_a=h(a)-h(0)`:

| Coefficient | Exact integral |
| --- | --- |
| `M₁₁` | `A/2`, `A=∫₀∞s³G/(s²+t)ds` |
| `M₁₂` | `-B/(4πκ)`, `B=∫₀∞sD/(s²+t)ds` |
| `M₂₁` | `a²P`, `P=∫₀∞sG(1-J)/(s²+t)ds` |
| `M₂₂` | `-a²Q/(2πκ)`, `Q=∫₀∞D(1-J)/[s(s²+t)]ds` |

All integrals converge for positive `t`. The exact rank criterion is

`det M = a²(BP-AQ)/(4πκ) ≠ 0`.                         (4)

Zero determinant means these two summaries lose an amplitude direction even though the complete fields remain independent; a small determinant can make recovery imprecise. This note supplies the preregistered rank criterion but does not claim a numerical determinant or noise performance. Practical precision would require calibrated summary covariance and an extraction model.

A constant vertical offset cancels in both summaries. Center/pose errors change their extraction; an unknown lateral scale changes physical `a`, curvature and `t`, while an unknown vertical scale rescales the apparent amplitudes. If `κ` and `σ` have an unknown shared positive scale, `(κ,σ,F)→λ(κ,σ,F)` leaves (1) and all shapes invariant with `C` fixed. Absolute `F` then requires independent mechanical scale calibration. Unknown `σ/κ` or template widths add parameters and require a fresh rank calculation. The public fitted cap area is not a prescribed `a`.

## Minimal independent observable

An independently calibrated **spatial traction map** `f(r)`, including the compensating return load, would break (2) if the full shape, `κ`, `σ` and radial scale were also calibrated. Equation (1) then determines `Δc=(L_σh-f)/κ`; localized decay fixes the harmonic freedom in `c`. Net force alone cannot do this because both candidate loads are balanced. This states a mathematical measurement requirement, not experimental availability, force calibration from current tables, biological preference or novelty.
