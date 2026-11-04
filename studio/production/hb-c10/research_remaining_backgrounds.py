"""Read Commons primary metadata for distinct relevant remaining backgrounds."""
from pathlib import Path
import subprocess
R=Path(__file__).resolve().parents[3];P=Path(__file__).resolve().parent
for slug,query in [('traffic','intitle:liikenne Helsinki'),('fire','intitle:paloasema'),('emergency','intitle:Hätäkeskus'),('disability','intitle:Validia'),('mental','intitle:Kellokosken sairaala'),('sexual','intitle:terveysasema'),('sickness','intitle:Porvoon sairaala'),('pension','intitle:Keva'),('elderly','intitle:palvelutalo'),('leisure','intitle:Nuorisotalo')]:
 out=P/(slug+'-remaining-background-research.json')
 if out.exists():continue
 subprocess.run([str(R/'.venv/bin/python'),str(R/'studio/production/remaining/commons.py'),'--search',query,'--limit','8','--output',str(out)],cwd=R,check=True)
 print(slug,'retained primary metadata',flush=True)
