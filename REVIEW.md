# Adversarial code review

A systematic bug-hunt pass over the codebase, beyond the register/docs cleanup.
Findings are graded by severity; all actionable items were fixed in place and
covered by a test where a regression is possible.

## Fixed

### 1. `channel_link.link_channel_to_gating` rejected valid channel names (medium)
`channels_from_screen()` surfaces a friendly `channel` display name (e.g.
`"TRAAK"`), but the lookup keyed only on the raw screen `protein` name
(`"TRAAK (K2P4.1)"`). Passing the name the function itself returns raised
`KeyError` for TRAAK and TREK-1. It escaped notice because the only test used
MscL, where `protein == channel`. **Fix:** the lookup now accepts either the
protein key or the display name. **Regression test:** `test_structural_screen_
channel_link` now asserts TRAAK resolves and that every screened channel returns
`Po ∈ [0,1]` under both name forms.

### 2. `render_picalm_figure.py` loaded modules from hardcoded artifact paths (medium)
The script loaded `curvo.evaluator_tier0`, `curvo.players`, and
`orchestration_schematic` from absolute `/root/.claude-science/.../artifacts/...`
paths that exist only in this workspace — it would fail on any other checkout.
**Fix:** replaced with normal package imports
(`from curvo import evaluator_tier0`, etc.).

### 3. `render_picalm_figure.py` rendered at import time (medium)
The figure body executed at module top level with no `if __name__` guard, so
`import render_picalm_figure` ran a full render and wrote a PNG as a side effect.
**Fix:** wrapped the body in `render(out_path=...)` with a `__main__` guard, and
factored the ladder computation into `_ladder_rows()`. Importing the module is
now side-effect-free; `python -m ... .render_picalm_figure` still renders.

### 4. Stale test name `test_registry_one_executable_rest_stubs` (low)
The assertions were correct (membrane is GROUNDED-emittable; the four analytic
modules are not), but the name and loop variable called the analytic modules
"stubs" — they have been closed-form analytic-limit-validated forward models
since the mechanome build-out. **Fix:** renamed to
`test_registry_membrane_grounded_analytic_modules_not` with a clarifying comment.

## Checked, no change needed

- **Four analytic forward models** (`forward_tissue/cortex/bond/channel`):
  `self_validate()` passes for all four; the channel gating `Po(σ½)=0.5` identity
  holds exactly.
- **`except Exception` clauses** (emit, schema, modality_adapter,
  perception_benchmark, image_to_force, tether_sted, field_movie): all are
  `# pragma: no cover` dual-import fallbacks (package vs top-level import path),
  not silent error-swallowing.
- **No mutable default arguments** anywhere in the package.
- **numpy 2.x traps** (`np.trapz`, `.ptp()` method, `np.float`): none present.
- **`print()` in library modules** (mechanism, recovery, orchestrator): all
  behind `if verbose:` guards; registry/emit/forward_* prints are inside
  `__main__` demo blocks.
- **`/root/projects/...` paths** in the realdata ingestion modules: intentional
  references to the raw imaging under the host grant, guarded to skip when absent
  (raw imaging is never committed — the firewall).
- **`md_gap_queue.py` "TODO: define estimator"**: a default fallback string for
  the documented, stubbed MD-gap seam, not an unfinished code path.
