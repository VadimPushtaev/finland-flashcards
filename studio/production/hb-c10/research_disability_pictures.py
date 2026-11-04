"""Research exact concrete aids,accessibility and planning objects for disability services."""
from pathlib import Path
import subprocess
R=Path(__file__).resolve().parents[3];P=Path(__file__).resolve().parent
queries=[('notebook','intitle:blank notebook filetype:bitmap'),('centre','intitle:terveysasema 2024 filetype:bitmap'),('ramp','intitle:wheelchair ramp Finland filetype:bitmap'),('parking','intitle:disabled parking Finland filetype:bitmap'),('therapy','intitle:exercise ball filetype:bitmap'),('organization','intitle:Invalidiliitto filetype:bitmap'),('visualbell','intitle:deaf doorbell filetype:bitmap'),('craft','intitle:knitting needles yarn filetype:bitmap'),('basket','intitle:shopping basket filetype:bitmap')]
for slug,q in queries:
 out=P/f'disability-{slug}-research.json'
 if out.exists():continue
 subprocess.run([str(R/'.venv/bin/python'),'studio/production/remaining/commons.py','--search',q,'--limit','8','--output',str(out)],cwd=R,check=True);print(slug,flush=True)
