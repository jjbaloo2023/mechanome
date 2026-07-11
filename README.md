# curvo — bitter-lesson curvature orchestration **and mechanistic inference**

curvo has two coupled halves:

1. **Forward / orchestration (v0.1).** Given a UniProt ID and a target membrane
   curvature, a closed loop decides **which physical representation to use for
   each player**, resolves parameters from pre-existing data, evaluates against
   closed-form ground truth, and revises — until it meets the target.
   Demonstrated on the epsin clathrin-coated-structure (CCS) case.
2. **Inverse / mechanistic inference (v0.2).** The north-star endpoint
   **`analyze(video, question)`** runs the loop *backwards*: a microscopy movie
   and a mechanistic question in → **inferred forces, the favored mechanism,
   calibrated uncertainty, an identifiability report, and a suggested
   disambiguating experiment** out. It inverts the same biophysical forward
   model under MD-derived priors with a proper Bayesian engine (nested sampling
   + MCMC), and it **refuses to report a force it cannot identify** — returning a
   posterior flagged *underdetermined* instead of a confident wrong number.

The v2 build (Phases 0–8) is documented in
[**§ The inverse engine**](#the-inverse-engine-analyzevideo-question) below;
the whole synthetic-recovery validation gate that licenses every force claim is
in [§ The credibility gate](#the-credibility-gate-synthetic-recovery-validation).

```bash
git clone https://github.com/jjbaloo2023/curvo.git
cd curvo
pip install -e .              # numpy, scipy, requests
pip install -e ".[plots]"     # + matplotlib for the figure scripts
pip install -e ".[inference]" # + dynesty, emcee, corner for the inverse engine
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

## The inverse engine: `analyze(video, question)`

This is the v2 north star — the endpoint an agent calls.

```python
from curvo.analyze import analyze
result = analyze(movie,                       # np.ndarray [T, C, H, W]
                 question="Is the invagination driven by the wedge or by actin?",
                 channels=["membrane", "coat", "actin"], nm_per_px=2.0)
# -> {forces, favored_mechanism, uncertainty, identifiability,
#     suggested_experiment, provenance}
```

The pipeline is four honest stages:

```
video ──PerceptionProvider──▶ geometry(t) ──inverse (nested sampling)──▶ force posterior
                              + per-frame σ         + identifiability
                                                          │
                                              mechanism core ──▶ evidence ranking
                                                          │         + disambiguating experiment
                                                          ▼
                                                  structured result
```

![analyze() endpoint](outputs/analyze_endpoint.png)

1. **PerceptionProvider** (`perception.py`) turns pixels into a geometry
   trajectory: a PSF-corrected spherical-cap fit on the *contiguous central
   invagination* (rejecting flat-membrane wings), giving `R(t)`, mean curvature
   `H(t)`, neck, depth, and the coat/actin density channels — each with a
   **per-frame uncertainty**. Caps shallower than one PSF σ are flagged and their
   `H` uncertainty inflated (a resolvability gate), so the downstream likelihood
   down-weights them rather than trusting a spurious point value. The
   model-choice step is LLM-orchestrated behind a guardrail fallback (only the
   analytic extractor is installed; the seam is there).
2. **Bayesian inverse** (`inverse.py`) inverts the forward model — the same
   spherical-cap Helfrich energetics as the evaluator, plus the new
   **active-stress / cortex term** (a cortical force pulling the cap inward, work
   `−f·d`) — for the posterior over `{c_eff_max, active_force_max, σ}`. A
   vectorized fast forward model matches the evaluator to `7e-5` and runs ~350×
   faster, so a full nested-sampling run finishes in seconds on a CPU. **dynesty**
   (nested sampling, exact log-evidence) is the primary engine; **emcee** (MCMC)
   is an independent cross-check (active-force medians agree to <0.3%); **SBI** is
   a documented seam (`fit_sbi`), not built — the cheap forward model makes exact
   inference tractable, so hardware pointed us at exact-first (this inverts the
   plan's SBI-primary recommendation, on purpose).
3. **Identifiability & the anti-force-astrology guardrail.** `identifiability()`
   reports per-parameter interval width, information gain, **joint degeneracy**
   (two actors can each have a tight marginal yet trade off — detected from the
   posterior correlation and both demoted to *unidentified*), and **prior
   railing** (a posterior piled against a bound is not data-driven). `analyze()`
   then returns a **point estimate only for forces the recovery-validation gate
   certified calibrated**; everything else comes back as a posterior with the
   reason it is underdetermined. This is the difference between an inference
   engine and a horoscope.
4. **Mechanism discrimination** (`mechanism.py`) fits competing hypotheses —
   `tension_only`, `wedge_only`, `actin_only`, `wedge+actin` — each a restricted
   forward model, and ranks them by **Bayesian evidence** (nested sampling's
   built-in Occam penalty). A decisive winner needs a log-Bayes-factor ≥ 2.5 over
   the runner-up *and* must not have won only via an unidentifiable extra actor
   (an overfit guard). Otherwise the verdict is **UNDETERMINED** and the engine
   **proposes the disambiguating experiment**.

**The headline result — the same movie, two answers, honestly:**

![mechanism discrimination](outputs/mechanism_discrimination.png)

| analysis of the *same* actin-driven movie | favored mechanism | active force | verdict |
|---|---|---|---|
| **with** the cortical-actin channel | wedge+actin (lnB ≈ 18) | **41 pN** (truth 40, identified) | decisive |
| **geometry only** (actin channel withheld) | — | *underdetermined* | UNDETERMINED → **suggests** co-imaging actin / latrunculin / H0-mutation |

From membrane geometry alone, spontaneous curvature and cortical force are
**mathematically degenerate** — they trade off in the cap energy. curvo does not
paper over this: it flags both as unidentified and tells you the one measurement
that would separate them. Add the actin channel and the force becomes
identifiable, calibrated, and reported.

## The credibility gate: synthetic recovery validation

**No force claim ships without this.** `recovery.py` sweeps known ground-truth
forces through the *entire* pipeline (`forces → render → perceive → invert`)
across five regimes × eight independent noise realizations (40 inversions), and
checks the recovered posteriors against truth:

![recovery validation](outputs/recovery_validation.png)

| force | identified | coverage of 68% CI \| identified | bias \| identified | verdict |
|-------|-----------|-------------------------------|-------------------|---------|
| `active_force_max` | 24/40 (only with actin channel) | **0.96** | **+2.0%** | **calibrated** ✅ |
| `c_eff_max` | 0/40 | — | — | degenerate from geometry alone |
| `sigma` (tension) | 0/40 | — | — | not identifiable from one CCP's geometry |

Cortical force is recovered with correct calibration **only where the actin
channel constrains it** — never from geometry alone, exactly as the degeneracy
structure demands. Spontaneous curvature and tension are honestly reported as
unidentifiable from this observable set. Two calibration bugs were caught *by
this gate* and fixed at source (a max-of-noise actin-peak bias → robust top-k
peak + a measured estimator-gain correction; a railed-σ false positive → prior-
rail detection). The gate is what licenses `analyze()` to return `active_force`
as a number at all.

Reproduce: `python -c "from curvo import recovery as r; recs=r.recovery_grid(); print(r.calibration_summary(recs))"`
(≈13 min, 40 nested-sampling inversions). Guardrail contract tests:
`python tests/test_analyze_guardrails.py`.

## Validation against real force-paired data

The synthetic recovery gate proves the inverse is *self-consistent*. This section
tests it against **real measured forces** (`validation/`).

**Tether / STED (the real force-paired test).** Roy, Steinkühler, Zhao, Lipowsky
& Dimova (2020, *Nano Lett.* 20:3185, doi:10.1021/acs.nanolett.9b05232) pull a
POPC giant vesicle into a membrane nanotube: the tube **radius** is measured by
super-resolution STED, the membrane **tension** is set independently by
micropipette aspiration (15–140 µN/m), and κ is measured two independent ways
(23±2 kBT thermal, 23±5 kBT tube-pulling). POPC has ~zero spontaneous curvature,
so curvo's `helfrich_tube` forward map applies exactly. We feed curvo the STED
radius (with the paper's ±11 nm precision) + κ as a prior, infer the tension, and
propagate to the holding force — checked against the aspiration-tension ground
truth.

![force recovery on real membrane data](outputs/tether_force_recovery.png)

| Σ (µN/m) | f measured (pN) | f recovered (pN) | 68% coverage | rel. bias |
|---|---|---|---|---|
| 20 | 12.2 | 12.5 | 0.97 | +2.5% |
| 40 | 17.3 | 18.5 | 0.92 | +7.2% |
| 72 | 23.2 | 24.3 | 0.90 | +4.7% |
| 100 | 27.3 | 27.5 | 0.94 | +0.7% |
| 130 | 31.2 | 30.0 | 0.96 | −3.7% |

**Verdict: acceptable.** Forces recovered near-unbiased (mean |bias| 3.8%) across
the full range; the 68% CIs are *conservative* (coverage 0.90–0.97, wider than
nominal) — the posteriors err toward humility, not overconfidence. The mild
low-tension positive bias is the √-nonlinearity mapping radius noise
asymmetrically into force (explainable, not a defect). Reproduce:
`python validation/tether_sted.py`.

**MDDB adapter (provenance breadth, not force).** `validation/mddb_adapter.py`
pulls real per-frame membrane observables live from the
[Molecular Dynamics Data Bank](https://mddbr.eu) (REST API). An honest finding
from the live API: **MDDB serves *structural* observables** (thickness,
area-per-lipid, lipid-order, density) — **not** stress profiles or tension. So it
is an independent MD source for curvo's elastic *parameters* (which set κ), not a
direct force ground truth. The cross-check is diagnostic: a protein-containing
bilayer (A020P, 303 K) is 0.44 nm thinner than pure POPC — a large z-score that
correctly flags a *composition mismatch* rather than agreement. That is exactly
what a parameter cross-check should surface.

*Scope, stated plainly:* the tether/STED test validates the forward map + Bayesian
inverse on the **tube geometry** against real forces; the MDDB adapter adds a
second orthogonal source for structural inputs. Neither replaces the synthetic
recovery gate for the CCS spherical-cap `analyze()` pipeline — they are
complementary evidence, at different points in the pipeline.

## Perception validation on image data

The tether/STED test above inverts *reported* radii. The one piece it does not
exercise is **perception** — pixels → geometry — the front end that every image
analysis depends on. `validation/perception_benchmark.py` is a held-out image
benchmark that closes that gap. Because measuring recovery accuracy requires exact
geometry ground truth, and only rendered images carry it, the benchmark images are
synthetic *by necessity*; the companion probe below is an honest look at a real
image.

**Operating envelope (exact ground truth).** Single clathrin-coated-pit images are
rendered across conditions *outside* the calibration set — PSF width, pixel size,
photon budget, cap depth, off-center — and the extractor recovers mean curvature H
from the resolvable band (cap depth 1.3–2.2 × PSF σ, a data-driven reliable
window).

![operating envelope](outputs/envelope_recovery.png)

- **Core envelope: H recovered to ~10–22% (median 13%)** across the 13
  resolution-matched conditions — PSF σ = 18 nm, pixel size 2–4 nm/px, photons
  40–400, cap depth c_eff 0.045–0.08, off-center ≤ 6 px — robust to SNR (photons
  40–400: 13–18%) and moderate off-center (6 px: 22%).
- **Degradation edges, characterized honestly:** at PSF σ = 10 nm the reliable band
  nearly vanishes (few frames clear the resolvability floor → 76%);
  under-sampling at 1 nm/px → 98%; large off-center (12 px) → 42%; and the
  **deep-Ω plateau** (depth > 2.2 σ) under-reads by ~25–38% because the
  spherical-cap-on-projection assumption saturates. (Note PSF σ = 10 nm and
  1 nm/px each satisfy a naive "fine-resolution" reading yet sit far outside the
  core band — they are excluded from it by measurement, not by the σ/sampling
  numbers alone.)
- **Uncertainty caveat, flagged not hidden:** the per-frame bootstrap CI
  *under-covers* (coverage68 ≈ 0.33 vs 0.68 nominal) in this band. The point
  estimate is trustworthy; the per-frame σ needs widening. This is reported as a
  known limitation, not glossed as a pass.

**Robustness stressors.** The failure modes a real micrograph carries:

![robustness stressors](outputs/stressor_panels.png)

Partial occlusion is tolerated (~0.9× baseline — the extractor keys on the
contiguous central dip, so a cropped edge is harmless) and doubled shot noise is
absorbed (~1.0×). Background gradients and neighboring bright structures roughly
double the error (~1.9–2.0×): they shift the intensity baseline the cap-fit
references.

**End-to-end image → force (closing the pixels→force gap).** The STED test used
reported radii; here the *full* pipeline runs from pixels — perception extracts the
geometry, the inverse recovers the force — on held-out actin-driven movies with
known force.

![image to force](outputs/image_to_force.png)

Identified forces (25, 40 pN) are recovered at **6% bias from pixels alone**; 55
and 70 pN are correctly **refused as UNDETERMINED** by the anti-force-astrology
guardrail rather than reporting a biased point value (at 70 pN the posterior median
drops to ~60). The guardrail that licenses force claims survives the move from
reported numbers to extracted geometry.

**Honest real-image transfer probe.** One accessible real curved-membrane image —
a cryo-ET synaptic-vesicle subtomogram average (EMDB EMD-65182, 0.906 nm/px) —
tests whether the front end transfers.

![real-image probe](outputs/real_image_probe.png)

It does **not**, and that is the finding: the modality differs on three axes at
once — density contrast (membrane *dark*, not bright), top-down *ring* geometry
(not a side-view *cap*), and a subtomogram *average* (not a single fluorescence
frame). curvo's native cap-extractor is inapplicable and correctly declines. The
underlying **curvature-measurement primitive does transfer**: a contrast-flipped
radial fit recovers a physical membrane radius (R ≈ 9 nm, band 6–15 nm, SNR 5).
Closing the gap needs a modality adapter (contrast flip + ring/cap geometry) — the
documented seam for a real super-resolution dataset when one is in hand.

**Modality adapter — the seam, now built.** `validation/modality_adapter.py`
closes the two axes of that gap that a *single image* can close. It contrast-flips
the density, fits the membrane ring (radial profile + sub-pixel peak, bootstrap
uncertainty from ±1 px center jitter), and emits a `GeometryTrace` — the exact
structure curvo's perception front end produces — so the rest of the stack can
consume a real cryo-ET image.

![modality adapter](outputs/modality_adapter.png)

On EMD-65182 it yields R = 8.9 ± 0.5 nm and mean curvature H = 0.056 ± 0.003 nm⁻¹
(cylindrical model; a `spherical` model gives 2×). The **third** axis — dynamics
and force — it does *not* close and does not pretend to: a static subtomogram
average has no time series and no actin channel, so the emitted trace carries one
frame, `has_actin_channel=False`, and `force_applicable=False`. Interpreting a
composition-set vesicle radius as a tension-set tube would back-calculate a
meaningless ~500 µN/m — precisely the force-astrology the project forbids — so the
adapter stops at the curvature measurement. Recovering force from a real sample
needs a time-resolved series, which the adapter is shaped to accept.

*Full report:* `outputs/perception_benchmark.json`. *Reproduce:*
`python validation/perception_benchmark.py` (sweep + stressors),
`python validation/image_to_force.py`, `python validation/real_image_probe.py`,
`python -m validation.modality_adapter`.

**Sampler plateau guard.** The end-to-end image→force run once hung ~6 h on a
dynesty likelihood plateau. `inverse.run_nested` now takes explicit `dlogz`
(default 0.05, tighter than dynesty's own nlive-dependent default), `maxcall`
(500k, ≈ minutes worst-case), and `maxiter` stopping caps, and reports
`stopped_early` / `ncall` so a caller can tell a converged run from a capped one.
The guard bounds runaway cost without truncating a healthy run.

## The mechanome: the schema curvo is the reference implementation of

curvo grounds *one* edge of the cell's mechanical layer. The `mechanome/` package
promotes curvo's `ParameterRecord` discipline — provenance + uncertainty +
validity — into the organizing principle of a whole federated schema, where every
mechano-relationship wears its **epistemic tier** on its face.

**The invariant (the whole design rests on it):** every claim is **GROUNDED**
(a forward-model inverse run against data, carrying value + uncertainty +
identifiability), **MEASURED** (a cited experimental value with provenance), or
**LINKED** (a flagged mechanotransduction hypothesis with an explicit causal
chain and a proposed test, and **no physical value**). The system never silently
promotes a lower tier to a higher one — the schema raises rather than emit a claim
that would.

| Tier | Produced by | Carries |
|------|-------------|---------|
| **GROUNDED** | a module's forward+inverse against data | value + uncertainty + identifiability |
| **MEASURED** | retrieval of a cited measurement | value + uncertainty + citation |
| **LINKED** | a mechanotransduction chain | causal chain + proposed experiment; **no value** |

The GROUNDED↔LINKED boundary is the **credibility firewall**: force-to-shape is
force balance (a well-posed inverse); force-to-transcription-factor-activity is
multi-step signaling (correlative). Mixing them is how a knowledge graph launders
correlation into physics — `mechanome/schema.py` forbids it structurally, in
`__post_init__`.

![tiered mechanome walk](outputs/mechanome_schematic.png)

The figure is the walk: a GROUNDED force (curvo's real force-paired tether result,
solid), a GROUNDED capacity prediction (epsin EPN1, tiered honestly as
grounded-on-*synthetic-recovery*, **not** on an EPN1 trajectory we never had), and
a dashed LINKED node (membrane tension → Piezo1 → YAP) that carries a proposed
experiment and **no force value**.

```json
// GROUNDED (real force-paired) — from mechanome.emit
{ "subject": {"id":"POPC_bilayer","type":"lipid"}, "relation":"bears",
  "object":"tether_force", "forward_model":"helfrich_v1",
  "value":{"estimate":24.1,"uncertainty":7.47,"units":"pN"},
  "identifiability":"constrained", "epistemic_tier":"GROUNDED",
  "evidence":["STED tube diameter 51 nm (Roy et al. 2020, doi:10.1021/acs.nanolett.9b05232)",
              "curvo:inverse","real_force_paired_validation:pass (mean |bias| 3.8%)"] }

// LINKED (note: no value; chain + experiment required)
{ "subject":{"id":"membrane_tension"}, "relation":"modulates",
  "object":"YAP_nuclear_localization", "value":null, "epistemic_tier":"LINKED",
  "evidence":["chain: membrane_tension -> Piezo1 -> [Ca2+] -> ... -> YAP (correlative, lit)"],
  "reasoning_trace":"proposed test: hyperosmotic shock + YAP reporter" }
```

**What is real vs stub in the mechanome (stated openly):**

| Component | Status |
|-----------|--------|
| `MechanoClaim` schema + tier enforcement + provenance | **REAL** |
| curvo membrane module (GROUNDED, force-paired + synthetic-recovery validated) | **REAL** |
| GROUNDED emitters (tether force, family capacity) | **REAL (run live)** |
| `helfrich_v1` forward-model registry entry | **REAL (executable)** |
| tension→Piezo1→YAP edge | **LINKED — curated from literature, not learned; no value** |
| tissue / cortex / bond / channel modules | **REGISTERED STUBS — cannot emit GROUNDED until they pass `validate()`** |

A module that can't pass `validate()` (synthetic recovery + an analytic anchor)
is blocked from emitting GROUNDED claims (`registry.can_emit_grounded`) — it may
register MEASURED literature or LINKED hypotheses only. Reproduce the walk:
`python -m mechanome.mechano_schematic`.

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
  --- v2 inverse engine ---
  synth_movie.py        forces -> spherical-cap trajectory -> noisy multi-channel movie + ground truth
  perception.py         PerceptionProvider: pixels -> geometry(t) with per-frame uncertainty
  inverse.py            Bayesian inverse: fast forward model + dynesty/emcee + identifiability
  mechanism.py          competing-hypothesis evidence ranking + disambiguating-experiment proposer
  recovery.py           synthetic recovery validation — the credibility gate
  analyze.py            analyze(video, question) — the north-star agent endpoint
  --- real-data validation (validation/) ---
  validation/tether_sted.py    inverse vs force-paired STED nanotubes (Roy et al. 2020)
  validation/mddb_adapter.py   live Molecular Dynamics Data Bank membrane-parameter adapter
  validation/perception_benchmark.py  held-out image operating-envelope sweep + robustness stressors
  validation/plot_envelope.py  operating-envelope figure renderer
  validation/image_to_force.py end-to-end pixels->force on EXTRACTED geometry
  validation/real_image_probe.py  honest transfer probe on a real cryo-ET membrane (EMD-65182)
  validation/modality_adapter.py  cryo-ET density image -> curvo GeometryTrace (contrast + ring/cap)
  --- mechanome schema (mechanome/) ---
  mechanome/schema.py          MechanoClaim + epistemic-tier firewall (GROUNDED/MEASURED/LINKED)
  mechanome/emit.py            curvo outputs -> GROUNDED claims (tether force, family capacity)
  mechanome/links.py           curated LINKED edge (tension -> Piezo1 -> YAP), no value
  mechanome/registry.py        forward-model + module registry (helfrich_v1 real; rest stubs)
  mechanome/mechano_schematic.py  tiered walk renderer (solid=GROUNDED, dashed=LINKED)
run_demo.py             one-command end-to-end demo (offline by default)
family_screen.py        ENTH-vs-ANTH family screen -> falsifiable ranked prediction
tests/test_players.py   guardrail validator unit tests (12)
tests/test_analyze_guardrails.py  anti-force-astrology endpoint contract tests (4)
tests/test_validation.py          real-data validation contract tests (4)
design_note.md          the bitter-lesson reframing in full
```

The forward evaluator gained an **active-stress / cortex term** this build
(`evaluator_tier0.ccs_curvature(..., active_force_pN=...)`): a cortical machine
applies an axial force pulling the cap inward, contributing work `−f·d` (depth
`d = R(1−cos ψ)`) to the cap energy — physically distinct from tension (which
opposes footprint growth) and from spontaneous curvature (which sets the
preferred shape). This is what makes actin an inferable actor and is the origin
of the c_eff/active degeneracy the inverse engine must confront.

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

### v2 inverse-engine results

- **Recovery calibration**: cortical `active_force` is recovered with 96% CI
  coverage and +2% bias — but **only where the actin channel constrains it**
  (24/40 grid cells). `c_eff` and tension are honestly reported unidentifiable
  from geometry alone (0/40).
- **Degeneracy, flagged not hidden**: from `H(t)` alone, spontaneous curvature
  and cortical force have posterior correlation ≈ −0.74; both are demoted to
  *underdetermined* rather than reported as confident (wrong) point values.
- **Mechanism discrimination**: the same actin-driven movie is decisively
  `wedge+actin` (log-Bayes-factor ≈ 18) with the actin channel, but UNDETERMINED
  from geometry alone — where the engine instead **proposes the disambiguating
  experiment** (co-image actin / latrunculin / H0-mutation).
- **Engine cross-check**: dynesty (nested sampling) and emcee (MCMC) active-force
  medians agree to <0.3%.
- **Guardrail contracts**: 12/12 player-validator tests + 4/4 anti-force-astrology
  endpoint tests pass.
