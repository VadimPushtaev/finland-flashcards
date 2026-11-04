"""Research actual licensed pharmacy,dental and medicine-object photographs."""
from pathlib import Path
import subprocess
R=Path(__file__).resolve().parents[3];P=Path(__file__).resolve().parent
queries=[('pharmacy','Finland pharmacy exterior filetype:bitmap'),('dentalclinic','Finland dental clinic filetype:bitmap'),('instrument','intitle:"dental mirror" filetype:bitmap'),('waiting','intitle:"waiting room" dentist filetype:bitmap'),('expiry','medicine expiration date filetype:bitmap'),('customs','Finland Tulli customs filetype:bitmap'),('parcel','intitle:"cardboard box" filetype:bitmap')]
for name,query in queries:
    out=P/f'medicines-{name}-research.json'
    if out.exists():continue
    print('Research',name,query,flush=True);subprocess.run([str(R/'.venv/bin/python'),str(R/'studio/production/remaining/commons.py'),'--search',query,'--output',str(out),'--limit','8'],check=True)
out=P/'medicines-background-metadata.json'
if not out.exists():subprocess.run([str(R/'.venv/bin/python'),str(R/'studio/production/remaining/commons.py'),'--titles','File:Punkaharjun apteekki.JPG','--output',str(out)],check=True)
