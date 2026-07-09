# curvo — a bitter-lesson curvature-orchestration pipeline

A closed loop that, given a UniProt ID and a target membrane curvature, decides
**which physical representation to use for each player**, resolves parameters
from pre-existing data, evaluates against ground truth, and revises — until it
finds an orchestration that meets the target. Demonstrated end-to-end on the
epsin clathrin-coated-structure (CCS) case.

```bash
git clone https://github.com/jjbaloo2023/curvo.git
cd curvo
pip install -e .              # numpy, scipy, requests
pip install -e ".[plots]"     # + matplotlib for the figure scripts
python run_demo.py            # offline, deterministic — no network/LLM needed
python run_demo.py --llm      # use the host.llm proposer for the search
```

One command prints the representation decisions + physical justifications
(including the AlphaFold pLDDT → wedge/crowding split), achieved-vs-target
curvature, the recovered ENTH+IDP complementarity, the spherical/filamentous
IAV divergence, and the stubbed MD-job queue it would dispatch — and writes the
headline SVG orchestration schematic.

Run the guardrail tests with `python tests/test_players.py` (or `pytest`).

### The headline artifact

The loop's decision is rendered as a single schematic, generated directly from
the `OrchestrationRecord` (not hand-drawn): membrane profile bent by the
achieved order parameter, player glyphs sized by their gated contribution, a
faithful contribution waterfall (wedge + crowding + coat + synergy = c_eff),
and target-vs-achieved with a pass/fail verdict.

![epsin orchestration schematic](outputs/epsin_orchestration_schematic.svg)

### What the loop recovers

| Test | Figure |
|------|--------|
| AlphaFold pLDDT → representation split (EPN1) | `outputs/epsin_pLDDT_profile.png` |
| ENTH+IDP complementarity (only FULL crosses Ω) | `outputs/epsin_complementarity.png` |
| IAV cargo divergence (spherical needs H0, filamentous does not) | `outputs/iav_cargo_divergence.png` |
| Closed-form budding anchor a\*=4κ/λ (loop vs analytic) | `outputs/anchor_convergence.png` |
| Helfrich tube radius / pulling force | `outputs/tube_radius_vs_force.png` |
| Budding phase diagram | `outputs/budding_phase_diagram.png` |
| Parameter-store coverage (live / cached / stub) | `outputs/param_coverage.png` |

---

## The one idea (design_note.md)

The project mantra is **the bitter lesson** (Sutton 2019): what scales with
compute is *search* and *learning*, not baked-in human knowledge. The sprint
plan's §4 wrote the representation choice as a fixed rule table. We inverted
that:

> **Don't encode which representation to use. Encode how to tell a good one
> from a bad one — cheaply — and let search find it.**

- **Search is the engine.** The LLM orchestrator *proposes* a representation +
  parameters for each player; a cheap analytic evaluator scores it against
  ground truth; the loop searches.
- **Physics rules are guardrails, not deciders.** The §4 table lives in
  `players.py` as cheap *validators* that prune physically-impossible proposals
  (scaffold→anisotropic, crowding-as-fixed-c₀, helix double-counting) and as
  *priors* that seed the proposer. They shrink the search space; they don't make
  the call.
- **Cheap evaluation is why search wins.** Closed-form Helfrich energetics run
  in microseconds, so the loop can afford many iterations. This is the
  bitter-lesson argument *for* Tier-0 primacy — not a fallback.
- **Division of labour.** The LLM does the discrete/structural reasoning (which
  representation, is it coupled, why) and the natural-language post-mortem; a
  bounded deterministic solver nails the continuous magnitude. LLMs are poor
  numeric hill-climbers; this keeps each doing what it is good at.

## What is REAL vs STUBBED this sprint

| Component | Status | Notes |
|-----------|--------|-------|
| AlphaFold pLDDT → representation split | **REAL** | live AlphaFold DB API; EPN1 Q9Y6I3, PICALM Q13492; per-residue pLDDT parsed from the model |
| Disorder cross-check (conditional-folding guardrail) | **REAL** | TOP-IDP composition scale (independent of pLDDT) + Eisenberg hydrophobic moment for the amphipathy test |
| NMRlipids/FAIRMD lipid params | **REAL (live)** | area-per-lipid + thickness pulled from the GitHub-hosted databank |
| Curated literature params (c₀, κ, λ) | **REAL (cached)** | cited values (Kollmitzer 2013, Dimova 2014, Garcia-Saez 2007) with provenance + validity range + uncertainty |
| Tier-0 analytic evaluator | **REAL** | Helfrich tube + spherical-cap budding/CCS; validated vs closed forms (rel_err ≤ 0.05%) |
| LLM orchestrator search loop | **REAL** | `host.llm` proposer with tool-forced structured output; offline deterministic fallback |
| Complementarity + IAV + CALM tests | **REAL** | run against the evaluator; falsifiable |
| MD-gap queue | **REAL detector, STUB return** | emits well-formed job specs on state-point mismatch; returns widened-uncertainty literature value |
| **FreeDTS Tier-1** | **STUB** | valid input deck generated & runnable later; not built on this host (design_note §4). Tier-0 carried the demo behind the same interface |
| **Averaged clathrin-track imaging data** | **NOT IN HAND** | CCS target anchored to published CCP geometry (R≈30–50 nm ⇒ Ω-stage H≈0.02–0.03 nm⁻¹); `ingest_clathrin_track()` seam swaps in the real trajectory unchanged |

### On the epsin biology citations

`Joseph et al. 2020 (Commun Biol)` is the **user's own paper**, named in the
sprint-plan document attached to this session (epsin tension-responsive
recruitment; abortive-fraction-vs-tension). `Joseph et al. 2022, Membranes
12(9):859` (doi:10.3390/membranes12090859) is a real related paper the user
supplied for the IAV spherical/filamentous case — it is **not** named in the
plan. The pipeline reproduces the **qualitative mechanism** described in these
works (ENTH+IDP complementarity; spherical/filamentous H0-dependence). It was
**not** quantitatively validated against those papers' measured data, which are
not in hand this sprint.

## Where MD plugs in (the seams that already exist)

1. **MD-Gap Queue** (`md_gap_queue.py`): when a target state point falls outside
   a parameter's stored validity range, the loop emits a well-formed MD job spec
   (system, observable, estimator — e.g. "c₀ of lipid X at tension σ via first
   moment of the lateral pressure profile") to a queue. Stubbed now; runnable
   later.
2. **FreeDTS Tier-1** (`md_gap_queue.FreeDTSTier1`): config-generator behind the
   same evaluator interface as Tier-0 — swap it in without touching the loop.
3. **Reverse seam**: a found FreeDTS shape backmaps to CG-MD via TS2CG (push a
   mesoscale result down to molecular detail).

## Can curvo extract *new* science? A worked demonstration

The honest test of a discovery engine is whether it produces a **falsifiable
prediction that was not already encoded in its inputs**. curvo passes this test
in three distinct modes.

### Mode 1 — Family screening (demonstrated: `outputs/family_screen.png`)

We ran the *identical* pipeline over six real AlphaFold structures spanning the
ENTH/epsin and ANTH families — **without ever telling it which protein is in
which family**. Each protein's wedge and crowding capacities were derived only
from its own pLDDT profile, N-terminal amphipathic moment, and disordered-tail
bulk, then pushed through the evaluator for maximum achievable curvature:

| rank | protein | family | H_max (nm⁻¹) | stage | crosses Ω? |
|------|---------|--------|-------------|-------|-----------|
| 1 | EPN1 | ENTH/epsin | 0.033 | Ω | ✅ |
| 2 | EPN2 | ENTH/epsin | 0.033 | Ω | ✅ |
| 3 | EPN3 | ENTH/epsin | 0.033 | Ω | ✅ |
| 4 | HIP1R | ANTH | 0.032 | Ω | ⚠️ **flagged false positive** |
| 5 | PICALM | ANTH | 0.020 | dome | ❌ |
| 6 | HIP1 | ANTH | 0.013 | flat | ❌ |

**The prediction (falsifiable, and not in the inputs):** all three epsins are
autonomous curvature generators (cross Ω); PICALM and HIP1 are not (they act as
adaptors, staying at dome/flat). This is a *ranking with a threshold* the
pipeline was never given — it emerges from structure alone. It matches the
documented ENTH-vs-ANTH division of labour (epsins insert an amphipathic AH0 and
generate curvature; ANTH proteins bind PIP2 and cargo but do not autonomously
bend the membrane).

**The most useful output is the error.** HIP1R is flagged: its N-terminal
amphipathic stretch trips the wedge detector, so the pipeline predicts Ω-crossing
capacity that its ANTH classification argues against. That disagreement is not
noise — it is a **specific, testable experimental target**: does HIP1R's
N-terminus actually insert and generate curvature, or is the moment a
false positive? A liposome tubulation assay on the HIP1R N-terminal peptide
answers it directly. curvo turned "screen a family" into "here is the one
protein worth doing the experiment on, and here is the exact experiment."

This is the bitter-lesson payoff: because the evaluator is cheap, the same loop
that solved epsin screens a whole family in seconds and *self-identifies where
its own prior is weakest*.

### Mode 2 — State-space prediction (built in)

For any single protein, the loop predicts how the flat→dome→Ω trajectory shifts
as you change **membrane tension, rigidity, or crowding** — because tension
enters the wedge sensor (`c_wedge = c0/(1+σ/σ_half)`) and the evaluator's
energetics directly. Concrete predictions it can already generate: the tension
at which epsin-driven budding stalls; how much IDR crowding compensates for a
tension increase; the cargo-size threshold at which H0 becomes load-bearing (the
IAV spherical/filamentous divergence is exactly this, computed).

### Mode 3 — Gap-driven discovery (the MD queue)

When a target state point falls outside the validity range of every stored
parameter, the loop does not guess — it **emits a well-formed MD job spec**
naming the system, observable, and estimator needed to close the gap. This turns
"we don't know c₀ for this lipid at this tension" into a runnable simulation
request. The queue *is* a prioritized list of the measurements that would most
improve the model — discovery as a scheduling problem.

### What would make these findings publishable

The predictions above are **mechanistically derived and internally validated**,
but not yet experimentally confirmed. To move from "curvo predicts" to "we
show": (1) run the flagged HIP1R tubulation assay; (2) validate one family
member's predicted tension-response against your imaging; (3) run Tier-1 MD
(the FreeDTS deck is generated) on one case to confirm the closed-form ranking
survives molecular detail. The pipeline is built so each of these plugs into an
existing seam without touching the loop.

To reproduce the family screen: `python family_screen.py`. It writes
`outputs/family_screen.png` and `outputs/family_screen.json` (full per-protein
breakdown: moment, AH0 position, IDR bulk, c_eff, stage, flag).

## Module map

```
curvo/
  schemas.py            data contracts: ParameterRecord (provenance+validity+uncertainty),
                        StructureModel, RepresentationDecision, OrchestrationRecord
  structure_provider.py AlphaFold DB adapter + pLDDT→representation split + guardrails
  parameter_store.py    live (NMRlipids) + curated-literature adapters, uniform records
  evaluator_tier0.py    closed-form Helfrich tube + budding/CCS; the ground-truth engine
  players.py            wedge/crowding/coat/tension; candidate reps + guardrail validators
  orchestrator.py       propose→prune→resolve→EVALUATE→revise search loop
  md_gap_queue.py       MD-gap detector + job specs; FreeDTS Tier-1 seam (stub)
  schematic.py          SVG orchestration schematic, generated from OrchestrationRecord
run_demo.py             one-command end-to-end demo (offline by default)
family_screen.py        ENTH-vs-ANTH family screen -> falsifiable ranked prediction
tests/test_players.py   guardrail validator unit tests
design_note.md          the bitter-lesson reframing in full
```

## Key results (all reproduced by `run_demo.py`)

- **Epsin CCS**: full orchestration reaches the Ω-stage curvature target at
  elevated tension.
- **Complementarity**: neither H0 wedge (max H≈0.017) nor IDP crowding
  (max H≈0.021) alone crosses the Ω threshold; only the full wedge+crowding+coat
  orchestration does (H≈0.033).
- **IAV divergence**: spherical cargo is H0-dependent (fails without H0);
  filamentous cargo is H0-independent (pre-curved, low demand).
- **CALM transfer**: the identical pipeline, given PICALM's own pLDDT-derived
  representation, predicts a ~40 nm vesicle in the documented sub-100 nm regime
  — proving the method generalizes rather than overfitting epsin.
- **Closed-form anchors**: the loop recovers the budding phase boundary
  a\* = 4κ/λ to <0.05% before being trusted on epsin.
