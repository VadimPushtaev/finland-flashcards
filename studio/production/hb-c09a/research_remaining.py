"""Research verified Finnish family-topic places through the shared throttle."""
from pathlib import Path
import subprocess,sys
p=Path('studio/production/hb-c09a/research')
for term in ['perhekeskus','neuvola','päiväkoti','hautausmaa','käräjäoikeus','poliisiasema','leikkipuisto','kirjasto','puutalo']:
    output=p/('institutions-'+term+'.json')
    if output.exists():continue
    command=['.venv/bin/python','studio/production/remaining/commons.py','--search','filetype:bitmap intitle:'+term,'--limit','12','--output',str(output)]
    proc=subprocess.Popen(command,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
    while True:
        try:log,_=proc.communicate(timeout=35);break
        except subprocess.TimeoutExpired:print('Research request pending:',term,flush=True)
    print(term,proc.returncode,log,flush=True)
    if 'cooldown' in log.lower():raise SystemExit('Respecting shared API cooldown; resume later from saved metadata.')
