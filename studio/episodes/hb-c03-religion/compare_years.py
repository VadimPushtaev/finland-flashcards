"""Generate one bounded speech-only year-expansion comparison, preserving selected takes."""
from pathlib import Path
import fcntl
import hashlib
import json
import time
import numpy as np
import soundfile as sf
import yaml

ROOT = Path(__file__).resolve().parents[3]
EPISODE = Path(__file__).resolve().parent
OUTPUT = ROOT / 'studio/media/hb-c03-religion/retakes-year-expansion'


def main():
    """Use the same production model/settings on the two diagnosed full sentences."""
    OUTPUT.mkdir(parents=True, exist_ok=True)
    script = yaml.safe_load((EPISODE / 'script.yaml').read_text())
    selected = json.loads((ROOT / 'studio/media/hb-c03-religion/narration/metrics.json').read_text())
    before = json.loads((ROOT / 'studio/media/hb-c03-religion/narration/asr.json').read_text())
    by_asr = {Path(a['file']).stem: a for a in before}
    assert len(selected) == len(before) == len(script['sentences']) == 41
    assert json.loads((ROOT / 'studio/media/hb-c03-religion/tts-exit.json').read_text())['exit_code'] == 0
    targets = {'hb-c03-u0044-s001', 'hb-c03-u0044-s002'}
    changes = [(i, 'två tusen tjugotre', 'tjugohundratjugotre') for i, row in enumerate(script['sentences']) if row['sentence_id'] in targets]
    assert len(changes) == 2
    original = []
    for index, source, target in changes:
        row, metric = script['sentences'][index], selected[index]
        path = ROOT / metric['path']
        assert '2023' in row['sv'] and source in metric['text']
        checksum = hashlib.sha256(path.read_bytes()).hexdigest()
        assert by_asr[row['sentence_id']]['sha256'] == checksum
        original.append(dict(index=index, sentence_id=row['sentence_id'], source_text=row['sv'], input=metric['text'], sha256=checksum, asr_text=by_asr[row['sentence_id']]['asr_text'], seconds=metric['seconds'], change=[source, target]))
    (OUTPUT / 'original-comparison.json').write_text(json.dumps(original, ensure_ascii=False, indent=2) + '\n')
    with open('/tmp/homebrew-retake.lock', 'a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        from supertonic import TTS
        np.random.seed(42)
        model = TTS(model_dir=ROOT / 'studio/media/models/supertonic3', auto_download=False, intra_op_num_threads=4)
        style = model.get_voice_style('F1')
        records = []
        for item in original:
            text = item['input'].replace(*item['change'])
            path = OUTPUT / (item['sentence_id'] + '.wav')
            if path.exists():
                raise RuntimeError('Bounded comparison already exists; inspect rather than repeat: ' + str(path))
            start = time.monotonic()
            audio, duration = model.synthesize(text, voice_style=style, lang='sv', total_steps=32, speed=.95)
            sf.write(path, audio.flatten(), model.sample_rate, subtype='PCM_16')
            data, rate = sf.read(path)
            row = dict(sentence_id=item['sentence_id'], text=text, engine='supertonic', voice='F1', speed=.95, seed=42, path=str(path.relative_to(ROOT)), sample_rate=rate, seconds=len(data)/rate, peak=float(np.max(np.abs(data))), generation_seconds=time.monotonic()-start, generation_run='One bounded full-sentence year-expansion comparison, shared retake lock, F1/32steps/.95/four ONNX threads/default CPU affinity, NumPy seed42 restarted for this two-sentence invocation.')
            records.append(row)
            (OUTPUT / 'metrics.json').write_text(json.dumps(records, ensure_ascii=False, indent=2) + '\n')
            print(json.dumps(row, ensure_ascii=False), flush=True)
    (OUTPUT / 'tts-complete.json').write_text(json.dumps({'exit_code': 0, 'candidates': len(changes), 'finished': time.time()}) + '\n')


if __name__ == '__main__':
    main()
