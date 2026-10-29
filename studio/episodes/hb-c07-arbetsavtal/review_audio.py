"""Check retained audio and record diagnostic differences without claiming listening."""
from pathlib import Path
import json,re,hashlib,difflib
import numpy as np,soundfile as sf,yaml
ROOT=Path(__file__).resolve().parents[3];EP=Path(__file__).resolve().parent;SID=EP.name;MEDIA=ROOT/'studio/media'/SID
script=yaml.safe_load((EP/'script.yaml').read_text());metrics=json.loads((MEDIA/'narration/metrics.json').read_text());asr={r['file']:r for r in json.loads((MEDIA/'narration/asr.json').read_text())}
assert len(metrics)==len(script['sentences'])==len(asr)
normalize=lambda text:re.sub(r'[^\w\s]',' ',text.casefold().replace('%',' procent')).split()
records=[]
for row,m in zip(script['sentences'],metrics):
 assert row['sentence_id']==m['sentence_id'];assert m['text']==(row.get('speech_override') or {}).get('text',row['sv'])
 p=ROOT/m['path'];digest=hashlib.sha256(p.read_bytes()).hexdigest();a=asr[m['path']];assert a['sha256']==digest
 audio,rate=sf.read(p);assert rate==44100 and audio.ndim==1 and np.isfinite(audio).all() and 0.001<float(abs(audio).max())<0.999
 assert abs(len(audio)/rate-m['seconds'])<1/rate
 ratio=difflib.SequenceMatcher(None,normalize(m['text']),normalize(a['asr_text'])).ratio()
 records.append(dict(sentence_id=row['sentence_id'],path=m['path'],sha256=digest,tts_input=m['text'],asr_text=a['asr_text'],seconds=len(audio)/rate,peak=float(abs(audio).max()),word_similarity=ratio,listening_priority=ratio<.95 or any(c.isdigit() for c in row['sv']) or bool(row.get('speech_override')),start_seconds=row.get('start_seconds'),end_seconds=row.get('end_seconds')))
report=dict(section_id=SID,method='All retainedWAVs checked forfinite/unclipped44100Hzmono,exactsource-order/currentinput,measureddurationandcurrentASRhash; ASRdiagnostics cannot establish listening quality.',all_clips_integrity_passed=True,clips=len(records),whole_video_listening_performed=False,records=records)
(EP/'narration-check.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
flags=[r for r in records if r['listening_priority']]
(EP/'listening-priorities.json').write_text(json.dumps(dict(section_id=SID,note='Unconfirmed transcript/numerical/phonetic differences forwhole-videolistening; notestablishedaudibledefects.',records=flags),ensure_ascii=False,indent=2)+'\n')
print(SID,'all',len(records),'integritypassed;',len(flags),'unconfirmedlisteningpriorities')
