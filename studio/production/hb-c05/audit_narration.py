"""Check every selected Chapter 5 waveform and its diagnostic binding."""
from pathlib import Path
import hashlib
import json

import numpy as np
import soundfile as sf
import yaml

ROOT = Path(__file__).resolve().parents[3]


def main():
    inventory = yaml.safe_load((ROOT / 'studio/episodes.yaml').read_text())
    results = []
    for entry in inventory['episodes']:
        if entry['chapter_id'] != 'hb-c05':
            continue
        sid = entry['section_id']
        episode = ROOT / 'studio/episodes' / sid
        narration = ROOT / 'studio/media' / sid / 'narration'
        script = yaml.safe_load((episode / 'script.yaml').read_text())
        metrics = json.loads((narration / 'metrics.json').read_text())
        transcripts = {Path(row['file']).stem: row for row in
                       json.loads((narration / 'asr.json').read_text())}
        assert [m['sentence_id'] for m in metrics] == [r['sentence_id'] for r in script['sentences']]
        clips = []
        for row, metric in zip(script['sentences'], metrics):
            path = ROOT / row['audio_path']
            checksum = hashlib.sha256(path.read_bytes()).hexdigest()
            diagnostic = transcripts[row['sentence_id']]
            assert diagnostic['sha256'] == checksum
            assert diagnostic.get('language', 'sv') == 'sv'
            assert hashlib.sha256((ROOT / metric['path']).read_bytes()).hexdigest() == checksum
            expected = (row.get('speech_override') or {}).get('text', row['sv'])
            assert metric['text'] == expected
            samples, rate = sf.read(path, dtype='float32', always_2d=True)
            assert rate == 44100 and samples.shape[1] == 1 and len(samples) > 0
            assert np.isfinite(samples).all()
            peak = float(np.abs(samples).max())
            assert 0 < peak < 1
            assert abs(len(samples) / rate - metric['seconds']) < 1 / rate
            clips.append(dict(sentence_id=row['sentence_id'], sha256=checksum,
                              frames=len(samples), sample_rate=rate, peak=peak))
        results.append(dict(section_id=sid, sentences=len(clips), clips=clips))
    report = dict(method='Selected WAV hashes, exact source-order synthesis inputs, '
                  'matching Swedish ASR hashes, finite mono PCM, measured duration and peak.',
                  episodes=len(results), sentences=sum(r['sentences'] for r in results),
                  auditory_review=False, results=results)
    assert report['episodes'] == 15 and report['sentences'] == 469
    (ROOT / 'studio/hb-c05-narration-check.json').write_text(json.dumps(report, indent=2) + '\n')
    print('PASS: 15 episodes, 469 selected waveforms and diagnostic bindings.')


if __name__ == '__main__':
    main()
