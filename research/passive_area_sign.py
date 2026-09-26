"""Bounded branch-connected passive area continuation using frozen rho physics."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from scipy.integrate import solve_bvp

ROOT = Path(__file__).resolve().parents[1]
HERE = Path(__file__).resolve()
DESIGN = HERE.with_name("passive_area_design.json")
RESULT = HERE.with_name("passive_area_results_001.json")
STATE_DIR = HERE.with_name("passive_area_states_001")
FROZEN_RHO = HERE.with_name("axisymmetric_rho_frozen_002.py")
SOURCE_SNAPSHOT = HERE.with_name("passive_area_source_frozen_001.py")
DESIGN_SNAPSHOT = HERE.with_name("passive_area_design_frozen_001.json")

spec = importlib.util.spec_from_file_location("frozen_rho", FROZEN_RHO)
frozen_rho = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(frozen_rho)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def initial_values(rho: np.ndarray, case: dict) -> tuple[np.ndarray, np.ndarray, str | None]:
    seed_path = case.get("seed_state_path")
    if seed_path:
        with np.load(seed_path) as saved:
            source_rho = saved["rho"]
            source_y = saved["y"]
            p = saved["p"]
        y = np.vstack([np.interp(rho, source_rho, row) for row in source_y])
        return y, p, sha256(Path(seed_path))
    y, p = frozen_rho.seed(rho, float(case["c_repo_ell"]), float(case["x"]))
    return y, p, None


def save_state(path: Path, rho: np.ndarray, y: np.ndarray, p: np.ndarray) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(path, rho=rho, y=y, p=p)
    return sha256(path)


def solve_case(case: dict) -> dict:
    x = float(case["x"])
    amplitude = float(case["c_repo_ell"])
    curvature = amplitude / 2
    alpha_coat = x*x/2
    width = float(case["width_alpha"])
    cutoff = float(case["alpha_cutoff"])
    rho0 = np.sqrt(2*cutoff)
    rho_outer = np.sqrt(2*float(case["alpha_outer"]))
    rho = np.linspace(rho0, rho_outer, int(case["nodes_rho"]))
    guess, parameters, seed_hash = initial_values(rho, case)
    fun, bc = frozen_rho.system(curvature, alpha_coat, width, rho0)
    began = time.perf_counter()
    sol = solve_bvp(fun, bc, rho, guess, p=parameters, tol=float(case["tol"]), max_nodes=12000)
    runtime = time.perf_counter() - began
    alpha = sol.x*sol.x/2
    y = sol.y
    q_raw, q_scale, q_relative = frozen_rho.q_metric(alpha, y, curvature, alpha_coat, width)
    probe_alpha = np.linspace(cutoff, alpha_coat, 2001)
    probe_y = sol.sol(np.sqrt(2*probe_alpha))
    coat_mean = (sol.p[0]*cutoff + np.trapezoid(probe_y[3], probe_alpha))/alpha_coat
    edge_y = sol.sol(np.array([x]))[:, 0]
    outer_y = y[:, -1]
    max_psi = float(np.max(np.abs(y[2])))
    min_cos_psi = float(np.min(np.cos(y[2])))
    min_r_away_axis = float(np.min(y[0, 1:]))
    state_path = Path(case["state_path"])
    state_hash = save_state(state_path, sol.x, sol.y, sol.p) if sol.success else None
    observables = {
        "apex_H_over_C_source": float(sol.p[0]/curvature),
        "coat_mean_H_over_C_source": float(coat_mean/curvature),
        "reservoir_depth_over_c_repo_ell": float(-sol.p[1]/amplitude),
        "edge_depth_over_c_repo_ell": float((edge_y[1]-sol.p[1])/amplitude),
        "material_coat_area_over_2pi_ell2": alpha_coat,
        "projected_coat_area_over_2pi_ell2": float(edge_y[0]**2/2),
        "max_abs_psi_radians": max_psi,
        "min_cos_psi": min_cos_psi,
        "total_projected_area_over_2pi_ell2": float(outer_y[0]**2/2),
    }
    gates = {
        "solver": bool(sol.success),
        "rms": bool(np.max(sol.rms_residuals) <= 1.01*float(case["tol"])),
        "outer_bc": bool(max(abs(outer_y[1]), abs(outer_y[2]), abs(outer_y[5]-.5)) <= 1e-9),
        "Q": bool(q_relative <= 1e-6),
        "positive_radius": bool(min_r_away_axis > 0),
        "psi_bound": bool(max_psi < .6),
        "cos_psi_bound": bool(min_cos_psi > np.cos(.6)),
        "finite": bool(np.all(np.isfinite(y)) and np.all(np.isfinite(sol.p))),
    }
    return {
        "case": case, "status": int(sol.status), "message": str(sol.message), "success": bool(sol.success),
        "runtime_seconds": runtime, "nodes_final": int(sol.x.size), "iterations": int(sol.niter),
        "max_rms_rho_ode_residual": float(np.max(sol.rms_residuals)),
        "outer_bc_errors": {"z": float(abs(outer_y[1])), "psi": float(abs(outer_y[2])), "lambda": float(abs(outer_y[5]-.5))},
        "force_balance_Q_relative": q_relative, "max_abs_force_balance_Q": q_raw, "force_balance_scale": q_scale,
        "min_r_away_axis": min_r_away_axis, "min_cos_psi": min_cos_psi, "gates": gates, "observables": observables,
        "state_path": str(state_path.relative_to(ROOT)).replace("\\", "/") if state_hash else None,
        "state_sha256": state_hash, "seed_state_path": case.get("seed_state_path"), "seed_state_sha256": seed_hash,
    }


def child(case: dict) -> dict:
    try:
        return solve_case(case)
    except Exception as error:
        return {"case": case, "success": False, "status": "exception", "message": repr(error)}


def run_subprocess(case: dict) -> dict:
    try:
        completed = subprocess.run([sys.executable, str(HERE), "--single", json.dumps(case)], capture_output=True,
                                   text=True, encoding="utf-8", timeout=45, check=False)
        if completed.returncode:
            return {"case": case, "success": False, "status": "subprocess_error", "message": completed.stderr[-2000:]}
        return json.loads(completed.stdout)
    except subprocess.TimeoutExpired:
        return {"case": case, "success": False, "status": "timeout", "message": "subprocess exceeded 45 seconds", "runtime_seconds": 45}


def base_case(x: float, amplitude: float, label: str, nodes: int = 801, cutoff: float = 1e-6) -> dict:
    return {"label": label, "x": x, "c_repo_ell": amplitude, "width_alpha": .01, "alpha_outer": 98.,
            "alpha_cutoff": cutoff, "nodes_rho": nodes, "tol": 1e-8,
            "state_path": str(STATE_DIR / f"{label}.npz")}


def accepted(record: dict) -> bool:
    return bool(record.get("success")) and all(record.get("gates", {}).values())


def run_all() -> dict:
    records: list[dict] = []
    strongest: dict | None = None
    for x in (.5, 1., 2.):
        prior: dict | None = None
        stopped = False
        for amplitude in (.02, .1, .3, .6):
            label = f"x{x:g}_c{amplitude:g}"
            case = base_case(x, amplitude, label)
            if stopped:
                records.append({"case": case, "success": False, "status": "skipped", "message": "earlier continuation stop in this x sequence"})
                continue
            if prior:
                case["seed_state_path"] = prior["state_path"]
            record = run_subprocess(case)
            records.append(record)
            if accepted(record):
                prior = record
                if strongest is None or record["observables"]["max_abs_psi_radians"] > strongest["observables"]["max_abs_psi_radians"]:
                    strongest = record
            else:
                stopped = True
    sensitivity = None
    if strongest:
        original = strongest["case"]
        case = base_case(float(original["x"]), float(original["c_repo_ell"]), original["label"]+"_sensitivity", 1601, 2.5e-7)
        case["seed_state_path"] = strongest["state_path"]
        sensitivity = run_subprocess(case)
    dependencies = [HERE, DESIGN, SOURCE_SNAPSHOT, DESIGN_SNAPSHOT, FROZEN_RHO]
    return {"task_id": "passive-area-numerical-001", "attempt": 1, "created_utc": datetime.now(timezone.utc).isoformat(),
            "source_hashes": {str(p.relative_to(ROOT)).replace("\\", "/"): sha256(p) for p in dependencies},
            "records": records, "sensitivity": sensitivity}


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "--single":
        print(json.dumps(child(json.loads(sys.argv[2]))))
        raise SystemExit(0)
    if RESULT.exists():
        raise FileExistsError(RESULT)
    with RESULT.open("x", encoding="utf-8") as handle:
        json.dump(run_all(), handle, indent=2)
        handle.write("\n")
    print(RESULT)
