"""One bounded Swedish numeral comparison; selected script/takes stay intact."""
from pathlib import Path
import hashlib
import json
import time

import numpy as np
import soundfile as sf
import yaml
from supertonic import TTS

ROOT = Path(__file__).resolve().parents[3]
EPISODE = ROOT / 'studio/episodes/hb-c09-forandring'
OUTPUT = ROOT / 'studio/media/hb-c09-forandring/retake-expanded-years'
OUTPUT.mkdir(exist_ok=True)
script = yaml.safe_load((EPISODE / 'script.yaml').read_text())
original_metrics = json.loads((ROOT / 'studio/media/hb-c09-forandring/narration/metrics.json').read_text())
choices = [(28, '1700-talet', 'sjuttonhundratalet'),
           (34, '1906', 'nittonhundrasex'),
           (35, '1919', 'nittonhundranitton'),
           (36, '1921', 'nittonhundratjugoett'),
           (38, '1930', 'nittonhundratrettio')]
plan = []
for index, numeral, expansion in choices:
    row = script['sentences'][index]
    assert row['sv'].count(numeral) == 1 and not row.get('speech_override')
    selected = original_metrics[index]
    assert selected['sentence_id'] == row['sentence_id']
    assert selected['text'] == row['sv']
    plan.append(dict(index=index, sentence_id=row['sentence_id'],
                     source_text=row['sv'], text=row['sv'].replace(numeral, expansion),
                     numeral=numeral, expansion=expansion, original_metrics=selected,
                     reason='Meaning-preserving Swedish historical numeral spelling for a concrete automated year diagnostic; exact displayed archive remains unchanged.'))
(EPISODE / 'year-retake-proposal.json').write_text(json.dumps(plan, ensure_ascii=False, indent=2) + '\n')
assert not (OUTPUT / 'metrics.json').exists(), 'Comparison already exists; inspect and resume deliberately.'
np.random.seed(42)
model = TTS(model_dir=ROOT / 'studio/media/models/supertonic3', auto_download=False,
            intra_op_num_threads=2)
style = model.get_voice_style('F1')
metrics = []
for proposal in plan:
    start = time.monotonic()
    audio, _ = model.synthesize(proposal['text'], voice_style=style, lang='sv',
                               total_steps=32, speed=.95)
    path = OUTPUT / (proposal['sentence_id'] + '.wav')
    assert not path.exists()
    sf.write(path, audio.flatten(), model.sample_rate, subtype='PCM_16')
    data, rate = sf.read(path)
    assert data.ndim == 1 and rate == 44100 and np.isfinite(data).all()
    metrics.append(dict(sentence_id=proposal['sentence_id'], text=proposal['text'],
                        engine='supertonic', voice='F1', speed=.95, seed=42,
                        path=str(path.relative_to(ROOT)), sample_rate=rate,
                        seconds=len(data) / rate, peak=float(np.abs(data).max()),
                        generation_seconds=time.monotonic() - start,
                        intra_op_num_threads=2, steps=32,
                        sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                        generation_run='One bounded expanded-year comparison; seed 42 at batch start; source-order selected indices 28,34,35,36,38.'))
    (OUTPUT / 'metrics.json').write_text(json.dumps(metrics, ensure_ascii=False, indent=2) + '\n')
    print(proposal['sentence_id'], 'comparison clip complete.', flush=True)
