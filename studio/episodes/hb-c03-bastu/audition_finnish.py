"""Bounded Finnish loanword comparison; canonical source and takes stay unchanged.

Use the locked studio runtime. This mirrors studio/tools/audition.py's selected
Supertonic settings, changing only the two speech-only hyphenation candidates.
Raw candidate files are scratch; retain their inputs/hashes and selection history.
"""
from pathlib import Path
import fcntl
import hashlib
import json
import os
import time

import numpy as np
import soundfile as sf
import yaml

ROOT = Path(__file__).resolve().parents[3]
EPISODE = Path(__file__).resolve().parent
OUTPUT = ROOT / 'studio/media/hb-c03-bastu/finnish-comparison'


def main():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    if list(OUTPUT.glob('*.wav')):
        raise RuntimeError('Comparison already generated; do not silently replace it')
    source = yaml.safe_load((EPISODE / 'script.yaml').read_text())
    candidates = []
    for row in source['sentences']:
        if row['sentence_id'].endswith('u0142-s001'):
            candidates.append((row, row['sv'].replace('kiuas', 'ki-uas', 1)))
        elif row['sentence_id'].endswith('u0143-s001'):
            candidates.append((row, row['sv'].replace('löyly', 'löy-ly', 1)))
    assert len(candidates) == 2
    metrics = []
    with open('/tmp/homebrew-retake.lock', 'a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        (OUTPUT / 'status.json').write_text(json.dumps({'phase': 'tts', 'pid': os.getpid()}))
        from supertonic import TTS
        np.random.seed(42)
        model = TTS(model_dir=ROOT / 'studio/media/models/supertonic3', auto_download=False,
                    intra_op_num_threads=4)
        style = model.get_voice_style('F1')
        for row, text in candidates:
            path = OUTPUT / (row['sentence_id'] + '.wav')
            start = time.monotonic()
            audio, _ = model.synthesize(text, voice_style=style, lang='sv', total_steps=32, speed=.95)
            sf.write(path, audio.flatten(), model.sample_rate, subtype='PCM_16')
            wave, rate = sf.read(path)
            item = dict(sentence_id=row['sentence_id'], text=text, engine='supertonic',
                        voice='F1', speed=.95, seed=42, path=str(path.relative_to(ROOT)),
                        sample_rate=rate, seconds=len(wave)/rate,
                        peak=float(np.max(np.abs(wave))), generation_seconds=time.monotonic()-start,
                        sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                        generation_run='One bounded Finnish syllable-hyphenation comparison batch; NumPy seed42')
            metrics.append(item)
            (OUTPUT / 'metrics.json').write_text(json.dumps(metrics, ensure_ascii=False, indent=2)+'\n')
            print(json.dumps(item, ensure_ascii=False), flush=True)
    (OUTPUT / 'tts.exit').write_text('0\n')
    (OUTPUT / 'status.json').write_text(json.dumps({'phase': 'tts_complete', 'pid': os.getpid()}))


if __name__ == '__main__':
    main()
