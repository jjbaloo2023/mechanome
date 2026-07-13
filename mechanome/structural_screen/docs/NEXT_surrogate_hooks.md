# Second-half handoff: neural surrogate + folding, and how to dodge the circularity trap

> Sequencing is FIXED: the Stage-3 solver must exist before the surrogate (it is the training-data
> generator). It does. This doc is the handoff spec — no GPU work is done here.

## 1. The solver is the data generator (why the surrogate is free-data)

The Stage-3 capacity solver (`E_curv = ½κ(2c₀)²A + γΔA`) is CPU-light and fully differentiable in its
continuum parameters. It maps a small structured input to a scalar:

- **Inputs (per protein-state):** `c₀ (1/nm)`, `A_footprint (nm²)`, `ΔA (nm²)`, `charge_moment (e·Å)`,
  leg/sign, plus the Stage-0 constants `(κ, γ, neck radius)`.
- **Output:** `E_curv (k_BT)` and its sign.

Because the solver is cheap, it can emit **unlimited self-supervised labels** by sweeping the input
space (c₀ ∈ [−0.15, 0.15]/nm, A ∈ [1, 300] nm², γ ∈ [resting, lysed], κ ∈ [10, 40] k_BT). A small MLP
(minutes, CPU) or a neural operator (DeepONet/FNO, single GPU) emulates it for ms-latency inference →
snappy design-inversion loops ("what c₀ do I need to hit 20 k_BT at this footprint?").

**Right-sized compute:** the coworker's single GPU is correct for surrogate training. No HPC needed.
This is the first real job for that GPU.

## 2. The circularity trap and its defeat

"You trained a net to copy your own equations, so what?" — correct criticism if the surrogate only
emulates the solver. **Defeat it by learning the residual between physics and experiment:**

```
E_measured (SIM-TIRF / literature curvature assays) = E_curv_physics + f_θ(structure features)
                                                        └ known ┘        └ learned correction ┘
```

`f_θ` is trained on the gap between the continuum prediction and measured curvature-generation data.
Where physics is right, `f_θ → 0`; where it breaks (specific lipid chemistry, crowding, protein–protein
cooperativity), `f_θ` is nonzero — and **`f_θ` is a fingerprint of the molecular machinery the continuum
theory omits.** That operationalizes the "where does mechanism fail" finding and makes the module a real
scientific instrument, not a lookup table.

## 3. Folding: candidates needing a second conformational state

9/13 proteins have only one experimental state, so their capacity is an intrinsic-shape upper bound.
Boltz-2 / OpenFold3 (coworker GPU) should generate the missing state to convert these to clean
ΔA/Δc₀ transitions. Priority order (highest current rank first, so the folding buys the most):

| Protein | Have | Need | Why it matters |
|---|---|---|---|
| TRPV4 | 8FC7 (RhoA complex) | apo / ligand-open | rank-1 rests on a single conical state — most important to confirm |
| Piezo1 | 6B3R (curved dome) | flattened/tension state | dome→flat is the whole mechanism; ΔA would be large |
| MscL | 2OAR (closed) | expanded/open | classic ΔA; open models exist but not experimental |
| TREK-1 | 4TWK | up/down gating pair | K2P gating area change |
| OSCA1.2 | 6MGV | activated state | mechano-gating |

Clean two-state proteins (MscS, nhTMEM16, Epsin ENTH) need no folding — their ΔA/Δc₀ are already
measured.

## 4. Scope axes (same recipe, different regimes)

- **data:** solver generates labels; residual net learns corrections
- **inference:** ms vs s → design-inversion and screening loops
- **scope:** endocytosis / exocytosis / membrane escape = different `(κ, γ, sign)` regimes, one engine.
  The Stage-3 sign-flip figure already demonstrates the endo/exo axis works from one functional.

## 5. Validation data (upgrade, not dependency)

SIM-TIRF curvature-generation data (if the PI call yields it) validates the *physics core* and trains
`f_θ`. It is decoupled from the deliverable: Stage-4 validation already ran on public GO labels. Nothing
load-bearing is gated behind the PI call.
