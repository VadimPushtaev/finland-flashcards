"""Measure the last long bilingual pair once its selected narration is immutable."""
from pathlib import Path
import datetime,json,os,signal,subprocess,time
ROOT=Path(__file__).resolve().parents[3];PROD=ROOT/'studio/production/hb-c08';SID='hb-c12-tjanster';STATE=PROD/'tjanster-alignment-state.json';paused=False
state=dict(supervisor_pid=os.getpid(),started_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),status='waiting_final_selected_narration')
def stamp():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def save():
 p=STATE.with_suffix('.tmp');p.write_text(json.dumps(state,indent=2)+'\n');p.replace(STATE)
def children(parent):
 r=subprocess.run(['ps','-eo','pid,ppid,state,args'],text=True,capture_output=True,check=True);return [x for x in r.stdout.splitlines() if len(x.split())>2 and x.split()[1]==str(parent) and x.split()[2]!='Z']
try:
 while json.loads((PROD/'durable-tts-state.json').read_text())['jobs'].get(SID,{}).get('status')!='complete':
  save();print(stamp(),'Waiting for selected Tjanster metrics; no compute occupied',flush=True);time.sleep(35)
 try:
  os.kill(94559,signal.SIGSTOP);paused=True
 except ProcessLookupError:
  assert json.loads((PROD/'durable-asr-state.json').read_text())['status']=='complete', 'ASR supervisor vanished before completion'
  state['ASR_already_complete']=True
 state['status']='waiting_current_immutable_ASR';save();begin=time.monotonic()
 while children(94559):
  if time.monotonic()-begin>600:raise TimeoutError('ExistingASRchildunfinished; no alignmentstarted')
  print(stamp(),'Waiting currentASR child',children(94559),flush=True);time.sleep(10)
 with (PROD/'tjanster-display-alignment.log').open('ab',buffering=0) as h:
  p=subprocess.Popen([str(ROOT/'studio/runtime/.venv/bin/python'),'studio/production/remaining/align_display_segments.py',SID,'--threads','1','--apply'],cwd=ROOT,stdout=h,stderr=subprocess.STDOUT);state.update(status='measuring_final_WAV_boundary',active_pid=p.pid);save()
  while True:
   try:code=p.wait(timeout=35);break
   except subprocess.TimeoutExpired:print(stamp(),'Measured-boundary alignmentrunning',p.pid,flush=True)
 state.update(status='applied_pending_visual_review' if code==0 else 'manual_review_required',exit_code=code,finished_at=stamp());save()
finally:
 if paused:
  try:os.kill(94559,signal.SIGCONT);state['ASR_resumed']=True
  except ProcessLookupError:state['ASR_completed_before_resume']=True
  save()
