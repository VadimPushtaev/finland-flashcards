"""Resume only missing narration takes, retaining per-invocation metrics and PIDs."""
from pathlib import Path
import json,subprocess,datetime,hashlib,os,sys,time
ROOT=Path(__file__).resolve().parents[3];PROD=Path(__file__).resolve().parent;SID='hb-c10-valfard';MEDIA=ROOT/'studio/media'/SID;EP=ROOT/'studio/episodes'/SID
STATUS=PROD/f'{SID}-resume-status.json';CONTROL=PROD/f'{SID}-resume-control.json'
def stamp():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def save(d):STATUS.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
import yaml
script=yaml.safe_load((EP/'script.yaml').read_text());rows=script['sentences'];selected={}
for folder,label in[(MEDIA/'narration','Initial source-order seed42 invocation, interrupted after13complete clips.'),(MEDIA/'narration-resume-1','First resume source-order subset indices13-22, freshNumPyseed42 invocation, interrupted after2complete clips.')]:
    p=folder/'metrics.json'
    if p.exists():
        for m in json.loads(p.read_text()):
            checksum=hashlib.sha256((ROOT/m['path']).read_bytes()).hexdigest();m['generation_run']=label;selected[m['sentence_id']]=dict(metric=m,sha256=checksum)
# Include successfully checkpointed later chunks if supervisor itself restarts.
for folder in sorted(MEDIA.glob('narration-resume-chunk-*')):
    p=folder/'metrics.json'
    if p.exists():
        for m in json.loads(p.read_text()):
            m['generation_run']=f'{folder.name}:freshNumPyseed42perinvocation, retainedsource-orderrequestedsubset.';selected[m['sentence_id']]=dict(metric=m,sha256=hashlib.sha256((ROOT/m['path']).read_bytes()).hexdigest())
state=dict(section_id=SID,supervisor_pid=os.getpid(),status='running',started_at=stamp(),retained_takes=len(selected),completed_invocations=[],active_pid=None);save(state)
while len(selected)<len(rows):
    control=json.loads(CONTROL.read_text()) if CONTROL.exists() else {}
    if control.get('stop_after_chunk'):
        state.update(status='checkpointed',completed_takes=len(selected),finished_at=stamp());save(state);raise SystemExit(0)
    indices=[i for i,r in enumerate(rows) if r['sentence_id'] not in selected][:5]
    serial=1
    while (MEDIA/f'narration-resume-chunk-{serial:02}').exists():serial+=1
    dest=MEDIA/f'narration-resume-chunk-{serial:02}';log=PROD/'logs'/f'{SID}-resume-chunk-{serial:02}.log';cmd=[str(ROOT/'studio/runtime/.venv/bin/python'),str(ROOT/'studio/tools/audition.py'),'supertonic','--voice','F1','--speed','.95','--section',SID,'--indices',','.join(map(str,indices)),'--threads','2','--output',str(dest)]
    with log.open('w') as out:
        p=subprocess.Popen(cmd,cwd=ROOT,stdout=out,stderr=subprocess.STDOUT);state.update(active_pid=p.pid,active_indices=indices,active_log=str(log.relative_to(ROOT)),completed_takes=len(selected));save(state)
        rc=p.wait()
    checkpoint=dest/'metrics.json'
    if checkpoint.exists():
        for m in json.loads(checkpoint.read_text()):
            m['generation_run']=f'{dest.name}:freshNumPyseed42perinvocation, source-orderindices{indices}.';selected[m['sentence_id']]=dict(metric=m,sha256=hashlib.sha256((ROOT/m['path']).read_bytes()).hexdigest())
    state['completed_invocations'].append(dict(indices=indices,pid=p.pid,returncode=rc,log=str(log.relative_to(ROOT)),metrics=str(checkpoint.relative_to(ROOT)),finished_at=stamp()));save(state)
    if rc:
        state.update(status='failed_checkpoint_retained',completed_takes=len(selected),active_pid=None,finished_at=stamp());save(state);raise SystemExit(rc)
ordered=[selected[r['sentence_id']]['metric'] for r in rows]
for r,m in zip(rows,ordered):
    assert m['text']==(r.get('speech_override') or {}).get('text',r['sv'])
    assert hashlib.sha256((ROOT/m['path']).read_bytes()).hexdigest()==selected[r['sentence_id']]['sha256']
original=MEDIA/'narration/metrics.json';backup=MEDIA/'narration/metrics.initial.json'
if not backup.exists():backup.write_bytes(original.read_bytes())
original.write_text(json.dumps(ordered,ensure_ascii=False,indent=2)+'\n')
(EP/'narration-preservation.json').write_text(json.dumps(dict(section_id=SID,selected_takes=[dict(sentence_id=r['sentence_id'],path=selected[r['sentence_id']]['metric']['path'],sha256=selected[r['sentence_id']]['sha256'],generation_run=selected[r['sentence_id']]['metric']['generation_run']) for r in rows],original_initial_and_resume_takes_unchanged=True,interruption_reason='Two externally terminated tool sessions143; exact cause unknown, no model exception or OOM evidence.',supervisor_pid=os.getpid()),ensure_ascii=False,indent=2)+'\n')
state.update(status='complete',completed_takes=len(ordered),active_pid=None,finished_at=stamp());save(state)
