# Passive-area execution audit

This note audits only the saved attempt-1 files. It does not rerun the BVP,
alter a state, or interpret the area-sign result; the lead performs the
independent state reconstruction and quadrature checks.

The result contains 12 base records and one sensitivity record. Every base
record has solver status success and all frozen record gates true. The maximum
native rho RMS is `9.998e-9` against the `1.01e-8` limit, maximum outer BC
error is `6.28e-30`, maximum normalized axial-force residual is `5.41e-11`,
maximum angle is `0.26785` rad, and the minimum radius away from the cutoff is
`0.00946`.

For each material-label sequence, the first amplitude has no seed; every later
amplitude references the immediately preceding state path and its recorded
SHA-256 matches that NPZ file. Accepted state files contain `rho`, six-by-mesh
`y`, and pole parameters `p`. The current source, design, both exact frozen
copies, and frozen rho dependency all match the hashes stored in the result.

The sensitivity selected `x2_c0.6`, the accepted base case with largest
recorded angle. It jointly changes initial nodes from 801 to 1601 and cutoff
from `1e-6` to `2.5e-7`; it therefore does not attribute the response to either
change alone. Its largest normalized-observable difference is `8.25e-9`, below
the registered `2e-6` gate.

The frozen runner uses `subprocess.run(timeout=45)` and records a timeout as a
case result. During the elapsed-time overrun, interrupting the parent did not
prevent already-created children from completing; this audit does not claim
retrospective timing compliance. The frozen record also lacks an explicit pole
BC gate and adjacent-state jump gate, and state files are overwriteable. Those
are preserved limitations for a new version, not silent repairs to this one.
