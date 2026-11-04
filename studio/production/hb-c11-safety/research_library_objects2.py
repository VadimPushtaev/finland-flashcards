from pathlib import Path
import subprocess
R=Path(__file__).resolve().parents[3];P=Path(__file__).resolve().parent
for slug,query in [('palokka','intitle:Palokka Library filetype:bitmap'),('dvd','intitle:DVD discs filetype:bitmap'),('games','board games library filetype:bitmap'),('kaisa','intitle:Kaisa library filetype:bitmap')]:
 out=P/('library-'+slug+'-research.json')
 if out.exists():continue
 subprocess.run([str(R/'.venv/bin/python'),str(R/'studio/production/remaining/commons.py'),'--search',query,'--limit','8','--output',str(out)],check=True,cwd=R);print(slug,flush=True)
