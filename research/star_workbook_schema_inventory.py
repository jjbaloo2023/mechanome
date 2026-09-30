"""One-shot, capped public workbook schema inventory; no numeric analysis."""
import hashlib
import io
import json
import time
import urllib.request
import urllib.parse
import zipfile
import xml.etree.ElementTree as ET
from collections import Counter
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DESIGN = json.loads((ROOT / 'star_workbook_schema_design.json').read_text(encoding='utf-8'))
CACHE = ROOT / 'metadata' / 'star-workbook-001'
RESULT = ROOT / 'star_workbook_schema_result.json'

def now():
    return datetime.now(timezone.utc).isoformat()

record = {'task_id': DESIGN['task_id'], 'started_at_utc': now(), 'requests': [], 'status': 'started', 'scientific_calls': 0}

def save():
    RESULT.write_text(json.dumps(record, indent=2) + '\n', encoding='utf-8')

class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise RuntimeError('Redirect refused: no alternate endpoint/retry budget')

opener = urllib.request.build_opener(NoRedirect())

def fetch(url, cap, name):
    item = {'url': url, 'started_at_utc': now(), 'byte_cap': cap, 'status': 'reserved'}
    record['requests'].append(item)
    save()
    request = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (public research schema audit)'})
    start = time.monotonic()
    with opener.open(request, timeout=30) as response:
        item.update(status_code=response.status, content_type=response.headers.get('Content-Type'), content_length=response.headers.get('Content-Length'))
        if response.headers.get('Content-Length') and int(response.headers['Content-Length']) > cap:
            raise RuntimeError('Content-Length exceeds registered cap')
        chunks, total = [], 0
        while True:
            if time.monotonic() - start > 30:
                raise RuntimeError('Request elapsed limit exceeded')
            chunk = response.read(min(65536, cap + 1 - total))
            if not chunk:
                break
            chunks.append(chunk)
            total += len(chunk)
            if total > cap:
                raise RuntimeError('Response exceeds registered byte cap')
    data = b''.join(chunks)
    (CACHE / name).write_bytes(data)
    item.update(status='completed', completed_at_utc=now(), bytes=len(data), sha256=hashlib.sha256(data).hexdigest(), local_path='research/metadata/star-workbook-001/' + name)
    save()
    return data

class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self.current = None
    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            self.current = {'href': dict(attrs).get('href', ''), 'label': ''}
    def handle_data(self, data):
        if self.current is not None:
            self.current['label'] += data
    def handle_endtag(self, tag):
        if tag == 'a' and self.current is not None:
            self.links.append(self.current)
            self.current = None

def inspect(data):
    ns = {'s': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
    with zipfile.ZipFile(io.BytesIO(data)) as book:
        infos = book.infolist()
        size = sum(i.file_size for i in infos)
        if size > DESIGN['limits']['uncompressed_workbook_bytes']:
            raise RuntimeError('Workbook uncompressed size exceeds cap')
        strings = []
        if 'xl/sharedStrings.xml' in book.namelist():
            shared = ET.fromstring(book.read('xl/sharedStrings.xml'))
            strings = [''.join(t.text or '' for t in si.iter('{'+ns['s']+'}t')) for si in shared]
        wb = ET.fromstring(book.read('xl/workbook.xml'))
        rels = ET.fromstring(book.read('xl/_rels/workbook.xml.rels'))
        targets = {r.attrib['Id']: r.attrib['Target'] for r in rels}
        sheets = []
        for sheet in wb.find('s:sheets', ns):
            rid = sheet.attrib['{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id']
            target = targets[rid]
            target = target.lstrip('/') if target.startswith('/') else 'xl/' + target
            xml = ET.fromstring(book.read(target))
            rows, labels, types = [], [], Counter()
            cell_count = 0
            for row in xml.findall('s:sheetData/s:row', ns):
                cells = []
                for c in row.findall('s:c', ns):
                    typ = c.attrib.get('t', 'n')
                    types[typ] += 1
                    v = c.find('s:v', ns)
                    value = v.text if v is not None else ''
                    if typ == 's' and value:
                        value = strings[int(value)]
                    elif typ == 'inlineStr':
                        value = ''.join(t.text or '' for t in c.findall('.//s:t', ns))
                    if value:
                        cell_count += 1
                        if typ in ('s', 'inlineStr', 'str'):
                            labels.append({'cell': c.attrib['r'], 'text': value[:500]})
                        cells.append({'cell': c.attrib['r'], 'type': typ, 'value': value[:160]})
                if cells:
                    rows.append({'row': row.attrib['r'], 'nonempty_count': len(cells), 'first_cells': cells[:12]})
            dimension = xml.find('s:dimension', ns)
            sheets.append({'name': sheet.attrib['name'], 'xml': target, 'dimension': dimension.attrib if dimension is not None else None, 'nonempty_rows': len(rows), 'nonempty_cells': cell_count, 'cell_types': dict(types), 'first_rows': rows[:15], 'last_rows': rows[-2:], 'text_labels_count': len(labels), 'text_labels': labels[:1000]})
        return {'uncompressed_bytes': size, 'zip_entries': len(infos), 'shared_strings': len(strings), 'sheets': sheets}

if __name__ == '__main__':
    if RESULT.exists():
        raise SystemExit('Refusing repeat: result ledger already exists')
    CACHE.mkdir(parents=True, exist_ok=False)
    save()
    try:
        html = fetch(DESIGN['primary_url'], DESIGN['limits']['publisher_html_bytes'], 'publisher.html')
        parser = Links()
        parser.feed(html.decode('utf-8'))
        candidates = [x for x in parser.links if '.xlsx' in x['href'].lower() and 'source data' in x['label'].lower()]
        record['matching_links'] = candidates
        save()
        unique = {urllib.parse.urljoin(DESIGN['primary_url'], x['href']) for x in candidates}
        if len(unique) != 1:
            raise RuntimeError('Expected one exact Source Data XLSX target; no rescue permitted')
        url = unique.pop()
        if urllib.parse.urlparse(url).scheme != 'https':
            raise RuntimeError('Non-HTTPS target refused')
        data = fetch(url, DESIGN['limits']['workbook_bytes'], 'source_data.xlsx')
        record['workbook'] = inspect(data)
        record['status'] = 'schema_inspected'
    except Exception as exc:
        record['status'] = 'stopped_at_first_failure'
        record['error'] = type(exc).__name__ + ': ' + str(exc)
    finally:
        record['finished_at_utc'] = now()
        save()
    print(json.dumps({k:v for k,v in record.items() if k != 'workbook'}, indent=2))
    if 'workbook' in record:
        print(json.dumps([{k:v for k,v in s.items() if k in ('name','dimension','nonempty_rows','nonempty_cells','text_labels_count')} for s in record['workbook']['sheets']], indent=2))
