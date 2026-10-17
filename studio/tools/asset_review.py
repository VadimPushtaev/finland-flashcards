"""Build an offline review page for the episode's acquired images and audio."""
import argparse
import html
from pathlib import Path
import yaml
import numpy as np
import soundfile as sf

ROOT = Path(__file__).resolve().parents[2]


def build(section):
    episode = ROOT / 'studio/episodes' / section
    assets = yaml.safe_load((episode / 'assets.yaml').read_text())['assets']
    script = yaml.safe_load((episode / 'script.yaml').read_text())
    output = ROOT / 'studio/media' / section / 'review.html'
    import os
    def url(path):
        return html.escape(os.path.relpath(ROOT / path, output.parent), quote=True)
    def esc(value):
        return html.escape(str(value))
    chunks = ['<!doctype html><html lang="en"><meta charset="utf-8"><title>Episode asset review</title>', '<style>body{font:18px/1.5 system-ui;max-width:1000px;margin:40px auto;padding:20px;background:#edf2ef;color:#183c35}img{max-width:100%;max-height:650px}article{background:white;padding:24px;margin:24px 0;border-radius:12px}audio{width:100%}small{display:block}</style>', '<h1>' + esc(script['title_sv']) + '</h1>', '<p>Assets for review. This is not the final video or final audio mix. Pronunciation and voice approval are pending.</p>']
    pieces = []
    sample_rate = None
    for row in script['sentences']:
        waveform, rate = sf.read(ROOT / row['audio_path'])
        if sample_rate is not None and rate != sample_rate:
            raise ValueError('Narration sample rates differ')
        sample_rate = rate
        pieces.extend([waveform, np.zeros(round(rate * row['pause_after_seconds']))])
    preview = output.parent / 'narration-preview.wav'
    sf.write(preview, np.concatenate(pieces), sample_rate, subtype='PCM_16')
    chunks.append('<h2>Complete narration with planned pauses</h2><audio controls preload="none" src="narration-preview.wav"></audio>')
    sentences = {r['sentence_id']: r for r in script['sentences']}
    for asset in assets:
        chunks += ['<article><h2>' + esc(asset['asset_id']) + '</h2><p>' + esc(asset['required_credits']) + '</p>']
        for entry in asset['files']:
            path = entry['path']
            if path.endswith('.svg'):
                continue
            chunks.append('<h3>' + esc(Path(path).stem) + '</h3>')
            if entry.get('sentence_id'):
                row = sentences[entry['sentence_id']]
                chunks.append('<p lang="sv">' + esc(row['sv']) + '</p><p lang="ru">' + esc(row['ru']) + '</p>')
            if path.endswith(('.png', '.jpg')):
                chunks.append('<img src="' + url(path) + '" alt="' + esc(asset['asset_id']) + '">')
            else:
                chunks.append('<audio controls preload="none" src="' + url(path) + '"></audio>')
        chunks.append('</article>')
    chunks.append('</html>')
    output.write_text('\n'.join(chunks))
    print(output)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('section')
    build(parser.parse_args().section)
