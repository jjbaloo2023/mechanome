# Clathrin research campaign

**Current status: paused by the user, 29 September 2026.** Start with the
[overview](OVERVIEW.md) for the research story, workflow and restart steps.
The recurring loop is deleted; no automatic restart is scheduled. The separate
mesoscopic branch is outside this campaign pause.

**Reviewed checkpoint: 29 September 2026.** We have descriptive results from
public geometry tables, conditional mechanics results, and tested observation
software. We have not selected a biological mechanism or recovered forces from
these public data. The latest geometry comparison shows that the preferred
curve changes with the held-out cell line and inclusion policy.

The latest operational milestone is an [offline cumulative work-unit guard](WORK_UNITS_FINDINGS.md):
17 tests passed, with independent review. It retains limits across retries and
database reopens, rejects duplicates and blocks unresolved replacement. It is
not yet wired into live agent work.

The [separate-process follow-up](WORK_UNIT_RECOVERY_FINDINGS.md) stopped at a
process-ID mismatch. A [direct-interpreter probe](PROCESS_IDENTITY_FINDINGS.md)
and [reviewed local reconciliation](WORK_UNIT_RECOVERY_REPAIR_FINDINGS.md) enabled
the two remaining phases to finish without resetting the budget. The original
failure remains preserved; this does not establish live-agent or reboot recovery.

The newest [observation result](STAR_OBSERVATION_FINDINGS.md) shows, under a
stated two-channel model, that inferred coat amount and axial position have
shared measurement error and become unstable as attenuation coefficients
converge. Six exact arithmetic cases and independent review passed. A new
[public workbook listing](PAIRED_SHAPE_PUBLIC_FINDINGS.md) was found, but its
schema remains unverified after a local network-permission failure.

## Start here

1. [Findings](FINDINGS.md): the evidence, its limits, and what would change the conclusion.
2. [Assessment](ASSESSMENT.md): competing explanations, data requirements and branch decisions.
3. [Pipeline architecture](PIPELINE_ARCHITECTURE.md): how one lead and bounded specialists resume, review and steer the work.
4. [Study index](INDEX.md): original designs, code, results, figures, reviews and failed attempts.
5. [Reproduce and verify](REPRODUCE.md): input provenance, checks and protected historical outputs.
6. [Next decision](NEXT_CYCLE.md): the current executable direction and stopping rules.

## What belongs where

| Records | Purpose |
| --- | --- |
| Study notes, scripts, results and figures linked from the index | Evidence, assumptions, interpretation and independent challenge |
| Designs and hash manifests | Registered limits and exact artifact identity |
| [Progress](PROGRESS.md) and [task register](agent_tasks.json) | Actual observed activity, ownership, corrections and dispositions |
| [Campaign](campaign.json), next decision and [agent protocol](AGENT_LOOP.md) | Current direction and operating limits |
| `metadata/` | Public locators, access records and checksums; downloaded caches are excluded from Git |
| [Offline controller](../mechanome/research/) | Separate SQLite persistence/restart demonstration |

Original study paths remain stable. Rejected and inconclusive attempts stay
available with their dispositions; they are not silently replaced by successful
runs. The earlier navigation pages are preserved in the [synthesis snapshot](campaign_navigation_before_001.zip).

The campaign used subscription tools and local computation with zero direct
API spending. A 30-minute heartbeat requested bounded cycles before retirement. Scheduled
delivery, active work, queued work and a dated checkpoint are different states;
saved files do not demonstrate uninterrupted execution or a remote backup.

Older [research notes](../RESEARCH.md) and the [manuscript](../MANUSCRIPT.md)
contain historical demonstrations. Use the reviewed findings for current claim
boundaries. Publishing and Git pushes are outside this heartbeat's authorization.
