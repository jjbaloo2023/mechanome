"""Corrected deadline-guarded finite-window fits of saved states; no BVP."""
from __future__ import annotations
import hashlib, importlib.util, json
from datetime import datetime, timezone
from pathlib import Path
import numpy as np
from scipy.interpolate import CubicHermiteSpline
from scipy.optimize import brentq, minimize_scalar

ROOT=Path(__file__).resolve().parents[1]; HERE=Path(__file__).resolve(); DEADLINE=datetime.fromisoformat('2026-09-25T03:10:12+00:00')
DESIGN=HERE.with_name('cap_observation_design_002.json'); RESULT=HERE.with_name('cap_observation_results_002.json'); RECORDS=HERE.with_name('cap_observation_records_002')
FROZEN=HERE.with_name('axisymmetric_rho_frozen_002.py'); SNAP=HERE.with_name('cap_observation_source_frozen_002.py'); DSNAP=HERE.with_name('cap_observation_design_frozen_002.json'); PASSIVE=HERE.with_name('passive_area_results_001.json')
spec=importlib.util.spec_from_file_location('fr',FROZEN); fr=importlib.util.module_from_spec(spec); assert spec and spec.loader; spec.loader.exec_module(fr)
def now(): return datetime.now(timezone.utc)
def expired(): return now()>=DEADLINE
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(path,data):
 path.parent.mkdir(parents=True,exist_ok=True)
 with path.open('x',encoding='utf-8') as f: json.dump(data,f,indent=2); f.write('\n')
def inc(r,h): return np.zeros_like(r) if h==0 else h*r*r/(1+np.sqrt(1-(h*r)**2))
def dgdh(r,h):
 if h==0: return r*r/2
 q=np.sqrt(1-(h*r)**2); return r*r/(q*(1+q))
def fit(r,z,w,R):
 upper=(1-1e-10)/R
 def objective(h,details=False):
  g=inc(r,h); b=float(np.sum(w*(z-g))/np.sum(w)); e=z-b-g; value=float(np.sum(w*e*e)/np.sum(w)); grad=float(-2*np.sum(w*e*dgdh(r,h))/np.sum(w))
  return (value,b,grad) if details else value
 opt=minimize_scalar(objective,bounds=(0,upper),method='bounded',options={'xatol':1e-12})
 zero=objective(0.,True); high=objective(upper,True)
 cand=[(0.,*zero),(upper,*high),(float(opt.x),*objective(float(opt.x),True))]
 h,val,b,grad=min(cand,key=lambda t:t[1]); return {'h':h,'b':b,'rmse':float(np.sqrt(val)),'gradient':grad,'optimizer_success':bool(opt.success),'flat_boundary':bool(h<=1e-8),'upper_boundary':bool(h>=upper*(1-1e-7)),'upper_h':upper,'upper_distance':upper-h,'objective_h0':zero[0],'objective_hupper':high[0]}
def quadrature(R,n=201):
 x,w=np.polynomial.legendre.leggauss(n); return (x+1)*R/2,w*R/2
def objective_at(r,z,w,h):
 g=inc(r,h); b=float(np.sum(w*(z-g))/np.sum(w)); e=z-b-g
 return float(np.sum(w*e*e)/np.sum(w)),float(-2*np.sum(w*e*dgdh(r,h))/np.sum(w))
def profile(label,amp,x):
 path=ROOT/'research/passive_area_states_001'/f'{label}.npz'
 with np.load(path) as d: rho,y,p=d['rho'],d['y'],d['p']
 rho=np.r_[0.,rho]; y=np.column_stack((np.array([0.,p[1],0.,p[0],0.,p[2]]),y)); der=np.empty_like(y); der[:,0]=[1.,0.,p[0],0.,0.,0.]
 der[:,1:]=rho[1:]*fr.alpha_rhs(rho[1:]**2/2,y[:,1:],amp/2,x*x/2,.01)
 return path,sha(path),CubicHermiteSpline(rho,y[0],der[0]),CubicHermiteSpline(rho,y[1],der[1]),CubicHermiteSpline(rho,y[2],der[2]),p
def expected_state_hash(label):
 data=json.loads(PASSIVE.read_text(encoding='utf-8'))
 for record in data['records']:
  if record['case']['label']==label: return record['state_sha256']
 raise KeyError(label)
def inverse_r(rs,r,edge_rho):
 return np.array([0. if q==0 else brentq(lambda t: float(rs(t)-q),0.,edge_rho,xtol=1e-13) for q in r])
def control(name,weighting):
 if expired(): return {'status':'deadline_not_started','name':name,'weighting':weighting}
 R=.4; r,qw=quadrature(R); h=.4 if name=='sphere' else 0.; b=.02 if name=='sphere' else 0.; z=b+inc(r,h); w=qw if weighting=='uniform_r' else qw*r
 out={'status':'control','name':name,'weighting':weighting,**fit(r,z,w,R),'target_h':h,'target_b':b}; return out
def one(label,amp,x,window,weighting):
 if expired(): return {'status':'deadline_not_started','label':label,'window':window,'weighting':weighting,'checked_utc':now().isoformat()}
 path,statehash,rs,zs,psis,p=profile(label,amp,x); edge=float(rs(x)); R=edge if window=='whole_nominal_coat' else float(window)
 if statehash!=expected_state_hash(label): return {'status':'input_hash_mismatch','label':label,'expected_state_sha256':expected_state_hash(label),'actual_state_sha256':statehash}
 if R>edge+1e-12:return {'status':'window_outside_nominal_coat','label':label,'window':window,'edge_r':edge}
 r,qw=quadrature(R); rho=inverse_r(rs,r,x); z=zs(rho)-p[1]; psi=psis(rho); w=qw if weighting=='uniform_r' else qw*r/np.cos(psi)
 if expired(): return {'status':'deadline_not_started','label':label,'window':window,'weighting':weighting,'checked_utc':now().isoformat()}
 f=fit(r,z,w,R); roundtrip=float(np.max(abs(rs(rho)-r))); actual_rho=float(inverse_r(rs,np.array([R]),x)[0]
 ); f['interior_gradient_pass']=bool(f['flat_boundary'] or f['upper_boundary'] or abs(f['gradient'])<=1e-8)
 r401,q401=quadrature(R,401); rho401=inverse_r(rs,r401,x); z401=zs(rho401)-p[1]; psi401=psis(rho401); w401=q401 if weighting=='uniform_r' else q401*r401/np.cos(psi401); mse401,grad401=objective_at(r401,z401,w401,f['h'])
 c0,cdot=fr.coat(np.array([0.]),amp/2,x*x/2,.01); h2=.5*(float(cdot[0])+p[0]*(p[2]-float(c0[0])*(p[0]-float(c0[0])))); predicted=(3*h2*R*R/14 if weighting=='uniform_r' else h2*R*R/4); bias=f['h']-p[0]; rel=None if abs(predicted)<1e-12 else abs(bias-predicted)/abs(predicted)
 return {'status':'fit','label':label,'amplitude':amp,'x':x,'window':window,'weighting':weighting,'Rfit':R,'alpha_support':actual_rho*actual_rho/2,'inverse_roundtrip_max_abs':roundtrip,'state_sha256':statehash,**f,'h_over_Csource':f['h']/(amp/2),'apex_H_over_Csource':p[0]/(amp/2),'bias_over_Csource':bias/(amp/2),'quadrature_401_rmse_at_201_h':float(np.sqrt(mse401)),'quadrature_401_gradient_at_201_h':grad401,'small_window_bias_prediction':predicted,'small_window_bias_relative_error':rel,'small_window_bias_gate_applicable':window==.1 and rel is not None,'small_window_bias_pass':None if window!=.1 or rel is None else bool(rel<=.02)}
def run():
 if expired(): return {'status':'deadline_before_run','created_utc':now().isoformat()}
 controls=[]
 for n in ('sphere','flat'):
  for w in ('uniform_r','uniform_material_alpha'):
   c=control(n,w); write(RECORDS/(f'control_{n}_{w}.json'),c); controls.append(c)
 good=all(c.get('status')=='control' and abs(c['h']-c['target_h'])<=1e-8 and abs(c['b']-c['target_b'])<=1e-10 and c['rmse']<=1e-10 for c in controls)
 records=[]
 for x in (.5,1.,2.):
  for amp in (.02,.6):
   label=f'x{x:g}_c{amp:g}'
   for win in (.1,.25,.4,'whole_nominal_coat'):
    for w in ('uniform_r','uniform_material_alpha'):
     d={'status':'controls_failed'} if not good else one(label,amp,x,win,w); d['record_id']=f'{label}_{win}_{w}'.replace('.','p'); write(RECORDS/(d['record_id']+'.json'),d); records.append(d)
 deps=[HERE,DESIGN,SNAP,DSNAP,FROZEN,PASSIVE]; return {'task_id':'cap-observation-numerical-001','attempt':2,'created_utc':now().isoformat(),'deadline_utc':DEADLINE.isoformat(),'controls':controls,'controls_pass':good,'source_hashes':{str(p.relative_to(ROOT)).replace('\\','/'):sha(p) for p in deps},'records':records}
if __name__=='__main__':
 if RESULT.exists(): raise FileExistsError(RESULT)
 write(RESULT,run())
