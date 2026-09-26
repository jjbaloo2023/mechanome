# Shape2Fate validation observables: capability checkpoint

## Decision

The three `RPE1_egfpCLCa_033-annotations_{1,2,3}.csv` files are three tracking
reference sets for **one RPE-1 EGFP-CLCa movie**, not three biological replicates
or three perturbation arms.  Their audit can establish the reliability and
annotator sensitivity of a tracker-derived trajectory observable.  It cannot,
by itself, distinguish candidate cellular mechanisms: this subset has no
intervention contrast, no productivity/event label, and no calibrated time or
physical-coordinate metadata in the inspected materials.

## What is deposited and what each layer means

| Layer | What it contains | Status for mechanism discrimination |
| --- | --- | --- |
| Raw observable | A time series of EGFP-CLCa fluorescence in a TIRF-SIM acquisition (`RPE1_egfpCLCa_033.mrc`), with a reconstructed companion movie. The directly observable object is image intensity over image position and frame. | Potential upstream evidence only; raw movie was deliberately not downloaded or analysed here. |
| Derived morphology / tracks | Detection and linking produce per-detection `x`, `y`, `frame`, `cls`, then trajectories (`particle`). The example links by spatial distance plus a class-feature difference and filters tracks shorter than six frames. | Supports counts, lifetimes in **frames**, spatial paths and model-defined morphology class. It does not establish molecular state, curvature, force, or vesicle productivity. |
| Validation annotations | Three independently named annotation CSV inputs are each read as tracking ground truth, with `track_id` renamed `particle`; they are compared separately against the same predicted trajectories, then metrics are averaged. | A tracking-quality / annotation-variation benchmark for one movie. They are not independent biological observations. |
| Productive-event labels | The Zenodo README identifies separate “Exocytosis productivity annotations” only for the adipocyte-CME-coupling and RUSH-CME-local-coupling groups. | Absent from this CME tracking validation archive; do not infer event productivity from a track ending or beginning. |

The `3x tracking annotations` wording in the official dataset table, together
with the example’s loop over the three filenames, is direct evidence that the
three CSVs serve replicated tracking evaluation.  The example evaluates each
reference using MOTA/MOTP, HOTA/DetA/AssA, and mean temporal IoU, then takes
the arithmetic mean.  This establishes the intended use as agreement against
tracking references, rather than labels of morphology, perturbation, or event
fate.

## Limits on cadence and coordinates

The inspected sources provide **no frame interval** for this movie. The README
says acquisition parameters are stored in raw-file metadata, which has not
been accessed because raw movies are out of scope. Therefore frame counts must
not be translated into seconds. Likewise, the `x`, `y`, maximum-distance 7.5,
matching threshold 5, and the example crop bounds are supplied without units.
They should be reported as image-coordinate units (not asserted as nm, um, or
physical distance) until the MRC metadata provides calibration. The deposited
README documents 0.1-um beads only for **multicolour channel registration**;
that is not a pixel-scale calibration for this single-channel validation movie.

## What a CSV audit can still answer

Once the lead has safely inspected the CSV schema, compare the three annotator
sets pairwise within the same evaluation region and tolerance used by the
author example. Report agreement in detection, association, and temporal
overlap terms, plus distributions of track length (frames) and position
coverage. This can set a practical uncertainty ceiling for claims derived from
the Shape2Fate tracking pipeline: a method-to-reference score is interpretable
only alongside reference-to-reference agreement. It cannot turn a tracking
benchmark into evidence for a causal mechanism.

The one useful next comparison is therefore **predicted-versus-each-reference
alongside reference-versus-reference**, with the same coordinate window and
un-calibrated matching threshold. Stop this branch after that capability check
unless annotations reveal an explicit experiment/condition field (not assumed
here). Do not pool the three files as replicate movies.

For mechanistic discrimination, target a public dataset that supplies a
controlled perturbation or calibration and biological replication: the
deposited RUSH biotin or adipocyte insulin groups are candidates only after a
condition/member map, per-cell replicate structure, acquisition cadence, and
the productivity-label semantics have been verified. The distinct Dynamin
productivity-validation dataset is another better-targeted calibration route,
but its archive contents and label meaning remain uninspected.

## Evidence and exact locators

1. Zenodo, [record 17484958](https://doi.org/10.5281/zenodo.17484958), official
   description, **Dataset groups** table: “CME tracking validation” is RPE-1
   EGFP-CLCa, `.mrc`, “Reconstruction, 3x tracking annotations”; the same table
   identifies productivity annotations only for the two coupling datasets.
   Local verified copy: `research/metadata/dynamic-metadata-001/shape2fate_readme.md`,
   lines 41–49. The record member inventory names one raw movie, one
   reconstruction and `-annotations_1.csv` through `-annotations_3.csv`.
2. Harmanec et al., [tracking example](https://github.com/harmanea/shape2fate/blob/main/examples/tracking_example.py),
   lines 21–24 (validation ZIP and matching threshold), 69–90 (linking inputs),
   129–146 (six-frame filtering and the three annotation inputs), and 151–190
   (per-reference metrics averaged). Local text snapshot:
   `../work/dynamic-metadata-001/tracking_example.py.txt` at the same lines.
3. The linked Shape2Fate preprint DOI, [10.64898/2026.03.29.715120](https://doi.org/10.64898/2026.03.29.715120),
   was not needed for this capability conclusion and was not used to supply
   cadence, coordinate units, or label semantics.

## Limitations

No validation CSV payload, raw/reconstructed movie, archive-member CRC, or
external code was downloaded or executed in this assessment. The CSV columns,
annotation protocol, annotator independence, and any consensus process remain
unverified pending the separate schema check. The three files may be distinct
annotations, but the available material does not identify their annotators or
blinding. This note makes no claim about their agreement or the biological
validity of their tracks.
