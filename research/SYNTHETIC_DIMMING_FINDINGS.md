# Dimming can hide event loss behind a high conditional score

A controlled synthetic benchmark kept the same 45 latent events and 1,440
event-frames at three brightness levels. At gain 0.3, the existing tracker
recovered **35.0% of all event-frames and 30 of 45 events**, while coverage
restricted to noiselessly detectable frames was **93.8%**. The denominators
answer different questions: a high conditional score does not imply recovery
of the full cohort. The [independent review](SYNTHETIC_DIMMING_REVIEW.md) accepts
the saved calculation within this synthetic scope.

**Execution caveat:** the worker ran the full benchmark twice: 282 tracker-movie
runs against a 150-run cap. Only the second output and source version were
retained. The [execution audit](synthetic_dimming_execution_audit.json) records
this protocol failure and supersedes the saved single-run check's 141-run budget
claim. The result is a scoped demonstration, not a strictly compliant
preregistered execution. No further tracking was performed after reconciliation.

## What changed when brightness changed

| Signal multiplier | Events matched / fixed 45 | All-event frame coverage / fixed 1,440 | Eligible-only frame coverage |
| ---: | ---: | ---: | ---: |
| 1.0 | 45 | 1,215 / 1,440 = 84.4% | 1,209 / 1,220 = 99.1% |
| 0.6 | 45 | 1,051 / 1,440 = 73.0% | 1,042 / 1,060 = 98.3% |
| 0.3 | 30 | 504 / 1,440 = 35.0% | 497 / 530 = 93.8% |

Eligibility means noiseless center intensity at least 25 in this synthetic
setup; both its numerator and denominator use that same subset. At gain 0.3,
all 15 peak-60 events have maximum noiseless intensity below 25. They disappear
from the eligible denominator, as well as from the retained tracks. Missing
events still contribute to the fixed denominators. Their observed spans remain
null, not invented zero biological lifetimes. No retained false-positive points
or multi-fragment events occurred in this grid.

Mean observed spans among surviving events were 27.0, 23.36 and 16.8 frames.
The last mean describes 30 survivors rather than the original 45; it is not a
paired estimate of a biological lifetime change. Even the brightest condition
misses early/late latent frames. The underlying durations did not change.

## What was actually tested

The [registered design](synthetic_dimming_design.json) fixes stationary Gaussian
spots with half-sine intensity histories, durations 16/32/48 frames, peaks
60/90/120, five deterministic noise seeds and gains 1/0.6/0.3. Paired gain
conditions use identical latent geometry and Gaussian read-noise arrays. There
is no shot noise, crowding, motion, bleaching or calibrated microscope model.
The existing detector, linker and minimum-four-frame retention rule were used
unchanged. The [executed benchmark](synthetic_dimming_benchmark.py),
[frozen tracker](synthetic_dimming_tracker_frozen.py), [all saved rows](synthetic_dimming_results.json)
and [single-run controls](synthetic_dimming_checks.json) preserve the evidence.
Five no-event controls produced no detections; one noise-free high-SNR control
recovered its complete 48-frame event. The saved invocation exited successfully.

The initial post-tracking comparator only copied supports and described a
formula; it did not multiply measured values. A separate [reanalysis](synthetic_dimming_reanalysis.py)
and [numeric output](synthetic_dimming_reanalysis.json) corrected this limitation
without another tracker call. It samples noisy raw pixels at the known fixed
center on the saved gain-1 matched frames and computes
`I_post,g = 5 + g * (I_base,center - 5)` for 90 event/gain combinations. This is
a declared post-main synthetic estimator, not detector-coordinate photometry
or an intensity extractor supplied by the tracker. It preserves identities and
frame supports by construction; it cannot emulate the support changes caused
by dimming before detection. The reanalysis also independently checked all 135
saved rows, eligible sets, missing spans, aggregate counts and paired noise hashes.

## Consequence for Mechanome

Report total-cohort coverage alongside any conditional detection score. The
legacy `validate_tracking` currently matches true positives to all ground-truth
presence but counts false negatives only in its detectable subset. That mixes
two populations in one recall value. The benchmark deliberately used its own
consistent ground-truth scoring, so that issue does not explain these numbers.
A separate, bounded validator repair is the next software task.

This is an observation-pipeline demonstration, not a reanalysis of DASC or an
explanation of a published perturbation phenotype. It supplies no new clathrin
mechanism, force estimate or biological effect. The [yeast motion branch](YEAST_REFERENCE_FINDINGS.md)
remains stopped at its access/definition gap. No new source searches or movie
sweeps follow from this benchmark. [NEXT_CYCLE.md](NEXT_CYCLE.md) specifies the
minimal metric repair and its tests.
