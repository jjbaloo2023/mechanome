# Mechanome

Mechanome models cell mechanics. Its membrane engine, `curvo`, searches for
protein contributions that meet a curvature target and infers mechanical
parameters from microscopy movies. The `mechanome` package adds claim schemas,
forward models at other scales, and a structure-based protein screen.

This is research software for computational mechanobiologists developing and
testing model-based hypotheses. It combines representation search, observation
models, and explicit inference limits in one workspace. It is not a calibrated
force-measurement tool for arbitrary microscopy movies.

## Start here

- [Research findings](research/FINDINGS.md): supported conclusions and evidence limits.
- [Research overview](research/OVERVIEW.md): scientific story and persistent workflow.
- [Codebase guide](CODEBASE.md): call paths, reporting rules, and development.
- [Methods and evidence guide](RESEARCH.md): models, units, validation scope, and reproduction.
- [Manuscript](MANUSCRIPT.md): historical paper draft; see the campaign for current claim boundaries.
- [Pipeline architecture](research/PIPELINE_ARCHITECTURE.md): agents, persistent operation, steering and research progress.
- [Research campaign](research/README.md): reviewed findings, study index, reproducibility, and next decisions.

The current public-data campaign supports descriptive geometry and conditional
model results. It has not established a biological mechanism or calibrated force
from the public cap-fit tables. Start with [the findings](research/FINDINGS.md).

## Install

Requires Python 3.10 or newer. From the repository root:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[dev,inference,plots]"
```

For a minimal installation, use `pip install -e .`. The `inference` extra adds
Bayesian samplers; `plots` adds figure rendering; `dev` adds test/style tools.
Pandas is limited to 2.x because the frozen ranking's integrity check depends
on that series' CSV parsing and serialization. These dependency ranges are
installation constraints, not a fully frozen scientific environment.

## Run

After installation, this complete Python example runs offline and writes no
result files. It searches a simplified membrane model for a synthetic target:

```python
from curvo.orchestrator import Case, search

case = Case(
    name="synthetic target",
    target_curvature_inv_nm=0.02,
    sigma_kBT_nm2=0.02,
    A_coat_nm2=11310.0,
    kappa_kBT=20.0,
)
result = search(case, use_llm=False, verbose=False)[-1]["evaluator_result"]
print(round(result["observables"]["achieved_mean_curvature_inv_nm"], 4))
print(result["target_met"])
```

Expected output is approximately `0.0166` nm^-1 and `True`: the model reaches
the requested curvature within the default tolerance of `0.004` nm^-1. This
shows a feasible parameter combination, not a unique protein mechanism.

For the structure-backed demonstration, run `python run_demo.py`. It uses a
deterministic proposer by default, may fetch external inputs on a fresh cache,
and writes results to `outputs/`.

The inverse entry point is `curvo.analyze.analyze(movie, question)`. It accepts
24-frame side-view movies in `[frame, channel, height, width]` order. Unknown
or experimental observation contexts return exploratory intervals, without
force point estimates or decisive mechanism claims. No valid resolved geometry
returns `analysis_status="unsupported"` without running a sampler.

Synthetic analyses can explicitly declare the renderer-specific context:

```python
from curvo.inverse import ObservationContext

context = ObservationContext(
    input_kind="synthetic", calibration_id="synthetic_renderer_v1"
)
# analyze(movie, question, context=context)
```

That declaration applies only to the documented synthetic conditions; it does
not certify an experiment. The geometry-validity repair retires the old force
calibration: point estimates remain disabled pending a reviewed recovery grid
for the updated pipeline. Changed imaging conditions, coat area, coverage, or
actin-force scale also remain exploratory. See [CODEBASE.md](CODEBASE.md) for the
conditions and [RESEARCH.md](RESEARCH.md) for scientific limits.

## Check changes

For the reviewed research checkpoint, use the bounded offline selection in
[research/REPRODUCE.md](research/REPRODUCE.md). General development checks:

```powershell
.\.venv\Scripts\python.exe -m pytest -q tests/test_pipeline_contracts.py tests/test_imports.py tests/test_players.py tests/test_mechanome_modules.py tests/test_parameter_store.py tests/test_scientific_guards.py
.\.venv\Scripts\python.exe -m pytest -q
```

The first command checks decision branches and integration boundaries. The full
suite includes expensive sampling and image benchmarks; some tests require
cached microscopy data or optional Gymnasium.

## Layout

| Path | Purpose |
| --- | --- |
| `curvo/` | Membrane physics, search, perception, and inference |
| `mechanome/` | Claim schemas, other mechanical scales, structural screen |
| `validation/` | Validation programs and dataset-specific experiments |
| `tests/` | Automated checks |
| `research/` | Reviewed findings, designs, evidence, source records and campaign log |
| `figures/`, `outputs/`, `presentation/` | Saved scientific artifacts |
| `rl/` | Optional reinforcement-learning experiment |
| `cache/` | Reusable downloaded inputs |

Scientific artifacts are retained for reproducibility. Duplicate generated
figures are ignored; documentation uses the canonical copies in `figures/`.

## Contribute, cite, and release

Report problems or seek support through [GitHub issues](https://github.com/jjbaloo2023/mechanome/issues).
Include the commit, environment, minimal input, command, and expected versus
observed behavior. For contributions, open a focused pull request and follow
[CODEBASE.md](CODEBASE.md). Keep frozen study artifacts unchanged; new scientific
results need separate outputs, assumptions, provenance, and validation.

The code uses the [MIT license](LICENSE); third-party inputs retain their source
terms. Cite the software using [CITATION.cff](CITATION.cff), together with the
exact commit used. The declared package version alone does not identify a
reproducible snapshot. For a release, update package and citation versions
together, pass the documented checks, and tag the reviewed commit. An archived
release DOI should be added to the citation metadata when one is available.
