# Mechanome

Mechanome models cell mechanics. Its membrane engine, `curvo`, searches for
protein contributions that meet a curvature target and infers mechanical
parameters from microscopy movies. The `mechanome` package adds claim schemas,
forward models at other scales, and a structure-based protein screen.

## Start here

- [Codebase guide](CODEBASE.md): call paths, reporting rules, and development.
- [Scientific reference](RESEARCH.md): equations, validation, results, and reproduction.
- [Manuscript](MANUSCRIPT.md): the paper draft.

## Install

Requires Python 3.10 or newer. From the repository root:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[dev,inference,plots]"
```

For a minimal installation, use `pip install -e .`. The `inference` extra adds
Bayesian samplers; `plots` adds figure rendering; `dev` adds test/style tools.

## Run

```powershell
.\.venv\Scripts\python.exe run_demo.py
```

The demo uses the deterministic proposer by default. Protein structures and
parameter adapters may need network access on a fresh cache. It writes results
to `outputs/` when run; importing modules does not create that directory.

The two main entry points are:

```python
from curvo.analyze import analyze
from curvo.orchestrator import search

# analyze(movie, question): pixels -> geometry -> posterior -> mechanism -> report
# search(case): propose -> validate -> evaluate -> refine -> record
```

Movies use `[frame, channel, height, width]` order. The current inference model
defaults to 24 frames. A force gets a point estimate only when identifiability
and recovery calibration both pass. See the codebase guide for limitations.

## Check changes

```powershell
.\.venv\Scripts\python.exe -m pytest -q tests/test_pipeline_contracts.py tests/test_imports.py tests/test_players.py tests/test_mechanome_modules.py
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
| `figures/`, `outputs/`, `presentation/` | Saved scientific artifacts |
| `rl/` | Optional reinforcement-learning experiment |
| `cache/` | Reusable downloaded inputs |

Scientific artifacts are retained for reproducibility. Duplicate generated
figures are ignored; documentation uses the canonical copies in `figures/`.
