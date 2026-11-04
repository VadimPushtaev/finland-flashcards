"""Use the assigned Tillgång→Språk repair slot only after successful completion."""
from pathlib import Path
import datetime,hashlib,json,os,subprocess,time
ROOT=Path(__file__).resolve().parents[3];PROD=ROOT/'studio/production/hb-c08';SID='hb-c12-sprak';STATE=PROD/'sprak-repair-succession-state.json';state=dict(supervisor_pid=os.getpid(),started_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),status='waiting_Tillgang_render')
def stamp():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def save():
 q=STATE.with_suffix('.tmp');q.write_text(json.dumps(state,indent=2)+'\n');q.replace(STATE)
while True:
 prior=json.loads((ROOT/'studio/production/hb-c10/hb-c10-tillgang-render-state.json').read_text());assert prior['supervisor_pid']==206003
 if prior.get('status')=='finished':
  assert prior.get('returncode')==0 and not prior.get('missing_outputs'),'Assigned predecessor failed; do not consume slot silently.'
  encoders=[line for line in subprocess.run(['ps','-eo','args'],capture_output=True,text=True,check=True).stdout.splitlines() if '-c:v libx264' in line and '/studio/media/' in line]
  if len(encoders)<=1:
   ep=ROOT/'studio/episodes'/SID;freeze=json.loads((PROD/'sprak-repair-freeze.json').read_text())
   for filename,key in [('script.yaml','script_sha256'),('assets.yaml','assets_sha256')]:assert hashlib.sha256((ep/filename).read_bytes()).hexdigest()==freeze[key],filename+'changed since reviewed freeze'
   assert not (ep/'render.json').exists(),'Repair export alreadyexists; avoid duplicate.'
   state.update(status='launching',prior_finished_at=prior['finished_at'],host_encoders_before_launch=encoders);save()
   with (PROD/(SID+'-durable-export.log')).open('ab',buffering=0) as h:p=subprocess.Popen([str(ROOT/'studio/runtime/.venv/bin/python'),str(PROD/'export_pipeline.py'),SID],cwd=ROOT,stdout=h,stderr=subprocess.STDOUT,start_new_session=True)
   state.update(status='launched',export_supervisor_pid=p.pid,launched_at=stamp());save();print(stamp(),'SPRAK REPAIR LAUNCHED',p.pid,'priorfullencoders',len(encoders),flush=True)
   path=PROD/'batch-handoff.json';b=json.loads(path.read_text());b['running_export']=dict(section_id=SID,supervisor_pid=p.pid,state=SID+'-export-state.json',reason='One-picture repair');b['updated_at']=stamp();path.write_text(json.dumps(b,ensure_ascii=False,indent=2)+'\n');break
  state['host_encoder_count']=len(encoders)
 save();print(stamp(),'Waiting assigned Tillgang→Sprakrepair slot',flush=True);time.sleep(35)
