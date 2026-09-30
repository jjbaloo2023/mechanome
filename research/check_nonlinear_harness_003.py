"""Synthetic, no-BVP preflight for the mesh-refined attempt-3 source."""
from __future__ import annotations
import hashlib, importlib.util, json, tempfile
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace
import numpy as np
from scipy.interpolate import PPoly

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("nl003", HERE / "nonlinear_graph_numerical_003.py")
mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)

def ppoly(tiny_pole_slope=0.):
    c = np.zeros((4, 2, 2)); c[1, :, 0] = .0001
    c[3, 0, 0], c[3, 1, 0], c[2, :, 1], c[2, 0, 0] = .01, .0101, .0002, tiny_pole_slope
    return PPoly.construct_fast(c, np.array([0., 1., 8.]), axis=1)

def hidden_physical_bump():
    """C1 cubic v bump in an original-grid gap; stored w is exactly v'."""
    original = np.r_[0., np.geomspace(1e-10, .999999, 6000), np.linspace(1., 8., 6001)]
    a, b = original[7000], original[7001]; left, right = a+.2*(b-a), b-.2*(b-a); middle=(a+b)/2
    h, A = middle-left, 1e-6; c = np.zeros((4, 4, 2)); x = np.array([0., left, middle, right, 8.])
    c[0,1,0], c[1,1,0] = -2*A/h**3, 3*A/h**2
    c[0,2,0], c[1,2,0], c[3,2,0] = 2*A/h**3, -3*A/h**2, A
    c[1,1,1], c[2,1,1], c[1,2,1], c[2,2,1] = -6*A/h**3, 6*A/h**2, 6*A/h**3, -6*A/h**2
    return PPoly.construct_fast(c, x, axis=1), original

def physical_q_over_r(pp, grid):
    v, vp, vpp = pp(grid)[0], pp(grid,1)[0], pp(grid,2)[0]
    u, up, t, tp = grid*v, v+grid*vp, 2*v+grid*vp, 3*vp+grid*vpp
    q = -(1-u*u)*tp-t*u*up+.5*t*t*u+u; result=np.zeros_like(grid); result[1:]=q[1:]/grid[1:]; return result

def state(): return {"status":"running", "solves":[]}

def main():
    started=datetime.now(timezone.utc).isoformat(); captured={}; real={"count":0}
    def mesh_stub(fun, bc, mesh, y, **kwargs):
        captured.update({"mesh":mesh.copy(),"S":kwargs["S"].copy(),"rhs":fun(np.array([.5]),np.array([[.2],[.3]]))[1,0]}); return SimpleNamespace()
    mod.solve_bvp=mesh_stub; mod.bvp_solution("linear",2,1.,8.,1e-8)
    def forbidden(*args, **kwargs): real["count"]+=1; raise AssertionError("real solve_bvp forbidden")
    mod.solve_bvp=forbidden
    profiles, key, good = {}, "roundtrip", ppoly(); mod.ppoly_arrays(profiles,key,good); restored=mod.ppoly_from_arrays(profiles,key); radii=np.array([.25,2.,3.])
    roundtrip=all(np.allclose(restored(radii,d),good(radii,d)) for d in (0,1,2))
    linear=mod.make_rhs("linear",2,1.)(np.array([.5]),np.array([[.2],[.3]]))[1,0]; nonlinear=mod.make_rhs("nonlinear",2,1.)(np.array([.5]),np.array([[.2],[.3]]))[1,0]; expected=mod.c_over_r_prime(np.array([.5]),1.)[0]+.4
    bump, original=hidden_physical_bump(); strict=mod.exact_checks(bump,1,0.,8.,True); old_max=float(np.max(abs(physical_q_over_r(bump,original))))
    tiny=mod.exact_checks(ppoly(1e-12),1,.025,8.,True)
    with tempfile.TemporaryDirectory() as temp:
        temp=Path(temp); save=lambda s,p:mod.save_state(s,p,temp/"result.json",temp/"profiles.npz"); failed,partial=state(),{}
        fake=SimpleNamespace(status=0,message="synthetic",x=np.linspace(0,8,9),niter=1,sol=good); old_checks=mod.exact_checks; mod.exact_checks=lambda *args:(_ for _ in ()).throw(RuntimeError("injected post-store failure"))
        try: mod.solve_record(failed,partial,"nonlinear",1,.025,8,1e-8,solver=lambda *args:fake,save=save)
        except RuntimeError: pass
        finally: mod.exact_checks=old_checks
        disk=json.loads((temp/"result.json").read_text(encoding="utf-8")); saved=np.load(temp/"profiles.npz")
        failure_key=mod.config_label("nonlinear",1,.025,8,1e-8)
        checkpoint_on_disk=all(f"{failure_key}__{suffix}" in saved.files for suffix in ("x","c","axis"))
        saved.close()
    checks={"task_id":"nonlinear-mesh-preflight-001","observed_started_at_utc":started,"command":".venv\\Scripts\\python.exe research\\check_nonlinear_harness_003.py","actual_solve_bvp_calls":real["count"],"stubbed_bvp_wrapper_calls":1,"fresh_output_paths":{"results":mod.RESULTS.name,"profiles":mod.PROFILES.name,"execution":mod.EXECUTION.name},"mesh":{"nodes":int(captured["mesh"].size),"first":float(captured["mesh"][0]),"source_edge":float(captured["mesh"][1920]),"last":float(captured["mesh"][-1]),"source_spacing":float(captured["mesh"][1]-captured["mesh"][0]),"exterior_spacing":float(captured["mesh"][-1]-captured["mesh"][-2]),"singular_matrix":captured["S"].tolist()},"linear_rhs_exact_match":bool(np.isclose(linear,expected)),"linear_nonlin_dispatch_distinct":bool(not np.isclose(linear,nonlinear)),"ppoly_axis":int(profiles[f"{key}__axis"][0]),"nonconstant_value_first_second_roundtrip":roundtrip,"physical_between_knot_defect":{"old_original_grid_max_abs_Q_over_r":old_max,"augmented_grid_max_abs_Q_over_r":strict["max_abs_Q_over_r"],"augmented_grid_count":strict["residual_grid_count"],"original_grid_count":strict["original_residual_grid_count"],"interval_points":strict["interval_interior_point_count"],"knot_side_points":strict["knot_side_point_count"]},"tiny_pole_perturbation":{"actual_vprime0":tiny["actual_vprime0"],"stored_w0":tiny["stored_w0"],"exact_regular":tiny["pole_regularity_exact_pass"],"Q_over_r_is_infinite":bool(np.isinf(tiny["max_abs_Q_over_r_div_epsilon"]))},"k_suppressed_with_any_failed_gate":not mod.k_is_allowed({"first":True,"failed":False}),"postprocessing_failure_preserves_coefficients":f"{failure_key}__c" in partial,"postprocessing_failure_checkpoint_on_disk":checkpoint_on_disk,"postprocessing_failure_checkpoint":{"status":disk["status"],"outcome":disk["solves"][0]["outcome"],"solver_status":disk["solves"][0]["solver_status"]},"import_safe":True,"tested_source_sha256":hashlib.sha256((HERE/"nonlinear_graph_numerical_003.py").read_bytes()).hexdigest(),"tested_harness_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    required=[checks["actual_solve_bvp_calls"]==0,checks["mesh"]["nodes"]==5761,checks["mesh"]["first"]==0.,checks["mesh"]["source_edge"]==1.,checks["linear_rhs_exact_match"],checks["linear_nonlin_dispatch_distinct"],roundtrip,old_max==0.,strict["max_abs_Q_over_r"]>1e-4,not tiny["pole_regularity_exact_pass"],checks["tiny_pole_perturbation"]["Q_over_r_is_infinite"],checks["k_suppressed_with_any_failed_gate"],checks["postprocessing_failure_preserves_coefficients"],checkpoint_on_disk]
    if not all(required): raise SystemExit("mesh preflight assertion failed")
    checks["observed_finished_at_utc"]=datetime.now(timezone.utc).isoformat(); (HERE/"nonlinear_mesh_preflight_checks.json").write_text(json.dumps(checks,indent=2,sort_keys=True)+"\n",encoding="utf-8")

if __name__ == "__main__": main()
