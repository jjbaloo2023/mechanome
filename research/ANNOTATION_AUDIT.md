# Shape2Fate annotation checkpoint — updated 2026-09-22

Task `dynamic-annotations-001`, attempt 1. **Retrieval and local schema audit
completed on 2026-09-22.** Usable as a tracking-reference contract with the
limitations below; this is not a biological result. The earlier partial
retrieval checkpoint is preserved in the progress log and timing section below.

## Verified retrieval

The [official validation archive](https://zenodo.org/api/records/17484958/files/CME%20tracking%20validation.zip/content)
returned exactly bytes 776810781–776953307 of 776953308, with HTTP 206 and the
matching Content-Range: 142,527 bytes, below the 1 MiB total payload cap. This
section starts at the first annotation's local header and contains the three
annotations plus the directory; it excludes both movie bodies. The overlapping
65,557-byte tail exactly matches the previously saved directory snapshot.

For all three members, local filenames, flags, compression, sizes and CRC fields
match the central directory. Decompression was bounded by each declared output
size, required stream completion with no leftover data, and matched CRC32.
The complete archive's MD5 was not checked because the movies were not retrieved.

| Local file | Compressed bytes | Verified CSV bytes |
| --- | ---: | ---: |
| annotations_1.csv | 49,276 | 254,116 |
| annotations_2.csv | 42,457 | 217,455 |
| annotations_3.csv | 49,932 | 249,445 |

Member SHA-256 values, CRCs, offsets, URL, response range and actual request times
are saved in `metadata/dynamic-annotations-001/retrieval.json`. Payloads and the
saved section remain in `../work/dynamic-annotations-001/`. Retrieval script:
`../work/fetch_shape2fate_annotations.py`, SHA-256
`bfd67e852e89f3858c241e78804ac06d0bf0edf8f5d9d66e868e6a052d7fe76d`.
No author code was executed. All three CSV headers are `track_id,x,y,frame`.

## Completed local schema audit

`audit_annotations.py` checks a frozen SHA-256 for the retrieval record, then
the recorded hash of each CSV before parsing. `annotation_audit.json` preserves
all per-track summaries and the implementation hash. Twelve focused tests passed
for tampering, schema changes, invalid values, duplicate identities and gaps;
Ruff passed after replacing adjacent-list iteration with `itertools.pairwise`.

| Reference | Rows | Track IDs | Frame range | Median observations per track | Tracks touching first / last observed frame |
| --- | ---: | ---: | --- | ---: | --- |
| 1 | 13,451 | 479 | 0–119 | 26 | 82 / 117 |
| 2 | 11,570 | 418 | 0–119 | 25 | 76 / 79 |
| 3 | 13,285 | 480 | 0–119 | 24 | 92 / 88 |

All coordinates are finite and nonnegative, IDs/frames are nonnegative integers,
and there are no duplicate (track ID, frame) keys or internal gaps within a
track. Every frame 0–119 is represented. Reference 3 has one coordinate/frame
point assigned to two different track IDs; preserve this ambiguity rather than
silently deduplicating it. These checks establish structural usability, not
tracking correctness. Image dimensions and physical calibration are unverified.

The different counts are descriptive totals before alignment or an ROI rule,
not an agreement score or proof that one reference is better. Track identities
are local to a file. Boundary-touching tracks need censoring treatment if a
later protocol studies duration: observed track endpoints do not establish
biological initiation or scission. No frame-to-seconds conversion is justified.

The CSV schema contains no intensity, morphology, curvature, condition or
productive-event fields. Therefore close this task at the tracking contract;
defer inter-reference scoring unless a downstream question requires it.
Choose a small dynamin/productivity manifest check next to determine whether
directly usable event/calibration records exist before committing to movie work.
This has more immediate value to the campaign than generating more tracking
metrics without a discriminating biological observable.

Independent review `annotation-contract-review-001` accepted this structural
scope with no required corrections; see [ANNOTATION_REVIEW.md](ANNOTATION_REVIEW.md).
The reviewer independently checked hashes, summaries, the shared point in
reference 3, identity/censoring limits and the 12 tests. This is not independent
validation of the tracks against the movie or of any biological conclusion.

## Lead disposition of the source specialist

`shape2fate-observables-001` completed its independent source note in
[SHAPE2FATE_OBSERVABLES.md](SHAPE2FATE_OBSERVABLES.md), using the previously saved
official README and author example. Accept the distinction between tracking
references for one movie and biologically independent or perturbed observations.
The inspected documentation does not establish cadence, physical coordinate
scale or productive-event labels for this validation subset. Those are evidence
limitations, not established properties of all Shape2Fate data.

Two recommendations need qualification. Agreement between references can measure
annotation consistency under a specified matching rule; it cannot alone set a
calibrated uncertainty ceiling or establish accuracy against biological truth.
Predicted-versus-reference evaluation needs predicted trajectories, which are
not deposited in this ZIP. Generating them requires movies/model execution and
is outside the present bounded check. Do not automatically expand into that work.

## Earlier retrieval-cycle stop (2026-09-20)

First observed clock: 18:08:25 UTC. After retrieval, the clock was 21:35:27 UTC;
the request itself records 21:35:16–21:35:17 UTC. The intervening gap is unexplained
and exceeds the cycle's 20-minute target. Checkpointed without initiating schema
analysis or another investigation. Do not report this interval as active work.

The local continuation on 2026-09-22 completed the data contract above without
another retrieval or a new attempt. No mechanism comparison is yet ready.
