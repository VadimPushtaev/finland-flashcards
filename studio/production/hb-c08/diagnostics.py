"""Bind source-order narration, WAV integrity and ASR diagnostics without auditory claims."""
from pathlib import Path
import difflib,hashlib,json,re,sys
import numpy as np
import soundfile as sf
import yaml
ROOT=Path(__file__).resolve().parents[3]
def main(sid):
 ep=ROOT/'studio/episodes'/sid;media=ROOT/'studio/media'/sid;d=yaml.safe_load((ep/'script.yaml').read_text());metrics=json.loads((media/'narration/metrics.json').read_text());asr={Path(r['file']).stem:r for r in json.loads((media/'narration/asr.json').read_text())};assert [m['sentence_id'] for m in metrics]==[r['sentence_id'] for r in d['sentences']];checks=[];priorities=[]
 for r,m in zip(d['sentences'],metrics):
  p=ROOT/m['path'];sha=hashlib.sha256(p.read_bytes()).hexdigest();a=asr[r['sentence_id']];assert a['sha256']==sha;assert m['text']==(r.get('speech_override') or {}).get('text',r['sv']);audio,rate=sf.read(p);assert audio.ndim==1 and rate==44100 and np.isfinite(audio).all() and len(audio)>0;peak=float(np.abs(audio).max());assert peak<1 and peak>0.0001;assert abs(len(audio)/rate-m['seconds'])<1/rate
  normalize=lambda t:re.findall(r'\w+',t.casefold());expected=normalize(m['text']);observed=normalize(a['asr_text']);match=difflib.SequenceMatcher(a=expected,b=observed);differences=[dict(expected=' '.join(expected[i:j]),asr=' '.join(observed[k:l])) for op,i,j,k,l in match.get_opcodes() if op!='equal'];check=dict(sentence_id=r['sentence_id'],tts_input=m['text'],asr_text=a['asr_text'],sha256=sha,sample_rate=rate,seconds=m['seconds'],peak=peak,token_similarity=match.ratio(),transcript_differences=differences,listening_status='pending');checks.append(check)
  if differences or re.search(r'\d|FPA|Wilma|Celia|Hux',m['text']):priorities.append(dict(sentence_id=r['sentence_id'],start_seconds=r.get('start_seconds'),end_seconds=r.get('end_seconds'),intended_wording=m['text'],asr_text=a['asr_text'],transcript_differences=differences,status='Diagnostic uncertainty, not a confirmed audible error.'))
 render=json.loads((ep/'render.json').read_text()) if (ep/'render.json').exists() else {};report=dict(method='Local faster-whisper small, Swedish, beam5, int8 CPU. ASR cannot establish pronunciation, listening quality or exact units.',integrity='Every retained source-order mono44100Hz WAV and synthesis input checked; finite samples, nonzero unclipped waveform, measured duration and current ASR checksum verified.',sentences=checks,listening_status='pending');(ep/'narration-check.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');(ep/'listening-priorities.json').write_text(json.dumps(dict(export_sha256=render.get('sha256'),unresolved=priorities,resolved_audible_issues=[],listening_status='No auditory review performed; complete-video listening and user acceptance remain pending.'),ensure_ascii=False,indent=2)+'\n');print(sid,len(checks),'verified inputs/WAVs/ASR hashes;',len(priorities),'unconfirmed listening priorities',flush=True)
if __name__=='__main__':
 for sid in sys.argv[1:]:main(sid)
