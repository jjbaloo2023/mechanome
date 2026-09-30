# Manenschijn et al. 2019 Figure 6 — aggregate contract

**Scope.** This is a genotype-level observation contract for eLife e44215
(2019), Figure 6. It does not establish same-event covariance, force, scission,
or a mammalian mechanism.

## Publisher artifacts

| Figure result | File | Bytes | SHA-256 |
| --- | --- | ---: | --- |
| 6B average Sla1 trajectories | `elife-44215-fig6-data1-v1.csv` ([DOI .019](https://doi.org/10.7554/eLife.44215.019)) | 39,769 | `bc92afb9ede060f63b794823f79ec153840ea4204fc394614ffbc174f70866fa` |
| 6A median Act1 molecules | `elife-44215-fig6-data2-v1.csv` ([DOI .020](https://doi.org/10.7554/eLife.44215.020)) | 210 | `bf468206a22020e839eae9ce6bc9a2a179fa1c3dab5f35b287d0bda9c4ba38d0` |

Both direct publisher responses were HTTP 200 and `text/csv`. The
[request ledger](metadata/yeast-figure6-001/REQUEST_LEDGER.md) records URLs,
statuses, times, hashes, parsed-tool access, and the 39,979-byte body total.

## Schema and figure meaning

Figure 6A has `Protein`, `genotype`, `median nr of molecules`, and `SEM`;
every row is Act1 and genotypes are WT, `myo5del`, `bbc1del`, and
`bbc1delmyo5del`. The indexed primary caption identifies median Act1 with SEM
and two-sided z-tests. This file contains four aggregate values and SEMs, not
event/cell/experiment identifiers, sample counts, or biological replicate units.

Figure 6B has four blocks: `Sla1_WT`, `Sla1_myo5del`, `Sla1_bbc1del`, and
`Sla1_myo5delbbc1del`; each has `t (s)`, `x (nm)`, `n`, and `x_err (nm)`.
The indexed primary caption calls the Figure 6B panel Sla1 centroid movement
during the inward phase and identifies shaded 95% confidence intervals. The
CSV, however, includes negative times (for example, WT begins at -18.063 s),
so the full file cannot be labeled solely inward phase until its time-zero,
alignment, and plotted-subset definitions are verified. `x` is a
centroid-position trajectory, not fitted speed, scission time, or force;
`x_err` is the plotted error field associated with that captioned 95% CI, but
the CSV does not itself equate it to a CI half-width or define its exact
construction/biological unit. Article methods state that inward-movement plot
shading uses trajectory/alignment error terms to form 95% CIs. The CSV does not
define time-zero/alignment or the averaging rule. Time spans differ by genotype
and `n` varies by time point, with no zero entries in the 1,106 numeric rows.
The minimum is 3. The bbc1del time range is entirely positive
(15.4215 to 48.5415 s); direct same-time comparison with the other blocks is
not justified without the alignment definition. `n` is not an independently
verified biological-replicate count, and time rows are not independent.

The double-mutant labels differ in order across files:
`Sla1_myo5delbbc1del` in the trajectory CSV versus `bbc1delmyo5del` in the
Act1 CSV. They should be mapped by the shared two-gene deletion set, never row
order. The two tables still do not verify matched strain ancestry/cell samples
across readouts.

## Control ancestry and permitted estimand

The indexed Figure 6 caption says WT and `myo5del` Act1 values are reused from
Figure 1, while WT and `myo5del` Sla1 trajectories are reused from Figure 2.
They are shared controls, not independent validation or fresh replication. The
two tables do not establish common cells or events.

The permissible summary is descriptive: compare reported median Act1 abundance
and the stored average Sla1 centroid curves across the four
genotypes, retaining the published shared-control ancestry and figure-level
uncertainty conventions. A separate registered calculation must define a
trajectory functional, establish its positional reference and accommodate that
reuse; the full stored curve is not a verified inward-phase subset. No numerical contrast is made
here.

## Remaining limit

The two files omit cell/event observations, selection/censoring, biological
replicate IDs, time-alignment definition, and raw Act1 distributions. They can
support only the declared aggregate genotype summary, never within-event
actin/motion coupling or force inference. Acquisition closes at these two files.

Lead correction after source completion: removed the false zero-n statement
and narrowed the full-file inward-phase wording, following independent CSV
checks and review. No new source acquisition.
