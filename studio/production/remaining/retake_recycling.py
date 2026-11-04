"""Two bounded diagnostic comparisons; never replace selected narration here."""
from pathlib import Path
import hashlib
import json
import time

import numpy as np
import soundfile as sf
from supertonic import TTS
import yaml

ROOT=Path(__file__).resolve().parents[3]
SECTION='hb-c11-atervinning'
EPISODE=ROOT/'studio/episodes'/SECTION
OUTPUT=ROOT/'studio/media'/SECTION/'retake-wc-vederlag'


def main():
    script=yaml.safe_load((EPISODE/'script.yaml').read_text())
    original=json.loads((ROOT/'studio/media'/SECTION/'narration/metrics.json').read_text())
    proposals=[]
    for index in [8,20]:
        row=script['sentences'][index]
        text=row['sv']
        reason='One exact-input comparison for concrete vederlagen/hyrorna diagnostic; listening remains pending.'
        if index==8:
            assert text.count('WC:n')==1
            text=text.replace('WC:n','toaletten')
            reason='Speech-only Swedish expansion of WC:n to toaletten,with exact displayed source unchanged.'
        proposals.append(dict(index=index,sentence_id=row['sentence_id'],source_text=row['sv'],text=text,reason=reason,original_metrics=original[index]))
    assert not OUTPUT.exists(),'Inspect existing comparisons; never overwrite.'
    OUTPUT.mkdir(parents=True)
    (EPISODE/'retake-proposal.json').write_text(json.dumps(proposals,ensure_ascii=False,indent=2)+'\n')
    np.random.seed(42)
    model=TTS(model_dir=ROOT/'studio/media/models/supertonic3',auto_download=False,intra_op_num_threads=1)
    style=model.get_voice_style('F1');metrics=[]
    for proposal in proposals:
        start=time.monotonic();audio,_=model.synthesize(proposal['text'],voice_style=style,lang='sv',total_steps=32,speed=.95)
        path=OUTPUT/(proposal['sentence_id']+'.wav');sf.write(path,audio.flatten(),model.sample_rate,subtype='PCM_16')
        data,rate=sf.read(path);assert rate==44100 and np.isfinite(data).all()
        metrics.append(dict(sentence_id=proposal['sentence_id'],text=proposal['text'],engine='supertonic',voice='F1',speed=.95,seed=42,path=str(path.relative_to(ROOT)),sample_rate=rate,seconds=len(data)/rate,peak=float(np.abs(data).max()),generation_seconds=time.monotonic()-start,intra_op_num_threads=1,sha256=hashlib.sha256(path.read_bytes()).hexdigest(),generation_run='Bounded WC/vederlag comparison; seed42 per invocation,source selected indices8,20; one CPU thread.'))
        (OUTPUT/'metrics.json').write_text(json.dumps(metrics,ensure_ascii=False,indent=2)+'\n')
        print(proposal['sentence_id'],'comparison complete',flush=True)


if __name__=='__main__':main()
