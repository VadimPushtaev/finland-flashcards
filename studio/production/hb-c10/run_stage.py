"""Run an owned production stage and retain its exact process/log/status record."""
from pathlib import Path
import json,subprocess,sys,datetime,time
ROOT=Path(__file__).resolve().parents[3];PROD=Path(__file__).resolve().parent
sid,stage,*cmd=sys.argv[1:];path=PROD/f'{sid}-{stage}.json';log=PROD/'logs'/f'{sid}-{stage}.log';log.parent.mkdir(exist_ok=True)
if path.exists():
    previous=json.loads(path.read_text())
    if previous.get('status')=='complete':print('Already complete',sid,stage);raise SystemExit(0)
with log.open('w') as out:
    p=subprocess.Popen(cmd,cwd=ROOT,stdout=out,stderr=subprocess.STDOUT)
    rec=dict(section_id=sid,stage=stage,pid=p.pid,command=cmd,log=str(log.relative_to(ROOT)),status='running',started_at=datetime.datetime.now(datetime.timezone.utc).isoformat());path.write_text(json.dumps(rec,indent=2)+'\n');print(json.dumps(rec),flush=True)
    while p.poll() is None:
        time.sleep(30)
        lines=log.read_text(errors='replace').splitlines()
        print(json.dumps(dict(section_id=sid,stage=stage,pid=p.pid,status='running',last_log_line=lines[-1] if lines else 'initializing')),flush=True)
    rc=p.wait();rec.update(status='complete' if rc==0 else 'failed',returncode=rc,finished_at=datetime.datetime.now(datetime.timezone.utc).isoformat());path.write_text(json.dumps(rec,indent=2)+'\n');print(json.dumps(rec),flush=True)
raise SystemExit(rc)
