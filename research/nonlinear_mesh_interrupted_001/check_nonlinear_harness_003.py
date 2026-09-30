"""No-BVP preflight for nonlinear_graph_numerical_003.py."""
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

def canonical_ppoly(defect=False, irregular=False):
    # Canonical (degree, interval, component), as stored by solve_bvp axis=1.
    c = np.zeros((4, 2, 2)); x = np.array([0., 1., 8.])
    c[1, :, 0] = .0001; c[3, 0, 0] = .01; c[3, 1, 0] = .0101
    c[2, :, 1] = .0002
    if defect: c[1, 0, 1], c[2, 0, 1] = -.01, .0102  # zero at knot ends, nonzero inside
    if irregular: c[2, 0, 0] = .01  # actual v'(0), while w(0)=0
    return PPoly.construct_fast(c, x, axis=1)

def state(): return {"status":"running", "solves":[]}

def main():
    started = datetime.now(timezone.utc).isoformat(); pp = canonical_ppoly(); captured = {}
    def mesh_stub(fun, bc, mesh, y, **kwargs):
        captured.update({"mesh":mesh.copy(), "S":kwargs["S"].copy(), "rhs":fun(np.array([.5]), np.array([[.2],[.3]]))[1,0]}); return SimpleNamespace()
    mod.solve_bvp = mesh_stub
    mod.bvp_solution("linear", 2, 1., 8., 1e-8)
    forbidden = {"actual":0}
    def no_real_bvp(*args, **kwargs): forbidden["actual"] += 1; raise AssertionError("real solve_bvp forbidden")
    mod.solve_bvp = no_real_bvp
    profiles = {}; key = "roundtrip"; mod.store_ppoly(profiles, key, pp); restored = mod.load_ppoly(profiles, key); r = np.array([.25, 2., 3.])
    roundtrip = all(np.allclose(restored(r, d), pp(r, d)) for d in (0,1,2))
    rhs_linear = mod.make_rhs("linear", 2, 1.)(np.array([.5]), np.array([[.2],[.3]]))[1,0]
    rhs_nonlinear = mod.make_rhs("nonlinear", 2, 1.)(np.array([.5]), np.array([[.2],[.3]]))[1,0]
    expected_linear = mod.c_over_r_prime(np.array([.5]),1.)[0]+.4
    strict = mod.exact_checks(canonical_ppoly(defect=True), 1, .025, 8, True)
    irregular = mod.exact_checks(canonical_ppoly(irregular=True), 1, .025, 8, True)
    with tempfile.TemporaryDirectory() as d:
        d = Path(d); save = lambda s,p: mod.save_state(s,p,d/"r.json",d/"p.npz")
        failed, partial = state(), {}
        fake = SimpleNamespace(status=0,message="synthetic",x=np.linspace(0,8,9),niter=1,sol=pp)
        original_checks = mod.exact_checks; mod.exact_checks = lambda *args: (_ for _ in ()).throw(RuntimeError("injected post-store failure"))
        try: mod.solve_record(failed, partial, "nonlinear", 1, .025, 8, 1e-8, solver=lambda *a: fake, save=save)
        except RuntimeError: pass
        finally: mod.exact_checks = original_checks
        failure_disk = json.loads((d/"r.json").read_text(encoding="utf-8"))
    checks = {"task_id":"nonlinear-mesh-preflight-001", "observed_started_at_utc":started,
      "command":".venv\\Scripts\\python.exe research\\check_nonlinear_harness_003.py", "actual_solve_bvp_calls":forbidden["actual"], "stubbed_bvp_wrapper_calls":1,
      "mesh":{"nodes":int(captured["mesh"].size),"first":float(captured["mesh"][0]),"source_edge":float(captured["mesh"][1920]),"last":float(captured["mesh"][-1]),"source_spacing":float(captured["mesh"][1]-captured["mesh"][0]),"exterior_spacing":float(captured["mesh"][-1]-captured["mesh"][-2]),"singular_matrix":captured["S"].tolist()},
      "linear_rhs_exact_match":bool(np.isclose(rhs_linear, expected_linear)), "linear_nonlin_dispatch_distinct":bool(not np.isclose(rhs_linear,rhs_nonlinear)),
      "ppoly_axis":int(profiles[f"{key}__axis"][0]),"nonconstant_ppoly_value_first_second_roundtrip":roundtrip,
      "strict_grid":{"total":strict["residual_grid_count"],"original":strict["original_grid_count"],"interval_interior":strict["interval_interior_point_count"],"knot_sides":strict["knot_side_point_count"],"between_knot_derivative_defect":strict["max_abs_spline_vprime_minus_stored_w"]},
      "pole_invalidity":{"pass":irregular["pole_regularity_pass"],"actual_vprime0":irregular["actual_vprime0"],"stored_w0":irregular["stored_w0"],"normalized_residual_is_infinite":bool(np.isinf(irregular["max_abs_Q_over_r_div_epsilon"]))},
      "k_suppressed_with_failed_gate":mod.optional_k({"one":True,"failed":False},{},np.linspace(0,1,5))["run"] is False,
      "postprocessing_failure_preserves_coefficients":f"{mod.label('nonlinear',1,.025,8,1e-8)}__c" in partial,
      "postprocessing_failure_checkpoint":{"status":failure_disk["status"],"outcome":failure_disk["solves"][0]["outcome"],"solver_status":failure_disk["solves"][0]["solver_status"]},
      "import_safe":True, "tested_source_sha256":hashlib.sha256((HERE/"nonlinear_graph_numerical_003.py").read_bytes()).hexdigest(),"tested_harness_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    required = [checks["actual_solve_bvp_calls"]==0, checks["mesh"]["nodes"]==5761, checks["mesh"]["first"]==0, checks["mesh"]["source_edge"]==1, checks["linear_rhs_exact_match"], checks["linear_nonlin_dispatch_distinct"], roundtrip, strict["residual_grid_count"]>strict["original_grid_count"], strict["max_abs_spline_vprime_minus_stored_w"]>.001, not irregular["pole_regularity_pass"], checks["pole_invalidity"]["normalized_residual_is_infinite"], checks["k_suppressed_with_failed_gate"], checks["postprocessing_failure_preserves_coefficients"]]
    if not all(required): raise SystemExit("mesh preflight assertion failed")
    checks["observed_finished_at_utc"] = datetime.now(timezone.utc).isoformat()
    (HERE/"nonlinear_mesh_preflight_checks.json").write_text(json.dumps(checks,indent=2,sort_keys=True)+"\n",encoding="utf-8")

if __name__ == "__main__": main()
