"""
curvo.orchestrator — the search loop (the bitter-lesson engine).

propose -> prune (guardrails) -> resolve params -> EVALUATE (ground truth)
-> read -> revise (NL post-mortem) -> repeat.

The LLM (host.llm) is a *search operator with priors*: it proposes which
representation + magnitude to try for each player and writes a post-mortem that
steers the next proposal. It NEVER produces a curvature or energy number — those
come only from evaluator_tier0. Guardrails (players.validate) reject physically
impossible proposals before any evaluation; a rejected proposal is logged and
fed back so the LLM learns the constraint.

An offline fallback proposer (deterministic, guardrail-guided) runs when host.llm
is unavailable, so the loop is demonstrable without network.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass

from . import evaluator_tier0 as ev
from . import players as P
from .schemas import (EvaluatorResult, OrchestrationRecord, PlayerProposal,
                      RepresentationDecision)

# The proposer's structured-output schema (tool-forced).
PROPOSAL_TOOL = {
    "name": "propose_orchestration",
    "description": "Propose a representation and parameters for each active player.",
    "input_schema": {
        "type": "object",
        "properties": {
            "players": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "player": {"type": "string",
                                   "enum": ["wedge", "crowding", "coat", "tension"]},
                        "representation": {"type": "string"},
                        "parameters": {"type": "object",
                                       "description": "numeric params for this player's contribution()"},
                        "justification": {"type": "string"},
                    },
                    "required": ["player", "representation", "parameters", "justification"],
                },
            },
            "coupling_correction": {"type": "number",
                                    "description": "0 if additive; >0 for known-coupled synergy (wedge+coat)"},
            "reasoning": {"type": "string", "description": "overall physical rationale"},
        },
        "required": ["players", "coupling_correction", "reasoning"],
    },
}


@dataclass
class Case:
    """A target the loop searches against."""
    name: str
    target_curvature_inv_nm: float
    sigma_kBT_nm2: float
    A_coat_nm2: float
    kappa_kBT: float
    tol: float = 0.004
    active_players: tuple = ("wedge", "crowding", "coat", "tension")
    context: dict = None       # amphipathic flags etc. from structure_provider
    lam_kBT_nm: float = 0.0


def _system_prompt(case: Case) -> str:
    return (
        "You are the representation-search operator for a membrane-curvature "
        "orchestration pipeline. You PROPOSE which physical representation and "
        "which numeric parameters to use for each player; a separate analytic "
        "evaluator (Helfrich energetics) is the ONLY source of curvature/energy "
        "numbers. Never state a curvature or energy value yourself.\n\n"
        "Players and their PHYSICALLY VALID representations:\n"
        "- wedge (amphipathic helix, ENTH/H0): use 'c0_plus_kappa_softening'. It is "
        "tension-gated (curvature sensor). Params: c0_contribution_inv_nm (0..0.08), "
        "tension_half_kBT_nm2, kappa_softening_factor. NOT anisotropic, NOT a scaffold.\n"
        "- crowding (disordered IDP tail): use 'saturating_surface_pressure'. Entropic, "
        "saturates. Params: c_max_inv_nm (0..0.05), coverage (0..1), phi_half. NEVER a fixed c0.\n"
        "- coat (AP2/clathrin): use 'rigidity_area_constraint'. Params: rigidity_factor (1..6), "
        "intrinsic_c0_inv_nm (~0 unless a mature curved lattice). Stiffens, localizes, does NOT "
        "by itself bend a flat membrane.\n"
        "- tension: 'constant_tension_frame', sigma fixed by the case.\n\n"
        "Known coupling: wedge+coat and crowding+coat are >additive (the coat concentrates "
        "the wedge/crowd) — set coupling_correction>0 (~0.1-0.4) when both are active; else 0.\n\n"
        f"TARGET for case '{case.name}': achieve mean curvature "
        f"{case.target_curvature_inv_nm:.4f} nm^-1 at tension sigma={case.sigma_kBT_nm2} "
        f"kBT/nm^2 (coat patch area {case.A_coat_nm2:.0f} nm^2, kappa {case.kappa_kBT} kBT). "
        "Reach dome or Omega stage. Higher tension flattens the wedge — you may need more "
        "crowding or coat rigidity to compensate."
    )


def _offline_proposer(case: Case, history: list) -> dict:
    """Deterministic guardrail-guided proposer used when host.llm is unavailable.

    Implements a simple, physically-sensible hill-climb: start from priors,
    then nudge the parameter that most closes the gap based on the last result.
    """
    # priors
    c0_wedge, cov, rf, coup = 0.03, 0.5, 2.0, 0.25
    if history:
        last = history[-1]
        ach = last["evaluator_result"]["observables"]["achieved_mean_curvature_inv_nm"]
        gap = case.target_curvature_inv_nm - ach
        step = 3.0 * gap                      # proportional control
        # read back last params
        lp = {p["player"]: p for p in last["proposals"]}
        c0_wedge = float(lp.get("wedge", {}).get("parameters", {}).get("c0_contribution_inv_nm", 0.03))
        cov = float(lp.get("crowding", {}).get("parameters", {}).get("coverage", 0.5))
        rf = float(lp.get("coat", {}).get("parameters", {}).get("rigidity_factor", 2.0))
        coup = float(last.get("coupling_correction", 0.25))
        # distribute the nudge
        c0_wedge = min(0.08, max(0.0, c0_wedge + 0.5 * step))
        cov = min(1.0, max(0.0, cov + 4.0 * step))
        coup = min(0.5, max(0.0, coup + 2.0 * step))
    players = []
    if "wedge" in case.active_players:
        players.append({"player": "wedge", "representation": "c0_plus_kappa_softening",
                        "parameters": {"c0_contribution_inv_nm": round(c0_wedge, 4),
                                       "tension_half_kBT_nm2": 0.02,
                                       "kappa_softening_factor": 0.9},
                        "justification": "amphipathic H0 wedge, tension-gated (offline prior)"})
    if "crowding" in case.active_players:
        players.append({"player": "crowding", "representation": "saturating_surface_pressure",
                        "parameters": {"c_max_inv_nm": 0.04, "coverage": round(cov, 3),
                                       "phi_half": 0.3},
                        "justification": "disordered IDP saturating crowding (offline prior)"})
    if "coat" in case.active_players:
        players.append({"player": "coat", "representation": "rigidity_area_constraint",
                        "parameters": {"rigidity_factor": round(rf, 3),
                                       "intrinsic_c0_inv_nm": 0.0},
                        "justification": "clathrin coat rigidity/localization (offline prior)"})
    if "tension" in case.active_players:
        players.append({"player": "tension", "representation": "constant_tension_frame",
                        "parameters": {"sigma_kBT_nm2": case.sigma_kBT_nm2},
                        "justification": "constant-tension frame (case antagonist)"})
    return {"players": players, "coupling_correction": round(coup, 3),
            "reasoning": "offline deterministic guardrail-guided hill-climb"}


def _llm_proposer(host, case: Case, history: list):
    """host.llm proposer with tool-forced structured output."""
    if not history:
        user = ("Propose an initial orchestration to reach the target. The combined "
                "effective spontaneous curvature c_eff maps roughly to achieved mean "
                "curvature H via H ~ c_eff/2 at low tension (saturating near the "
                "hemisphere). Aim for c_eff ~ 2*target initially.")
    else:
        last = history[-1]
        obs = last["evaluator_result"]["observables"]
        c_eff_last = last["combined"]["c_eff_inv_nm"]
        target = case.target_curvature_inv_nm
        # give the proposer explicit proportional guidance (it still chooses how to distribute)
        c_eff_needed = 2.0 * target if obs["stage"] != "Omega" else c_eff_last * (target / max(obs["achieved_mean_curvature_inv_nm"], 1e-6))
        user = (
            f"Previous proposal used combined c_eff={c_eff_last:.4f} nm^-1 and the evaluator "
            f"returned mean curvature {obs['achieved_mean_curvature_inv_nm']:.4f} nm^-1 "
            f"(stage: {obs['stage']}, |gap|={last['evaluator_result']['objective_value']:.4f}). "
            f"Target is {target:.4f}. Note: the curvature SATURATES near the hemisphere, so "
            f"pushing c_eff far above ~{2*target:.3f} does not help — it just pins the stage at "
            f"Omega. To hit the target you want combined c_eff ≈ {c_eff_needed:.4f} nm^-1. "
            f"Adjust the per-player parameters (and coupling_correction) so the players' "
            f"contributions SUM (with coupling) to about that c_eff. Make a SMALL proportional "
            f"adjustment from the last proposal; do not overshoot. "
            + ("Rejected last round (fix these): " + json.dumps(last.get("rejections", [])) + ". "
               if last.get("rejections") else "")
        )
    r = host.llm(prompt=user, system=_system_prompt(case),
                 model=host.reasoning_model(),
                 tools=[PROPOSAL_TOOL],
                 tool_choice={"type": "tool", "name": "propose_orchestration"},
                 max_tokens=1200)
    if r.get("tool_use"):
        inp = r["tool_use"]["input"]
        return inp, inp.get("reasoning", "")
    raise RuntimeError("LLM proposer returned no tool_use")


def evaluate_proposal(case: Case, proposal: dict):
    """Prune with guardrails, resolve contributions, evaluate (ground truth)."""
    rejections = []
    contribs = {}
    accepted = []
    for pl in proposal["players"]:
        # defensive: skip malformed entries (LLM may occasionally emit a bad shape)
        if not isinstance(pl, dict) or "player" not in pl:
            rejections.append({"player": str(pl)[:40], "reason": "malformed proposal entry"})
            continue
        name = pl["player"]
        if name not in P.PLAYERS:
            rejections.append({"player": name, "reason": "unknown player"})
            continue
        pl.setdefault("parameters", {})
        pl.setdefault("representation", "")
        player = P.PLAYERS[name]
        ok, reason = player.validate(pl["representation"], pl["parameters"], case.context or {})
        if not ok:
            rejections.append({"player": name, "representation": pl["representation"],
                               "reason": reason})
            continue
        contribs[name] = player.contribution(pl["parameters"], case.sigma_kBT_nm2)
        accepted.append(pl)
    # combine (synergy/antagonism guardrail)
    combined = P.combine_curvature({k: v for k, v in contribs.items() if k != "tension"},
                                   coupling_correction=proposal.get("coupling_correction", 0.0))
    c_eff = combined["c_eff_inv_nm"]
    kappa_factor = combined["kappa_factor"]
    # evaluate
    model_out = ev.ccs_curvature(
        c_eff_inv_nm=c_eff, sigma_kBT_nm2=case.sigma_kBT_nm2, kappa_kBT=case.kappa_kBT,
        A_coat_nm2=case.A_coat_nm2, coat_rigidity_factor=kappa_factor,
        lam_kBT_nm=case.lam_kBT_nm)
    result = ev.score_ccs(model_out, case.target_curvature_inv_nm, tol=case.tol)
    return result, model_out, accepted, rejections, combined


def _compose_trace(proposal: dict, text: str = "") -> str:
    """Build the human-readable reasoning trace from the proposal's own fields.
    (Forced tool-use suppresses free-text, so we assemble the physical
    justifications the LLM gave per player plus its overall reasoning.)"""
    parts = []
    if proposal.get("reasoning"):
        parts.append(proposal["reasoning"])
    for pl in proposal.get("players", []):
        if isinstance(pl, dict) and pl.get("justification"):
            parts.append(f"[{pl.get('player')}→{pl.get('representation')}] {pl['justification']}")
    if proposal.get("coupling_correction"):
        parts.append(f"coupling_correction={proposal['coupling_correction']} "
                     "(coat concentrates wedge/crowd → >additive synergy)")
    if text:
        parts.append(text)
    return " || ".join(parts)


def refine_magnitude(case: Case, proposal: dict, n_bisect: int = 22):
    """Given the LLM's REPRESENTATION choices, find the overall magnitude scale
    that best hits the target — cheap bisection on the evaluator (ground truth).

    This is the bitter-lesson division of labour: the LLM does the discrete
    representation/structure search + interpretation; a cheap deterministic
    optimizer nails the continuous magnitude. The scale multiplies the tunable
    curvature-driving params (wedge c0, crowding coverage) uniformly, so the
    LLM's chosen SPLIT between players is preserved — only the overall drive is
    tuned. Guardrails still clamp each scaled value to its plausibility range.
    """
    import copy

    def scaled_proposal(scale):
        pp = copy.deepcopy(proposal)
        for pl in pp["players"]:
            if not isinstance(pl, dict):
                continue
            pr = pl.setdefault("parameters", {})
            if pl.get("player") == "wedge" and "c0_contribution_inv_nm" in pr:
                pr["c0_contribution_inv_nm"] = min(0.08, pr["c0_contribution_inv_nm"] * scale)
            if pl.get("player") == "crowding" and "coverage" in pr:
                pr["coverage"] = min(1.0, pr["coverage"] * scale)
        return pp

    lo, hi = 0.0, 4.0
    best = None
    for _ in range(n_bisect):
        mid = 0.5 * (lo + hi)
        res, mo, acc, rej, comb = evaluate_proposal(case, scaled_proposal(mid))
        ach = res.observables["achieved_mean_curvature_inv_nm"]
        if best is None or res.objective_value < best[0]:
            best = (res.objective_value, mid, res, mo, acc, rej, comb)
        if ach < case.target_curvature_inv_nm:
            lo = mid
        else:
            hi = mid
    _, scale, res, mo, acc, rej, comb = best
    return scaled_proposal(scale), res, mo, acc, rej, comb, scale


def search(case: Case, host=None, max_iter: int = 8, use_llm: bool = True,
           verbose: bool = True, refine: bool = True) -> list:
    """Run the propose->evaluate->revise loop. Returns list of OrchestrationRecords."""
    history = []
    for it in range(max_iter):
        # PROPOSE
        text = ""
        if use_llm and host is not None:
            try:
                proposal, text = _llm_proposer(host, case, history)
            except Exception as e:
                proposal = _offline_proposer(case, history)
                text = f"[offline fallback: {type(e).__name__}]"
        else:
            proposal = _offline_proposer(case, history)
        # EVALUATE (ground truth); optionally solve magnitude on the LLM's chosen reps
        if refine:
            proposal, result, model_out, accepted, rejections, combined, scale = \
                refine_magnitude(case, proposal)
        else:
            result, model_out, accepted, rejections, combined = evaluate_proposal(case, proposal)
        # build record
        rec = OrchestrationRecord(
            case=case.name, iteration=it,
            target={"observable": "mean_curvature_inv_nm",
                    "value": case.target_curvature_inv_nm, "tolerance": case.tol},
            proposals=accepted,
            evaluator_result=result.to_dict(),
            reasoning_trace=_compose_trace(proposal, text),
        ).to_dict()
        rec["rejections"] = rejections
        rec["coupling_correction"] = proposal.get("coupling_correction", 0.0)
        rec["combined"] = combined
        rec["model_out"] = model_out
        history.append(rec)
        if verbose:
            obs = result.observables
            print(f"  iter {it}: c_eff={combined['c_eff_inv_nm']:.4f} -> "
                  f"H={obs['achieved_mean_curvature_inv_nm']:.4f} ({obs['stage']}) "
                  f"|gap|={result.objective_value:.4f} "
                  f"{'MET' if result.target_met else ''} "
                  f"{('rej:'+str(len(rejections))) if rejections else ''}")
        if result.target_met:
            break
    return history
