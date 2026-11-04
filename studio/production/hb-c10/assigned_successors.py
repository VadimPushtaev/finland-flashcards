"""Launch only root-assigned frozen successors,with exact predecessor and central encoder guards."""
from pathlib import Path
import json,hashlib,time,subprocess,sys,datetime
R=Path(__file__).resolve().parents[3];P=Path(__file__).resolve().parent
configuration=json.loads((R/sys.argv[1]).read_text());status=R/configuration['status']
def load(p):return json.loads(p.read_text())if p.exists()else{}
def log(stage,**kw):
 r=dict(updated_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),stage=stage,**kw);status.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r),flush=True)
def count():
 found=[]
 for path in Path('/proc').glob('[0-9]*/cmdline'):
  try:args=[x.decode()for x in path.read_bytes().split(b'\0')if x]
  except(OSError,UnicodeError):continue
  if len(args)>2 and args[1].endswith('studio/tools/render.py')and'--stills-only'not in args:found.append(int(path.parent.name))
 return found
for entry in configuration['entries']:
 predecessor=R/entry['predecessor'];job=R/entry['render_job'];j=load(job);state=R/j['state']
 if load(state).get('status')=='finished'and load(state).get('returncode')==0:log('already_complete',section_id=entry['section_id']);continue
 while True:
  previous=load(predecessor)
  if previous.get('status')=='failed'or previous.get('returncode')not in[None,0]:raise RuntimeError('Predecessor failed;preserve output:'+str(predecessor))
  if previous.get('status')=='finished'and previous.get('returncode')==0 and not previous.get('missing_outputs'):break
  log('waiting_predecessor',section_id=entry['section_id'],predecessor=str(predecessor.relative_to(R)));time.sleep(25)
 for path,digest in entry['frozen_inputs'].items():assert hashlib.sha256((R/path).read_bytes()).hexdigest()==digest,('Frozen input changed',path)
 while True:
  live=count();budget=load(R/'studio/production/remaining/resource-budget.json')['max_full_encoders']
  if len(live)<budget:break
  log('waiting_encoder_budget',section_id=entry['section_id'],live=live,budget=budget);time.sleep(20)
 if load(state).get('status')in['running','starting']:raise RuntimeError('Existing owned renderer;do notduplicate:'+str(state))
 log('launching_assigned_successor',section_id=entry['section_id'],live=count(),budget=budget)
 subprocess.run([str(R/'.venv/bin/python'),'studio/production/remaining/job.py','start',str(job.relative_to(R))],cwd=R,check=True)
 while True:
  active=load(state)
  if active.get('status')=='finished':
   assert active.get('returncode')==0 and not active.get('missing_outputs'),active
   log('render_finished_slot_released',section_id=entry['section_id'],state=active)
   subprocess.run([str(R/'.venv/bin/python'),'studio/production/remaining/job.py','start',entry['verify_job']],cwd=R,check=True);break
  if active.get('status')=='failed':raise RuntimeError('Assigned render failed:'+str(state))
  log('assigned_render_active',section_id=entry['section_id'],supervisor_pid=active.get('supervisor_pid'),child_pid=active.get('pid'));time.sleep(25)
log('assigned_sequence_complete')
