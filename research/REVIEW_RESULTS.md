# Autonomous checkpoint: geometry self-audit

Disposition: retain the exploratory predictive result; do not promote it to a
single-pit dynamic or molecular-mechanism claim. Independent review is pending.

## What ran

Following the written `REVIEW_PROTOCOL.md`, local code ran a synthetic adversarial
control and six real-data sensitivity scenarios. No API, remote agent, or external
communication was used. The existing comparison, data hashes and original outputs
were preserved. Full new outputs are in `geometry_review.json`.

The constructed control has 105 pits in three groups, each with strictly constant
curvature throughout its synthetic trajectory. Snapshot phase is deliberately
correlated with pit curvature. Applied to these snapshots, the flexible reference
has approximately zero held-out MAE; constant curvature has MAE 0.001457 inverse
nm and constant area 0.001101 inverse nm. This is a counterexample to interpreting
the snapshot ranking as evidence of curvature changing within each pit. It does
not establish that experimental sampling follows the constructed pattern.

On the real primary population, uniform radius offsets of -10, 0 and +10 nm were
crossed with full-angle and 20–160 degree analyses. In all six scenarios and all
three cell lines, the average error ordering remained flexible reference, constant
area, constant curvature. This demonstrates robustness only to these particular
assumptions. They are neither independent datasets nor calibrated error draws.

## Measurement evidence

[Mund supplementary Fig. S2](https://research-explorer.ista.ac.at/download/14788/14811/2023_JCB_Mund.pdf)
describes angle-estimation performance in simulations, with greater spread near
the flat and near-closed limits. Fig. S5 examines labeling-related radius shifts.
These checks motivate our scenarios but do not supply joint, per-site experimental
angle/curvature covariance. The repo's localization-precision heuristic remains
insufficient for a calibrated measurement likelihood.

## Review checks

| Check | Outcome | Evidence / reason |
| --- | --- | --- |
| Input integrity | Pass | Cached tables verified against retained SHA-256 before execution |
| Training/held-out separation | Pass within implemented grouping | Automated target-perturbation test; stored fold group lists |
| Numerical/unit behavior | Pass for tested cases | Synthetic recovery, radius-transform and boundary tests |
| Population ranking implies pit dynamics | Fail | Constructed constant-curvature trajectories reproduce flexible preference |
| Robustness to tested radius shifts/endpoints | Pass within scope | All six scenarios retain average ordering |
| Calibrated observation uncertainty | Unresolved | No verified joint covariance or full measurement simulation calibration |
| Biological independence of groups | Unresolved | File/cell grouping is retained; culture-level replication not established |
| Independent review | Unresolved | This is the implementing assistant's self-audit |
| Molecular-mechanism discrimination | Unresolved | No direct mechanism-specific observable or perturbation evaluated |

## Next justified work

Stop escalating this dataset's descriptive ranking into mechanism claims. Broaden
the public-data search toward within-pit trajectories and perturbations that can
distinguish explanations. Audit the available localization simulations for a
joint observation model before assigning calibrated uncertainties. An independently
briefed reviewer must assess both the comparison and the population confound.

The controller remains a local foundation; this checkpoint is task-level autonomy
inside Codex, not a deployed continuous multi-agent research service. Persistent
files allow a later attempt to resume from the recorded decision.
