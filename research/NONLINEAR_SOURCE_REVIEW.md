# Independent review: nonlinear graph curvature/load compensation

**Task:** `nonlinear-source-review-001`, attempt 1, 2026-09-26. This is an independent variational check of the frozen [design](nonlinear_source_design.json) and the separate [theory note](NONLINEAR_SOURCE_THEORY.md), after the Bucher inclusion branch stopped. It concerns one exact axisymmetric single-valued graph with prescribed sources in projected radius. It is not a nonlinear solver, a stability test, or a biological mechanism claim.

## Independent derivation

Write `p=h'(r)`, `J=√(1+p²)`, and total curvature `C=(rp/J)'/r`. The registered energy is

`E=2π∫₀∞ r{κ/2(C-c)²J+σ(J-1)-fh}dr`,

where `f` is a vertical dead load per projected area and `c(r)` is preferred total curvature. For a finite source change `c→c+g`, the difference in bending energy at a fixed candidate shape is

`ΔE_b=2πκ∫₀∞ rJ[(c-C)g+g²/2]dr`.

The `g²J/2` term is essential; dropping it would check only infinitesimal source changes. Let `A=cg+g²/2`. Since `JC=p'/J²+p/r`, the integrand divided by `2πκ` is `rJA-rgp'/J²-gp`. Varying this functional with respect to `h`, integrating by parts, and equating its Euler derivative with the change in `-2π∫rfh dr` gives the exact stationary-shape correction

`δf_h(r)=-(κ/r) dT_h/dr`,

`T_h=r A p/J + r g'/J² - g p²/J²`.                 (1)

This includes the variation of the area factor and the full square. It depends on the specified shape slope, so the shallow source compensation is not a universal shape-independent transformation of this nonlinear energy. It does show that one specified stationary graph can be preserved by an adjusted *signed* load within this model; it says nothing about stability or whether another stationary branch is selected.

For smooth compactly supported radial `g`, regular `p(0)=0` and decay, `T_h(0)=T_h(∞)=0`. Hence `2π∫₀∞rδf_h dr=-2πκ[T_h(∞)-T_h(0)]=0`: the correction includes its own return load. At a flat graph `p=0`, (1) gives exactly `δf=-κ(g''+g'/r)`. If the original flat equilibrium has `f=-κΔ_rc`, then the changed sources keep it flat at every tension. This explicit degeneracy prevents a blanket claim that nonlinearity or two tensions always identify the sources.

If `p,c,g` are jointly small of order `ε`, `T_h=rg'+O(ε³)` and (1) reduces to the reviewed linear `δf=-κΔ_rg+O(ε³)` under smooth scaling. A shallow approximation that varies only `p` while keeping a finite `g` does not justify that order statement.

## Two known-tension profiles

Suppose two actual stationary profiles `h₁,h₂` were obtained at distinct known tensions with the **same** `κ,c,f`, boundary convention and projected-coordinate source labels. A single new `δf` preserves both only if `d(T₁-T₂)/dr=0`. Compact source support and the boundary conditions remove the integration constant, so the exact criterion is `T₁(r)=T₂(r)` for every `r`. Equivalently,

`(rg'+g)(J₁⁻²-J₂⁻²)+r(cg+g²/2)(p₁/J₁-p₂/J₂)=0` for every `r`.      (2)

Different profiles may fail this condition, but (2) alone does not prove that every nonzero `g` is excluded. In particular, identical profiles and the flat case satisfy it. The tension coefficients cancel from the source-change functional, though they determine which equilibrium profiles are compared. One must verify that proposed profiles actually solve the original equations; arbitrary test curves do not establish identifiability.

## Disposition and limits

Accept (1)–(2) as an exact **conditional stationarity** criterion for the registered graph energy. I derived (1) independently before reading the specialist theory note, then checked equivalence: its `q_h` is `T_h/r`, and its two-profile Eq. 7 multiplied by `r` reduces to (2). Both accounts retain the finite `g²J/2` term, signed load convention and zero-net-force boundary flux. The regular-origin expansion also makes (1) finite at `r=0`. The result neither proves a universal nonlinear gauge nor proves global uniqueness from two tensions. It does not cover overhangs, material-coordinate coats, normal-following loads, pressure, finite-boundary reactions, branch stability, or noisy microscopy. Those choices can alter the correction. No empirical source separation follows from the stopped Bucher/Saleem data contracts.


## Final synthesis check (2026-09-26 16:00 UTC)

I checked [NONLINEAR_SOURCE_FINDINGS.md](NONLINEAR_SOURCE_FINDINGS.md) against the frozen design and equations above. Its two forms of `T_h` are algebraically identical to (1), and its two-profile condition is (2) after using `p²/J²=1-J⁻²`. It correctly requires actual stationary profiles with the same projected-coordinate `c,f,κ`, and the same balanced correction; it does not treat arbitrary curves as equilibria. The shallow claim explicitly scales slope, `c` and `g` jointly, so it does not extend the quadratic rule to finite curvature at small slope alone. The flat family `f=-κΔ_rc` follows exactly from stationarity and preserves a nonzero compact `g` ambiguity at every tension. I find no correction required. The synthesis denies global uniqueness, stability and empirical permission, and its queued compact-`g` question remains conditional on the declared source support and actual profiles.
