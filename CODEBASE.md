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

- `analyze()` and the inference defaults currently assume a 24-frame model.
  Supporting arbitrary movie lengths needs an explicit model-context change
  through both full and restricted fits, plus recovery validation.
- `run_nested()` reports `stopped_early`, but downstream mechanism/reporting
  code does not yet propagate it as a reporting gate. That is a separate
  scientific behavior change, not part of the readability refactor.
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
