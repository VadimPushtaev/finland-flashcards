"""Find concrete photograph sources for access,appointments and patient rights."""
from pathlib import Path
import subprocess
R=Path(__file__).resolve().parents[3];P=Path(__file__).resolve().parent
for name,query in [('agency','Digi väestötietovirasto filetype:bitmap'),('clock','intitle:"wall clock" filetype:bitmap'),('room','intitle:"examination room" filetype:bitmap'),('bed','intitle:"hospital bed" filetype:bitmap')]:
    out=P/f'access-{name}-research.json'
    if out.exists():continue
    print('Research',name,query,flush=True);subprocess.run([str(R/'.venv/bin/python'),str(R/'studio/production/remaining/commons.py'),'--search',query,'--output',str(out),'--limit','8'],check=True)
