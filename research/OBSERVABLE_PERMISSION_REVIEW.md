# Observable permission review — 2026-09-22

Task `observable-permission-review-001`, attempt 1. Review window:
2026-09-22T20:01:26.0581760-04:00 to 2026-09-22T20:04:16.2689575-04:00
(2m 50s observed wall time). Read-only review except for this report; no inverse,
model, or test run was performed.

## Disposition

**Accept as a limited deny-all correction, with the two repository-level gaps
below explicitly retained.** `classify_observable.py:21-34` now treats all three
legacy tags as descriptions, and `classify_observable.py:45-67` always refuses
force permission. Caller-controlled provenance, including a true
`force_inference_allowed` field, cannot override the decision. Object and dict
inputs retain their prior classification interface, while callers that relied
on tags 2/3 being approved now fail closed by design.

The tests at `tests/test_realdata.py:44-77` cover bare tags, false and true
caller assertions, object/dict forms, and the actual BioTISR trace type. The
BioTISR module's corrected claims at `ingest_biotisr_sim.py:2-31` are consistent
with its implementation: lines 91-99 measure an equivalent-disc projected
footprint, lines 140-153 record the unverified pixel-scale assumption, and
lines 162-168 emit `1/R_proj` only as a proxy. This closes the historical
tag-only behavior captured in `research/dasc_capability_audit.json`; that file
is correctly treated as a pre-fix audit, not current output.

No positive authorization path should be added until independently reviewed,
model-specific calibration evidence exists. Permanent refusal is the correct
behavior for the current evidence.

## Retained gaps

1. **The refusal is an API-local guard, not an inverse firewall.** Repository
   search found `assert_force_permitted` only in its own demonstration and
   tests (`classify_observable.py:90-94`, `tests/test_realdata.py:31-77,107-117`).
   Actual inverse entry points accept arrays without consulting it, including
   `curvo/analyze.py:154`, `curvo/mechanism.py:44`, and
   `validation/realdata/epitirf_depth_model.py:162-177`; the latter is invoked
   directly by `tests/test_realdata.py:227-241`. Thus an observable-tagged
   dataset can still be transformed and passed around the router. Do not claim
   repository-wide enforcement. If real-data execution entry points are later
   exposed, require the refusal there or label them explicitly as synthetic /
   calibration-only. A global gate on the low-level numerical inverse is not
   justified by this patch because synthetic and model-validation callers do
   not carry dataset objects.

2. **Checked-in claims and metadata still contradict the new policy.** The
   observable table and data-boundary claim in `RESEARCH.md:724-734` say tags 2
   and 3 are permitted; `outputs/data_manifest.json:229-235` marks the existing
   tag-2 data `force_inference: true`; and
   `outputs/realdata_demonstration.json:3-30` calls tag 3 the inverse's real
   input and the BioTISR dataset a force-inverse keystone despite recording an
   unverified pixel size. These are bypass-prone contract/claim artifacts even
   though the Python router now refuses. Regenerate or annotate them before
   presenting the repository as internally consistent. Historical audit files
   should remain unchanged and visibly historical.

No compatibility defect was found in the changed classifier or ingester, and
`git diff --check` reported no patch errors. The previously reported focused
result (4 passed, 15 deselected) is adequate for this small contract change and
was not rerun.
