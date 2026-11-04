"""Start the explicitly assigned Språk export only after Stöd succeeds and one host encoder remains."""
from pathlib import Path
import datetime,hashlib,json,os,subprocess,time
ROOT=Path(__file__).resolve().parents[3];PROD=ROOT/'studio/production/hb-c08';SID='hb-c12-sprak';state={'supervisor_pid':os.getpid(),'started_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'waiting_stod_render'};STATE=PROD/'sprak-succession-state.json'
def stamp():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def save():STATE.write_text(json.dumps(state,indent=2)+'\n')
while True:
 s=json.loads((PROD/'hb-c08-stod-export-state.json').read_text());render=s.get('stages',{}).get('render',{})
 if render.get('status')=='failed':state.update(status='blocked_stod_failed');save();raise SystemExit(1)
 if render.get('status')=='complete' and render.get('exit_code')==0:
  host=subprocess.run(['ps','-eo','args'],capture_output=True,text=True,check=True).stdout.splitlines();encoders=[line for line in host if '-c:v libx264' in line and '/studio/media/' in line]
  if len(encoders)==1:
   freeze=json.loads((PROD/'sprak-export-freeze.json').read_text());ep=ROOT/'studio/episodes'/SID
   for file,key in [('script.yaml','script_sha256'),('assets.yaml','assets_sha256')]:assert hashlib.sha256((ep/file).read_bytes()).hexdigest()==freeze[key],'Reviewed inputs changed: '+file
   state.update(status='launching',host_encoders_before_launch=encoders,stod_render_completed_at=render['completed_at']);save()
   with (PROD/(SID+'-durable-export.log')).open('ab',buffering=0) as h:p=subprocess.Popen([str(ROOT/'studio/runtime/.venv/bin/python'),str(PROD/'export_pipeline.py'),SID],cwd=ROOT,stdout=h,stderr=subprocess.STDOUT,start_new_session=True)
   job={'section_id':SID,'supervisor_pid':p.pid,'started_at':stamp(),'log':'studio/production/hb-c08/'+SID+'-durable-export.log','authorization':'Root explicitly assigned released Stöd slot to Språk; release onward to C10 Tillgång after Språk.'};(PROD/(SID+'-supervisor.json')).write_text(json.dumps(job,indent=2)+'\n');state.update(status='launched',export_supervisor_pid=p.pid,launched_at=job['started_at']);save();print(stamp(),'SPRAK LAUNCHED',p.pid,'one prior host encoder',encoders,flush=True)
   path=PROD/'batch-handoff.json';batch=json.loads(path.read_text());batch['running_export']={'section_id':SID,'supervisor_pid':p.pid,'state':SID+'-export-state.json'};batch['ready_for_encoder']=[r for r in batch['ready_for_encoder'] if r['section_id']!=SID];batch['updated_at']=stamp();path.write_text(json.dumps(batch,indent=2)+'\n');break
  state['host_encoder_count']=len(encoders)
 save();print(stamp(),'Waiting for assigned Stöd→Språk succession',flush=True);time.sleep(35)
