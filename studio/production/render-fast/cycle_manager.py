"""Run the bounded prototype and always resume the owned ASR supervisor afterward."""
from pathlib import Path
import datetime,json,os,signal,subprocess,time
ROOT=Path(__file__).resolve().parents[3];PROD=ROOT/'studio/production/render-fast';state={'started_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'manager_pid':os.getpid(),'ASR_supervisor_pid':94559};path=PROD/'cycle-cache-state.json'
def save():path.write_text(json.dumps(state,indent=2)+'\n')
try:
 save()
 with (PROD/'cycle-cache.log').open('ab',buffering=0) as h:
  child=subprocess.Popen([str(ROOT/'studio/runtime/.venv/bin/python'),str(PROD/'cycle_cache.py')],cwd=ROOT,stdout=h,stderr=subprocess.STDOUT,start_new_session=True);state['child_pid']=child.pid;save();start=time.monotonic()
  while True:
   try:code=child.wait(timeout=35);break
   except subprocess.TimeoutExpired:
    print(datetime.datetime.now(datetime.timezone.utc).isoformat(),'prototype PID',child.pid,'running',flush=True)
    if time.monotonic()-start>1000:os.killpg(child.pid,signal.SIGTERM);code=child.wait(timeout=20);state['timeout']=True;break
 state['returncode']=code
finally:
 os.kill(94559,signal.SIGCONT);state.update(finished_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),ASR_resumed=True);save();print('ASR resumed',state,flush=True)
