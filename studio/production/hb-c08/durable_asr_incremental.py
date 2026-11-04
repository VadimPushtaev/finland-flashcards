"""Single-thread ASR of immutable registered takes via isolated snapshot batches."""
from pathlib import Path
import datetime,hashlib,json,os,shutil,subprocess,time,yaml
import soundfile as sf
ROOT=Path(__file__).resolve().parents[3];PROD=ROOT/'studio/production/hb-c08';STATE=PROD/'durable-asr-state.json';PY=ROOT/'studio/runtime/.venv/bin/python'
SECTIONS=['hb-c08-stod','hb-c08-utveckling','hb-c08-smabarn','hb-c08-gymnasium','hb-c08-hogskolor','hb-c08-grundskola','hb-c12-sprak','hb-c12-hemkommun','hb-c08-yrkesutbildning','hb-c12-e-tjanster','hb-c08-finansiering','hb-c12-tolkning','hb-c08-vuxna','hb-c12-norden-eu','hb-c12-integration','hb-c12-egna-arenden','hb-c12-myndigheter','hb-c12-personuppgifter','hb-c12-tjanster']
def stamp():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def atomic(path,data):
 tmp=path.with_suffix(path.suffix+'.tmp');tmp.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n');tmp.replace(path)
def save():atomic(STATE,state)
def metrics(sid):
 p=ROOT/'studio/media'/sid/'narration/metrics.json';return json.loads(p.read_text()) if p.exists() else []
def registered(sid):return {m['path']:m for m in metrics(sid)}
def merge_snapshot(snapshot):
 manifest=json.loads((snapshot/'snapshot.json').read_text());sid=manifest['section_id'];report=snapshot/'asr.json'
 if not report.exists():return
 current=registered(sid);dest=ROOT/'studio/media'/sid/'narration/asr.json';old={r['file']:r for r in json.loads(dest.read_text())} if dest.exists() else {};mapping={m['staged_file']:m for m in manifest['files']}
 for r in json.loads(report.read_text()):
  m=mapping[r['file']];assert r['sha256']==m['sha256'];assert m['canonical_file'] in current;assert sha(ROOT/m['canonical_file'])==m['sha256'];old[m['canonical_file']]={**r,'file':m['canonical_file']}
 rows=[old[m['path']] for m in metrics(sid) if m['path'] in old];atomic(dest,rows);manifest.update(merged_at=stamp(),canonical_records=len(rows));atomic(snapshot/'snapshot.json',manifest)
state=json.loads(STATE.read_text());state.update(supervisor_pid=os.getpid(),status='running',schedule='registered immutable snapshots only;16clipbatches;oneASRthread');save();totals={sid:len(yaml.safe_load((ROOT/'studio/episodes'/sid/'script.yaml').read_text())['sentences']) for sid in SECTIONS}
for sid in SECTIONS:
 for snapshot in sorted((ROOT/'studio/media'/sid/'narration/asr-snapshots').glob('*')):
  if (snapshot/'snapshot.json').exists():merge_snapshot(snapshot)
while True:
 pending=[sid for sid in SECTIONS if state['jobs'].get(sid,{}).get('status')!='complete']
 if not pending:break
 ready=[]
 for sid in pending:
  ms=metrics(sid);folder=ROOT/'studio/media'/sid/'narration';ap=folder/'asr.json';old={r['file']:r for r in json.loads(ap.read_text())} if ap.exists() else {};missing=[]
  # Only paths committed to canonical metrics are inspected. Other WAVs may be in flight.
  for m in ms:
   p=ROOT/m['path'];checksum=sha(p)
   if old.get(m['path'],{}).get('sha256')!=checksum:missing.append((m,checksum))
  state['jobs'].setdefault(sid,dict(total=totals[sid]));state['jobs'][sid].update(selected=len(ms),checked=len(ms)-len(missing),status='partial_waiting' if len(ms)<totals[sid] else 'ready_for_final_diagnostics')
  if missing:ready.append((sid,missing[:16]));continue
  if len(ms)==totals[sid]:
   subprocess.run([str(PY),'studio/production/hb-c08/diagnostics.py',sid],cwd=ROOT,check=True);state['jobs'][sid].update(status='complete',completed_at=stamp());save();print(stamp(),sid,'ASR COMPLETE',len(ms),flush=True)
 save()
 if not ready:print(stamp(),'Waiting for completed registered takes;',len(pending),'episodes pending',flush=True);time.sleep(35);continue
 sid,selected=ready[0];snapshot=ROOT/'studio/media'/sid/'narration/asr-snapshots'/stamp().replace(':','').replace('.','');snapshot.mkdir(parents=True);files=[]
 for m,checksum in selected:
  source=ROOT/m['path'];assert sha(source)==checksum;info=sf.info(source);assert info.channels==1 and info.samplerate==44100 and abs(info.duration-m['seconds'])<1/44100
  staged=snapshot/source.name;shutil.copy2(source,staged);assert sha(staged)==sha(source)==checksum;files.append(dict(staged_file=str(staged.relative_to(ROOT)),canonical_file=m['path'],sha256=checksum,synthesis_metrics=m))
 atomic(snapshot/'snapshot.json',dict(section_id=sid,created_at=stamp(),policy='Only completed canonical-metrics members, copied and checksum-verified before transcription. No synthesis destination folder globbed.',files=files));log=PROD/(sid+'-asr-snapshot-'+snapshot.name+'.log')
 with log.open('ab') as h:
  child=subprocess.Popen([str(PY),'studio/tools/check_audio.py',str(snapshot),'--pattern','hb-*.wav','--language','sv','--threads','1','--resume'],cwd=ROOT,stdout=h,stderr=subprocess.STDOUT);state['jobs'][sid].update(status='running_snapshot',pid=child.pid,snapshot=str(snapshot.relative_to(ROOT)),log=str(log.relative_to(ROOT)));save()
  while True:
   try:code=child.wait(timeout=35);break
   except subprocess.TimeoutExpired:print(stamp(),sid,'ASR snapshot running',child.pid,'clips',len(files),flush=True)
 merge_snapshot(snapshot);state['jobs'][sid].update(status='partial_checked' if code==0 else 'failed',last_exit_code=code);save()
 if code:state['status']='failed';save();raise SystemExit(code)
state['status']='complete';state['completed_at']=stamp();save()
