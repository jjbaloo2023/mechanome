# Independent review: LocMoFit adapter and real consumers

**Task:** `locmofit-adapter-review-001`, attempt 1.  
**Cycle first observed:** 2026-09-26 14:08:43 UTC.  
**Reviewer first observed:** 14:11:33 UTC; **this review checkpoint:** 14:19:39 UTC.  
**Registered implementation cutoff:** 14:23:43 UTC; **final checkpoint:** 14:28:43 UTC.  
**Scope:** bounded code-contract review; no empirical fits, raw microscopy, network access, dependency installation, or physical solver runs.

## Disposition

**Accept the bounded adapter and consumer contract cleanup.** The default adapter now states that per-site curvature uncertainty is unknown, retains the historical raw nonnegative cohort, and preserves deposited raw and corrected fields. The two fitting consumers independently require deliberate exploratory opt-in and label their returned scores as conditional diagnostics. These changes prevent the processed cap tables from silently becoming a calibrated likelihood or a mechanism verdict. They do not supply the missing point-cloud observation operator, covariance, nuisance settings, or a within-pit trajectory.

## Consumer inventory and review

`validation/realdata/ingest_smlm_locmofit.py` defines `SMLMSite`, `SMLMGeometrySet`, and `H_sigma_inv_nm`. No direct `SMLMGeometrySet` consumer reads that uncertainty field. Generic `curvo.analyze` and `curvo.recovery` read `H_sigma_inv_nm` on a distinct perception trace type; there is no traced static-adapter call path to them. `smlm_pseudotime.py` consumes site theta, H, R, and surface area, bins a static population, and propagates provenance. It now explicitly denies a measured within-pit trajectory. `smlm_shape_energetics.py` makes its own IQR/sqrt(n) likelihood scale and arbitrary floor. `smlm_mechanism.py` fits scatter on overlapping rolling medians and scores area/edge transforms of the same cap fit. Adapter uncertainty alone would not have guarded these two consumers.

Each fitting entry point refuses by default before reading input arrays or starting a sampler. Explicit `allow_exploratory=True` retains historical numerical formulas while setting `calibrated_likelihood=False` and `mechanism_inference_allowed=False` even when caller provenance falsely says true. The curvature score retains its numerical lnB and favored curve but forces `decisive=False`; a threshold crossing is separately marked as an exploratory diagnostic. The area/edge verdict follows the actual score winner and says the transforms are dependent, not independent held-out evidence. The shape inverse identifies its synthetic area-to-coverage mapping and IQR/floor scale as surrogate choices. Existing historical JSON output files were not migrated.

## Adapter contract and compatibility

The default `geometry="raw_nonnegative"` retains the old row selection and geometry values; it returns `H_sigma_inv_nm=None`. `legacy_curvature_sigma=True` explicitly restores the old `hypot(3.9,12.5)/R^2` heuristic with uncalibrated provenance. `geometry="corrected"` selects deposited corrected H and theta while retaining raw H, theta, signed radius, deposited area, rim length, projected area, source key/path and disconnected flag. The selected `R_nm` remains the legacy magnitude. Corrected-flat H/theta need not satisfy identities with the retained raw radius/area/projection, which is expressly documented; no geometry is recalculated to force agreement. `by_cell_line` and angle-bin provenance carry selection and uncertainty context. Adapter JSON writes unknown uncertainty as `null` and rejects nonstandard NaN/Infinity.

The checked projection convention remains the deposited piecewise orthogonal silhouette, including caps beyond 90 degrees. Since the adapter passes `projected_area` through, no projection rewrite was needed. `disconnected_sites` is treated as a supplied curation flag rather than as proof of a double-structure fit.

The saved read-only compatibility audit `research/locmofit_adapter_validation.json` verifies SHA-256 of all 23 audited processed tables, compares against the preserved pre-change adapter, and reports 2,551 default sites with all legacy geometry fields exactly equal, all default uncertainties unknown, and exact restoration of legacy heuristic values on opt-in. Corrected selection retains 2,574 unflagged sites, including 23 flat corrections; removing the flag filter yields all 2,831 deposited rows. The entire corrected site set passed strict JSON encoding. The synthetic regression now includes a negative raw-curvature row omitted by default and included as a corrected-flat row without changing deposited area, projection or signed raw radius.

The lead reports the focused new and relevant existing suite as **18 passed, 4 skipped in 1.44 s**. The four integration tests skip because their expected top-level CSV cache is absent; the 23 audited files are nested under the audit cache. The fit guards and score labels were exercised with mocked samplers, so no expensive fit was run. The saved whole-table audit supplies the cohort check that those skipped tests cannot supply.

## Remaining scientific boundary

The accepted source contract supports descriptive fitted-cap output comparison only. Per-site localization point clouds, fit covariance, likelihood/nuisance results and exact historical settings are absent. A whole shallow height graph also cannot cover the 1,500 overhanging caps in the corrected/unflagged cohort. Fitted area and theta are jointly estimated, while curvature, rim and projection are derived from that same fit. A negative fixed-angle H-area slope follows cap algebra and does not test controlled mechanical area response. No current score identifies molecular mechanism, force, kinetics, stability, or a calibrated passive-profile-to-LocMoFit map.

A subsequent theory question about curvature versus balanced normal-load identifiability in the full membrane linear operator would be distinct from the completed spherical-cap two-area algebra if it specifies load families and a balancing boundary/reaction, derives an operator nullspace or rank criterion, and identifies one informative perturbation. Repeating cap compensation or area-sign calculations would duplicate `TWO_AREA_FINDINGS.md`; `FULL_SHAPE_FINDINGS.md` already states why a nonzero net load needs a finite boundary or reaction.
