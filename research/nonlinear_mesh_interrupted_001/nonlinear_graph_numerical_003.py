#!/usr/bin/env python3
"""Queued attempt-3 implementation; import-safe and not executed by preflight."""
from __future__ import annotations

import hashlib, json, platform, sys, traceback
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import scipy
from scipy.integrate import quad, solve_bvp
from scipy.interpolate import PPoly
from scipy.special import i1, k1

HERE = Path(__file__).resolve().parent
DESIGN, EXECUTION = HERE / "nonlinear_numerical_design.json", HERE / "nonlinear_numerical_execution_003.json"
RESULTS, PROFILES = HERE / "nonlinear_numerical_results_003.json", HERE / "nonlinear_numerical_profiles_003.npz"
MAX_SOLVES, SOURCE_POINTS, POLE_TOL = 26, 4097, 1e-10
CONFIGS = ((8, 1e-6), (8, 1e-8), (12, 1e-8))

def utcnow(): return datetime.now(timezone.utc).isoformat()
def sha256(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def bump(r):
    r = np.asarray(r); out = np.zeros_like(r, dtype=float); m = r < 1.
    q = r[m]; out[m] = np.exp(1.-1./(1.-q*q)); return out

def c_over_r_prime(r, epsilon):
    r = np.asarray(r); out = np.zeros_like(r, dtype=float); m = r < 1.
    q = r[m]; out[m] = -2.*epsilon*bump(q)/(1.-q*q)**2; return out

def source(r, epsilon): return epsilon*bump(r)
def label(kind, sigma, epsilon, radius, tol):
    return f"{kind}_s{sigma}_{'zero' if epsilon == 0 else f'e{epsilon:g}'}_R{radius:g}_tol{tol:.0e}"

def initial_mesh(radius):
    """Reviewed fixed mesh: 1921 source nodes + 3840 exterior nodes."""
    return np.r_[np.linspace(0., 1., 1921), np.linspace(1., radius, 3841)[1:]]

def make_rhs(kind, sigma, epsilon):
    if kind == "linear":
        return lambda r, y: np.vstack((y[1], c_over_r_prime(r, epsilon)+sigma*y[0]))
    if kind not in ("nonlinear", "zero"): raise ValueError(f"unsupported kind {kind}")
    def rhs(r, y):
        v, w = y; c = source(r, epsilon)
        return np.vstack((w, c_over_r_prime(r, epsilon)+(sigma*v-.5*v*(2*v+r*w-c)*(r*w+c))/(1.-(r*v)**2)))
    return rhs

def bvp_solution(kind, sigma, epsilon, radius, tol, initial=None):
    mesh = initial_mesh(radius)
    if initial is None:
        y = np.empty((2, mesh.size)); y[0] = epsilon*np.exp(-mesh*mesh)*(1-(mesh/radius)**2); y[1] = np.gradient(y[0], mesh); y[1, 0] = 0.
    else:
        y = initial(mesh); y[1, 0] = 0.
    return solve_bvp(make_rhs(kind, sigma, epsilon), lambda ya, yb: np.array([ya[1], yb[0]]), mesh, y,
                     tol=tol, max_nodes=20000, S=np.array([[0., 0.], [0., -3.]]), verbose=0)

def save_state(state, profiles, results_path=RESULTS, profiles_path=PROFILES):
    state["updated_at_utc"] = utcnow(); results_path.write_text(json.dumps(state, indent=2, sort_keys=True)+"\n", encoding="utf-8"); np.savez_compressed(profiles_path, **profiles)

def store_ppoly(profiles, key, pp):
    profiles[f"{key}__x"], profiles[f"{key}__c"], profiles[f"{key}__axis"] = pp.x.copy(), pp.c.copy(), np.array([pp.axis], dtype=int)

def load_ppoly(profiles, key):
    return PPoly.construct_fast(profiles[f"{key}__c"], profiles[f"{key}__x"], axis=int(profiles[f"{key}__axis"][0]))

def residual_grid(pp, radius):
    """Original check grid plus 17 interior points/interval and knot sides."""
    original = np.r_[0., np.geomspace(1e-10, .999999, 6000), np.linspace(1., radius, 6001)]
    knots = pp.x
    interiors = [np.linspace(a, b, 19)[1:-1] for a, b in zip(knots[:-1], knots[1:])]
    sides = np.r_[np.nextafter(knots[1:-1], -np.inf), np.nextafter(knots[1:-1], np.inf)]
    return np.unique(np.r_[original, *interiors, sides]), len(original), 17*(len(knots)-1), 2*(len(knots)-2)

def exact_checks(pp, sigma, epsilon, radius, nonlinear_q):
    """Physical residual from actual v spline derivatives, never RHS substitution."""
    grid, old_count, interval_count, side_count = residual_grid(pp, radius)
    value, stored_w = pp(grid), pp(grid)[1]
    v, vp, vpp = value[0], pp(grid, 1)[0], pp(grid, 2)[0]
    c, cp_r = source(grid, epsilon), c_over_r_prime(grid, epsilon)
    u, up = grid*v, v+grid*vp; t, tp = 2*v+grid*vp-c, 3*vp+grid*vpp-grid*cp_r
    q = -(1-u*u)*tp-t*u*up+(.5*t*t+sigma)*u
    v0, vp0, w0, vpp0 = float(pp(0.)[0]), float(pp(0., 1)[0]), float(pp(0.)[1]), float(pp(0., 2)[0])
    regular = abs(vp0) <= POLE_TOL and abs(w0) <= POLE_TOL
    if regular:
        t0 = 2*v0-epsilon; pole_q = -4*vpp0-2*epsilon-t0*v0*v0+(.5*t0*t0+sigma)*v0
        q_over_r = np.r_[pole_q, q[1:]/grid[1:]]
    else:
        pole_q, q_over_r = float("nan"), np.r_[np.inf, q[1:]/grid[1:]]
    J = 1./np.sqrt(1.-u*u); p, Jp = u*J, u*up*J**3
    original_q = -(tp*J+t*Jp)/J**3+(.5*t*t+sigma)*p/J
    pole = 4*vpp0-(-2*epsilon+sigma*v0-.5*v0*(2*v0-epsilon)*epsilon)
    return {"residual_grid_count": int(grid.size), "original_grid_count": old_count, "interval_interior_point_count": interval_count,
            "knot_side_point_count": side_count, "final_intervals": int(len(pp.x)-1), "nonlinear_Q_acceptance_applicable": nonlinear_q,
            "actual_vprime0": vp0, "stored_w0": w0, "pole_regularity_tolerance": POLE_TOL, "pole_regularity_pass": regular,
            "pole_Q_over_r_limit": pole_q, "pole_relation_residual": pole, "max_abs_u": float(np.max(abs(u))),
            "boundary_vR": float(pp(radius)[0]), "boundary_w0": w0, "max_abs_spline_vprime_minus_stored_w": float(np.max(abs(vp-stored_w))),
            "max_abs_Q": float(np.max(abs(q))), "max_abs_Q_over_r": float(np.max(abs(q_over_r))),
            "max_abs_Q_over_r_div_epsilon": None if epsilon == 0 else float(np.max(abs(q_over_r))/epsilon),
            "max_abs_original_flux_minus_normalized_off_pole": float(np.max(abs(original_q[1:]-q[1:]))), "origin_v": v0, "origin_v_second": vpp0}

def solve_record(state, profiles, kind, sigma, epsilon, radius, tol, initial=None, solver=bvp_solution, save=save_state):
    if len(state["solves"]) >= MAX_SOLVES: raise RuntimeError("26-solve ceiling reached")
    key = label(kind, sigma, epsilon, radius, tol)
    rec = {"index": len(state["solves"])+1, "label": key, "kind": kind, "sigma": sigma, "epsilon": epsilon, "R": radius, "tol": tol, "started_at_utc": utcnow(), "outcome": "started"}
    state["solves"].append(rec); save(state, profiles)
    try: result = solver(kind, sigma, epsilon, radius, tol, initial)
    except Exception:
        rec.update({"outcome":"solver_call_exception_stop", "failure_traceback":traceback.format_exc()}); state["status"]="failed_solver_call_exception"; save(state, profiles); raise
    rec.update({"outcome":"solver_returned", "solver_returned":True, "solver_status":int(result.status), "solver_message":str(result.message), "nodes":int(result.x.size), "niter":int(result.niter), "finished_at_utc":utcnow()}); save(state, profiles)
    if result.status != 0 or result.x.size > 20000:
        rec["outcome"]="solver_status_failure_stop"; state["status"]="failed_solver_status"; save(state, profiles); raise RuntimeError(rec["solver_message"])
    try:
        store_ppoly(profiles, key, result.sol); rec["checks"] = exact_checks(result.sol, sigma, epsilon, radius, kind == "nonlinear"); rec["outcome"]="completed"; save(state, profiles)
    except Exception:
        rec.update({"outcome":"postprocessing_failure_stop", "failure_traceback":traceback.format_exc()}); state["status"]="failed_postprocessing_after_solver_return"; save(state, profiles); raise
    return key, result.sol

def relative(a, b): return float(np.max(abs(a-b))/max(float(np.max(abs(b))), 1e-12))

def bessel_a(r, sigma):
    lam=np.sqrt(sigma)
    def force(s): return 0. if s <= 0 or s >= 1 else 2*s*float(bump(np.array([s]))[0])/(1-s*s)**2
    def one(x):
        if x == 0: return lam/2*quad(lambda s:k1(lam*s)*force(s)*s,0,1,epsabs=2e-12,epsrel=2e-12,limit=300)[0]
        first=quad(lambda s:i1(lam*s)*force(s)*s,0,min(x,1),epsabs=2e-12,epsrel=2e-12,limit=300)[0]; second=0 if x>=1 else quad(lambda s:k1(lam*s)*force(s)*s,x,1,epsabs=2e-12,epsrel=2e-12,limit=300)[0]
        return k1(lam*x)*first+i1(lam*x)*second
    a=np.array([one(float(x)) for x in r]); out=np.empty_like(a); out[0]=one(0.); out[1:]=a[1:]/r[1:]; return out

def optional_k(gates, profiles, grid):
    if not all(gates.values()): return {"run":False, "reason":"suppressed because at least one required gate failed"}
    values={}
    for eps in (.025,.05,.1):
        v1=load_ppoly(profiles,label("nonlinear",1,eps,12,1e-8))(grid)[0]; v2=load_ppoly(profiles,label("nonlinear",2,eps,12,1e-8))(grid)[0]
        u1,u2=grid*v1,grid*v2; g=source(grid,eps); gp=grid*c_over_r_prime(grid,eps)
        k=(u1-u2)*(-(u1+u2)*(g+grid*gp)+grid*(g*g+.5*g*g)); profiles[f"K_e{eps:g}__source_grid"]=k
        values[f"epsilon_{eps:g}"]={"max_abs_K":float(np.max(abs(k))), "max_abs_K_over_epsilon_cubed":float(np.max(abs(k))/eps**3)}
    return {"run":True,"values":values}

def finalize(state, profiles):
    grid=np.linspace(0,1,SOURCE_POINTS); nl={}; linear={}; ordering={}; zero={}
    for eps in (.025,.05,.1):
        for sig in (1,2):
            co=load_ppoly(profiles,label("nonlinear",sig,eps,8,1e-6))(grid)[0]; f8=load_ppoly(profiles,label("nonlinear",sig,eps,8,1e-8))(grid)[0]; f12=load_ppoly(profiles,label("nonlinear",sig,eps,12,1e-8))(grid)[0]
            nl[f"epsilon_{eps:g}_sigma_{sig}"]={"tolerance_relative_change_R8":relative(co,f8),"reservoir_relative_change_R8_to_R12":relative(f8,f12),"absolute_profile_uncertainty_E":float(max(np.max(abs(co-f8)),np.max(abs(f8-f12))))}
        v1=load_ppoly(profiles,label("nonlinear",1,eps,12,1e-8))(grid)[0]; v2=load_ppoly(profiles,label("nonlinear",2,eps,12,1e-8))(grid)[0]; e1=nl[f"epsilon_{eps:g}_sigma_1"]["absolute_profile_uncertainty_E"]; e2=nl[f"epsilon_{eps:g}_sigma_2"]["absolute_profile_uncertainty_E"]
        ordering[f"epsilon_{eps:g}"]={"min_v2":float(np.min(v2)),"min_v1_minus_v2":float(np.min(v1-v2)),"threshold_v2":10*e2,"threshold_difference":10*(e1+e2)}
    for sig in (1,2):
        ref=bessel_a(grid,sig); profiles[f"bessel_reference_sigma_{sig}__source_grid"]=ref
        for radius,tol in CONFIGS: linear[label("linear",sig,1.,radius,tol)]={"infinite_bessel_relative_max_error":relative(load_ppoly(profiles,label("linear",sig,1.,radius,tol))(grid)[0],ref)}
        r=np.linspace(0,8,8001); zero[label("zero",sig,0.,8,1e-8)]={"max_abs_u":float(np.max(abs(r*load_ppoly(profiles,label("zero",sig,0.,8,1e-8))(r)[0])))}
    fine=[x for x in state["solves"] if x["kind"]=="nonlinear" and x["tol"]==1e-8]
    gates={"fine_status":all(x["solver_status"]==0 for x in fine),"graph_safety":all(x["checks"]["max_abs_u"]<.9 for x in fine),"boundary":all(abs(x["checks"]["boundary_vR"])<1e-9 and abs(x["checks"]["boundary_w0"])<1e-9 for x in fine),"pole_regularity":all(x["checks"]["pole_regularity_pass"] for x in fine),"Q_over_r":all(x["checks"]["max_abs_Q_over_r_div_epsilon"]<1e-5 for x in fine),"tolerance_refinement":all(x["tolerance_relative_change_R8"]<5e-4 for x in nl.values()),"reservoir_refinement":all(x["reservoir_relative_change_R8_to_R12"]<1e-5 for x in nl.values()),"linear_reference_fine_R8_and_R12":all(linear[label("linear",s,1.,r,1e-8)]["infinite_bessel_relative_max_error"]<1e-6 for s in (1,2) for r in (8,12)),"zero_source":all(x["max_abs_u"]<1e-10 for x in zero.values()),"ordering":all(x["min_v2"]>x["threshold_v2"] and x["min_v1_minus_v2"]>x["threshold_difference"] for x in ordering.values())}
    state["comparisons"]={"source_grid_count":SOURCE_POINTS,"nonlinear":nl,"linear":linear,"ordering":ordering,"zero_source":zero}; state["gates"]=gates; state["optional_K_diagnostic"]=optional_k(gates,profiles,grid); state["status"]="completed_gates_pass" if all(gates.values()) else "completed_gate_failed_optional_K_suppressed"; state["completed_at_utc"]=utcnow(); save_state(state,profiles)

def main():
    if RESULTS.exists() and json.loads(RESULTS.read_text(encoding="utf-8")).get("solves"): raise SystemExit("Attempt 3 already started; refusing duplicate BVP calls.")
    design=json.loads(DESIGN.read_text(encoding="utf-8")); state={"task_id":design["task_id"],"attempt_number":3,"status":"running","started_at_utc":utcnow(),"max_total_solves":MAX_SOLVES,"provenance":{"design_sha256":sha256(DESIGN),"execution_sha256":sha256(EXECUTION),"script_sha256":sha256(Path(__file__)),"python":sys.version,"numpy":np.__version__,"scipy":scipy.__version__,"platform":platform.platform()},"solves":[]}; profiles={}
    for eps in (.025,.05,.1):
        for sig in (1,2):
            prior=None
            for radius,tol in CONFIGS: _,prior=solve_record(state,profiles,"nonlinear",sig,eps,radius,tol,prior)
    for sig in (1,2):
        prior=None
        for radius,tol in CONFIGS: _,prior=solve_record(state,profiles,"linear",sig,1.,radius,tol,prior)
    for sig in (1,2): solve_record(state,profiles,"zero",sig,0.,8,1e-8)
    finalize(state,profiles)

if __name__ == "__main__": main()
