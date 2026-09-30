"""One registered exact-rational observation check; no empirical inputs."""
import json
from fractions import Fraction as F
from pathlib import Path
from datetime import datetime, timezone

root=Path(__file__).resolve().parent
out=root/'star_observation_checks.json'
if out.exists():
    raise SystemExit('Registered invocation already consumed; no rerun')
design=json.loads((root/'star_observation_design.json').read_text(encoding='utf-8'))
def now():return datetime.now(timezone.utc).isoformat()
def save():out.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
def mm(a,b):return [[sum(x*y for x,y in zip(row,col)) for col in zip(*b)] for row in a]
def trans(a):return list(map(list,zip(*a)))
def fmt(a):return [[str(x) for x in row] for row in a]
result={'task_id':design['task_id'],'started_at_utc':now(),'scientific_invocations':1,'invocation_cap':1,'status':'reserved','cases':[]}
save()
try:
    for index,case in enumerate(design['checks']['fixed_cases']):
        ag,ar,vg,vr=map(F,case)
        M=[[F(1),-ag],[F(1),-ar]]
        d=ag-ar
        r={'case':index+1,'inputs':list(map(str,(ag,ar,vg,vr))),'difference':str(d)}
        if d==0:
            null=[[ag],[F(1)]]
            assert mm(M,null)==[[0],[0]]
            r.update(status='nonidentifiable',null_direction=fmt(null),null_identity_passed=True)
        else:
            B=[[-ar/d,ag/d],[-1/d,1/d]]
            assert mm(B,M)==[[1,0],[0,1]]
            V=[[vg,F(0)],[F(0),vr]]
            C=mm(mm(B,V),trans(B))
            formula=[[(ar*ar*vg+ag*ag*vr)/(d*d),(ar*vg+ag*vr)/(d*d)],[(ar*vg+ag*vr)/(d*d),(vg+vr)/(d*d)]]
            assert C==formula
            cross=mm(V,trans(B))
            assert cross[0][1]==-vg/d and cross[1][1]==vr/d
            det=C[0][0]*C[1][1]-C[0][1]**2
            assert det==vg*vr/(d*d)>0
            r.update(status='passed',inverse=fmt(B),covariance=fmt(C),covariance_determinant=str(det),channel_u_covariance=[str(cross[0][1]),str(cross[1][1])],inverse_infinity_norm=str(max(sum(abs(x) for x in row) for row in B)),inverse_identity_passed=True,covariance_identity_passed=True,positive_definite=True)
        result['cases'].append(r)
        save()
    assert result['cases'][3]['covariance'][1][1]=='200'
    assert result['cases'][4]['covariance'][1][1]=='2000000'
    result['status']='passed'
except Exception as exc:
    result.update(status='failed',error=repr(exc))
finally:
    result['finished_at_utc']=now()
    save()
print(json.dumps(result,indent=2))
