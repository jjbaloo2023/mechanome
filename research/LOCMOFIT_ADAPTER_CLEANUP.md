# LocMoFit adapter cleanup and consumer boundaries

Task `locmofit-adapter-001`, attempt 1, 2026-09-26.

Missing deposited curvature uncertainty is now represented by `None` (JSON
`null`). The adapter preserves its original raw, nonnegative, unflagged default
cohort. It exposes corrected geometry only through an explicit selection and
keeps raw values alongside corrections. A small consumer inventory established
that changing this field alone would not stop the legacy likelihood paths:
shape energetics constructs its own IQR-based scale and floor, while the curve
comparison fits its own scatter. Both now require explicit exploratory opt-in.

## API and compatibility

- `ingest_locmofit(..., geometry="raw_nonnegative")` remains the cohort default.
  `geometry="corrected"` selects deposited corrected H/theta and requires valid
  corrected columns. It retains the signed raw radius, raw/corrected H/theta,
  deposited area/projection/rim, supplied exclusion flag, source key and path.
- `H_sigma_inv_nm` is optional. `legacy_curvature_sigma=True` deliberately
  restores the old numerical heuristic, labeled uncalibrated in provenance.
  Missing curation flags remain `None`; legacy filtering still keeps such rows.
- `R_nm` retains its historical magnitude convention. Its signed source value
  is available as `raw_R_nm`. Corrected H=0 does not recompute radius or area;
  the mixed selected/raw-field contract is explicit in provenance.
- `SMLMGeometrySet.to_json` writes standard JSON and rejects nonfinite sentinels.
  Existing consumers outside this repository must handle a null uncertainty;
  silently converting it into an inverse-variance weight is not supported.
- `fit_shape_energetics`, `discriminate` and `discriminate_multiobservable`
  require `allow_exploratory=True` before any fit begins. Their command-line
  entry points require `--allow-exploratory`. Caller-supplied provenance cannot
  bypass the gate. There is no calibrated path authorized by this change.

Exploratory numerical formulas remain unchanged. The curve comparison retains
its log-evidence difference and numerical preference, but `decisive` is always
false for mechanism inference; a threshold crossing is recorded only as an
exploratory diagnostic. Area/edge scores are labeled dependent geometric scores,
not independent held-out evidence. Verdict text now follows the actual numerical
preference instead of claiming a preselected winner. Legacy model and result
field names remain for compatibility; they do not validate their physical
interpretation.

Angle-binned summaries still run descriptively and carry the source selection
and uncertainty provenance. Their labels no longer claim a measured single-pit
trajectory. The inverse's coverage mapping and its arbitrary likelihood scale
are explicitly conditional surrogate assumptions. In corrected mode, its legacy
edge formula combines selected angle with deposited radius; that choice is
recorded, not passed off as a fresh deposited observable.

## Evidence and limits

The lead loaded the exact pre-change adapter from a saved snapshot and gave both
versions the same 23 checksum-verified cached tables. All 2,551 default site keys
and geometry fields match exactly; all default uncertainties are unknown. The
explicit legacy heuristic matches its old numbers exactly. Corrected/unflagged
selection retains 2,574 sites, including 23 corrected flats; including supplied
flags gives 2,831. The corrected cohort serializes as strict JSON. See
`locmofit_adapter_validation.json` and `check_locmofit_adapter.py`.

The relevant test suite passed 18 tests and skipped four data-dependent legacy
integration tests in 1.44 seconds. The audited tables are in a nested cache;
those legacy tests look for a different top-level cache and were not enabled.
No empirical nested sampling was performed. Consumer tests mock the samplers
and verify refusal before computation, false calibration despite caller-supplied
assertions, conditional results, and a large log-evidence difference that still
cannot yield a decisive mechanism verdict. After independent review requested
the negative-raw/corrected-flat fixture, its eight adapter tests passed again.
Both CLI help checks and Git whitespace checks passed.

Independent review accepts the bounded cleanup in `LOCMOFIT_ADAPTER_REVIEW.md`.
A final AST comparison confirms nine numerical helper functions match the
preserved pre-change implementations after excluding docstrings. This checks
formula preservation without rerunning any empirical sampler. Preserved
snapshots and `locmofit_adapter_design.json` document the baseline and scope.
Deposited files, historical numerical outputs, the reviewed grouped descriptive
comparison, and generic live-perception/inverse modules were not changed.

This is a code-contract correction, not a biological discovery or new validation
of the legacy likelihood. Stop this cleanup once review is accepted. Return to
a bounded theoretical discrimination question rather than expanding the adapter
or repeating the completed access and observation audits.
