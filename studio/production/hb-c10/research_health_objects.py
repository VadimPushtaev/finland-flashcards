"""Find actual licensed assistive/financial objects; metadata is reviewed before use."""
from pathlib import Path
import subprocess
R=Path(__file__).resolve().parents[3];P=Path(__file__).resolve().parent
for slug,q in [('wheelchair','intitle:wheelchair -intitle:icon -intitle:logo filetype:bitmap'),('hearingaid','intitle:"hearing aid" filetype:bitmap'),('whitecane','intitle:"white cane" filetype:bitmap'),('guidedog','intitle:"guide dog" filetype:bitmap'),('rollator','intitle:rollator filetype:bitmap'),('alarm','intitle:"medical alarm" filetype:bitmap'),('kela','intitle:Kelan toimisto filetype:bitmap'),('money','intitle:"Euro coins" filetype:bitmap'),('envelope','intitle:envelopes -intitle:stamp filetype:bitmap'),('stethoscope','intitle:stethoscope -intitle:icon filetype:bitmap')]:
 out=P/('health-object-'+slug+'-research.json')
 if out.exists():continue
 subprocess.run([str(R/'.venv/bin/python'),str(R/'studio/production/remaining/commons.py'),'--search',q,'--limit','8','--output',str(out)],cwd=R,check=True);print(slug,flush=True)
