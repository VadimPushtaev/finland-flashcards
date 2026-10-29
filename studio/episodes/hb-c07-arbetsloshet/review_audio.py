"""Bind exact narration inputs and diagnostic transcripts to retained complete WAVs."""
from pathlib import Path
import json,re,hashlib,difflib
import numpy as np,soundfile as sf,yaml
ROOT=Path(__file__).resolve().parents[3];EP=Path(__file__).resolve().parent;SID=EP.name;MEDIA=ROOT/'studio/media'/SID
script=yaml.safe_load((EP/'script.yaml').read_text());metrics=json.loads((MEDIA/'narration/metrics.json').read_text());asr={r['file']:r for r in json.loads((MEDIA/'narration/asr.json').read_text())}
assert len(metrics)==len(script['sentences'])==len(asr)
norm=lambda text:re.sub(r'[^\w\s]',' ',text.casefold()).split()
records=[]
for row,m in zip(script['sentences'],metrics):
 assert row['sentence_id']==m['sentence_id'];assert m['text']==(row.get('speech_override')or{}).get('text',row['sv'])
 p=ROOT/m['path'];sha=hashlib.sha256(p.read_bytes()).hexdigest();a=asr[m['path']];assert a['sha256']==sha
 audio,rate=sf.read(p);assert rate==44100 and audio.ndim==1 and np.isfinite(audio).all() and .001<float(abs(audio).max())<.999;assert abs(len(audio)/rate-m['seconds'])<1/rate
 expected,actual=norm(m['text']),norm(a['asr_text']);ratio=difflib.SequenceMatcher(None,expected,actual).ratio();negation_difference=any(expected.count(w)!=actual.count(w)for w in ['inte','utan','endast','ingen','inga','aldrig','måste','kan'])
 priority=ratio<.97 or negation_difference or any(c.isdigit()for c in row['sv']) or bool(row.get('speech_override'))
 records.append(dict(sentence_id=row['sentence_id'],path=m['path'],sha256=sha,tts_input=m['text'],asr_text=a['asr_text'],seconds=len(audio)/rate,peak=float(abs(audio).max()),word_similarity=ratio,negation_or_modality_count_difference=negation_difference,listening_priority=priority,start_seconds=row.get('start_seconds'),end_seconds=row.get('end_seconds')))
report=dict(section_id=SID,method='All retained clips checked for exact source order/current input, finite unclipped44100Hz mono audio, measured duration and current ASR hash. Every input/transcript pair must additionally be read by the producer; ASR cannot establish audible quality.',all_clips_integrity_passed=True,clips=len(records),whole_video_listening_performed=False,records=records)
(EP/'narration-check.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');flags=[r for r in records if r['listening_priority']]
(EP/'listening-priorities.json').write_text(json.dumps(dict(section_id=SID,note='Unconfirmed diagnostic differences and pronunciation risks for whole-video listening; not established audible defects.',records=flags),ensure_ascii=False,indent=2)+'\n');print(SID,len(records),'clips integrity passed;',len(flags),'listening priorities')
