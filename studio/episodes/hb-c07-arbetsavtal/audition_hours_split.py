"""Run the normal local audition CLI with one in-memory speech-only candidate.

This helper does not edit the anthology, displayed text or production script.
It separates the exact spoken compound37 into30+7 as recommended by the
studio's diagnostic-led number procedure. The candidate remains separate until
its complete transcript is compared; generation settings stay in the normal CLI.
"""
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT))
from studio.tools import audition
original_load=audition.yaml.safe_load

def load_candidate(stream):
    document=original_load(stream)
    if isinstance(document,dict) and document.get('section_id')=='hb-c07-arbetsavtal':
        row=document['sentences'][41]
        assert row['sentence_id']=='hb-c07-u0063-s001'
        text=(row.get('speech_override') or {}).get('text',row['sv'])
        assert 'trettiosju komma fem till fyrtio' in text or 'trettio sju komma fem till fyrtio' in text
        row['speech_override']=dict(text=text.replace('trettiosju','trettio sju'),reason='Candidate only: split a spoken number component while preserving37.5–40; exact displayed source retained.',review_status='pending')
    return document

if __name__=='__main__':
    audition.yaml.safe_load=load_candidate
    audition.main()
