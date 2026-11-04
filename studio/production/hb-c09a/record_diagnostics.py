"""Bind exact retained clips to local ASR evidence, without claiming listening."""
from pathlib import Path
import difflib,hashlib,json,re,sys
import yaml
ROOT=Path(__file__).resolve().parents[3]
def normalized(text):
    return re.findall(r'\w+',text.casefold())
assert normalized('Svenska ord 123!')==['svenska','ord','123']
assert normalized('ett barn')!=normalized('två barn')
def main(sid):
    ep=ROOT/'studio/episodes'/sid;media=ROOT/'studio/media'/sid;s=yaml.safe_load((ep/'script.yaml').read_text());metrics=json.loads((media/'narration/metrics.json').read_text());asr={Path(r['file']).stem:r for r in json.loads((media/'narration/asr.json').read_text())};rows=[];flags=[]
    render=ep/'render.json';export=json.loads(render.read_text()) if render.exists() else {}
    timing={item['sentence_id']:item for item in export.get('timeline',[]) if item.get('kind')=='sentence'}
    assert [m['sentence_id'] for m in metrics]==[r['sentence_id'] for r in s['sentences']]
    for row,m in zip(s['sentences'],metrics):
        a=asr[row['sentence_id']];path=ROOT/m['path'];assert a['sha256']==hashlib.sha256(path.read_bytes()).hexdigest();assert m['text']==(row.get('speech_override') or {}).get('text',row['sv'])
        expected,observed=normalized(m['text']),normalized(a['asr_text']);assert expected,'Nonempty Swedish source must yield words'
        match=difflib.SequenceMatcher(a=expected,b=observed);differences=[dict(operation=op,input=' '.join(expected[i:j]),asr=' '.join(observed[k:l])) for op,i,j,k,l in match.get_opcodes() if op!='equal']
        rec=dict(sentence_id=row['sentence_id'],tts_input=m['text'],asr_text=a['asr_text'],sha256=a['sha256'],seconds=m['seconds'],sample_rate=m['sample_rate'],peak=m['peak'],token_similarity=match.ratio(),input_tokens=len(expected),observed_tokens=len(observed),transcript_differences=differences,listening_status='pending');rows.append(rec)
        if differences or re.search(r'\d|FPA|testamentti|yhteishuoltaja',m['text']):flags.append(dict(sentence_id=row['sentence_id'],start_seconds=timing.get(row['sentence_id'],{}).get('speech_start_seconds',row.get('start_seconds')),end_seconds=timing.get(row['sentence_id'],{}).get('speech_end_seconds',row.get('end_seconds')),intended_wording=m['text'],asr_text=a['asr_text'],transcript_differences=differences,status='Unresolved automated transcript/name/number diagnostic; not a confirmed audible error'))
    (ep/'narration-check.json').write_text(json.dumps(dict(method='Local faster-whisper small, Swedish,beam5,int8CPU,2threads. Unicode word-token differences use actual word regex; numbers and speech spelling may differ in ASR. No auditory review claimed.',integrity='Every retained mono44100HzWAV matches selected metrics,source-order exact synthesis input,and ASRchecksum.',sentences=rows,listening_status='pending'),ensure_ascii=False,indent=2)+'\n')
    (ep/'listening-priorities.json').write_text(json.dumps(dict(export_sha256=export.get('sha256'),unresolved=flags,resolved_audible_issues=[],listening_status='No auditory review performed; transcript diagnostics do not establish accent,pronunciation or mix quality.'),ensure_ascii=False,indent=2)+'\n');print(sid,len(rows),'checked',len(flags),'diagnostic listening priorities',flush=True)
if __name__=='__main__':
    for sid in sys.argv[1:]:main(sid)
