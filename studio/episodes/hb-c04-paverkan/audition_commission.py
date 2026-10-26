"""One bounded phrase-boundary candidate; never overwrite production narration."""
from pathlib import Path
import json
import time

import numpy as np
import soundfile as sf
import yaml
from supertonic import TTS

ROOT = Path(__file__).resolve().parents[3]
EPISODE = Path(__file__).resolve().parent
SID = 'hb-c04-u0174-s002'


def main():
    script = yaml.safe_load((EPISODE / 'script.yaml').read_text())
    row = next(r for r in script['sentences'] if r['sentence_id'] == SID)
    original = (row.get('speech_override') or {}).get('text', row['sv'])
    text = original.replace('medborgarinitiativ ber man', 'medborgarinitiativ, ber man')
    assert text != original
    output = ROOT / 'studio/media/hb-c04-paverkan/narration-commission-candidate'
    output.mkdir(parents=True, exist_ok=True)
    path = output / (SID + '.wav')
    if path.exists():
        raise RuntimeError('Preserve existing candidate; do not overwrite it')
    np.random.seed(42)
    model = TTS(model_dir=ROOT / 'studio/media/models/supertonic3',
                auto_download=False, intra_op_num_threads=2)
    start = time.monotonic()
    audio, _ = model.synthesize(text, voice_style=model.get_voice_style('F1'),
                                lang='sv', total_steps=32, speed=.95)
    sf.write(path, audio.flatten(), model.sample_rate, subtype='PCM_16')
    data, rate = sf.read(path)
    metric = dict(sentence_id=SID, text=text, engine='supertonic', voice='F1',
                  speed=.95, seed=42, intra_op_num_threads=2,
                  path=str(path.relative_to(ROOT)), sample_rate=rate,
                  seconds=len(data) / rate, peak=float(np.abs(data).max()),
                  generation_seconds=time.monotonic() - start,
                  generation_tool=str(Path(__file__).relative_to(ROOT)),
                  generation_run='One bounded Commission phrase candidate; seed 42 in separate invocation; two threads')
    (output / 'metrics.json').write_text(json.dumps([metric], ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(metric, ensure_ascii=False), flush=True)


if __name__ == '__main__':
    main()
