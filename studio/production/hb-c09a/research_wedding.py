"""Research physical wedding objects and Finnish ceremony institutions."""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import json,requests,time
P=Path('studio/production/hb-c09a/research');P.mkdir(exist_ok=True)
queries=['filetype:bitmap wedding rings close','filetype:bitmap engagement ring box','filetype:bitmap Finland district court exterior','filetype:bitmap Helsinki orthodox cathedral exterior','filetype:bitmap Helsinki lutheran church exterior']
def run(q):
    p=P/(q.replace(':','-').replace(' ','-')+'.json')
    if p.exists():return
    r=requests.get('https://commons.wikimedia.org/w/api.php',params=dict(action='query',format='json',generator='search',gsrsearch=q,gsrnamespace=6,gsrlimit=8,prop='imageinfo',iiprop='url|extmetadata',iiurlwidth=1200),headers={'User-Agent':'HomebrewStudyStudio/1.0'},timeout=90);r.raise_for_status();d=r.json();p.write_text(json.dumps(d,ensure_ascii=False,indent=2));print(q,[v['title'] for v in d.get('query',{}).get('pages',{}).values()],flush=True)
with ThreadPoolExecutor(max_workers=3) as ex:list(ex.map(run,queries))
