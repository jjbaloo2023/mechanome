# Reading and changing Mechanome

Start with the path you want to change. The Python packages at the repository
root have different jobs; importing `mechanome` does not run the entire pipeline.

| Question | Start here | Follow the calls into |
| --- | --- | --- |
| How does a movie become a force report? | `curvo/analyze.py:analyze` | perception -> inverse -> mechanism -> `_report_forces` |
| How is a target curvature reached? | `curvo/orchestrator.py:search` | proposer -> `evaluate_proposal` -> `refine_magnitude` |
| Where do the physical numbers come from? | `curvo/evaluator_tier0.py` | `players.py` for contributions; `constants.py` for units |
| How is uncertainty assessed? | `curvo/inverse.py:identifiability` | posterior width, correlations, prior bounds |
| When is a mechanism supported? | `curvo/mechanism.py:discriminate` | evidence gap -> `_overfit_downgrade` -> experiment |
| How do results become claims? | `mechanome/emit.py` | `schema.py` enforces evidence tiers; `registry.py` describes validation |
| How does the structural screen connect to channels? | `mechanome/channel_link.py` | `structural_screen.full_ranking` and `forward_channel.py` |

## The two main flows

**Movie analysis.** Perception extracts curvature, depth, and uncertainty for
each frame. Frames shallower than the optical resolution are excluded from the
likelihood. The inverse fits mechanical parameters. Mechanism discrimination
compares restricted versions of that same model. Reporting allows a point value
only when identifiability and recovery calibration both pass. A narrow posterior
alone is insufficient.

**Forward search.** A proposer chooses a representation and parameters for each
player. Player validators reject physically invalid choices. The remaining
contributions are combined and passed to the evaluator. Optional bisection tunes
the overall magnitude. The record feeds the next proposal until the target is
met or the iteration budget is exhausted. The LLM cannot supply the evaluated
curvature or energy.

## Research paths

The [research front door](research/README.md) separates current findings from
historical demonstrations. Study code is indexed by scientific question in
[research/INDEX.md](research/INDEX.md); its frozen copies preserve earlier runs.

- Public static geometry: `ingest_smlm_locmofit` selects raw or corrected fields
  with provenance; `smlm_pseudotime` summarizes a population sorted by angle.
  It does not reconstruct a measured pit trajectory. Missing uncertainty is
  `None`. The optional legacy sigma heuristic is explicitly uncalibrated.
- Legacy `smlm_shape_energetics` and `smlm_mechanism` fits require
  `allow_exploratory=True` (CLI: `--allow-exploratory`) before computation.
  A score threshold cannot authorize a decisive biological mechanism verdict.
- `classify_observable` describes inputs and refuses tag-only force permission.
  It is not a global gate on numerical inverse functions.
- The separate `mechanome/research/controller.py` path is
  `acquire_lead -> decide -> start -> finish`. It stores attempts and artifacts
  for an offline persistence demo; it does not run the Codex research agents.

See [reproduction](research/REPRODUCE.md) for the offline test selection and
external-input boundaries. New studies need new designs/results; avoid edits to
frozen evidence while changing production code.

## Development

From the repository root:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[dev,inference,plots]"
.\.venv\Scripts\python.exe -m pytest -q tests/test_pipeline_contracts.py tests/test_players.py tests/test_mechanome_modules.py
.\.venv\Scripts\python.exe -m pytest -q
```

The first test command exercises the decision branches without Bayesian
sampling. The full suite also runs sampling and recovery tests. Some tests need
optional Gymnasium or locally cached microscopy data; their skips should remain
visible. The MDDB adapter test also contacts an external service.

Use descriptive names for workflow state (`posterior`, `resolved_frames`,
`accepted`, `rejections`). Keep conventional symbols and units where they help
read an equation or preserve an existing public API. A helper should name a
decision or repeated operation; avoid adding a class just to pass a dictionary.
Comments should explain assumptions, units, or scientific constraints.

## Boundaries worth keeping visible

- The tether/STED example generates its own radius and reference force using
  published parameters. Its emitter records `input=synthetic`; the membrane
  registry has `built_analytic` status. This is synthetic recovery, not an
  independent force-paired experimental validation. Historical plots retain
  earlier labels and are not current evidence of measured-force agreement.
- `analyze()` and the inference defaults currently assume a 24-frame model.
  Supporting arbitrary movie lengths needs an explicit model-context change
  through both full and restricted fits, plus recovery validation.
- `stopped_early` propagates through force reporting and every restricted fit.
  Capped sampling cannot support point estimates or a decisive verdict.
- `ObservationContext` records input kind, calibration identity, optional
  coverage, and fluorescence-to-force scale. Without an explicit supported
  synthetic context, reports remain exploratory. The existing recovery grid
  uses 128-by-128 images, 2 nm pixels, 18 nm PSF sigma, 220 peak photons,
  coat area pi*60^2 nm^2, the default assembly ramp, and a 60 pN actin scale.
  Declaring those assumptions does not certify measured data.
  The historical force calibration predates the geometry-validity repair and
  is retired. Current analyze() force reports remain intervals. Before enabling
  point estimates, qualify and independently review the updated pipeline's
  recovery grid, binding its source/dependency identities and supported conditions.
- Supply `ObservationContext(coverage=tuple(values))` to use a conditional coat
  coverage trace in both full and restricted fits. Its uncertainty is not
  propagated, so custom coverage has no recovery-calibrated point estimates.
  Extracted coat coverage remains a reported diagnostic until supplied explicitly.
- Extraction quality excludes failed bootstraps, unresolved caps, and inferred
  depth greater than rim radius. All-invalid observations return unsupported.
- Mechanism decisions require a numerical margin over every competitor:
  evidence gap minus twice the sum of reported evidence errors must exceed 2.5.
  This conservative screen is not a formal confidence interval. Ranking entries
  retain evidence errors and sampling status.
- Parameter caches store simulation identity and payload checksum. Unidentified
  legacy caches are ignored. Applicability requires matching composition and
  known thermodynamic conditions; missing metadata is reported as unknown.
- GROUNDED claim construction requires a registered executable model, finite
  values, nonnegative uncertainty, evidence, and structured `input_kind` and
  `validation` fields compatible with the registry. These are consistency checks;
  they cannot verify that a caller's scientific assertions are true.
- The structural screen is a frozen research result. Its adapter verifies the
  saved hash; ordinary imports and channel lookups do not rerun the screen or
  fetch structures. Do not regenerate frozen results during a refactor.
- `validation/realdata` and figure scripts still contain abbreviated research
  code and dataset-specific paths. Refactor those by experiment, with its input
  data and expected results available.

See RESEARCH.md and the manuscript for the scientific rationale, results, and
reproduction procedures. This guide describes the code's current control flow.

The runtime contains implemented paths. Unused proposal dataclasses, the SBI
placeholder, and the FreeDTS placeholder were removed; they are not compatibility
APIs. Parameter provenance and the MD-gap queue remain in use. Import package
modules normally after installation; obsolete flat-layout fallbacks are gone.
