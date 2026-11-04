"""Retain a completing invocation and hand off future synthesis without duplicates."""
from pathlib import Path
import datetime,hashlib,json,os,signal,shutil,subprocess,time,yaml
ROOT=Path(__file__).resolve().parents[3];PROD=ROOT/'studio/production/hb-c08';record=json.loads((PROD/'reorder-checkpoint.json').read_text());sid='hb-c08-grundskola';pid=record['active_child_pid'];old=record['paused_supervisor_pid']
def running(pid):
 try:
  raw=Path(f'/proc/{pid}/stat').read_text();return raw.rsplit(')',1)[1].split()[0]!='Z'
 except FileNotFoundError:return False
while running(pid):
 print(datetime.datetime.now(datetime.timezone.utc).isoformat(),'Finishing preserved invocation',pid,flush=True);time.sleep(20)
chunk=ROOT/record['current_chunk'];rows=yaml.safe_load((ROOT/'studio/episodes'/sid/'script.yaml').read_text())['sentences'];folder=ROOT/'studio/media'/sid/'narration';mp=folder/'metrics.json';selected={m['sentence_id']:m for m in json.loads(mp.read_text())};before={k:hashlib.sha256((ROOT/m['path']).read_bytes()).hexdigest() for k,m in selected.items()};checkpoint=json.loads((chunk/'metrics.json').read_text());expected={rows[i]['sentence_id'] for i in record['indices']};assert expected=={m['sentence_id'] for m in checkpoint},'Invocation incomplete; preserve without starting another writer'
for m in checkpoint:
 if m['sentence_id'] in selected:continue
 source=ROOT/m['path'];dest=folder/source.name;shutil.copy2(source,dest);m['path']=str(dest.relative_to(ROOT));m['generation_run']='Missing-only chunk '+record['current_chunk']+'; freshNumPyseed42,sourceorderwithinchunk';selected[m['sentence_id']]=m
for k,h in before.items():assert hashlib.sha256((ROOT/selected[k]['path']).read_bytes()).hexdigest()==h
mp.write_text(json.dumps([selected[r['sentence_id']] for r in rows if r['sentence_id'] in selected],ensure_ascii=False,indent=2)+'\n');record.update(retained_selected=len(selected),retained_before_hashes=before,all_retained_unchanged=True,completed_at=datetime.datetime.now(datetime.timezone.utc).isoformat());(PROD/'reorder-completed.json').write_text(json.dumps(record,indent=2)+'\n');os.kill(old,signal.SIGTERM);os.kill(old,signal.SIGCONT)
while running(old):time.sleep(1)
shutil.copy2(PROD/'durable-tts-state.json',PROD/'durable-tts-state-before-reorder.json')
with (PROD/'durable-tts.log').open('ab') as log:
 p=subprocess.Popen([str(ROOT/'studio/runtime/.venv/bin/python'),'studio/production/hb-c08/durable_tts.py'],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
print('Reordered synthesis supervisor',p.pid,flush=True)
