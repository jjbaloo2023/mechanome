# Tracking validation metric contract implementation

Task `tracking-metric-contract-001`, attempt 1.  This change repairs the
population mismatch in `validation.tracking.validate_tracking` without changing
the detector, linker, inverse code, or a frozen research result.

`metric_contract_version` is now `tracking-validation-v2`.  One deterministic
greedy matching pass is made at each frame: retained predictions are processed
in track/frame order, each takes the nearest unused GT point within and
including `match_radius_px`, and GT input order resolves an exact distance tie.
Points outside a GT event's presence interval cannot match it because that GT is
not present in the frame.

The return has two explicit blocks.

* `all_presence` counts every GT-present frame.  Its TP is every spatial and
  temporal match, FN is every unmatched GT-present frame, and FP is every
  unmatched retained prediction.  It includes `gt_presence_frames`, total GT
  events, and GT events ever matched by that same framewise rule.
* `detectable` uses the same assignments but restricts TP/FN to eligible GT
  frames.  With a supplied movie, eligibility is the observed local coat peak
  in the existing 8-pixel window meeting `coat_floor`; it is explicitly not a
  noiseless-truth threshold.  Without a movie, all present frames are eligible
  and `eligibility_source` says `all_presence_no_movie_fallback`.  A prediction
  matched to ineligible GT is reported as `ignored_ineligible_matches`, not a
  conditional FP.  An unmatched prediction remains FP in both blocks.

Explicit `precision`, `recall`, and `f1` are `null`/`None` when their own
denominator is zero.  F1 uses `2*TP / (2*TP + FP + FN)`, so it is `0.0` for an
all-missed nonempty GT cohort even though precision has no predicted-positive
denominator; it is undefined only when TP, FP, and FN are all zero.

For compatibility, the old top-level `precision`, `recall`, `f1`, `tp`, `fp`,
and `fn` now mean all-presence metrics.  A top-level rate keeps the old `0.0`
fallback when its explicit all-presence rate is undefined.  `gt_structures_detected`
and `gt_detected_frac` similarly use all-presence framewise event matches, so
completely ineligible/missing events remain in the denominator.  The
`lifetime_pairs` positional-median matching is retained only as a legacy
diagnostic and labeled as such; it is not an event-coverage denominator or a
continuous biological lifetime.

`tracking_sweep` now emits named all-presence and detectable metric fields,
including `all_presence_gt_event_detected_frac`, rather than the ambiguous
former `detected_frac` key or scalar precision/recall/F1 labels.  The hand-constructed
tests in `tests/test_tracking_validation.py` cover cohort separation, empty
denominators, event missingness, duplicate/out-of-presence predictions, and the
inclusive spatial boundary.  Per the registered execution contract, this
implementation worker did not run tests or tracking.
