"""Independent saved-spline audit of nonlinear numerical attempt 3; never calls a BVP solver."""
from __future__ import annotations
import hashlib, json
from pathlib import Path
import numpy as np
from scipy.interpolate import PPoly
from scipy.integrate import quad
from scipy.special import i1, k1

D=Path(__file__).resolve().parent
result=json.loads((D/'nonlinear_numerical_results_003.json').read_text(encoding='utf-8'))
data=np.load(D/'nonlinear_numerical_profiles_003.npz',allow_pickle=False)
source_grid=np.linspace(0.,1.,4097)

def poly(label):
    return PPoly.construct_fast(data[label+'__c'],data[label+'__x'],axis=int(data[label+'__axis'][0]))
def phi(r):
    r=np.asarray(r); z=np.zeros_like(r,dtype=float); m=r<1.; s=r[m]
    z[m]=np.exp(1.-1./(1.-s*s)); return z
def cprime_over_r(r,e):
    r=np.asarray(r); z=np.zeros_like(r,dtype=float); m=r<1.; s=r[m]
    z[m]=-2.*e*phi(s)/(1.-s*s)**2; return z
def relative(a,b): return float(np.max(np.abs(a-b))/max(float(np.max(np.abs(b))),1e-12))

def diagnostics(record):
    label=record['label']; e=record['epsilon']; sig=record['sigma']; R=record['R']; P=poly(label)
    old=np.r_[0.,np.geomspace(1e-10,.999999,6000),np.linspace(1.,R,6001)]
    knots=P.x
    interior=[np.linspace(a,b,19)[1:-1] for a,b in zip(knots[:-1],knots[1:])]
    sides=np.r_[np.nextafter(knots[1:-1],-np.inf),np.nextafter(knots[1:-1],np.inf)]
    grid=np.unique(np.r_[old,*interior,sides])
    v=P(grid)[0]; vp=P(grid,1)[0]; vpp=P(grid,2)[0]; w=P(grid)[1]
    u=grid*v; up=v+grid*vp; J=1./np.sqrt(1.-u*u); p=u*J
    C=2.*v+grid*vp; Cp=3.*vp+grid*vpp
    c=e*phi(grid); cp=grid*cprime_over_r(grid,e); t=C-c; tp=Cp-cp
    pp=up*J**3; Jp=p*pp/J
    Q=-(tp*J+t*Jp)/J**3 + (.5*t*t+sig)*p/J
    q0=-4.*float(P(0.,2)[0])-2.*e-(2.*float(P(0.)[0])-e)*float(P(0.)[0])**2+(.5*(2.*float(P(0.)[0])-e)**2+sig)*float(P(0.)[0])
    vp0=float(P(0.,1)[0]); w0=float(P(0.)[1]); pole_regular=vp0==0. and w0==0.
    qr=np.empty_like(Q); qr[0]=q0 if pole_regular else np.inf; qr[1:]=Q[1:]/grid[1:]
    i=int(np.argmax(np.abs(qr)))
    normq=-(1.-u*u)*tp-t*u*up+(.5*t*t+sig)*u
    out={'label':label,'status':record['solver_status'],'max_abs_Q_over_r_div_epsilon':float(np.max(np.abs(qr))/e),'argmax_r':float(grid[i]),'argmax_Q_over_r_div_epsilon':float(qr[i]/e),'pole_Q_over_r_div_epsilon':float(q0/e) if pole_regular else None,'pole_regularity_exact':pole_regular,'actual_vprime0':vp0,'stored_w0':w0,'grid_count':len(grid),'interval_count':len(knots)-1,'spline_axis':int(data[label+'__axis'][0]),'recorded_Qr_delta':float(np.max(np.abs(qr))/e-record['checks']['max_abs_Q_over_r_div_epsilon']),'max_abs_original_minus_normalized_Q':float(np.max(np.abs(Q-normq))),'max_abs_vprime_minus_w':float(np.max(np.abs(vp-w))),'max_abs_u_sampled':float(np.max(np.abs(u))),'boundary_vR':float(P(R)[0]),'boundary_w0':w0}
    for name,mask in [('r_lt_1e-4',grid<1e-4),('r_1e-4_to_1e-2',(grid>=1e-4)&(grid<1e-2)),('r_1e-2_to_1',(grid>=1e-2)&(grid<=1.)),('r_gt_1',grid>1.)]:
        out['max_Qr_over_e_'+name]=float(np.max(np.abs(qr[mask]))/e)
    return out

fine=[diagnostics(x) for x in result['solves'] if x['kind']=='nonlinear' and x['tol']==1e-8]
comparisons={}
for e in (.025,.05,.1):
    E={}
    for sig in (1,2):
        key=f'epsilon_{e:g}_sigma_{sig}'
        lbl=lambda R,t: f'nonlinear_s{sig}_e{e:g}_R{R}_tol{t:.0e}'
        co=poly(lbl(8,1e-6))(source_grid)[0]; f8=poly(lbl(8,1e-8))(source_grid)[0]; f12=poly(lbl(12,1e-8))(source_grid)[0]
        E[sig]=max(float(np.max(np.abs(co-f8))),float(np.max(np.abs(f8-f12))))
        comparisons[key]={'tolerance_relative_change_R8':relative(co,f8),'reservoir_relative_change_R8_to_R12':relative(f8,f12),'absolute_profile_uncertainty_E':E[sig]}
    v1=poly(f'nonlinear_s1_e{e:g}_R12_tol1e-08')(source_grid)[0]
    v2=poly(f'nonlinear_s2_e{e:g}_R12_tol1e-08')(source_grid)[0]
    comparisons[f'ordering_e{e:g}']={'min_v2':float(np.min(v2)),'min_v1_minus_v2':float(np.min(v1-v2)),'threshold_v2':10*E[2],'threshold_difference':10*(E[1]+E[2])}
linear={}
for sig in (1,2):
    ref=data[f'bessel_reference_sigma_{sig}__source_grid']
    for R in (8,12):
        label=f'linear_s{sig}_e1_R{R}_tol1e-08'
        v=poly(label)(source_grid)[0]
        linear[label]={'saved_infinite_bessel_relative_error':relative(v,ref)}
        # Independent Green quadrature at five fixed grid points.
        lam=np.sqrt(sig)
        def F(s): return 0. if s<=0. or s>=1. else 2*s*np.exp(1.-1./(1.-s*s))/(1.-s*s)**2
        def zgreen(r):
            if r==0.: return lam/2*quad(lambda s:k1(lam*s)*F(s)*s,0,1,epsabs=1e-12)[0]
            left=quad(lambda s:i1(lam*s)*F(s)*s,0,min(r,1),epsabs=1e-12)[0]
            right=0. if r>=1 else quad(lambda s:k1(lam*s)*F(s)*s,r,1,epsabs=1e-12)[0]
            return (k1(lam*r)*left+i1(lam*r)*right)/r
        pts=(0.,.25,.5,.75,1.)
        linear[label]['green_spot_max_abs_saved_reference_error']=max(abs(zgreen(r)-ref[round(r*4096)]) for r in pts)
zero={}
for sig in (1,2):
    label=f'zero_s{sig}_zero_R8_tol1e-08'; r=np.linspace(0,8,8001); v=poly(label)(r)[0]
    zero[label]=float(np.max(np.abs(r*v)))
nonlinear=[x for x in comparisons.values() if 'tolerance_relative_change_R8' in x]
ordering=[x for x in comparisons.values() if 'min_v2' in x]
independent_gates={
 'fine_status':len(fine)==12 and all(x['status']==0 for x in fine),
 'graph_safety':all(x['max_abs_u_sampled']<.9 for x in fine),
 'boundary':all(abs(x['boundary_vR'])<1e-9 and abs(x['boundary_w0'])<1e-9 for x in fine),
 'pole_regularity':all(x['pole_regularity_exact'] for x in fine),
 'Q_over_r':all(x['max_abs_Q_over_r_div_epsilon']<1e-5 for x in fine),
 'tolerance_refinement':all(x['tolerance_relative_change_R8']<5e-4 for x in nonlinear),
 'reservoir_refinement':all(x['reservoir_relative_change_R8_to_R12']<1e-5 for x in nonlinear),
 'linear_reference_fine_R8_and_R12':all(x['saved_infinite_bessel_relative_error']<1e-6 for x in linear.values()),
 'zero_source':all(x<1e-10 for x in zero.values()),
 'ordering':all(x['min_v2']>x['threshold_v2'] and x['min_v1_minus_v2']>x['threshold_difference'] for x in ordering)}
output={'source_code_sha256':hashlib.sha256((D/'nonlinear_graph_numerical_003.py').read_bytes()).hexdigest(),'design_sha256':hashlib.sha256((D/'nonlinear_numerical_design.json').read_bytes()).hexdigest(),'mesh_plan_sha256':hashlib.sha256((D/'nonlinear_numerical_mesh_plan.json').read_bytes()).hexdigest(),'execution_sha256':hashlib.sha256((D/'nonlinear_numerical_execution_003.json').read_bytes()).hexdigest(),'recorded_gates':result.get('gates'),'independent_gates':independent_gates,'recorded_status':result['status'],'solve_count':len(result['solves']),'solver_statuses':sorted(set(x.get('solver_status') for x in result['solves'])),'fine_nonlinear':fine,'source_disk_comparisons':comparisons,'fine_linear_reference':linear,'zero_source_max_abs_u':zero,'optional_K_recorded':result.get('optional_K_diagnostic')}
(D/'nonlinear_numerical_reanalysis_003.json').write_text(json.dumps(output,indent=2,sort_keys=True)+'\n',encoding='utf-8')
print('saved-spline audit complete',len(fine),'fine nonlinear cases')




