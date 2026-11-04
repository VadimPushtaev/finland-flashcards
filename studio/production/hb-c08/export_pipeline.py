"""Export one prepared episode through technical verification, with durable stage records."""
from pathlib import Path
import datetime,json,os,subprocess,sys
ROOT=Path(__file__).resolve().parents[3];PROD=ROOT/'studio/production/hb-c08';SID=sys.argv[1];STATE=PROD/(SID+'-export-state.json');MEDIA=ROOT/'studio/runtime/.venv/bin/python';SOURCE=ROOT/'.venv/bin/python'
def stamp():return datetime.datetime.now(datetime.timezone.utc).isoformat()
state=dict(section_id=SID,supervisor_pid=os.getpid(),started_at=stamp(),status='running',stages={})
def save():
 p=STATE.with_suffix('.tmp');p.write_text(json.dumps(state,indent=2)+'\n');p.replace(STATE)
def run(stage,cmd):
 log=PROD/(SID+'-'+stage+'.log')
 with log.open('a') as h:
  p=subprocess.Popen([str(x) for x in cmd],cwd=ROOT,stdout=h,stderr=subprocess.STDOUT);state['stages'][stage]=dict(status='running',pid=p.pid,log=str(log.relative_to(ROOT)),started_at=stamp());save()
  while True:
   try:code=p.wait(timeout=35);break
   except subprocess.TimeoutExpired:print(stamp(),SID,stage,'running PID',p.pid,flush=True)
 state['stages'][stage].update(status='complete' if code==0 else 'failed',exit_code=code,completed_at=stamp());save()
 if code:state['status']='failed';save();raise SystemExit(code)
save()
run('assets-validate',[MEDIA,'studio/tools/validate_assets.py',SID])
run('render',[MEDIA,'studio/tools/render.py',SID])
run('verify',[MEDIA,'studio/tools/verify_render.py',SID,'--save-frames'])
run('script-review',[SOURCE,'studio/tools/script.py','review',SID,'--ready'])
run('script-validate',[SOURCE,'studio/tools/script.py','validate',SID,'--ready'])
run('coverage',[SOURCE,'studio/tools/picture_coverage.py',SID,'--require-target'])
run('diversity',[SOURCE,'studio/production/remaining/picture_diversity.py',SID])
run('diagnostics',[MEDIA,'studio/production/hb-c08/diagnostics.py',SID])
run('finalize',[MEDIA,'studio/production/hb-c08/finalize.py',SID])
state['status']='preview_ready_pending_visual_and_whole_video_review';state['completed_at']=stamp();save();print(stamp(),SID,'TECHNICAL EXPORT COMPLETE; actual export visual review and user listening pending',flush=True)
