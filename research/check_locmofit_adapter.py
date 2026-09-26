"""Check adapter compatibility against the preserved pre-change source and tables."""
from pathlib import Path
from datetime import datetime,timezone
import dataclasses,hashlib,importlib.util,json,sys
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
from validation.realdata import ingest_smlm_locmofit as current

p=ROOT/'research'
if datetime.now(timezone.utc)>=datetime.fromisoformat('2026-09-26T14:23:43+00:00'):
    raise RuntimeError('Implementation validation deadline passed')
audit=json.loads((p/'data_audit.json').read_text(encoding='utf-8'))
files=[]
for table in audit['tables']:
    f=ROOT/'cache/smlm_locmofit/audit'/table['path']
    assert hashlib.sha256(f.read_bytes()).hexdigest()==table['sha256']
    files.append(str(f))
old_path=p/'locmofit_adapter_before_001/ingest_smlm_locmofit.py'
spec=importlib.util.spec_from_file_location('locmofit_legacy_check',old_path)
legacy=importlib.util.module_from_spec(spec);sys.modules[spec.name]=legacy;spec.loader.exec_module(legacy)
# Only the file listing is adapted to the existing audited nested cache; inputs
# are neither copied nor rewritten, and both versions receive identical paths.
with patch.object(current.glob,'glob',return_value=sorted(files)):
    before=legacy.ingest_locmofit('audited-cache')
    after=current.ingest_locmofit('audited-cache')
    corrected=current.ingest_locmofit('audited-cache',geometry='corrected')
    exploratory=current.ingest_locmofit('audited-cache',legacy_curvature_sigma=True)
    all_sites=current.ingest_locmofit('audited-cache',geometry='corrected',drop_disconnected=False)
fields=['site_id','cell_line','file_number','psi_rad','theta_deg','H_inv_nm','R_nm','surface_area_nm2','projected_area_nm2']
assert len(before.sites)==len(after.sites)==2551
for a,b,e in zip(before.sites,after.sites,exploratory.sites):
    assert all(getattr(a,k)==getattr(b,k) for k in fields)
    assert b.H_sigma_inv_nm is None
    assert e.H_sigma_inv_nm==a.H_sigma_inv_nm
assert len(corrected.sites)==2574 and len(all_sites.sites)==2831
assert sum(s.H_inv_nm==0 for s in corrected.sites)==23
# Whole corrected cohort can serialize without nonstandard NaN/Infinity.
encoded=json.dumps([dataclasses.asdict(s) for s in corrected.sites],allow_nan=False)
assert len(json.loads(encoded))==2574
result={'task_id':'locmofit-adapter-001','completed_at_utc':datetime.now(timezone.utc).isoformat(),'checks':{'audited_tables_sha256':len(files),'legacy_default_sites':len(before.sites),'new_default_sites':len(after.sites),'all_legacy_geometry_fields_exactly_equal':True,'all_default_uncertainties_unknown':True,'explicit_legacy_heuristics_exactly_equal':True,'corrected_unflagged_sites':len(corrected.sites),'corrected_flat_sites':23,'corrected_all_sites':len(all_sites.sites),'corrected_cohort_strict_json':True},'file_hashes':{str(f.relative_to(ROOT)):hashlib.sha256(f.read_bytes()).hexdigest() for f in [Path(__file__),old_path,Path(current.__file__)]},'scope':'Adapter compatibility only; no empirical fit, physical validation, or deposited data change.'}
with (p/'locmofit_adapter_validation.json').open('x',encoding='utf-8') as f:json.dump(result,f,indent=2);f.write('\n')
print(json.dumps(result,indent=2))
