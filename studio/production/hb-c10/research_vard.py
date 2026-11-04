"""Query the centrally throttled source research helper for concrete healthcare objects."""
from pathlib import Path
import subprocess
R=Path(__file__).resolve().parents[3];P=Path(__file__).resolve().parent
for name,query in [('envelope','blank white envelope'),('dental','intitle:"dental chair"'),('telephone','intitle:"corded telephone"'),('pressure','intitle:sphygmomanometer'),('emergency','Finland hospital emergency entrance'),('taxi','Finland taxi'),('waiting','empty hospital waiting room'),('private','Mehiläinen building'),('occupational','Terveystalo building')]:
    out=P/f'vard-{name}-research.json'
    if out.exists():continue
    print('Research',name,query,flush=True);subprocess.run([str(R/'.venv/bin/python'),str(R/'studio/production/remaining/commons.py'),'--search',query,'--output',str(out),'--limit','8'],check=True)
print('Healthcare object source research complete.',flush=True)
