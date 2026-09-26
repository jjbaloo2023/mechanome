"""Check the cached fit-table observation contract; never fit or infer noise."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RESEARCH = ROOT / 'research'

def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    design_path = RESEARCH / 'locmofit_contract_design.json'
    design = json.loads(design_path.read_text(encoding='utf-8'))
    if datetime.now(timezone.utc) >= datetime.fromisoformat(design['deadline_utc'].replace('Z', '+00:00')):
        raise RuntimeError('Contract check deadline passed')
    audit_path = RESEARCH / 'data_audit.json'
    audit = json.loads(audit_path.read_text(encoding='utf-8'))
    frames = []
    inputs = []
    for table in audit['tables']:
        path = ROOT / 'cache' / 'smlm_locmofit' / 'audit' / table['path']
        digest = sha256(path)
        if digest != table['sha256']:
            raise ValueError(f'Input hash changed: {path}')
        frame = pd.read_csv(path)
        frames.append(frame)
        inputs.append({'path': str(path.relative_to(ROOT)), 'sha256': digest, 'rows': len(frame), 'columns': list(frame.columns)})
    data = pd.concat(frames, ignore_index=True)
    radius = data['radius'].to_numpy()
    theta = np.deg2rad(data['theta'].to_numpy())
    predictions = {
        'curvature': 1 / radius,
        'surface_area': 4 * np.pi * radius**2 * np.sin(theta/2)**2,
        'rim_length': 2 * np.pi * np.abs(radius * np.sin(theta)),
        'projected_area': np.pi * (radius * np.sin(theta))**2,
    }
    identities = {}
    for field, expected in predictions.items():
        observed = data[field].to_numpy()
        error = np.abs(observed-expected) / np.maximum(np.maximum(np.abs(observed), np.abs(expected)), 1e-12)
        identities[field] = {'max_relative_error': float(error.max()), 'rows_above_tolerance': int((error > design['identity_relative_tolerance']).sum()), 'worst_source_key': data.loc[int(error.argmax()), ['cell_line','file_number','ID']].to_dict()}
    flag = data['disconnected_sites'].astype(str).str.lower().eq('true')
    policies = {
        'all_deposited_raw': np.ones(len(data), dtype=bool),
        'deposited_corrected_unflagged': (~flag).to_numpy(),
        'raw_nonnegative_unflagged': ((~flag) & (data['curvature'] >= 0)).to_numpy(),
    }
    supports = {}
    for name, mask in policies.items():
        angle_name = 'theta_corrected' if name == 'deposited_corrected_unflagged' else 'theta'
        selected = data.loc[mask]
        deep = selected[angle_name] > 90
        supports[name] = {'rows': len(selected), 'angle_field': angle_name, 'beyond_hemisphere_rows': int(deep.sum()), 'beyond_hemisphere_fraction': float(deep.mean()), 'by_cell_line': {str(k): {'rows':len(v), 'beyond_hemisphere_rows':int((v[angle_name]>90).sum())} for k,v in selected.groupby('cell_line')}}
    result = {'task_id': design['task_id'], 'completed_at_utc': datetime.now(timezone.utc).isoformat(), 'source_sha256': sha256(Path(__file__)), 'design_sha256': sha256(design_path), 'audit_sha256': sha256(audit_path), 'inputs': inputs, 'rows': len(data), 'same_schema_all_tables': all(x['columns'] == inputs[0]['columns'] for x in inputs), 'schema': inputs[0]['columns'], 'identities': identities, 'supports': supports, 'negative_raw_curvature_rows': int((data['curvature']<0).sum()), 'corrected_flat_rows': int((data['curvature_corrected']==0).sum()), 'missing_likelihood_ingredients': ['localization xyz coordinates','per-localization covariance/precision','site ROI and background weight','fitted translation and orientation','extra broadening','joint fitted area-angle covariance','localization count and linkage/sampling calibration','exact historical fitter/settings identity'], 'scope': 'Geometry columns are same-fit transforms, not independent validation. Beyond-hemisphere counts are descriptive and do not reject a mechanism.'}
    out = RESEARCH / 'locmofit_contract_checks.json'
    with out.open('x', encoding='utf-8') as stream:
        json.dump(result, stream, indent=2); stream.write('\n')
    print(json.dumps({key:result[key] for key in ['rows','same_schema_all_tables','identities','supports','negative_raw_curvature_rows']},indent=2))

if __name__ == '__main__':
    main()
