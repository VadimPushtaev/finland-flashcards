"""Resolve actual household safety objects and reject irrelevant broad matches."""
from pathlib import Path
import subprocess
R=Path(__file__).resolve().parents[3];P=Path(__file__).resolve().parent
queries=[('alarm','intitle:"smoke detector" ceiling filetype:bitmap'),('hardware','intitle:K-Rauta filetype:bitmap'),('electric-sauna','"electric sauna" heater filetype:bitmap'),('iron','intitle:clothes iron filetype:bitmap'),('radiator','intitle:electric radiator filetype:bitmap'),('candle','intitle:unlit candle filetype:bitmap'),('valve','intitle:water shutoff valve filetype:bitmap'),('deadbolt','intitle:Abloy security lock filetype:bitmap'),('cleaning','intitle:cleaning cloth floor filetype:bitmap'),('vent','intitle:ventilation valve apartment filetype:bitmap'),('balcony','intitle:balcony door apartment filetype:bitmap'),('stair-extinguisher','intitle:extinguisher stairwell filetype:bitmap')]
for slug,q in queries:
 out=P/f'fire-{slug}-research.json'
 if out.exists():continue
 subprocess.run([str(R/'.venv/bin/python'),'studio/production/remaining/commons.py','--search',q,'--limit','8','--output',str(out)],cwd=R,check=True);print(slug,flush=True)
