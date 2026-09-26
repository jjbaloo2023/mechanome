# Clathrin research checkpoint

**Reviewed through 26 September 2026.** The campaign has a descriptive result
from public cap-fit tables, conditional mechanics results, and a reviewed
software boundary for exploratory fits. It does not yet identify a biological
mechanism or calibrate force from those tables.

## Read in this order

1. [Findings](FINDINGS.md): what the evidence supports, what failed, and what is still missing.
2. [Study index](INDEX.md): grouped links to each design, implementation, result, figure and review.
3. [Reproduce and verify](REPRODUCE.md): offline checks, external inputs, and frozen-run conventions.
4. [Assessment](ASSESSMENT.md): the detailed theory/data decision and remaining gaps.
5. [Next decision](NEXT_CYCLE.md): the queued full-membrane curvature-versus-load question; no result yet.

The latest completed implementation is the [LocMoFit adapter and consumer
cleanup](LOCMOFIT_ADAPTER_CLEANUP.md). Missing uncertainty is explicit, raw and
corrected cohorts are distinct, and the two legacy static fitting consumers
require exploratory opt-in. These changes do not validate earlier biological
interpretations or the generic inverse pipeline.

## Where things live

| Location | Purpose |
| --- | --- |
| This directory's study notes, scripts, JSONs, figures and synthetic states | Reviewed scientific evidence and retained attempts; navigate through the study index |
| `*_frozen_*`, `*_before_*`, numbered result/record directories | Historical source, designs and outputs; a stored file is not automatically an accepted result |
| `metadata/` | Source inventories, access records, locators and checksums; downloaded payloads stay outside Git |
| [PROGRESS.md](PROGRESS.md), [agent_tasks.json](agent_tasks.json) | Dated activity, result dispositions, corrections and execution limitations |
| [campaign.json](campaign.json), [NEXT_CYCLE.md](NEXT_CYCLE.md), [AGENT_LOOP.md](AGENT_LOOP.md) | Current direction and subscription-driven operating protocol |
| [mechanome/research](../mechanome/research/) | Separate offline SQLite controller and restart demo |
| [validation/realdata](../validation/realdata/), [tests](../tests/) | Dataset adapters, exploratory consumers and regression checks |

Original evidence paths remain stable because code, manifests and reviews refer
to them. Rejected attempts are retained and labeled in the index; generated
caches and downloaded payload copies are ignored. Git preserves the exact bytes
of the research archive and the adapter files covered by its hash manifest.

## Operation and its limits

The active research workflow uses a coordinating Codex task and bounded
subscription subagents. Heartbeats request another cycle; they do not establish
continuous execution. The progress log distinguishes observed work, scheduling
gaps, stopped runs and queued decisions. Direct API spending remains zero.

The Python controller is an **offline persistence demonstration**. Its flow is
`acquire_lead -> decide -> start -> finish`; it records attempts, reservations,
fenced ownership and hashed artifacts. Unknown execution blocks replacement,
and valid negative outcomes are retained. It does not launch the subscription
agents, choose research questions, enforce provider budgets or run a service.
`quality="valid"` is a trusted caller assertion. SQLite and its artifact directory
must be backed up together. See the reproduction guide for its two-process demo.

The older [scientific reference](../RESEARCH.md) and [manuscript](../MANUSCRIPT.md)
contain historical demonstrations. Use this checkpoint's findings and reviews
for the current public-data claim boundary.
