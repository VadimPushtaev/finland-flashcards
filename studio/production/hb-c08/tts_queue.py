"""Run a resumable source-order narration queue without replacing completed takes."""
from pathlib import Path
import os,json,subprocess,sys,time,yaml
ROOT=Path(__file__).resolve().parents[3];PROD=ROOT/'studio/production/hb-c08';STATE=PROD/'tts-state.json'
def write(d):STATE.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
sections=sys.argv[1:] or ['hb-c08-hux','hb-c08-utveckling','hb-c08-smabarn','hb-c08-gymnasium','hb-c08-hogskolor','hb-c08-grundskola','hb-c08-yrkesutbildning','hb-c08-finansiering','hb-c08-vuxna','hb-c08-stod']
state=dict(pid=os.getpid(),started=time.time(),jobs={});write(state)
# The first episode already has an exclusive producer; wait for its checkpoint.
first=ROOT/'studio/media/hb-c08-forskola/narration/metrics.json'
while not first.exists() or len(json.loads(first.read_text()))<26:
 state['waiting_for']='hb-c08-forskola narration checkpoint26';write(state);time.sleep(5)
state.pop('waiting_for',None);write(state)
for sid in sections:
 script=yaml.safe_load((ROOT/'studio/episodes'/sid/'script.yaml').read_text());out=ROOT/'studio/media'/sid/'narration';metrics=out/'metrics.json'
 if metrics.exists():
  old=json.loads(metrics.read_text());ids={m['sentence_id'] for m in old}
  if ids=={r['sentence_id'] for r in script['sentences']} and all((ROOT/m['path']).exists() for m in old):state['jobs'][sid]={'status':'complete_existing','clips':len(old)};write(state);continue
  raise ValueError('Partial existing narration requires deliberate checkpoint merge: '+sid)
 state['jobs'][sid]={'status':'validating'};write(state)
 for mode in ('review','validate'):
  subprocess.run([str(ROOT/'.venv/bin/python'),'studio/tools/script.py',mode,sid,'--ready'],cwd=ROOT,check=True,stdout=subprocess.DEVNULL)
 log=PROD/(sid+'-tts.log');cmd=[str(ROOT/'studio/runtime/.venv/bin/python'),'studio/tools/audition.py','supertonic','--voice','F1','--speed','.95','--section',sid,'--all','--threads','2','--output',str(out)]
 with log.open('a') as h:
  p=subprocess.Popen(cmd,cwd=ROOT,stdout=h,stderr=subprocess.STDOUT);state['jobs'][sid]={'status':'running','pid':p.pid,'log':str(log.relative_to(ROOT))};write(state)
  while p.poll() is None:
   try:p.wait(timeout=35)
   except subprocess.TimeoutExpired:
    print(time.strftime('%Y-%m-%dT%H:%M:%S'),sid,'TTS running; child PID',p.pid,'log',str(log.relative_to(ROOT)),flush=True)
  code=p.returncode
 state['jobs'][sid].update(status='complete' if code==0 else 'failed',exit_code=code);write(state)
 if code:sys.exit(code)
state['status']='complete';write(state)
