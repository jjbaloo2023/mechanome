# mechanome — Design Note

This note describes **what mechanome is**, **why it is built the way it is**, and
**the stages through which it was developed**. It is the architectural companion
to the README: the README documents how to run each component and reports
results; this note explains the reasoning behind the structure.

`mechanome` is the umbrella project; its core is **curvo**, the membrane-scale
inverse engine. Sections 1–2 describe curvo's two-directional design, which the
whole project inherits; Stage 6 onward (§3) describes the multi-scale forward
models and the structural screen that extend curvo into a mechanome.

---

## 1. What we are building

curvo (the membrane-scale core of mechanome) is a membrane-curvature reasoning
system with two coupled directions and a schema layer that regulates what it is
allowed to claim.

**Forward direction — orchestration (`analyze` inputs: protein + target).**
Given a protein (UniProt ID) and a target membrane curvature, curvo decides
which physical representation each molecular player should take (a rigid wedge,
a polymer-brush crowder, a rigid coat, a tension term), resolves the parameters
of those representations from pre-existing data, scores the combination against
closed-form membrane energetics, and revises until it meets the target. The
output is a set of representation decisions with physical justifications and an
achieved-versus-target curvature.

**Inverse direction — mechanistic inference (`analyze(video, question)`).**
The same biophysical forward model is run backwards. A microscopy movie and a
mechanistic question go in; inferred forces, the favored mechanism, calibrated
uncertainty, an identifiability report, and a suggested disambiguating experiment
come out. The inverse is a Bayesian engine (nested sampling with an MCMC
cross-check) that **declines to report a force it cannot identify**, returning a
posterior marked underdetermined instead of a confident but unsupported number.

**Schema layer — the mechanome.** Every quantitative claim curvo emits is tagged
with an epistemic tier (GROUNDED, MEASURED, or LINKED) that records how much
evidence stands behind it. A structural firewall prevents a correlative
hypothesis from being represented as a measured force.

The scientific motivation is specific: a model that reasons about protein
orchestration is more useful when it recovers the **physics** — forces,
energies, identifiability — than when it produces qualitative narrative alone.
Recovered physical constraints are testable and transferable; narrative is not.

## 2. Why it is built this way

### 2.1 The architectural commitment: search against a cheap evaluator

The project's organizing principle is Sutton's *Bitter Lesson* (2019): across
the history of AI, methods that scale with computation — general-purpose search
and learning — outperform methods that encode human knowledge about how a
problem "should" be solved. Hand-engineered decision rules are productive early
and become a ceiling later.

An early design for the representation-decision step was a fixed lookup table
mapping each player to a representation. That table is exactly the baked-in
knowledge the lesson warns against: it cannot discover that the expected
representation is wrong for a new protein or state point, and it does not improve
with more compute. curvo inverts it.

| | Fixed-rule design | curvo (search-based) |
|---|---|---|
| Who chooses the representation | a static rule table | a search loop proposing candidates |
| Role of physics rules | the decision itself | cheap validators and priors that prune and seed |
| What scales with compute | nothing | the number of proposals evaluated |
| Source of truth | the rule | the evaluator's score against data |

The control flow that follows:

```
propose         (LLM proposer, seeded by physics priors)
  → prune       (guardrail validators reject physically invalid proposals)
  → resolve     (Parameter Store supplies values, or a gap is flagged for MD)
  → EVALUATE    (closed-form analytic score vs ground truth)  ← only source of truth
  → revise      (LLM reads the score and proposes the next candidate)
repeat until the target is met robustly, or the budget is spent
```

### 2.2 Three consequences of the commitment

**A cheap evaluator is the engine, not a fallback.** Search dominates only if
each evaluation is inexpensive. Closed-form Helfrich energetics evaluate in
microseconds; a full mesoscale simulation (FreeDTS) takes minutes to hours. The
analytic evaluator is therefore the main component, and higher-fidelity
simulation is an upgrade to evaluation quality wired behind the same interface —
not a dependency of the demonstration.

**Physics rules become guardrails, which strengthens them.** Demoting the rule
table from decision-maker to validator does not discard the physics; it applies
it where human knowledge genuinely helps a search — pruning the proposal space
so compute is not spent on physically impossible candidates (for example,
rejecting an isotropic spontaneous-curvature proposal for a dense directional
scaffold). The same rules seed the proposer as priors. Human knowledge
constrains the space; search and evaluation select the point.

**Test diversity keeps search honest.** A search procedure will overfit a single
case. curvo is validated on observables it was not tuned on — the CALM transfer
test (a different adaptor protein), the ENTH-versus-ANTH family screen, and the
real force-paired STED tether data — so that passing requires generalization, not
memorization of one protein's behavior.

### 2.3 Division of labour between LLM and solver

The LLM orchestrator proposes representations, configures parameters, interprets
results, and revises. It performs the discrete and structural reasoning (which
representation, whether two players are coupled, why) and the natural-language
post-mortem. It never produces a curvature or an energy value — those come only
from the deterministic evaluator, which optimizes continuous magnitudes. LLMs are
poor numeric optimizers; a bounded solver is exact and cheap. Each component does
what it is suited to, and a hard validator runs before every evaluation so that
an LLM assertion contradicting the physics is rejected and fed back.

### 2.4 The credibility firewall

The inverse engine and the mechanome share one discipline: a claim may carry a
physical value only when the data identify it. In the inverse, this is the
anti-force-astrology guardrail — a force is reported as a number only if it is
not degenerate with another actor and not railed against a prior bound. In the
mechanome, it is the tier firewall — a GROUNDED claim (a forward-model inverse
against data) carries value, uncertainty, and identifiability; a LINKED claim (a
mechanotransduction hypothesis) carries a causal chain and a proposed experiment
but **no value**. The boundary between them prevents correlation from being
represented as force balance.

## 3. Development stages

curvo was built in stages, each of which established a capability the next
depended on.

**Stage 1 — Forward orchestration (v0.1).** The propose–prune–resolve–evaluate–
revise loop, the closed-form evaluator (validated against analytic budding
boundaries to within 0.05%), the AlphaFold-driven representation split, and the
parameter store. Demonstrated on the epsin clathrin-coated-structure case and
generalized without retuning to the CALM adaptor and a six-protein
ENTH-versus-ANTH family screen.

**Stage 2 — Inverse engine (v0.2).** The forward model extended with an
active-stress (cortical/actin) term, a synthetic movie generator, a perception
front end (pixels to geometry), the Bayesian inverse (nested sampling plus MCMC),
mechanism discrimination by Bayesian evidence, and the `analyze(video, question)`
endpoint with its identifiability guardrails.

**Stage 3 — Credibility gate.** A synthetic recovery-validation grid that sweeps
known forces through the entire pipeline and checks recovered posteriors against
truth. No force claim is reported without passing this gate. It established that
cortical force is calibrated (68% CI coverage 0.96, +2.0% bias) only where the
actin channel constrains it, and that spontaneous curvature and tension are
unidentifiable from single-structure geometry alone.

**Stage 4 — Real-data and image validation.** The inverse tested against real
force-paired STED nanotube measurements (mean |bias| 3.8%), a perception
operating-envelope benchmark on rendered images (mean curvature recovered to
10–22%), an end-to-end pixels-to-force test, and an honest transfer probe on a
real cryo-ET membrane image (which established the modality gap and the adapter
that closes its measurable axes).

**Stage 5 — Orchestration-recovery program.** Scaling from one structure to a
field: a multi-structure synthetic time-lapse, a detection-and-tracking pipeline,
a motion-field (PIV-analog) extraction that demonstrates empirically that velocity
is not force, per-structure physics recovery across the crowded field, and a
coordination model that produces a falsifiable, experimentally testable statement
about the temporal ordering of curvature and active force.

**Stage 6 — The mechanome (multi-scale forward models).** curvo's membrane module
is one edge of a mechanical map that spans molecule to tissue. Four further scales
— tissue (vertex junction-tension force balance), cortex (Young–Laplace surface
tension), molecular adhesion (Bell / two-pathway catch–slip bonds), and
mechanosensitive channels (two-state Boltzmann gating) — ship as executable,
closed-form forward models. The *why*: a mechanome that an agent can query across
scales needs each edge to be an executable physics kernel, not a description, and
each edge must wear its evidential status honestly. These four are validated to a
deliberately weaker bar than the membrane module — a `built_analytic` tier that
requires recovering a known analytic limit and reproducing a canonical published
anchor's parameters, but explicitly *not* pairing against a raw dataset acquired
here. The registry records the tier (`can_emit_grounded` vs `can_emit_analytic`,
`validation_provenance`), and every claim these modules emit carries
`validation=analytic_limit` on its face. The channel module reads curvo's inferred
membrane tension directly — the one cross-scale link grounded on both ends.

**Stage 6b — The structural screen (molecule / structure entry point).** A
separate physics-first project (*mechanistic-entry-model*) ranks membrane
proteins by structure-derived curvature-generating capacity, computed against the
same Helfrich energy scale. It was vendored into `mechanome/structural_screen/`
because it shares mechanome's DNA — the same κ, the same signed-curvature engine,
and it screens the exact mechanosensitive channels the channel module anchors on.
The *why*: it gives the mechanome a molecule-scale entry point that takes
experimental structures in and emits, for each channel, a structure-derived
spontaneous curvature c₀ that feeds the gating model — closing one edge on both
ends. Its integrity discipline matches the rest of the project: the scored
ranking is frozen with a SHA-256 hash and a pre-registration whose label set was
fixed before scoring, both preserved and re-verified through the move. It is
registered as `structural_screen_v1` at the `built_analytic` tier (validated on
home turf — BAR radii reproduce literature — and by the pre-registered enrichment
test, but not paired against a raw dynamic dataset).

**Stage 7 — RL scaffold (a byproduct, not the aim).** The forward model exposes a
sequential decision problem, so it wraps cleanly as a Gymnasium environment
(`CCPBuddingEnv`) in which an agent orchestrates a budding attempt by recruiting
players and ramping actin. This is a scaling scaffold, explicitly *not* a
scientific claim: the physics lives entirely in curvo's forward model. Its value
is as evidence that the env is well-posed — a physics-blind Q-learning agent
learns to reach the Ω (scission) stage and, in doing so, recovers the same
physical priority curvo established from the PICALM/epsin data (build curvature
drive first, then ramp force). An agent searching the env rediscovers the
orchestration curvo inferred, which is the bitter-lesson thesis in miniature.

## 4. Implemented vs. stubbed components

The same discipline governs what curvo claims to have built. Components out of
reach on the current host are implemented as labelled seams rather than
simulated results:

- **Averaged clathrin-track imaging data** (a measured CCS curvature trajectory)
  is not in hand. The CCS target is anchored to published CCP geometry, and
  `ingest_clathrin_track()` is the single-function seam that swaps in a real
  trajectory without changing the loop.
- **FreeDTS Tier-1** mesoscale simulation is implemented as a config-generator and
  run-wrapper behind the evaluator interface and stubbed; the analytic Tier-0
  evaluator carries the demonstration. Swapping Tier-1 in touches nothing
  upstream.
- **Simulation-based inference** (`fit_sbi`) is a documented seam. The cheap
  forward model makes exact nested-sampling inference tractable, so exact
  inference is primary and amortized inference is optional.

Every other component — AlphaFold retrieval, the representation split, the
reachable parameter adapters, the evaluator, the search loop, the inverse engine,
and the validation suite — runs on real data and real computation.

## 5. One-line statement

> Do not encode which representation to use. Encode how to tell a good one from a
> bad one, cheaply, and let search find it — then recover the physics, and report
> only what the data identify.
