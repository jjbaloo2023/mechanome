"""Saved-polynomial diagnosis only; no boundary-value solver calls."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import numpy as np
from scipy.interpolate import PPoly

HERE = Path(__file__).resolve().parent

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def analyze(poly, r, sigma, eps):
    v, w = poly(r)
    vp, wp = poly(r, 1)
    vpp = poly(r, 2)[0]
    c = np.zeros_like(r)
    cp_r = np.zeros_like(r)
    inside = r < 1
    c[inside] = eps * np.exp(1 - 1/(1-r[inside]**2))
    cp_r[inside] = -2*c[inside]/(1-r[inside]**2)**2
    A = 1 - (r*v)**2
    tv, tw = 2*v+r*vp-c, 2*v+r*w-c
    # The physical flux differentiates v, not the auxiliary w component.
    d, dp = vp-w, vpp-wp
    with np.errstate(divide='ignore', invalid='ignore'):
        physical = -A*(3*vp/r+vpp-cp_r)-tv*v*(v+r*vp)+(.5*tv**2+sigma)*v
        system = -A*(3*w/r+wp-cp_r)-tw*v*(v+r*w)+(.5*tw**2+sigma)*v
        defect = -A*(3*d/r+dp)-r*v*d*(v+r*w)-.5*v*r*r*d*d
    pole = r == 0
    physical[pole] = -4*vpp[pole]+cp_r[pole]-tv[pole]*v[pole]**2+(.5*tv[pole]**2+sigma)*v[pole]
    system[pole] = -4*wp[pole]+cp_r[pole]-tw[pole]*v[pole]**2+(.5*tw[pole]**2+sigma)*v[pole]
    defect[pole] = -4*dp[pole]
    ix = int(np.argmax(abs(physical)))
    interval = min(int(np.searchsorted(poly.x,r[ix],side='right')-1),len(poly.x)-2)
    return {
        'points':len(r), 'max_physical_normalized':float(max(abs(physical))/eps),
        'max_system_normalized_diagnostic_only':float(max(abs(system))/eps),
        'max_defect_normalized':float(max(abs(defect))/eps),
        'decomposition_max_abs_error_normalized':float(max(abs(physical-system-defect))/eps),
        'max_abs_vprime_minus_w':float(max(abs(d))),
        'max_abs_vsecond_minus_wprime':float(max(abs(dp))),
        'physical_argmax_r':float(r[ix]),
        'physical_argmax_interval':[float(poly.x[interval]),float(poly.x[interval+1])],
        'at_physical_argmax':{'physical_over_epsilon':float(physical[ix]/eps),'system_over_epsilon':float(system[ix]/eps),'defect_over_epsilon':float(defect[ix]/eps)},
        'pole':{'physical_over_epsilon':float(physical[0]/eps),'system_over_epsilon':float(system[0]/eps),'defect_over_epsilon':float(defect[0]/eps)}
    }

def main():
    start=datetime.now(timezone.utc).isoformat()
    names=('nonlinear_numerical_results_002.json','nonlinear_numerical_profiles_002.npz')
    run=json.loads((HERE/names[0]).read_text())
    arrays=np.load(HERE/names[1],allow_pickle=False)
    rows=[]
    for rec in run['solves']:
        if rec['kind']!='nonlinear' or rec['tol']!=1e-8:
            continue
        label=rec['label']
        poly=PPoly.construct_fast(arrays[label+'__c'],arrays[label+'__x'],axis=int(arrays[label+'__axis'][0]))
        x=poly.x
        assert float(poly(0., 1)[0]) == 0.0 and float(poly(0.)[1]) == 0.0, "Pole limit needs exact regularity; inspect rather than substituting."
        original=np.unique(np.r_[0.,np.geomspace(1e-10,.999999,6000),np.linspace(1.,rec['R'],6001)])
        # More stringent diagnostic grid samples every interval, both knot sides.
        fractions=np.linspace(0,1,17)
        per_interval=(x[:-1,None]+np.diff(x)[:,None]*fractions).ravel()
        left=np.nextafter(x[1:-1],-np.inf)
        right=np.nextafter(x[1:-1],np.inf)
        dense=np.unique(np.r_[original,per_interval,left,right])
        row={'label':label,'epsilon':rec['epsilon'],'sigma':rec['sigma'],
             'actual_vprime_at_zero':float(poly(0., 1)[0]),'actual_w_at_zero':float(poly(0.)[1]),
             'fixed_grid':analyze(poly,original,rec['sigma'],rec['epsilon']),
             'augmented_interval_grid':analyze(poly,dense,rec['sigma'],rec['epsilon'])}
        expected=rec['checks']['max_abs_Q_over_r_div_epsilon']
        assert np.isclose(row['fixed_grid']['max_physical_normalized'],expected,rtol=1e-8,atol=1e-12)
        assert row['augmented_interval_grid']['decomposition_max_abs_error_normalized']<1e-12
        rows.append(row)
    out={'task_id':'nonlinear-residual-postmortem-001','started_at_utc':start,
         'completed_at_utc':datetime.now(timezone.utc).isoformat(),'new_BVP_calls':0,
         'scope':'Diagnostic identity only; physical gate remains failed and K suppressed.',
         'input_sha256':{str(Path('research')/n):sha(HERE/n) for n in names},
         'script_sha256':sha(Path(__file__)), 'fine_cases':rows}
    (HERE/'nonlinear_residual_postmortem.json').write_text(json.dumps(out,indent=2)+'\n')
    for row in rows:
        d=row['augmented_interval_grid']
        print(row['label'], d['max_physical_normalized'],d['max_system_normalized_diagnostic_only'],d['max_defect_normalized'],d['physical_argmax_r'],d['physical_argmax_interval'])

if __name__=='__main__':
    main()
