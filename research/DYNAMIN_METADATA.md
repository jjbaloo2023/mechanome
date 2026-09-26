# Dynamin productivity: no separate event table in the archive

Task `dynamin-manifest-001`, attempt 1, completed 2026-09-22. This is a directory
access result, not a judgment about biological evidence in the movies.

The [official Shape2Fate deposit](https://zenodo.org/records/17484958) lists the
2,846,893,415-byte `Dynamin productivity validation.zip`. Read only its exact
22-byte footer and 1,751-byte central directory, with verified HTTP 206 and
Content-Range for both requests. No movie or mask body was read. The complete
single-disk directory contains 16 entries:

- One containing directory.
- Seven `.dv` acquisitions, named with IDs 194, 195, 206, 207, 208, 211 and 212.
- Seven corresponding `-mask.tif` files.
- One `registration_transform.json` (370 bytes uncompressed).

There is no separate CSV, track table or productivity annotation file in this
member inventory. The smallest compressed movie is 208,211,279 bytes. Acquisition
names do not establish seven independent biological replicates. The README
identifies the registration transform as channel alignment; its presence alone
does not establish a physical pixel scale, frame cadence or event labels.

Saved source: `metadata/dynamin-manifest-001/manifest.json`, `footer.bin` and
`directory.bin`. The manifest records exact ranges, hashes, member offsets,
sizes, methods and reported CRC fields. Those CRCs and the archive MD5 have
**not** been verified against member bodies. Operational script:
`../work/inspect_dynamin_manifest.py`, SHA-256
`0e7fcea2d1dc108055ef25b24b78e637f992c96c143d984749140ef726278af4`.

## Decision and alternative

Stop this small-table access branch. Do not download movies or execute a tracking
pipeline solely because the archive title mentions productivity. A useful
future comparison needs the authors' event definition, an observation model,
condition/replicate mapping and justified calibrated measurements.

The lead chose a bounded metadata check of the separate public DASC deposit,
already identified by the source specialist, for processed traces or explicit
experimental grouping. An independent specialist handles that check while the
lead accepts and checkpoints the annotation-contract review. If DASC is raw-only
as well, reassess the minimum analysis capability and measurement needed rather
than continuing to collect convenient archive listings.
