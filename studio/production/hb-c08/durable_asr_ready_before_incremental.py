"""Ready-first single-thread diagnostics, preserving completed ASR evidence."""
from pathlib import Path
import datetime,json,os,signal,shutil,subprocess,time,yaml
ROOT=Path(__file__).resolve().parents[3];PROD=ROOT/'studio/production/hb-c08';STATE=PROD/'durable-asr-state.json';OLD=49105
SECTIONS=['hb-c08-utveckling','hb-c08-smabarn','hb-c08-gymnasium','hb-c08-hogskolor','hb-c08-stod','hb-c12-sprak','hb-c08-grundskola','hb-c12-hemkommun','hb-c08-yrkesutbildning','hb-c12-e-tjanster','hb-c08-finansiering','hb-c12-tolkning','hb-c08-vuxna','hb-c12-norden-eu','hb-c12-integration','hb-c12-egna-arenden','hb-c12-myndigheter','hb-c12-personuppgifter','hb-c12-tjanster']
def stamp():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def save():
 p=STATE.with_suffix('.tmp');p.write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n');p.replace(STATE)
# The old controller may finish its current ASR invocation normally.
while Path(f'/proc/{OLD}').exists():
 old=json.loads(STATE.read_text())
 if any(j.get('status')=='running' for j in old['jobs'].values()):print(stamp(),'Retaining active ASR invocation owned by',OLD,flush=True);time.sleep(25);continue
 shutil.copy2(STATE,PROD/'durable-asr-state-before-reorder.json');os.kill(OLD,signal.SIGTERM);break
state=json.loads(STATE.read_text());state.update(supervisor_pid=os.getpid(),status='running',schedule='ready-first, one ASR thread; completed evidence retained');save();totals={sid:len(yaml.safe_load((ROOT/'studio/episodes'/sid/'script.yaml').read_text())['sentences']) for sid in SECTIONS}
while True:
 pending=[sid for sid in SECTIONS if state['jobs'].get(sid,{}).get('status')!='complete']
 if not pending:break
 ready=[]
 for sid in pending:
  folder=ROOT/'studio/media'/sid/'narration';mp=folder/'metrics.json';state['jobs'].setdefault(sid,dict(status='waiting_for_final_narration',total=totals[sid]))
  if mp.exists() and len(json.loads(mp.read_text()))==totals[sid]:ready.append(sid)
 save()
 if not ready:print(stamp(),'Waiting for finalized narration;',len(pending),'episodes pending',flush=True);time.sleep(35);continue
 sid=ready[0];folder=ROOT/'studio/media'/sid/'narration';log=PROD/(sid+'-asr-final.log')
 with log.open('a') as h:
  p=subprocess.Popen([str(ROOT/'studio/runtime/.venv/bin/python'),'studio/tools/check_audio.py',str(folder),'--language','sv','--pattern','hb-*.wav','--resume','--threads','1'],cwd=ROOT,stdout=h,stderr=subprocess.STDOUT);state['jobs'][sid].update(status='running',pid=p.pid,log=str(log.relative_to(ROOT)));save()
  while True:
   try:code=p.wait(timeout=35);break
   except subprocess.TimeoutExpired:print(stamp(),sid,'ASR running PID',p.pid,flush=True)
 state['jobs'][sid].update(status='complete' if code==0 else 'failed',exit_code=code);save()
 if code:state['status']='failed';save();raise SystemExit(code)
 subprocess.run([str(ROOT/'studio/runtime/.venv/bin/python'),'studio/production/hb-c08/diagnostics.py',sid],cwd=ROOT,check=True)
state['status']='complete';state['completed_at']=stamp();save()
