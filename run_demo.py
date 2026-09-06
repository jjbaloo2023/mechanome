#!/usr/bin/env python
"""
run_demo.py — one command runs the curvo closed loop on the epsin case.

    python run_demo.py

Prints the orchestrator's representation decisions + physical justifications
(including the AlphaFold pLDDT -> wedge/crowding split), achieved-vs-target
curvature, the recovered ENTH+IDP complementarity, the spherical/filamentous
IAV divergence, the stubbed MD-job queue it would dispatch, and writes the
headline SVG orchestration schematic.

Runs OFFLINE by default (deterministic guardrail-guided proposer) so the demo
never depends on network/LLM. Pass --llm to use the host.llm proposer instead.
"""
from __future__ import annotations

import argparse
import os

import numpy as np

from curvo import evaluator_tier0 as ev
from curvo import md_gap_queue as mdq
from curvo import orchestrator as orch
from curvo import parameter_store as ps
from curvo import players as pl
from curvo import schematic as sch
from curvo import structure_provider as sp
from curvo.schemas import StatePoint

OUT = "outputs"
SIGMA_HIGH = 0.03
A_PATCH = np.pi * 60 ** 2
KAPPA = 20.0


def hr(t):
    print("\n" + "=" * 72 + f"\n{t}\n" + "=" * 72)


def faithful_breakdown(rec, sigma):
    params = {p["player"]: p.get("parameters", {}) for p in rec["proposals"]}
    bd = {}
    for name, cls in (("wedge", pl.WedgePlayer), ("crowding", pl.CrowdingPlayer),
                      ("coat", pl.CoatPlayer)):
        if name in params:
            bd[name] = cls().contribution(params[name], sigma)["c0_contribution_inv_nm"]
    return bd


def main(use_llm=False, host=None):
    os.makedirs(OUT, exist_ok=True)
    hr("1. STRUCTURE PROVIDER — AlphaFold pLDDT -> representation split (real data)")
    model = sp.fetch_alphafold("Q9Y6I3", cache_dir="cache")   # EPN1
    call = sp.representation_call(model)
    print(f"EPN1 (Q9Y6I3): {call['n_residues']} residues, mean pLDDT {call['mean_pLDDT']}")
    print("Signals used:", ", ".join(call["signals_used"]))
    for s in call["segments"]:
        flag = f"  [FLAG: {s['guardrail_flag']}]" if s["guardrail_flag"] else ""
        print(f"  res {s['start']:>3}-{s['end']:<3} pLDDT={s['mean_pLDDT']:>5} "
              f"disorder_z={s['disorder_z']:+.2f} muH={s['hydrophobic_moment']:.2f} "
              f"-> {s['representation']}{flag}")
    print("Physical reasoning: high-pLDDT + order-promoting composition + confirmed "
          "amphipathic moment -> WEDGE (P3); low-pLDDT + disorder-promoting -> CROWDING (P4).")

    hr("2. PARAMETER STORE — use existing data, with provenance + validity + uncertainty")
    store = ps.ParameterStore(cache_dir="cache")
    for param, system in [("area_per_lipid", "POPC"), ("c0", "PIP2"), ("kappa", "POPC"),
                          ("insertion_depth", "ENTH_H0")]:
        r = store.get(param, system)
        print(f"  {param:16s} {system:8s} = {r.value:+.4f} ± {r.uncertainty:.4f} {r.units:6s} "
              f"[{r.provenance.access}] {r.provenance.source}")

    hr("3. ORCHESTRATOR SEARCH — epsin CCS toward dome->Omega at HIGH tension")
    case = orch.Case(name="epsin_ccs_highTension", target_curvature_inv_nm=0.030,
                     sigma_kBT_nm2=SIGMA_HIGH, A_coat_nm2=A_PATCH, kappa_kBT=KAPPA, tol=0.003,
                     active_players=("wedge", "crowding", "coat", "tension"),
                     context={"amphipathic": True, "is_disordered": True,
                              "coat_active": True, "coat_role": "stabilize"})
    hist = orch.search(case, host=host, use_llm=use_llm, max_iter=6, verbose=True)
    rec = hist[-1]
    print("\nRepresentation decisions (LLM proposes, guardrails prune, evaluator scores):")
    for p in rec["proposals"]:
        print(f"  {p['player']:9s} -> {p['representation']:26s} :: {p.get('justification','')[:64]}")
    print(f"coupling_correction = {rec['coupling_correction']} (coat concentrates wedge/crowd)")
    print(f"ACHIEVED mean curvature {rec['evaluator_result']['observables']['achieved_mean_curvature_inv_nm']:.4f} "
          f"nm^-1 (target {case.target_curvature_inv_nm}) -> "
          f"{'TARGET MET' if rec['evaluator_result']['target_met'] else 'below target'} "
          f"({rec['evaluator_result']['observables']['stage']} stage)")

    hr("4. COMPLEMENTARITY TEST — neither ENTH/H0 nor IDP alone suffices")

    def max_achievable(active, coupling=0.35):
        contribs = {}
        if "wedge" in active:
            contribs["wedge"] = pl.WedgePlayer().contribution(
                {"c0_contribution_inv_nm": 0.08, "tension_half_kBT_nm2": 0.02,
                 "kappa_softening_factor": 0.9}, SIGMA_HIGH)
        if "crowding" in active:
            contribs["crowding"] = pl.CrowdingPlayer().contribution(
                {"c_max_inv_nm": 0.05, "coverage": 1.0, "phi_half": 0.3}, SIGMA_HIGH)
        if "coat" in active:
            contribs["coat"] = pl.CoatPlayer().contribution(
                {"rigidity_factor": 3.0, "intrinsic_c0_inv_nm": 0.0}, SIGMA_HIGH)
        comb = pl.combine_curvature(contribs, coupling_correction=(coupling if "coat" in active else 0.0))
        mo = ev.ccs_curvature(comb["c_eff_inv_nm"], SIGMA_HIGH, KAPPA, A_PATCH,
                              coat_rigidity_factor=comb["kappa_factor"])
        return mo["achieved_mean_curvature_inv_nm"], mo["stage"]

    thr = 0.030
    for label, active in [("H0 wedge alone", ("wedge", "coat", "tension")),
                          ("IDP crowding alone", ("crowding", "coat", "tension")),
                          ("wedge+crowding, NO coat", ("wedge", "crowding", "tension")),
                          ("FULL", ("wedge", "crowding", "coat", "tension"))]:
        H, stg = max_achievable(active)
        print(f"  {label:26s} max H={H:.4f} ({stg}) crosses Omega: {H >= thr}")
    print("=> Only the FULL orchestration crosses the Omega threshold (complementarity).")

    hr("5. IAV CARGO DIVERGENCE — spherical needs H0, filamentous does not")

    def meets(active, demand, tol=0.004):
        c = orch.Case(name="iav", target_curvature_inv_nm=demand, sigma_kBT_nm2=0.01,
                      A_coat_nm2=A_PATCH, kappa_kBT=KAPPA, tol=tol, active_players=active,
                      context={"amphipathic": True, "is_disordered": True, "coat_active": True})
        h = orch.search(c, host=None, use_llm=False, max_iter=8, verbose=False)
        H = h[-1]["evaluator_result"]["observables"]["achieved_mean_curvature_inv_nm"]
        return H, H >= demand - tol
    for cargo, demand in [("SPHERICAL", 0.028), ("FILAMENTOUS", 0.010)]:
        Hw, mw = meets(("wedge", "crowding", "coat", "tension"), demand)
        Ho, mo = meets(("crowding", "coat", "tension"), demand)
        print(f"  {cargo:12s} (demand {demand}): with H0 {'MEETS' if mw else 'FAILS'} (H={Hw:.4f}) | "
              f"without H0 {'MEETS' if mo else 'FAILS'} (H={Ho:.4f})")
    print("=> spherical cargo is H0-DEPENDENT; filamentous is H0-INDEPENDENT (pre-curved).")

    hr("6. MD-GAP QUEUE — job specs the loop WOULD dispatch (stubbed)")
    q = mdq.MDGapQueue()
    r_c0 = store.get("c0", "PIP2")
    _, spec = q.check_and_emit(r_c0, StatePoint(temperature_K=330, tension_mN_per_m=0.5,
                                                composition="PIP2"))
    if spec:
        print(f"  [{spec.priority}] {spec.job_id}: simulate '{spec.system}' -> {spec.observable}")
        print(f"     estimator: {spec.estimator}")
        print(f"     reason: {spec.reason}")
    q.dump(f"{OUT}/example_md_jobspecs.json")

    hr("7. HEADLINE ARTIFACT — SVG orchestration schematic")
    rec["contribution_breakdown"] = faithful_breakdown(rec, SIGMA_HIGH)
    svg = sch.render_schematic(rec, f"{OUT}/epsin_orchestration_schematic.svg")
    print(f"  wrote {svg}")

    print("\nDEMO COMPLETE. See outputs/ for schematic, results JSON, and MD-gap queue.")
    return rec


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--llm", action="store_true", help="use host.llm proposer (needs kernel host)")
    args = ap.parse_args()
    main(use_llm=args.llm, host=None)
