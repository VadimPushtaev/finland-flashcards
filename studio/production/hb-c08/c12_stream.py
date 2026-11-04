"""Dispatch only the coordinator-assigned frozen C12 stream after exact slot releases."""
from pathlib import Path
import datetime,hashlib,json,os,subprocess,time,yaml
ROOT=Path(__file__).resolve().parents[3];PROD=Path(__file__).parent;STATE=PROD/'c12-stream-state.json';QUEUE=PROD/'c12-stream-queue.json';state=dict(supervisor_pid=os.getpid(),started_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),status='running',predecessor=dict(section_id='hb-c12-tjanster',supervisor_pid=306005),launched=[])
def stamp():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save():
 p=STATE.with_suffix('.tmp');p.write_text(json.dumps(state,indent=2)+'\n');p.replace(STATE)
def active():
 result=[]
 for line in subprocess.check_output(['ps','-eo','pid,ppid,args'],text=True).splitlines():
  parts=line.split()
  if len(parts)>3 and Path(parts[2]).name.startswith('python') and any(p.endswith('studio/tools/render.py') for p in parts[3:]) and '--stills-only' not in parts:result.append(line.strip())
 return result
def frozen(section):
 f=next(r for r in json.loads((PROD/'ready-export-freezes.json').read_text())['episodes'] if r['section_id']==section)
 for r in f['input_snapshots'].values():assert sha(ROOT/r['path'])==r['sha256'],r['path']
 ep=ROOT/'studio/episodes'/section;narr=ROOT/'studio/media'/section/'narration';s=yaml.load((ep/'script.yaml').read_text(),Loader=yaml.CSafeLoader);metrics=json.loads((narr/'metrics.json').read_text());asr={Path(r['file']).stem:r for r in json.loads((narr/'asr.json').read_text())};assert [r['sentence_id'] for r in metrics]==[r['sentence_id'] for r in s['sentences']]
 for row,m in zip(s['sentences'],metrics):
  assert m['text']==(row.get('speech_override') or {}).get('text',row['sv']);assert sha(ROOT/m['path'])==asr[m['sentence_id']]['sha256']
 assert len(asr)==len(metrics)
 return f
save()
try:
 while True:
  queue=json.loads(QUEUE.read_text())['successors'];done={r['section_id'] for r in state['launched']};remaining=[r for r in queue if r not in done]
  if not remaining:state.update(status='all_assigned_successors_launched',completed_at=stamp());save();break
  pred=state['predecessor'];release=json.loads((PROD/(pred['section_id']+'-export-state.json')).read_text());assert release['supervisor_pid']==pred['supervisor_pid'],'Predecessor changed'
  stage=release.get('stages',{}).get('render',{})
  if stage.get('status')=='failed':raise RuntimeError('Assigned predecessor failed; retain all assets/takes for repair')
  if stage.get('status')=='complete':
   assert stage['exit_code']==0;ep=ROOT/'studio/episodes'/pred['section_id'];r=json.loads((ep/'render.json').read_text());assert (ROOT/r['output']).is_file();section=remaining[0];host=active();budget=json.loads((ROOT/'studio/production/remaining/resource-budget.json').read_text())['max_full_encoders']
   if len(host)<budget:
    freeze=frozen(section);assert not (ROOT/'studio/episodes'/section/'render.json').exists(),'Export already present; refuse duplicate'
    with (PROD/(section+'-export-supervisor.log')).open('ab',buffering=0) as h:child=subprocess.Popen([str(ROOT/'studio/runtime/.venv/bin/python'),str(PROD/'export_pipeline.py'),section],cwd=ROOT,stdout=h,stderr=subprocess.STDOUT,start_new_session=True)
    proof=dict(section_id=section,supervisor_pid=child.pid,launched_at=stamp(),predecessor=pred,predecessor_render_stage=stage,current_frozen_inputs=freeze,selected_wav_asr_hash_checks='all current exact matches',prior_full_renderers=host,max_full_encoders=budget)
    (PROD/(section+'-stream-launch-proof.json')).write_text(json.dumps(proof,indent=2)+'\n');state['launched'].append(proof);state['predecessor']=dict(section_id=section,supervisor_pid=child.pid);save();print('LAUNCHED',section,child.pid,flush=True)
  state['heartbeat_at']=stamp();save();print(state['heartbeat_at'],'assigned stream waiting/monitoring',state['predecessor'],flush=True);time.sleep(35)
except Exception as exc:state.update(status='failed_closed',error=repr(exc));save();raise
