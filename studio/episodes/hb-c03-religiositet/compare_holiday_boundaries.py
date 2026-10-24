"""One approved comparison each for USA, forty days and Pentecost verb boundary."""
from pathlib import Path
import hashlib, json, time
import numpy as np
import soundfile as sf
import yaml
from supertonic import TTS
ROOT = Path(__file__).resolve().parents[3]

def main():
    cases = [('hb-c03-vinterfester', 'hb-c03-u0071-s002', 'usa'), ('hb-c03-pask', 'hb-c03-u0075-s002', 'forty'), ('hb-c03-pask', 'hb-c03-u0151-s001', 'pentecost')]
    np.random.seed(42)
    model = TTS(model_dir=ROOT / 'studio/media/models/supertonic3', auto_download=False, intra_op_num_threads=4)
    style = model.get_voice_style('F1')
    records = {}
    for section, sid, kind in cases:
        d = yaml.safe_load((ROOT / 'studio/episodes' / section / 'script.yaml').read_text())
        row = next((r for r in d['sentences'] if r['sentence_id'] == sid))
        text = row['sv']
        if kind == 'usa':
            text = text.replace('USA', 'Förenta staterna')
        elif kind == 'pentecost':
            text = text.replace('himmelsfärdsdag firas', 'himmelsfärdsdag, firas')
        out = ROOT / 'studio/media' / section / 'retakes-holiday-boundaries'
        out.mkdir(parents=True, exist_ok=True)
        p = out / (sid + '.wav')
        start = time.monotonic()
        data, _ = model.synthesize(text, voice_style=style, lang='sv', total_steps=32, speed=0.95)
        sf.write(p, data.flatten(), model.sample_rate, subtype='PCM_16')
        audio, rate = sf.read(p)
        m = {'sentence_id': sid, 'text': text, 'engine': 'supertonic', 'voice': 'F1', 'speed': 0.95, 'seed': 42, 'path': str(p.relative_to(ROOT)), 'sample_rate': rate, 'seconds': len(audio) / rate, 'peak': float(np.max(np.abs(audio))), 'generation_seconds': time.monotonic() - start, 'sha256': hashlib.sha256(p.read_bytes()).hexdigest(), 'generation_run': 'One bounded3clipholidaycomparison in recorded order,NumPy42stream,4ONNXthreads,defaultfullCPUaffinity'}
        records.setdefault(section, []).append(m)
        (out / 'metrics.json').write_text(json.dumps(records[section], ensure_ascii=False, indent=2) + '\n')
        print(json.dumps(m, ensure_ascii=False), flush=True)
if __name__ == '__main__':
    main()
