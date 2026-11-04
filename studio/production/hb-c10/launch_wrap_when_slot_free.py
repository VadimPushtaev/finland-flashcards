"""Launch only the assigned wrap repair after root recycling exits and one encoder remains."""
from pathlib import Path
import json
import shlex
import subprocess
import time
import datetime
R=Path(__file__).resolve().parents[3];P=Path(__file__).resolve().parent;STATE=R/'studio/production/remaining/hb-c11-atervinning-render-state.json';OUT=P/'folkhalsa-wrap-fix/launch-status.json';JOB=P/'hb-c10-folkhalsa-wrap-render-job.json'
def renderers():
    raw=subprocess.check_output(['ps','-eo','pid=,comm=,args='],text=True)
    active=[]
    for line in raw.splitlines():
        fields=line.strip().split(None,2)
        if len(fields)<3 or not fields[1].startswith('python'):continue
        try:args=shlex.split(fields[2])
        except ValueError:continue
        if any(a.endswith('studio/tools/render.py') for a in args) and '--stills-only' not in args:
            active.append(dict(pid=int(fields[0]),args=args))
    return active
for tick in range(100000):
    state=json.loads(STATE.read_text()) if STATE.exists() else {}
    active=renderers();root_present=any('hb-c11-atervinning' in p['args'] for p in active)
    ready=state.get('status')=='finished' and state.get('returncode')==0 and not root_present and len(active)==1
    record=dict(updated_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),status='assigned_slot_available' if ready else 'waiting',dependency=str(STATE.relative_to(R)),dependency_supervisor=state.get('supervisor_pid'),dependency_status=state.get('status'),full_renderers=active,assigned_job=str(JOB.relative_to(R)),additional_allocation=False)
    OUT.write_text(json.dumps(record,indent=2)+'\n')
    if tick%6==0:print(json.dumps(record),flush=True)
    if ready:
        result=subprocess.run([str(R/'.venv/bin/python'),'studio/production/remaining/job.py','start',str(JOB.relative_to(R))],cwd=R,check=True,capture_output=True,text=True);print(result.stdout,flush=True);record.update(status='launched_exact_assigned_job',launcher_result=result.stdout.strip());OUT.write_text(json.dumps(record,indent=2)+'\n');break
    if state.get('status')=='finished' and state.get('returncode') not in [None,0]:raise RuntimeError('Root render failed; coordinator must reassign before launching repair.')
    time.sleep(5)
else:raise RuntimeError('Unexpected slot monitor time limit')
