"""Refresh selected internal picture pairings; no audio/timeline approval."""
from pathlib import Path
import sys

from PIL import Image
import yaml

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / 'studio/tools'))
import render

for request in sys.argv[1:]:
    slug, numbers = request.split(':')
    sid = 'hb-c09-' + slug
    script = yaml.safe_load((ROOT / 'studio/episodes' / sid / 'script.yaml').read_text())
    rows = {row['sentence_id']: row for row in script['sentences']}
    render.configure_style(script)
    background = script['render']['background_image']
    paths = {row['render_image'] for row in rows.values()} | {background}
    images = {path: Image.open(ROOT / path).convert('RGB') for path in paths}
    style = script['render']['background_style']
    backdrop = render.prepare_background(images[background], style)
    directory = HERE / 'draft-picture-review' / sid
    for number in map(int, numbers.split(',')):
        row = script['sentences'][number - 1]
        card, _ = render.make_card(script, dict(kind='sentence', sentence_id=row['sentence_id']), rows, images)
        frame = render.composite_rgb_frame(backdrop, .5, style, card.convert('RGB'), card.getchannel('A'))
        frame.resize((768, 432)).save(directory / f'draft-{number:03}.png')
        print(sid, number, 'internal draft sample refreshed; timing remains separate.')
