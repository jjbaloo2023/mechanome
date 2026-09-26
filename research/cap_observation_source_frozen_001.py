"""Deadline-guarded finite-window cap fits of saved passive states only."""
from __future__ import annotations
import hashlib, importlib.util, json
from datetime import datetime, timezone
from pathlib import Path
import numpy as np
from scipy.interpolate import CubicHermiteSpline
from scipy.optimize import minimize_scalar

ROOT=Path(__file__).resolve().parents[1]; HERE=Path(__file__).resolve()
DESIGN=HERE.with_name('cap_observation_design.json'); RESULT=HERE.with_name('cap_observation_results_001.json')
RECORDS=HERE.with_name('cap_observation_records_001'); DEADLINE=datetime.fromisoformat('2026-09-25T03:10:12+00:00')
FROZEN=HERE.with_name('axisymmetric_rho_frozen_002.py'); SNAP=HERE.with_name('cap_observation_source_frozen_001.py'); DSNAP=HERE.with_name('cap_observation_design_frozen_001.json')
spec=importlib.util.spec_from_file_location('frozen_rho',FROZEN); frozen=importlib.util.module_from_spec(spec); assert spec and spec.loader; spec.loader.exec_module(frozen)

def now(): return datetime.now(timezone.utc)
def expired(): return now() >= DEADLINE
def digest(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def exclusive(path,data):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('x',encoding='utf-8') as f: json.dump(data,f,indent=2); f.write('\n')

def cap_increment(r,h):
    if h==0: return np.zeros_like(r)
    return h*r*r/(1+np.sqrt(1-(h*r)**2))

def fit_curve(r,z,weight):
    limit=(1-1e-10)/r[-1]
    def evaluate(h):
        g=cap_increment(r,h); b=float(np.average(z-g,weights=weight)); e=z-(b+g)
        return float(np.average(e*e,weights=weight)),b
    zero,b0=evaluate(0.)
    result=minimize_scalar(lambda h:evaluate(h)[0],bounds=(0.,limit),method='bounded',options={'xatol':1e-12})
    candidates=[(zero,0.,b0),(float(result.fun),float(result.x),evaluate(float(result.x))[1])]
    mse,h,b=min(candidates,key=lambda x:x[0]); boundary=(h<=1e-8 or h>=limit*(1-1e-7))
    return {'h':h,'b':b,'rmse':float(np.sqrt(mse)),'optimizer_success':bool(result.success),'flat_boundary':bool(h<=1e-8),'upper_boundary':bool(h>=limit*(1-1e-7)),'objective_h0':zero}

def controls():
    r=np.linspace(0,.4,401); h=.4; b=.02; z=b+cap_increment(r,h); out=[]
    for name,y in [('sphere',z),('flat',np.zeros_like(r))]:
        for kind,w in [('uniform_r',np.ones_like(r)),('uniform_material_alpha',r+1e-12)]:
            out.append({'name':name,'weighting':kind,**fit_curve(r,y,w),'target_h':h if name=='sphere' else 0.,'target_b':b if name=='sphere' else 0.})
    return out

def profile(label):
    state=ROOT/'research/passive_area_states_001'/f'{label}.npz'
    with np.load(state) as d: rho,y,p=d['rho'],d['y'],d['p']
    rho=np.r_[0.,rho]; y=np.column_stack((np.array([0.,p[1],0.,p[0],0.,p[2]]),y))
    # Pole derivatives are regular limits; off-pole derivatives use frozen RHS.
    deriv=np.empty_like(y); deriv[:,0]=[1.,0.,p[0],0.,0.,0.]
    deriv[:,1:]=rho[1:]*frozen.alpha_rhs(rho[1:]**2/2,y[:,1:],0.,0.,.01)
    return state,digest(state),CubicHermiteSpline(rho,y[0],deriv[0]),CubicHermiteSpline(rho,y[1],deriv[1]),CubicHermiteSpline(rho,y[2],deriv[2]),p

def record_fit(label,amp,window,weighting):
    if expired(): return {'status':'deadline_not_started','label':label,'window':window,'weighting':weighting,'checked_utc':now().isoformat()}
    state,statehash,rs,zs,psis,p=profile(label); x=float(label.split('_')[0][1:]); C=amp/2
    edge=float(rs(x)); R=edge if window=='whole_nominal_coat' else float(window)
    if R>edge+1e-12: return {'status':'window_outside_nominal_coat','label':label,'window':window,'edge_r':edge}
    r=np.linspace(0,R,401); rho=np.interp(r,rs.x,rs(rs.x)); z=zs(rho)-p[1]; psi=psis(rho)
    w=np.ones_like(r) if weighting=='uniform_r' else r/np.cos(psi)+1e-12
    fit=fit_curve(r,z,w); alpha_support=float(rho[-1]**2/2)
    data={'status':'fit','label':label,'amplitude':amp,'window':window,'weighting':weighting,'Rfit':R,'alpha_support':alpha_support,'state_sha256':statehash,**fit,
      'h_over_Csource':fit['h']/C,'apex_H_over_Csource':p[0]/C,'bias_over_Csource':(fit['h']-p[0])/C}
    return data

def run():
    control=controls()
    good=all(abs(c['h']-c['target_h'])<=1e-8 and abs(c['b']-c['target_b'])<=1e-10 and c['rmse']<=1e-10 for c in control)
    records=[]
    for x in (.5,1.,2.):
      for amp in (.02,.6):
       label=f'x{x:g}_c{amp:g}'
       for win in (.1,.25,.4,'whole_nominal_coat'):
        for wt in ('uniform_r','uniform_material_alpha'):
         data={'status':'controls_failed'} if not good else record_fit(label,amp,win,wt)
         data['record_id']=f'{label}_{win}_{wt}'.replace('.','p'); exclusive(RECORDS/(data['record_id']+'.json'),data); records.append(data)
    hashes={str(p.relative_to(ROOT)).replace('\\','/'):digest(p) for p in [HERE,DESIGN,SNAP,DSNAP,FROZEN]}
    return {'task_id':'cap-observation-numerical-001','created_utc':now().isoformat(),'deadline_utc':DEADLINE.isoformat(),'controls':control,'controls_pass':good,'source_hashes':hashes,'records':records}

if __name__=='__main__':
    if RESULT.exists(): raise FileExistsError(RESULT)
    exclusive(RESULT,run())
