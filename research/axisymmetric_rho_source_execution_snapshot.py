"""Passive S40 BVP in rho=sqrt(2*alpha), with per-case subprocess bounds."""
from __future__ import annotations

import hashlib, json, subprocess, sys, time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from scipy.integrate import quad, solve_bvp
from scipy.special import iv, kv

ROOT = Path(__file__).resolve().parents[1]
HERE = Path(__file__).resolve()
DESIGN = HERE.with_name("axisymmetric_rho_design.json")
RESULT = HERE.with_name("axisymmetric_rho_results_002.json")
SNAPSHOT = HERE.with_name("axisymmetric_rho_snapshot.py")
DESIGN_SNAPSHOT = HERE.with_name("axisymmetric_rho_design_snapshot.json")


def coat(alpha, c, ac, w):
    u = (alpha-ac)/w; t = np.tanh(u)
    return .5*c*(1-t), -.5*c*(1-t*t)/w


def pole(rho, c, ac, w, p):
    hp, zp, lp = p; c0, ca = coat(np.array([0.]), c, ac, w)
    c0, ca = float(c0[0]), float(ca[0]); q = lp-c0*(hp-c0); h2 = .5*(ca+hp*q)
    return np.array([rho-hp*hp*rho**3/8,
        zp+hp*rho*rho/2+h2*rho**4/8,
        hp*rho+(h2/2+hp**3/24)*rho**3,
        hp+h2*rho*rho, hp*q*rho*rho, lp+(hp-c0)*ca*rho*rho])


def alpha_rhs(alpha, y, c, ac, w):
    r,z,psi,h,l,lam = y; C,Ca = coat(alpha,c,ac,w); sr=np.sin(psi)/r
    return np.vstack((np.cos(psi)/r, np.sin(psi)/r, (2*r*h-np.sin(psi))/r**2,
        (l+r*r*Ca)/r**2,
        2*h*((h-C)**2+lam)-2*(h-C)*(h*h+(h-sr)**2), 2*(h-C)*Ca))


def system(c, ac, w, rho0):
    def fun(rho,y,p):
        return rho*alpha_rhs(rho*rho/2,y,c,ac,w)
    def bc(ya,yb,p): return np.r_[ya-pole(rho0,c,ac,w,p), yb[1],yb[2],yb[5]-.5]
    return fun,bc


def seed(rho, camp, x):
    r=rho.copy(); c=camp/2; inside=r<=x
    h=np.where(inside,c*x*kv(1,x)*iv(0,r),-c*x*iv(1,x)*kv(0,r))
    z=np.where(inside,camp*(x*kv(1,x)*iv(0,r)-1),-camp*x*iv(1,x)*kv(0,r))
    psi=np.where(inside,camp*x*kv(1,x)*iv(1,r),camp*x*iv(1,x)*kv(1,r))
    return np.vstack((r,z,psi,h,np.zeros_like(r),np.full_like(r,.5))),np.array([h[0],z[0],.5])


def smooth_apex(ac,w):
    g=lambda r: float(coat(np.array([r*r/2]),1.,ac,w)[0][0])
    return float(g(0)-quad(lambda r:r*kv(0,r)*g(r),0,40,epsabs=2e-10,epsrel=2e-10)[0])


def q_metric(alpha,y,c,ac,w):
    r,z,p,h,l,la=y; C,_=coat(alpha,c,ac,w); alg=r*((h-C)*(h+C-np.sin(p)/r)-la)*np.sin(p)
    q=alg+l*np.cos(p); scale=max(float(np.max(abs(alg))),float(np.max(abs(l))),1e-12)
    return float(np.max(abs(q))),scale,float(np.max(abs(q))/scale)


def arc_defect(sol,c,ac,w):
    # Fraction .37 of selected final intervals avoids the solver's midpoint
    # collocation points.  It compares r*Y_alpha to (r/rho)*Y_rho.
    grid=sol.x; take=np.linspace(0,len(grid)-2,min(97,len(grid)-1),dtype=int)
    rho=grid[take]+.37*(grid[take+1]-grid[take]); y=sol.sol(rho); yr=sol.sol(rho,1)
    left=(y[0]/rho)*yr; right=y[0]*alpha_rhs(rho*rho/2,y,c,ac,w)
    return [float(v) for v in np.max(abs(left-right),axis=1)]


def solve_case(case):
    x=float(case['x']); camp=float(case['c_repo_ell']); c=camp/2; ac=x*x/2; w=float(case['width_alpha'])
    rho0=np.sqrt(2*float(case['alpha_cutoff'])); rho_end=float(case['outer_radius'])
    rho=np.linspace(rho0,rho_end,int(case['nodes_rho'])); guess,p=seed(rho,camp,x); fun,bc=system(c,ac,w,rho0)
    began=time.perf_counter(); sol=solve_bvp(fun,bc,rho,guess,p=p,tol=float(case['tol']),max_nodes=12000); elapsed=time.perf_counter()-began
    alpha=np.linspace(float(case['alpha_cutoff']),ac,1001); sy=sol.sol(np.sqrt(2*alpha)); mean=(sol.p[0]*alpha[0]+np.trapezoid(sy[3],alpha))/ac
    edge=sol.sol(np.array([x]))[1,0]; qraw,qscale,qrel=q_metric(sol.x*sol.x/2,sol.y,c,ac,w); yb=sol.y[:,-1]
    obs={'apex_H_over_C_source':float(sol.p[0]/c),'coat_mean_H_over_C_source':float(mean/c),
         'reservoir_depth_over_c_repo_ell':float(-sol.p[1]/camp),'edge_depth_over_c_repo_ell':float((edge-sol.p[1])/camp)}
    return {'case':case,'status':int(sol.status),'message':str(sol.message),'success':bool(sol.success),'runtime_seconds':elapsed,
      'iterations':int(sol.niter),'nodes_final':int(sol.x.size),'max_rms_rho_ode_residual':float(np.max(sol.rms_residuals)),
      'outer_bc_errors':{'z':float(abs(yb[1])),'psi':float(abs(yb[2])),'lambda':float(abs(yb[5]-.5))},
      'pole_bc_max_abs_error':float(np.max(abs(sol.y[:,0]-pole(rho0,c,ac,w,sol.p)))), 'observables':obs,
      'smooth_linear_reference':{'apex_H_over_C_source':smooth_apex(ac,w)},'relative_apex_error_vs_smooth_linear':float(abs(obs['apex_H_over_C_source']-smooth_apex(ac,w))/smooth_apex(ac,w)),
      'max_abs_force_balance_Q':qraw,'force_balance_scale':qscale,'force_balance_Q_relative':qrel,
      'max_abs_arc_length_cross_coordinate_defect':arc_defect(sol,c,ac,w),
      'arc_defect_sample_definition':'0.37 through 97 selected final mesh intervals; excludes endpoints and midpoint collocation points',
      'native_residual_note':'rho residual is coordinate-dependent; compare observables/BC/Q and off-mesh arc defects, not its magnitude to alpha RMS.'}


def hashes():
    paths=[HERE,DESIGN,SNAPSHOT,DESIGN_SNAPSHOT,HERE.with_name('axisymmetric_rho_source_snapshot.py'),HERE.with_name('axisymmetric_rho_design_full_snapshot.json'),HERE.with_name('axisymmetric_rho_source_execution_snapshot.py'),ROOT/'research/axisymmetric_passive_initial_snapshot.py',ROOT/'research/axisymmetric_design_initial_snapshot.json',ROOT/'research/AXISYMMETRIC_THEORY.md']
    return {str(p.relative_to(ROOT)).replace('\\','/'):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}


def single(case):
    try: return solve_case(case)
    except Exception as exc: return {'case':case,'success':False,'status':'exception','message':repr(exc)}


def run_all():
    design=json.loads(DESIGN.read_text(encoding='utf-8')); out=[]
    for case in design['cases']:
        try:
            cp=subprocess.run([sys.executable,str(HERE),'--single',json.dumps(case)],capture_output=True,text=True,encoding='utf-8',timeout=45,check=False)
            if cp.returncode: out.append({'case':case,'success':False,'status':'subprocess_error','message':cp.stderr[-2000:],'runtime_seconds':None})
            else: out.append(json.loads(cp.stdout))
        except subprocess.TimeoutExpired:
            out.append({'case':case,'success':False,'status':'timeout','message':'subprocess exceeded 45 seconds','runtime_seconds':45})
    return {'task_id':'axisymmetric-passive-rho-002','attempt':2,'created_utc':datetime.now(timezone.utc).isoformat(),'source_hashes':hashes(),'records':out}


if __name__=='__main__':
    if len(sys.argv)==3 and sys.argv[1]=='--single': print(json.dumps(single(json.loads(sys.argv[2])))); raise SystemExit(0)
    if RESULT.exists(): raise FileExistsError(RESULT)
    with RESULT.open('x',encoding='utf-8') as f: json.dump(run_all(),f,indent=2); f.write('\n')
    print(RESULT)

