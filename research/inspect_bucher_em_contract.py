"""Bounded, read-only XLSX package inventory; no Excel/formula execution or fit."""
from pathlib import Path
import collections, datetime, hashlib, io, json, urllib.request, zipfile
import xml.etree.ElementTree as ET
R=Path(__file__).resolve().parent
D=R/'bucher_em_contract_design.json'
NS={'m':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
def now(): return datetime.datetime.now(datetime.timezone.utc).isoformat()
def inspect(data):
    out=[]
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        total=sum(i.file_size for i in z.infolist())
        if total>5000000: raise ValueError('Expanded package exceeds registered bound')
        shared=[]
        if 'xl/sharedStrings.xml' in z.namelist():
            shared=[''.join(e.itertext()) for e in ET.fromstring(z.read('xl/sharedStrings.xml'))]
        rel={e.attrib['Id']:e.attrib['Target'] for e in ET.fromstring(z.read('xl/_rels/workbook.xml.rels'))}
        wb=ET.fromstring(z.read('xl/workbook.xml'))
        for sh in wb.find('m:sheets',NS):
            target=rel[sh.attrib['{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id']]
            target=target.lstrip('/') if target.startswith('/') else 'xl/'+target
            root=ET.fromstring(z.read(target)); rows=[]; labels=[]; cols=collections.Counter(); formulas=[]
            for row in root.findall('m:sheetData/m:row',NS):
                vals={}
                for c in row:
                    addr=c.attrib['r']; v=c.find('m:v',NS); val=None if v is None else v.text
                    if c.attrib.get('t')=='s' and val is not None: val=shared[int(val)]
                    elif c.attrib.get('t')=='inlineStr': val=''.join(c.find('m:is',NS).itertext())
                    if c.find('m:f',NS) is not None: formulas.append({'cell':addr,'formula':c.find('m:f',NS).text,'cached_value':val})
                    if val is not None:
                        vals[addr]=val; cols[''.join(x for x in addr if x.isalpha())]+=1
                        if c.attrib.get('t') in ['s','inlineStr']: labels.append({'cell':addr,'text':val})
                if vals: rows.append(vals)
            dim=root.find('m:dimension',NS)
            out.append({'name':sh.attrib['name'],'dimension':None if dim is None else dim.attrib.get('ref'),'nonempty_rows':len(rows),'nonempty_cells_by_column':dict(cols),'first_8_rows':rows[:8],'last_2_rows':rows[-2:],'text_cells':labels,'formulas':formulas})
    return {'expanded_bytes':total,'sheets':out}
def main():
    started=now(); design=json.loads(D.read_text()); cache=R/'.cache-bucher-em-001'; cache.mkdir(exist_ok=True)
    result={'task_id':design['task_id'],'started_at_utc':started,'design_sha256':hashlib.sha256(D.read_bytes()).hexdigest(),'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'files':[],'interpretation':'Structure only; labels and counts are not independently validated biological sampling or effects.'}
    for spec in design['files']:
        rec={'id':spec['id'],'name':spec['name'],'url':spec['download_url'],'expected_bytes':spec['size'],'expected_md5':spec['computed_md5'],'started_at_utc':now()}
        try:
            request=urllib.request.Request(spec['download_url'],headers={'User-Agent':'Mechanome public-data provenance audit'})
            with urllib.request.urlopen(request,timeout=20) as response:
                data=response.read(100001); rec['resolved_url']=response.url
            rec.update(bytes=len(data),md5=hashlib.md5(data).hexdigest(),sha256=hashlib.sha256(data).hexdigest())
            if len(data)!=spec['size'] or rec['md5']!=spec['computed_md5']: raise ValueError('Publisher length or MD5 mismatch')
            path=cache/spec['name']; path.write_bytes(data)
            rec.update(status='verified',cache_path=str(path),inventory=inspect(data))
        except Exception as e: rec.update(status='stopped',error=type(e).__name__+': '+str(e))
        rec['finished_at_utc']=now(); result['files'].append(rec)
    result['finished_at_utc']=now()
    (R/'bucher_em_contract_001.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    for f in result['files']:
        print(json.dumps({k:f.get(k) for k in ['id','status','bytes','error']}))
        for s in f.get('inventory',{}).get('sheets',[]): print(json.dumps({k:s[k] for k in ['name','dimension','nonempty_rows','nonempty_cells_by_column','text_cells']}))
if __name__=='__main__': main()
