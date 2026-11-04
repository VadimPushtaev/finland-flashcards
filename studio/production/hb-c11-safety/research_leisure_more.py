from pathlib import Path
import subprocess
R=Path(__file__).resolve().parents[3];P=Path(__file__).resolve().parent
for slug,q in [('hall','intitle:community hall interior filetype:bitmap'),('litter','intitle:litter picking filetype:bitmap'),('parish','intitle:seurakuntatalo filetype:bitmap'),('computer','intitle:laptop computer filetype:bitmap')]:
 out=P/('leisure-'+slug+'-research.json')
 if out.exists():continue
 subprocess.run([str(R/'.venv/bin/python'),str(R/'studio/production/remaining/commons.py'),'--search',q,'--limit','8','--output',str(out)],cwd=R,check=True);print(slug,flush=True)
