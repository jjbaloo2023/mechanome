# Program structure

`mechanome` is organized as one umbrella project with a membrane-scale inverse
engine (`curvo/`) at its core, a multi-scale schema and forward-model set
(`mechanome/`), a structure-based screen (`mechanome/structural_screen/`), a
validation suite (`validation/`), and an RL scaffold (`rl/`). Physical
constants live in exactly one place (`curvo/constants.py`).

## `curvo/` — the membrane-scale inverse engine

| Module | Responsibility |
|--------|----------------|
| `constants.py` | Single source of truth for shared physical constants (kBT, default κ, coat rigidity). |
| `schemas.py` | Core data contracts for the curvature-orchestration pipeline. |
| `players.py` | The player ontology; physics enters as guardrails, not deciders. |
| `parameter_store.py` | The "use existing data" backbone (cached literature/DB parameters with provenance). |
| `structure_provider.py` | Public ML structure models (AlphaFold) as pre-existing data. |
| `evaluator_tier0.py` | The cheap analytic evaluator (Helfrich tube + spherical-cap budding/CCS), microseconds/call. |
| `orchestrator.py` | The search loop — the bitter-lesson engine (propose → prune → resolve → evaluate → revise). |
| `synth_movie.py` | Forward-simulate a curvature trajectory from known forces (synthetic ground truth). |
| `perception.py` | PerceptionProvider: pixels → calibrated Geometry(t) + Density(t). |
| `inverse.py` | The Bayesian inverse engine: geometry(t) → posterior (nested sampling + MCMC cross-check). |
| `mechanism.py` | Bayesian mechanism-discrimination core (evidence-ratio model comparison). |
| `recovery.py` | Synthetic recovery validation — the credibility gate for every force claim. |
| `analyze.py` | The top-level agent endpoint: `analyze(video, question)`. |
| `md_gap_queue.py` | The future-oriented seam where MD plugs in. |
| `schematic.py` | Auto-generated publication-style output schematic. |

## `mechanome/` — the multi-scale schema and forward models

| Module | Responsibility |
|--------|----------------|
| `schema.py` | The `MechanoClaim` data contract with structural epistemic-tier enforcement. |
| `registry.py` | The Forward-Model and Module registries — makes the schema executable. |
| `emit.py` | Convert curvo's validated outputs into GROUNDED `MechanoClaim`s. |
| `links.py` | Curated LINKED edges (flagged mechanotransduction hypotheses). |
| `mechano_schematic.py` | Render a set of `MechanoClaim`s as a tiered scale-map graph. |
| `forward_tissue.py` | Tissue module — vertex / junction force inference (`vertex_v1`). |
| `forward_cortex.py` | Cortex module — active-gel cortical tension via Young-Laplace (`active_gel_v1`). |
| `forward_bond.py` | Bond module — Bell / catch-slip molecular bond (`catch_slip_v1`). |
| `forward_channel.py` | Channel module — mechanosensitive gating, MscL/Piezo-type (`ms_gating_v1`). |
| `channel_link.py` | The structural-screen → channel cross-scale link (structure-derived c₀ → gating Po). |

## `mechanome/structural_screen/` — the structure-based mechanical screen

Vendored from *mechanistic-entry-model*. Ranks membrane proteins by
structure-derived curvature-generating capacity (`structural_screen_v1`). Stages
0–4 under `src/`; precomputed `results/` + `figures/` are authoritative; the
scored ranking is frozen with a SHA-256 integrity hash and a pre-registration.
See `structural_screen/MODULE.md`.

## `validation/` — the validation and demonstration suite

Real force-paired STED (`tether_sted.py`), the perception operating-envelope
benchmark (`perception_benchmark.py`, `plot_envelope.py`), pixels→force
(`image_to_force.py`), cryo-ET modality transfer (`modality_adapter.py`,
`real_image_probe.py`, `mddb_adapter.py`), the orchestration-recovery program
(`field_movie.py` → `tracking.py` → `motion.py` → `per_track_recovery.py` →
`orchestration.py`), and the real-data case studies under `validation/realdata/`
(2020/2022 epsin/IAV ingestion, PICALM and epsin-domain orchestration,
ENTH-fusion designs, the ENTH+AP180 inverse-recovery closure).

## `rl/` — the RL scaffold (a byproduct, not the scientific aim)

| Module | Responsibility |
|--------|----------------|
| `ccp_budding_env.py` | `CCPBuddingEnv` — a Gymnasium environment over curvo's forward model. |
| `train_agent.py` | A lightweight tabular Q-learning sanity run on `CCPBuddingEnv`. |

## `tests/` — the test suite

One test module per subsystem: `test_players`, `test_validation`,
`test_analyze_guardrails`, `test_inverse_guard`, `test_perception_benchmark`,
`test_modality_adapter`, `test_orchestration`, `test_realdata`,
`test_mechanome` (schema + emission), `test_mechanome_modules` (the four
analytic forward models + registry integrity + structural-screen integrity),
and `test_rl_env` (the RL environment API).
