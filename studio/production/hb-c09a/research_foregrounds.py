"""Research licensed source-specific physical objects and historical contexts."""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import json,requests,time
P=Path('studio/production/hb-c09a/research');P.mkdir(exist_ok=True)
queries=['filetype:bitmap Finland family 1900','filetype:bitmap Finland farm 1940 women','filetype:bitmap Finnish women factory 1940','filetype:bitmap Finland textile factory women','filetype:bitmap Helsinki worker home 1911','filetype:bitmap Finland agriculture 1920','filetype:bitmap Finland daycare children','filetype:bitmap Finland kindergarten toys','filetype:bitmap wooden toy car','filetype:bitmap doll toy','filetype:bitmap cooking father child','filetype:bitmap household laundry','filetype:bitmap Helsinki nurse 1900','filetype:bitmap Finland women teacher 1900']
def run(q):
    p=P/(q.replace(':','-').replace(' ','-')+'.json')
    if p.exists():return
    for attempt in range(4):
        r=requests.get('https://commons.wikimedia.org/w/api.php',params=dict(action='query',format='json',generator='search',gsrsearch=q,gsrnamespace=6,gsrlimit=10,prop='imageinfo',iiprop='url|extmetadata',iiurlwidth=1200),headers={'User-Agent':'HomebrewStudyStudio/1.0'},timeout=90)
        if r.status_code!=429:break
        time.sleep(4)
    r.raise_for_status();d=r.json();p.write_text(json.dumps(d,ensure_ascii=False,indent=2));print(q,[v['title'] for v in d.get('query',{}).get('pages',{}).values()],flush=True)
with ThreadPoolExecutor(max_workers=3) as ex:list(ex.map(run,queries))
