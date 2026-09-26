# Independent annotation-contract review

Review task `annotation-contract-review-001`, attempt 1. Verdict:
**accept within the stated structural scope**. I found no material integrity defect
or scientific overinterpretation that requires correction. This verdict permits
use as a checked tracking-table contract only; it does not validate trajectories
against the movie, quantify reference agreement, establish physical units, or
support a biological-mechanism claim.

## Contract evidence

- Input binding is adequate for this bounded audit. `audit_annotations.py:18-20`
  freezes the retrieval-record SHA-256; lines 24-28 verify bytes before use; and
  lines 150-155 require the expected three saved member names and verify each CSV
  against its recorded SHA-256. The current script, retrieval record, and three
  payloads reproduce the hashes stored in `annotation_audit.json:5-6` and
  `retrieval.json:17,30,43`.
- The parser's structural guards match the claimed contract. Exact column order is
  required at `audit_annotations.py:52-54`; IDs and frames must be ASCII
  nonnegative integers at lines 31-35 and 67-69; coordinates must be finite at
  lines 70-72; and missing or surplus row fields are rejected at lines 65-66.
  Duplicate `(track_id, frame)` rows make a table unusable at lines 102-103.
  Statistics explicitly cover structurally valid rows only
  (`audit_annotations.py:111`).
- The generated summaries agree with the report: 13,451 rows / 479 IDs, 11,570 /
  418, and 13,285 / 480, each covering observed frame indices 0 through 119 with
  no missing frame index globally, duplicate track-frame key, or within-track
  frame gap (`ANNOTATION_AUDIT.md:43-51`). These are counts before any matching
  rule. The report correctly says they are neither agreement scores nor evidence
  that one reference is better (`ANNOTATION_AUDIT.md:56-58`).
- `x` and `y` are handled only as finite numeric coordinates. The output labels
  position as image coordinates with unverified physical scale
  (`annotation_audit.json:10-13`), and the report also leaves image dimensions
  unverified (`ANNOTATION_AUDIT.md:49-54`). Frame values are indices only; the
  report correctly rejects a frame-to-seconds conversion
  (`ANNOTATION_AUDIT.md:58-60`).
- Identity scope is explicit and correct: `track_id` is local to each annotation
  file (`annotation_audit.json:14`; `ANNOTATION_AUDIT.md:56-58`). The three source
  member names all contain `RPE1_egfpCLCa_033` (`retrieval.json:9,22,35`), so these
  are three references for one movie rather than independent movies or biological
  replicates, as stated in `annotation_audit.json:15-20`.
- Reference 3 contains exactly one shared coordinate/frame point: frame 50,
  `(x, y) = (510.0, 636.0)`, assigned to local track IDs 247 and 277. The audit
  counts it without deleting either row (`audit_annotations.py:59,81,117-119`),
  and the report preserves it as an ambiguity rather than treating it as an
  agreement result (`ANNOTATION_AUDIT.md:51-54`). Each track-frame key remains
  unique, so this does not contradict the structural contract.
- Boundary handling is appropriately cautious. The audit reports tracks touching
  the first and last *observed* frame (`audit_annotations.py:135-140`), and the
  report says such tracks need censoring treatment for any later duration study;
  observed endpoints are not initiation or scission events
  (`ANNOTATION_AUDIT.md:58-60`). This wording does not promote endpoint-touching
  counts into complete lifetimes.

## Independent checks and limits

The focused test file passes all 12 collected cases, and Ruff passes for the audit
script and test file. The tests exercise checksum rejection, schema changes,
missing/surplus fields, nonfinite coordinates, noninteger or negative IDs/frames,
duplicate track-frame keys, unordered rows, gaps, and empty tables
(`tests/test_annotation_audit.py:17-70`). Pytest emitted only a cache-write warning;
it did not affect test execution.

The full ZIP checksum was not verified because the movie bodies were not
retrieved, a limitation already disclosed at `ANNOTATION_AUDIT.md:17-20` and
`retrieval.json:52`. The audit also cannot establish coordinate origin, image
bounds, physical distance, frame cadence, annotator accuracy, correspondence of
tracks across files, or whether any observed endpoint has event meaning. Any
future agreement analysis would require a declared spatial-temporal matching rule
and would measure consistency under that rule, not biological truth or a
calibrated uncertainty bound. No broader scientific inference is accepted here.
