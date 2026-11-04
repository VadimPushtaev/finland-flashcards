"""Measure manual display-chunk boundaries against selected local narration.

Two local word-timestamp passes must agree around unique three-word anchors.
No duration is inferred from text length. Source text and the complete WAV stay
unchanged; the resulting timing evidence still requires producer frame review
and eventual complete-video listening.
"""
from pathlib import Path
import argparse
import hashlib
import json
import math
import re
import sys

import yaml

ROOT=Path(__file__).resolve().parents[3]


def tokens(text):
    return re.findall(r'[a-zåäö]+|[0-9]+',text.casefold())


def unique_match(needle,haystack):
    matches=[i for i in range(len(haystack)-len(needle)+1)
             if haystack[i:i+len(needle)]==needle]
    if len(matches)!=1:
        raise ValueError('Need one unambiguous audible anchor: '+' '.join(needle))
    return matches[0]


def boundary(left,right,words,seconds):
    """Use the actual last-word end/next-word start,not word-count ratios."""
    left_anchor=tokens(left)[-3:];right_anchor=tokens(right)[:3]
    if len(left_anchor)!=3 or len(right_anchor)!=3:
        raise ValueError('Three complete words needed on each boundary side')
    expanded=[]
    for word in words:
        for token in tokens(word['word']):expanded.append({**word,'token':token})
    heard=[w['token'] for w in expanded]
    li=unique_match(left_anchor,heard);ri=unique_match(right_anchor,heard)
    if li+3>ri:
        raise ValueError('Anchors overlap or occur in the wrong spoken order')
    anchors=expanded[li:li+3]+expanded[ri:ri+3]
    if any(not math.isfinite(w['probability']) or not .35<=w['probability']<=1 for w in anchors):
        raise ValueError('Low-confidence boundary anchor; inspect word report/listen')
    end=expanded[li+2]['end'];start=expanded[ri]['start']
    if not all(math.isfinite(v) for v in (end,start)) or not 0<end<=start<seconds:
        raise ValueError('Invalid/nonmonotonic measured anchor timing')
    if start-end>1.5:
        raise ValueError('Large unaccounted gap between boundary anchors')
    return dict(offset=(end+start)/2,left_anchor=left_anchor,right_anchor=right_anchor,
                left_word_end=end,right_word_start=start,
                minimum_anchor_probability=min(w['probability'] for w in anchors))


def agreed_boundary(left,right,first,second,seconds):
    a=boundary(left,right,first,seconds);b=boundary(left,right,second,seconds)
    if abs(a['offset']-b['offset'])>.12:
        raise ValueError('Word-timestamp passes disagree by more than120ms')
    return dict(offset_seconds=round((a['offset']+b['offset'])/2,6),
                unprompted=a,source_prompted=b,
                pass_difference_seconds=abs(a['offset']-b['offset']))


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('section')
    parser.add_argument('--sentence-id',action='append')
    parser.add_argument('--threads',type=int,default=1)
    parser.add_argument('--apply',action='store_true')
    args=parser.parse_args()
    if args.threads<1:parser.error('Positive CPU-thread allocation required')
    episode=ROOT/'studio/episodes'/args.section
    path=episode/'script.yaml';original=path.read_bytes();script=yaml.safe_load(original)
    metrics=json.loads((ROOT/'studio/media'/args.section/'narration/metrics.json').read_text())
    selected={m['sentence_id']:m for m in metrics}
    rows=[r for r in script['sentences'] if r.get('display_segments')
          and (not args.sentence_id or r['sentence_id'] in args.sentence_id)]
    if not rows:raise ValueError('No requested manually segmented sentences')
    if args.apply and (episode/'render.json').exists():
        raise ValueError('Preserve the finished export; revise explicitly before applying new timing')
    import numpy as np
    import soundfile as sf
    from scipy.signal import resample_poly
    from faster_whisper import WhisperModel
    model=None
    reports=[]
    for row in rows:
        chunks=row['display_segments'];take=selected[row['sentence_id']]
        for language in ('sv','ru'):
            normalize=lambda value:' '.join(value.split())
            if normalize(' '.join(c[language] for c in chunks))!=normalize(row[language]):
                raise ValueError('Manual chunks must preserve every source character/word in order')
        assert take['text']==(row.get('speech_override') or {}).get('text',row['sv'])
        wav=ROOT/take['path'];digest=hashlib.sha256(wav.read_bytes()).hexdigest()
        plan=[dict(sv=c['sv'],ru=c['ru']) for c in chunks]
        key=hashlib.sha256(json.dumps(dict(wav=digest,text=take['text'],chunks=plan),ensure_ascii=False).encode()).hexdigest()[:16]
        report_path=episode/('display-alignment-'+row['sentence_id']+'-'+key+'.json')
        if report_path.exists():
            report=json.loads(report_path.read_text())
        else:
            waveform,rate=sf.read(wav,dtype='float32')
            if waveform.ndim!=1:raise ValueError('Selected narration must be mono')
            seconds=len(waveform)/rate;divisor=math.gcd(rate,16000)
            waveform=resample_poly(waveform,16000//divisor,rate//divisor).astype(np.float32)
            if model is None:
                model=WhisperModel(str(ROOT/'studio/media/models/whisper-small'),device='cpu',
                    compute_type='int8',cpu_threads=args.threads,local_files_only=True)
            passes=[]
            for prompt in (None,take['text']):
                result,_=model.transcribe(waveform,language='sv',beam_size=5,vad_filter=False,
                    condition_on_previous_text=False,word_timestamps=True,initial_prompt=prompt)
                words=[]
                for segment in result:
                    for word in segment.words or []:
                        words.append(dict(word=word.word,start=float(word.start),end=float(word.end),probability=float(word.probability)))
                passes.append(words)
            report=dict(section_id=args.section,sentence_id=row['sentence_id'],wav=take['path'],
                wav_sha256=digest,seconds=seconds,chunks=plan,spoken_text=take['text'],
                model='Existing pinned local whisper-small,int8',threads=args.threads,
                word_timestamps=dict(unprompted=passes[0],source_prompted=passes[1]),
                method='Unique3wordanchors on both sides,two measured timestamp passes,midpoint of actual spoken-word gap. No text-length timing.',
                whole_video_listening=False,user_acceptance=False)
            try:
                report['boundaries']=[agreed_boundary(a['sv'],b['sv'],*passes,seconds) for a,b in zip(chunks,chunks[1:])]
                report['status']='measured_candidates'
            except ValueError as error:
                report.update(status='manual_review_required',error=str(error))
            report_path.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
        if hashlib.sha256(wav.read_bytes()).hexdigest()!=digest:
            raise ValueError('Narration changed while measuring; preserve evidence and re-evaluate')
        if report['status']!='measured_candidates':
            raise ValueError('No timing applied; inspect '+str(report_path)+': '+report['error'])
        if args.apply:
            existing=[c.get('speech_offset_seconds') for c in chunks]
            if any(value not in (None,0,0.0) for value in existing):
                raise ValueError('Existing positive offsets require explicit revision; do not overwrite')
            for chunk,offset in zip(chunks,[0.0,*[b['offset_seconds'] for b in report['boundaries']]]):
                chunk['speech_offset_seconds']=offset
        reports.append(str(report_path.relative_to(ROOT)))
        print(row['sentence_id'],[b['offset_seconds'] for b in report['boundaries']],flush=True)
    if args.apply:
        if path.read_bytes()!=original:raise ValueError('Concurrent producer edit; candidates saved,but script untouched')
        path.write_text(yaml.safe_dump(script,allow_unicode=True,sort_keys=False,width=100))
    print(json.dumps(dict(reports=reports,applied=args.apply)),flush=True)


if __name__=='__main__':main()
