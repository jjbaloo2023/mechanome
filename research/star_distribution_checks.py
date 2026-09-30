"""One registered exact-rational counterexample; no empirical data or searches."""
from datetime import datetime, timezone
from fractions import Fraction as F
from pathlib import Path
import json
import hashlib

root=Path(__file__).resolve().parent
design_path=root/'star_distribution_design.json'
design=json.loads(design_path.read_text(encoding='utf-8'))
output=root/'star_distribution_checks.json'
def now():return datetime.now(timezone.utc).isoformat()
result={'task_id':design['task_id'],'started_at_utc':now(),'scientific_invocations':1,'invocation_cap':1,'distribution_pairs':1,'design_sha256':hashlib.sha256(design_path.read_bytes()).hexdigest(),'status':'reserved'}
with output.open('x',encoding='utf-8') as f:json.dump(result,f,indent=2)
def save():output.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
try:
    spec=design['assumptions']
    t=list(map(F,spec['t_values']))
    p=list(map(F,spec['weights_p']))
    q=list(map(F,spec['weights_q']))
    assert len(t)==len(p)==len(q)==4
    assert all(0 < x <= 1 for x in t)
    assert all(w > 0 for w in p+q)
    assert sum(p)==sum(q)==1 and p!=q
    moments_p=[sum(w*x**a for w,x in zip(p,t)) for a in spec['attenuation_coefficients']]
    moments_q=[sum(w*x**a for w,x in zip(q,t)) for a in spec['attenuation_coefficients']]
    assert moments_p==moments_q==[F(5,8),F(15,32)]
    delta=[a-b for a,b in zip(p,q)]
    coefficients=[12*d for d in delta]
    assert coefficients==[1,-3,3,-1]
    # delta mean = -(1/12) log(product(t_i ** (12*delta_weight_i))).
    product=F(1)
    for value,exponent in zip(t,coefficients):
        assert exponent.denominator==1
        product*=value**int(exponent)
    assert product==F(27,32) and 0 < product < 1
    result.update(status='passed',t_values=list(map(str,t)),weights_p=list(map(str,p)),weights_q=list(map(str,q)),normalization_p=str(sum(p)),normalization_q=str(sum(q)),strictly_positive_weights=True,finite_nonnegative_heights=True,total_amount_each='1',moments_p=list(map(str,moments_p)),moments_q=list(map(str,moments_q)),weight_difference=list(map(str,delta)),scaled_log_coefficients=list(map(str,coefficients)),log_product=str(product),exact_mean_p_minus_mean_q='log(32/27)/12',strict_positive_mean_gap_proof='27/32 is strictly between 0 and 1, so -log(27/32)/12 > 0',scientific_scope='Idealized finite axial distributions; no membrane geometry, empirical calibration, biological timing, or mechanism test.')
except Exception as exc:
    result.update(status='failed',error=repr(exc))
finally:
    result['finished_at_utc']=now()
    save()
print(json.dumps(result,indent=2))
