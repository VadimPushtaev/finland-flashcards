"""One authorized speech-only range comparison, preserving selected source/WAVs."""
from pathlib import Path
import datetime,hashlib,json,os,signal,subprocess,time,yaml
ROOT=Path(__file__).resolve().parents[3];PROD=ROOT/'studio/production/hb-c08';SID='hb-c08-vuxna';TARGET='hb-c08-u0144-s002';STATE=PROD/'range-comparison-state.json';state=json.loads(STATE.read_text());state['manager_pid']=os.getpid();original=None;changed=False

def stamp():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def save():STATE.write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n')
def children(parent):
 p=subprocess.run(['ps','-eo','pid,ppid,state,args'],capture_output=True,text=True,check=True);return [r for r in p.stdout.splitlines() if len(r.split())>2 and r.split()[1]==str(parent) and r.split()[2]!='Z']
def wait_children(parent):
 begin=time.monotonic()
 while children(parent):
  if time.monotonic()-begin>600:raise TimeoutError('Active batch wait exceeded ten minutes; supervisors will resume.')
  print(stamp(),'Waiting for current batch',parent,children(parent),flush=True);time.sleep(10)
def run(cmd,log):
 with log.open('ab',buffering=0) as h:
  p=subprocess.Popen(cmd,cwd=ROOT,stdout=h,stderr=subprocess.STDOUT);state.update(active_pid=p.pid,log=str(log.relative_to(ROOT)));save();start=time.monotonic()
  while True:
   try:return p.wait(timeout=35)
   except subprocess.TimeoutExpired:
    print(stamp(),'Comparison running',p.pid,flush=True)
    if time.monotonic()-start>600:p.terminate();return p.wait(timeout=30)
try:
 save();wait_children(78335);ep=ROOT/'studio/episodes'/SID;path=ep/'script.yaml';original=path.read_bytes();script=yaml.safe_load(original);row=next(r for r in script['sentences'] if r['sentence_id']==TARGET);assert '17–25-åriga' in row['sv'];selected=json.loads((ROOT/'studio/media'/SID/'narration/metrics.json').read_text());take=next(m for m in selected if m['sentence_id']==TARGET);oldwav=ROOT/take['path'];oldhash=hashlib.sha256(oldwav.read_bytes()).hexdigest();candidate=ROOT/'studio/media'/SID/'narration'/('range-comparison-'+stamp().replace(':','').replace('.',''));candidate.mkdir();(candidate/'script-before.yaml').write_bytes(original)
 text=row['sv'].replace('17–25-åriga','sjutton till tjugofemåriga');row['speech_override']=dict(text=text,reason='Single comparison warranted by two existing ASR passes misrendering archived17–25 age range; expand only the number range as Swedish spoken words.',review_status='approved');path.write_text(yaml.safe_dump(script,allow_unicode=True,sort_keys=False,width=100));changed=True;modified=path.read_bytes();state.update(status='synthesizing_one_comparison',candidate_dir=str(candidate.relative_to(ROOT)),old_wav=take['path'],old_wav_sha256=oldhash,original_text=take['text'],candidate_text=text,selected_metrics_unchanged=True,adoption='deferred until complete Vuxna queue and diagnostic comparison');save()
 code=run([str(ROOT/'studio/runtime/.venv/bin/python'),'studio/tools/audition.py','supertonic','--voice','F1','--speed','.95','--section',SID,'--indices','3','--threads','2','--output',str(candidate)],PROD/'range-comparison-tts.log');assert code==0,code;assert path.read_bytes()==modified,'Concurrent script producer change; inspect saved source snapshot';path.write_bytes(original);changed=False;assert hashlib.sha256(oldwav.read_bytes()).hexdigest()==oldhash;os.kill(78335,signal.SIGCONT);state['TTS_resumed_at']=stamp();save()
 os.kill(94559,signal.SIGSTOP);state.update(status='waiting_ASR_snapshot',ASR_paused=True);save();wait_children(94559);code=run([str(ROOT/'studio/runtime/.venv/bin/python'),'studio/tools/check_audio.py',str(candidate),'--pattern','hb-*.wav','--language','sv','--threads','1'],PROD/'range-comparison-asr.log');state.update(status='comparison_diagnostic_ready' if code==0 else 'comparison_diagnostic_failed',returncode=code,finished_at=stamp());save()
finally:
 if changed and original is not None:
  # Temporary speech-only proposal must never leak into the running selected-take queue.
  (ROOT/'studio/episodes'/SID/'script.yaml').write_bytes(original)
 os.kill(78335,signal.SIGCONT);os.kill(94559,signal.SIGCONT);state.update(TTS_resumed=True,ASR_resumed=True);save();print(stamp(),'Both supervisors resumed; comparison preserved outside selected metrics',flush=True)
