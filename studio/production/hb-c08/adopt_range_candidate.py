"""Adopt the single approved age-range comparison after Vuxna's metrics writer finishes."""
from pathlib import Path
import datetime,hashlib,json,os,signal,subprocess,time,yaml
ROOT=Path(__file__).resolve().parents[3];PROD=ROOT/'studio/production/hb-c08';SID='hb-c08-vuxna';TARGET='hb-c08-u0144-s002';STATE=PROD/'range-adoption-state.json';state={'manager_pid':os.getpid(),'started_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'waiting_Vuxna_complete'};paused=False

def stamp():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def atomic(p,d):
 q=p.with_suffix(p.suffix+'.tmp');q.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n');q.replace(p)
def save():atomic(STATE,state)
def children(parent):
 r=subprocess.run(['ps','-eo','pid,ppid,state,args'],capture_output=True,text=True,check=True);return [line for line in r.stdout.splitlines() if len(line.split())>2 and line.split()[1]==str(parent) and line.split()[2]!='Z']
try:
 while json.loads((PROD/'durable-tts-state.json').read_text())['jobs'].get(SID,{}).get('status')!='complete':save();print(stamp(),'Waiting for finalized Vuxna selected metrics',flush=True);time.sleep(35)
 comp=json.loads((PROD/'range-comparison-state.json').read_text());assert comp['status']=='comparison_diagnostic_ready';candidate=ROOT/comp['candidate_dir'];new=json.loads((candidate/'metrics.json').read_text())[0];asr=json.loads((candidate/'asr.json').read_text())[0];assert asr['sha256']==sha(ROOT/new['path']);assert '17 till 25' in asr['asr_text'];ep=ROOT/'studio/episodes'/SID;media=ROOT/'studio/media'/SID;mp=media/'narration/metrics.json';metrics=json.loads(mp.read_text());assert len(metrics)==63;old=next(m for m in metrics if m['sentence_id']==TARGET);assert sha(ROOT/old['path'])==comp['old_wav_sha256'];assert old['path']!=new['path'];assert not (ep/'render.json').exists()
 os.kill(94559,signal.SIGSTOP);paused=True;state.update(status='waiting_current_ASR_before_adoption',ASR_paused_at=stamp());save();begin=time.monotonic()
 while children(94559):
  if time.monotonic()-begin>600:raise TimeoutError('Current ASR snapshot still active; no selection changed.')
  print(stamp(),'Waiting for immutable ASR snapshot',children(94559),flush=True);time.sleep(10)
 before=mp.read_bytes();(ep/'narration-metrics-before-range-revision.json').write_bytes(before);scriptpath=ep/'script.yaml';script=yaml.safe_load(scriptpath.read_text());row=next(r for r in script['sentences'] if r['sentence_id']==TARGET);assert row['display_segments'][1].get('speech_offset_seconds') is None;assert comp['candidate_text']==row['sv'].replace('17–25-åriga','sjutton till tjugofemåriga');row['speech_override']={'text':new['text'],'reason':'Approved single comparison: two original ASR passes misread17–25; candidate recognizes17 till25. Visible source/Russian unchanged. Candidate possible repeated ordnas and extra en remain unconfirmed listening flags.','review_status':'approved'};row['pronunciation_notes'].append('Selected one number-word range comparison; retain original and candidate. ASR age range improves, but possible repeated ordnas/extra en still need complete-video listening.')
 new['generation_run']='Single approved number-range comparison '+comp['candidate_dir']+'; fresh NumPyseed42,F1,.95,2threads; original retained at '+old['path'];metrics=[new if m['sentence_id']==TARGET else m for m in metrics];atomic(mp,metrics);scriptpath.write_text(yaml.safe_dump(script,allow_unicode=True,sort_keys=False,width=100))
 ap=media/'narration/asr.json';reports={r['file']:r for r in json.loads(ap.read_text())};reports[new['path']]=asr;atomic(ap,[reports[m['path']] for m in metrics if m['path'] in reports]);retired=[]
 for folder in (media/'narration/asr-snapshots').glob('*'):
  p=folder/'snapshot.json'
  if not p.exists():continue
  data=json.loads(p.read_text())
  if any(f['canonical_file']==old['path'] for f in data['files']):
   assert (folder/'asr.json').exists();assert len(json.loads((folder/'asr.json').read_text()))==len(data['files']);oldmanifest=folder/'prior-selection-snapshot.json';assert not oldmanifest.exists();p.rename(oldmanifest);atomic(folder/'retired-selection.json',{'reason':'This immutable snapshot includes a superseded selected take; raw WAVs/report/original manifest retained, all unchanged rows already merged into canonical ASR.','retired_at':stamp(),'original_manifest':str(oldmanifest.relative_to(ROOT)),'manifest_sha256':sha(oldmanifest),'old_selected_wav':old['path'],'new_selected_wav':new['path']});retired.append(str(oldmanifest.relative_to(ROOT)))
 preservation=ep/'narration-preservation.json';pr=json.loads(preservation.read_text());pr['prior_selected_takes_before_range_revision']=pr['selected_takes'];pr['selected_takes']=[dict(sentence_id=m['sentence_id'],path=m['path'],sha256=sha(ROOT/m['path']),generation_run=m.get('generation_run')) for m in metrics];pr['range_revision']={'old_take':old,'new_take':new,'original_wav_unchanged':sha(ROOT/old['path'])==comp['old_wav_sha256'],'diagnostic_basis':'Age range now17 till25 instead of sju-fem-fem /17–25–25; possible repeated words remain unconfirmed. No whole-video listening claimed.','retired_snapshot_manifests':retired};atomic(preservation,pr);state.update(status='adopted_measuring_fresh_boundary',old_wav=old['path'],new_wav=new['path'],new_sha256=asr['sha256'],adopted_at=stamp(),retired_snapshot_manifests=retired);save()
 with (PROD/'range-adopted-display-alignment.log').open('ab',buffering=0) as h:
  p=subprocess.Popen([str(ROOT/'studio/runtime/.venv/bin/python'),'studio/production/remaining/align_display_segments.py',SID,'--sentence-id',TARGET,'--threads','1','--apply'],cwd=ROOT,stdout=h,stderr=subprocess.STDOUT);state['alignment_pid']=p.pid;save();begin=time.monotonic()
  while True:
   try:code=p.wait(timeout=35);break
   except subprocess.TimeoutExpired:
    print(stamp(),'Fresh selected-WAV boundary alignment',p.pid,flush=True)
    if time.monotonic()-begin>600:p.terminate();code=p.wait(timeout=30);break
 state.update(status='selected_boundary_applied' if code==0 else 'selected_boundary_manual_review_required',returncode=code,finished_at=stamp());save()
finally:
 if paused:os.kill(94559,signal.SIGCONT);state.update(ASR_resumed=True);save()
 print(stamp(),'Adoption manager ended; original take and all records retained',flush=True)
