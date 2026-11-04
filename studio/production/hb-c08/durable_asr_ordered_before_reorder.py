"""Wait for finalized narration then resume hash-bound diagnostics with one CPU thread."""
from pathlib import Path
import datetime,hashlib,json,os,subprocess,time,yaml
ROOT=Path(__file__).resolve().parents[3];PROD=ROOT/'studio/production/hb-c08';STATE=PROD/'durable-asr-state.json'
def stamp():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def save():
 p=STATE.with_suffix('.tmp');p.write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n');p.replace(STATE)
state=dict(supervisor_pid=os.getpid(),status='running',jobs={});save()
# The earlier incremental producer is the exclusive writer until it exits.
while Path('/proc/45133').exists():
 print(stamp(),'Waiting for previous incremental ASR PID45133',flush=True);time.sleep(35)
for sid in ['hb-c08-utveckling','hb-c08-smabarn','hb-c08-gymnasium','hb-c08-hogskolor','hb-c08-grundskola','hb-c08-yrkesutbildning','hb-c08-finansiering','hb-c08-vuxna','hb-c08-stod']:
 ep=ROOT/'studio/episodes'/sid;folder=ROOT/'studio/media'/sid/'narration';total=len(yaml.safe_load((ep/'script.yaml').read_text())['sentences']);state['jobs'][sid]=dict(status='waiting_for_final_narration',total=total);save()
 while not (folder/'metrics.json').exists() or len(json.loads((folder/'metrics.json').read_text()))<total:
  print(stamp(),sid,'waiting for finalized narration',flush=True);time.sleep(35)
 log=PROD/(sid+'-asr-final.log')
 with log.open('a') as h:
  p=subprocess.Popen([str(ROOT/'studio/runtime/.venv/bin/python'),'studio/tools/check_audio.py',str(folder),'--language','sv','--pattern','hb-*.wav','--resume','--threads','1'],cwd=ROOT,stdout=h,stderr=subprocess.STDOUT);state['jobs'][sid].update(status='running',pid=p.pid,log=str(log.relative_to(ROOT)));save()
  while True:
   try:code=p.wait(timeout=35);break
   except subprocess.TimeoutExpired:print(stamp(),sid,'ASR running PID',p.pid,flush=True)
 state['jobs'][sid].update(status='complete' if code==0 else 'failed',exit_code=code);save()
 if code:state['status']='failed';save();raise SystemExit(code)
 subprocess.run([str(ROOT/'studio/runtime/.venv/bin/python'),'studio/production/hb-c08/diagnostics.py',sid],cwd=ROOT,check=True)
state['status']='complete';save()
