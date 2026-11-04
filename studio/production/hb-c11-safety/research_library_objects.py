"""Research actual library objects and accurately identified Finnish library uses."""
from pathlib import Path
import subprocess
R=Path(__file__).resolve().parents[3];P=Path(__file__).resolve().parent
for slug,query in [('bookbus','intitle:kirjastoauto'),('reading','Finland library reading room'),('children','Finland library children books'),('computer','Finland library computers'),('university','Kaisa House library interior'),('easy','intitle:selkokirja'),('media','CD DVD books library')]:
    out=P/('library-'+slug+'-research.json')
    if out.exists():continue
    subprocess.run([str(R/'.venv/bin/python'),str(R/'studio/production/remaining/commons.py'),'--search',query,'--limit','8','--output',str(out)],cwd=R,check=True);print(slug,flush=True)
