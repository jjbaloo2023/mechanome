# Design note: the bitter lesson applied to curvature orchestration

*Companion to the one-week sprint plan. This note states the single
architectural commitment that shapes every module: **search against a cheap
evaluator is the engine; hand-written physics is a guardrail, not the
decision.***

---

## 1. The tension in the original plan

The sprint plan's §4 ("the representation-decision engine") is written as a
hand-authored rule table and says, explicitly, *"encode these as explicit
rules, not vibes."* That instinct is right about one thing — we do not want the
orchestrator hallucinating physics — but it is in direct tension with the
mantra the project is built on.

Sutton's *Bitter Lesson* (2019): across 70 years of AI, the approaches that
win are the ones that **scale with computation** — general-purpose **search**
and **learning** — and the approaches that plateau are the ones where humans
tried to bake in their own knowledge of how the problem "should" be solved.
Hand-engineered knowledge feels productive in the short run and caps the system
in the long run.

A fixed lookup table `{player → representation}` is exactly the baked-in
knowledge the lesson warns about. It cannot discover that, for some new protein
or state point, the "obviously right" representation is wrong. It does not get
better with more compute. It is a ceiling.

## 2. The reframing

We keep all of the physics in the plan. We change **where it sits in the
control flow.**

| | Original plan (§4) | Bitter-lesson reframing (this pipeline) |
|---|---|---|
| Who chooses the representation | a fixed rule table | a **search loop** proposing candidates |
| Role of physics rules | *the decision* | **cheap validators / priors** that prune and seed |
| What scales with compute | nothing (table is static) | the **number of proposals evaluated** |
| What is ground truth | the rule ("scaffold → anisotropic") | the **evaluator's score** against data |
| Failure mode removed | — | silently applying a wrong-but-plausible rule |

Concretely, the loop is:

```
propose  (LLM proposer, seeded by priors)
  → prune (guardrail validators reject physically-invalid proposals, cheaply)
  → resolve params (Parameter Store, or flag MD gap)
  → EVALUATE (Tier-0 analytic score vs ground truth)   ← the only source of truth
  → read + revise (LLM post-mortem → next proposal)
repeat until threshold met with robustness, or budget spent
```

Three consequences follow, and they justify design choices elsewhere in the
plan that would otherwise look like mere expedients:

### 2a. Tier-0 primacy is a bitter-lesson argument, not a fallback

The plan treats the analytic Tier-0 evaluator as a "working fallback" in case
FreeDTS eats a day. Under this reframing it is **the main event**. Search wins
only if you can afford a lot of it, and you can afford a lot of it only if each
evaluation is cheap. Closed-form Helfrich energetics and the budding phase
diagram run in **microseconds**; FreeDTS runs in minutes-to-hours. So the cheap
evaluator is what makes the engine (search) dominate. FreeDTS is an *upgrade to
evaluation fidelity*, wired behind the same interface, not the thing the demo
depends on.

### 2b. The physics rules become guardrails, and that makes them stronger

Demoting the §4 table from "decision" to "validator" does not throw the physics
away — it uses it where hand-knowledge genuinely helps a search: **pruning the
proposal space** so compute isn't wasted on nonsense. A guardrail that says
"scaffold imposes directional curvature → an isotropic-c₀ proposal for a dense
scaffold is rejected" is a cheap, correct constraint. It shrinks the search;
it does not make the final call. The same rules also act as **priors** that
seed the proposer toward good regions. This is the standard, healthy division
of labour: human knowledge constrains the *space*, search + evaluation pick the
*point*.

### 2c. Diversity of the test suite is what keeps search honest

A searcher will happily overfit one case. The plan's auto-discovered registry
(§1b) — CALM as a **transfer test**, Boucrot as an **antagonism test**,
Kaksonen as a **representation-subtlety test** — is therefore not decoration;
it is the mechanism that prevents the loop from learning "epsin-shaped" tricks.
A general method must pass observables it was not tuned on. We build the CALM
transfer test explicitly for this reason.

## 3. What "the LLM does" and does not do

The orchestrator (an LLM via `host.llm`) **proposes, configures, interprets,
and revises.** It is a search operator with good priors and a language for
post-mortems. It **never produces a curvature or an energy number** — those
come only from the evaluator. This keeps the bitter-lesson bargain intact: the
learnable/searchable part is unbounded, but truth is external and cheap to
check. A hard validator runs before every evaluation; an assertion of physics
by the LLM that contradicts a guardrail is rejected, logged, and fed back.

## 4. Honest seams (what is real vs stubbed this sprint)

The lesson also disciplines what we claim. Two pieces are out of reach this
week and are built as **clean seams with explicit labels**, never faked:

- **Proprietary averaged clathrin-track imaging data** (the CCS ground-truth
  trajectory) is not in hand. The CCS curvature target is therefore anchored to
  **published CCP geometry** (vesicle radius R ≈ 50–100 nm ⇒ mean curvature
  ~0.01–0.02 nm⁻¹ for the Ω stage) with a single-function ingestion seam
  (`ingest_clathrin_track()`) that swaps in the real trajectory unchanged.
- **FreeDTS Tier-1** is a build risk on this machine. Its config-generator and
  run-wrapper are implemented behind the evaluator interface and **stubbed**;
  Tier-0 carries the demo. Swapping Tier-1 in touches nothing upstream.

Everything else — AlphaFold pLDDT, the representation split, the parameter
adapters where the domain is reachable, the evaluator, the search loop, the
schematic — runs on **real data / real computation.**

## 5. One-line statement

> **Don't encode which representation to use. Encode how to tell a good one
> from a bad one — cheaply — and let search find it.**
