# From time-lapse to orchestration: what transfers, what doesn't

*The goal (user, this session): look at time-lapse super-resolution images of
membrane structures (clathrin pits, caveolae, actin), detect and track their
evolution, apply motion/force-field ideas (PIV, TFM — listed as candidates, "this
may not work for our case"), then **recover the underlying membrane/structure
physics from first principles** and propose a model of how the protein players are
orchestrated. The emphasis on recovering physics is deliberate: a model that
carries real physical constraints is worth far more than one that reasons
qualitatively — and, as a side effect, a validated forward+inverse world makes a
scored RL environment. Scaling the science is the aim; the environment is a bonus,
not a build target.*

This document is the honest map of that program onto what curvo already has and
what real data actually exists — written before building, so the plan is grounded
rather than aspirational.

## 1. Data-reality gate

The program needs **time-resolved images of curved membrane structures with enough
signal to extract geometry per frame**, ideally with force ground truth. What is
actually reachable from this sandbox:

| Source | Reachable? | What it serves | Gap for this program |
|---|---|---|---|
| **IDR** (Image Data Resource) | yes (147 studies, after allowlisting) | public live-cell / light-sheet microscopy | dominated by developmental / tissue / light-sheet studies; **one** cytoskeletal study (`idr0050-springer`), **no** CME/caveolae force-paired live-cell time-lapse in the public API set |
| **EMDB / EMPIAR** (cryo-ET) | yes | real curved-membrane density (probed earlier in this project — EMD-65182, the basis of `real_image_probe.py` + `modality_adapter.py`) | static subtomogram **averages**, no time axis, density-contrast modality (needs the modality adapter) — no dynamics, no force |
| **STED tether paper** (Roy 2020) | fetched | force-paired tube geometry | single geometry, reported radii — already used to validate the inverse on tube geometry |
| **Live-cell super-res (CCP)** | not yet in hand | the real target | the documented ingestion seam |

**Ruling (consistent with the whole project):** no accessible real dataset carries
the modality + per-structure force ground truth this program needs. So we build
**synthetic-first** — a multi-structure time-lapse with exact ground-truth tracks
and known forces — and keep the real-image ingestion seam (the modality adapter,
built last session, is the front half of it). This is the same honest posture that
governed the single-CCP recovery gate and the perception benchmark: validate on
data where truth is known, expose a seam for data where it isn't.

## 2. Method-transfer map

PIV and TFM are candidate approaches for extracting kinematics and forces from
image sequences. This section sets out what each actually contributes here, and
where it does not transfer.

### Particle Image Velocimetry (PIV) — *transfers as an input, not as the answer*
PIV extracts a dense **velocity field** from intensity-pattern displacement between
frames. On our images that is a real, extractable observable: membrane inflow at a
constricting neck, actin retrograde/assembly flux. **But velocity is kinematics,
not force.** A fast-constricting neck and a slow one differ in kinematics; turning
that into a force requires a constitutive law (drag, tension, active stress). So
PIV is a **feature extractor feeding the physics inverse**, not the physics
recovery itself. We build a PIV-analog motion-field step and are explicit about the
kinematics→force gap it does *not* close.

### Traction Force Microscopy (TFM) — *the method doesn't transfer; its inverse structure does*
TFM infers cell-substrate traction from the displacement of fiducial beads in a gel
of **known stiffness**. Membrane imaging has no bead-seeded substrate and no gel
modulus, so TFM cannot be applied literally. What *does* transfer is its
**inverse-problem shape**: measured displacement + a known constitutive law →
inferred force, regularized against noise. That is exactly curvo's paradigm
(measured geometry + Helfrich/active-stress law → inferred force, with Bayesian
regularization and an identifiability guardrail). We borrow the *shape*, not the
apparatus.

### curvo's Bayesian inverse — *this is the actual physics recovery*
Geometry(t) [+ actin channel, + motion-derived neck inflow] → the validated forward
model (Helfrich bending + tension + active cortical stress) → nested-sampling
posterior over forces → per-structure force with honest identifiability. This is
built, cross-checked (dynesty vs emcee), calibrated on a single-CCP recovery grid
(**active_force_max: cov68|identified = 0.96, rel_bias +2.0%**), guarded against
force-astrology (refuses point estimates where unidentifiable) and, as of this
session, against sampler plateaus (explicit dlogz/maxcall caps). The new work is a
**front end** (many structures, tracked over time) and a **back end** (aggregate
recovered physics into an orchestration model) around this validated core.

## 3. Program shape

```
many-structure time-lapse            [Step 2: field_movie — synthetic, GT tracks]
      |
      v  detect + link
tracks (position, geometry(t))       [Step 3: tracking — validated vs GT]
      |
      v  PIV-analog motion field
per-track kinematics (neck inflow)   [Step 4: motion — kinematics, NOT force]
      |
      v  curvo Bayesian inverse (existing, guarded)
per-structure force + identifiability[Step 5: per_track_recovery — bias/coverage]
      |
      v  aggregate over structures
orchestration model + falsifiable    [Step 6: orchestration — timing/space/stage]
      statement + proposed experiment
```

### Scope, stated plainly
- **Anchor structure = clathrin-coated pits with actin as the active co-player.**
  We have a validated forward+inverse for exactly this. Caveolae and
  actin-as-primary-object would each need their own first-principles physics
  (different mechanics, different constitutive law) — genuine new modules, out of
  scope for this slice and flagged as such.
- **Synthetic-first**, real ingestion via the seam. Every accuracy number comes
  from data where the truth is known.
- **The RL-environment angle is a documented affordance, not a build target.** A
  forward model that renders images from forces + an inverse that scores recovered
  forces against truth *is* a scored simulator; this note records where it plugs
  in without building it out here.
