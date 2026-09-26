"""Check the predeclared silhouette alternative without refitting anything."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json
import numpy as np
import pandas as pd
R=Path(__file__).resolve().parents[1]; p=R/'research'
if datetime.now(timezone.utc)>=datetime.fromisoformat('2026-09-25T04:00:37+00:00'):
    raise RuntimeError('Deadline passed')
audit=json.loads((p/'data_audit.json').read_text(encoding='utf-8'))
frames=[]; variants={}
for table in audit['tables']:
    file=R/'cache/smlm_locmofit/audit'/table['path']
    assert hashlib.sha256(file.read_bytes()).hexdigest()==table['sha256']
    d=pd.read_csv(file); frames.append(d)
    variants.setdefault(tuple(d.columns),[]).append(table['path'])
d=pd.concat(frames,ignore_index=True); r=d['radius'].to_numpy(); t=np.deg2rad(d['theta'].to_numpy())
expected=np.pi*r**2*np.where(d['theta'].to_numpy()>90,1,np.sin(t)**2)
observed=d['projected_area'].to_numpy(); error=np.abs(observed-expected)/np.maximum(np.maximum(abs(observed),abs(expected)),1e-12)
result={'task_id':'locmofit-contract-001','completed_at_utc':datetime.now(timezone.utc).isoformat(),'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'amendment_sha256':hashlib.sha256((p/'locmofit_projection_amendment.json').read_bytes()).hexdigest(),'candidate':'orthogonal silhouette area: pi R^2 sin^2(theta) at theta<=90deg, pi R^2 at theta>90deg','rows':len(d),'max_relative_error':float(error.max()),'rows_above_1e_minus4':int((error>1e-4).sum()),'schema_variants':[{'columns':list(k),'table_paths':v} for k,v in variants.items()],'common_columns':sorted(set.intersection(*(set(x) for x in variants))),'scope':'A checked numerical identity for stored raw geometry, not proof of an author export implementation or independent measurement.'}
with (p/'locmofit_projection_checks.json').open('x',encoding='utf-8') as f:json.dump(result,f,indent=2);f.write('\n')
print(json.dumps(result,indent=2))
