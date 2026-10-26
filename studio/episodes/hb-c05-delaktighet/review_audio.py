"""Record integrity and transcript diagnostics without claiming auditory review."""
from pathlib import Path
import sys, json, re, hashlib, difflib
import numpy as np, soundfile as sf, yaml
root = Path(__file__).resolve().parents[3]
sid = Path(__file__).resolve().parent.name
ep = root / 'studio/episodes' / sid
media = root / 'studio/media' / sid
script = yaml.safe_load((ep / 'script.yaml').read_text())
metrics = json.loads((media / 'narration/metrics.json').read_text())
asr = {r['file']: r for r in json.loads((media / 'narration/asr.json').read_text())}
assert len(metrics) == len(script['sentences']) == len(asr)

def normalize(text):
    return re.sub('[^\\w\\s]', ' ', text.lower().replace('%', ' procent')).split()
records = []
for row, m in zip(script['sentences'], metrics):
    assert row['sentence_id'] == m['sentence_id']
    assert m['text'] == (row.get('speech_override') or {}).get('text', row['sv'])
    p = root / m['path']
    digest = hashlib.sha256(p.read_bytes()).hexdigest()
    a = asr[m['path']]
    assert a['sha256'] == digest
    audio, rate = sf.read(p)
    assert rate == 44100 and audio.ndim == 1 and np.isfinite(audio).all() and (0.001 < abs(audio).max() < 0.999)
    ratio = difflib.SequenceMatcher(None, normalize(m['text']), normalize(a['asr_text'])).ratio()
    records.append({'sentence_id': row['sentence_id'], 'path': m['path'], 'sha256': digest, 'tts_input': m['text'], 'asr_text': a['asr_text'], 'seconds': len(audio) / rate, 'peak': float(abs(audio).max()), 'word_similarity': ratio, 'listening_priority': ratio < 0.95 or any((c.isdigit() for c in row['sv'])) or bool(row.get('speech_override'))})
report = {'section_id': sid, 'method': 'All selected WAVs checked for finite unclipped 44100Hz mono audio, complete source-order inputs, measured durations and current ASR SHA256. ASR is diagnostic only.', 'all_clips_integrity_passed': True, 'clips': len(records), 'whole_video_listening_performed': False, 'records': records}
(ep / 'narration-check.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
flags = [r for r in records if r['listening_priority']]
(ep / 'listening-priorities.json').write_text(json.dumps({'section_id': sid, 'note': 'Unconfirmed transcript differences and numerical/abbreviation passages for whole-video listening; not established audible defects.', 'records': flags}, ensure_ascii=False, indent=2) + '\n')
print(sid, 'all', len(records), 'clips pass integrity,', len(flags), 'listening priorities')
for r in flags:
    print(r['sentence_id'], round(r['word_similarity'], 2), 'INPUT', r['tts_input'], 'ASR', r['asr_text'])
