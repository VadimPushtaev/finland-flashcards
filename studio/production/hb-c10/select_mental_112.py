"""Select one explicit-digit emergency-number take while retaining the complete original set."""
from pathlib import Path
import json,hashlib,shutil,datetime,re
R=Path(__file__).resolve().parents[3];E=R/'studio/episodes/hb-c10-psykisk';M=R/'studio/media/hb-c10-psykisk';N=M/'narration';T=M/'narration-retakes/emergency112';target='hb-c10-u0130-s001';proof=json.loads((E/'emergency112-retake-proof.json').read_text());new=json.loads((T/'metrics.json').read_text());diag=json.loads((T/'asr.json').read_text());assert len(new)==len(diag)==1 and new[0]['sentence_id']==target;take=new[0];a=diag[0];assert take['voice']=='F1'and take['speed']==.95 and take['seed']==42 and'ett ett två'in take['text'];assert a['sha256']==hashlib.sha256((R/take['path']).read_bytes()).hexdigest();text=a['asr_text'];normalized=re.sub(r'[^a-zåäö0-9]','',text.lower());selected='112'in normalized or'ettetttvå'in normalized
comparison=dict(updated_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),original_input=proof['original_selected_takes'][52]['text'],original_asr=next(r['asr_text']for r in json.loads((M/'revisions/pre-emergency112/asr.json').read_text())if r['file']==proof['original_selected_takes'][52]['path']),retake_metrics=take,retake_asr=a,selected=selected,selection_basis='Exact explicit-digit synthesis input and bounded diagnostic confirmation,not listening or proof of accent/acoustic correctness.',whole_video_listening=False)
(E/'emergency112-comparison.json').write_text(json.dumps(comparison,ensure_ascii=False,indent=2)+'\n')
if not selected:
 print('Bounded comparison not selected automatically;both takes retained. Independent tail work may continue.');raise SystemExit(0)
if proof.get('new_selected_take'):
 assert hashlib.sha256((R/proof['original_selected_takes'][52]['path']).read_bytes()).hexdigest()==proof['new_sha256']
 for row in proof['original_selected_takes']:
  if row['sentence_id']!=target:assert hashlib.sha256((R/row['path']).read_bytes()).hexdigest()==row['sha256']
 print('Already selected this one bounded take;current hashes preserved.');raise SystemExit(0)
metrics=json.loads((N/'metrics.json').read_text());asr=json.loads((N/'asr.json').read_text());canonical=metrics[52]['path'];assert metrics[52]['sentence_id']==target
for row in proof['original_selected_takes']:
 assert hashlib.sha256((R/row['path']).read_bytes()).hexdigest()==row['sha256'],'Original selected take changed before bounded selection.'
shutil.copy2(R/take['path'],R/canonical);selected_take={**take,'path':canonical,'selected_from':take['path'],'generation_run':'Targeted one-sentence explicit112digit expansion,index52;fresh NumPyseed42 invocation;original full-stream take retained.','selection_record':'studio/episodes/hb-c10-psykisk/emergency112-comparison.json'};metrics[52]=selected_take;selected_asr={**a,'file':canonical,'selected_from':a['file']}
for i,row in enumerate(asr):
 if row['file']==canonical:asr[i]=selected_asr;break
else:raise RuntimeError('Original ASR target absent')
(N/'metrics.json').write_text(json.dumps(metrics,ensure_ascii=False,indent=2)+'\n');(N/'asr.json').write_text(json.dumps(asr,ensure_ascii=False,indent=2)+'\n')
for row in proof['original_selected_takes']:
 if row['sentence_id']!=target:assert hashlib.sha256((R/row['path']).read_bytes()).hexdigest()==row['sha256']
original=M/'revisions/pre-emergency112'/f'{target}.wav';assert hashlib.sha256(original.read_bytes()).hexdigest()==proof['original_selected_takes'][52]['sha256'];proof.update(new_selected_take=True,selected_take=selected_take,new_sha256=a['sha256'],all_other_78_selected_wavs_unchanged=True,original_target_retained=str(original.relative_to(R)),original_target_sha256=hashlib.sha256(original.read_bytes()).hexdigest(),whole_video_listening=False);(E/'emergency112-retake-proof.json').write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n');print('Selected explicit112take;78otherWAVs unchanged,originaltarget+fullmetrics+ASR retained.')
