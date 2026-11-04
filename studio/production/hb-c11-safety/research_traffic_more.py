"""Resolve narrower Finnish transport and inspection source identities."""
from pathlib import Path
import subprocess
R=Path(__file__).resolve().parents[3];P=Path(__file__).resolve().parent
for slug,q in [('street','intitle:Mannerheimintie 2024 filetype:bitmap'),('rural','intitle:Seututie road filetype:bitmap'),('bicycle','intitle:bicycle Helsinki filetype:bitmap'),('winter','winter cycling Finland filetype:bitmap'),('cyclepath','intitle:cycle path Helsinki filetype:bitmap'),('localtrain','intitle:Sm5 Helsinki filetype:bitmap'),('tram','intitle:Artic tram Helsinki filetype:bitmap'),('metro','intitle:Helsinki Metro M100 filetype:bitmap'),('ferry','intitle:Suomenlinna ferry filetype:bitmap'),('inspection','intitle:katsastus filetype:bitmap'),('fuel','intitle:Finland fuel pump filetype:bitmap'),('ruralbus','intitle:bus stop Lapland filetype:bitmap')]:
 out=P/f'traffic-{slug}-research.json'
 if out.exists():continue
 subprocess.run([str(R/'.venv/bin/python'),'studio/production/remaining/commons.py','--search',q,'--limit','8','--output',str(out)],cwd=R,check=True);print(slug,flush=True)
