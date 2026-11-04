"""Fetch reusable picture metadata for the chapter's source-specific scene plans."""
from pathlib import Path
import json,subprocess,sys,urllib.parse,concurrent.futures
ROOT=Path(__file__).resolve().parents[3];OUT=ROOT/'studio/production/hb-c08/research';OUT.mkdir(exist_ok=True)
queries=['Taivallahden peruskoulu','kindergarten Finland','school classroom Finland','school meal Finland','Helsinki preschool','Finnish school history','Tölö gymnasium','vocational school Finland','university lecture Finland','adult education Finland','Metropolia campus','student housing Finland','daycare Helsinki','children playing Finland','school books Finland','teacher Finland']
def run(q):
 p=OUT/(q.replace(' ','_')+'.json')
 if not p.exists():
  params=dict(action='query',generator='search',gsrsearch=q,gsrnamespace=6,gsrlimit=20,prop='imageinfo',iiprop='url|extmetadata',iiurlwidth=1920,format='json')
  cmd=['curl','-sS','-L','--connect-timeout','12','--max-time','40','--get','https://commons.wikimedia.org/w/api.php']
  for k,v in params.items():cmd+=['--data-urlencode',k+'='+str(v)]
  r=subprocess.run(cmd,capture_output=True)
  if r.returncode:print(q,r.stderr.decode()[:100],flush=True);return
  try:d=json.loads(r.stdout)
  except Exception:print(q,'bad json',r.stdout[:100],flush=True);return
  p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
 else:d=json.loads(p.read_text())
 print(q,[r['title'] for r in d.get('query',{}).get('pages',{}).values()],flush=True)
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:list(pool.map(run,queries))
