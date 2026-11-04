"""Measure selected immutable display boundaries in the sole ASR lane, then resume it."""
from pathlib import Path
import datetime,json,os,signal,subprocess,sys,time
ROOT=Path(__file__).resolve().parents[3];PROD=ROOT/'studio/production/hb-c08';SID=sys.argv[1];STATE=PROD/'display-alignment-job-state.json';state=json.loads(STATE.read_text());state.update(manager_pid=os.getpid(),section_id=SID)
def save():STATE.write_text(json.dumps(state,indent=2)+'\n')
def children():
 result=subprocess.run(['ps','-eo','pid,ppid,state,args'],capture_output=True,text=True,check=True)
 return [line for line in result.stdout.splitlines() if len(line.split())>2 and line.split()[1]=='94559' and line.split()[2]!='Z']
try:
 while children():
  print(datetime.datetime.now(datetime.timezone.utc).isoformat(),'Waiting for existing immutable ASR snapshot',children(),flush=True);time.sleep(10)
 state['waiting_for_current_child']=False;save()
 with (PROD/(SID+'-display-alignment.log')).open('ab',buffering=0) as h:
  p=subprocess.Popen([str(ROOT/'studio/runtime/.venv/bin/python'),'studio/production/remaining/align_display_segments.py',SID,*sys.argv[2:],'--threads','1','--apply'],cwd=ROOT,stdout=h,stderr=subprocess.STDOUT);state.update(active_pid=p.pid,started_at=datetime.datetime.now(datetime.timezone.utc).isoformat());save();start=time.monotonic()
  while True:
   try:code=p.wait(timeout=35);break
   except subprocess.TimeoutExpired:
    print(datetime.datetime.now(datetime.timezone.utc).isoformat(),SID,'actual word alignment running',p.pid,flush=True)
    if time.monotonic()-start>600:p.terminate();code=p.wait(timeout=30);state['timeout']=True;break
 state['returncode']=code;save()
finally:
 os.kill(94559,signal.SIGCONT);state.update(ASR_resumed=True,finished_at=datetime.datetime.now(datetime.timezone.utc).isoformat());save();print('ASR resumed',state,flush=True)
