"""Bind listening priorities to every currently selected root narration take."""
from pathlib import Path
import difflib
import hashlib
import json
import re
import sys

import yaml

ROOT=Path(__file__).resolve().parents[3]


def main(section):
    episode=ROOT/'studio/episodes'/section
    folder=ROOT/'studio/media'/section/'narration'
    script=yaml.safe_load((episode/'script.yaml').read_text())
    metrics=json.loads((folder/'metrics.json').read_text())
    asr=json.loads((folder/'asr.json').read_text())
    assert len(metrics)==len(asr)==len(script['sentences'])
    indexed={str((ROOT/r['file']).resolve()):r for r in asr}
    records=[];priorities=[]
    normalize=lambda text:re.sub(r'[^a-zåäö0-9]','',text.casefold())
    for row,take in zip(script['sentences'],metrics):
        assert take['sentence_id']==row['sentence_id']
        assert take['text']==(row.get('speech_override') or {}).get('text',row['sv'])
        path=ROOT/take['path'];digest=hashlib.sha256(path.read_bytes()).hexdigest()
        heard=indexed[str(path.resolve())]
        assert digest==heard['sha256'],'Current selected take needs its own diagnostic: '+str(path)
        score=difflib.SequenceMatcher(None,normalize(take['text']),normalize(heard['asr_text'])).ratio()
        record=dict(sentence_id=row['sentence_id'],path=take['path'],sha256=digest,
                    expected=take['text'],asr=heard['asr_text'],character_similarity=score)
        records.append(record)
        if score<.97:priorities.append(record)
    report=dict(section_id=section,records_checked=len(records),records=records,priorities=priorities,
        asr_sha256=hashlib.sha256((folder/'asr.json').read_bytes()).hexdigest(),
        metrics_sha256=hashlib.sha256((folder/'metrics.json').read_bytes()).hexdigest(),
        purpose='Diagnostic listening priorities,not pronunciation acceptance. Numeral formatting and homophones can create false positives; review the complete exported video.',
        whole_video_listening=False,user_acceptance=False)
    (episode/'audio-diagnostics.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(section,len(records),'current-take hashes checked;',len(priorities),'unconfirmed diagnostic listening priorities')


if __name__=='__main__':main(sys.argv[1])
