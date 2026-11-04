"""Research actual traffic and safety objects through shared rate-limited metadata requests."""
from pathlib import Path
import subprocess
R=Path(__file__).resolve().parents[3];P=Path(__file__).resolve().parent
queries=[('traffic-walk','intitle:Helsinki pedestrian filetype:bitmap'),('traffic-road','intitle:Finland road traffic filetype:bitmap'),('traffic-crossing','intitle:Finland pedestrian crossing filetype:bitmap'),('traffic-cycle','intitle:bicycle helmet filetype:bitmap'),('traffic-light','intitle:bicycle light filetype:bitmap'),('traffic-reflector','intitle:pedestrian reflector filetype:bitmap'),('traffic-ticket','intitle:HSL ticket machine filetype:bitmap'),('traffic-seatbelt','intitle:seat belt filetype:bitmap'),('fire-blanket','intitle:fire blanket filetype:bitmap'),('fire-extinguisher','intitle:fire extinguisher Finland filetype:bitmap'),('fire-battery','intitle:9V battery filetype:bitmap'),('fire-stove','intitle:electric stove filetype:bitmap'),('fire-sauna','intitle:sauna heater filetype:bitmap'),('fire-lock','intitle:door security lock filetype:bitmap'),('emergency-police','intitle:Finnish police van filetype:bitmap'),('emergency-house-number','intitle:Helsinki house number filetype:bitmap')]
for slug,q in queries:
 out=P/(slug+'-research.json')
 if out.exists():continue
 subprocess.run([str(R/'.venv/bin/python'),'studio/production/remaining/commons.py','--search',q,'--limit','8','--output',str(out)],cwd=R,check=True);print(slug,flush=True)
