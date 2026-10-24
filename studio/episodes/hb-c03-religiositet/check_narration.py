"""Retain hash-bound selected narration diagnostics for one assigned episode."""
from pathlib import Path
import argparse, difflib, hashlib, json, re
import numpy as np
import soundfile as sf
import yaml
ROOT = Path(__file__).resolve().parents[3]

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('section')
    args = p.parse_args()
    ep = ROOT / 'studio/episodes' / args.section
    folder = ROOT / 'studio/media' / args.section / 'narration'
    script = yaml.safe_load((ep / 'script.yaml').read_text())
    metrics = json.loads((folder / 'metrics.json').read_text())
    asr = {r['file']: r for r in json.loads((folder / 'asr.json').read_text())}
    assert [r['sentence_id'] for r in script['sentences']] == [m['sentence_id'] for m in metrics]
    records = []
    norm = lambda s: re.sub('[^\\w]+', ' ', s.casefold()).split()
    for row, m in zip(script['sentences'], metrics):
        path = ROOT / m['path']
        sha = hashlib.sha256(path.read_bytes()).hexdigest()
        r = asr[m['path']]
        assert r['sha256'] == sha
        expected = (row.get('speech_override') or {}).get('text', row['sv'])
        assert m['text'] == expected
        wav, rate = sf.read(path)
        assert rate == 44100 and wav.ndim == 1 and np.isfinite(wav).all() and (np.max(np.abs(wav)) < 1) and (len(wav) > 0)
        ratio = difflib.SequenceMatcher(None, norm(row['sv']), norm(r['asr_text'])).ratio()
        records.append({'sentence_id': row['sentence_id'], 'source_sv': row['sv'], 'tts_input': expected, 'file': m['path'], 'sha256': sha, 'language': 'sv', 'asr_text': r['asr_text'], 'source_token_similarity': round(ratio, 3), 'sample_rate': rate, 'seconds': len(wav) / rate, 'peak': float(np.max(np.abs(wav)))})
    out = {'section_id': args.section, 'engine': 'faster-whisper small, pinned536b0662742c02347bc0e980a01041f333bce120;CPU int8,beam5,sv,one thread', 'scope': 'Automated diagnostic only; no auditory review, physical-device review or user acceptance claimed. Inspect the full sentence before using a retake.', 'sentences': records}
    (ep / 'narration-check.json').write_text(json.dumps(out, ensure_ascii=False, indent=2) + '\n')
    print(args.section, len(records), 'selected complete clips verified')
    for r in records:
        if r['source_token_similarity'] < 0.86:
            print(r['sentence_id'], r['source_sv'], '=>', r['asr_text'])
if __name__ == '__main__':
    main()
