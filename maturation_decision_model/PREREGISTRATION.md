# Pre-registered prediction — epsin steric term (sign committed before plotting)

**Model:** steric-augmented Helfrich barrier → logistic decision layer.
**Free parameters (the ONLY floated numbers):** decision-layer α, ΔE½. Fixed once so
the baseline abortive fraction lands in a physiological band; NOT fit per condition.
All membrane/steric physics fixed from literature (see MODEL.md).

## Committed prediction (direction, not precision)
1. **P(abort) rises monotonically with membrane tension** (hyper→iso→hypo), because
   tension raises the commit barrier ΔE_commit(σ). [foundational, Rangamani]
2. **The epsin disordered-CTD steric term LOWERS P(abort)** at every tension, because
   the steric pressure adds positive C₀_eff, lowering the commit barrier. [novel term]
3. **The steric term BUFFERS the tension-driven rise** — the P(abort)-vs-σ curve is
   flatter with the steric term than without it (ENTH wedge alone). This is the
   model's explanation for the reported epsin damping of the abortive increase.
4. **Robustness:** the direction of (2)–(3) holds across the steric efficiency η∈[0.5,2]
   (the one order-of-magnitude-uncertain parameter); only the magnitude scales.

Sign committed 2026-07-08 before rendering fig_pabort_vs_tension.png.
Empirical validation against live-cell abortive fractions is handled separately (Jophin);
this module delivers the physics prediction only.
