"""One bounded punctuation-only comparison for two diagnosed phrase boundaries."""
from pathlib import Path
import hashlib, json, time
import numpy as np
import soundfile as sf
import yaml
from supertonic import TTS
ROOT = Path(__file__).resolve().parents[3]
EP = Path(__file__).resolve().parent
OUT = ROOT / 'studio/media/hb-c03-religiositet/retakes-separation'

def main():
    d = yaml.safe_load((EP / 'script.yaml').read_text())
    rows = {r['sentence_id']: r for r in d['sentences']}
    replacements = {'hb-c03-u0058-s001': ('daghem firas', 'daghem, firas'), 'hb-c03-u0061-s005': ('ger hen någonting', 'ger hen, någonting')}
    OUT.mkdir(parents=True, exist_ok=True)
    np.random.seed(42)
    model = TTS(model_dir=ROOT / 'studio/media/models/supertonic3', auto_download=False, intra_op_num_threads=4)
    style = model.get_voice_style('F1')
    records = []
    for sid, (old, new) in replacements.items():
        row = rows[sid]
        text = row['sv'].replace(old, new)
        assert text != row['sv']
        start = time.monotonic()
        data, _ = model.synthesize(text, voice_style=style, lang='sv', total_steps=32, speed=0.95)
        p = OUT / (sid + '.wav')
        sf.write(p, data.flatten(), model.sample_rate, subtype='PCM_16')
        audio, rate = sf.read(p)
        record = {'sentence_id': sid, 'text': text, 'engine': 'supertonic', 'voice': 'F1', 'speed': 0.95, 'seed': 42, 'path': str(p.relative_to(ROOT)), 'sample_rate': rate, 'seconds': len(audio) / rate, 'peak': float(np.max(np.abs(audio))), 'generation_seconds': time.monotonic() - start, 'sha256': hashlib.sha256(p.read_bytes()).hexdigest(), 'generation_run': 'One bounded punctuation-separation comparison;seed42stream,4ONNXthreads,defaultfullCPUaffinity'}
        records.append(record)
        (OUT / 'metrics.json').write_text(json.dumps(records, ensure_ascii=False, indent=2) + '\n')
        print(json.dumps(record, ensure_ascii=False), flush=True)
if __name__ == '__main__':
    main()
