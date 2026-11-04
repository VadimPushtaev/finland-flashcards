"""Record exact command/PID/log and outcome for one owned local stage."""
from pathlib import Path
import subprocess,sys,json,time,os
P=Path(__file__).resolve().parent;sid,stage,*cmd=sys.argv[1:];state=P/(sid+'-'+stage+'-state.json');log=P/(sid+'-'+stage+'.log')
with log.open('a') as stream:
    proc=subprocess.Popen(cmd,stdout=stream,stderr=subprocess.STDOUT)
    d=dict(section_id=sid,stage=stage,pid=proc.pid,controller_pid=os.getpid(),command=cmd,started=time.time(),log=str(log.relative_to(Path.cwd())),status='running');state.write_text(json.dumps(d,indent=2))
    print(sid,stage,proc.pid,flush=True)
    while proc.poll() is None:
        try:proc.wait(timeout=35)
        except subprocess.TimeoutExpired:
            d['heartbeat']=time.time();state.write_text(json.dumps(d,indent=2));print(sid,stage,'running',round(time.time()-d['started']),'seconds',flush=True)
    rc=proc.returncode;d.update(status='done' if rc==0 else 'failed',returncode=rc,ended=time.time());state.write_text(json.dumps(d,indent=2))
raise SystemExit(rc)
