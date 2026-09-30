# Mechanome research overview

**Status: paused at the user's request, 29 September 2026.** The recurring loop
has been deleted and no research workers remain active in this campaign. We may
return to it next week; no automatic restart is scheduled. The separate mesoscopic
work on `feature/mesoscopic-two-body` is outside this pause and checkpoint.

## What we set out to do

The question was broad: what drives clathrin pit formation, and which public
measurements can distinguish the proposed explanations? Alongside that assessment,
we tested a persistent research workflow using subscription agents and local
computation, with zero direct API spending.

We have useful descriptive results, mathematical limits and software improvements.
**We have not established a new biological mechanism.** Lower fitting error,
a successful simulation and a verified software contract are different kinds of
evidence; none alone settles the biology.

## Where the research took us

| Work | Main result | What it does not establish |
| --- | --- | --- |
| [Public static geometry](GEOMETRY_TRANSFER_FINDINGS.md) | A flexible curve performs well within cell lines, but rankings change when holding out a cell line or changing inclusion rules | Static population ordering is not a measured trajectory of one pit |
| [Mechanical identifiability](KNOWN_LOAD_RECOVERY_FINDINGS.md) | Shape-based source recovery depends on declared boundaries, mechanics and sufficiently known loading; several combinations remain indistinguishable | The assessed public tables do not provide calibrated force recovery |
| [Dynamic-data assessment](ASSESSMENT.md) | Public sources offer tracks, geometry or useful metadata, but the required pairing, calibration, event definitions or biological grouping remain incomplete for the proposed tests | Missing metadata and access failures are not negative biological results |
| [Two-channel observation](STAR_OBSERVATION_FINDINGS.md) | In an idealized model, inferred coat amount and axial position share measurement error; similar attenuation depths make the inverse unstable | Two derived traces are not automatically independent measurements |
| [Distributed fluorescence](STAR_DISTRIBUTION_FINDINGS.md) | Two positive axial distributions can have the same coat amount and both calibrated intensities, but different mean heights | A single-position estimate need not equal a distributed coat's mean height |
| [Tracking metrics](TRACKING_METRIC_FINDINGS.md) | The validator now separates the full ground-truth cohort from the detectable subset, with consistent matching and denominators | This is a scoring repair, not validation of every detector or a scission label |

The nonlinear numerical branch stopped after its bounded attempts failed the
physical-residual check. That failure is retained. The earlier synthetic dimming
run also exceeded its declared call limit; later accounting work does not erase
that overrun. Other stopped or inconclusive branches are indexed in [INDEX.md](INDEX.md).

## How the persistent job worked

```mermaid
flowchart LR
    Wake[Scheduled wake-up or user direction] --> Lead[One coordinating lead]
    State[Saved plan, task register and progress] --> Lead
    Lead --> Workers[Bounded specialist work]
    Workers --> Review[Check evidence and independent review]
    Review --> Decision[Accept, correct, stop or change direction]
    Decision --> Save[Save artifacts, limits and next decision]
    Save --> State
```

The lead read `campaign.json`, `NEXT_CYCLE.md`, the task register and recent progress
before dispatching work. Specialists handled theory, numerical checks, source
inspection and independent review. The lead changed direction after inspecting
their results. Files preserved the campaign across turns; the heartbeat only
requested another turn. Scheduled delivery did not mean uninterrupted execution.

A separate [offline controller](WORK_UNITS_FINDINGS.md) demonstrated cumulative
work limits and duplicate handling. A [local recovery exercise](WORK_UNIT_RECOVERY_REPAIR_FINDINGS.md)
completed after explicit reconciliation of an earlier process-identity failure.
Those checks do not establish live enforcement across subscription agents,
reboot recovery or exactly-once external actions.

## What is saved and how it was checked

- [Findings](FINDINGS.md) and [assessment](ASSESSMENT.md): conclusions, limits and missing evidence.
- [Study index](INDEX.md): designs, results, proofs, reviews and preserved failed attempts.
- [Pipeline architecture](PIPELINE_ARCHITECTURE.md): components, persistence and steering.
- [Reproduction guide](REPRODUCE.md): offline checks and input provenance.
- [Progress](PROGRESS.md), [task register](agent_tasks.json) and [current direction](NEXT_CYCLE.md): the handoff for resuming.

Recorded software checks include 15 targeted tracking checks and 17 controller/work-unit
checks. The two-channel observation result used six exact arithmetic cases, and
the final distribution counterexample used one fixed pair. These validate their
stated scopes. Frozen files have hash manifests; downloaded source caches remain
local, with source locations and checksums retained where recorded.

## When we return

Start with the [dated handoff](CAMPAIGN_CHECKPOINT_20260929.md). The most concrete
candidate is the newly identified public STAR Source Data workbook. Its schema
was never inspected: the first retrieval failed locally before any HTTP response.
A deliberately reopened, bounded access check can establish whether it contains
paired event traces, time/calibration fields, selection rules and cell/repeat IDs.
It would not by itself validate the axial proxy as membrane shape.

A new paired dataset or an independently measured physical endpoint could support
a different comparison. Choose that next question before restarting the loop.
Preserve the existing stopping decisions and keep mathematical, software and
biological claims separate.

This checkpoint belongs to `refactor/readable-pipelines`. It does not merge,
reset or replace the separate mesoscopic branch.
