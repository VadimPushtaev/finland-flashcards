"""Measure manually aligned display boundaries from finalized local narration.

Run only inside this worker's allocated ASR slot after finalized WAVs exist.
This uses actual Whisper word timestamps, never word-count timing estimates.
"""
from pathlib import Path
import hashlib,json,math,re,sys
import numpy as np,soundfile as sf,yaml
from faster_whisper import WhisperModel
from scipy.signal import resample_poly
ROOT=Path(__file__).resolve().parents[3]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def tokens(text):return re.findall(r'\w+',text.casefold())
def main(sid):
 ep=ROOT/'studio/episodes'/sid;p=ep/'script.yaml';script=yaml.safe_load(p.read_text());target=[r for r in script['sentences'] if len(r.get('display_segments') or [])>1];assert target,'No manually aligned display chunks';mp=ROOT/'studio/media'/sid/'narration/metrics.json';metrics={m['sentence_id']:m for m in json.loads(mp.read_text())};model=None;evidence=[]
 for row in target:
  for language in ['sv','ru']:assert ' '.join(seg[language] for seg in row['display_segments'])==row[language]
  m=metrics[row['sentence_id']];assert m['text']==(row.get('speech_override') or {}).get('text',row['sv']);wav=ROOT/m['path'];checksum=sha(wav);cache=ep/'segment-alignment';cache.mkdir(exist_ok=True);record=cache/(row['sentence_id']+'-word-times.json')
  if record.exists() and json.loads(record.read_text()).get('wav_sha256')==checksum:word_record=json.loads(record.read_text())
  else:
   if model is None:model=WhisperModel(str(ROOT/'studio/media/models/whisper-small'),device='cpu',compute_type='int8',cpu_threads=1,local_files_only=True)
   audio,rate=sf.read(wav,dtype='float32');assert audio.ndim==1 and rate==44100;g=math.gcd(rate,16000);audio=resample_poly(audio,16000//g,rate//g).astype(np.float32);segments,_=model.transcribe(audio,language='sv',beam_size=5,vad_filter=False,condition_on_previous_text=False,word_timestamps=True);words=[dict(word=str(w.word),start=float(w.start),end=float(w.end),probability=float(w.probability)) for seg in segments for w in (seg.words or [])];word_record=dict(wav=m['path'],wav_sha256=checksum,method='Pinned local Whisper-small,int8,Swedish,beam5,oneCPUthread,word_timestamps=True; unconfirmed acoustic alignment, not human listening.',words=words);record.write_text(json.dumps(word_record,ensure_ascii=False,indent=2)+'\n')
  normalized=[]
  for word in word_record['words']:
   for token in tokens(word['word']):normalized.append((token,word))
  row_evidence=[]
  for j,seg in enumerate(row['display_segments']):
   if j==0:seg['speech_offset_seconds']=0.0;continue
   phrase=tokens(seg['sv'])[:5];matches=[k for k in range(len(normalized)-len(phrase)+1) if [x[0] for x in normalized[k:k+len(phrase)]]==phrase]
   if len(matches)!=1:raise ValueError(f'Unique measured source prefix not found for {sid}:{row["sentence_id"]}:{j}. Keep prior source/manual segmentation; review word-times record. Matches={matches},prefix={phrase}')
   k=matches[0];onset=normalized[k][1]['start'];assert 0<onset<m['seconds'];assert all(w['probability']>=.35 for _,w in normalized[k:k+len(phrase)]),'Low confidence measured prefix requires manual review';seg['speech_offset_seconds']=onset;row_evidence.append(dict(segment_index=j,source_prefix=phrase,measured_first_word=normalized[k][1],speech_offset_seconds=onset,word_timing_record=str(record.relative_to(ROOT))))
  assert sha(wav)==checksum;row['display_segment_review']='Bilingual phrase alignment authored manually. Later display onset measured from the final retained WAV with pinned local Whisper word timestamps; source prefix matched uniquely. No word-count timing, auditory approval or user acceptance inferred.';evidence.append(dict(sentence_id=row['sentence_id'],wav_sha256=checksum,boundaries=row_evidence))
 # Write only after every requested source boundary succeeds.
 p.write_text(yaml.safe_dump(script,allow_unicode=True,sort_keys=False,width=100));(ep/'segment-alignment.json').write_text(json.dumps(dict(section_id=sid,review_status='Measured alignment; whole-video listening pending',rows=evidence),ensure_ascii=False,indent=2)+'\n');print(sid,'measured boundaries',sum(len(r['boundaries']) for r in evidence))
if __name__=='__main__':main(sys.argv[1])
