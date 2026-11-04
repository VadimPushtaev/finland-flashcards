"""Detached, resumable Chapter 8 narration production with immutable selected takes."""
from pathlib import Path
import datetime,hashlib,json,os,shutil,subprocess,sys,time
import yaml
ROOT=Path(__file__).resolve().parents[3];PROD=ROOT/'studio/production/hb-c08';STATE=PROD/'durable-tts-state.json';PY=ROOT/'studio/runtime/.venv/bin/python'
SECTIONS=['hb-c08-stod','hb-c12-sprak','hb-c08-grundskola','hb-c12-hemkommun','hb-c08-yrkesutbildning','hb-c12-e-tjanster','hb-c08-finansiering','hb-c12-tolkning','hb-c08-vuxna','hb-c12-norden-eu','hb-c12-integration','hb-c12-egna-arenden','hb-c12-myndigheter','hb-c12-personuppgifter','hb-c12-tjanster']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def stamp():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def save():
 tmp=STATE.with_suffix('.tmp');tmp.write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n');tmp.replace(STATE)
def metrics_write(path,rows,selected):
 entries=[selected[r['sentence_id']] for r in rows if r['sentence_id'] in selected];tmp=path.with_suffix('.tmp');tmp.write_text(json.dumps(entries,ensure_ascii=False,indent=2)+'\n');tmp.replace(path)
state=dict(supervisor_pid=os.getpid(),started_at=stamp(),status='running',jobs={});save()
for sid in SECTIONS:
 ep=ROOT/'studio/episodes'/sid;d=yaml.safe_load((ep/'script.yaml').read_text());rows=d['sentences'];out=ROOT/'studio/media'/sid/'narration';out.mkdir(parents=True,exist_ok=True);metrics=out/'metrics.json';selected={m['sentence_id']:m for m in json.loads(metrics.read_text())} if metrics.exists() else {};before={k:sha(ROOT/m['path']) for k,m in selected.items()}
 for r in rows:
  if r['sentence_id'] in selected:assert selected[r['sentence_id']]['text']==(r.get('speech_override') or {}).get('text',r['sv'])
 # Preserve any fully written but not checkpointed orphan separately.
 for r in rows:
  p=out/(r['sentence_id']+'.wav')
  if p.exists() and r['sentence_id'] not in selected:
   archive=out/'interrupted-unselected';archive.mkdir(exist_ok=True);dest=archive/p.name
   if dest.exists():dest=archive/(p.stem+'-'+sha(p)[:12]+'.wav')
   shutil.copy2(p,dest)
 state['jobs'][sid]=dict(status='validating',retained_before=len(selected),total=len(rows));save()
 for mode in ('review','validate'):subprocess.run([str(ROOT/'.venv/bin/python'),'studio/tools/script.py',mode,sid,'--ready'],cwd=ROOT,check=True)
 invocation=0
 while len(selected)<len(rows):
  missing=[i for i,r in enumerate(rows) if r['sentence_id'] not in selected][:8];invocation+=1;chunk=out/('resume-'+stamp().replace(':','').replace('-','').replace('.','')+'-'+str(invocation));chunk.mkdir();log=PROD/(sid+'-resume-'+chunk.name+'.log');cmd=[str(PY),'studio/tools/audition.py','supertonic','--voice','F1','--speed','.95','--section',sid,'--indices',','.join(map(str,missing)),'--threads','2','--output',str(chunk)]
  with log.open('a') as h:
   p=subprocess.Popen(cmd,cwd=ROOT,stdout=h,stderr=subprocess.STDOUT);state['jobs'][sid].update(status='running',active_pid=p.pid,indices=missing,chunk=str(chunk.relative_to(ROOT)),log=str(log.relative_to(ROOT)));save()
   while True:
    try:code=p.wait(timeout=35);break
    except subprocess.TimeoutExpired:
     print(stamp(),sid,'TTS running, PID',p.pid,'selected',len(selected),'of',len(rows),flush=True)
     checkpoint=chunk/'metrics.json'
     if checkpoint.exists():
      for m in json.loads(checkpoint.read_text()):
       if m['sentence_id'] in selected:continue
       source=ROOT/m['path'];dest=out/source.name;shutil.copy2(source,dest);m['path']=str(dest.relative_to(ROOT));m['generation_run']='Missing-only chunk '+str(chunk.relative_to(ROOT))+'; freshNumPyseed42,sourceorderwithinchunk';selected[m['sentence_id']]=m
      metrics_write(metrics,rows,selected);state['jobs'][sid]['selected']=len(selected);save()
  checkpoint=chunk/'metrics.json'
  if checkpoint.exists():
   for m in json.loads(checkpoint.read_text()):
    if m['sentence_id'] in selected:continue
    source=ROOT/m['path'];dest=out/source.name;shutil.copy2(source,dest);m['path']=str(dest.relative_to(ROOT));m['generation_run']='Missing-only chunk '+str(chunk.relative_to(ROOT))+'; freshNumPyseed42,sourceorderwithinchunk';selected[m['sentence_id']]=m
   metrics_write(metrics,rows,selected)
  state['jobs'][sid].update(last_exit_code=code,selected=len(selected),active_pid=None);save()
  if code:
   state['status']='failed';state['jobs'][sid]['status']='interrupted_preserved';save();raise SystemExit(code)
 for k,h in before.items():assert sha(ROOT/selected[k]['path'])==h
 (ep/'narration-preservation.json').write_text(json.dumps(dict(section_id=sid,interruption_reason='Durable missing-only production; earlier selected takes retained byte-identical. Future queue reorder occurs between complete invocations.',initial_retained_hashes=before,all_initial_retained_unchanged=True,selected_takes=[dict(sentence_id=r['sentence_id'],path=selected[r['sentence_id']]['path'],sha256=sha(ROOT/selected[r['sentence_id']]['path']),generation_run=selected[r['sentence_id']].get('generation_run','Original complete-stream invocation before interruption')) for r in rows]),ensure_ascii=False,indent=2)+'\n');state['jobs'][sid].update(status='complete',selected=len(selected));save();print(stamp(),sid,'COMPLETE',len(selected),flush=True)
state['status']='complete';state['completed_at']=stamp();save()
