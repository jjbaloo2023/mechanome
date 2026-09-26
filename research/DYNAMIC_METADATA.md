# Public dynamic-data metadata checkpoint — 2026-09-20

Task `dynamic-metadata-001`, attempt 1. No movies downloaded or external code
executed. Evidence is in `metadata/dynamic-metadata-001/`; operational scripts
and the bounded ZIP tail are in the workspace's `work/` directory.

## Tension dataset: unresolved access

The [Mendeley record](https://data.mendeley.com/datasets/pfgfbv3rjx/1) remains
readable through the web reader but exposes no detailed condition/member map.
A direct HTTPS request returned HTTP 403; no bypass or archive download was
attempted. Intervention, cadence, reporter and replicate mapping remain unverified.
This is an access limitation, not negative scientific evidence.

## Shape2Fate: verified small access route

The [official Zenodo API](https://zenodo.org/api/records/17484958) returned 10,487
bytes of metadata. Its 3,228-byte README matches the deposit MD5. The validation
group is identified as RPE-1 EGFP-CLCa, and the deposit is CC BY 4.0. The wider
record describes stimulated experiments; that does not establish a perturbation
comparison inside this validation subset.

The validation ZIP is 776,953,308 bytes. An exact byte-range request returned 206
with the expected Content-Range. Reading the last 65,557 bytes yielded a complete
six-entry directory, including one containing directory and these members:

| Member | Compressed bytes | Uncompressed bytes |
| --- | ---: | ---: |
| Raw `RPE1_egfpCLCa_033.mrc` | 324,838,996 | 566,232,064 |
| Reconstructed `RPE1_egfpCLCa_033-recon.mrc` | 451,971,575 | 503,317,504 |
| `RPE1_egfpCLCa_033-annotations_1.csv` | 49,276 | 254,116 |
| `RPE1_egfpCLCa_033-annotations_2.csv` | 42,457 | 217,455 |
| `RPE1_egfpCLCa_033-annotations_3.csv` | 49,932 | 249,445 |

This is one named movie acquisition with three annotation files, not three
biological replicates. Archive MD5 and member payload CRCs remain unverified:
only the directory was parsed. The range snapshot has a saved SHA-256.

The [author's tracking example](https://github.com/harmanea/shape2fate/blob/main/examples/tracking_example.py)
references these annotation paths and generates `trajectories.csv` after tracking.
That filename is an output, not a deposited member of this ZIP. Code was inspected
as text only.

## Decision

Retrieve the three small annotations under bounded ranges and check member sizes,
decompression limits and CRCs. Inspect fields, frames, track IDs and coverage
before specifying disagreement metrics. Cadence remains unverified: frames are
not seconds. Coordinates are not calibrated axial curvature or force. This
enables a small tracking-data contract check, not a mechanistic comparison or
evidence that annotation sets are independent observations.
