"""Independent objective, derivative and pole-asymptotic audit; no new fits."""
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
import numpy as np
from research import cap_observation_v2 as fitting

ROOT=Path(__file__).resolve().parents[1]
R=ROOT/'research'
DEADLINE=datetime.fromisoformat('2026-09-25T03:10:12+00:00')

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def run():
    source=R/'cap_observation_results_002.json'
    results=json.loads(source.read_text(encoding='utf-8'))
    r=np.linspace(0,.7,101)
    h=.4
    stable=fitting.inc(r,h)
    exact=1/h-np.sqrt(1/h**2-r*r)
    derivative=fitting.dgdh(r,h)
    complex_derivative=np.imag(fitting.inc(r,h+1e-30j))/1e-30
    function_error=float(np.max(abs(stable-exact)))
    derivative_error=float(np.max(abs(derivative-complex_derivative)))
    assert function_error<1e-12 and derivative_error<1e-12
    nodes,weights=np.polynomial.legendre.leggauss(401)
    profiles={}; supports={}; rows=[]
    for record in results.get('records',[]):
        if datetime.now(timezone.utc)>=DEADLINE:
            break
        if record.get('status')!='fit':
            rows.append({'record_id':record.get('record_id'),'status':'not_a_fit'})
            continue
        label=record['label']; amplitude=record['amplitude']; x=record['x']
        if label not in profiles:
            profiles[label]=fitting.profile(label,amplitude,x)
        path,digest,rs,zs,psis,p=profiles[label]
        assert digest==record['state_sha256']
        key=(label,record['Rfit'])
        if key not in supports:
            physical_r=(nodes+1)*record['Rfit']/2
            rho=fitting.inverse_r(rs,physical_r,x)
            supports[key]=(physical_r,zs(rho)-p[1],psis(rho))
        physical_r,z,psi=supports[key]
        w=weights.copy()
        if record['weighting']=='uniform_material_alpha':
            w*=physical_r/np.cos(psi)
        w/=w.sum()
        h=record['h']; s=np.sqrt(1-(h*physical_r)**2)
        g=h*physical_r**2/(1+s)
        b=float(w@(z-g)); error=z-b-g
        derivative=physical_r**2/(s*(1+s)); centered=derivative-w@derivative
        mse=float(w@(error*error)); rmse=np.sqrt(mse)
        correlation=abs(float(w@(error*centered)))/max(np.sqrt(mse*float(w@(centered*centered))),1e-30)
        shifted=z+.125; shifted_b=float(w@(shifted-g)); shifted_mse=float(w@((shifted-shifted_b-g)**2))
        row={'record_id':record['record_id'],'objective_401':mse,'rmse_401':float(rmse),
             'rmse_difference_401_vs_201':float(abs(rmse-record['rmse'])),
             'normalized_stationarity_401':correlation,'stationarity_pass':bool(correlation<=1e-3),
             'offset_translation_objective_error':abs(shifted_mse-mse)}
        if record['window']==.1:
            c0,cdot=fitting.fr.coat(np.array([0.]),amplitude/2,x*x/2,.01)
            hp,zp,lp=p
            h2=(float(cdot[0])+hp*(lp-float(c0[0])*(hp-float(c0[0]))))/2
            coefficient=3/14 if record['weighting']=='uniform_r' else 1/4
            predicted=coefficient*h2*.1**2
            relative_error=abs((h-hp)-predicted)/abs(predicted)
            row.update(small_window_predicted_bias=float(predicted),small_window_observed_bias=float(h-hp),
                       asymptotic_relative_error=float(relative_error),asymptotic_2percent_gate=bool(relative_error<=.02))
        rows.append(row)
    data={'task_id':'cap-observation-001','observed_utc':datetime.now(timezone.utc).isoformat(),
          'source_sha256':sha(Path(__file__)),'result_sha256':sha(source),
          'stable_sphere_function_max_error':function_error,'complex_step_derivative_max_error':derivative_error,
          'checks':rows,'complete':len(rows)==len(results.get('records',[])),
          'method':'401-node objective/normal-equation check at stored201-node optima; analytic small-window prediction; no extra fit.',
          'limits':'No reoptimized quadrature-convergence claim, empirical likelihood, or independent biological evidence.'}
    with (R/'cap_observation_lead_checks.json').open('x',encoding='utf-8') as handle:
        json.dump(data,handle,indent=2);handle.write('\n')
    print(json.dumps({'checked':len(rows),'complete':data['complete'],
      'stationarity_failures':sum(not row.get('stationarity_pass',False) for row in rows),
      'max_stationarity':max([row.get('normalized_stationarity_401',0) for row in rows],default=0),
      'max_small_window_relative_error':max([row.get('asymptotic_relative_error',0) for row in rows],default=0)}))

if __name__=='__main__':
    run()
