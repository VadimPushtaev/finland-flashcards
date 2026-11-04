"""Research concrete leisure objects,venues and ordinary accurately identified activities."""
from pathlib import Path
import subprocess
R=Path(__file__).resolve().parents[3];P=Path(__file__).resolve().parent
for slug,q in [('jogging','intitle:Jogging filetype:bitmap'),('institute','intitle:kansalaisopisto filetype:bitmap'),('art','intitle:painting brushes filetype:bitmap'),('pool','intitle:uimahalli filetype:bitmap'),('gym','intitle:gym equipment filetype:bitmap'),('field','intitle:urheilukenttä filetype:bitmap'),('sauna','intitle:sauna interior filetype:bitmap'),('community','intitle:asukastalo filetype:bitmap'),('park','intitle:puisto Helsinki filetype:bitmap'),('beach','intitle:uimaranta filetype:bitmap'),('youth','intitle:nuorisotila filetype:bitmap'),('music','intitle:musical instruments filetype:bitmap'),('theatre','intitle:teatteri filetype:bitmap'),('dance','intitle:dance class filetype:bitmap')]:
    out=P/('leisure-'+slug+'-research.json')
    if out.exists():continue
    subprocess.run([str(R/'.venv/bin/python'),str(R/'studio/production/remaining/commons.py'),'--search',q,'--limit','8','--output',str(out)],cwd=R,check=True);print(slug,flush=True)
