"""Prepare finalized owned narration for coordinated rendering; never launches encoders."""
from pathlib import Path
import datetime,json,os,subprocess,time,yaml
ROOT=Path(__file__).resolve().parents[3];PROD=ROOT/'studio/production/hb-c08';STATE=PROD/'durable-prepare-state.json';MEDIA=ROOT/'studio/runtime/.venv/bin/python';SOURCE=ROOT/'.venv/bin/python'
SECTIONS=['hb-c12-sprak','hb-c08-grundskola','hb-c12-hemkommun','hb-c08-yrkesutbildning','hb-c12-e-tjanster','hb-c08-finansiering','hb-c12-tolkning','hb-c08-vuxna','hb-c12-norden-eu','hb-c12-integration','hb-c12-egna-arenden','hb-c12-myndigheter','hb-c12-personuppgifter','hb-c12-tjanster']
def stamp():return datetime.datetime.now(datetime.timezone.utc).isoformat()
state=dict(supervisor_pid=os.getpid(),started_at=stamp(),status='running',jobs={})
def save():
 p=STATE.with_suffix('.tmp');p.write_text(json.dumps(state,indent=2)+'\n');p.replace(STATE)
def run(sid,name,cmd):
 log=PROD/(sid+'-prepare-'+name+'.log')
 with log.open('ab') as h:
  p=subprocess.Popen([str(x) for x in cmd],cwd=ROOT,stdout=h,stderr=subprocess.STDOUT);state['jobs'][sid].update(stage=name,active_pid=p.pid,log=str(log.relative_to(ROOT)));save()
  while True:
   try:code=p.wait(timeout=35);break
   except subprocess.TimeoutExpired:print(stamp(),sid,name,'running PID',p.pid,flush=True)
 state['jobs'][sid].update(active_pid=None,last_exit_code=code);save()
 if code:raise RuntimeError(sid+' '+name+' failed; inspect '+str(log))
save()
while True:
 pending=[sid for sid in SECTIONS if state['jobs'].get(sid,{}).get('status')!='prepared_pending_visual_and_ASR_review']
 if not pending:break
 ready=[]
 for sid in pending:
  ep=ROOT/'studio/episodes'/sid;script=yaml.safe_load((ep/'script.yaml').read_text());mp=ROOT/'studio/media'/sid/'narration/metrics.json';state['jobs'].setdefault(sid,dict(status='waiting_for_final_narration'))
  if not mp.exists() or len(json.loads(mp.read_text()))!=len(script['sentences']):continue
  if any(seg.get('speech_offset_seconds') is None for r in script['sentences'] for seg in r.get('display_segments') or []):state['jobs'][sid]['status']='waiting_for_measured_display_alignment';continue
  ready.append(sid)
 save()
 if not ready:print(stamp(),'Preparation waiting;',len(pending),'episodes pending',flush=True);time.sleep(35);continue
 sid=ready[0];state['jobs'][sid]['status']='preparing';save();helper='studio/production/hb-c12a/assets.py' if sid.startswith('hb-c12-') else 'studio/production/hb-c08/assets.py'
 try:
  run(sid,'assets',[MEDIA,helper,sid]);run(sid,'asset-integrity',[MEDIA,'studio/tools/validate_assets.py',sid]);run(sid,'stills',[MEDIA,'studio/tools/render.py',sid,'--stills-only']);run(sid,'script-review',[SOURCE,'studio/tools/script.py','review',sid,'--ready']);run(sid,'script-validation',[SOURCE,'studio/tools/script.py','validate',sid,'--ready']);run(sid,'picture-diversity',[SOURCE,'studio/production/remaining/picture_diversity.py',sid]);state['jobs'][sid].update(status='prepared_pending_visual_and_ASR_review',completed_at=stamp());save();print(stamp(),sid,'PREPARED; no encoder started; actual visual/ASR reviews remain',flush=True)
 except Exception as exc:state['jobs'][sid].update(status='failed',error=str(exc));state['status']='failed';save();raise
state['status']='complete';state['completed_at']=stamp();save()
