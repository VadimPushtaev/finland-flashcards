"""Record full retained-take integrity and diagnostic ASR differences, never listening approval."""
from pathlib import Path
import difflib,hashlib,json,re
import numpy as np
import soundfile as sf
import yaml
ROOT=Path(__file__).resolve().parents[3];EP=Path(__file__).resolve().parent;SID=EP.name;MEDIA=ROOT/'studio/media'/SID
normalize=lambda text:''.join(c for c in text.lower() if c.isalnum())
def main():
 d=yaml.safe_load((EP/'script.yaml').read_text());metrics=json.loads((MEDIA/'narration/metrics.json').read_text());transcripts=json.loads((MEDIA/'narration/asr.json').read_text())
 assert len(metrics)==len(d['sentences'])==len(transcripts),'Incomplete diagnostic coverage'
 bypath={r['file']:r for r in transcripts};rows=[]
 timeline_path=MEDIA/'render/timeline.json'
 timings={r['sentence_id']:r for r in json.loads(timeline_path.read_text()) if r['kind']=='sentence'} if timeline_path.exists() else {}
 for row,m in zip(d['sentences'],metrics):
  assert row['sentence_id']==m['sentence_id'];intended=(row.get('speech_override')or{}).get('text',row['sv']);assert m['text']==intended
  path=ROOT/m['path'];checksum=hashlib.sha256(path.read_bytes()).hexdigest();asr=bypath[m['path']];assert asr['sha256']==checksum
  samples,rate=sf.read(path,dtype='float32');assert rate==44100 and samples.ndim==1 and np.isfinite(samples).all();peak=float(np.abs(samples).max());assert .001<peak<.999 and abs(len(samples)/rate-m['seconds'])<.001
  score=difflib.SequenceMatcher(None,normalize(intended),normalize(asr['asr_text'])).ratio();priority=score<.995 or bool(re.search(r'\d',row['sv'])) or bool(row.get('speech_override'))
  rows.append(dict(sentence_id=m['sentence_id'],path=m['path'],sha256=checksum,tts_input=intended,asr_text=asr['asr_text'],seconds=m['seconds'],start_seconds=timings.get(m['sentence_id'],{}).get('speech_start_seconds'),end_seconds=timings.get(m['sentence_id'],{}).get('speech_end_seconds'),peak=peak,character_similarity=round(score,4),listening_priority=priority))
 report=dict(section_id=SID,source_section_sha256=d['source_section_sha256'],sentences=len(rows),all_wav_integrity_passed=True,all_asr_hashes_current=True,narration_source_order_passed=True,language='sv',review_mode='automated_integrity_plus_producer_transcript_review',note='Every retained take checked for exact intended synthesis input, sample rate/shape/duration/headroom/hash and current diagnostic transcript. Transcript differences, spelling and numerical normalization are not established audible errors. No listening, speaker/headphone or whole-video user acceptance claimed.',records=rows)
 (EP/'narration-check.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
 (EP/'listening-priorities.json').write_text(json.dumps(dict(section_id=SID,note='Unconfirmed diagnostic differences and number/compound passages for complete-video listening; no audible-defect or listening-approval claim.',records=[r for r in rows if r['listening_priority']]),ensure_ascii=False,indent=2)+'\n')
 print(SID,len(rows),'retained takes verified;',sum(r['listening_priority'] for r in rows),'listening priorities')
 for r in rows:
  if r['listening_priority']:print(r['sentence_id'],r['character_similarity'],'INTENDED',r['tts_input'],'ASR',r['asr_text'])
if __name__=='__main__':main()
