# Independent review of the two-area cap analysis

## Scope and clocks

This is an independent algebra, rank, and evidence review of the implemented
zero-line-tension cap inverse. I derived the rank conditions before reading the
new two-area findings, theory, numerical narrative, or results.

- First recorded review clock: 2026-09-22 21:18:08 EDT
  (2026-09-23 01:18:08 UTC).
- Initial counterexamples and qualifications sent to the lead, theory worker,
  and numerical worker: 2026-09-22 21:18 EDT.
- Final review clock: 2026-09-22 21:26:16 EDT
  (2026-09-23 01:26:16 UTC).

No production source was edited, no data were fitted, and no biological or
novelty claim is reviewed as established here.

## Independent algebraic conclusion

For nonzero coverage, define `B=4*pi*kappa`, `P=F/kBT`, and `y_i=H_i/u`.
The unclipped shared-parameter model is

`y_i(B) = (B*C + P)/(2*B + sigma*A_i)`.

At one known constant rigidity, two distinct areas identify `sigma` and only
the combined numerator `N=B*C+P`. They cannot split spontaneous curvature from
force: `C -> C+delta`, `P -> P-B*delta` is an exact symmetry. The Jacobian rank
is generically two, and drops to one at zero signal because tension is then
invisible. Adding further areas at the same rigidity does not remove this
`C`/`P` ambiguity.

With two distinct known rigidity values, two distinct areas generically
identify all three shared parameters. At any nonzero matched state, the area
ratio identifies tension; the numerator recovered at two rigidities then gives
the slope `C` and intercept `P`. This also removes the single-area compensation
ridge because `P=C*sigma*A_i/2` cannot hold at two distinct areas unless it
collapses to a boundary case. All-zero signal remains degenerate. Equal areas,
zero-coverage frames, and a set of entirely clipped observations supply no such
rank gain.

The principal variants have different conclusions:

| Model | Constant known rigidity | Known varying rigidity |
| --- | --- | --- |
| Shared `C,P,sigma` | Rank 2 of 3 for two areas | Generic rank 3; two distinct levels suffice locally |
| `P_i=rho*A_i` | Rank 2 of 3 | Generic rank 3, but `rho=C*sigma/2` is an exact all-area ridge |
| Area-specific `C_i`, shared `P,sigma` | Rank 2 of 4 | Generic rank 4 with two levels; three levels remove a two-level singular hypersurface, except simultaneous compensation `C_i*A_i=2P/sigma` |
| Unknown common rigidity scale | Rank 2 of 4 for the shared model | Generic rank 3 of 4 because `(alpha,P,sigma)` has an exact common scaling symmetry |

For area-specific curvature, the theory's two-rigidity determinant condition
was independently checked by solving each area's two observations for an
affine function `P_i(sigma)`. Equality of the two slopes gives Eq. (12) in
`TWO_AREA_THEORY.md`. The equations conditional on observed `y_ij` are linear
in `(C_1,C_2,P,sigma)`, so a full-rank two-level design is already globally
unique. On the determinant-zero hypersurface the solution set is affine, not
an isolated alias. A third distinct level can remove that two-level singular
hypersurface and leaves simultaneous compensation as the nontrivial ridge.

## Numerical evidence audit

The numerical artifact evaluates the analytic clipped continuum expression and
its analytic Jacobian. It does not take finite differences through the
400-point grid argmin. That separation is necessary: the grid map is
piecewise constant, so grid derivatives can be zero within cells and unstable
at cell changes. Analytic derivatives are explicitly zeroed for saturated
clip values, and finite differences are compared only on interior rows.

The stored script hash matches the script on disk. Across the recorded cases,
the maximum scaled finite-difference discrepancy is `3.70e-12`. The varying,
two-area records reproduce the expected ranks: shared generic `3/3`, shared
single-area-ridge case `3/3`, force-density ridge `2/3`, area-specific generic
`4/4`, area-specific compensation `3/4`, and unknown rigidity scale `3/4`.
Exact symmetry errors are at most about `5.3e-18`; the shared single-area ridge
transformation instead changes the two-area prediction by about
`9.83e-4 nm^-1`, as it should.

Rank does not imply precise recovery. Using the declared dimensionless column
scales, the full-rank varying two-area examples have condition numbers of about
`46.3` (shared parameters), `1339` (force proportional to area), and `118.8`
(area-specific curvature). These are local design diagnostics, not microscope
precision estimates, and they depend on the chosen areas, rigidity range, and
column scaling. The primary experiment does not simulate noise or report uncertainty.
Near-equal areas, small tension-area contrast `sigma*|A2-A1|/(8*pi*kappa)`,
small rigidity range, weak signal, and division by small `u` must all worsen
conditioning even when exact rank is full. Those limiting sweeps were not
included in the immutable result set and should be described as analytic
expectations rather than numerical findings.

The first figure used an absolute horizontal threshold while labeling it as a
relative rank threshold. That display is not valid for comparing records with
different largest singular values. I visually inspected the corrected
`two_area_comparison_v2.png` and inspected its renderer: it reads the immutable
JSON, plots `s/s_max`, places the relative cutoff at `1e-10`, and labels the
`1e-16` display floor. The rank computation and stored singular values were
unaffected by the first display error.

The registered noise postprocess correctly applies
`sd(z_worst)=sigma_H/s_min(J_z)` only to full-column-rank cases. At hypothetical
iid curvature noise `1e-5 / 1e-4 / 1e-3 nm^-1`, it gives worst-direction scaled
standard deviations `0.00802 / 0.0802 / 0.802` for shared parameters,
`0.228 / 2.28 / 22.8` for force proportional to area, and
`0.0272 / 0.272 / 2.72` for area-specific curvature. The latter two examples
show why structural rank is insufficient for a practical claim. Rank-deficient
cases are correctly reported as unidentifiable rather than assigned a finite
pseudoinverse uncertainty. These are conditional local linear bounds under a
frozen hypothetical noise model, not individual-parameter intervals or an
empirical imaging claim.

## Biological assumptions required

The identification result is conditional on assumptions that the geometric
data alone cannot establish:

- Both areas must be externally known or calibrated and must describe the
  fixed-area ensemble used by the cap energy. Inferring area and curvature
  from the same shape fit introduces correlated errors and does not create an
  independent mechanical observable.
- Compared states need known nonzero coverage, matched assembly state, and a
  known rigidity history in absolute units. Knowing only the shape of the
  rigidity ramp leaves absolute force and tension unidentified. An
  independently measured rigidity scale, independently measured nonzero
  tension, known nonzero force, or another calibrated mechanical parameter can
  anchor that scale; the remaining rank conditions must still be checked.
- The shared-total-force result assumes `C`, total `F`, and `sigma` do not
  change when area changes. If active machinery scales with area, the
  force-density model is more appropriate and retains its exact compensation
  ridge. If coat composition or preferred curvature changes with size,
  area-specific `C_i` must be modeled; two rigidity levels are generically
  enough, while a third protects against the two-level singular hypersurface.
- The prediction assumes a quasistatic spherical cap, zero line tension, and
  an interior optimum. Size-dependent neck mechanics, surrounding-membrane
  boundary conditions, nonequilibrium dynamics, line tension, and flat or
  closed saturation are outside this inverse formula.

Therefore the two-area result is a conditional synthetic measurement-design
statement. It neither discovers a biological scaling law nor establishes that
real pits share force, curvature preference, tension, or rigidity.

## Disposition

The algebra and stored numerical ranks support the qualified conclusions in
`TWO_AREA_THEORY.md` and `TWO_AREA_FINDINGS.md`. The theory's initially stated
possibility of isolated two-level aliases was corrected: the inverse equations
are linear conditional on the observed curvatures, so full rank gives global
uniqueness and singularity gives an affine continuum. The normalized figure,
noise postprocess, source hashes, analytic-versus-grid separation, actual
theory clock, and biological qualifications have been checked. I accept the
result as a model-conditional measurement-design finding, with no biological
discovery, empirical precision, or novelty claim.
