"""Check asset coverage, checksums, credits and generated audio integrity."""
import argparse
import hashlib
from pathlib import Path

import numpy as np
import soundfile as sf
import yaml

ROOT = Path(__file__).resolve().parents[2]


def validate(section):
    episode = ROOT / 'studio/episodes' / section
    script = yaml.safe_load((episode / 'script.yaml').read_text())
    manifest = yaml.safe_load((episode / 'assets.yaml').read_text())
    expected = {r['id']: r['kind'] for r in script['asset_requests']}
    assets = manifest['assets']
    if len(assets) != len(expected) or {a['asset_id']: a['kind'] for a in assets} != expected:
        raise ValueError('Asset requests and acquired asset IDs/kinds differ')
    for asset in assets:
        for key in ['creator', 'reuse_terms', 'required_credits', 'relevance_verification']:
            if not asset.get(key):
                raise ValueError(f'Missing {key}: {asset["asset_id"]}')
        if not asset.get('files'):
            raise ValueError(f'No files: {asset["asset_id"]}')
        for entry in asset['files']:
            path = ROOT / entry['path']
            if not path.resolve().is_relative_to((ROOT / 'studio/media').resolve()):
                raise ValueError(f'Path outside studio media: {path}')
            if hashlib.sha256(path.read_bytes()).hexdigest() != entry['sha256']:
                raise ValueError(f'Checksum mismatch: {path}')
            if path.suffix == '.wav':
                data, rate = sf.read(path)
                if data.ndim != 1 or not np.all(np.isfinite(data)) or len(data) < rate * .25:
                    raise ValueError(f'Invalid audio: {path}')
                peak = float(np.max(np.abs(data)))
                if peak < .001 or peak >= .999:
                    raise ValueError(f'Silent or full-scale audio: {path}')
                if abs(len(data) / rate - entry['seconds']) > .001:
                    raise ValueError(f'Duration mismatch: {path}')
        print(asset['asset_id'], len(asset['files']), 'files verified')
    narration = next(a for a in assets if a['asset_id'] == 'narration')
    if [f['sentence_id'] for f in narration['files']] != [s['sentence_id'] for s in script['sentences']]:
        raise ValueError('Narration sentence coverage/order differs from script')
    for row, entry in zip(script['sentences'], narration['files']):
        if entry['tts_input'] != (row.get('speech_override') or {}).get('text', row['sv']):
            raise ValueError('Generated narration input differs from current script')
        if row['audio_path'] != entry['path']:
            raise ValueError('Script audio path differs from asset register')
    print('File integrity passed. Review narration and mix together in the complete video.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('section')
    validate(parser.parse_args().section)
