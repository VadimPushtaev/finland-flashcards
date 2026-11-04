"""Research neutral reproductive-health equipment and empty care/education places."""
from pathlib import Path
import subprocess
R=Path(__file__).resolve().parents[3];P=Path(__file__).resolve().parent
for slug,q in [('family','intitle:perhekeskus filetype:bitmap'),('maternity','intitle:Naistenklinikka filetype:bitmap'),('classroom','intitle:luokkahuone filetype:bitmap'),('condom','intitle:"condom package" filetype:bitmap'),('pill','intitle:"contraceptive pill" -intitle:woman filetype:bitmap'),('barrier','intitle:"dental dam" -intitle:teeth -intitle:patient -intitle:mouth filetype:bitmap'),('consultation','intitle:neuvola filetype:bitmap')]:
 out=P/('sexual-'+slug+'-research.json')
 if out.exists():continue
 subprocess.run([str(R/'.venv/bin/python'),str(R/'studio/production/remaining/commons.py'),'--search',q,'--limit','8','--output',str(out)],cwd=R,check=True);print(slug,flush=True)
