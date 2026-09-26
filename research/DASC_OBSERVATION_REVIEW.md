# Independent DASC observation review — 2026-09-22

Task `dasc-observation-review-001`, attempt 1. Scientific review window:
2026-09-22T20:07:43.9684305-04:00 to 2026-09-22T20:11:33.4292743-04:00
(3m 49s observed wall time). No network access, fits, tests, or source changes.

## Disposition

**Accept without required correction.** The decision correctly parks the AP2
WT versus K57E/Y58E contrast as a physical-mechanism test under the currently
verified observation constraints, while retaining two narrower uses: published-
result reproduction under fixed analysis conventions and a predeclared
detection-sensitivity exercise. It does not claim that AP2 biology is absent,
that the published phenotype is an artifact, or that all constrained models are
untestable with single-channel data.

The selection construction is correct for normalized observed densities. With
`f=(p_W+p_M)/2` and `q_c=p_c/(p_W+p_M)` wherever the denominator is positive,
`0 <= q_c <= 1`, `integral(q_c f)=1/2`, and conditioning gives `p_c` exactly;
setting `q_c=0` on the joint zero set is harmless. The text correctly presents
this as an existence result for arbitrary condition-dependent selection. It
explicitly says this is not a calibrated detector model and uses the result only
to motivate independent bounds on detection and retention. It therefore does
not overgeneralize to a fixed measured detector or to every mechanistic model.

The retained JATS supports the source reconciliation. Results section
`s2-4`, “Validation through perturbation of established CCP initiation and
stabilization pathways,” says clustering was determined from control movies and
the control boundaries were applied to experimental perturbations in the AP2
discussion. Methods `s4-1`, “Computational flow of DAS analysis,” nevertheless
instructs the reader to cluster a single condition and repeat that step for all
same-day conditions. Keeping this apparent paper-level tension unresolved until
a pinned implementation/configuration is available is correct.

The decision also distinguishes normalization from calibration accurately.
Control-derived `D(i,t)`, control mean/SD feature scaling, and the per-day affine
control-CDF adjustment specify references and reduce day-to-day variation; none
independently measures gain, noise, bleaching, or detection completeness. This
supports parking the mechanistic contrast without invalidating reproduction.

Finally, the proposed theory-equations-first direction is appropriately prior
to another archive search or implementation: extract each primary model's
equations and control assumptions, require a differing observable prediction
under matched constraints, and identify the needed measurement. The warning
against relabeling parameter choices or imposed force histories as distinct
biological mechanisms is scientifically necessary.
